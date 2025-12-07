# Nonprofit Example - US MA 01

This directory provides a **vertical slice** of the CEP Entity pipeline:

```
01_raw_source.json        = original source record
02_normalized.json        = adapter-normalized form
03_canonical.json         = fully normalized canonical form
04_entity_record.json     = final CEP EntityRecord (Rust builder output)
```

## 1. Raw Source (`01_raw_source.json`)

The raw input is what an ETL adapter would receive from a state, federal, or third-party system.  
No assumptions are made about casing, naming, or data quality.

## 2. Normalized Input (`02_normalized.json`)

Adapters transform the raw input into the **NormalizedEntityInput** shape:

```json
{
    "jurisdictionIso": "...",
    "legalName": "...",
    "legalNameNormalized": "...",
    "snfei": "...",
    "entityType": "..."
}
```

This step is domain-specific and may include local business rules.

## 3. Canonical Input (`03_canonical.json`)

The canonical input is produced by the **Normalizing Functor**, ensuring:

-   whitespace normalization
-   Unicode stability
-   deterministic hashing input
-   consistent international treatment

This file is used for SNFEI computation.

## 4. Final CEP Record (`04_entity_record.json`)

This is the full **EntityRecord** produced by:

```
build_entity_json(normalized_json)
```

It includes:

-   envelope metadata
-   timestamps
-   attestation block
-   SNFEI-based `verifiableId`
-   identifier array (SNFEI termUri)
-   domain attributes

## How to Regenerate

From repo root:

```bash
uv run cx generate-example --path examples/entity/nonprofit/us_ma_01
```

(or run manual normalization + Rust builder steps)

---

For questions about the fields or process, see:

-   [`docs/en/reference/identifier-schemes.md`](../../../../docs/en/reference/identifier-schemes.md)
-   [`docs/en/reference/entity.md`](../../../../docs/en/reference/entity.md)
-   [`docs/en/concepts/normalization.md`](../../../../docs/en/concepts/normalization.md)
