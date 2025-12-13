"""Smoke tests for TedEformsAdapter."""

from ci_adapters.eu.ted_eforms.adapter import TedEformsAdapter


def test_smoke_adapt_records_returns_result():
    """Smoke test for adapt_records method."""
    adapter = TedEformsAdapter()
    result = adapter.adapt_records([{"notice_id": "N1"}])
    assert isinstance(result.envelopes, list)
    assert len(result.envelopes) == 1
    assert result.envelopes[0]["adapterId"] == "eu/ted_eforms"
