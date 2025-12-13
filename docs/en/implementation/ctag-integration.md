# CTag Integration in CEP Record Envelopes

This is provided for implementers of CEP-compliant systems and pipelines.

---

# 1. Purpose

Context Tags (**CTags**) are lightweight annotations that attach to a **record envelope**, not to the internal entity, relationship, or exchange payload.

CTags provide interpretive, analytic, or contextual notes that help downstream systems understand how a record is being used, evaluated, or interpreted.
They do **not** affect canonical identity, SNFEI, schema validity, or the meaning of the core data.

CTags are:

- optional  
- vocabulary-governed  
- non-destructive  
- independent of canonicalization  
- safe to add, modify, or remove without altering the record's semantics  

This document defines how CTags integrate with CEP record envelopes.

---

# 2. Record Envelope Overview

All CEP records (entities, relationships, exchanges, p3tags, etc.) share the same envelope structure.
The envelope contains:

- identity and type information  
- schema version  
- lifecycle status  
- timestamps  
- attestations  
- optional **ctags**  

The CTags appear at the envelope level:

```json
{
  "recordKind": "entity",
  "recordSchemaUri": "...",
  "schemaVersion": "1.0.0",
  "revisionNumber": 1,
  "verifiableId": "cep-entity:snfei:...",
  "recordTypeUri": "...",
  "status": { "...": "..." },
  "timestamps": { "...": "..." },
  "attestations": [ "...snip..." ],

  "ctags": [
    {
      "typeUri": "https://example.org/vocab/ctag-type#analysis.cluster.membership",
      "value": "cluster-12",
      "note": "Optional note."
    }
  ]
}
```

The **payload** (e.g., entity fields, relationship fields, exchange content) sits beside the envelope fields, not inside CTags.

---

# 3. Why CTags Live in the Envelope

### 3.1 Separation of Meaning vs Interpretation

The envelope is the correct location for annotations because:

- The **payload** expresses the factual civic record.
- The **envelope** expresses lifecycle context, attestations, and analytic overlays.
- CTags belong with the latter.

This separation prevents accidental semantic modification of the underlying civic facts.

---

### 3.2 Safe for Canonicalization

CTags **do not participate** in:

- normalization  
- canonical input building  
- SNFEI hashing or ID derivation  

A record with or without CTags must have the **same SNFEI** and the same canonical identity.

Deterministic pipelines must treat CTags as optional, removable accessories.

---

### 3.3 Compatible With Multiple Uses

Envelope-level CTags support:

- risk flags  
- data quality indicators  
- clustering or classification results  
- editorial highlights  
- narrative tags used in reports  
- AI-assisted annotations  

All without polluting the core civic data model.

---

# 4. CTag Object Structure

Each tag references a controlled vocabulary term:

```json
{
  "typeUri": "https://example.org/vocab/ctag-type#quality.issue.incomplete_address",
  "value": true,
  "note": "Address missing postal code"
}
```

Fields:

| Field     | Required | Description |
|-----------|----------|-------------|
| `typeUri` | yes      | URI of the CTag type from the ctag-type vocabulary |
| `value`   | no       | JSON value (string, boolean, number, object) |
| `note`    | no       | Human-readable explanation |

Implementations may extend with additional optional fields as long as the vocabulary contract remains intact.

---

# 5. How Systems Should Use CTags

### 5.1 Ingestion Pipelines
Adapters may add tags such as:

- incomplete fields  
- inconsistent identifiers  
- address quality issues  

Example:

```json
{
  "ctags": [
    {
      "typeUri": "https://...#quality.issue.incomplete_address",
      "value": true
    }
  ]
}
```

---

### 5.2 Analysis and Machine Learning Pipelines

Analytic systems may add tags like:

- cluster membership  
- risk classification  
- anomaly scores  
- narrative highlights  
- AI summary categories  

These do not change the core record; they only annotate it.

Example:

```json
{
  "ctags": [
    {
      "typeUri": "https://...#analysis.cluster.membership",
      "value": "cluster-7"
    },
    {
      "typeUri": "https://...#narrative.highlight.key_actor",
      "note": "Mentioned in investigative report"
    }
  ]
}
```

---

### 5.3 Exchange and Workflow Systems

When a workflow involves document packets, filings, or automated transformations, CTags may indicate:

- processing status  
- triage flags  
- routing categories  
- confidence levels from AI models  

Because CTags are non-semantic, they can be applied uniformly across record types.

---

# 6. Validation Rules

A conformant implementation MUST ensure:

1. `typeUri` is a valid URI and maps to a vocabulary term.  
2. CTags do **not** modify `verifiableId`, canonical identity, or payload semantics.  
3. `value` is valid JSON if present.  
4. Adding or removing a CTag must leave the core record unchanged.  
5. CTags must not interfere with schema-required fields.

Best practices:

- flag deprecated CTag terms  
- treat unknown terms as warnings, not fatal errors  
- keep CTags small and additive  

---

# 7. Example: Entity Record Envelope with CTags

```json
{
  "recordKind": "entity",
  "recordSchemaUri": "https://.../entity.schema.json",
  "schemaVersion": "1.0.0",
  "revisionNumber": 1,
  "verifiableId": "cep-entity:snfei:...",
  "recordTypeUri": "https://...#municipality",
  "status": { "statusCode": "ACTIVE", "statusEffectiveDate": "1900-01-01" },
  "timestamps": { "firstSeenAt": "...", "lastUpdatedAt": "...", "validFrom": "..." },
  "attestations": [ { "...": "..." } ],

  "ctags": [
    {
      "typeUri": "https://...#narrative.highlight.key_actor",
      "note": "Frequently referenced in planning documents"
    }
  ],

  "legalName": "City of Springfield",
  "jurisdictionIso": "US-IL",
  "identifiers": { "...": "..." }
}
```

---

# 8. Summary

- CTags live exclusively in the **record envelope**, not in core payload structures.  
- CTags provide non-destructive, optional, vocabulary-driven annotations.  
- Adding, removing, or modifying CTags does not affect canonicalization or identity.  
- CTags support analytics, data quality, workflows, and narrative reporting.  
- CTag infrastructure unifies annotation across all CEP record families.

