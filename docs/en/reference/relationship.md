# Relationship Records

A **RelationshipRecord** models a connection between two entities.  
Relationships define structure, governance, control, affiliation, and membership in civic systems.

Where EntityRecords describe _what something is_, RelationshipRecords describe _how two things relate_.

---

## 1. Structure

| Field | Description |
|-------|-------------|
| `fromEntityId` | Source entity |
| `toEntityId` | Target entity |
| `relationshipTypeUri` | Vocabulary describing the connection |
| `timestamps` | When the relationship is valid |
| `attestations` | Proofs or verification of the relationship |

Relationships also inherit:

- Envelope fields  
- Canonical schema version  
- Revision lifecycle  

---

## 2. Common Relationship Types

- `#governs`  
- `#reports-to`  
- `#affiliate-of`  
- `#subsidiary-of`  
- `#vendor-for`  
- `#receives-grant-from`  
- `#board-membership`  

Each is governed through the Relationship Vocabulary.

---

## 3. Example RelationshipRecord

```json
{
  "recordKind": "Relationship",
  "relationshipTypeUri": ".../relationship-type.json#governs",
  "fromEntityId": "cep-entity:snfei:aaa...",
  "toEntityId": "cep-entity:snfei:bbb...",
  "timestamps": {
    "validFrom": "2023-01-01"
  },
  "attestations": [
    { "attestationTimestamp": "2023-04-01T00:00:00Z", "proofType": "ManualAttestation" }
  ],
  "revisionNumber": 1
}
```

---

## 4. Use Cases

- School board -> school district relationships  
- Nonprofit -> fiscal sponsor relationships  
- Campaign -> committee hierarchy  
- Government agency -> subdivision governance  
- Vendor -> contract recipient connections  

Relationship graphs allow CEP to express organizational structure and flow.

---

## 5. Provenance

Relationship provenance tracks:

- Source documents  
- Review authorities  
- Versions and updates  
- Verification method  

This ensures that civic relationship networks are high-trust and tamper-evident.
