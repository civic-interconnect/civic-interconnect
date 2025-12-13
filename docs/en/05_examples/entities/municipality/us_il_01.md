# Example: Municipality Entity (US-IL 01)

This example demonstrates a basic CEP EntityRecord for a municipality in Illinois.  
It uses the standard four-stage CEP example pipeline described in  
[**How CEP Examples Work**](../../README.md).

Directory:

```text
examples/entity/municipality/us_il_01/
```

Files:

```text
01_raw_source.json
02_normalized.json
03_canonical.json
04_entity_record.json
```

---

## Highlights of This Example

**What is unique about this particular example:**

- Demonstrates a *minimal viable municipality* record.
- Uses **SNFEI** as the sole identifier input for constructing the `verifiableId`.
- Shows normalization of a plain-text municipal name into a canonical form.
- Displays the default entity type mapping for municipalities.
- Includes a single revision (no prior history).

For all pipeline details (normalization → canonicalization → identifier construction → record building),  
see the master page:  
[How CEP Examples Work](../../README.md).

---

## Pipeline Notes (Specific to This Example)

### Normalization (02)

The adapter extracts:

- `jurisdictionIso: "US-IL"`
- `legalName` and `legalNameNormalized`
- `entityType: municipality`
- SNFEI preimage fields (used to generate the hash)

Nothing unusual is required for this example — Illinois municipalities follow the default normalization pattern.

### Canonicalization (03)

The canonical representation includes:

- normalized name  
- jurisdiction code  
- entity type  
- deterministic field ordering  

This example canonicalizes cleanly with no special transformations.

### Verifiable ID (SNFEI)

SNFEI is computed via:

```
SHA256( canonical.to_hash_string() )
```

The resulting value populates:

- `verifiableId = "cep-entity:snfei:<hash>"`
- an entry in `identifiers[]` using the SNFEI identifier scheme.

*(Example SNFEI value is shown inside the final record.)*

### Final EntityRecord (04)

The Rust builder (`build_entity_json`) produces:

- envelope metadata (status, timestamps)  
- `recordHash` and `previousRecordHash` (none for first revision)  
- cryptographic attestation  
- canonical `entityTypeUri` and identifier scheme references  

---

## Regenerating This Example

From the repo root:

```bash
uv run cx generate-example --path examples/entity/municipality/us_il_01/
```

Or run the steps manually:

```python
from cep_py import build_entity_json

entity_record = build_entity_json(normalized_json)
```

---

## Related Documentation

- [Identifier Schemes](../../../reference/identifier-schemes.md)  
- [Entity Specification](../../../reference/entity.md)  
- [Normalization & SNFEI](../../../concepts/normalization.md)

---

## Example Files

- [`01_raw_source.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/municipality/us_il_01/01_raw_source.json)
- [`02_normalized.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/municipality/us_il_01/02_normalized.json)
- [`03_canonical.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/municipality/us_il_01/03_canonical.json)
- [`04_entity_record.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/municipality/us_il_01/04_entity_record.json)
