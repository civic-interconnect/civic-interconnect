# Cross-Domain Identity Resolution Algorithm (CDIRA v1)

Version: 1.0.0

Status: Draft

Applies to: All CEP entities across all domains (campaign finance, environment, education, municipal, etc.)

Purpose: Define a deterministic algorithm for resolving when multiple CEP entities (possibly from different domains or sources) represent the same real-world entity.

---

# 1. Overview

CEP treats identity as a minimal, canonical fingerprint (EFS v1) plus a rewriting-based normalization strategy. Cross-domain identity resolution is the process of:

-   detecting when multiple CEP entities refer to the same real entity,
-   assigning them to a shared identity cluster, and
-   ensuring that this process is deterministic, auditable, and versioned.

The Cross-Domain Identity Resolution Algorithm (CDIRA) defines:

1. The evidence model for identity.
2. The deterministic resolution steps (candidate generation, evidence evaluation, cluster assignment).
3. The relationship between fingerprints, graphs, and identity clusters.
4. Versioning and provenance requirements for the resolution process.

CDIRA is a rewriting system over entity graphs: it rewrites sets of entity nodes into equivalence classes (identity clusters) using strategy-governed rules.

---

# 2. Identity Model

CDIRA operates on CEP entities that already satisfy:

-   canonicalization (names, identifiers, vocabularies),
-   fingerprint specification (EFS v1),
-   canonical encoding (CEC v1),
-   graph normalization (GNS v1) where applicable.

## 2.1 Identity Units

An Identity Unit is a single CEP entity with:

-   verifiableId
-   fingerprint (EFS object)
-   domain-specific payload
-   provenance

## 2.2 Identity Cluster

An Identity Cluster is a non-empty set of Identity Units believed to refer to the same real-world entity.

Each cluster has:

-   clusterId (stable identifier, see Section 7)
-   members: list of verifiableIds
-   clusterFingerprint: optional aggregated fingerprint summary
-   cdiraVersion: version of the resolution algorithm used
-   provenance for how and when it was formed

---

# 3. Evidence Model

CDIRA uses deterministic, rule-based evidence classes. No probabilistic black-box logic is required in the core spec (implementations may use statistical methods internally, but final decisions must be reproducible).

Evidence is grouped into:

-   Strong evidence
-   Moderate evidence
-   Weak evidence

## 3.1 Strong Evidence

Strong evidence is sufficient to treat two entities as identical:

-   Exact fingerprint match (same EFS fingerprint, same verifiableId).
-   Shared authoritative identifier under a globally trusted scheme:
    -   same SNFEI, LEI, FEC ID, EPA Facility ID, IPEDS ID, national corporate registry ID, etc., after canonicalization.

If strong evidence is present, entities must be placed in the same cluster.

## 3.2 Moderate Evidence

Moderate evidence suggests likely identity but is not self-sufficient:

-   Same canonical name + same jurisdictionUri + same entityTypeUri.
-   Same canonical name + shared external identifier from a mid-confidence registry.
-   Name equivalence plus matching normalized attributes that are relatively stable.

Moderate evidence may trigger clustering if no conflicting evidence exists.

## 3.3 Weak Evidence

Weak evidence by itself must not cause a merge:

-   co-occurrence patterns (same officers, same addresses),
-   shared phone or email,
-   similar but not identical names,
-   proximity in graph structure.

Weak evidence is only used to support moderate evidence or break ties.

---

# 4. Deterministic Resolution Strategy

CDIRA defines a three-phase resolution pipeline:

1. Candidate Generation
2. Evidence Evaluation
3. Cluster Assignment

## 4.1 Candidate Generation

Candidate generation finds potential matches but does not decide identity.

Blocking keys (deterministic):

-   Identifier-based blocks: entities sharing a canonical value under any identifier scheme.
-   Name + jurisdiction blocks: same legalNameNormalized AND same jurisdictionUri.
-   Domain-specific blocks: e.g., same IPEDS ID, same EPA Registry ID, same FEC ID.

Within each block, consider all unordered pairs as candidates.

## 4.2 Evidence Evaluation

For each candidate pair (A, B):

1. Collect evidence of all types.
2. Apply rules in order:

### Rule 1 (Fingerprint Equality).

If A.verifiableId == B.verifiableId, they must be in the same cluster.

### Rule 2 (Strong Identifier Equality).

If they share an authoritative identifier and no explicit conflict exists, they must be merged.

### Rule 3 (Moderate Evidence Rule).

If:

-   names, jurisdiction, and entity type match,
-   no contradictory identifier evidence exists,
-   one or more moderate evidence conditions hold,

then A and B should be clustered.

### Rule 4 (Conflict Rule).

If strong identifiers match but identity-defining attributes contradict domain rules, they must not be auto-merged. Emit a conflict record.

### Rule 5 (Default Non-Merge).

If weak evidence only, entities remain separate.

## 4.3 Cluster Assignment

Clusters are formed using transitive closure:

If A merges with B, and B merges with C, then all three belong to the same cluster unless forbidden by a conflict rule.

Cluster construction is deterministic given:

-   same input entities,
-   same version tuple,
-   same configuration.

---

# 5. CDIRA as a Rewriting System

Conceptually, CDIRA:

-   Starts from singleton clusters `{A}, {B}, {C}, ...`
-   Applies merge rewrites based on evidence rules:
    -   `{A}, {B} → {A,B}`
-   Produces a partition of the entity set.

The merge operation is:

-   associative,
-   idempotent (re-running CDIRA on identical clusters produces no changes).

The internal merge process need not be commutative; the resulting partition must be independent of evaluation order.

---

# 6. Conflict Handling

CDIRA must produce explicit artifacts for:

-   conflicting strong identifiers,
-   inconsistent identity-defining attributes,
-   ambiguous clusters with insufficient evidence.

Conflicts are recorded as:

```json
{
  "conflictType": "IdentifierConflict" | "FingerprintConflict" | "AmbiguousCluster",
  "entities": ["verifiableId1", "verifiableId2", "..."],
  "evidence": {
    "strong": [],
    "moderate": [],
    "weak": []
  },
  "cdiraVersion": "1.0.0",
  "timestamp": "...",
  "resolutionStatus": "unresolved" | "manuallyResolved" | "ignored"
}
```

These become part of provenance and may be resolved later.

---

# 7. Cluster Identifiers

Each Identity Cluster receives a stable clusterId.

Two allowed strategies:

1. Derived clusterId (hash-based):

-   Deterministic hash of:

    -   sorted member verifiableIds
    -   version tuple

2. Externally assigned clusterId:

-   Used when authoritative registries assign persistent IDs.

In both cases:

`clusterId = "cep-cluster:" || base64url( H( clusterSummary ) )`

Where clusterSummary is a CEC-serialized object including:

-   sorted member IDs
-   version tuple
-   optional clusterFingerprint

---

# 8. Versioning and Provenance

CDIRA is versioned:

`cdiraVersion: 1.0.0`

Every cluster and conflict record must include:

```json
{
    "cdiraVersion": "1.0.0",
    "versions": {
        "cec": "...",
        "fingerprint": "...",
        "schema": "...",
        "vocabulary": {},
        "adapter": "...",
        "gns": "..."
    }
}
```

Identity resolution is a provenance activity:

-   identityResolverId
-   identityResolverVersion
-   timestamp
-   input sets (entity IDs)
-   output clusters and conflicts

This ensures auditability and reproducibility.

---

# 9. Determinism Requirements

CDIRA must be deterministic:

Given the same inputs, versions, and configuration, the resulting clusters and conflicts must be identical.

Any use of probabilistic or heuristic methods must:

-   produce deterministic outputs (e.g., fixed seeds), or
-   be advisory only, not part of final merge decisions.

---

# 10. Summary

CDIRA v1 defines:

-   a rule-based deterministic approach to cross-domain identity resolution
-   an evidence model (strong, moderate, weak)
-   a rewrite system forming clusters via merge operations
-   explicit conflict handling
-   stable cluster identifiers
-   full versioning and provenance for identity decisions

This specification ties together canonicalization (CEC), fingerprints (EFS), graph normalization (GNS), and adapter semantics (AAS) into a coherent, cross-domain identity resolution framework for CEP.
