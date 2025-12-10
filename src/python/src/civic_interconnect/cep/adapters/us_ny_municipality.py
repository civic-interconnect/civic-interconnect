"""Adapter for US New York state municipality data sources.

This module provides an adapter for turning raw state municipality
records into normalized payloads for the CEP Entity builder.
"""

from typing import Any

from civic_interconnect.cep.adapters.base import AdapterKey, JsonDict, SimpleEntityAdapter
from civic_interconnect.cep.localization import (
    LocalizationConfig,
    load_localization,
    normalize_name,
)


class UsNyMunicipalityAdapter(SimpleEntityAdapter):
    """Adapter for US New York State municipality records."""

    key = AdapterKey(
        domain="municipality",
        jurisdiction="US-NY",
        source_system="ny-municipal-registry",
        version="1.0.0",
    )

    def canonicalize(self, raw: dict[str, Any]) -> JsonDict:
        """Convert raw record into canonical form."""
        if "legal_name" not in raw:
            raise ValueError("raw must contain 'legal_name'.")

        legal_name = str(raw["legal_name"]).strip()
        jurisdiction_iso = str(raw.get("jurisdiction_iso", "US-NY")).strip()

        loc_cfg: LocalizationConfig = load_localization(jurisdiction_iso)
        normalized_name = normalize_name(legal_name, loc_cfg)

        return {
            "legalName": legal_name,
            "legalNameNormalized": normalized_name,
            "jurisdictionIso": jurisdiction_iso,
            "entityType": "municipality",
        }
