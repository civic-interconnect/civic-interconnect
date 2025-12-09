# CEP Foundational Principles

This document identifies the foundational architectural invariants required for
the Civic Exchange Protocol (CEP) to function as a deterministic, compositional,
and verifiable system across diverse civic domains.

## 1. Canonical Serialization (CEC)
CEP requires a stable, deterministic canonical encoding for all entities,
relationships, and exchanges. This includes:

- key ordering
- omission rules for null/empty fields
- Unicode normalization
- numeric normalization
- canonical list ordering
- no ambiguity in datatype representation

CEC is mandatory for hashing, deduplication, and cross-system verification.

## 2. Cross-Domain Entity Identity
All domains must support a common identity model grounded in:

- minimal identity-defining attributes
- domain-agnostic fingerprint rules
- deterministic merge semantics
- stable identifier construction

Identity must be consistent across campaigns, environment, education,
municipalities, nonprofits, etc.

## 3. Graph-Level Normalization
Provenance, merges, and entity graphs must have:

- canonical ordering of edges
- deterministic blank-node labeling
- merge strategy determinism
- recursion guards during rewriting

This ensures stable cross-domain provenance and reproducible entity histories.

## 4. Vocabulary and Schema Versioning
CEP vocabularies evolve. Therefore:

- each vocabulary entry MUST define a stable URI
- deprecated terms are never reused
- canonicalization must state vocabulary version
- adapters must declare the vocab version they target

Versioning is part of the trust model.

## 5. Adapter Algebra
Adapters form a category of typed rewriting morphisms:

- each adapter has a domain and codomain schema
- composition must be well-defined and deterministic
- identity adapters must exist for each schema version
- adapters MUST document partiality (when they can fail)

CEP interoperability relies on predictable adapter composition.

## 6. Global Integrity Constraints
All domains must adhere to:

- unique verifiable IDs
- referential integrity for entity relationships
- attestation timestamps ≥ dependency timestamps
- symmetry/antisymmetry rules for relationships as needed

These constraints prevent inconsistent or unverifiable data.

## 7. Security and Attestation
Every CTag (cryptographic tag) must:

- commit to a canonical serialization (CEC)
- state the vocabulary version
- state the adapter version
- include attestation metadata
- guard against canonicalization confusion

Security is inseparable from canonicalization.

## 8. Minimal Feature Set for Unique Identification
Across all domains CEP defines:

- minimal identity-defining attributes
- additional non-identity metadata
- optional descriptive context

Identity must be explicit and separable from metadata.

---

## Summary
These eight principles are the architectural backbone of CEP. They define the
minimal mathematical and engineering structure necessary for CEP to function as
a unified, multi-domain rewriting system supporting canonicalization, hashing,
provenance, and exchange.
