# Civic Education Access and Program Value

Vertical ID: `edaccess`  
About file: `docs/en/04_verticals/edaccess/about.yaml`  
Explanations: `docs/en/04_verticals/edaccess/explanations.md`

This vertical slice explores how CEP and CEE can help **students,
institutions, and policymakers** understand which educational programs are
**accessible and high-value**, and explain **why** specific programs are highlighted.

The focus is on **positive, actionable guidance** for learners and
improvement paths for institutions.

## Who this vertical is for

This example is designed for:

- Prospective students and families
- Institutional leaders (deans, program directors)
- State or regional higher education agencies
- Analysts working with IPEDS / Scorecard / similar datasets

See `about.yaml` for detailed user stories and data-source notes.

## What this vertical demonstrates

- **CEP side**
  - Modeling institutions, programs, credentials, and regions
  - Relationships:
    - institution offers program
    - program leads to credential
    - institution located in region
  - Identity strategies for institutions and programs across data sources

- **CEE side**
  - An explanation type (e.g., `PROGRAM_ACCESS_VALUE`) that answers:
    > Why is this program highlighted as a strong option for this learner?
  - Evidence such as:
    - tuition or net cost
    - completion rate
    - earnings or employment outcomes
    - distance or online availability
    - support for specific learner groups

## Files in this vertical

- Definition and intent:
  - `docs/en/04_verticals/edaccess/about.yaml`
  - `docs/en/04_verticals/edaccess/index.md` (this file)
  - `docs/en/04_verticals/edaccess/explanations.md`

- Example data (planned structure):
  - `examples/education/access/raw/`
    - Small slices of institution, program, and outcome data
  - `examples/education/access/cep/`
    - CEP entities and relationships for institutions and programs
  - `examples/education/access/cee/`
    - Example `ExplanationBundle` instances for highlighted programs

- Tests (planned structure):
  - `src/python/tests/examples/test_examples_education_access_roundtrip.py`

## How to read this vertical

1. Start with `about.yaml` to see the user stories and the policy context.
2. Read `explanations.md` to understand the `PROGRAM_ACCESS_VALUE`
   explanation design.
3. Inspect example CEP and CEE JSON under `examples/education/access/`.
4. Use the example test as an executable spec of the end-to-end slice.
