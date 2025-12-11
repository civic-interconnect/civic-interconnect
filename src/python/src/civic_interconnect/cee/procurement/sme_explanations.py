# src/python/src/civic_interconnect/cee/procurement/sme_explanations.py
"""CEE helpers for SME-friendly procurement explanations.

This module builds lightweight CEE-style explanation structures for
procurement lots that are considered SME-friendly.

It is intentionally simple and does not yet enforce the full CEE
JSON Schema shapes; instead it focuses on:
- making unit tests pass,
- keeping the design easy to refactor once CEE schemas stabilize.

Public functions:

- build_sme_evidence(lot_entity, context) -> dict
- build_sme_attribution(rule_version, agent_id) -> dict
- build_sme_explanation_bundle(lot_entity, evidence, attribution) -> dict
"""

from typing import Any

JsonDict = dict[str, Any]


EXPLANATION_TYPE = "SME_FRIENDLY_PROCUREMENT"


def _get_estimated_value_amount(lot_entity: JsonDict) -> float | None:
    """Extract the numeric estimated value from a CEP lot entity."""
    estimated = lot_entity.get("estimatedValue") or {}
    amount = estimated.get("amount")
    if isinstance(amount, (int, float)):
        return float(amount)
    return None


def _passes_value_threshold(lot_entity: JsonDict, context: JsonDict) -> bool | None:
    """Return True if the lot passes the SME value threshold rule.

    Returns:
        True if estimated value is <= threshold,
        False if it is > threshold,
        None if either value or threshold is missing.
    """
    amount = _get_estimated_value_amount(lot_entity)
    threshold = context.get("sme_value_threshold_eur")

    if amount is None or not isinstance(threshold, (int, float)):
        return None

    return float(amount) <= float(threshold)


def build_sme_evidence(lot_entity: JsonDict, context: JsonDict) -> JsonDict:
    """Build an evidence structure for SME-friendly classification.

    The structure is intentionally simple and test-friendly. It includes:

    - metrics: numeric and categorical fields used by the rule
    - isSmeFriendlyByValue: optional boolean flag (if data is present)
    - source: basic provenance back to the original notice
    """
    amount = _get_estimated_value_amount(lot_entity)
    currency = (lot_entity.get("estimatedValue") or {}).get("currency") or "EUR"

    threshold = context.get("sme_value_threshold_eur")
    procedure_type = lot_entity.get("procedureType")
    cpv_codes = lot_entity.get("cpvCodes") or []
    historical_rate = context.get("historical_sme_win_rate")

    is_sme_by_value = _passes_value_threshold(lot_entity, context)

    evidence: JsonDict = {
        "type": "SME_FRIENDLY_PROCUREMENT_EVIDENCE_V1",
        "lotId": lot_entity.get("id"),
        "metrics": {
            "estimatedValueAmount": amount,
            "estimatedValueCurrency": currency,
            "smeValueThresholdEur": threshold,
            "procedureType": procedure_type,
            "numCpvCodes": len(cpv_codes),
            "historicalSmeWinRate": historical_rate,
        },
        "source": {
            "sourceNoticeId": context.get("source_notice_id"),
            "sourceSystemUri": context.get("source_system_uri"),
        },
    }

    # Only include the flag if we have enough information to compute it.
    if is_sme_by_value is not None:
        evidence["isSmeFriendlyByValue"] = is_sme_by_value

    return evidence


def build_sme_attribution(rule_version: str, agent_id: str) -> JsonDict:
    """Build a minimal attribution structure for SME-friendly explanations.

    Args:
        rule_version: Version string for the SME rule (e.g., "1.0.0").
        agent_id: Identifier for the agent responsible for the rule/model.

    Returns:
        A dict describing the model and responsible agent.
    """
    return {
        "modelId": "sme-friendly-rule-v1",
        "modelType": "rule-based",
        "ruleVersion": rule_version,
        "developerAgentId": agent_id,
    }


def _build_headline(is_sme_friendly: bool | None) -> str:
    """Create a short headline for the explanation."""
    if is_sme_friendly is True:
        return "This lot is highlighted as SME-friendly."
    if is_sme_friendly is False:
        return "This lot does not meet the SME-friendly criteria."
    return "SME-friendly assessment for this lot is inconclusive."


def _build_narrative(
    lot_entity: JsonDict,
    evidence: JsonDict,
    is_sme_friendly: bool | None,
) -> str:
    """Create a simple human-readable narrative."""
    metrics = evidence.get("metrics") or {}
    amount = metrics.get("estimatedValueAmount")
    threshold = metrics.get("smeValueThresholdEur")
    procedure_type = metrics.get("procedureType")

    parts: list[str] = []

    if is_sme_friendly is True:
        parts.append(
            "This procurement lot is considered SME-friendly based on its "
            "estimated value and procedure type."
        )
    elif is_sme_friendly is False:
        parts.append(
            "This procurement lot does not meet the SME-friendly criteria based "
            "on its estimated value and procedure type."
        )
    else:
        parts.append(
            "This procurement lot has been assessed against SME-friendly "
            "criteria, but the result is inconclusive due to missing data."
        )

    if amount is not None and threshold is not None:
        parts.append(
            f"The estimated value is {amount} EUR compared to a threshold of {threshold} EUR."
        )

    if procedure_type:
        parts.append(f"The procedure type is '{procedure_type}'.")

    cpv_codes = lot_entity.get("cpvCodes") or []
    if cpv_codes:
        parts.append(
            "The lot covers the following CPV codes: "
            + ", ".join(str(code) for code in cpv_codes)
            + "."
        )

    return " ".join(parts)


def build_sme_explanation_bundle(
    lot_entity: JsonDict,
    evidence: JsonDict,
    attribution: JsonDict,
) -> JsonDict:
    """Build a complete explanation bundle for an SME-friendly assessment.

    Args:
        lot_entity: CEP lot entity dict (subject of the explanation).
        evidence: Evidence dict produced by build_sme_evidence.
        attribution: Attribution dict produced by build_sme_attribution.

    Returns:
        A dict representing an explanation bundle suitable for further
        validation once CEE schemas are in place.
    """
    subject_id = lot_entity.get("id")

    # Derive is_sme_friendly from the evidence, if present.
    is_sme_friendly = evidence.get("isSmeFriendlyByValue")
    if not isinstance(is_sme_friendly, bool):
        is_sme_friendly = None

    bundle: JsonDict = {
        "bundleId": f"cee:explanation:smeFriendly:{subject_id}",
        "subjectEntityId": subject_id,
        "explanationType": EXPLANATION_TYPE,
        "headline": _build_headline(is_sme_friendly),
        "narrative": _build_narrative(lot_entity, evidence, is_sme_friendly),
        "evidenceSet": evidence,
        "attributionSet": attribution,
    }

    return bundle
