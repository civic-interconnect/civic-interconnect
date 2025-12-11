# src/python/tests/cee/test_procurement_sme_explanations.py

from civic_interconnect.cee.procurement import sme_explanations
import pytest


def _make_example_lot_entity():
    """Return a minimal CEP lot entity dict for testing SME explanations."""
    return {
        "id": "cep-entity:procurement:lot:example-1",
        "schemaVersion": "1.0.0",
        "entityType": "procurement.lot",
        "jurisdictionIso": "EU",
        "tenderId": "EU-EXAMPLE-TENDER-001",
        "lotId": "LOT-001",
        "cpvCodes": ["30200000"],
        "estimatedValue": {
            "amount": 180000.0,
            "currency": "EUR",
        },
        "procedureType": "open",
        "metadata": {},
    }


def _make_example_context():
    """Return a minimal context dict that a rule function might use."""
    return {
        "sme_value_threshold_eur": 250000.0,
        "allowed_procedure_types": ["open", "restricted", "simplified"],
        # Optional historic SME win rate, if used by the rule.
        "historical_sme_win_rate": 0.42,
        "source_notice_id": "EU-EXAMPLE-NOTICE-001",
        "source_system_uri": "https://example.eu/notice/EU-EXAMPLE-NOTICE-001",
    }


@pytest.mark.parametrize("amount,expected_flag", [(180000.0, True), (300000.0, False)])
def test_build_sme_evidence_reflects_value_threshold(amount, expected_flag):
    """Evidence set should reflect whether the lot passes the SME threshold rule."""
    lot = _make_example_lot_entity()
    lot["estimatedValue"]["amount"] = amount
    context = _make_example_context()

    # We assume the helper exposes build_sme_evidence; adjust if your API differs.
    assert hasattr(sme_explanations, "build_sme_evidence"), (
        "Expected build_sme_evidence in sme_explanations module."
    )

    evidence = sme_explanations.build_sme_evidence(lot, context)

    # Basic structural checks
    assert isinstance(evidence, dict)
    assert "metrics" in evidence or "evidenceItems" in evidence

    # We do not assume exact shape, but we expect the threshold to appear somewhere.
    # If you have a fixed schema, tighten these assertions later.
    serialized = repr(evidence)
    assert "180000" in serialized or "300000" in serialized
    assert "250000" in serialized or "sme_value_threshold" in serialized

    # Optional: if you include a boolean flag in the evidence, assert it.
    if "isSmeFriendlyByValue" in evidence:
        assert evidence["isSmeFriendlyByValue"] is expected_flag


def test_build_sme_explanation_bundle_structure():
    """Explanation bundle for an SME friendly lot should have expected core fields."""
    lot = _make_example_lot_entity()
    context = _make_example_context()

    assert hasattr(sme_explanations, "build_sme_evidence"), (
        "Expected build_sme_evidence in sme_explanations module."
    )
    assert hasattr(sme_explanations, "build_sme_attribution"), (
        "Expected build_sme_attribution in sme_explanations module."
    )
    assert hasattr(sme_explanations, "build_sme_explanation_bundle"), (
        "Expected build_sme_explanation_bundle in sme_explanations module."
    )

    evidence = sme_explanations.build_sme_evidence(lot, context)
    attribution = sme_explanations.build_sme_attribution(
        rule_version="1.0.0",
        agent_id="cep-agent:procurement:sme-friendly-rule",
    )
    bundle = sme_explanations.build_sme_explanation_bundle(
        lot_entity=lot,
        evidence=evidence,
        attribution=attribution,
    )

    assert isinstance(bundle, dict)

    # Minimal structural assertions. Tighten these once the schema is stable.
    assert "bundleId" in bundle
    assert "subjectEntityId" in bundle
    assert bundle["subjectEntityId"] == lot["id"]

    assert "explanationType" in bundle
    assert bundle["explanationType"] == "SME_FRIENDLY_PROCUREMENT"

    assert "headline" in bundle
    assert "narrative" in bundle

    assert "evidenceSet" in bundle
    assert "attributionSet" in bundle
