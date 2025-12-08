# src/python/src/civic_interconnect/cep/snfei/normalizer.py

"""Thin normalization wrappers around the Rust core.

All actual normalization logic lives in `cep_core::common::normalizer` and is
exposed to Python via the `cep_py` extension module.

This module exists only to provide a stable Python surface:
- normalize_legal_name
- normalize_address
- normalize_registration_date
- CanonicalInput
- build_canonical_input

There is no business logic here; everything delegates to Rust.
"""

from typing import TypedDict

import cep_py as _core


class CanonicalInput(TypedDict, total=False):
    """Canonical snapshot returned by the Rust SNFEI pipeline.

    This mirrors the shape of the `canonical` block in SnfeiResult as
    serialized by serde_json:

        {
            "legalNameNormalized": str,
            "countryCode": str,
            "addressNormalized": str | None,
            "registrationDate": str | None,
            ...
        }
    """

    legalNameNormalized: str
    countryCode: str
    addressNormalized: str | None
    registrationDate: str | None


def normalize_legal_name(value: str) -> str:
    """Normalize a legal name using the Rust core."""
    return _core.normalize_legal_name_py(value)


def normalize_address(value: str) -> str:
    """Normalize an address using the Rust core."""
    return _core.normalize_address_py(value)


def normalize_registration_date(value: str) -> str | None:
    """Normalize a registration/formation date using the Rust core.

    Returns:
        ISO date string (e.g. "2020-01-31") or None if the date
        cannot be normalized.
    """
    return _core.normalize_registration_date_py(value)


def build_canonical_input(
    legal_name: str,
    country_code: str,
    address: str | None = None,
    registration_date: str | None = None,
) -> CanonicalInput:
    """Build a canonical snapshot via the Rust SNFEI pipeline.

    For now, we reuse the Rust SNFEI pipeline and extract its `canonical`
    section. This guarantees that:

    - Canonicalization happens exactly once (in Rust).
    - The canonical shape matches what SNFEI actually uses.

    If you only care about normalization (and not the hash), this is still
    safe; it just does a bit more work under the hood.

    Returns:
        CanonicalInput dict with the normalized fields.
    """
    # Import here to avoid cycles: civic_interconnect.cep.snfei.__init__
    from civic_interconnect.cep.snfei import generate_snfei_detailed

    detailed = generate_snfei_detailed(
        legal_name=legal_name,
        country_code=country_code,
        address=address,
        registration_date=registration_date,
        lei=None,
        sam_uei=None,
    )
    # Trust Rust’s canonical structure; we only type it.
    return detailed["canonical"]  # type: ignore[return-value]


__all__ = [
    "CanonicalInput",
    "build_canonical_input",
    "normalize_legal_name",
    "normalize_address",
    "normalize_registration_date",
]
