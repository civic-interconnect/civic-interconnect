# Environmental Compliance Risk and Prioritization

Vertical ID: `env`  
About file: `docs/en/04_verticals/env/about.yaml`  
Explanations: `docs/en/04_verticals/env/explanations.md`

This vertical slice explores how CEP and CEE can provide **transparent,
evidence-based explanations** for why certain facilities are **prioritized
for monitoring or mitigation**, with an emphasis on **risk and harm
reduction**.

The goal is to support smarter, fairer allocation of attention and
resources.

## Who this vertical is for

This example is designed for:

- Environmental regulators and compliance supervisors
- Corporate or facility sustainability and ESG teams
- Residents and community groups near facilities
- Researchers working with facility, inspection, and violation data

See `about.yaml` for detailed user stories and data-source notes.

## What this vertical demonstrates

- **CEP side**
  - Modeling facilities, permits, inspections, violations, sensitive areas
  - Relationships:
    - facility has permit
    - facility had inspection
    - inspection resulted in violation
    - facility near sensitive area
  - Identity strategies for facilities and related records

- **CEE side**
  - An explanation type (e.g., `FACILITY_RISK_PRIORITY`) that answers:
    > Why is this facility placed in a higher-risk monitoring tier?
  - Evidence such as:
    - violation counts and severity
    - time since last incident
    - distance to sensitive receptors (schools, hospitals, water bodies)
    - sector-level risk categories

## Files in this vertical

- Definition and intent:
  - `docs/en/04_verticals/env/about.yaml`
  - `docs/en/04_verticals/env/index.md` (this file)
  - `docs/en/04_verticals/env/explanations.md`

- Example data (planned structure):
  - `examples/environment/compliance/raw/`
    - Small slices of facility, inspection, and violation data
  - `examples/environment/compliance/cep/`
    - CEP entities and relationships for facilities and permits
  - `examples/environment/compliance/cee/`
    - Example `ExplanationBundle` instances for risk-priority facilities

- Tests (planned structure):
  - `src/python/tests/examples/test_examples_environment_compliance_roundtrip.py`

## How to read this vertical

1. Start with `about.yaml` to understand the risk framing and user stories.
2. Read `explanations.md` to see how `FACILITY_RISK_PRIORITY` is structured.
3. Inspect CEP and CEE example JSON under `examples/environment/compliance/`.
4. Run the example test to exercise the end-to-end risk explanation flow.
