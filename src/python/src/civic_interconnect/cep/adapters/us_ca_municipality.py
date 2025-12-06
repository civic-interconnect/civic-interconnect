"""Adapter for US California municipality data sources.

This module provides adapters for connecting to and retrieving data from
California municipal government systems and data sources.
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
class RawMunicipality:
    """Minimal view of a raw municipality record."""

    legal_name: str
    jurisdiction_iso: str = "US-CA"


def compute_snfei(normalized_name: str, jurisdiction_iso: str) -> str:
    """Compute SNFEI-style hash from normalized name and jurisdiction."""
    key = f"{normalized_name}|{jurisdiction_iso}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def build_municipality_entity(
    raw_record: dict[str, Any],
    localization_jurisdiction: str = "US-CA",
) -> dict[str, Any]:
    """Build a CEP Entity record for a municipality from a raw input dict.

    Adapter responsibilities:
    - extract and clean raw fields from source
    - apply localization and normalization
    - compute SNFEI and other derived fields
    - produce a normalized payload for the builder facade

    Builder responsibilities (ci_cep.entity.api):
    - convert normalized payload to a full CEP Entity envelope
    - apply schema-level defaults, attestation, revision chain, etc.
    """
    if "legal_name" not in raw_record:
        raise ValueError("raw_record must contain 'legal_name'.")

    raw = RawMunicipality(legal_name=str(raw_record["legal_name"]).strip())

    # Load and apply localization
    loc_cfg: LocalizationConfig = load_localization(localization_jurisdiction)
    normalized_name = normalize_name(raw.legal_name, loc_cfg)

    # Compute SNFEI based on normalized name and jurisdiction
    snfei = compute_snfei(normalized_name, raw.jurisdiction_iso)

    # This is the normalized payload passed to the builder.
    normalized_payload: dict[str, Any] = {
        "jurisdictionIso": raw.jurisdiction_iso,
        "legalName": raw.legal_name,
        "legalNameNormalized": normalized_name,
        "snfei": snfei,
        "entityType": "municipality",
        # Room for additional fields later:
        # "sourceSystem": raw_record.get("source_system"),
        # "externalIds": raw_record.get("external_ids", {}),
    }

    # Delegate to the builder facade (Python now, Rust later).
    return build_entity_from_raw(normalized_payload)
