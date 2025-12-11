# Disaster Preparedness and Community Resilience

Vertical ID: `resilience`  
About file: `docs/en/verticals/resilience/about.yaml`  
Explanations: `docs/en/verticals/resilience/explanations.md`

This vertical slice explores how CEP and CEE can highlight **critical
shelters, routes, and facilities** in a disaster preparedness context,
and explain **why** they are considered high-priority for resilience
planning.

The emphasis is on **saving lives and reducing harm** through better
planning, not on assigning blame.

## Who this vertical is for

This example is designed for:

- Emergency managers and operations centers
- Public works and infrastructure planners
- Community preparedness groups
- Researchers working with hazard, exposure, and capacity data

See `about.yaml` for detailed user stories and data-source notes.

## What this vertical demonstrates

- **CEP side**
  - Modeling shelters, critical facilities, hazard zones, routes, and
    population catchments
  - Relationships:
    - shelter serves catchment
    - facility located in hazard zone
    - route connects areas and facilities
  - Geospatial identity and intersection patterns across multiple layers

- **CEE side**
  - An explanation type (for example, `SHELTER_CRITICALITY`) that answers:
    > Why is this shelter or facility considered critical in a given scenario?
  - Evidence such as:
    - population served within a time/distance window
    - hazard intensity in the catchment
    - availability of alternative shelters
    - network connectivity and route redundancy

## Files in this vertical

- Definition and intent:
  - `docs/en/verticals/resilience/about.yaml`
  - `docs/en/verticals/resilience/index.md` (this file)
  - `docs/en/verticals/resilience/explanations.md`

- Example data (planned structure):
  - `examples/resilience/shelters/raw/`
    - Small slices of hazard, shelter, and population data
  - `examples/resilience/shelters/cep/`
    - CEP entities and relationships for shelters and routes
  - `examples/resilience/shelters/cee/`
    - Example `ExplanationBundle` instances for critical shelters

- Tests (planned structure):
  - `src/python/tests/examples/test_examples_resilience_roundtrip.py`

## How to read this vertical

1. Start with `about.yaml` for the high-level preparedness and resilience
   user stories.
2. Read `explanations.md` to see how criticality explanations are structured.
3. Inspect example CEP and CEE JSON under `examples/resilience/shelters/`.
4. Use the examples and tests as a basis for more complex scenario modeling.
