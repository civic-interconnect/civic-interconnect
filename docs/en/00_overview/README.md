# Overview: How These Parts Fit Together

This documentation set describes a layered framework for representing, normalizing, and reasoning about civic data in a way that is durable, auditable, and interoperable across domains and jurisdictions.

The material is organized to separate concerns that are often conflated: raw description of civic facts, structural exchange formats, contextual explanation, and downstream assurance. Each layer can be used independently, but they are designed to compose in a predictable way.

## The Layers

At the base is **CAE (Civic Activity Entities)**.  
CAE defines how real-world civic actors, roles, and authorities are represented as entities. It concerns itself only with describing what exists and how it is identified, without assuming any exchange format, explanatory model, or evaluative claim.

Above that is **CEP (Civic Exchange Protocol)**.  
CEP defines how entities and relationships are bundled into records, exchanges, and envelopes that can move between systems. It specifies structure, canonicalization, and validation rules, but does not interpret meaning or outcomes.

Above CEP is **CEE (Contextual Evidence and Explanations)**.  
CEE provides a way to attach observations, explanations, models, and interpretations to CEP records. It enables reasoning about why something happened, what it implies, or how it should be understood, without changing the underlying facts.

Alongside these is **Assurance**.  
Assurance concerns attestations, audits, and claims made about data, processes, or outcomes. It depends on the lower layers for structure and provenance, but remains conceptually separate from explanation and exchange.

## How They Relate

Information flows upward.

CAE entities may appear inside CEP records.  
CEP records may be referenced by CEE explanations.  
Assurance artifacts may refer to any of the above.

The reverse is intentionally not true.  
Lower layers do not depend on higher ones, and they do not assume the existence of explanations, evaluations, or guarantees.

This separation allows systems to exchange data without agreeing on interpretation, and to reason about interpretation without rewriting history.

## How to Read These Docs

If you are defining or consuming civic entities, start with the CAE reference.

If you are building systems that exchange civic data, focus on the CEP reference and implementation sections.

If you are modeling outcomes, impacts, or interpretations, read the CEE reference and explanations.

If you are evaluating trust, claims, or compliance, refer to the Assurance section.

Each section is written to stand on its own. Cross-references are minimal by design.

## Stability

The layering and responsibilities described here are intended to remain stable over time.

Details may be refined, terminology may be clarified, and additional material may be added. The separation of concerns described in this overview reflects deliberate design choices and is expected to remain a reliable foundation as the project evolves.
