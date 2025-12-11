# CEE Disaster Resilience and Critical Facility Explanations

Module: `civic_interconnect.cee.resilience.criticality_explanations`

Explanation type: `CRITICAL_INFRASTRUCTURE_PRIORITY`

This module builds CEE `ExplanationBundle` objects explaining why a
shelter, facility, or infrastructure asset is considered critical in a
disaster preparedness or emergency response context.

Evidence components may include:

- Population served by the shelter or facility’s catchment
- Proximity to hazard zones (flood, wildfire, seismic, etc.)
- Redundancy and network centrality of evacuation routes
- Capacity relative to expected demand
- Availability of essential services (power, water, medical resources)

These structured explanations attach to CEP `shelter`, `facility`, or
other resilience-related entities.

See `examples/verticals/resilience/cee/` for illustrative examples.
