"""Adapter: OCDS-like release -> CEP Procurement SME vertical slice.

Location:
    civic_interconnect.cep.adapters.procurement.sme.adapter

This adapter produces:
    - buyer entity
    - tender entity
    - lot entities
    - contract entities
    - simple supplier-in-contract relationships

Identity strategy (first vertical slice):
    - buyer SNFEI = hash(jurisdictionIso + legalNameNormalized)
    - lot SNFEI   = hash(buyerSnfei + tenderId + lotId)
    - contract    = hash(buyerSnfei + contractId)

Schema alignment:
    Produces CEP-shaped dicts (not envelopes yet). Attestation added by base class.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from civic_interconnect.cep.adapters.base import (
    Adapter,
    AdapterContext,
    AdapterKey,
    SimpleEntityAdapter,
    registry,
)

JsonDict = dict[str, Any]


# ---------------------------------------------------------------------------
# Adapter Key
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProcurementSmeAdapterKey(AdapterKey):
    """Typed key for this adapter."""


# ---------------------------------------------------------------------------
# Main Adapter
# ---------------------------------------------------------------------------


class ProcurementSmeAdapter(Adapter):
    """Adapter for procurement data in the SME vertical slice.

    From raw OCDS-like release -> canonical record -> aligned CEP entities ->
    identity computation -> attestation.

    Future refinements:
      - wrap outputs in ENTITY / RELATIONSHIP envelopes
      - validate against CEP procurement schemas
      - expand relationships (lot-tender, buyer-tender, etc.)
    """

    key: AdapterKey = ProcurementSmeAdapterKey(
        domain="procurement",
        jurisdiction="EU",  # SME vertical slice uses EU procurement patterns
        source_system="ocds-like",
        version="0.1.0",
    )

    def __init__(self, context: AdapterContext | None = None) -> None:
        """Initialize adapter with optional context."""
        super().__init__(context=context)

    # ------------------------------------------------------------------
    # Step 1 - Canonicalization
    # ------------------------------------------------------------------

    def canonicalize(self, raw: Any) -> JsonDict:
        """Normalize an OCDS-style release into a minimal internal representation."""
        if not isinstance(raw, Mapping):
            raise TypeError("ProcurementSmeAdapter expects a mapping as input.")

        # Buyer
        buyer_raw = raw.get("buyer") or {}
        buyer_name = str(buyer_raw.get("name") or "").strip()
        buyer_id = str(buyer_raw.get("id") or "").strip()
        buyer_country = (
            buyer_raw.get("address", {}).get("countryName")
            or buyer_raw.get("address", {}).get("countryCode")
            or "EU"
        )
        buyer_country = str(buyer_country).strip()

        # Tender
        tender_raw = raw.get("tender") or {}
        tender_id = str(tender_raw.get("id") or "").strip()
        tender_title = str(tender_raw.get("title") or "").strip()
        procurement_method = str(tender_raw.get("procurementMethod") or "").strip()

        tender_value = tender_raw.get("value") or {}
        tender_amount = tender_value.get("amount")
        tender_currency = tender_value.get("currency")

        # Lots
        lots = []
        for lot in tender_raw.get("lots") or []:
            lot_id = str(lot.get("id") or "").strip()
            lot_title = str(lot.get("title") or tender_title).strip()
            lv = lot.get("value") or {}
            amount = lv.get("amount", tender_amount)
            currency = lv.get("currency", tender_currency)
            lots.append(
                {
                    "lotId": lot_id,
                    "title": lot_title,
                    "estimatedValue": amount,
                    "currency": currency,
                    "smeTargeted": bool(lot.get("smeTargeted", False)),
                }
            )

        # Awards -> simplified contract structures
        contracts = []
        for award in raw.get("awards") or []:
            award_id = str(award.get("id") or "").strip()
            suppliers = award.get("suppliers") or []
            value_raw = award.get("value") or {}
            amount = value_raw.get("amount")
            currency = value_raw.get("currency")

            normalized_suppliers = []
            for s in suppliers:
                nm = str(s.get("name") or "").strip()
                sid = str(s.get("id") or "").strip()
                normalized_suppliers.append(
                    {
                        "supplierId": sid,
                        "legalName": nm,
                        "legalNameNormalized": nm.lower(),
                        "jurisdictionIso": buyer_country,
                    }
                )

            contracts.append(
                {
                    "contractId": award_id,
                    "relatedLotIds": [str(x) for x in award.get("relatedLots", [])],
                    "finalValue": amount,
                    "currency": currency,
                    "suppliers": normalized_suppliers,
                }
            )

        return {
            "buyer": {
                "buyerId": buyer_id,
                "legalName": buyer_name,
                "legalNameNormalized": buyer_name.lower(),
                "jurisdictionIso": buyer_country,
            },
            "tender": {
                "tenderId": tender_id,
                "title": tender_title,
                "procedureType": procurement_method,
                "estimatedValue": tender_amount,
                "currency": tender_currency,
            },
            "lots": lots,
            "contracts": contracts,
        }

    # ------------------------------------------------------------------
    # Step 2 - Schema Alignment
    # ------------------------------------------------------------------

    def align_schema(self, canonical: JsonDict) -> JsonDict:
        """Map canonical structures into CEP-shaped entities."""
        buyer = canonical["buyer"]
        tender = canonical["tender"]

        # Buyer entity
        buyer_entity = {
            "entityType": "procurement.buyer",
            "jurisdictionIso": buyer["jurisdictionIso"],
            "legalName": buyer["legalName"],
            "legalNameNormalized": buyer["legalNameNormalized"],
            "identifiers": {
                "sourceBuyerId": {"value": buyer["buyerId"]},
                "snfei": {},
            },
        }

        # Tender
        tender_entity = {
            "entityType": "procurement.tender",
            "tenderId": tender["tenderId"],
            "title": tender["title"],
            "procedureType": tender["procedureType"],
            "estimatedValue": tender["estimatedValue"],
            "currency": tender["currency"],
        }

        # Lot entities
        lot_entities = []
        for lot in canonical.get("lots", []):
            lot_entities.append(
                {
                    "entityType": "procurement.lot",
                    "lotId": lot["lotId"],
                    "title": lot["title"],
                    "estimatedValue": {
                        "amount": lot["estimatedValue"],
                        "currency": lot["currency"],
                    },
                    "smeTargeted": lot.get("smeTargeted", False),
                    "identifiers": {
                        "sourceLotId": {"value": lot["lotId"]},
                        "snfei": {},
                    },
                }
            )

        # Contract entities + supplier relationships
        contract_entities = []
        relationships = []

        for contract in canonical.get("contracts", []):
            contract_entities.append(
                {
                    "entityType": "procurement.contract",
                    "contractId": contract["contractId"],
                    "finalValue": contract["finalValue"],
                    "currency": contract["currency"],
                    "identifiers": {
                        "sourceContractId": {"value": contract["contractId"]},
                        "snfei": {},
                    },
                }
            )
            for supplier in contract.get("suppliers", []):
                relationships.append(
                    {
                        "relationshipType": "procurement.contract-awarded-to-supplier",
                        "contractId": contract["contractId"],
                        "supplier": {
                            "entityType": "procurement.supplier",
                            "legalName": supplier["legalName"],
                            "legalNameNormalized": supplier["legalNameNormalized"],
                            "jurisdictionIso": supplier["jurisdictionIso"],
                            "identifiers": {
                                "sourceSupplierId": {"value": supplier["supplierId"]},
                                "snfei": {},
                            },
                        },
                    }
                )

        return {
            "buyer": buyer_entity,
            "tender": tender_entity,
            "lots": lot_entities,
            "contracts": contract_entities,
            "relationships": relationships,
        }

    # ------------------------------------------------------------------
    # Step 3 - Identity
    # ------------------------------------------------------------------

    def compute_identity(self, aligned: JsonDict) -> JsonDict:
        """Compute SNFEI for buyer, lots, and contracts."""
        buyer = aligned["buyer"]
        tender = aligned["tender"]
        lots = aligned.get("lots", [])
        contracts = aligned.get("contracts", [])

        # Buyer SNFEI
        buyer_proj = {
            "jurisdictionIso": buyer["jurisdictionIso"],
            "legalNameNormalized": buyer["legalNameNormalized"],
        }
        buyer_snfei = SimpleEntityAdapter._compute_snfei_from_projection(buyer_proj)
        buyer["identifiers"]["snfei"] = {"value": buyer_snfei}

        # Lots
        for lot in lots:
            lot_proj = {
                "buyerSnfei": buyer_snfei,
                "tenderId": tender["tenderId"],
                "lotId": lot["lotId"],
            }
            lot_snfei = SimpleEntityAdapter._compute_snfei_from_projection(lot_proj)
            lot["identifiers"]["snfei"] = {"value": lot_snfei}

        # Contracts
        for contract in contracts:
            proj = {
                "buyerSnfei": buyer_snfei,
                "contractId": contract["contractId"],
            }
            c_snfei = SimpleEntityAdapter._compute_snfei_from_projection(proj)
            contract["identifiers"]["snfei"] = {"value": c_snfei}

        return aligned


# Register adapter
registry.register(ProcurementSmeAdapter)
