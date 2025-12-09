# CEC v1 - Canonical Encoding for CEP

Status: Draft

Version: 1.0.0

Applies to: CEP Entities, Relationships, Envelopes, CTags

Purpose: Ensure deterministic, cross-system, cross-version hashing and verification.

---

## 1. Overview

CEC (Canonical Encoding for CEP) defines a deterministic, language-independent serialization format for all CEP records. It ensures that two semantically identical CEP structures produce identical byte sequences and therefore identical cryptographic tags.

CEC does not replace JSON, but defines the rules for turning a CEP structure into a canonical JSON byte representation.

CEC is versioned independently of CEP schemas and vocabularies.

---

## 2. Goals

-   Deterministic across programming languages
-   Deteministic across CEP versions
-   Hash-stable
-   Independent of in-memory ordering
-   Immune to whitespace or pretty-printing differences
-   Explicit about versioning
-   Backwards compatible via declared CEC version

---

## 3. Canonicalization Pipeline

CEC requires that the following pipeline be applied after CEP canonicalization and before hashing:

CEP.Normalization → CEC.Serialization → hash()

Where:

-   CEP.Normalization = rewrite pipeline (canonical names, vocabulary terms, identifiers, units, etc.)
-   CEC.Serialization = deterministic JSON encoding defined in this document


---

## 4. Canonical Serialization Rules

### 4.1 Key Ordering (Deterministic Lexicographic Order)

-   All JSON object keys must be sorted lexicographically by Unicode code point, ascending.
-   Sorting is stable.
-   No domain-specific exceptions.

Example:
`{"b":1, "a":2}` becomes:

`{"a":2,"b":1}`

### 4.2 Whitespace

-   No whitespace except where required by JSON string literals.
-   No pretty printing.
-   No indentation.
-   No newline required at end of file.

CEC is optimized for hashing, not for readability.

### 4.3 Null and Empty Field Omission Rules

To avoid non-determinism:

-   Fields with value null MUST be omitted entirely.
-   Empty arrays MUST be encoded as [] (not omitted).
-   Empty objects MUST be encoded as {} (not omitted).

Reason: presence/absence of an empty list has semantic meaning; null does not.

### 4.4 Numeric Normalization

Rules:

1. No scientific notation.
2. No trailing zeros after decimal.
3. No + sign.
4. `-0` must be encoded as `0`.
5. Integers and floats share the same normalization rules.

Examples:

```text
1.0    → 1
01.50  → 1.5
-0.000 → 0
```

### 4.5 String Normalization

-   All strings must be Unicode NFC after canonicalization.
-   Escaping rules follow RFC8259 strictly.
-   No control characters except via escape sequences.

### 4.6 Boolean Normalization

Booleans are always:

```text
true
false
```

(lowercase, ASCII).

### 4.7 List Normalization

Lists may be:

-   order-preserving if the schema defines semantic order
-   sorted lexicographically if order is not semantically meaningful
-   CEC requires each schema field to declare:

```text
"ordering": "preserved" | "sorted"
```

Default = `"preserved"`.

### 4.8 Deterministic Representation of Nested Structures

All rules apply recursively.


---

## 5. Canonical Envelope Structure (Required Metadata)

Every CEP object that participates in hashing MUST include:

-   "cecVersion" — version string (e.g., "1.0.0").
-   "schemaVersion" — version of the CEP schema used.
-   "vocabularyVersion" — list or mapping of vocab versions used.
-   "adapterVersion" — version of the adapter that produced the record.

This ensures hashes remain interpretable even as schemas change.


---

## 6. Versioning Rules (Formal Versioning Structure)

CEC itself must be versioned using SemVer:

-   MAJOR: breaking changes
-   MINOR: behavior additions that preserve determinism
-   PATCH: clarifications or typo fixes

Every CEP structure hashed MUST include:

-   "cecVersion" — the version used to transform it into bytes
-   "schemaVersion" — because schemas change
-   "vocabularyVersion" — because vocabularies evolve
-   "adapterVersion" — because adapter logic changes

Guaranteed Property:

For any fixed {cecVersion, schemaVersion, vocabularyVersion, adapterVersion}, the hash of a CEP structure is deterministic across all implementations.

This is the backbone of verifiable civic data.


---

## 7. Example Canonical Byte Representation

Input structure:

```json
{
    "legalName": "City of Springfield",
    "identifiers": {
        "snfei": { "value": "abc123" },
        "localId": null
    },
    "status": { "statusCode": "ACTIVE", "statusEffectiveDate": "1900-01-01" }
}
```

After CEP canonicalization → CEC v1 serialization:

```json
{
    "cecVersion": "1.0.0",
    "identifiers": { "snfei": { "value": "abc123" } },
    "legalName": "City of Springfield",
    "status": { "statusCode": "ACTIVE", "statusEffectiveDate": "1900-01-01" }
}
```

Observe:

-   keys sorted
-   null field removed
-   minimal whitespace
-   no formatting differences
