# CEE SME-Friendly Procurement Explanations

Module: `civic_interconnect.cee.procurement.sme_explanations`

Explanation type: `SME_FRIENDLY_PROCUREMENT`

This module builds CEE `ExplanationBundle` objects that explain why a
procurement lot or contract is considered SME-friendly.

Evidence inputs typically include:

- Lot or contract estimated value compared to SME thresholds
- Procedure type (open, restricted, simplified)
- Lot structure (degree of bundling, number of CPV categories)
- Optional historical SME win patterns for similar tenders

The resulting explanation bundles attach to CEP `lot` entities and
provide transparent justification for SME suitability.

See `examples/verticals/sme/cee/` for illustrative examples.
