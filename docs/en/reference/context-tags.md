# Context Tags (CTags)

Context Tags (CTags) are a new layer in the Civic Exchange Protocol (CEP) that capture **interpretive, analytic, or contextual facts about a record**, without changing its canonical identity or payload.

They are:

- Optional
- Append-only
- Vocabulary-driven
- Non-canonical (do not affect SNFEI or verifiableId)
- Attested (you always know who applied them, when, and why)

CTags live next to a record, not inside the payload.

---

## 1. Why CTags Exist

Most data standards handle:

- **Payload fields** (facts in the record)
- **Envelope metadata** (IDs, timestamps, status, attestations)

They do not have a clean place for:

- ML-derived classifications
- Risk or quality flags
- Narrative context (for example, _key actor in investigation X_)
- Cluster membership and similarity-based hints
- Interpretive statements by analysts or oversight bodies

If you put these inside the payload, they pollute the domain model and can change semantics.  
If you try to squeeze them into provenance metadata, they become awkward and hard to query.

CTags solve this by creating a **third layer**:

1. Envelope (identity, timestamps, attestations)
2. Payload (facts)
3. Context (CTags: interpretations, analysis, narrative, risk)

---

## 2. Relationship to PTags and W3C PROV

CTags are distinct from both PTags and PROV:

- **PTags** (Privacy Tags for social content)

    - Describe how a post behaves in a privacy-preserving way (account age bucket, automation flag, client family, etc.).
    - Designed for social media research and platform transparency.
    - Domain: behavior and privacy, attached to posts.

- **CTags** (Context Tags for CEP records)

    - Describe interpretive facts about civic records: risk, analysis, narrative, quality.
    - Domain: provenance narrative and analytic interpretation.
    - Attached to Entities, Relationships, Exchanges, or aggregates.

- **W3C PROV**
    - Describes how things came to be: Entities, Activities, Agents, and their causal links.
    - CTags can reference PROV activities via `provActivityUri`, but they are simpler, operational labels for day-to-day analysis.

That is:

- PROV is the **graph** of what happened.
- The CEP envelope is the **canonical record** of what is.
- CTags are the **commentary layer**: what we think about this record, and how we classify or interpret it.

---

## 3. CTag Schema Shape

CTags are defined by `cep.ctag.schema.json` and are typically embedded as an array property `ctags` in CEP records.

Simplified shape:

```json
{
    "tagTypeUri": "https://.../ctag-type.v1.0.0.json#risk.flag.potential_shell",
    "code": "risk.flag.potential_shell",
    "value": "cluster_07",
    "appliedBy": "cep-analysis:snfei-risk-v1",
    "appliedAt": "2025-12-07T10:00:00Z",
    "scope": "record",
    "confidence": 0.87,
    "note": "High-velocity donations across related PACs.",
    "sourceRunId": "risk-model-2025-12-07T09-55Z",
    "provActivityUri": "urn:prov:activity:snfei-risk-scan:2025-12-07"
}
```

Key points:

- `tagTypeUri` and `code` tie the tag to a controlled vocabulary term.
- `appliedBy` and `appliedAt` make the tag attributable and auditable.
- `scope` and `targetPath` let you aim the tag at a full record, a particular field, or an inferred relationship.
- `confidence` is optional but encouraged for ML-inferred tags.

---

## 4. Embedding CTags in CEP Records

CTags appear as an optional array at the top level of an Entity, Relationship, or Exchange record.

Example (Entity excerpt):

```json
{
    "verifiableId": "cep-entity:snfei:34486b3...",
    "recordKind": "Entity",
    "recordTypeUri": "https://.../entity-type.v1.0.0.json#municipality",
    "schemaVersion": "1.0.0",
    "jurisdictionIso": "US-MN",
    "legalName": "City of Springfield",
    "identifiers": [
        {
            "schemeUri": "https://.../entity-identifier-scheme.v1.0.0.json#snfei",
            "identifier": "34486b3..."
        }
    ],
    "status": {
        "statusCode": "ACTIVE",
        "statusEffectiveDate": "1900-01-01"
    },
    "attestations": [
        {
            "attestationTimestamp": "1900-01-01T00:00:00.000000Z",
            "attestorId": "cep-entity:example:ingest",
            "proofType": "ManualAttestation"
        }
    ],
    "ctags": [
        {
            "tagTypeUri": "https://.../ctag-type.v1.0.0.json#risk.flag.potential_shell",
            "code": "risk.flag.potential_shell",
            "value": "cluster_07",
            "appliedBy": "cep-analysis:snfei-risk-v1",
            "appliedAt": "2025-12-07T10:00:00Z",
            "scope": "record",
            "confidence": 0.87,
            "note": "Pattern matches known shell-like structures in state filings."
        },
        {
            "tagTypeUri": "https://.../ctag-type.v1.0.0.json#analysis.cluster.membership",
            "code": "analysis.cluster.membership",
            "value": {
                "clusterId": "mn-muni-cluster-02",
                "method": "louvain",
                "graph": "snfei-donation-graph-v3"
            },
            "appliedBy": "cep-analysis:graph-cluster-v3",
            "appliedAt": "2025-12-07T10:05:00Z",
            "scope": "record",
            "confidence": 0.93
        }
    ]
}
```

The record remains valid CEP even if `ctags` is omitted entirely.  
CTags are designed to be safe to drop and safe to ignore.

---

## 5. Design Principles

CTags obey several key principles:

1. **Non-canonical**

    - CTags never participate in the SNFEI hash or in the canonical string.
    - Changing or adding CTags does not change `verifiableId`.

2. **Append-only**

    - Systems should treat `ctags` as append-only.
    - New tags may be added over time as models improve or oversight evolves.
    - Historical tags should be retained for audit and reproducibility.

3. **Attributable**

    - Every tag is tied to `appliedBy` and `appliedAt`.
    - Optional `sourceRunId` and `provActivityUri` provide deeper reproducibility.

4. **Vocabulary-driven**

    - `tagTypeUri` and `code` refer to a controlled vocabulary for interoperability.
    - Vocabularies can define enums, allowed shapes, and intended usage.

5. **Interoperable and Optional**
    - Downstream systems may filter, group, or display records based on CTags.
    - Systems that do not understand CTags can ignore them safely.

---

## 6. Typical Use Cases

Some common patterns where CTags are useful:

- Risk analysis

    - Flags for potential shell entities, pass-through entities, high-risk flows.

- Data quality

    - Indicators of incomplete address, inconsistent identifiers, or duplicate candidates.

- Narrative and investigation

    - Marking key actors, focal relationships, or important funding chains in cases or reports.

- Model outputs

    - ML or heuristic model classifications attached as tags, including confidence scores.

- Aggregation and rollup
    - Indicators that a record participates in an aggregate (for example, rollup-by-grant-program or funding stream).

---

## 7. Interaction With Governance

CTags are governed like any other vocabulary-backed component in CEP:

- New CTag types are proposed, reviewed, and versioned through the vocabulary governance process.
- Deprecation of CTag types is handled via vocabulary status flags.
- Implementations are encouraged to log which CTag types they emit and to document their semantics.

Because CTags are non-canonical and optional, introducing new types does not break existing records.  
This makes CTags a safe, evolvable layer for emerging analytic and oversight needs.

---

## 8. Summary

CTags give CEP a dedicated layer for:

- Interpretive, analytic, or narrative facts
- Risk and quality signals
- ML and heuristic outputs
- Human oversight tagging

They are the missing piece between raw facts (payload) and pure provenance (PROV), allowing researchers, agencies, and tools to enrich records without compromising identity or integrity.
