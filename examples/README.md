# Civic Exchange Protocol (CEP) Implementation Examples

This directory provides small, self-contained example files for:

-   **Entity** records
-   **Exchange** (grant/contract) records
-   **Relationship** records
-   **SNFEI test corpus** (canonical inputs and expected hashes)

These examples serve four purposes:

1. **Demonstration** - show what valid CEP records look like.
2. **Testing** - provide cross-language test fixtures for validating canonicalization, normalization, and SNFEI generation.
3. **Validation** - e.g., used to test the CLI command
    ```bash
    uv run cx generate-example examples/entity --overwrite
    ```
4. **Reference Implementation** - ensure all language SDKs generate identical canonical strings and SNFEI hashes.

---

## Directory Layout

```
examples/
  entity/        # Entity-level examples (municipalities, agencies, orgs, etc.)
  exchange/      # Grant, contract, or transaction-type records
  relationship/  # Entity-to-entity relationships
  snfei/         # SNFEI test vectors (raw → canonical → hash)
  README.md
```

Each subfolder contains multiple minimal, schema-valid examples that demonstrate the correct use of:

-   `recordKind`
-   `recordSchemaUri`
-   `entityTypeUri` (for entities)
-   Fully populated `identifiers`, `timestamps`, `attestations`, and `status` blocks

These files should be treated as canonical examples for contributors building new adapters, validators, or SDKs.

---

## SNFEI Test Corpus

The Structured Non-Fungible Entity Identifier (SNFEI) test corpus is structured into three parts:

-   **inputs.jsonl** containing messy real-world inputs
-   **canonical_expected.jsonl** containing the expected canonical strings
-   **snfei_expected.jsonl** containing the calculated final hash output

These can be used by language SDKs to ensure correctness:

```bash
uv run python -m civic_exchange_protocol.snfei test examples/snfei/
cargo test --features snfei
dotnet test
```

---

## How Examples Relate to Adapters

Adapters typically produce four conceptual stages.
Examples in this directory correspond to stage 4, but developers implementing adapters may want to inspect:

1. Raw Input (untyped, messy)
2. Canonical Core (normalized, semantic expansions applied)
3. Identity Projection (minimal canonical JSON used to compute SNFEI)
4. Final CEP Envelope (entity/exchange/relationship)

Only Stage 4 appears in this directory, because examples are required to be _schema-valid CEP artifacts_.

Stages 1–3 appear only in the SNFEI test vectors.

This ensures:

- Adapters produce schema-valid outputs
- Identity rules remain stable
- Canonicalization rules are provably deterministic

---

## Contributing New Examples

When adding examples:

-   Keep them small and narrowly scoped
-   Use realistic civic entities (municipalities, nonprofits, committees, agencies, etc.)
-   Ensure they validate against the appropriate CEP schema
-   Avoid embedding large narrative text or editorial comments
-   Update SNFEI expected hashes if canonicalization rules change
-   Maintain consistent naming (camelCase externally, snake_case in SDKs)
-   Include the full envelope structure (`timestamps`, `status`, `attestations`, etc.)
  
When adding a new domain or adapter, include at least:

- 1-2 entity examples
- 1 exchange example (if applicable)
- 1 relationship example
- A corresponding SNFEI entry in the corpus if identity logic is impacted



---

## License

All examples are licensed under Apache 2.0, consistent with the rest of the project.

