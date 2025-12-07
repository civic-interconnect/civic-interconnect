# CEP Entity Example: Nonprofit (us_ma_01)

This page provides a documentation view of the example located at:

```
examples/entity/nonprofit/us_ma_01/
```

That directory contains a **vertical slice** of the CEP Entity pipeline:

```
01_raw_source.json   = raw input from the upstream system
02_normalized.json   = adapter-normalized form (NormalizedEntityInput)
03_canonical.json    = canonicalized input (Normalizing Functor)
04_entity_record.json= final EntityRecord produced by the Rust builder
```

---

## What This Example Shows

This example illustrates:

- How the **Normalizing Functor** transforms inconsistent source data  
- How the **SNFEI** is computed and used as the entity’s `verifiableId`
- How the **Identifier Scheme Vocabulary** applies (`schemeUri` → SNFEI term)
- How the **EntityRecord envelope** (status, timestamps, attestation) is produced
- How minimal but valid inputs produce a fully structured CEP record

---

## Pipeline Summary

### 1. Raw Source → Normalized Input  
The adapter extracts:

- `jurisdictionIso`
- `legalName`
- `legalNameNormalized`
- `entityType`
- `snfei` (via Rust SNFEI generator)

### 2. Normalized Input → Canonical Input  
The Canonical Input stage applies:

- Unicode normalization  
- whitespace & punctuation cleanup  
- deterministic hashing-preimage formation

### 3. Canonical Input → SNFEI  
SNFEI is computed as:

```
SNFEI = SHA256( canonical.to_hash_string() )
```

### 4. SNFEI + Normalized Input → EntityRecord  
Using:

```
cep_py.build_entity_json(normalized_json)
```

The resulting EntityRecord includes:

- `verifiableId = "cep-entity:snfei:<hash>"`
- `identifiers[]` with the official SNFEI `schemeUri`
- Envelope metadata (status, timestamps, attestation)
- Domain fields (legalName, jurisdictionIso, entityTypeUri)

---

## Quick Preview

**SNFEI used:**

```
<insert-short-hash>…
```

**Record Type URI:**

```
https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabularies/entity-type.json#<entity-type>
```

**Identifier Scheme:**

```
https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabularies/entity-identifier-scheme.v1.0.0.json#snfei
```

---

## Regenerating This Example

From the repository root:

```bash
uv run cx generate-example --path examples/entity/nonprofit/us_ma_01/
```

Or run each step manually:

1. Normalize the raw source  
2. Canonicalize  
3. Compute SNFEI  
4. Build final entity record via Rust:

```python
from cep_py import build_entity_json
build_entity_json(normalized_json)
```

---

## Related Documentation

- **Identifier Schemes**  
  `docs/en/reference/identifier-schemes.md`

- **Entity Specification**  
  `docs/en/reference/entity.md`

- **Normalization and SNFEI**  
  `docs/en/concepts/normalization.md`

---

## Files for This Example

Links to the files in GitHub:

- [`01_raw_source.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/nonprofit/us_ma_01/01_raw_source.json)
- [`02_normalized.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/nonprofit/us_ma_01/02_normalized.json)
- [`03_canonical.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/nonprofit/us_ma_01/03_canonical.json)
- [`04_entity_record.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/nonprofit/us_ma_01/04_entity_record.json)

