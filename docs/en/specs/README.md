# Civic Exchange Protocol – Specification Suite

This directory contains the **formal specifications** that define the core
behavior of the Civic Exchange Protocol (CEP). These documents together form
the normative foundation for interoperability, reproducibility, and
provable identity across all CEP domains (public procurement, campaign
finance, corporate registries, environment, education, etc.).

The specifications are versioned independently. Each one describes a distinct
layer or subsystem of the protocol. Collectively they form the basis for:

- canonicalization and hashing,
- entity and relationship modeling,
- provenance and c-tags,
- adapter execution,
- graph normalization,
- identity resolution,
- vocabulary governance.

---

## Ordering of specifications

CEP has one **primary standard**, on which all others depend:

1. **CEC v1 — Canonical Encoding & Canonicalization**  
   Defines the deterministic rewriting and normalization rules used throughout CEP,
   including the canonical JSON form, string canonicalization, field ordering,
   and the hashing process that yields `verifiableId` values.

After CEC, all remaining specs are listed **alphabetically**.  
This avoids implying a linear or hierarchical dependency structure, since each
layer is designed to be *modular* and *composable*.

---

## Specification Index (Alphabetical After CEC)

### Canonical Encoding & Canonicalization
- **CEC v1**  
  Core deterministic encoding and canonicalization rules.  
  Required by all other CEP standards.

### Remaining Standards (A → Z)

- **AAS v1 — Adapter Architecture Specification**  
  Defines how raw external data is transformed into CEP domain objects.
  Includes adapter manifests, APS compatibility, self-test rules, and
  standardized envelope formats.

- **CDIRA v1 — Cross-Domain Identity Resolution & Attestation**  
  Mechanisms for merging and reconciling entities that appear across
  independent domains.  
  Includes identity graphs, similarity models, evidence weighting,
  stable reference construction, and conflict handling.

- **EFS v1 — Entity Fingerprint Specification**  
  Defines how canonicalized entities produce stable fingerprint inputs
  for hashing, including domain-specific and cross-domain fingerprint
  modules.  
  Used to derive `verifiableId` values across CEP.

- **GIC v1 — Global Integrity Constraints**  
  Cross-entity and cross-relationship constraints applicable to all CEP
  graphs, including jurisdictional closure, relationship validation,
  entity type compatibility, and temporal consistency.

- **GNS v1 — Graph Normalization Specification**  
  Defines how transformed domain records are merged into a coherent,
  deduplicated, canonical graph.  
  Includes node merging rules, relationship normalization,
  provenance tracing, and conflict resolution.

- **VGS v1 — Vocabulary Governance Specification**  
  Defines the structure, lifecycle, and evolution rules of controlled
  vocabularies used throughout CEP.  
  Includes term governance, versioning, SKOS-style mappings, and the
  relationship between vocabularies and core schemas.

---

## How these specifications fit together

A simplified view:

```text
Raw Data (external APIs, files, scrapers)
       |
       v
AAS v1 — Adapters produce domain objects
       |
       v
CEC v1 — Canonical encoding + deterministic rewriting
       |
       v
EFS v1 — Fingerprints → verifiableId creation
       |
       v
GNS v1 — Graph normalization + merging
       |
       v
CDIRA v1 — Cross-domain identity resolution
       |
       v
GIC v1 — Global integrity checks
       |
       v
VGS v1 — Controlled terms, domain vocabularies, governance
```

Each specification is self-contained but interoperable, ensuring that:

- any CEP pipeline is reproducible,
- every entity has a verifiable cryptographic identity,
- transformations are audit-ready,
- graphs remain consistent across domains and over time,
- vocabulary evolution is stable and governed.

---

## Contributing & Versioning

Every spec:

- declares a semantic version (e.g., `1.0.0`),
- must document all breaking and non-breaking changes,
- should include examples, diagrams, and reference implementations when possible.

Proposals for changes follow the **CEP Evolution Policy**, including:

- issue creation,
- discussion period,
- review by editors,
- version increment (minor/patch/major),
- publication to the specs directory.

