"""Adapter for US school district data sources.

This module provides an adapter for turning raw US school district records
into normalized payloads for the CEP Entity builder.
"""

from typing import Any

from civic_interconnect.cep.adapters.base import AdapterKey, JsonDict, SimpleEntityAdapter
from civic_interconnect.cep.localization import (
    LocalizationConfig,
    load_localization,
    normalize_name,
)


class UsSchoolDistrictAdapter(SimpleEntityAdapter):
    """Adapter for US school district records."""

    key = AdapterKey(
        domain="education",
        jurisdiction="US",
        source_system="us-school-district-registry",
        version="1.0.0",
    )

    def canonicalize(self, raw: dict[str, Any]) -> JsonDict:
        """Convert raw record into canonical form."""
        if "legal_name" not in raw:
            raise ValueError("raw must contain 'legal_name'.")
        if "jurisdiction_iso" not in raw:
            raise ValueError("raw must contain 'jurisdiction_iso'.")

        legal_name = str(raw["legal_name"]).strip()
        jurisdiction_iso = str(raw["jurisdiction_iso"]).strip()

        loc_cfg: LocalizationConfig = load_localization(jurisdiction_iso)
        normalized_name = normalize_name(legal_name, loc_cfg)

        return {
            "legalName": legal_name,
            "legalNameNormalized": normalized_name,
            "jurisdictionIso": jurisdiction_iso,
            "entityType": "school_district",
        }
