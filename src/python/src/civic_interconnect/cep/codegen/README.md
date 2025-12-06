# Code Generator

This uses Python to read the schema and create the Rust generated.rs files that reflect that shape. 

For example, the code parses the record envelope the same for entity, relationship, and exchange. 

It converts to enums, and merges the properties.

## Shared Record Envelope Types

Shared envelope types:

- RecordKind
- StatusCode
- StatusEnvelope
- Timestamps
- Attestation

## Schema Translation Examples

Example 1

1. Detect the presence of:
```json
"status": {
  "properties": {
    "statusCode": { "enum": [...] }
  }
}
```

1. Emit:

- ExchangeStatusCode enum
- ExchangeStatus struct
- Map exchangeStatus to ExchangeStatus

3. Insert into special_types:

```rust
special_types["exchangeStatus"] = "ExchangeStatus"
special_types["status.statusCode"] = "ExchangeStatusCode"
```

Example 2

We turn URI-style termUri strings into Rust enum variants. 
We get the trailing fragment / slug and provide that.

So:

- `"https://.../value-type.json#monetary"` → `ValueType::Monetary`
- `"https://.../entity-type.json#federal-agency"` → `EntityType::FederalAgency`

## Substructures

| Structure          | Typed?       | Source                 |
| ------------------ | ------------ | ---------------------- |
| StatusEnvelope     | ✅            | Envelope $defs         |
| StatusCode         | ✅            | Envelope $defs         |
| Timestamps         | ✅            | Envelope $defs         |
| Attestation        | ✅            | Envelope $defs         |
| RecordKind         | ✅            | enum from schema       |
| ExchangeStatus     | ✅            | new extraction logic   |
| ExchangeStatusCode | ✅            | new extraction logic   |
| SourceEntity       | ✅            | schema object → struct |
| RecipientEntity    | ✅            | schema object → struct |
| ExchangeValue      | ✅            | schema object → struct |
| ValueType          | ❌ on purpose | Option<String>         |


## Value Type Enums 

Vocab-driven ValueType enums are kept as Option<String> for flexibility.

Enums can, if desired, be provided in manual.rs (rather than generated.rs).