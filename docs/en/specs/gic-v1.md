# Global Integrity Constraints (GIC v1)

Version: 1.0.0

Status: Draft

Applies to: All CEP entities, relationships, provenance graphs, adapters, and envelopes

Purpose: Define system-wide invariants that must hold for CEP data to be valid, canonicalizable, interoperable, and verifiable.

---

# 1. Overview

The Civic Exchange Protocol (CEP) unifies multiple rewriting systems across
domains (canonicalization, adapters, fingerprints, provenance, graph merging,
and hashing). Global Integrity Constraints (GIC) define the _cross-cutting
rules_ that govern all CEP data and transformations. They ensure that:

-   identities remain stable and non-ambiguous
-   relationships are consistent and well-formed
-   provenance is coherent and auditable
-   graph normalization yields deterministic results
-   CTags and fingerprints remain trustworthy
-   versioning is explicit and reproducible

These constraints are mandatory. Any violation indicates an invalid record,
invalid adapter output, or corrupted graph.

---

# 2. Identity Integrity Constraints

## 2.1 Unique Verifiable Identifier

Every entity MUST have exactly one `verifiableId`, produced via:

1. canonicalization
2. fingerprint construction
3. CEC encoding
4. cryptographic hashing

`verifiableId` MUST be globally unique for entities with distinct fingerprints.

## 2.2 Stability Under Attribute Change

An entity's `verifiableId` MUST remain unchanged if:

-   addresses change
-   phone/email change
-   officers or membership change
-   descriptive fields change
-   statuses change (ACTIVE → INACTIVE)

Only **identity-defining attributes** may influence the fingerprint.

## 2.3 Deterministic Cross-Domain Identity

If entity A in one domain and entity B in another are representing the same
real-world entity, then their fingerprints MUST normalize to the same value.
If fingerprints differ, entities MUST be treated as distinct.

---

# 3. Relationship Integrity Constraints

## 3.1 Referential Integrity

All relationships MUST reference existing entities using _their canonical
verifiableId_.  
No relationship may point to a:

-   blank/empty ID
-   temporary/local ID
-   non-existent entity

## 3.2 Type Consistency

A relationship's `relationshipTypeUri` MUST be compatible with the types of the
referenced entities.  
For example:

committeeRepresentsCandidate(Committee, Candidate)

may not be applied to:

committeeRepresentsCandidate(School, City)

Type compatibility follows domain vocabulary definitions.

## 3.3 Cardinality Rules

Each relationship type MUST specify its cardinality:

-   one-to-one
-   one-to-many
-   many-to-many

Adapters MUST enforce these constraints.

## 3.4 Relationship Symmetry / Antisymmetry / Directionality

If a relationship vocabulary declares:

-   symmetric
-   antisymmetric
-   directional
-   inverse-of

then every instance MUST satisfy that constraint.

Example:

If `parentOf` is antisymmetric, we must forbid:

```text
parentOf(A, B)
parentOf(B, A)
```

unless `A = B` and the vocabulary allows reflexive relations.

---

# 4. Fingerprint and Hash Integrity Constraints

## 4.1 Deterministic Fingerprints

Fingerprints MUST be reproducible across languages, platforms, and
implementations.

## 4.2 Canonical Encoding Required

Only CEC v1 (or later explicitly declared versions) may be used to produce
bytes for hashing.

## 4.3 Metadata Commitment

Each hash MUST commit to:

-   `cecVersion`
-   `schemaVersion`
-   `vocabularyVersion`
-   `adapterVersion`
-   `fingerprintVersion`

If any of these change, fingerprints may change or be non-interoperable.

## 4.4 No Hidden Fields

No field outside the fingerprint structure may influence the hash.

---

# 5. Provenance Integrity Constraints

## 5.1 Provenance Completeness

Every entity and relationship MUST retain provenance sufficient to answer:

-   Who created this record?
-   Which adapter(s) produced it?
-   When was the transformation performed?
-   What version of the schema/vocab was used?

## 5.2 Temporal Monotonicity

If an activity uses an input and generates an output:

`used(entity) → activity → wasGeneratedBy(entity)`

then:

`timestamp(used.input) ≤ timestamp(activity) ≤ timestamp(wasGeneratedBy.output)`

## 5.3 Activity Determinism

Provenance activities MUST reflect deterministic adapter behavior.

No activity may claim a transformation occurred without referencing the adapter
that performed it.

---

# 6. Graph Integrity Constraints

## 6.1 Graph Validity

A graph is valid if:

-   all nodes have canonical IDs
-   all edges connect existing nodes
-   all payloads satisfy schema
-   the graph normalizes correctly under GNS

## 6.2 No Dangling Edges

Edges MUST not reference deleted or unresolvable nodes.

## 6.3 No Cycles in Provenance DAG

Provenance graphs MUST be directed acyclic graphs.

Cycles violate causality.

## 6.4 Idempotent Graph Normalization

Normalizing an already normalized graph MUST yield identical bytes.

---

# 7. Adapter Integrity Constraints

## 7.1 Version Declaration

All adapters MUST emit:

-   `adapterId`
-   `adapterVersion`

## 7.2 Total Determinism for Valid Inputs

Given valid input `x`:

`A(x) = y`

must always produce the same `y`.

## 7.3 Typed Partiality

Errors MUST be explicit, typed, and reproducible.

## 7.4 Composition Rules

Adapter pipelines MUST respect adapter algebra composition and version-compatibility.

---

# 8. Cross-Version Integrity Constraints

## 8.1 Version Awareness

Every CEP record MUST declare:

-   `schemaVersion`
-   `vocabularyVersion`
-   `adapterVersion`
-   `cecVersion`
-   `fingerprintVersion`
-   `gnsVersion` (if graph-level)

## 8.2 Monotonic Version Evolution

Adapters MAY target:

-   the same version
-   or a compatible future version

They MUST NOT mix incompatible versions without a defined version-bridge adapter.

## 8.3 Consistency Under Updates

Updating a schema or vocabulary MUST NOT retroactively break previously valid
records.  
Backwards-compatible evolution requires:

-   versioned vocabularies
-   explicit deprecation
-   backwards-compatible adapters

---

# 9. Summary

These Global Integrity Constraints define the invariants required for CEP to be:

-   deterministic
-   interoperable
-   identity-stable
-   graph-stable
-   hash-verifiable
-   provenance-complete

Any valid CEP dataset, entity, graph, or exchange MUST satisfy these
constraints.
