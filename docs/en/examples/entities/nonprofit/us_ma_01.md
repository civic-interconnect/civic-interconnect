# Example: Nonprofit Entity (US-MA 01)

This example demonstrates a CEP EntityRecord for a nonprofit organization based in Massachusetts.  
It uses the standard four-stage CEP example pipeline described in  
[**How CEP Examples Work**](../../README.md).

Directory:

```text
examples/entity/nonprofit/us_ma_01/
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

This example illustrates nonprofit-specific details:

- Shows CEP’s handling of **nonprofit legal names** and their normalized variants.
- Demonstrates how a nonprofit’s identifier inputs feed into SNFEI-based identity.
- Applies the nonprofit `entityTypeUri`.
- Contains a simple first-revision record with no amendment history.
- Displays how minimal upstream data can still produce a valid, attested CEP EntityRecord.

For a full explanation of each pipeline stage, see  
[How CEP Examples Work](../../README.md).

---

## Pipeline Notes (Specific to This Example)

### Normalization (02)

The adapter extracts and standardizes:

- `jurisdictionIso: "US-MA"`
- `legalName`  
- `legalNameNormalized`  
- `entityType: nonprofit`
- SNFEI preimage inputs

Massachusetts nonprofit names often include punctuation, abbreviations (e.g., “Inc.”), or suffixes; the normalizer removes or reduces these deterministically.

### Canonicalization (03)

The canonical form includes:

- normalized legal name  
- Massachusetts jurisdiction code  
- nonprofit entity type  
- deterministically ordered fields  

This example requires no special locale-specific adjustments.

### Verifiable ID (SNFEI)

SNFEI is calculated via:

```text
SHA256( canonical.to_hash_string() )
```

The value is used:

- as the basis of `verifiableId`, and  
- as an entry in `identifiers[]` using the SNFEI identifier scheme.

### Final EntityRecord (04)

The Rust builder (`build_entity_json`) constructs:

- the canonical EntityRecord  
- `status` and `statusEffectiveDate`
- `recordHash` and the first-revision `revisionNumber`  
- a cryptographic attestation  
- structured URI references for entity type and identifier scheme  

---

## Regenerating This Example

From the repository root:

```bash
uv run cx generate-example --path examples/entity/nonprofit/us_ma_01/
```

Or manually:

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

- [`01_raw_source.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/nonprofit/us_ma_01/01_raw_source.json)  
- [`02_normalized.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/nonprofit/us_ma_01/02_normalized.json)  
- [`03_canonical.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/nonprofit/us_ma_01/03_canonical.json)  
- [`04_entity_record.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/nonprofit/us_ma_01/04_entity_record.json)
