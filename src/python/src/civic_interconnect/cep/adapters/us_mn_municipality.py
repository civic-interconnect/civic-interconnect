"""Adapter for US Minnesota municipality data sources.

This module provides an adapter for turning raw municipality
records into normalized payloads for the CEP Entity builder.
"""

from typing import Any

from civic_interconnect.cep.adapters.base import AdapterKey, JsonDict, SimpleEntityAdapter
from civic_interconnect.cep.localization import apply_localization_name


class UsMnMunicipalityAdapter(SimpleEntityAdapter):
    """Adapter for US Minnesota municipality records.

    This converts raw source inputs -> CEP canonical form -> CEP envelope.
    The builder facade applies schema defaults and attestation, so here we
    only handle:
        - lexical normalization
        - semantic normalization
        - schema alignment (via SimpleEntityAdapter)
        - SNFEI identity derivation (via SimpleEntityAdapter)
    """

    key = AdapterKey(
        domain="municipality",
        jurisdiction="US-MN",
        source_system="mn-municipal-registry",
        version="1.0.0",
    )

    def canonicalize(self, raw: dict[str, Any]) -> JsonDict:
        """Convert raw record into canonical form."""
        if "legal_name" not in raw:
            raise ValueError("raw must contain 'legal_name'.")

        legal_name = str(raw["legal_name"]).strip()
        jurisdiction_iso = str(raw.get("jurisdiction_iso", "US-MN")).strip()

        # Rust localization pre-normalization (jurisdiction-aware)
        localized = apply_localization_name(legal_name, jurisdiction_iso)

        return {
            "legalName": legal_name,
            "legalNameNormalized": localized,
            "jurisdictionIso": jurisdiction_iso,
            "entityType": "municipality",
        }
