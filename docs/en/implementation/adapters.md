# CEP Adapters: Implementation Guide

Adapters are the mechanism by which heterogeneous civic data sources are rewritten into canonical CEP records.
Each adapter is a deterministic, strategy-governed transformation function that takes a source-specific record and returns a fully validated CEP
**entity**, **relationship**, or **exchange**, wrapped in a CEP **record envelope**.

This document describes the adapter model, required invariants, implementation structure, and best practices for adding new domain or jurisdiction adapters.

---

## 1. CEP Adapter

A **CEP adapter** is a deterministic mapping:

```
SourceRecord → CEPRecord
```

It consists of three layered rewriting stages:

1. **Lexical canonicalization** - Normalizes raw strings, punctuation, Unicode, abbreviations, corporate suffixes, whitespace, etc.

2. **Semantic expansion** - Converts codes, categories, and jurisdiction-specific classifications into CEP **vocabulary URIs**. Aligns the structure with CEP schemas.

3. **Schema alignment + envelope construction** - Produces a CEP JSON payload and adds:
    - recordSchemaUri
    - recordKind
    - vocabulary references
    - timestamps
    - attestation placeholders
    - identity inputs (used later for SNFEI)

Adapters do **not** compute SNFEI hashes directly.

---

## 2. Determinism and Strategy Control

Adapters use **ordered, stratified rewriting**, not free application of rules.  
This guarantees:

-   deterministic output
-   no rule commutation
-   predictable interpretation of source records
-   reproducible hash inputs

Evaluation order:

1. information-preserving rewrites
2. semantic enrichments
3. information-reducing defaults
4. schema assembly
5. envelope construction

Only the full pipeline defines semantic meaning.

---

## 3. Input and Output Types

### Input

Any structured representation of source data  
(e.g., CSV row → dict, API JSON → dict).

### Output

A dict that validates under a CEP JSON Schema:

-   `cep.entity.schema.json`
-   `cep.relationship.schema.json`
-   `cep.exchange.schema.json`
-   domain-specific schemas in `schemas/domains/…`

This payload is then wrapped in a CEP record envelope.

---

## 4. Adapter Responsibilities

Every adapter must implement:

### 4.1 Structural Mapping

-   Select target CEP record type.
-   Map source fields → CEP fields.
-   Remove non-CEP source fields.

### 4.2 Name Canonicalization

Use the global canonicalization module:

-   ASCII folding
-   Unicode NFKC
-   corporate suffix normalization
-   jurisdictional abbreviation expansion
-   strict whitespace/punctuation rules

Never implement local name hacks.

### 4.3 Vocabulary Application

Controlled vocabularies require the adapter to produce URIs such as:

```
"committeeTypeUri": "cep:committeeType:cf:principalCampaignCommittee"
```

Rules:

-   must use valid, versioned URIs
-   must not invent terms
-   must not use deprecated codes

### 4.4 Identifier Handling

Adapters:

-   **may** parse external identifiers (OCD, LEI, SAM-UEI, etc.)
-   **must not** compute CEP SNFEI
-   **must** expose cleaned identity-relevant fields

Identity invariants must be preserved.

### 4.5 Provenance Attachment

Include minimal provenance:

-   adapterVersion
-   sourceUri or metadata
-   attestation seed data

Downstream pipelines may enrich provenance.

---

## 5. Adapter Composition

Adapters compose into the following chain:

```
raw_source
   → lexical canonicalizer
   → domain adapter
   → jurisdiction adapter
   → entity canonicalizer (SNFEI input)
   → envelope constructor
```

Properties:

-   associative (up to strategy)
-   not commutative
-   fully deterministic

Each adapter must declare:

-   required upstream adapters
-   required vocabularies
-   canonicalization version dependency

---

## 6. Domain vs. Jurisdiction Adapters

### Domain Adapters

Define the meaning of data within a domain:

-   campaign finance
-   environmental permits
-   education
-   procurement
-   elections

Domain adapters perform:

-   code → vocabulary mapping
-   high-level structural alignment
-   domain canonicalization rules

### Jurisdiction Adapters

Handle differences across states, counties, authorities:

-   state-specific IDs
-   local naming conventions
-   differing code definitions
-   special cases or omissions

A domain can have many jurisdiction adapters.

---

## 7. Rust and Python Implementations

### Python Location

```shell
src/python/src/civic_interconnect/cep/adapters/
    us_mn_campaign_finance.py
    us_ca_environment.py
```

### Rust Location

```shell
crates/cep-adapters/src/us/mn/campaign_finance.rs
crates/cep-adapters/src/us/ca/environment.rs
```

Both languages must implement equivalent rewriting semantics.

### Codegen Integration

Adapters consume generated constants for:

-   schema URIs
-   vocabulary URIs
-   record kinds

Avoid hand-typed camelCase; always use generated constants.

---

## 8. Testing Requirements

Every adapter must include:

-   **Round-trip tests** - Sample → canonical → schema-validated.

-   **Identity stability tests** - SNFEI must be stable under irrelevant reordering.

-   **Vocabulary resolution tests** - URIs must correspond to actual vocab terms.

-   **Provenance tests** - Envelope structure must match expectations.

If any test fails, the adapter cannot be merged.

---

## 9. When to Create a New Adapter

Create a new adapter when:

-   a new domain is added
-   a new state or jurisdiction is introduced
-   a new agency format appears
-   a source version changes

Document each adapter under:

```
docs/en/implementation/adapters/
```

---

## 10. Task Checklist for Adapter Authors

### Required

-   [ ] Identify the source format
-   [ ] Build input parser
-   [ ] Apply canonicalization
-   [ ] Map domain categories to vocabularies
-   [ ] Map jurisdiction identifiers
-   [ ] Construct CEP payload
-   [ ] Run canonicalization to compute SNFEI input
-   [ ] Construct envelope
-   [ ] Add attestation seed
-   [ ] Add sample input/output records
-   [ ] Add test suite (round-trip, vocab, identity)

### Optional

-   [ ] Add debug logging for rewrite steps
-   [ ] Document edge cases
-   [ ] Add CTag suggestions for low-quality data

