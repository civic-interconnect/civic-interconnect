"""Adapter for US FEC campaign finance data sources.

This module provides an adapter for turning raw FEC campaign finance records
into normalized payloads for the CEP Entity and Exchange builders.

Adapters are responsible for:
- extracting and cleaning raw fields from source
- applying localization and normalization (where applicable)
- computing SNFEI and other derived fields
- producing a normalized payload for the builder facade

The builder facade (civic_interconnect.cep.entity.api.build_entity_from_raw
and related exchange builders) is responsible for:
- converting the normalized payload to a full CEP Entity or Exchange envelope
- applying schema-level defaults, attestation, revision chain, etc.
- delegating to the Rust core via cep_py when available
"""

from typing import Any

from civic_interconnect.cep.adapters.base import Adapter, AdapterKey, JsonDict, registry

# ---------------------------------------------------------------------
# Adapter Definition
# ---------------------------------------------------------------------


class UsFecCampaignFinanceAdapter(Adapter):
    """Adapter for US FEC campaign finance records.

    This converts raw source inputs -> CEP canonical form -> CEP envelope.
    The builder facade applies schema defaults and attestation, so here we
    only handle:
        - lexical normalization
        - semantic normalization (e.g., codes -> vocab URIs)
        - schema alignment
        - SNFEI identity derivation
    """

    key = AdapterKey(
        domain="campaign-finance",
        jurisdiction="US-FEC",
        source_system="fec-bulk",
        version="1.0.0",
    )

    # STEP 1. Canonicalization -------------------------------------------------

    def canonicalize(self, raw: dict[str, Any]) -> JsonDict:
        """Convert raw FEC record into canonical form.

        This step should:
        - normalize donor / committee names,
        - normalize office / district codes,
        - map local FEC codes to CEP vocab URIs.

        For now, this is a shallow copy placeholder.
        """
        if not isinstance(raw, dict):
            raise TypeError("Expected raw FEC record as dict.")

        canonical: JsonDict = dict(raw)
        # TODO: apply lexical + semantic normalization rules here.
        return canonical

    # STEP 2. Schema Alignment -------------------------------------------------

    def align_schema(self, canonical: JsonDict) -> JsonDict:
        """Map canonical FEC record into CEP schema envelope.

        This should:
        - choose appropriate CEP record kind (entity, exchange, relationship),
        - place fields into schema-correct locations,
        - prepare identifiers section for SNFEI.

        Returns:
            JsonDict: Aligned record ready for identity computation.
        """
        envelope: JsonDict = {
            "schemaVersion": "1.0.0",
            "jurisdictionIso": "US",
            "identifiers": {
                # SNFEI populated later in compute_identity.
                "snfei": {},
            },
            # TODO: copy and transform fields from canonical into
            #       entity / exchange / relationship envelopes as needed.
        }
        return envelope

    # STEP 3. Identity Derivation ----------------------------------------------

    def compute_identity(self, aligned: JsonDict) -> JsonDict:
        """Project into identity-relevant view, canonicalize JSON, hash -> SNFEI.

        Returns:
            JsonDict: Updated record with SNFEI in identifiers.
        """
        from hashlib import sha256
        import json

        # Minimal example: hash the aligned record minus attestation.
        projection = dict(aligned)
        projection.pop("attestation", None)

        canonical_json = json.dumps(
            projection,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        snfei_value = sha256(canonical_json).hexdigest()

        updated: JsonDict = dict(aligned)
        identifiers: JsonDict = dict(updated.get("identifiers") or {})
        identifiers["snfei"] = {"value": snfei_value}
        updated["identifiers"] = identifiers

        return updated


# Register for lookup via the registry
registry.register(UsFecCampaignFinanceAdapter)
