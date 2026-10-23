"""Tests for the US FEC campaign finance adapter.

This module validates that the adapter converts FEC-style campaign finance
records into the expected attestations and identifier payloads.
"""

from civic_interconnect.cep.adapters.us_fec_campaign_finance import (
    UsFecCampaignFinanceAdapter,
)


def test_us_fec_adapter_basic_pipeline():
    """Test the basic pipeline of the US FEC Campaign Finance adapter."""
    adapter = UsFecCampaignFinanceAdapter()

    raw = {
        "donor_name": "ACME PAC",
        "amount": "1000",
        # TODO: more realistic FEC fields
    }

    result = adapter.run(raw)

    assert "attestations" in result
    assert "identifiers" in result
    assert "snfei" in result["identifiers"]
    assert result["identifiers"]["snfei"]["value"]
