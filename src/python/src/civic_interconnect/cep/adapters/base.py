"""Base classes and utilities for CEP adapters."""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
from typing import Any

JsonDict = dict[str, Any]


@dataclass(frozen=True)
class AdapterKey:
    """Uniquely identifies an adapter implementation."""

    domain: str  # e.g. "campaign-finance"
    jurisdiction: str  # e.g. "US-FEC", "US-MN"
    source_system: str  # e.g. "fec-bulk", "mn-cf-portal"
    version: str  # e.g. "1.0.0"


@dataclass
class AdapterContext:
    """Shared context passed into adapters.

    This keeps things like attestor id, clock, and configuration in one place.
    """

    attestor_id: str = "cep-entity:example:ingest"
    proof_purpose: str = "assertionMethod"
    proof_type: str = "ManualAttestation"
    verification_method_uri: str = "urn:cep:attestor:cep-entity:example:ingest"

    # In tests you can override time via a custom callable if you want.
    def now(self) -> datetime:
        """Get the current UTC time for attestationTimestamp."""
        return datetime.now(UTC)


class Adapter(ABC):
    """Abstract base class for all CEP adapters.

    Each concrete adapter implements:
    - lexical + semantic canonicalization,
    - schema alignment into CEP envelopes,
    - SNFEI computation,
    - attestation construction.
    """

    key: AdapterKey

    def __init__(self, context: AdapterContext | None = None) -> None:
        """Initialize adapter with optional context (uses defaults if None)."""
        self.context = context or AdapterContext()

    # High-level pipeline -------------------------------------------------

    def run(self, raw: Any) -> JsonDict:
        """End-to-end pipeline: raw input -> CEP envelope or envelope set.

        For some domains you may want this to return a dict with multiple
        envelopes (entities, relationships, exchanges). For now we keep
        the type as JsonDict, and refine later.
        """
        canonical = self.canonicalize(raw)
        aligned = self.align_schema(canonical)
        with_identity = self.compute_identity(aligned)
        return self.attach_attestation(with_identity)

    # Steps in the pipeline ----------------------------------------------

    @abstractmethod
    def canonicalize(self, raw: Any) -> JsonDict:
        """Lexical and semantic canonicalization.

        Should:
        - normalize strings (names, jurisdictions, corp suffixes),
        - map local codes to CEP vocab URIs where possible,
        - be idempotent: canonicalize(canonicalize(raw)) gives same result.
        """
        raise NotImplementedError

    @abstractmethod
    def align_schema(self, canonical: JsonDict) -> JsonDict:
        """Map canonicalized input into CEP core schema shapes.

        Should produce something that matches the CEP schemas:
        - entity envelopes,
        - relationship envelopes,
        - exchange envelopes.

        For simple cases this may just be an entity envelope.
        """
        raise NotImplementedError

    @abstractmethod
    def compute_identity(self, aligned: JsonDict) -> JsonDict:
        """Compute SNFEI (and any other identity hashes) on the aligned record.

        This should:
        - project the aligned record into the identity-relevant view,
        - canonicalize that view via JSON canonicalization (RFC 8785 style),
        - hash to produce SNFEI,
        - write it into the 'identifiers' section.

        Must be stable: running the full pipeline twice yields same SNFEI.
        """
        raise NotImplementedError

    def attach_attestation(self, record: JsonDict) -> JsonDict:
        """Attach an attestation block using the adapter's key and context."""
        attestation = {
            "attestationTimestamp": self.context.now().isoformat().replace("+00:00", "Z"),
            "attestorId": self.context.attestor_id,
            "adapterDomain": self.key.domain,
            "adapterJurisdiction": self.key.jurisdiction,
            "adapterSourceSystem": self.key.source_system,
            "adapterVersion": self.key.version,
            "proofPurpose": self.context.proof_purpose,
            "proofType": self.context.proof_type,
            "proofValue": "",
            "verificationMethodUri": self.context.verification_method_uri,
        }

        # Simple case: top-level "attestation" field on an entity envelope.
        updated = dict(record)
        updated["attestation"] = attestation
        return updated


# Optional: a very small registry for wiring things up --------------------


class AdapterRegistry:
    """Maps (domain, jurisdiction, source_system) to adapter classes."""

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._registry: dict[tuple[str, str, str], type[Adapter]] = {}

    def register(self, adapter_cls: type[Adapter]) -> None:
        """Register an adapter class."""
        key = adapter_cls.key  # type: ignore[attr-defined]
        if not isinstance(key, AdapterKey):
            raise TypeError("Adapter class must define a class attribute 'key' of type AdapterKey.")
        triple = (key.domain, key.jurisdiction, key.source_system)
        self._registry[triple] = adapter_cls

    def get(
        self,
        domain: str,
        jurisdiction: str,
        source_system: str,
    ) -> type[Adapter] | None:
        """Look up an adapter class by (domain, jurisdiction, source_system)."""
        return self._registry.get((domain, jurisdiction, source_system))


registry = AdapterRegistry()


class SimpleEntityAdapter(Adapter, ABC):
    """Base adapter for simple CEP entity records.

    Assumes canonical records contain:
        - legalName
        - legalNameNormalized
        - jurisdictionIso
        - entityType

    and that SNFEI is computed from:
        - legalNameNormalized
        - jurisdictionIso

    Subclasses usually only need to implement `canonicalize`.
    """

    # Fields used in the identity projection, in order.
    identity_projection_keys: tuple[str, str] = (
        "legalNameNormalized",
        "jurisdictionIso",
    )

    def align_schema(self, canonical: JsonDict) -> JsonDict:
        """Align schema for simple entity envelopes.

        Produces a minimal entity-shaped dict that the builder facade
        will turn into a full CEP entity envelope.
        """
        return {
            "entityType": canonical["entityType"],
            "jurisdictionIso": canonical["jurisdictionIso"],
            "legalName": canonical["legalName"],
            "legalNameNormalized": canonical["legalNameNormalized"],
            "identifiers": {
                "snfei": {}  # filled in during compute_identity
            },
            # schemaVersion applied later by the builder
        }

    def compute_identity(self, aligned: JsonDict) -> JsonDict:
        """Compute SNFEI from a stable projection of the aligned record.

        By default, this uses the keys in `identity_projection_keys`.
        Subclasses can override `identity_projection_keys` if needed.
        """
        projection = {key: aligned[key] for key in self.identity_projection_keys}

        snfei_value = self._compute_snfei_from_projection(projection)

        updated = dict(aligned)
        updated_ident = dict(updated.get("identifiers") or {})
        updated_ident["snfei"] = {"value": snfei_value}
        updated["identifiers"] = updated_ident

        return updated

    @staticmethod
    def _compute_snfei_from_projection(projection: Mapping[str, Any]) -> str:
        """Compute SNFEI-style hash from a projection dict.

        This centralizes:
        - canonical JSON encoding (sorted keys, no extra whitespace),
        - hashing algorithm (currently SHA-256),
        so that changes can be made in one place.
        """
        canonical_json = json.dumps(
            projection,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical_json).hexdigest()
