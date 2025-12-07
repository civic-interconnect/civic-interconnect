"""Adapter for US school district data sources.

This module provides an adapter for turning raw US school district records
into normalized payloads for the CEP Entity builder.

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

from dataclasses import dataclass
import hashlib
from typing import Any

from civic_interconnect.cep.entity.api import build_entity_from_raw
from civic_interconnect.cep.localization import (
    LocalizationConfig,
    load_localization,
    normalize_name,
)


@dataclass
class RawSchoolDistrict:
    """Minimal view of a raw school district record."""

    legal_name: str
    jurisdiction_iso: str  # e.g. "US-MN", "US-CA", "US-NY"


def compute_snfei(normalized_name: str, jurisdiction_iso: str) -> str:
    """Compute SNFEI-style hash from normalized name and jurisdiction."""
    key = f"{normalized_name}|{jurisdiction_iso}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def build_school_district_entity(
    raw_record: dict[str, Any],
    localization_jurisdiction: str | None = None,
) -> dict[str, Any]:
    """Build a CEP Entity record for a school district from a raw input dict.

    Expected raw_record keys:
    - legal_name: display/legal name from the source system
    - jurisdiction_iso: ISO 3166 style jurisdiction, e.g. "US-MN"

    If localization_jurisdiction is not provided, this function will
    use raw_record["jurisdiction_iso"] as the localization key.
    """
    if "legal_name" not in raw_record:
        raise ValueError("raw_record must contain 'legal_name'.")
    if "jurisdiction_iso" not in raw_record:
        raise ValueError("raw_record must contain 'jurisdiction_iso'.")

    raw = RawSchoolDistrict(
        legal_name=str(raw_record["legal_name"]).strip(),
        jurisdiction_iso=str(raw_record["jurisdiction_iso"]).strip(),
    )

    loc_key = localization_jurisdiction or raw.jurisdiction_iso
    loc_cfg: LocalizationConfig = load_localization(loc_key)

    normalized_name = normalize_name(raw.legal_name, loc_cfg)
    snfei = compute_snfei(normalized_name, raw.jurisdiction_iso)

    normalized_payload: dict[str, Any] = {
        "jurisdictionIso": raw.jurisdiction_iso,
        "legalName": raw.legal_name,
        "legalNameNormalized": normalized_name,
        "snfei": snfei,
        "entityType": "school_district",
        # Extension surface for future fields:
        # "sourceSystem": raw_record.get("source_system"),
        # "externalIds": raw_record.get("external_ids", {}),
    }

    return build_entity_from_raw(normalized_payload)
