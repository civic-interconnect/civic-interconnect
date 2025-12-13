# src/python/src/civic_interconnect/cep/adapters/procurement/spine/tender.py
"""Procurement spine adapter: Tender/Notice -> normalized CEP build request.

Input shape (from source_ocds.py):

tender = {
  "kind": "tender",
  "source_system": "...",
  "jurisdiction_iso": "IT",
  "ocid": "...",
  "release_id": "...",
  "tender_id": "...",
  "title": "...",
  "description": "...",
  "status": "...",
  "procurement_method": "...",
  "procurement_method_details": "...",
  "main_procurement_category": "...",
  "value": { "amount": ..., "currency": ... } | None,
  "items": [ ... ],
  "lots": [ ... ],
  "tender_period": { ... } | None,
}

Output:
{
  "record_kind": "entity",
  "record_type": "procurement.tender",
  "payload": { ... }
}
"""

from typing import Any

JsonObj = dict[str, Any]


def tender_build_request(
    tender: JsonObj,
    *,
    ocds_ref: JsonObj,
) -> JsonObj:
    """Output single tender build request."""
    if tender.get("kind") != "tender":
        raise ValueError(f"Expected kind=tender, got {tender.get('kind')}")

    jurisdiction_iso = _require_str(tender, "jurisdiction_iso")
    source_system = _require_str(tender, "source_system")

    payload: JsonObj = {
        "jurisdictionIso": jurisdiction_iso,
        "entityType": "tender",
        # Replace with vocabulary-backed URI when you have it.
        "tender": {
            "tenderId": tender.get("tender_id"),
            "title": tender.get("title"),
            "description": tender.get("description"),
            "status": tender.get("status"),
            "procurementMethod": tender.get("procurement_method"),
            "procurementMethodDetails": tender.get("procurement_method_details"),
            "mainProcurementCategory": tender.get("main_procurement_category"),
            "value": _maybe_dict(tender, "value"),
            "tenderPeriod": _maybe_dict(tender, "tender_period"),
            # Keep items/lots as raw evidence; a later adapter can map them to CEP types.
            "items": tender.get("items") if isinstance(tender.get("items"), list) else [],
            "lots": tender.get("lots") if isinstance(tender.get("lots"), list) else [],
        },
        "source": {
            "sourceSystem": source_system,
            "sourceKind": "ocds",
            "ocds": _min_ocds_ref(ocds_ref),
            "tender": {
                "ocid": tender.get("ocid"),
                "releaseId": tender.get("release_id"),
                "tenderId": tender.get("tender_id"),
            },
        },
    }

    return {
        "record_kind": "entity",
        "record_type": "procurement.tender",
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
