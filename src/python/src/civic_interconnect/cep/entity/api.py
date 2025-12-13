"""Rust-backed CEP Entity builder facade.

This module defines the Python-facing API for constructing CEP Entity records
from normalized adapter payloads.

Adapters and tools should call build_entity_from_raw() instead of constructing
CEP envelopes directly.

Contract (Rust-only):
- The Rust core (via the cep_py extension) is required.
- There is NO pure-Python fallback.
- Builders MUST reject missing or empty attestations (attestations are created
  upstream and passed in).

File: src/python/src/civic_interconnect/cep/entity/api.py
"""

import json
from typing import Any

try:
    # Native extension from crates/cep-py, if built and on PYTHONPATH.
    from cep_py import (  # type: ignore
        build_entity_json as _build_entity_json_native,  # type: ignore[attr-defined]
    )

    _HAS_NATIVE = True
except ImportError:
    _build_entity_json_native = None  # type: ignore[assignment]
    _HAS_NATIVE = False


# Public flag so tools and tests can see what is available.
HAS_NATIVE_BACKEND: bool = _HAS_NATIVE


def build_entity_from_raw(raw: dict[str, Any]) -> dict[str, Any]:
    """Convert a normalized adapter payload into a full CEP Entity record (Rust-only).

    Expected raw keys (minimum):
    - jurisdictionIso: ISO 3166 style jurisdiction code, e.g. "US-MN"
    - legalName: canonical or near-canonical name from source
    - legalNameNormalized: normalized form used for SNFEI
    - snfei: SNFEI hash computed by the adapter
    - entityType: domain type label such as "municipality", "school_district", etc.
    - attestations: list[dict], MUST be non-empty (record-envelope requirement)

    This function delegates to Rust via cep_py. If cep_py is not available,
    it raises an error. If Rust validation fails, it raises and does not fallback.
    """
    if not HAS_NATIVE_BACKEND or _build_entity_json_native is None:
        raise RuntimeError(
            "cep_py native extension is required (Rust-only). No pure-Python fallback is permitted."
        )

    _validate_minimal_raw_payload(raw)

    try:
        input_json = json.dumps(raw, sort_keys=True)
        output_json = _build_entity_json_native(input_json)  # type: ignore[misc]
        entity: dict[str, Any] = json.loads(output_json)
        return entity
    except Exception as exc:
        # Provide a clearer error for the most common failure mode.
        msg = str(exc)
        if "attestations" in msg:
            raise ValueError(
                "Rust builder rejected input: record envelope requires "
                "'attestations' as a non-empty list. Supply one or more "
                "attestation objects upstream (adapter/ingest/CLI)."
            ) from exc
        raise


def _validate_minimal_raw_payload(raw: dict[str, Any]) -> None:
    required_keys = [
        "jurisdictionIso",
        "legalName",
        "legalNameNormalized",
        "snfei",
        "entityType",
        "attestations",
    ]
    missing = [k for k in required_keys if k not in raw]
    if missing:
        raise ValueError(f"Normalized entity payload is missing keys: {missing}")

    attestations = raw.get("attestations")
    if not isinstance(attestations, list) or len(attestations) < 1:
        raise ValueError("'attestations' must be a non-empty list.")

    for i, a in enumerate(attestations):
        if not isinstance(a, dict):
            raise ValueError(f"'attestations[{i}]' must be an object (dict).")
