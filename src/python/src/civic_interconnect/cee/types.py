"""CEE Shared Types.

Path: src/python/src/civic_interconnect/cee/types.py
"""

from typing import Any, TypedDict


class EvidenceItem(TypedDict, total=False):
    """Evidence Item structure."""

    metric: str
    value: Any
    notes: str


class EvidenceSet(TypedDict, total=False):
    """Evidence Set structure."""

    metrics: list[EvidenceItem]
    summary: str


class AttributionEntry(TypedDict, total=False):
    """Attribution Entry structure."""

    modelId: str
    modelType: str
    version: str
    agentId: str


class AttributionSet(TypedDict, total=False):
    """Attribution Set structure."""

    entries: list[AttributionEntry]


class ExplanationBundle(TypedDict, total=False):
    """Explanation Bundle structure."""

    bundleId: str
    explanationType: str
    subjectEntityId: str
    headline: str
    narrative: str
    evidenceSet: EvidenceSet
    attributionSet: AttributionSet
