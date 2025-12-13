# How These Pieces Fit Together

This documentation describes a layered framework for representing, exchanging, and interpreting civic data in a way that is durable, interoperable, and auditable over long time horizons.

The framework is composed of three primary layers:

CAE (Civic Accountable Entities)
CEP (Civic Exchange Protocol)
CEE (Contextual Evidence and Explanations)

Each layer has a distinct purpose and a clear boundary. The layers are designed to compose, but not to collapse into one another.

The intent is not to prescribe applications, policy outcomes, or analytic conclusions. It is to define stable structural contracts that many systems can share, even when they disagree about interpretation, values, or goals.

---

## Direction of Dependence

The layers are ordered from most foundational to most interpretive.

CAE defines a stable object universe for civic representation.
CEP defines how civic entities and relationships are exchanged and validated.
CEE defines how observations and explanations are expressed over exchanged records.

Dependencies flow upward only.

Lower layers do not assume the existence of higher layers. Higher layers may rely on lower layers but must not retroactively redefine them.

This one-way dependency supports long-term stability. It allows foundational representations to remain valid even as explanatory models, regulatory regimes, and analytic methods change.

---

## CAE

CAE defines the object universe: what kinds of civic things exist and what kinds of relationships are admissible between them.

CAE is intentionally conservative. It does not prescribe exchange formats, evidence models, or evaluative claims. It provides the stable entity partition and relationship constraints that higher layers build upon.

---

## CEP

CEP defines exchange structure: entities, relationships, exchanges, and record envelopes, along with validation and canonicalization rules.

CEP is value-neutral with respect to interpretation. It specifies what was asserted, in what form, and under what structural constraints. It assumes the CAE object universe and does not redefine it.

---

## CEE

CEE defines interpretation structure: observations, explanations, models, assumptions, and claims expressed over exchanged records.

CEE is pluralistic. Multiple, even conflicting, explanations may coexist over the same underlying CEP records.

CEE depends on CEP, and transitively on CAE, but does not redefine either.

---

## Where to Find Implementations and Examples

These docs describe specifications and contracts.

Concrete examples, datasets, adapters, and test vectors are maintained in the repository alongside the code that consumes them. This avoids duplication and reduces documentation drift.

Refer to the repository structure for current implementations and examples.

---

This page is intentionally minimal. It exists to establish orientation before introducing the individual layers in detail.
