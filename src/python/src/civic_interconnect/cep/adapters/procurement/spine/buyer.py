# src/python/src/civic_interconnect/cep/adapters/procurement/spine/buyer.py
"""Procurement spine adapter: Buyer (organization) -> normalized CEP build request.

This module does NOT perform entity resolution. It only:
- validates minimal fields are present
- maps a source "buyer" payload into a stable internal build request

Expected input shape (from source parsers like it_anac/source_ocds.py):

buyer = {
  "kind": "party",
  "role": "buyer",
  "source_system": "it_anac_ocds",
  "jurisdiction_iso": "IT",
  "ocds_party_source": "...",
  "party_id": "...",
  "legal_name": "...",
  "identifier": { ... } | None,
  "additional_identifiers": [ ... ],
  "address": { ... } | None,
  "contact_point": { ... } | None,
}

ocds_ref = {
  "ocid": "...",
  "release_id": "...",
  "date": "...",
  "tag": ["..."]
}

Output build request (internal contract):

{
  "record_kind": "entity",
  "record_type": "procurement.buyer",
  "jurisdiction_iso": "IT",
  "source_system": "it_anac_ocds",
  "source_ref": { ... },
  "payload": { ... }   # minimal normalized payload for Rust builder
}
"""

from typing import Any

JsonObj = dict[str, Any]


def buyer_build_request(
    buyer: JsonObj,
    *,
    ocds_ref: JsonObj,
) -> JsonObj:
    """Output single buyer build request."""
    _require_kind_role(buyer, kind="party", role="buyer")
    legal_name = _require_str(buyer, "legal_name")

    jurisdiction_iso = _require_str(buyer, "jurisdiction_iso")
    source_system = _require_str(buyer, "source_system")

    payload: JsonObj = {
        # Canonical name field that downstream localization/SNFEI expects.
        # Keep key names stable; the Rust builder can map to CEP schema.
        "legalName": legal_name,
        "jurisdictionIso": jurisdiction_iso,
        # Treat as an organization by default for procurement parties.
        # Replace with your vocabulary URI when ready.
        "entityType": "organization",
        # Source/Evidence block is intentionally verbose but structured.
        "source": {
            "sourceSystem": source_system,
            "sourceKind": "ocds",
            "ocds": _min_ocds_ref(ocds_ref),
            "party": {
                "role": "buyer",
                "partyId": buyer.get("party_id"),
                "partySource": buyer.get("ocds_party_source"),
            },
        },
        # Identifiers are carried forward as evidence; do not interpret here.
        "identifiers": _collect_identifiers(buyer),
        "address": _maybe_dict(buyer, "address"),
        "contactPoint": _maybe_dict(buyer, "contact_point"),
    }

    return {
        "record_kind": "entity",
        "record_type": "procurement.buyer",
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
