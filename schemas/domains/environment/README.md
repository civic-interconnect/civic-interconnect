# Domain: Environment

## Core entities

-   Facility (plant, site)
-   EmissionSource (stack, unit)
-   Permit (air/water/waste)
-   Inspection
-   Violation
-   EmissionMeasurement

## Relationships

-   facilityHasPermit(Facility, Permit)
-   permitCoversSource(Permit, EmissionSource)
-   inspectionOf(Inspection, Facility)
-   violationDetectedIn(Violation, Inspection)
-   measuresEmission(EmissionMeasurement, EmissionSource)

## Vocabulary seed (codes / types)

Example environmental-permit-type.json:

-   ENV_PERMIT_AIR_MAJOR
-   ENV_PERMIT_AIR_MINOR
-   ENV_PERMIT_WATER_NPDES
-   ENV_PERMIT_WASTE_SOLID
-   ENV_PERMIT_WASTE_HAZARDOUS

Example environmental-violation-severity.json:

-   ENV_VIOLATION_MINOR
-   ENV_VIOLATION_SIGNIFICANT
-   ENV_VIOLATION_HIGH_PRIORITY

## Rewrite Problems

Facility IDs:

-   EPA Facility Registry IDs vs state-specific IDs; various formatted versions.

Unit normalization:

-   lbs/day, tons/year, kg/year → canonical unit + numeric value.

Permit codes:

-   “Title V”, “TV”, “Major source” → ENV_PERMIT_AIR_MAJOR.

Location canonicalization:

-   Addresses vs coordinates vs county/census IDs.

## Good Test For

-   Numeric and unit rewriting
-   Multi-identifier integration
-   Geo-related canonicalization
