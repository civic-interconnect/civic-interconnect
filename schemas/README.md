# Schemas

This directory contains the machine-readable specifications for the Civic Exchange Protocol (CEP).  
Schemas define the structural rules, validation contracts, controlled vocabularies, and governance models used across CEP implementations.

---

## Directory Structure

```
schemas/
  README.md
  core/
  vocabulary/
  domains/
  governance/
```

Each subdirectory serves a distinct role within the specification:

### `core/`
Defines the foundational schema components shared across all domains, including entities, relationships, exchanges, record envelopes, identifier schemes, and content tags.  
These schemas establish the canonical structural model that all CEP records build upon.

### `vocabulary/`
Contains the vocabulary meta-schema along with versioned controlled vocabularies.  
Vocabularies provide stable identifiers and terms for classifications, codes, and relationship types.  
Schemas and data instances may reference vocabulary URIs rather than embedding codes directly.

### `domains/`
Holds domain-specific schemas such as campaign finance, education, environment, procurement, and others.  
Domain schemas extend the core model and define structures unique to particular civic contexts.

### `governance/`
Includes schemas that describe how CEP itself is validated, encoded, and traced.  
This includes canonical graph encoding, fingerprinting, provenance, versioning rules, and related governance structures.

---

## File Naming Conventions

Schema filenames follow a consistent pattern:

```
<schema-name>.schema.json
```

Where:

- `<schema-name>` is a descriptive, lowercase, kebab-case identifier  
- `.schema.json` indicates a JSON Schema document  
- Versioning is governed by the `$id` field rather than the filename  

Examples:

- `cep.entity.schema.json`  
- `cep.relationship.schema.json`  
- `contribution.schema.json` (domain example)  
- `cep.record-envelope.schema.json`  
- `cep.graph.schema.json`

Filenames describe **what** the schema is.  
The directory path describes **where** the schema belongs within CEP's structure.  
These concerns remain independent so that schemas may relocate without requiring filename changes.

---

## `$id` and `$ref` Conventions

Each schema defines a unique `$id` that corresponds to its public URI, typically served from GitHub Raw URLs.  
Schemas reference one another using relative `$ref` paths that match the directory layout shown above.

This organization ensures that:

- References resolve deterministically  
- Validators can locate dependencies without custom configuration  
- Implementations can mirror or vend schemas in different hosting environments  

---

## Hosting and Resolution

Tools may load schemas directly via their `$id` URIs or from a local checkout of this directory.  
The directory structure is arranged so that relative references remain valid regardless of where the schemas are hosted or embedded.

---

This README describes the organization and conventions of the CEP schema tree.  
Individual schemas provide further detail on the structures and rules they define.
