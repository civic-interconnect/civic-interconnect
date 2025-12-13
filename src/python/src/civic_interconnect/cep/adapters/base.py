"""Base classes and utilities for CEP adapters.

Key design points:
- Adapters implement canonicalize -> align_schema -> compute_identity -> attach_attestation.
- Localization is Rust-only via the cep_py extension module (no Python fallback) to avoid drift.
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

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
    anchor_uri: str | None = None  # optional

    def now(self) -> datetime:
        """Get the current UTC time for attestationTimestamp."""
        return datetime.now(UTC)


class Adapter(ABC):
    """Abstract base class for all CEP adapters."""

    key: AdapterKey

    def __init__(self, context: AdapterContext | None = None) -> None:
        """Initialize adapter with optional context (uses defaults if None)."""
        self.context = context or AdapterContext()

    # High-level pipeline -------------------------------------------------

    def run(self, raw: Any) -> JsonDict:
        """End-to-end pipeline: raw input -> CEP envelope or envelope set."""
        canonical = self.canonicalize(raw)
        aligned = self.align_schema(canonical)
        with_identity = self.compute_identity(aligned)
        return self.attach_attestation(with_identity)

    # Steps in the pipeline ----------------------------------------------

    @abstractmethod
    def canonicalize(self, raw: Any) -> JsonDict:
        """Lexical and semantic canonicalization."""
        raise NotImplementedError

    @abstractmethod
    def align_schema(self, canonical: JsonDict) -> JsonDict:
        """Map canonicalized input into CEP core schema shapes."""
        raise NotImplementedError

    @abstractmethod
    def compute_identity(self, aligned: JsonDict) -> JsonDict:
        """Compute SNFEI (and any other identity hashes) on the aligned record."""
        raise NotImplementedError

    def attach_attestation(self, record: JsonDict) -> JsonDict:
        """Attach an attestation block using the adapter's key and context."""
        attestation: JsonDict = {
            "attestationTimestamp": self.context.now().isoformat().replace("+00:00", "Z"),
            "attestorId": self.context.attestor_id,
            "verificationMethodUri": self.context.verification_method_uri,
            "proofType": self.context.proof_type,
            "proofPurpose": self.context.proof_purpose,
            # optional fields allowed by schema:
            "proofValue": "",
            "sourceSystem": self.key.source_system,
            "sourceReference": f"{self.key.domain}:{self.key.jurisdiction}:{self.key.version}",
            "anchorUri": self.context.anchor_uri,
        }

        # Drop None values so we don't emit anchorUri when not provided.
        attestation = {k: v for k, v in attestation.items() if v is not None}

        updated = dict(record)

        existing = updated.get("attestations")
        attestations: list[JsonDict] = []
        if isinstance(existing, list):
            attestations = [a for a in existing if isinstance(a, dict)]

        attestations.append(attestation)
        updated["attestations"] = attestations

        # IMPORTANT: remove any legacy singular key if present
        if "attestation" in updated:
            updated.pop("attestation", None)

        return updated

    # Localization (Rust-only) --------------------------------------------

    @staticmethod
    def _require_cep_py() -> Any:
        try:
            import cep_py  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "cep_py is required for localization (Rust FFI). "
                "Build/install it (e.g., uv run maturin develop --release)."
            ) from e
        return cep_py

    def apply_localization_name(self, name: str, jurisdiction: str | None = None) -> str:
        """Apply YAML-driven localization to a name (fast path).

        Rust-only. Raises RuntimeError if cep_py is missing or does not expose the function.
        """
        j = (jurisdiction or self.key.jurisdiction).strip() or self.key.jurisdiction
        cep_py = self._require_cep_py()

        fn: Callable[[str, str], str] | None = getattr(cep_py, "apply_localization_name", None)
        if fn is None:
            raise RuntimeError("cep_py.apply_localization_name is missing (FFI not exposed).")

        return fn(name, j)

    def apply_localization_name_detailed_json(
        self, name: str, jurisdiction: str | None = None
    ) -> str:
        """Apply localization and return JSON string (FFI-friendly).

        Rust-only. Raises RuntimeError if cep_py is missing or does not expose the function.
        """
        j = (jurisdiction or self.key.jurisdiction).strip() or self.key.jurisdiction
        cep_py = self._require_cep_py()

        fn: Callable[[str, str], str] | None = getattr(
            cep_py, "apply_localization_name_detailed_json", None
        )
        if fn is None:
            raise RuntimeError(
                "cep_py.apply_localization_name_detailed_json is missing (FFI not exposed)."
            )

        return fn(name, j)

    def apply_localization_name_detailed(
        self, name: str, jurisdiction: str | None = None
    ) -> JsonDict:
        """Apply localization and return parsed JSON (output + provenance)."""
        return json.loads(self.apply_localization_name_detailed_json(name, jurisdiction))


# Optional: a very small registry for wiring things up --------------------


class AdapterRegistry:
    """Maps (domain, jurisdiction, source_system) to adapter classes."""

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._registry: dict[tuple[str, str, str], type[Adapter]] = {}

    def register(self, adapter_cls: type[Adapter]) -> None:
        """Register an adapter class by its AdapterKey."""
        key = adapter_cls.key  # type: ignore[attr-defined]
        if not isinstance(key, AdapterKey):
            raise TypeError("Adapter class must define a class attribute 'key' of type AdapterKey.")
        triple = (key.domain, key.jurisdiction, key.source_system)
        self._registry[triple] = adapter_cls

    def get(self, domain: str, jurisdiction: str, source_system: str) -> type[Adapter] | None:
        """Look up an adapter class by (domain, jurisdiction, source_system)."""
        return self._registry.get((domain, jurisdiction, source_system))


registry = AdapterRegistry()


class SimpleEntityAdapter(Adapter, ABC):
    """Base adapter for simple CEP entity records."""

    identity_projection_keys: tuple[str, str] = (
        "legalNameNormalized",
        "jurisdictionIso",
    )

    def align_schema(self, canonical: JsonDict) -> JsonDict:
        """Map canonical dict into simple CEP entity shape."""
        return {
            "entityType": canonical["entityType"],
            "jurisdictionIso": canonical["jurisdictionIso"],
            "legalName": canonical["legalName"],
            "legalNameNormalized": canonical["legalNameNormalized"],
            "identifiers": {"snfei": {}},
        }

    def compute_identity(self, aligned: JsonDict) -> JsonDict:
        """Compute SNFEI from identity projection keys."""
        projection = {key: aligned[key] for key in self.identity_projection_keys}
        snfei_value = self._compute_snfei_from_projection(projection)

        updated = dict(aligned)
        updated_ident = dict(updated.get("identifiers") or {})
        updated_ident["snfei"] = {"value": snfei_value}
        updated["identifiers"] = updated_ident
        return updated

    @staticmethod
    def _compute_snfei_from_projection(projection: Mapping[str, Any]) -> str:
        canonical_json = json.dumps(
            projection,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical_json).hexdigest()
