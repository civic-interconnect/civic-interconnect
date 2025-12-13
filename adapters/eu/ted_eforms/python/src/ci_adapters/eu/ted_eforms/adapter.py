"""EU TED eForms adapter.

This module intentionally contains orchestration only:
- parse source records
- call normalization and identity services (owned by core)
- build CEP/CEE artifacts (owned by core)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


@dataclass(frozen=True)
class AdapterResult:
    """Minimal adapter output container.

    Replace these placeholders with your real core types (envelope, entity, etc.)
    once wired into civic_interconnect core.
    """

    envelopes: list[Mapping[str, Any]]
    observations: list[Mapping[str, Any]]
    explanations: list[Mapping[str, Any]]


class TedEformsAdapter:
    """Adapter for EU TED eForms source data."""

    adapter_id = "eu/ted_eforms"

    def adapt_records(self, records: Iterable[Mapping[str, Any]]) -> AdapterResult:
        """Transform source records into CEP/CEE artifacts.

        This method must be deterministic for a given input set and configuration.
        """
        envelopes: list[Mapping[str, Any]] = []
        observations: list[Mapping[str, Any]] = []
        explanations: list[Mapping[str, Any]] = []

        for record in records:
            # 1) Parse raw record -> internal fields (keep raw values for provenance)
            parsed = record

            # 2) Normalize (call core normalization service when wired)
            normalized = parsed

            # 3) Identify (call core SNFEI/identity service when wired)
            identity = {"adapterId": self.adapter_id}

            # 4) Map to CEP/CEE shapes (use mapping helpers)
            envelope = {
                "adapterId": self.adapter_id,
                "identity": identity,
                "payload": normalized,
            }
            envelopes.append(envelope)

        return AdapterResult(
            envelopes=envelopes, observations=observations, explanations=explanations
        )
