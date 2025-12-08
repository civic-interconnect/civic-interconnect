# src/python/src/civic_interconnect/cep/snfei/__init__.py


import json
from typing import Any

import cep_py as _core


def generate_snfei(
    legal_name: str,
    country_code: str,
    address: str | None = None,
    registration_date: str | None = None,
) -> str:
    """Return SNFEI as a 64-char hex string via the Rust core."""
    return _core.generate_snfei(
        legal_name,
        country_code,
        address,
        registration_date,
    )


def generate_snfei_detailed(
    legal_name: str,
    country_code: str,
    address: str | None = None,
    registration_date: str | None = None,
    lei: str | None = None,
    sam_uei: str | None = None,
) -> dict[str, Any]:
    """Return a structured dict with SNFEI plus canonical input and metadata.

    `lei` and `sam_uei` are accepted for future compatibility but are not yet
    forwarded into the Rust implementation.
    """
    raw = _core.generate_snfei_detailed(
        legal_name,
        country_code,
        address,
        registration_date,
    )

    # Rust FFI currently returns a JSON string; normalize to dict.
    if isinstance(raw, str):
        return json.loads(raw)

    # If we ever change the Rust side to return a mapping directly,
    # this still works.
    return raw


def normalize_legal_name(value: str) -> str:
    """Normalize a legal name using the Rust core."""
    return _core.normalize_legal_name_py(value)


def normalize_address(value: str) -> str:
    """Normalize an address using the Rust core."""
    return _core.normalize_address_py(value)


def normalize_registration_date(value: str) -> str | None:
    """Normalize a registration/formation date, or return None."""
    return _core.normalize_registration_date_py(value)


__all__ = [
    "generate_snfei",
    "generate_snfei_detailed",
    "normalize_legal_name",
    "normalize_address",
    "normalize_registration_date",
]
