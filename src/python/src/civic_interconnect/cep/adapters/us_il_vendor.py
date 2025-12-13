"""Adapter for US Illinois vendor records (Chicago contracts).

This module provides an adapter for turning raw vendor records
into normalized payloads for the CEP Entity builder, and for
computing SNFEI via SimpleEntityAdapter.

Intended usage:
    - identity experiments (SNFEI stability)
    - name normalization evaluation
    - cross-source vendor matching

The adapter assumes the raw record contains a vendor name under
one of the following keys:

    - "vendor_name"
    - "Vendor Name"
    - "VENDOR_NAME"
"""

from typing import Any

from civic_interconnect.cep.adapters.base import AdapterKey, JsonDict, SimpleEntityAdapter
from civic_interconnect.cep.localization import apply_localization_name


class UsIlVendorAdapter(SimpleEntityAdapter):
    """Adapter for US Illinois vendor records.

    This converts raw source inputs -> CEP canonical form -> CEP envelope.
    The builder facade applies schema defaults and attestation, so here we
    only handle:
        - lexical normalization
        - semantic normalization
        - schema alignment (via SimpleEntityAdapter)
        - SNFEI identity derivation (via SimpleEntityAdapter)
    """

    key = AdapterKey(
        domain="vendor",
        jurisdiction="US-IL",
        source_system="chicago-contracts",
        version="1.0.0",
    )

    def canonicalize(self, raw: dict[str, Any]) -> JsonDict:
        """Convert raw record into canonical form.

        Args:
            raw: A mapping-like object with at least a vendor name field.

        Returns:
            A canonical dict with:
                - legalName
                - legalNameNormalized
                - jurisdictionIso
                - entityType

        Raises:
            ValueError: if no vendor name field can be found.
        """
        # Try a few expected keys; extend as needed.
        name_keys = ("vendor_name", "Vendor Name", "VENDOR_NAME")
        legal_name: str | None = None

        for key in name_keys:
            if key in raw and raw[key] is not None:
                legal_name = str(raw[key]).strip()
                break

        if not legal_name:
            raise ValueError(f"raw must contain a vendor name under one of: {', '.join(name_keys)}")

        jurisdiction_iso = str(raw.get("jurisdiction_iso", "US-IL")).strip() or "US-IL"

        # Rust localization pre-normalization (jurisdiction-aware)
        localized = apply_localization_name(legal_name, jurisdiction_iso)

        return {
            "legalName": legal_name,
            "legalNameNormalized": localized,
            "jurisdictionIso": jurisdiction_iso,
            "entityType": "vendor",
        }
