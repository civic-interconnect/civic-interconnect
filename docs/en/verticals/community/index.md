# Community Assets and Local Access

Vertical ID: `community`  
About file: `docs/en/verticals/community/about.yaml`  
Explanations: `docs/en/verticals/community/explanations.md`

This vertical slice explores how CEP and CEE can highlight **neighborhoods
with limited access to community assets** such as parks, libraries, and
recreation centers, and explain **why** those areas are prioritized for investment.

It is focused on optimization and identifying a **place** where improved assets
are likely to incur better outcomes.

## Who this vertical is for

This example is designed for:

- City planners and urban designers
- Public health and equity analysts
- Community and neighborhood organizations
- Anyone exploring **place-based** equity with civic data

See `about.yaml` for detailed user stories and data-source notes.

## What this vertical demonstrates

- **CEP side**
  - Modeling community assets as CEP entities
  - Representing neighborhoods / areas and jurisdictions
  - Relationships:
    - asset located in area
    - area part of jurisdiction
  - Using record envelopes and provenance for city / regional open data

- **CEE side**
  - An explanation type (e.g., `AREA_ACCESS_PRIORITY`) that answers:
    > Why is this neighborhood highlighted as a priority for investment?
  - Evidence such as:
    - population served
    - distance to nearest assets
    - number of assets within a threshold
    - equity or deprivation indices

## Files in this vertical

- Definition and intent:
  - `docs/en/verticals/community/about.yaml`
  - `docs/en/verticals/community/index.md` (this file)
  - `docs/en/verticals/community/explanations.md`

- Example data (planned structure):
  - `examples/assets/community/raw/`
    - Small slices of asset and population data
  - `examples/assets/community/cep/`
    - CEP entities and relationships for assets and areas
  - `examples/assets/community/cee/`
    - Example `ExplanationBundle` instances for priority areas

- Tests (planned structure):
  - `src/python/tests/examples/test_examples_assets_community_roundtrip.py`

## How to read this vertical

1. Start with `about.yaml` to see the high-level goals, user stories, and
   data-source strategy.
2. Read `explanations.md` for the CEE explanation type and helper logic.
3. Inspect the example CEP and CEE JSON files under `examples/`.
4. Use the test in `src/python/tests/examples/` as an executable spec for
   the vertical slice.
