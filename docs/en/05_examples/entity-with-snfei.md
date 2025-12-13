# Example: CEP EntityRecord with SNFEI

This example demonstrates how a CEP `EntityRecord` includes a **Structured Non-Fungible Entity Identifier (SNFEI)** when an entity does not have a national or global registry ID (such as LEI or SAM-UEI).  
SNFEI provides a deterministic, recomputable identifier for joining datasets across civic, nonprofit, educational, and local-government domains.

---

## Input (Normalized Entity Payload)

This is the minimal normalized payload an adapter or ETL process would emit:

```json
{
    "jurisdictionIso": "US-MN",
    "legalName": "Example School District 123",
    "legalNameNormalized": "example school district 123",
    "snfei": "34486b382c620747883952d6fb4c0ccdbf25388dfb0bb99231f33a93ad5ca5b3",
    "entityType": "educational-institution"
}
```

The SNFEI here is the SHA-256 hash of the canonical input string:

`legalNameNormalized|addressNormalized|countryCode|registrationDate`

Empty/None fields are included as empty strings to keep positions stable.

Example (no address, no registration date):

`example school district 123||US|`

Example (with address, no registration date):

`new york school district 01|200 learning street|US|`


---

## Output (CEP EntityRecord)

After running this normalized input through the CEP builder, the resulting `EntityRecord` looks like this:

```json
{
    "recordKind": "entity",
    "recordSchemaUri": "https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/schemas/core/cep.entity.schema.json",
    "schemaVersion": "1.0.0",
    "revisionNumber": 1,

    "verifiableId": "cep-entity:snfei:34486b382c620747883952d6fb4c0ccdbf25388dfb0bb99231f33a93ad5ca5b3",
    "recordTypeUri": "https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabulary/core/entity-type.json#educational-institution",

    "status": {
        "statusCode": "ACTIVE",
        "statusEffectiveDate": "1900-01-01"
    },

    "timestamps": {
        "firstSeenAt": "1900-01-01T00:00:00.000000Z",
        "lastUpdatedAt": "1900-01-01T00:00:00.000000Z",
        "validFrom": "1900-01-01T00:00:00.000000Z"
    },

    "attestations": [
        {
            "attestationTimestamp": "1900-01-01T00:00:00.000000Z",
            "attestorId": "cep-entity:example:ingest",
            "verificationMethodUri": "urn:cep:attestor:cep-entity:example:ingest",
            "proofType": "ManualAttestation",
            "proofPurpose": "assertionMethod"
        }
    ],

    "jurisdictionIso": "US-MN",
    "legalName": "Example School District 123",
    "legalNameNormalized": "example school district 123",

    "identifiers": [
        {
            "schemeUri": "https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabulary/entity-identifier-scheme.v1.0.0.json#snfei",
            "identifier": "34486b382c620747883952d6fb4c0ccdbf25388dfb0bb99231f33a93ad5ca5b3"
        }
    ]
}
```

---

## Key Points

### Deterministic ID

The `verifiableId` incorporates the SNFEI value to create a stable, recomputable entity identifier:

```
cep-entity:snfei:<hash>
```

### Vocabulary-backed Identifier Scheme

The SNFEI entry references the official vocabulary term:

```
https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabulary/entity-identifier-scheme.v1.0.0.json#snfei
```

This ensures consistent identifier semantics across systems.

### Minimal but Complete Envelope

Even in a minimal example, CEP includes:

-   envelope metadata (`recordKind`, `schemaVersion`)
-   timestamps
-   an attestation block
-   status envelope

---

## When to Use SNFEI

Use SNFEI when:

-   an entity lacks LEI, SAM-UEI, or other authoritative identifiers,
-   datasets need a stable join key,
-   building civic registries,
-   integrating multiple heterogeneous data sources.

SNFEI is a deterministic, transparent identifier that enables **cross-dataset linkage without a central registry**.
