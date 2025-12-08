# Example: PAC Entity (pac_01)

This example demonstrates a CEP EntityRecord for a Political Action Committee (PAC).  
It follows the standard four-stage CEP example pipeline described in  
[**How CEP Examples Work**](../../README.md).

Directory:

```text
examples/entity/pac/pac_01/
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

This example demonstrates PAC-specific characteristics:

- Shows normalization of PAC names, which often include financial or campaign-specific suffixes.
- Illustrates how identifier inputs (e.g., state or federal PAC IDs) contribute to the SNFEI preimage.
- Applies the `pac` `entityTypeUri`.
- Demonstrates that even highly varied upstream PAC filings normalize into a stable canonical representation.
- Contains a first-revision EntityRecord with no amendment history.

For a complete explanation of each pipeline stage, see  
[How CEP Examples Work](../../README.md).

---

## Pipeline Notes (Specific to This Example)

### Normalization (02)

The adapter extracts:

- `jurisdictionIso`
- `legalName`
- `legalNameNormalized`
- `entityType: pac`
- SNFEI preimage components (sometimes including federal or state PAC identifiers)

PAC names often contain uppercase acronyms, campaign references, and punctuation; the normalizer handles these deterministically.

### Canonicalization (03)

The canonical form includes:

- normalized PAC name  
- jurisdiction code  
- entity type  
- deterministically ordered fields  

PACs sometimes have complex or lengthy names, but canonicalization treats them uniformly.

### Verifiable ID (SNFEI)

SNFEI is computed via:

```text
SHA256( canonical.to_hash_string() )
```

The resulting SNFEI:

- forms the `verifiableId`, and  
- appears in the `identifiers[]` array under the SNFEI identifier scheme.

### Final EntityRecord (04)

The Rust builder (`build_entity_json`) produces:

- the complete EntityRecord  
- default `status` and `statusEffectiveDate`
- revision metadata (`revisionNumber`, `recordHash`)
- a cryptographic attestation
- canonical URIs for PAC entity type and SNFEI identifier scheme  

---

## Regenerating This Example

From the repository root:

```bash
uv run cx generate-example --path examples/entity/pac/pac_01/
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

- [`01_raw_source.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/pac/pac_01/01_raw_source.json)  
- [`02_normalized.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/pac/pac_01/02_normalized.json)  
- [`03_canonical.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/pac/pac_01/03_canonical.json)  
- [`04_entity_record.json`](https://github.com/civic-interconnect/civic-interconnect/blob/main/examples/entity/pac/pac_01/04_entity_record.json)
