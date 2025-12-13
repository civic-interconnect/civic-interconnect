# Relationships

Relationships express structured links between civic entities.

A relationship states that two or more entities are connected in a specific,
typed way, within a defined context.

CEP treats relationships as first-class records.

---

## Relationship Structure

A relationship consists of:

-   One or more endpoints
-   A relationship type
-   Optional contextual attributes
-   Source references

Endpoints refer to entities but do not redefine them.

---

## Direction and Semantics

Relationships may be directional or non-directional.

CEP does not assign semantic meaning beyond the declared relationship type.
Interpretation is delegated to consuming systems.

---

## Stability

Relationships are versioned records.

Changes to a relationship result in a new record rather than mutation of
existing history.

---

This page defines how connections between entities are represented in CEP.
