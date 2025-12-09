# CEP as a Unified Rewriting Framework

CEP (Civic Exchange Protocol) is built on the idea that civic data integration
can be understood as a **family of rewriting systems** glued together by a
shared category-theoretic backbone. Instead of treating canonicalization,
adapters, graphs, and identity resolution as separate ad-hoc mechanisms, CEP
treats them as layers of **typed, strategy-governed rewrites**.

This document explains how the major CEP specifications fit together as a
unified rewriting framework.

---

## 1. Layers of Rewriting in CEP

CEP operates at several semantic layers:

1. **String-level rewriting**  
   - Normalizing names, codes, abbreviations, and text fields.  
   - Handled by the canonicalization pipeline in conjunction with vocabularies.

2. **Record-level rewriting (adapters)**  
   - Mapping source-specific records into CEP domain schemas and core entities.  
   - Handled by the Adapter Algebra Specification (AAS).

3. **Identity-level rewriting (fingerprints)**  
   - Selecting minimal identity-defining features and constructing stable
     fingerprints and verifiable IDs.  
   - Handled by the Entity Fingerprint Specification (EFS).

4. **Graph-level rewriting (normalization and merges)**  
   - Normalizing provenance and entity graphs into canonical forms.  
   - Handled by the Graph Normalization Specification (GNS).

5. **Cluster-level rewriting (identity resolution)**  
   - Merging entities into cross-domain identity clusters based on rule-based
     evidence.  
   - Handled by the Cross-Domain Identity Resolution Algorithm (CDIRA).

Each layer is a rewriting system with its own objects, morphisms, and
strategies, but all share the same design principles:

- determinism  
- explicit strategy (not implicit commutativity)  
- clear versioning  
- explicit provenance  

---

## 2. Strategy-Governed Rewriting (Not “Everything Commutes”)

In many practical systems, rewriting rules **do not commute**:

- Expanding “S.A.” into a French corporate form must happen before punctuation
  removal, or the pattern disappears.
- Mapping legacy codes onto controlled vocabularies must happen before schema
  validation.
- Merging records must happen after identifiers and names have been
  canonicalized.

CEP does not claim that all rewrite rules can be applied in arbitrary order.
Instead, it adopts **stratified, strategy-governed rewriting**:

- Within a stratum (e.g., semantic expansions, then structural simplifications),
  rules are associative and confluent on their domain.
- Across strata, CEP fixes a **global evaluation order** to preserve meaning.

This mirrors established practice in compilers, NLP pipelines, Unicode
normalization, and term-rewriting systems: correctness depends on strategy, not
on naive commutativity.

---

## 3. Core Specifications in the Framework

The unified framework is realized through a small set of core specifications:

### 3.1 Canonical Encoding (CEC v1)

CEC defines a **deterministic JSON-level encoding**:

- lexicographic key ordering  
- null omission rules  
- numeric normalization  
- Unicode NFC  
- stable list handling  

CEC is the last step before hashing and ensures that semantically identical
structures produce identical byte sequences.

### 3.2 Entity Fingerprints (EFS v1)

EFS defines **minimal identity**:

- canonical identifiers (e.g., SNFEI, registry IDs)  
- canonical names  
- optional jurisdiction context  

Fingerprints **exclude** descriptive attributes such as address or status.
They are serialized via CEC and hashed to produce `verifiableId`.

### 3.3 Adapter Algebra (AAS v1)

Adapters are **typed rewriting morphisms** between schemas:

- objects: `(schemaId, schemaVersion)`  
- morphisms: deterministic (possibly partial) adapters  
- composition: associative function composition  
- identities: validation-only adapters `id_S : S → S`

Adapters form the backbone of CEP pipelines from raw sources to core entities
and envelopes.

### 3.4 Graph Normalization (GNS v1)

GNS treats CEP graphs as objects to be normalized:

- entity nodes use `verifiableId` as canonical IDs  
- non-entity nodes receive canonical local IDs derived from their payload and
  incident edges  
- nodes and edges are sorted deterministically  
- the result is serialized with CEC and can be hashed for graph-level tags

This ensures that equivalent provenance or entity graphs collapse to the same
canonical form.

### 3.5 Global Integrity Constraints (GIC v1)

GIC defines **system-wide invariants**:

- unique and stable `verifiableId` per entity  
- referential integrity for relationships  
- DAG structure for provenance  
- idempotent normalization  
- completeness and temporal coherence of provenance  

These constraints prevent silent corruption and non-deterministic behavior.

### 3.6 Versioning Governance (VGS v1)

VGS defines independent semantic versioning for:

- CEC  
- EFS  
- GNS  
- Schemas  
- Vocabularies  
- Adapters  

Every record carries a **version tuple**, ensuring that any hashed object can be
reinterpreted and revalidated in the future.

### 3.7 Cross-Domain Identity Resolution (CDIRA v1)

CDIRA defines a deterministic clustering algorithm:

- strong, moderate, and weak evidence  
- rule-based merge decisions  
- conflict records when evidence disagrees  
- cluster identifiers derived from member IDs and versions  

This extends the rewriting perspective to cross-domain identity graphs.

---

## 4. Category-Theoretic Perspective

At a high level, CEP can be viewed as a category (or family of categories)
where:

- **Objects** are:
  - schemas and schema versions  
  - graphs (entity/provenance)  
  - identity clusters  

- **Morphisms** are:
  - adapters (record-level rewrites)  
  - normalization functions (string-level, graph-level)  
  - cluster merges (identity-level rewrites)

Rewriting systems at each layer are connected via functor-like mappings:

- string rewriting feeds into record schemas,  
- record rewriting feeds into graph construction,  
- graph-normalized entities feed into identity resolution.

The important point is not the specific categorical formalism, but the fact
that **CEP treats all of these as typed, compositional morphisms with explicit
strategies**, rather than unrelated ad-hoc scripts.

---

## 5. Adding a New Domain as a Rewriting Testbed

When CEP is extended to a new domain (e.g., campaign finance, environmental
regulation, education), that domain is integrated by defining:

1. **Domain vocabularies**  
   - entity types, relationship types, codes, statuses.

2. **Canonicalization rules for domain-specific strings**  
   - names, codes, abbreviations, units.

3. **Domain schemas**  
   - entity and relationship records, with required fields and types.

4. **Adapters**  
   - source-specific → domain schema  
   - domain schema → core CEP entities/relationships

5. **Graph patterns and provenance requirements**  
   - how filings, permits, inspections, or programs connect to entities.

The unified rewriting framework guarantees that:

- canonicalization behaves consistently,  
- fingerprints and verifiable IDs behave consistently,  
- graphs normalize consistently,  
- identity resolution works the same way across domains,  
- hashes are stable and interpretable over time.

Domains differ in their vocabularies and schemas, **not** in the foundational
mechanics of rewriting and normalization.

---

## 6. Summary

CEP is not just a collection of schemas and APIs. It is a **unified rewriting
framework** in which:

- strings, records, graphs, and identity clusters are all normalized via
  deterministic, strategy-governed rewrites;
- canonical encoding, fingerprints, graphs, and adapters share a consistent
  versioning and provenance model;
- new domains can be added by plugging into the same rewriting architecture.

This framework is what allows CEP to support long-lived, verifiable, and
composable civic data across many heterogeneous domains.
