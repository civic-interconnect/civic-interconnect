"""State portal example adapter for the CEP system.

This module provides an adapter for turning raw state portal civic engagement
records into normalized payloads for the CEP Entity builder.

Adapters are responsible for:
- extracting and cleaning raw fields from source
- applying localization and normalization
- computing SNFEI and other derived fields
- producing a normalized payload for the builder facade

The builder facade (civic_interconnect.cep.entity.api.build_entity_from_raw)
is responsible for:
- converting the normalized payload to a full CEP Entity envelope
- applying schema-level defaults, attestation, revision chain, etc.
- delegating to the Rust core via cep_py when available
"""

from typing import Any

from civic_interconnect.cep.adapters.base import Adapter, AdapterKey, JsonDict
from civic_interconnect.cep.localization import apply_localization_name

# ---------------------------------------------------------------------
# Adapter Definition
# ---------------------------------------------------------------------


class StatePortalExampleAdapter(Adapter):
    """Adapter for generic state portal civic engagement records.

    This converts raw source inputs -> CEP canonical form -> CEP envelope.
    The builder facade applies schema defaults and attestation, so here we
    only handle:
        - lexical normalization
        - semantic normalization
        - schema alignment
        - SNFEI identity derivation
    """

    key = AdapterKey(
        domain="civic-engagement",
        jurisdiction="US-STATE-PORTAL",
        source_system="state-portal-example",
        version="1.0.0",
    )

    # STEP 1. Canonicalization -------------------------------------------------

    def canonicalize(self, raw: dict[str, Any]) -> JsonDict:
        """Convert raw state portal record into canonical form.

        Expected raw fields (example):
        - program_name: display/legal name from the portal
        - jurisdiction_iso: ISO 3166 style jurisdiction, e.g. "US-MN"

        Additional fields (e.g. portal_id, category, url) can be carried
        through in canonical and used in align_schema.
        """
        if "program_name" not in raw:
            raise ValueError("raw must contain 'program_name'.")
        if "jurisdiction_iso" not in raw:
            raise ValueError("raw must contain 'jurisdiction_iso'.")

        program_name = str(raw["program_name"]).strip()
        jurisdiction_iso = str(raw["jurisdiction_iso"]).strip()

        # Rust localization pre-normalization (jurisdiction-aware)
        localized = apply_localization_name(program_name, jurisdiction_iso)

        canonical: JsonDict = {
            "legalName": program_name,
            "legalNameNormalized": localized,
            "jurisdictionIso": jurisdiction_iso,
            "entityType": "organization",
        }

        # Pass through extra fields for later mapping
        if "portal_id" in raw:
            canonical["portalId"] = str(raw["portal_id"]).strip()
        if "category" in raw:
            canonical["category"] = str(raw["category"]).strip()
        if "url" in raw:
            canonical["url"] = str(raw["url"]).strip()

        return canonical

    # STEP 2. Schema Alignment -------------------------------------------------

    def align_schema(self, canonical: JsonDict) -> JsonDict:
        """Shape the record to match the CEP entity schema structure.

        This should produce something that the builder facade understands.

        Returns:
            JsonDict: Aligned record ready for identity computation.
        """
        aligned: JsonDict = {
            "entityType": canonical["entityType"],
            "jurisdictionIso": canonical["jurisdictionIso"],
            "legalName": canonical["legalName"],
            "legalNameNormalized": canonical["legalNameNormalized"],
            "identifiers": {
                "snfei": {}  # filled in during compute_identity
            },
            # schemaVersion applied later by the builder
        }

        # Optionally map extra fields into standard slots or extensions
        if "portalId" in canonical:
            aligned.setdefault("externalIds", {})["statePortalId"] = canonical["portalId"]
        if "category" in canonical:
            aligned["category"] = canonical["category"]
        if "url" in canonical:
            aligned["homepageUrl"] = canonical["url"]

        return aligned

    # STEP 3. Identity Derivation ----------------------------------------------

    def compute_identity(self, aligned: JsonDict) -> JsonDict:
        """Project into identity-relevant view, canonicalize JSON, hash -> SNFEI.

        Returns:
            JsonDict: Updated record with SNFEI in identifiers.
        """
        import hashlib
        import json

        projection = {
            "legalNameNormalized": aligned["legalNameNormalized"],
            "jurisdictionIso": aligned["jurisdictionIso"],
        }

        canonical_json = json.dumps(
            projection,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        snfei_value = hashlib.sha256(canonical_json).hexdigest()

        updated = dict(aligned)
        updated_ident = dict(updated["identifiers"])
        updated_ident["snfei"] = {"value": snfei_value}
        updated["identifiers"] = updated_ident

        return updated
