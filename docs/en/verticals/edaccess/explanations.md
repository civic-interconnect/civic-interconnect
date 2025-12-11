# CEE Education Access and Value Explanations

Module: `civic_interconnect.cee.education.access_value_explanations`

Explanation type: `PROGRAM_ACCESS_VALUE`

This module builds CEE `ExplanationBundle` objects explaining why a
particular educational program is highlighted as an accessible and
high-value opportunity for specific learner groups.

The explanation is derived from a combination of transparent metrics,
including:

- Tuition or net price for the learner profile
- Completion rates for the program
- Earnings or employment outcomes
- Distance or travel time to campus, or online availability
- Availability of supports for target learner groups (first-gen, low-income, etc.)

The module outputs structured `ExplanationBundle` instances attached to
CEP `program` entities.

See `examples/verticals/eduaccess/cee/` for illustrative examples.
