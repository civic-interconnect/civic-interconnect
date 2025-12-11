"""SME-friendly explanation builders.

Path: src/python/src/civic_interconnect/cee/sme/sme_explanations.py
"""

from typing import Any

from civic_interconnect.cee.types import AttributionSet, EvidenceSet, ExplanationBundle


def build_sme_evidence(lot_entity: dict[str, Any]) -> EvidenceSet:
    """Build an EvidenceSet describing why a lot is SME-friendly.

    This is a scaffold; the internal structure will follow the
    CEE evidence-set schema.
    """
    # TODO: extract estimated value, procedure type, etc.
    raise NotImplementedError("build_sme_evidence is not implemented yet.")


def build_sme_attribution(rule_version: str) -> AttributionSet:
    """Build an AttributionSet for the SME-friendly rule."""
    # TODO: include model id, version, responsible agent, timestamp
    raise NotImplementedError("build_sme_attribution is not implemented yet.")


def build_sme_explanation_bundle(
    lot_entity: dict[str, Any],
) -> ExplanationBundle:
    """Build an ExplanationBundle for a SME-friendly lot.

    This function should:
    - Construct an EvidenceSet
    - Construct an AttributionSet
    - Assemble an ExplanationBundle with a narrative headline
    """
    # TODO: call build_sme_evidence and build_sme_attribution
    raise NotImplementedError("build_sme_explanation_bundle is not implemented yet.")
