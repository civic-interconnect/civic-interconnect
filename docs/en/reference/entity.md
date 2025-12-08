# Entity Records

A **CEP EntityRecord** represents a real-world organization, jurisdiction, or legally recognized actor.
It is the foundation for linking civic data across domains such as campaign finance, procurement, grants, education, and nonprofit oversight.

EntityRecords combine:

- Canonical identity (SNFEI)
- Domain classifications
- Provenance and attestations
- Status lifecycle
- Cryptographic record integrity

---

## 1. Structure

An EntityRecord includes:

### 1.1 Core Fields

| Field | Description |
|-------|-------------|
| `verifiableId` | Cryptographically derived identity (`cep-entity:snfei:<hash>`) |
| `entityTypeUri` | Vocabulary reference describing entity category |
| `jurisdictionIso` | ISO-like jurisdiction code (e.g., `US-MN`) |
| `legalName` | Human-readable legal name |
| `legalNameNormalized` | Normalized form used to compute SNFEI |
| `identifiers` | External and internal identifiers (SNFEI, LEI, UEI, EIN, etc.) |

### 1.2 Envelope Fields

EntityRecords inherit the CEP record envelope:

- `schemaVersion`
- `recordSchemaUri`
- `revisionNumber`
- `previousRecordHash`
- `status` block (ACTIVE / INACTIVE)
- `timestamps`
- `attestations`
- `ctags`

See `/en/implementation/record-envelope.md` for details.

---

## 2. SNFEI in Entity Records

The SNFEI identity appears twice:

1. In identifiers:

```json
"identifiers": {
  "snfei": { "value": "3448..." }
}
```

2. In verifiableId:

```json
"verifiableId": "cep-entity:snfei:3448..."
```

This ensures:

- Cross-schema consistency  
- Reproducible identity derivation  
- Compatibility with external ID systems  

---

## 3. entityTypeUri

Entity type is resolved via the entity-type vocabulary:

```
https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabularies/entity-type.v1.0.0.json#municipality
```

Adapters provide simple labels (`"municipality"`), and the builder expands them to the full URI.

---

## 4. Example EntityRecord

```json
{
  "schemaVersion": "1.0.0",
  "recordSchemaUri": ".../schemas/cep.entity.schema.json",
  "verifiableId": "cep-entity:snfei:34486b38...",
  "entityTypeUri": ".../vocabularies/entity-type.v1.0.0.json#municipality",
  "jurisdictionIso": "US-MN",
  "legalName": "City of Springfield",
  "legalNameNormalized": "city springfield",
  "identifiers": {
    "snfei": { "value": "34486b38..." }
  },
  "status": {
    "statusCode": "ACTIVE",
    "statusEffectiveDate": "1900-01-01"
  },
  "attestations": [
    {
      "attestationTimestamp": "2025-01-01T00:00:00Z",
      "proofType": "ManualAttestation"
    }
  ],
  "revisionNumber": 1
}
```

---

## 5. How EntityRecords Are Produced

1. Adapter Normalizes Input  
2. Canonicalization builds hash string  
3. SNFEI computed (Rust or Python)  
4. Entity builder constructs full envelope  
5. Record emitted as JSON

---

## 6. Usage

EntityRecords are used for:

- Linking datasets (campaign finance -> contracts -> lobbying)  
- Regulatory and financial reporting  
- Auditable data pipelines  
- Provenance-aware knowledge graphs  

Entity identity is the backbone of the CI/CEP ecosystem.
