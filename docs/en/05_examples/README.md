# CEP Examples: How to Read and Reproduce Them

The CEP repository includes many example records demonstrating the complete entity and relationship pipeline.  
This page describes **how all examples are structured**, what each file represents, and how the Rust + Python toolchain produces the final attested CEP record.

Each specific example page (e.g., a municipality, nonprofit, PAC, or contractor) includes only the details unique to that case.  
**This file is the canonical reference for the example pipeline.**

---

# Directory Structure of an Example

Every example follows the same four-stage layout:

```text
01_raw_source.json    = raw input from an upstream system
02_normalized.json    = adapter-normalized form (NormalizedEntityInput)
03_canonical.json     = canonicalized form (Normalizing Functor)
04_entity_record.json = final EntityRecord from the Rust builder
```

For relationship or exchange examples, the fourth file will be a `RelationshipRecord` or `ExchangeRecord`, but the pipeline stages remain the same.

---

# Stage 1 — Raw Source → Normalized Input

The adapter reads `01_raw_source.json` and produces `02_normalized.json`.

Normalization ensures:

- consistent Unicode handling  
- consistent whitespace and punctuation cleanup  
- deterministic field names  
- structured jurisdiction and entity-type fields  
- extraction of identifier inputs (e.g., SNFEI, SAM.gov, state vendor IDs)

Normalization is implemented in Python using shared utilities from `cep_py`.

---

# Stage 2 — Normalized Input → Canonical Input

The canonicalization stage applies the **normalizing functor** implemented in Rust (`cep_core`) and exposed through Python.

Canonicalization:

- orders fields deterministically  
- converts complex structures into canonical hash-preimage form  
- produces a stable `to_hash_string()` representation

Any two semantically identical civic records must canonicalize to the same string.

---

# Stage 3 — Canonical Input → Verifiable ID

From the canonical string, the Rust core computes the **Verifiable ID**.

For entities, this may use:

- SNFEI (SHA-256 based)  
- OR a multi-identifier universal construction  
- OR a future identifier system  

The Verifiable ID serves as the stable identity of the entity across all revisions.

If the example includes additional identifiers, they are incorporated into the `identifiers[]` block.

---

# Stage 4 — Build the Final Record (Rust Builder)

In the final stage, Python calls into the Rust `cep_core` builder:

```python
from cep_py import build_entity_json
record = build_entity_json(normalized_input)
```

The builder:

1. Confirms or computes the Verifiable ID  
2. Creates or extends the non-destructive **revision chain**  
3. Computes `recordHash` and `previousRecordHash`  
4. Fills required envelope fields (status, timestamps, jurisdiction, type)  
5. Generates a **cryptographic attestation** using the configured keys

This produces `04_entity_record.json`.

If a prior revision exists, a new one is added without overwriting history.

---

# How CEP Invariants Appear in Examples

All examples share these foundational guarantees:

### **Verifiable ID as a Universal Construction**
Identity is derived canonically and remains stable across revisions.

### **Non-Destructive Revision Chain**
Every new build creates a new revision linked by `previousRecordHash`.

### **Immutable Provenance**
Hashes guarantee that revision history cannot be altered without detection.

### **Cryptographic Attestation**
Records are attested using independent keys; verification does not depend on trusting any hosting service.

### **Distributed Verification (implicit)**
Examples can be validated locally, offline, or in distributed environments.

---

# Regenerating Any Example

From the repository root:

```bash
uv run cx generate-example --path examples/.../<example-folder>/
```

Or run manually:

```python
from cep_py import (
    normalize_entity_input,
    canonicalize_entity_input,
    compute_verifiable_id,
    build_entity_json,
)
```

(Examples may use `compute_snfei` or other identifier constructors depending on the schema version.)

---

# Template for Example-Specific Pages

Each example page should include:

```markdown
# Example: <Name>

**Purpose:** (What this example highlights — unique bits only)

**Files:**
- 01_raw_source.json
- 02_normalized.json
- 03_canonical.json
- 04_entity_record.json

**Highlights:**
- Unique identifiers
- Special normalization rules
- Unusual entityType or jurisdiction
- Notes on revision history (if multiple revisions)

**Link back to this page:**
See [How CEP Examples Work](../README.md) for the full pipeline description.
```

This keeps example pages small and consistent.

---

# Where to Find Example Definitions

Examples live under:

```
examples/
    entity/
    relationship/
    exchange/
```

Each example folder includes its own markdown page and the four pipeline files.

---

This page is the authoritative description of how CEP examples work.  
All example pages link back here for more complete information.
