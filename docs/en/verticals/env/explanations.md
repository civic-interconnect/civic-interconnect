# CEE Environmental Compliance Risk Explanations

Module: `civic_interconnect.cee.environment.risk_explanations`

Explanation type: `FACILITY_RISK_PRIORITY`

This module builds CEE `ExplanationBundle` objects explaining why a
facility is placed into a higher-priority monitoring or mitigation tier,
with emphasis on risk and harm reduction.

The evidence inputs typically include:

- Number of violations in a specified time window
- Severity of violations or exceedances
- Time since last violation
- Distance to sensitive receptors (schools, hospitals, water bodies)
- Sector-level inherent risk category

The resulting `ExplanationBundle` objects attach to CEP `facility`
entities and provide clear, structured reasoning for prioritization.

See `examples/verticals/env/cee/` for illustrative examples.
