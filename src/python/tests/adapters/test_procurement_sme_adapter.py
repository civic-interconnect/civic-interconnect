"""Test module for Procurement SME adapter.

This module contains tests for the ProcurementSmeAdapter to verify
its ability to process procurement data related to SME-targeted contracts.
"""

from civic_interconnect.cep.adapters.base import AdapterContext
from civic_interconnect.cep.adapters.procurement.sme.adapter import (
    ProcurementSmeAdapter,
)


def test_procurement_sme_adapter_basic_run() -> None:
    """Basic smoke test: ProcurementSmeAdapter processes a minimal raw input."""
    raw = {
        "buyer": {
            "name": "Example City Council",
            "id": "EC-123",
            "address": {"countryName": "ES"},
        },
        "tender": {
            "id": "T1",
            "title": "IT Support Services",
            "procurementMethod": "open",
            "value": {"amount": 180000, "currency": "EUR"},
            "lots": [
                {
                    "id": "LOT-1",
                    "title": "Helpdesk services",
                    "value": {"amount": 90000, "currency": "EUR"},
                    "smeTargeted": True,
                }
            ],
        },
        "awards": [
            {
                "id": "AW1",
                "relatedLots": ["LOT-1"],
                "value": {"amount": 85000, "currency": "EUR"},
                "suppliers": [
                    {"id": "SUP-1", "name": "SmallTech Ltd"},
                ],
            }
        ],
    }

    adapter = ProcurementSmeAdapter(context=AdapterContext())
    result = adapter.run(raw)

    # Very soft assertions for now; tighten as schemas settle.
    assert "buyer" in result
    assert result["buyer"]["identifiers"]["snfei"]["value"]
    assert result["lots"][0]["identifiers"]["snfei"]["value"]
