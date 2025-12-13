# Entity Fingerprint Specification (EFS v1)

Version: 1.0.0

Status: Draft

Applies to: All CEP Entity types across all civic domains

Purpose: Define a deterministic, minimal, cross-domain identity model for civic entities.

---

## 1. Overview

The Entity Fingerprint Specification (EFS) defines the minimal set of canonical features that uniquely identify an entity within CEP.
The fingerprint:

-   is derived after canonicalization (rewriting),
-   is serialized using CEC v1,
-   is hashed to produce the verifiableId,
-   remains stable across domains, sources, adapters, and time.

The fingerprint is domain-agnostic, strategy-governed, and minimal — no descriptive or non-identity metadata is included.

---

## 2. Goals

The fingerprint must:

-   produce identical results across all implementations
-   be stable across adapter versions (unless identity rules change)
-   be independent of source formatting
-   be invariant under non-identity attribute changes (e.g., address, status, phone number)
-   support cross-domain deduplication and linking
-   encode only essential identity-defining attributes

The fingerprint is not a record; it is an identity contract.

---

## 3. Canonical Fingerprint Object Structure

Every CEP Entity must generate a fingerprint object of the form:

```json
{
    "entityTypeUri": "<URI>",
    "jurisdictionFingerprint": "<object | null>",
    "identifierFingerprint": "<object>",
    "nameFingerprint": "<object>",
    "schemaVersion": "<semver>",
    "vocabularyVersion": "<mapping of vocab domains>",
    "fingerprintVersion": "1.0.0"
}
```

This object is then CEC-serialized and hashed, yielding:

`verifiableId = CTag(hash(CEC(fingerprintObject)))`

Each sub-fingerprint is defined below.

---

## 4. Identifier Fingerprint (Required)

Identifiers are the strongest signal of identity.

Rules:

1. Each entityType defines a list of primary identifier schemes
   (e.g.,

-   SNFEI (CEP universal entity ID),
-   FEC committee ID,
-   EPA facility ID,
-   IPEDS institution ID,
-   LEI for legal entities,
-   National corporate registry IDs).

2. The fingerprint MUST include all canonical identifiers available, after rewriting.

3. Identifiers MUST be represented as:

```json
{
    "<scheme>": "<canonicalValue>"
}
```

4.Identifiers are sorted by key lexicographically (CEC rule).

5. Absent identifiers are omitted, not null.

Example:

```json
{
    "snfei": "34486b...",
    "fecId": "C12345678"
}
```

---

## 5. Name Fingerprint (Required for entities with names)

Names are rewritten using the full CEP canonicalization pipeline:

-   lowercase,

-   uniform spacing,

-   punctuation removal (post abbreviation expansion),

-   locale-aware handling of accronyms / corporate forms,

-   Unicode NFC.

The fingerprint includes:

```json
{
    "legalNameNormalized": "<string>"
}
```

For individuals, this becomes:

```json
{
    "familyName": "...",
    "givenName": "...",
    "additionalNames": "...",
    "normalizedFullName": "..."
}
```

Names are generally weaker evidence than identifiers but essential when identifiers are missing or unreliable.

---

## 6. Jurisdiction Fingerprint (Optional but Recommended)

Many civic entities only make sense within a jurisdictional context (cities, counties, permits, schools, etc.).

If the entity has a jurisdiction:

```json
{
    "jurisdictionUri": "<canonical URI>"
}
```

If jurisdiction is not applicable, then omit.

---

## 7. What is not allowed in the fingerprint

Fingerprint must exclude:

-   addresses
-   dates
-   statuses
-   revision numbers
-   descriptions
-   contact information
-   provenance
-   relationships
-   email, phone, geo
-   filing history
-   members / officers / associates

These are attributes, not identity.

This strict minimalism is what prevents identity drift over time.

---

## 8. Determinism Requirements

The fingerprint MUST be:

-   constructed after canonicalization
-   stable across all platforms
-   CEC-serialized
-   independent of representation or ordering
-   stable across descriptive changes
-   variant only if identity-defining attributes change

Example:

If a municipality changes its address or mayor, the entity's fingerprint stays the same.

---

## 9. Fingerprint Versioning (Formal Versioning Structure)

Fingerprint rules evolve slowly and must be versioned explicitly.

Each fingerprint includes:

```json
"fingerprintVersion": "1.0.0"
```

Semantic versioning rules:

-   MAJOR: changes to identity rules (breaking identity linkage)
-   MINOR: addition of optional fingerprint components
-   PATCH: clarifications or bugfixes

Every hashed verifiableId implicitly commits to:

-   CEC version
-   Schema version
-   Vocabulary version(s)
-   Fingerprint version

This ensures verifiers can always interpret a fingerprint from any year.

---

## 10. Example Fingerprint Object (Municipality)

Before hashing:

```json
{
    "entityTypeUri": "https://…/entity-type/municipality",
    "jurisdictionFingerprint": { "jurisdictionUri": "US-IL" },
    "identifierFingerprint": {
        "snfei": "34486b...ca5b3"
    },
    "nameFingerprint": {
        "legalNameNormalized": "city of springfield"
    },
    "schemaVersion": "1.0.0",
    "vocabularyVersion": { "entityType": "1.0.0" },
    "fingerprintVersion": "1.0.0"
}
```

CEC → hash → CTag → verifiableId.

---

## Multiple Domains, One Fingerprint System

-   Campaign finance → donors, committees
-   Environmental → facilities, permits
-   Education → institutions, programs

All of them use the exact same fingerprint structure.

Only the content varies.

This unifies CEP across domains and ensures cross-domain linkability.
