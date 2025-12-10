from civic_interconnect.cep.adapters.us_mn_municipality import UsMnMunicipalityAdapter


def test_us_mn_municipality_basic_pipeline() -> None:
    adapter = UsMnMunicipalityAdapter()

    raw = {
        "legal_name": "City of Minneapolis",
        "jurisdiction_iso": "US-MN",
    }

    result1 = adapter.run(raw)
    result2 = adapter.run(raw)

    # Basic envelope fields from align_schema
    assert result1["legalName"] == "City of Minneapolis"
    assert result1["jurisdictionIso"] == "US-MN"

    # SNFEI presence
    assert "identifiers" in result1
    assert "snfei" in result1["identifiers"]
    snfei1 = result1["identifiers"]["snfei"]["value"]
    assert isinstance(snfei1, str)
    assert len(snfei1) == 64  # sha256 hex length

    # Determinism: running the pipeline twice yields same SNFEI
    snfei2 = result2["identifiers"]["snfei"]["value"]
    assert snfei1 == snfei2
