# Civic Interconnect Schemas

These schemas are the source of truth for CEP:

{% include-markdown "../../schemas/README.md" %}

## CEP Schemas

| Schema | Description |
|--------|-------------|
| [cep.entity.schema.json](https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/schemas/cep.entity.schema.json) | Entity records |
| [cep.entity.identifier-scheme.schema.json](https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/schemas/cep.entity.identifier-scheme.schema.json) | Identifier scheme metadata |
| [cep.relationship.schema.json](https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/schemas/cep.relationship.schema.json) | Relationship records |
| [cep.exchange.schema.json](https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/schemas/cep.exchange.schema.json) | Exchange records |
| [cep.record-envelope.schema.json](https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/schemas/cep.record-envelope.schema.json) | Core envelope shared by all record families |
| [cep.vocabulary.schema.json](https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/schemas/cep.vocabulary.schema.json) | Vocabulary definition meta-schema |
| [cep.ctag.schema.json](https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/schemas/cep.ctag.schema.json) | Per-post tagging model |
| [README.md](https://github.com/civic-interconnect/civic-interconnect/blob/main/schemas/README.md) | Schema overview and documentation |

## Schema and Vocabulary Versions

Schemas are expected to change less often than vocabularies and the versioning is handled differently.

- Schema URIs are found from the file names `schemas/cep.entity.schema.json`, etc. Schemas are unversioned at the path, and the `schemaVersion` field provides the version.

- Vocabulary URIs are found in `vocabularies/<name>.v1.0.0.json#<code>`.
