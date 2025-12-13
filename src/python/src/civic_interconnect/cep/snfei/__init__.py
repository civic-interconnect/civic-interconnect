# src/python/src/civic_interconnect/cep/snfei/__init__.py

"""Python facade for CEP SNFEI + core normalizers.

Design contract:
- Thin wrappers only: call Rust FFI (cep_py) and return the result.
- No business logic here (no normalization rules beyond calling core).
- Keep the Python surface stable and aligned with typings/cep_py/__init__.pyi.

Expected Rust FFI surface (names must match exactly):
SNFEI:
- generate_snfei(...)
- generate_snfei_detailed_json(...)
- generate_snfei_detailed(...)

Normalizers:
- normalize_legal_name(...)
- normalize_address(...)
- normalize_registration_date(...)
"""

import json
from typing import Any

import cep_py as _core


def generate_snfei(
    legal_name: str,
    country_code: str,
    address: str | None = None,
    registration_date: str | None = None,
) -> str:
    """Return SNFEI as a 64-char lowercase hex string via the Rust core."""
    return _core.generate_snfei(
        legal_name,
        country_code,
        address,
        registration_date,
    )


def generate_snfei_detailed_json(
    legal_name: str,
    country_code: str,
    address: str | None = None,
    registration_date: str | None = None,
    lei: str | None = None,
    sam_uei: str | None = None,
) -> str:
    """Return SNFEI pipeline metadata as a JSON string via the Rust core.

    The returned JSON is the Rust-serialized SnfeiResult.
    Use this for snapshots, golden files, and deterministic CLI output.
    """
    return _core.generate_snfei_detailed_json(
        legal_name,
        country_code,
        address,
        registration_date,
        lei,
        sam_uei,
    )


def generate_snfei_detailed(
    legal_name: str,
    country_code: str,
    address: str | None = None,
    registration_date: str | None = None,
    lei: str | None = None,
    sam_uei: str | None = None,
) -> dict[str, Any]:
    """Return SNFEI pipeline metadata as a parsed dict via the Rust core.

    If the Rust FFI returns a dict already, we return it.
    If it returns a JSON string, we parse it.
    """
    raw = _core.generate_snfei_detailed(
        legal_name,
        country_code,
        address,
        registration_date,
        lei,
        sam_uei,
    )

    if isinstance(raw, str):
        return json.loads(raw)

    return raw


def normalize_legal_name(value: str) -> str:
    """Normalize a legal name using the Rust core."""
    return _core.normalize_legal_name(value)


def normalize_address(value: str) -> str:
    """Normalize an address using the Rust core."""
    return _core.normalize_address(value)


def normalize_registration_date(value: str) -> str | None:
    """Normalize a registration/formation date, or return None."""
    return _core.normalize_registration_date(value)


__all__ = [
    "generate_snfei",
    "generate_snfei_detailed_json",
    "generate_snfei_detailed",
    "normalize_legal_name",
    "normalize_address",
    "normalize_registration_date",
]
