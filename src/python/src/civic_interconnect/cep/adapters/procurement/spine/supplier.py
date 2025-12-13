# src/python/src/civic_interconnect/cep/adapters/procurement/spine/supplier.py
"""Procurement spine adapter: Supplier (organization) -> normalized CEP build request(s).

Input supplier shape matches buyer.py (party role=supplier). We keep the same
output build-request shape, with record_type="procurement.supplier".

We intentionally do not dedupe suppliers here beyond what the source parser
already did; any entity resolution happens later, explicitly, with evidence.
"""

from collections.abc import Iterable
from typing import Any

JsonObj = dict[str, Any]


def supplier_build_requests(
    suppliers: Iterable[JsonObj],
    *,
    ocds_ref: JsonObj,
) -> list[JsonObj]:
    """Output multiple supplier build requests."""
    out: list[JsonObj] = []
    for s in suppliers:
        out.append(supplier_build_request(s, ocds_ref=ocds_ref))
    return out


def supplier_build_request(
    supplier: JsonObj,
    *,
    ocds_ref: JsonObj,
) -> JsonObj:
    """Output single supplier build request."""
    _require_kind_role(supplier, kind="party", role="supplier")
    legal_name = _require_str(supplier, "legal_name")

    jurisdiction_iso = _require_str(supplier, "jurisdiction_iso")
    source_system = _require_str(supplier, "source_system")

    payload: JsonObj = {
        "legalName": legal_name,
        "jurisdictionIso": jurisdiction_iso,
        "entityType": "organization",
        "source": {
            "sourceSystem": source_system,
            "sourceKind": "ocds",
            "ocds": _min_ocds_ref(ocds_ref),
            "party": {
                "role": "supplier",
                "partyId": supplier.get("party_id"),
                "partySource": supplier.get("ocds_party_source"),
            },
        },
        "identifiers": _collect_identifiers(supplier),
        "address": _maybe_dict(supplier, "address"),
        "contactPoint": _maybe_dict(supplier, "contact_point"),
    }

    return {
        "record_kind": "entity",
        "record_type": "procurement.supplier",
        "jurisdiction_iso": jurisdiction_iso,
        "source_system": source_system,
        "source_ref": _min_ocds_ref(ocds_ref),
        "payload": payload,
    }


def _min_ocds_ref(ocds_ref: JsonObj) -> JsonObj:
    return {
        "ocid": ocds_ref.get("ocid"),
        "releaseId": ocds_ref.get("release_id"),
        "date": ocds_ref.get("date"),
        "tag": ocds_ref.get("tag"),
    }


def _collect_identifiers(party: JsonObj) -> JsonObj:
    out: JsonObj = {"primary": None, "additional": []}

    ident = party.get("identifier")
    if isinstance(ident, dict):
        out["primary"] = {
            "scheme": ident.get("scheme"),
            "id": ident.get("id"),
            "legalName": ident.get("legalName"),
            "uri": ident.get("uri"),
        }

    addl = party.get("additional_identifiers")
    if isinstance(addl, list):
        cleaned = []
        for x in addl:
            if not isinstance(x, dict):
                continue
            cleaned.append(
                {
                    "scheme": x.get("scheme"),
                    "id": x.get("id"),
                    "legalName": x.get("legalName"),
                    "uri": x.get("uri"),
                }
            )
        out["additional"] = cleaned

    return out


def _require_kind_role(obj: JsonObj, *, kind: str, role: str) -> None:
    if obj.get("kind") != kind:
        raise ValueError(f"Expected kind={kind}, got {obj.get('kind')}")
    if obj.get("role") != role:
        raise ValueError(f"Expected role={role}, got {obj.get('role')}")


def _require_str(obj: JsonObj, key: str) -> str:
    v = obj.get(key)
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"Missing or invalid string field: {key}")
    return v.strip()


def _maybe_dict(obj: JsonObj, key: str) -> JsonObj | None:
    v = obj.get(key)
    if isinstance(v, dict):
        return v
    return None
