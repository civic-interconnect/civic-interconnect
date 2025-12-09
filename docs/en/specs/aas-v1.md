# Adapter Algebra Specification (AAS v1)

Version: 1.0.0  

Status: Draft  

Applies to: All CEP adapters (local, domain, core, envelope)  

Purpose: Define a deterministic, compositional algebra of adapters as typed rewriting morphisms between CEP schemas.

---

## 1. Overview

Adapters are the primary way CEP connects heterogeneous data sources to the
canonical CEP representation. Each adapter is a *typed rewriting morphism*
between schemas:

- from a **source schema** (e.g., a CSV layout, an API response, a legacy JSON schema)
- to a **target schema** (e.g., a CEP domain record, a core CEP entity, an envelope)

This document defines:

- the **type signature** of adapters  
- **determinism** and **partiality** requirements  
- **composition** and **identity adapters**  
- **versioning** and **provenance** requirements

The goal is to ensure that adapter pipelines behave predictably and can be
reasoned about as a compositional algebra.

---

## 2. Adapter Types and Signatures

### 2.1 Schema Objects

Every adapter operates between two schemas:

- A **source schema** `S`
- A **target schema** `T`

Schemas are identified by stable URIs:

- `schemaId: string` (e.g., `https://.../schema/cep.entity.municipality.json`)
- `schemaVersion: semver` (e.g., `"1.0.0"`)

The pair `(schemaId, schemaVersion)` uniquely identifies a schema.

### 2.2 Adapter Definition

An adapter `A` is defined by:

- `adapterId: string` (stable identifier, e.g., `adapter.us_mn_muni_raw_to_domain_v1`)
- `adapterVersion: semver`
- `sourceSchemaId: string`
- `sourceSchemaVersion: semver`
- `targetSchemaId: string`
- `targetSchemaVersion: semver`
- `adapterKind: "local" | "domain" | "core" | "envelope"` (classification)
- **rewrite function**:
  - `A: SourceRecord -> Result<TargetRecord, AdapterError>`

Conceptually:

```text
A : Records(S) → Records(T) ∪ {AdapterError}
```

Adapters are pure functions: for fixed input, they must always return the
same output or the same error.

---

## 3. Determinism and Partiality

### 3.1 Determinism

For any given input record x that conforms to sourceSchemaId / sourceSchemaVersion:

If A(x) succeeds once, it must succeed always with the same TargetRecord.

If A(x) fails, it must always fail with the same AdapterError category.

Non-deterministic behavior (e.g., depending on current time, external services,
randomness) is not allowed in the core adapter function.

If time-dependent or context-dependent behavior is needed (e.g., “now”), it
must be pushed into explicit input fields or handled outside the adapter.

### 3.2 Partiality

Adapters are generally partial:

- Not all SourceRecords are necessarily valid or mappable.
- Failures must be explicit and typed.

We model this using `Result<TargetRecord, AdapterError>`.

AdapterError categories include (but are not limited to):

- SchemaViolation (input does not conform to the declared source schema)
- MissingRequiredField
- InvalidCode (unknown vocabulary term)
- CanonicalizationFailure
- InconsistentIdentifiers
- UnsupportedVersion
- InternalInvariantViolation (bug, not data issue)

Adapters must not silently correct or drop records without either:

- returning an explicit error, or
- recording warnings in an attested envelope.

---

## 4. Composition of Adapters

Given adapters:

`A: S → T`

`B: T → U`

We can form a composite adapter:

`B ∘ A : S → U`


defined by:

```text
(B ∘ A)(x) = 
    match A(x) with
      | Ok(y)    -> B(y)
      | Error(e) -> Error(e)
```

4.1 Associativity

Composition of adapters is associative:

`C ∘ (B ∘ A) = (C ∘ B) ∘ A`


at the level of the underlying functions, provided they all share compatible
schemas and error semantics.

This means adapter pipelines behave like morphisms in a category:

- Objects: schemas (schemaId, schemaVersion)
- Morphisms: adapters between schemas

### 4.2 Identity Adapters

For every schema (S, v), there MUST exist an identity adapter:

`id_S : S → S`


such that for all adapters `A: S → T` and `B: U → S`:

`A ∘ id_S = A`

`id_S ∘ B = B`


The identity adapter performs validation but no transformation:

- It may enforce schema conformance.
- It must not change any field value.

### 4.3 Version-Aware Composition

Adapters are tied to specific (schemaId, schemaVersion) pairs.

Composition `B ∘ A` is only valid if:

- `A.targetSchemaId == B.sourceSchemaId`
- `A.targetSchemaVersion` is compatible with `B.sourceSchemaVersion`

Compatibility rules must be explicit:

- Exact match, or
- Declared compatibility ranges (e.g., >=1.0.0 <2.0.0)

If versions are incompatible, composition is not allowed without an explicit
version-bridge adapter.

---

## 5. Adapter Kinds and Pipelines

Adapters are grouped into kinds to reflect their typical position in a pipeline:

- Local adapters: Source-specific → domain-specific raw

- Domain adapters: Domain-specific raw → CEP domain record

- Core adapters: CEP domain record → CEP core entity/relationship

- Envelope adapters: CEP core entity/relationship → exchange/envelope

A typical pipeline:

```text
RawSource
  → (Local Adapter)
DomainRaw
  → (Domain Adapter)
DomainEntity
  → (Core Adapter)
CoreEntity
  → (Envelope Adapter)
Envelope
```

Each step is a morphism of schemas; the full pipeline is the composite morphism.

---

## 6. Rewriting Semantics

Adapters are typed rewriting functions:

- They rewrite structures (records), not just strings.
- They apply the canonicalization pipeline to relevant fields.
- They enforce vocabulary mappings and schema constraints.

The adapter algebra is therefore:

- structural at the record level
- compositional under function composition
- strategy-governed in terms of pipeline order (we do not assume commutativity)

---

## 7. Versioning of Adapters

Each adapter has an explicit adapterVersion (SemVer):

- MAJOR: breaking change in output schema or semantics.
- MINOR: backward-compatible enhancements (additional computed fields, new optional behavior).
- PATCH: bugfixes that preserve behavior for valid inputs.

Every produced record MUST include:

- adapterId
- adapterVersion

in its provenance / envelope, so that downstream processes and verifiers can
reproduce or audit adapter behavior.

---

## 8. Equivalence of Adapters

Two adapters `A, B: S → T` are extensionally equivalent if for all valid
inputs `x`:

`A(x) = B(x)`


CEP may treat extensionally equivalent adapters as interchangeable, but they may
still differ in:

- implementation language
- performance
- internal logging or diagnostics

Equivalence is a conceptual notion; practical systems may use tests to
approximate it.

---

## 9. Adapter Provenance and Attestation

Adapters are central to trust in CEP data. Therefore:

Every adapter invocation SHOULD be recorded in provenance:

- adapterId
- adapterVersion
- timestamps
- success or failure

Cryptographic tags (CTags) SHOULD commit to:

- adapter identity and version
- input fingerprint (if applicable)
- canonical output representation (CEC)

This allows verifiers to:

- reconstruct the adapter chain,
- reproduce transformations,
- detect tampering or missing pipeline steps.

---

## 10. Summary

The adapter algebra defines a category of schemas and adapters:

- Objects: versioned schemas
- Morphisms: deterministic, typed, possibly partial adapters
- Composition: associative function composition
- Identities: schema-preserving validators

This algebra underpins cross-domain interoperability, reproducible pipelines,
and verifiable transformations in CEP.
