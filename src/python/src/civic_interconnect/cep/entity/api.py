"""CEP Entity builder facade.

This module defines the Python-facing API for constructing CEP Entity records
from normalized adapter payloads.

Adapters should call build_entity_from_raw()
instead of constructing CEP envelopes directly.

This module uses the Rust core (via the cep_py extension) when
available, and falls back to a pure Python implementation otherwise.

File: src/python/src/civic_interconnect/cep/entity/api.py
"""

import json
from typing import Any

# Canonical URIs used by the pure-Python fallback.
# Rust is the source of truth; keep these in sync with crates/cep-core.
ENTITY_RECORD_SCHEMA_URI = (
    "https://raw.githubusercontent.com/"
    "civic-interconnect/civic-interconnect/main/"
    "schemas/cep.entity.schema.json"
)

ENTITY_TYPE_VOCAB_BASE = (
    "https://raw.githubusercontent.com/"
    "civic-interconnect/civic-interconnect/main/"
    "vocabularies/entity-type.v1.0.0.json#"
)

SNFEI_SCHEME_URI = (
    "https://raw.githubusercontent.com/"
    "civic-interconnect/civic-interconnect/main/"
    "vocabularies/entity-identifier-scheme.v1.0.0.json#snfei"
)

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
    - populates timestamps and an initial attestation block

    If the cep_py native extension is available, this function delegates
    to Rust. Otherwise, it uses a pure Python implementation.

    In both cases, it normalizes the output shape so that:
    - entityTypeUri is present
    - identifiers["snfei"] exists and is a dict with a "value" field
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

    # Decide which backend to use
    if HAS_NATIVE_BACKEND and _build_entity_json_native is not None:
        try:
            input_json = json.dumps(raw, sort_keys=True)
            output_json = _build_entity_json_native(input_json)  # type: ignore[misc]
            entity: dict[str, Any] = json.loads(output_json)
        except Exception as exc:
            # Defensive fallback: log-friendly message and drop back to Python.
            print(
                "[ci_cep.entity.api] Warning: native backend failed "
                f"({exc!r}); falling back to pure Python builder."
            )
            entity = _build_entity_from_raw_python(raw)
    else:
        entity = _build_entity_from_raw_python(raw)

    # Normalize shape so tests (and downstream code) see consistent fields.
    return _normalize_entity_shape(entity, raw)


def _build_entity_from_raw_python(raw: dict[str, Any]) -> dict[str, Any]:
    """Pure Python implementation of the entity builder.

    This is a spec mirror and test oracle for the Rust implementation.
    """
    jurisdiction_iso = str(raw["jurisdictionIso"])
    legal_name = str(raw["legalName"])
    legal_name_normalized = str(raw["legalNameNormalized"])
    snfei = str(raw["snfei"])
    entity_type = str(raw["entityType"])

    entity_type_uri = _entity_type_uri(entity_type)

    identifiers = [
        {
            "schemeUri": (
                "https://raw.githubusercontent.com/"
                "civic-interconnect/civic-interconnect/main/"
                "vocabularies/entity-identifier-scheme.v1.0.0.json#snfei"
            ),
            "identifier": snfei,
            "sourceReference": None,
        }
    ]

    entity: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "verifiableId": f"cep-entity:snfei:{snfei}",
        "identifiers": identifiers,
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


def _normalize_entity_shape(entity: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
    """Lightweight normalization so callers see a consistent shape.

    Guarantees:
    - entityTypeUri is present (derived from raw["entityType"] if missing).
    - identifiers["snfei"] exists as a dict with a "value" field when possible.
    """
    # 1) Ensure entityTypeUri
    if "entityTypeUri" not in entity:
        entity_type = raw.get("entityType")
        if isinstance(entity_type, str) and entity_type:
            entity["entityTypeUri"] = _entity_type_uri(entity_type)

    # 2) Normalize identifiers["snfei"]
    _normalize_identifiers(entity)

    return entity


def _normalize_identifiers(entity: dict[str, Any]) -> None:
    """Normalize the identifiers field to ensure consistent SNFEI shape."""
    ids = entity.get("identifiers")

    if isinstance(ids, dict):
        _normalize_dict_identifiers(ids)
    elif isinstance(ids, list):
        _normalize_list_identifiers(entity, ids)


def _normalize_dict_identifiers(ids: dict[str, Any]) -> None:
    """Normalize dict-like identifiers."""
    snfei_ident = ids.get("snfei")
    if isinstance(snfei_ident, str):
        ids["snfei"] = {"value": snfei_ident}


def _normalize_list_identifiers(entity: dict[str, Any], ids: list[Any]) -> None:
    """Normalize list-like identifiers (typical Rust shape)."""
    snfei_value = _extract_snfei_from_list(ids)
    if snfei_value is not None:
        entity["identifiers"] = {"snfei": {"value": snfei_value}}


def _extract_snfei_from_list(ids: list[Any]) -> str | None:
    """Extract SNFEI value from a list of identifier objects."""
    for ident in ids:
        if not isinstance(ident, dict):
            continue
        scheme_uri = str(ident.get("schemeUri") or "")
        if scheme_uri.endswith("#snfei"):
            value = ident.get("identifier") or ident.get("value")
            if value is not None:
                return str(value)
    return None


def _entity_type_uri(entity_type: str) -> str:
    """Map a simple entityType label (for example, 'municipality') to a CEP Entity Type Vocabulary URI.

    Vocabulary convention:
        vocabularies/entity-type.v1.0.0.json#<code>
    """
    base = (
        "https://raw.githubusercontent.com/"
        "civic-interconnect/civic-interconnect/main/"
        "vocabularies/entity-type.v1.0.0.json#"
    )

    # Special cases:
    if entity_type == "school_district":
        return base + "school-district"

    # Default fallback
    return base + entity_type.replace(" ", "-")
