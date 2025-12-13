# How These Pieces Fit Together

This documentation describes a layered framework for representing, exchanging,
and interpreting civic data in a way that is durable, interoperable, and auditable
over long time horizons.

The framework is composed of three primary layers:

- Civic Actor Environment (CAE)
- Civic Exchange Protocol (CEP)
- Contextual Evidence and Explanations (CEE)

Each layer has a distinct purpose and a clearly defined boundary. The layers are
designed to compose, but not to collapse into one another.

The intent of this framework is not to prescribe applications, policy outcomes,
or analytic conclusions. It is to define stable structural contracts that many
systems can share, even when they disagree about interpretation, values, or goals.

---

## Direction of Dependence

The layers are ordered from most foundational to most interpretive.

CAE defines what civic actors are.  
CEP defines how civic facts are exchanged.  
CEE defines how civic facts are interpreted and explained.

Dependencies flow upward only.

Lower layers do not assume the existence of higher layers. Higher layers may rely
on lower layers but must not retroactively redefine them.

This one-way dependency is essential for long-term stability. It allows
foundational representations to remain valid even as explanatory models,
regulatory regimes, and analytic methods change.

---

## Civic Actor Environment (CAE)

CAE defines the minimal structure required to talk about civic actors at all.

It is concerned with the existence, identity, and roles of actors that participate
in civic systems. This includes, but is not limited to, individuals, organizations,
public bodies, and collective entities.

CAE answers questions such as:

- What kinds of civic actors exist?
- What roles or authorities can an actor hold?
- How are identities referenced and compared?
- What does it mean for two records to refer to the same actor?

CAE does not define data exchange formats, transactions, contracts, or outcomes.
It does not assume the existence of schemas, APIs, or explanatory models.

CAE stands alone. It does not refer to CEP or CEE.

---

## Civic Exchange Protocol (CEP)

CEP defines how civic data is exchanged between systems in a structured,
verifiable way.

It introduces formal structures for entities, relationships, exchanges, and
record envelopes, along with validation and canonicalization rules.

CEP is intentionally value-neutral. It does not explain why something occurred,
whether it was appropriate, or what should happen next. It only specifies what
was asserted, in what form, by whom, and under what structural constraints.

CEP assumes the existence of civic actors as defined by CAE, but does not assume
any particular explanatory or evaluative framework.

---

## Contextual Evidence and Explanations (CEE)

CEE defines how civic data is interpreted, explained, and evaluated in context.

It introduces mechanisms for attaching observations, explanations, models,
assumptions, and evaluative claims to CEP records without altering the underlying
exchange layer.

CEE is explicitly pluralistic. Multiple, even conflicting, explanations may
coexist over the same underlying data.

CEE depends on CEP, and transitively on CAE, but does not redefine either.

---

## Stability and Change

Each layer has a different stability horizon.

CAE is expected to change very slowly.  
CEP evolves through versioned specifications and governance processes.  
CEE is expected to evolve rapidly as analytic methods, norms, and policies change.

This separation allows innovation at the interpretive layer without destabilizing
foundational representations.

---

## Where to Find Implementations and Examples

This documentation describes specifications and contracts, not tutorials.

Concrete examples, datasets, adapters, and test vectors are maintained in the
repository alongside the code that consumes them. This avoids duplication and
reduces the risk of documentation drift.

Refer to the repository structure for current implementations and examples.

---

This page is intentionally minimal. It exists to establish shared orientation
before introducing the individual layers in detail.
