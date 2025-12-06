"""CEP Entity builder facade.

This module defines the Python-facing API for constructing CEP Entity records
from normalized adapter payloads.

Adapters should call build_entity_from_raw()
instead of constructing CEP envelopes directly.

This module uses the Rust core (via the cep_py extension) when
available, and falls back to a pure Python implementation otherwise.
"""

import json
from typing import Any

try:
    # Native extension from crates/cep-py, if built and on PYTHONPATH
    from cep_py import (  # type: ignore
        build_entity_json as _build_entity_json_native,  # type: ignore[attr-defined, import]
    )

    _HAS_NATIVE = True
except ImportError:
    _build_entity_json_native = None  # type: ignore[assignment]
    _HAS_NATIVE = False

# Public flag so tools and tests can see what is available.
HAS_NATIVE_BACKEND: bool = _HAS_NATIVE


def build_entity_from_raw(raw: dict[str, Any]) -> dict[str, Any]:
    """Convert a normalized adapter payload into a full CEP Entity record.

    Expected raw keys:
    - jurisdictionIso: ISO 3166 style jurisdiction code, for example "US-MN"
    - legalName: canonical or near-canonical name from source
    - legalNameNormalized: normalized form used for SNFEI
    - snfei: SNFEI hash computed by the adapter
    - entityType: domain type label such as "municipality", "school_district", etc.

    This function:
    - applies schema-level defaults
    - constructs verifiableId
    - attaches identifiers and status
    - populates an initial attestation block

    If the cep_py native extension is available, this function delegates
    to Rust. Otherwise, it uses a pure Python implementation.
    """
    # Basic validation of the normalized payload
    required_keys = [
        "jurisdictionIso",
        "legalName",
        "legalNameNormalized",
        "snfei",
        "entityType",
    ]
    missing = [k for k in required_keys if k not in raw]
    if missing:
        raise ValueError(f"Normalized entity payload is missing keys: {missing}")

    # Prefer native backend when available, but never crash if it fails.
    if HAS_NATIVE_BACKEND and _build_entity_json_native is not None:
        try:
            input_json = json.dumps(raw, sort_keys=True)
            output_json = _build_entity_json_native(input_json)  # type: ignore[misc]
            return json.loads(output_json)
        except Exception as exc:
            # Defensive fallback: log-friendly message and drop back to Python.
            # You can replace this print with proper logging later.
            print(
                f"[ci_cep.entity.api] Warning: native backend failed "
                f"({exc!r}); falling back to pure Python builder."
            )

    # Fallback: pure Python builder
    return _build_entity_from_raw_python(raw)


def _build_entity_from_raw_python(raw: dict[str, Any]) -> dict[str, Any]:
    """Pure Python implementation of the entity builder."""
    jurisdiction_iso = str(raw["jurisdictionIso"])
    legal_name = str(raw["legalName"])
    legal_name_normalized = str(raw["legalNameNormalized"])
    snfei = str(raw["snfei"])
    entity_type = str(raw["entityType"])

    entity_type_uri = _entity_type_uri(entity_type)

    entity: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "verifiableId": f"cep-entity:snfei:{snfei}",
        "identifiers": {
            "snfei": snfei,
        },
        "legalName": legal_name,
        "legalNameNormalized": legal_name_normalized,
        "entityTypeUri": entity_type_uri,
        "jurisdictionIso": jurisdiction_iso,
        "status": {
            "statusCode": "ACTIVE",
            "statusEffectiveDate": "1900-01-01",
            "statusTerminationDate": None,
            "successorEntityId": None,
        },
        "attestation": {
            "attestorId": "cep-entity:example:ingest",
            "attestationTimestamp": "1900-01-01T00:00:00.000000Z",
            "proofType": "ManualAttestation",
            "proofValue": "",
            "verificationMethodUri": "urn:cep:attestor:cep-entity:example:ingest",
            "proofPurpose": "assertionMethod",
            "anchorUri": None,
        },
        "previousRecordHash": None,
        "revisionNumber": 1,
    }

    return entity


def _entity_type_uri(entity_type: str) -> str:
    """Map a simple entityType label (for example, 'municipality') to a CEP Entity Type Vocabulary URI.

    This is intentionally simple for the first version so that we can
    refine it as the vocabulary stabilizes.
    """
    base = (
        "https://raw.githubusercontent.com/"
        "civic-interconnect/civic-interconnect/main/"
        "vocabulary/entity-type.json#"
    )

    # Special cases:
    if entity_type == "school_district":
        return base + "school-district"

    # Default fallback
    return base + entity_type.replace(" ", "-")
