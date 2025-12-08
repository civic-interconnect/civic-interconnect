# Quick Start

The **Civic Exchange Protocol (CEP)** is an open, standards-driven framework for creating verifiable civic records with canonical identities, provenance, and interoperability across jurisdictions.

This guide shows how to:

1. Install CEP tools  
2. Validate schemas  
3. Generate example records  
4. Build entities programmatically  

---

## 1. Install the CEP Toolkit

You can install the CLI and Python API from PyPI:

```
uv pip install civic-interconnect
```

Or add to an existing environment:

```
pip install civic-interconnect
```

Confirm installation:

```
cx --help
```

---

## 2. Validate a CEP Record

CEP ships with a JSON Schema validator:

```
cx validate path/to/my-entity.json
```

You may validate any record family:

```
cx validate --schema entity path/to/my-entity.json
cx validate --schema relationship path/to/my-relationship.json
cx validate --schema exchange path/to/my-exchange.json
```

Successful validation confirms:

- Schema compliance  
- Vocabulary references  
- Canonical field types  
- Envelope integrity  

---

## 3. Generate Example Data

The CLI can generate examples for any directory under `examples/`:

```
cx generate-example examples/entity --overwrite
```

This produces three files per slice:

- **01_raw_source.json** – raw adapter input  
- **02_normalized.json** – normalized fields  
- **03_canonical.json** – canonical hash inputs  
- **04_entity_record.json** – final CEP EntityRecord  

This is the best way to understand the transformation pipeline.

---

## 4. Build an Entity Using Python

You can construct SNFEI values and full EntityRecords programmatically.

```python
from civic_interconnect.cep.snfei import compute_snfei
from civic_interconnect.cep.entity import build_entity_from_raw

raw = {
    "jurisdictionIso": "US-MN",
    "legalName": "City of Springfield",
    "legalNameNormalized": "city springfield",
    "snfei": compute_snfei("city springfield", "US-MN"),
    "entityType": "municipality",
}

entity = build_entity_from_raw(raw)
print(entity["verifiableId"])
```

If Rust bindings are installed, CEP uses them automatically; otherwise, it falls back to the pure-Python implementation.

---

## 5. Next Steps

- Learn how SNFEI canonical identities work at `/en/reference/snfei.md`
- Understand normalization at `/en/concepts/normalization.md`
- Explore record envelopes and provenance at `/en/implementation/record-envelopes.md`
- Explore schemas at `/en/schemas.md`

CEP aims to make civic data **verifiable**, **interoperable**, and **future-proof** with minimal integration overhead.

Welcome to the network of connected civic data!
