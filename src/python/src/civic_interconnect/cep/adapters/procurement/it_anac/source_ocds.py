# src/python/src/civic_interconnect/cep/adapters/procurement/it_anac/source_ocds.py
"""Italy ANAC (OCDS) source parser.

This module reads OCDS JSON (release package or record package) and emits
normalized "procurement spine" payloads that downstream adapters can consume.

Design goals:
- Deterministic extraction (no network access here).
- Keep this as "source parsing" only: do not perform identity merges here.
- Prefer safe defaults and explicit None over guessing.

Typical usage in tests:

  from pathlib import Path
  from civic_interconnect.cep.adapters.procurement.it_anac.source_ocds import (
      iter_spine_bundles_from_path,
  )

  for bundle in iter_spine_bundles_from_path(
      Path("src/python/tests/data/procurement/it_anac/ocds_sample.jsonl"),
      jurisdiction_iso="IT",
      source_system="it_anac_ocds",
  ):
      ...

Bundle shape (stable internal contract):

{
  "source_system": "it_anac_ocds",
  "jurisdiction_iso": "IT",
  "ocds": {
    "ocid": "...",
    "release_id": "...",
    "date": "...",
    "tag": ["..."]
  },
  "buyer": { ... } | None,
  "suppliers": [ { ... }, ... ],
  "tender": { ... } | None,
  "awards": [ { ... }, ... ],
  "contracts": [ { ... }, ... ],
  "raw_release": { ... }  # optional: only if include_raw=True
}

Each of buyer/supplier/tender/award/contract objects is a "normalized payload"
dict intended for the corresponding spine adapter (buyer.py, supplier.py, etc).
"""

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

JsonObj = dict[str, Any]


@dataclass(frozen=True)
class OcdsRef:
    """Extracted OCDS reference fields from a release."""

    ocid: str | None
    release_id: str | None
    date: str | None
    tags: list[str]


def iter_spine_bundles_from_path(
    path: Path,
    *,
    jurisdiction_iso: str,
    source_system: str = "it_anac_ocds",
    include_raw: bool = False,
) -> Iterator[JsonObj]:
    """Iterate "spine bundles" from a JSON or JSONL file.

    Supported:
    - *.json  : OCDS release package or record package object
    - *.jsonl : each line is a release or a package object (we handle both)
    """
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                s = line.strip()
                if not s:
                    continue
                try:
                    obj = json.loads(s)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON on line {line_no} of {path}: {e}") from e
                yield from iter_spine_bundles_from_obj(
                    obj,
                    jurisdiction_iso=jurisdiction_iso,
                    source_system=source_system,
                    include_raw=include_raw,
                )
        return

    if path.suffix.lower() == ".json":
        obj = json.loads(path.read_text(encoding="utf-8"))
        yield from iter_spine_bundles_from_obj(
            obj,
            jurisdiction_iso=jurisdiction_iso,
            source_system=source_system,
            include_raw=include_raw,
        )
        return

    raise ValueError(f"Unsupported file type: {path}")


def iter_spine_bundles_from_obj(
    obj: Any,
    *,
    jurisdiction_iso: str,
    source_system: str = "it_anac_ocds",
    include_raw: bool = False,
) -> Iterator[JsonObj]:
    """Iterate spine bundles from a decoded JSON object.

    Accepts:
    - OCDS release object
    - OCDS release package (has "releases")
    - OCDS record package (has "records", each has "releases")
    """
    for release in _iter_releases(obj):
        bundle = _release_to_spine_bundle(
            release,
            jurisdiction_iso=jurisdiction_iso,
            source_system=source_system,
            include_raw=include_raw,
        )
        if bundle is not None:
            yield bundle


def _iter_releases(obj: Any) -> Iterator[JsonObj]:
    """Yield OCDS release dicts from a release, release package, or record package."""
    if not isinstance(obj, dict):
        return

    if _is_release_package(obj):
        yield from _iter_release_package(obj)
        return

    if _is_record_package(obj):
        yield from _iter_record_package(obj)
        return

    if _looks_like_release(obj):
        yield obj  # type: ignore[misc]


def _is_release_package(obj: JsonObj) -> bool:
    return isinstance(obj.get("releases"), list)


def _is_record_package(obj: JsonObj) -> bool:
    return isinstance(obj.get("records"), list)


def _iter_release_package(pkg: JsonObj) -> Iterator[JsonObj]:
    releases = pkg.get("releases")
    if not isinstance(releases, list):
        return
    for r in releases:
        if isinstance(r, dict):
            yield r


def _iter_record_package(pkg: JsonObj) -> Iterator[JsonObj]:
    records = pkg.get("records")
    if not isinstance(records, list):
        return

    for rec in records:
        if not isinstance(rec, dict):
            continue
        yield from _iter_record_releases(rec)


def _iter_record_releases(rec: JsonObj) -> Iterator[JsonObj]:
    releases = rec.get("releases")
    if not isinstance(releases, list):
        return
    for r in releases:
        if isinstance(r, dict):
            yield r


def _looks_like_release(obj: JsonObj) -> bool:
    # Most releases have ocid and at least one of: id, date, tag, tender, awards, contracts.
    if "ocid" not in obj:
        return False
    for k in ("id", "date", "tag", "tender", "awards", "contracts", "parties", "buyer"):
        if k in obj:
            return True
    return True


def _release_to_spine_bundle(
    release: JsonObj,
    *,
    jurisdiction_iso: str,
    source_system: str,
    include_raw: bool,
) -> JsonObj | None:
    ref = _extract_ocds_ref(release)

    parties = release.get("parties")
    parties_list: list[JsonObj] = parties if isinstance(parties, list) else []

    buyer_payload = _extract_buyer_payload(
        release, parties_list, jurisdiction_iso=jurisdiction_iso, source_system=source_system
    )
    supplier_payloads = _extract_supplier_payloads(
        release, parties_list, jurisdiction_iso=jurisdiction_iso, source_system=source_system
    )

    tender_obj = release.get("tender") if isinstance(release.get("tender"), dict) else None
    tender_payload = _normalize_tender(
        tender_obj, ref=ref, jurisdiction_iso=jurisdiction_iso, source_system=source_system
    )

    awards_raw = release.get("awards")
    awards_list: list[Any] = awards_raw if isinstance(awards_raw, list) else []
    award_payloads = [
        _normalize_award(a, ref=ref, jurisdiction_iso=jurisdiction_iso, source_system=source_system)
        for a in awards_list
        if isinstance(a, dict)
    ]

    contracts_raw = release.get("contracts")
    contracts_list: list[Any] = contracts_raw if isinstance(contracts_raw, list) else []
    contract_payloads = [
        _normalize_contract(
            c, ref=ref, jurisdiction_iso=jurisdiction_iso, source_system=source_system
        )
        for c in contracts_list
        if isinstance(c, dict)
    ]

    bundle: JsonObj = {
        "source_system": source_system,
        "jurisdiction_iso": jurisdiction_iso,
        "ocds": {
            "ocid": ref.ocid,
            "release_id": ref.release_id,
            "date": ref.date,
            "tag": ref.tags,
        },
        "buyer": buyer_payload,
        "suppliers": supplier_payloads,
        "tender": tender_payload,
        "awards": award_payloads,
        "contracts": contract_payloads,
    }
    if include_raw:
        bundle["raw_release"] = release

    return bundle


def _extract_ocds_ref(release: JsonObj) -> OcdsRef:
    ocid = release.get("ocid") if isinstance(release.get("ocid"), str) else None
    release_id = release.get("id") if isinstance(release.get("id"), str) else None
    date = release.get("date") if isinstance(release.get("date"), str) else None
    tags_raw = release.get("tag")
    tags: list[str] = []
    if isinstance(tags_raw, list):
        tags = [t for t in tags_raw if isinstance(t, str)]
    elif isinstance(tags_raw, str):
        tags = [tags_raw]
    return OcdsRef(ocid=ocid, release_id=release_id, date=date, tags=tags)


def _extract_buyer_payload(
    release: JsonObj,
    parties: Sequence[JsonObj],
    *,
    jurisdiction_iso: str,
    source_system: str,
) -> JsonObj | None:
    # Prefer release["buyer"] if present.
    buyer_obj = release.get("buyer") if isinstance(release.get("buyer"), dict) else None
    if buyer_obj is not None:
        return _normalize_party(
            party=buyer_obj,
            role="buyer",
            jurisdiction_iso=jurisdiction_iso,
            source_system=source_system,
            ocds_party_source="release.buyer",
        )

    # Otherwise, find a party with role "buyer".
    for p in parties:
        roles = p.get("roles")
        if isinstance(roles, list) and any(isinstance(r, str) and r == "buyer" for r in roles):
            return _normalize_party(
                party=p,
                role="buyer",
                jurisdiction_iso=jurisdiction_iso,
                source_system=source_system,
                ocds_party_source="release.parties",
            )

    return None


def _extract_supplier_payloads(
    release: JsonObj,
    parties: Sequence[JsonObj],
    *,
    jurisdiction_iso: str,
    source_system: str,
) -> list[JsonObj]:
    suppliers: list[JsonObj] = []

    # Primary source: awards[].suppliers
    awards_raw = release.get("awards")
    awards_list: list[Any] = awards_raw if isinstance(awards_raw, list) else []
    for a in awards_list:
        if not isinstance(a, dict):
            continue
        sup_list = a.get("suppliers")
        if not isinstance(sup_list, list):
            continue
        for s in sup_list:
            if isinstance(s, dict):
                suppliers.append(
                    _normalize_party(
                        party=s,
                        role="supplier",
                        jurisdiction_iso=jurisdiction_iso,
                        source_system=source_system,
                        ocds_party_source="release.awards[].suppliers",
                    )
                )

    # Secondary source: parties with role "supplier"
    for p in parties:
        roles = p.get("roles")
        if isinstance(roles, list) and any(isinstance(r, str) and r == "supplier" for r in roles):
            suppliers.append(
                _normalize_party(
                    party=p,
                    role="supplier",
                    jurisdiction_iso=jurisdiction_iso,
                    source_system=source_system,
                    ocds_party_source="release.parties",
                )
            )

    return _dedupe_parties_by_key(suppliers)


def _dedupe_parties_by_key(parties: list[JsonObj]) -> list[JsonObj]:
    """Deduplicate by (party_id, name) to stabilize output."""
    seen: set[tuple[str, str]] = set()
    out: list[JsonObj] = []
    for p in parties:
        pid = p.get("party_id") or ""
        name = p.get("legal_name") or ""
        pid = pid if isinstance(pid, str) else ""
        name = name if isinstance(name, str) else ""
        key = (pid, name)
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def _normalize_party(
    party: JsonObj,
    role: str,
    *,
    jurisdiction_iso: str,
    source_system: str,
    ocds_party_source: str,
) -> JsonObj:
    """Normalize an OCDS OrganizationReference / party object into a minimal payload.

    This is intentionally minimal. Downstream adapters can enrich and localize.
    """
    pid = party.get("id") if isinstance(party.get("id"), str) else None
    name = party.get("name") if isinstance(party.get("name"), str) else None

    # OCDS parties can include identifiers/address/contactPoint
    identifiers = party.get("identifier") if isinstance(party.get("identifier"), dict) else None
    additional_ids = (
        party.get("additionalIdentifiers")
        if isinstance(party.get("additionalIdentifiers"), list)
        else []
    )
    address = party.get("address") if isinstance(party.get("address"), dict) else None
    contact = party.get("contactPoint") if isinstance(party.get("contactPoint"), dict) else None

    return {
        "kind": "party",
        "role": role,
        "source_system": source_system,
        "jurisdiction_iso": jurisdiction_iso,
        "ocds_party_source": ocds_party_source,
        "party_id": pid,
        "legal_name": name,
        "identifier": identifiers,
        "additional_identifiers": [x for x in (additional_ids or []) if isinstance(x, dict)],
        "address": address,
        "contact_point": contact,
    }


def _normalize_tender(
    tender: JsonObj | None,
    *,
    ref: OcdsRef,
    jurisdiction_iso: str,
    source_system: str,
) -> JsonObj | None:
    if tender is None:
        return None

    return {
        "kind": "tender",
        "source_system": source_system,
        "jurisdiction_iso": jurisdiction_iso,
        "ocid": ref.ocid,
        "release_id": ref.release_id,
        "tender_id": tender.get("id") if isinstance(tender.get("id"), str) else None,
        "title": tender.get("title") if isinstance(tender.get("title"), str) else None,
        "description": tender.get("description")
        if isinstance(tender.get("description"), str)
        else None,
        "status": tender.get("status") if isinstance(tender.get("status"), str) else None,
        "procurement_method": tender.get("procurementMethod")
        if isinstance(tender.get("procurementMethod"), str)
        else None,
        "procurement_method_details": tender.get("procurementMethodDetails")
        if isinstance(tender.get("procurementMethodDetails"), str)
        else None,
        "main_procurement_category": tender.get("mainProcurementCategory")
        if isinstance(tender.get("mainProcurementCategory"), str)
        else None,
        "value": tender.get("value") if isinstance(tender.get("value"), dict) else None,
        "items": tender.get("items") if isinstance(tender.get("items"), list) else [],
        "lots": tender.get("lots") if isinstance(tender.get("lots"), list) else [],
        "tender_period": tender.get("tenderPeriod")
        if isinstance(tender.get("tenderPeriod"), dict)
        else None,
    }


def _normalize_award(
    award: JsonObj,
    *,
    ref: OcdsRef,
    jurisdiction_iso: str,
    source_system: str,
) -> JsonObj:
    return {
        "kind": "award",
        "source_system": source_system,
        "jurisdiction_iso": jurisdiction_iso,
        "ocid": ref.ocid,
        "release_id": ref.release_id,
        "award_id": award.get("id") if isinstance(award.get("id"), str) else None,
        "title": award.get("title") if isinstance(award.get("title"), str) else None,
        "description": award.get("description")
        if isinstance(award.get("description"), str)
        else None,
        "status": award.get("status") if isinstance(award.get("status"), str) else None,
        "date": award.get("date") if isinstance(award.get("date"), str) else None,
        "value": award.get("value") if isinstance(award.get("value"), dict) else None,
        "suppliers": award.get("suppliers") if isinstance(award.get("suppliers"), list) else [],
        "items": award.get("items") if isinstance(award.get("items"), list) else [],
        "related_lots": award.get("relatedLots")
        if isinstance(award.get("relatedLots"), list)
        else [],
    }


def _normalize_contract(
    contract: JsonObj,
    *,
    ref: OcdsRef,
    jurisdiction_iso: str,
    source_system: str,
) -> JsonObj:
    return {
        "kind": "contract",
        "source_system": source_system,
        "jurisdiction_iso": jurisdiction_iso,
        "ocid": ref.ocid,
        "release_id": ref.release_id,
        "contract_id": contract.get("id") if isinstance(contract.get("id"), str) else None,
        "award_id": contract.get("awardID") if isinstance(contract.get("awardID"), str) else None,
        "title": contract.get("title") if isinstance(contract.get("title"), str) else None,
        "description": contract.get("description")
        if isinstance(contract.get("description"), str)
        else None,
        "status": contract.get("status") if isinstance(contract.get("status"), str) else None,
        "period": contract.get("period") if isinstance(contract.get("period"), dict) else None,
        "value": contract.get("value") if isinstance(contract.get("value"), dict) else None,
        "date_signed": contract.get("dateSigned")
        if isinstance(contract.get("dateSigned"), str)
        else None,
        "related_lots": contract.get("relatedLots")
        if isinstance(contract.get("relatedLots"), list)
        else [],
        "implementation": contract.get("implementation")
        if isinstance(contract.get("implementation"), dict)
        else None,
    }
