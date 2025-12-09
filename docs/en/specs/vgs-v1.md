# Versioning Governance Specification (VGS v1)

Version: 1.0.0

Status: Draft

Applies to: CEP schemas, vocabularies, adapters, fingerprints, canonical encoding, graph normalization

Purpose: Provide a coherent and formal approach to versioning in CEP, ensuring stability, backward compatibility, and long-term reproducibility.

---

# 1. Overview

CEP consists of several interacting specifications:

- Canonical encoding (CEC)
- Entity fingerprints (EFS)
- Adapter algebra (AAS)
- Graph normalization (GNS)
- Controlled vocabularies
- Domain schemas
- Adapters

Each of these evolves over time. Versioning Governance Specification (VGS) defines:

- how each component is versioned  
- what kinds of changes are allowed in each version class  
- how components reference one another  
- how backward compatibility is maintained  
- how verifiable IDs remain interpretable over time  

This is essential for the long-term stability of CEP data, hashes, and interoperability.

### Vocabulary Identification

Each CEP vocabulary is a JSON document identified by its `$id` field.

- The **canonical URI** for a vocabulary is the value of `$id`.
- All references to a vocabulary (in schemas, adapters, and documentation) MUST use this URI.
- Vocabulary documents MUST include a `$schema` field pointing to `cep.vocabulary.schema.json`.
- No additional field (such as `vocabularyUri`) is required or permitted for the canonical URI.

Tools MAY assert that `$id` is unique within a CEP deployment and SHOULD treat the `$id` value as the stable identifier for versioning, governance, and dependency resolution.


---

# 2. Versioning Design Principles

CEP versioning follows five principles:

1. Explicitness: Every versionable artifact declares its version using Semantic Versioning (SemVer).
2. Locality: Each artifact (schema, vocab, adapter, CEC, EFS, GNS) versions independently.
3. Composability: Records embed a complete version tuple so verifiers can reconstruct semantics exactly.
4. Backward Compatibility: New versions must not invalidate previously valid records except via clearly documented major version changes.
5. Non-Interference: Changes in descriptive metadata must not affect identity or hashes.

---

# 3. Semantic Versioning Model

CEP uses Semantic Versioning (SemVer):

MAJOR.MINOR.PATCH

## MAJOR
Breaking changes:

- identity rules change (fingerprint rules)  
- canonicalization strategy changes in a way that affects output  
- renaming or removing vocabulary terms  
- schema structural changes  
- canonical encoding (CEC) incompatibility  
- graph normalization rule changes  
- adapter output semantics change  

MAJOR versions should be rare.

## MINOR
Backward-compatible changes:

- new optional fields  
- new vocabulary terms (non-breaking)  
- new adapters or extended adapter behavior that preserves old semantics  
- new relationship types  
- clarifications that do not change meaning  

## PATCH
Non-semantic fixes:

- typos  
- documentation clarifications  
- test coverage changes  
- reformatting of examples  

Hashes must not change across patches.

---

# 4. Versioned Components

| Component               | Version Field        | Independent? | Notes                                 |
|------------------------|----------------------|--------------|---------------------------------------|
| Canonical Encoding     | cecVersion           | Yes          | Must be stable across ecosystems      |
| Fingerprint Rules      | fingerprintVersion   | Yes          | Identity-critical                     |
| Graph Normalization    | gnsVersion           | Yes          | Affects graph-level hashes            |
| Domain Schemas         | schemaVersion        | Yes          | Structural constraints                |
| Controlled Vocabularies| vocabularyVersion    | Yes          | Must provide deprecation paths        |
| Adapters               | adapterVersion       | Yes          | Reproducibility of transformations    |

Every CEP record, fingerprint, and graph must carry all applicable version tags.

---

# 5. Version Tuples in Records

Each CEP object (entity, relationship, envelope, graph) must embed:

```json
{
  "versions": {
    "cec": "1.0.0",
    "fingerprint": "1.0.0",
    "schema": "1.0.0",
    "vocabulary": { "...": "1.0.0" },
    "adapter": "1.0.0",
    "gns": "1.0.0"
  }
}
```

This version tuple makes it possible for a verifier to:

- reconstruct canonicalization  
- rebuild the fingerprint  
- normalize the graph  
- verify relationships  
- recreate the hash  

for any record at any time in history.

---

# 6. Version Compatibility Rules

## 6.1 Schema Compatibility
A schema version may accept records from earlier MINOR/PATCH versions.  
MAJOR schema changes must include a migration adapter.  
Backfilling or reinterpretation is forbidden — migration must be explicit.

## 6.2 Vocabulary Compatibility
New vocabulary terms must not break existing records.  
Deprecated terms must not be reused.  
Vocabulary upgrades must specify:

- mappings for deprecated terms  
- migration semantics if necessary  

## 6.3 Adapter Compatibility
Composition remains valid only if target and source schema versions are compatible.  
Adapter upgrades may alter output formats only in MINOR or MAJOR versions.  
No adapter may silently target a new schema version without declaring it.

---

# 7. Versioned Provenance

Each adapter activity must record:

- adapterId  
- adapterVersion  
- schemaVersions  
- vocabularyVersions  
- timestamp  
- optional inputFingerprint  

Provenance must be version-stable: the same pipeline version tuple must always reconstruct the same output from the same input.

---

# 8. Effects on Hashes and Identity

## 8.1 Hash Interpretation
A hash is valid only in the context of the version tuple used to generate it.  
A verifier must use:

- cecVersion  
- fingerprintVersion  
- schemaVersion  
- vocabularyVersion  
- adapterVersion  
- gnsVersion  

to re-derive the canonical bytes.

## 8.2 Identity Stability
A change to:

- vocabulary labels  
- schema descriptive fields  
- adapter metadata  
- optional attributes  

must not affect fingerprints or verifiable IDs.

Only MAJOR fingerprint changes may alter identities.

---

# 9. Version Migration Requirements

Whenever a MAJOR version increases, VGS requires:

- migration adapters  
- mapping tables (old vocabulary → new vocabulary)  
- canonicalization compatibility notes  
- hash interpretation notes  

Records must be convertible through deterministic, auditable, versioned adapters.

Backward compatibility is achieved through:

- version-bridge adapters  
- provenance annotations  
- dual-version compatibility modes (optional)

---

# 10. Long-Term Guarantees

VGS ensures that:

- A CEP record from 2030 can still be verified in 2050.  
- A hash published today remains interpretable forever.  
- New domains (campaign finance, environmental, education) remain interoperable.  
- Schema/vocabulary evolution does not undermine reproducibility.  
- Fingerprints and graph-level hashes remain stable under descriptive changes.  

---

# 11. Summary

VGS v1 defines:

- independent versioning of major CEP components  
- explicit version tuples in records  
- semantic rules for MAJOR/MINOR/PATCH  
- backward-compatibility constraints  
- migration paths for incompatible updates  

This versioning framework ensures CEP remains a reproducible, extensible, and audit-ready civic data infrastructure.
