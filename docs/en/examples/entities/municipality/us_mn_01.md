# Example: Municipality Entity (US-MN 01)

This example demonstrates a basic CEP EntityRecord for a municipality in Minnesota.  
It follows the standard four-stage CEP example pipeline described in  
[**How CEP Examples Work**](../../README.md).

Directory:

```text
examples/entity/municipality/us_mn_01/
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

This example illustrates Minnesota-specific details:

- Shows a *minimal viable municipality* using SNFEI as the identifier input.
- Demonstrates normalization of a Minnesota municipal name.
- Applies the standard `municipality` entityTypeUri.
- Contains a single revision with no prior history.
- Follows the canonical CEP entity pipeline with no special adapter rules.

See the master documentation for details of normalization, canonicalization, SNFEI construction, and the Rust builder:  
[How CEP Examples Work](../../README.md).

---

## Pipeline Notes (Specific to This Example)

### Normalization (02)

The adapter extracts common core fields:

- `jurisdictionIso: "US-MN"`
- `legalName`
- `legalNameNormalized`
- `entityType: municipality`
- SNFEI preimage components

Minnesota municipalities typically have clean name formatting, so no special tokenization or alias handling was required.

### Canonicalization (03)

The canonical form contains:

- normalized name  
- Minnesota jurisdiction code  
- entity type  
- deterministically ordered fields  

The input canonicalizes without additional preprocessing.

### Verifiable ID (SNFEI)

SNFEI is calculated as:

```text
SHA256( canonical.to_hash_string() )
```

This value:

- populates the `verifiableId`, and  
- appears in the `identifiers[]` array using the SNFEI identifier scheme.

### Final EntityRecord (04)

The Rust builder (`build_entity_json`) produces:

- a complete CEP EntityRecord  
- default `status` and `statusEffectiveDate`  
- revision metadata (`revisionNumber`, `recordHash`)  
- a cryptographic attestation  
- canonical URIs for identifier scheme and entity type  

---

## Regenerating This Example

From the repository root:

```bash
uv run cx generate-example --path examples/entity/municipality/us_mn_01/
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

- [`01_raw_source.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/municipality/us_mn_01/01_raw_source.json)
- [`02_normalized.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/municipality/us_mn_01/02_normalized.json)
- [`03_canonical.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/municipality/us_mn_01/03_canonical.json)
- [`04_entity_record.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/municipality/us_mn_01/04_entity_record.json)
