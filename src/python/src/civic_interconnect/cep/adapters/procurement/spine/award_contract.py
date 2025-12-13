# src/python/src/civic_interconnect/cep/adapters/procurement/spine/award_contract.py
"""Procurement spine adapter: Awards + Contracts -> normalized CEP build request(s).

This module is intentionally conservative:
- It emits "award" and "contract" records as separate internal build requests.
- It ALSO emits relationship "links" that can later be promoted to CEP Relationship
  records when you have stable relationship vocab URIs.

Input shapes come from it_anac/source_ocds.py:

award = {
  "kind": "award",
  "source_system": "...",
  "jurisdiction_iso": "IT",
  "ocid": "...",
  "release_id": "...",
  "award_id": "...",
  "title": "...",
  "description": "...",
  "status": "...",
  "date": "...",
  "value": { ... } | None,
  "suppliers": [ {id,name,...}, ... ] (raw OCDS refs, not normalized party payloads),
  "items": [ ... ],
  "related_lots": [ ... ],
}

contract = {
  "kind": "contract",
  "source_system": "...",
  "jurisdiction_iso": "IT",
  "ocid": "...",
  "release_id": "...",
  "contract_id": "...",
  "award_id": "...",
  "title": "...",
  "description": "...",
  "status": "...",
  "period": { ... } | None,
  "value": { ... } | None,
  "date_signed": "...",
  "related_lots": [ ... ],
  "implementation": { ... } | None,
}

We do NOT attempt to reconcile award suppliers with normalized supplier entities here.
That belongs to the identity/evidence layer later.
"""

from collections.abc import Iterable
from typing import Any

JsonObj = dict[str, Any]


def award_and_contract_build_requests(
    *,
    awards: Iterable[JsonObj],
    contracts: Iterable[JsonObj],
    ocds_ref: JsonObj,
    buyer_request: JsonObj | None,
    supplier_requests: list[JsonObj],
    tender_request: JsonObj | None,
) -> list[JsonObj]:
    """Produce build requests for award/contract records plus conservative link stubs.

    buyer_request/supplier_requests/tender_request are the outputs from spine buyer/supplier/tender modules.
    We use them only to attach stable references (not to merge identity).
    """
    out: list[JsonObj] = []

    award_reqs = [award_build_request(a, ocds_ref=ocds_ref) for a in awards]
    contract_reqs = [contract_build_request(c, ocds_ref=ocds_ref) for c in contracts]

    out.extend(award_reqs)
    out.extend(contract_reqs)

    # Relationship/link stubs (internal). Downstream can map these to CEP Relationship records.
    out.extend(
        link_stub_requests(
            ocds_ref=ocds_ref,
            buyer_request=buyer_request,
            supplier_requests=supplier_requests,
            tender_request=tender_request,
            award_requests=award_reqs,
            contract_requests=contract_reqs,
        )
    )

    return out


def award_build_request(award: JsonObj, *, ocds_ref: JsonObj) -> JsonObj:
    """Output single award build request."""
    if award.get("kind") != "award":
        raise ValueError(f"Expected kind=award, got {award.get('kind')}")

    jurisdiction_iso = _require_str(award, "jurisdiction_iso")
    source_system = _require_str(award, "source_system")

    payload: JsonObj = {
        "jurisdictionIso": jurisdiction_iso,
        "entityType": "award",
        "award": {
            "awardId": award.get("award_id"),
            "title": award.get("title"),
            "description": award.get("description"),
            "status": award.get("status"),
            "date": award.get("date"),
            "value": _maybe_dict(award, "value"),
            "relatedLots": award.get("related_lots")
            if isinstance(award.get("related_lots"), list)
            else [],
            "items": award.get("items") if isinstance(award.get("items"), list) else [],
            # Raw supplier references (OCDS); do not resolve here.
            "suppliers": award.get("suppliers") if isinstance(award.get("suppliers"), list) else [],
        },
        "source": {
            "sourceSystem": source_system,
            "sourceKind": "ocds",
            "ocds": _min_ocds_ref(ocds_ref),
            "award": {
                "ocid": award.get("ocid"),
                "releaseId": award.get("release_id"),
                "awardId": award.get("award_id"),
            },
        },
    }

    return {
        "record_kind": "entity",
        "record_type": "procurement.award",
        "jurisdiction_iso": jurisdiction_iso,
        "source_system": source_system,
        "source_ref": _min_ocds_ref(ocds_ref),
        "payload": payload,
    }


def contract_build_request(contract: JsonObj, *, ocds_ref: JsonObj) -> JsonObj:
    """Output single contract build request."""
    if contract.get("kind") != "contract":
        raise ValueError(f"Expected kind=contract, got {contract.get('kind')}")

    jurisdiction_iso = _require_str(contract, "jurisdiction_iso")
    source_system = _require_str(contract, "source_system")

    payload: JsonObj = {
        "jurisdictionIso": jurisdiction_iso,
        "entityType": "contract",
        "contract": {
            "contractId": contract.get("contract_id"),
            "awardId": contract.get("award_id"),
            "title": contract.get("title"),
            "description": contract.get("description"),
            "status": contract.get("status"),
            "dateSigned": contract.get("date_signed"),
            "period": _maybe_dict(contract, "period"),
            "value": _maybe_dict(contract, "value"),
            "relatedLots": contract.get("related_lots")
            if isinstance(contract.get("related_lots"), list)
            else [],
            "implementation": _maybe_dict(contract, "implementation"),
        },
        "source": {
            "sourceSystem": source_system,
            "sourceKind": "ocds",
            "ocds": _min_ocds_ref(ocds_ref),
            "contract": {
                "ocid": contract.get("ocid"),
                "releaseId": contract.get("release_id"),
                "contractId": contract.get("contract_id"),
                "awardId": contract.get("award_id"),
            },
        },
    }

    return {
        "record_kind": "entity",
        "record_type": "procurement.contract",
        "jurisdiction_iso": jurisdiction_iso,
        "source_system": source_system,
        "source_ref": _min_ocds_ref(ocds_ref),
        "payload": payload,
    }


def link_stub_requests(
    *,
    ocds_ref: JsonObj,
    buyer_request: JsonObj | None,
    supplier_requests: list[JsonObj],
    tender_request: JsonObj | None,
    award_requests: list[JsonObj],
    contract_requests: list[JsonObj],
) -> list[JsonObj]:
    """Emit conservative link stubs between the procurement spine records."""
    src = _min_ocds_ref(ocds_ref)

    buyer_key = _endpoint_key(buyer_request)
    tender_key = _endpoint_key(tender_request)

    supplier_keys = _collect_supplier_keys(supplier_requests)

    award_keys_by_award_id = _index_awards_by_award_id(award_requests)
    contract_pairs = _iter_contract_award_pairs(contract_requests)

    links: list[JsonObj] = []
    links.extend(_buyer_to_tender_links(src, buyer_key, tender_key))
    links.extend(_supplier_to_award_links(src, supplier_keys, award_requests))
    links.extend(_award_to_contract_links(src, award_keys_by_award_id, contract_pairs))
    return links


def _buyer_to_tender_links(
    src: JsonObj,
    buyer_key: JsonObj | None,
    tender_key: JsonObj | None,
) -> list[JsonObj]:
    if not buyer_key or not tender_key:
        return []
    return [
        {
            "record_kind": "relationship_stub",
            "record_type": "procurement.link.buyer_to_tender",
            "source_ref": src,
            "endpoints": {"from": buyer_key, "to": tender_key},
        }
    ]


def _collect_supplier_keys(supplier_requests: list[JsonObj]) -> list[JsonObj]:
    keys = [_endpoint_key(r) for r in supplier_requests]
    return [k for k in keys if k]


def _supplier_to_award_links(
    src: JsonObj,
    supplier_keys: list[JsonObj],
    award_requests: list[JsonObj],
) -> list[JsonObj]:
    if not supplier_keys:
        return []

    links: list[JsonObj] = []
    for a in award_requests:
        award_key = _endpoint_key(a)
        if not award_key:
            continue
        for sk in supplier_keys:
            links.append(
                {
                    "record_kind": "relationship_stub",
                    "record_type": "procurement.link.supplier_to_award",
                    "source_ref": src,
                    "endpoints": {"from": sk, "to": award_key},
                }
            )
    return links


def _index_awards_by_award_id(award_requests: list[JsonObj]) -> dict[str, JsonObj]:
    out: dict[str, JsonObj] = {}
    for a in award_requests:
        aid = _get_award_id(a)
        if aid:
            out[aid] = a
    return out


def _iter_contract_award_pairs(contract_requests: list[JsonObj]) -> list[tuple[JsonObj, str]]:
    """Return list of (contract_request, award_id) for contracts that reference an award."""
    out: list[tuple[JsonObj, str]] = []
    for c in contract_requests:
        aid = _get_contract_award_id(c)
        if isinstance(aid, str) and aid:
            out.append((c, aid))
    return out


def _award_to_contract_links(
    src: JsonObj,
    award_by_award_id: dict[str, JsonObj],
    contract_pairs: list[tuple[JsonObj, str]],
) -> list[JsonObj]:
    links: list[JsonObj] = []
    for contract_req, award_id in contract_pairs:
        award_req = award_by_award_id.get(award_id)
        if not award_req:
            continue

        from_key = _endpoint_key(award_req)
        to_key = _endpoint_key(contract_req)
        if not from_key or not to_key:
            continue

        links.append(
            {
                "record_kind": "relationship_stub",
                "record_type": "procurement.link.award_to_contract",
                "source_ref": src,
                "endpoints": {"from": from_key, "to": to_key},
            }
        )
    return links


def _endpoint_key(req: JsonObj | None) -> JsonObj | None:
    """Produce a stable endpoint key from a build request.

    This is not a CEP id. It is an internal key used for link stubs.
    """
    if not req or not isinstance(req, dict):
        return None
    rt = req.get("record_type")
    payload = req.get("payload") if isinstance(req.get("payload"), dict) else None
    if not isinstance(rt, str) or payload is None:
        return None

    if rt == "procurement.buyer":
        src_party_id = _deep_get(payload, ["source", "party", "partyId"])
        return {"type": "buyer", "partyId": src_party_id}

    if rt == "procurement.supplier":
        src_party_id = _deep_get(payload, ["source", "party", "partyId"])
        return {"type": "supplier", "partyId": src_party_id}

    if rt == "procurement.tender":
        tid = _deep_get(payload, ["tender", "tenderId"])
        return {"type": "tender", "tenderId": tid}

    if rt == "procurement.award":
        aid = _deep_get(payload, ["award", "awardId"])
        return {"type": "award", "awardId": aid}

    if rt == "procurement.contract":
        cid = _deep_get(payload, ["contract", "contractId"])
        return {"type": "contract", "contractId": cid}

    return {"type": rt}


def _get_award_id(req: JsonObj) -> str | None:
    payload = req.get("payload")
    if isinstance(payload, dict):
        aid = _deep_get(payload, ["award", "awardId"])
        return aid if isinstance(aid, str) else None
    return None


def _get_contract_id(req: JsonObj) -> str | None:
    payload = req.get("payload")
    if isinstance(payload, dict):
        cid = _deep_get(payload, ["contract", "contractId"])
        return cid if isinstance(cid, str) else None
    return None


def _get_contract_award_id(req: JsonObj) -> str | None:
    payload = req.get("payload")
    if isinstance(payload, dict):
        aid = _deep_get(payload, ["contract", "awardId"])
        return aid if isinstance(aid, str) else None
    return None


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


def _deep_get(obj: Any, keys: list[str]) -> Any:
    cur = obj
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur
