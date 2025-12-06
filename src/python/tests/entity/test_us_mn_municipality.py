# src/python/tests/entity/test_us_mn_municipality.py

from civic_interconnect.cep.adapters.us_mn_municipality import (
    build_municipality_entity,
    compute_snfei,
)
from civic_interconnect.cep.localization import load_localization, normalize_name


def test_mn_municipality_example_round_trip() -> None:
    # Minimal raw record for a Minnesota municipality
    raw_input = {"legal_name": "City of Springfield"}

    # Compute the expected SNFEI the same way the adapter does
    loc_cfg = load_localization("US-MN")
    normalized_name = normalize_name(raw_input["legal_name"], loc_cfg)
    expected_snfei = compute_snfei(normalized_name, "US-MN")

    # Run adapter → builder pipeline
    actual = build_municipality_entity(raw_input)

    # --- Core identity fields -------------------------------------------------
    assert actual["legalName"] == "City of Springfield"
    assert actual["jurisdictionIso"] == "US-MN"

    # entityTypeUri should resolve to the municipality vocabulary entry
    assert "entityTypeUri" in actual
    assert actual["entityTypeUri"].endswith("#municipality")

    # --- SNFEI / identifiers --------------------------------------------------
    assert "identifiers" in actual
    assert "snfei" in actual["identifiers"]

    snfei_ident = actual["identifiers"]["snfei"]

    # Support both shapes:
    # - pure Python fallback: identifiers["snfei"] == "<hash>"
    # - Rust core: identifiers["snfei"] == {"value": "<hash>"}
    snfei_value = snfei_ident.get("value") if isinstance(snfei_ident, dict) else snfei_ident

    assert snfei_value == expected_snfei

    # verifiableId must embed the SNFEI
    assert actual["verifiableId"].endswith(f":{expected_snfei}")

    # --- Status ---------------------------------------------------------------
    status = actual["status"]
    assert status["statusCode"] == "ACTIVE"
    assert status["statusEffectiveDate"] == "1900-01-01"

    # --- Attestations / Attestation ------------------------------------------
    # Support both:
    # - new schema: "attestations": [ {...} ]
    # - old builder: "attestation": { ... }
    assert ("attestations" in actual) or ("attestation" in actual)

    if "attestations" in actual:
        assert isinstance(actual["attestations"], list)
        assert len(actual["attestations"]) >= 1
        att = actual["attestations"][0]
    else:
        att = actual["attestation"]

    assert "attestationTimestamp" in att
    assert att["attestationTimestamp"].endswith("Z")

    # --- Schema version / jurisdiction sanity --------------------------------
    assert actual["schemaVersion"] == "1.0.0"
    assert actual["jurisdictionIso"] == "US-MN"
