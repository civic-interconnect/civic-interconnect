# Use Correct Casing

## Golden Rule

- External JSON (schemas + records) use camelCase.
- Internal code (Rust/Python) uses snake_case + explicit mapping.

Everything hangs off that:

- JSON Schemas: legalName, legalNameNormalized, statusEffectiveDate
- JSON instances: same as schema
- Rust / Python names: legal_name, legal_name_normalized, status_effective_date

Rust bridges via #[serde(rename_all = "camelCase")] (or explicit rename), Python passes dicts whose keys are camelCase while variables stay snake_case.

## Rules by Layer

JSON Schema and JSON records

Required:

- Property names: camelCase
  - legalName, legalNameNormalized, statusEffectiveDate, firstSeenAt
- Enum values:
- Use SCREAMING_SNAKE_CASE where they represent codes (e.g. ACTIVE, INACTIVE).
- $defs object keys: lowerCamelCase.
- No snake_case in public JSON unless it is an external standard we are mirroring (document any exceptions).

## Rust

For types that serialize to JSON:

- Struct names: PascalCase: EntityRecord, StatusEnvelope, CanonicalTimestamp.
- Field names: snake_case and always decorated with serde to map to camelCase
- Enum names: PascalCase; variants: PascalCase; #[serde(rename_all = "SCREAMING_SNAKE_CASE")] when they are code-ish
- Internal-only types that never serialize to JSON can be pure Rust style without serde.

## Python

- Module / function / variable names: snake_case.
- Dataclasses: snake_case attributes, but any dict intended to go over the wire must use camelCase keys matching the schema, even though Python variables are snake_case, e.g.jurisdiction_iso.

```python
normalized_payload: dict[str, Any] = {
    "jurisdictionIso": raw.jurisdiction_iso,
    "legalName": raw.legal_name,
    "legalNameNormalized": normalized_name,
    "snfei": snfei,
    "entityType": "school_district",
}
```

## Rules

- Do not hand-edit generated.rs.
- If a JSON-facing type is not in generated.rs, it must still use #[serde(rename_all = "camelCase")].
- Ruff/pyright don't know about casing in dict keys, so centralize constants:

```python
LEGAL_NAME = "legalName"
LEGAL_NAME_NORMALIZED = "legalNameNormalized"
JURISDICTION_ISO = "jurisdictionIso"
ENTITY_TYPE = "entityType"

normalized_payload = {
    JURISDICTION_ISO: raw.jurisdiction_iso,
    LEGAL_NAME: raw.legal_name,
    LEGAL_NAME_NORMALIZED: normalized_name,
    "snfei": snfei,
    ENTITY_TYPE: "school_district",
}
```