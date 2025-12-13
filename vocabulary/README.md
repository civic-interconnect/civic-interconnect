# Vocabularies

This directory contains the controlled vocabularies used by the Civic Exchange Protocol (CEP).  
Vocabularies provide stable identifiers and terms for classifications, codes, types, roles, and other enumerated concepts referenced by CEP schemas and data.

Vocabularies are defined as versioned JSON documents and evolve independently of the schemas that reference them.

---

## Directory Structure

```
vocabulary/
  README.md
  core/
  common/
  intl/
  domains/
```

Each subdirectory serves a distinct purpose within CEP's vocabulary system.

### `core/`
Contains vocabularies intrinsic to CEP itself.  
These vocabularies define concepts that are structural to CEP's data model, such as:

- entity types  
- relationship types  
- exchange types  
- identifier schemes  
- content tag types  
- exchange roles  

These vocabularies are broadly applicable and change conservatively.

### `common/`
Holds cross-cutting vocabularies that may be used freely across multiple domains.  
These vocabularies are not structural to CEP, but are widely useful in practice—examples include:

- party or actor roles  
- resolution or confidence methods  
- source or system identifiers  
- value or measurement types  

These vocabularies can be referenced by any domain or implementation without requiring domain-specific interpretation.

### `intl/`
Provides vocabularies related to international or jurisdictional standards.  
Typical categories include:

- currency codes  
- languages  
- jurisdictions and subnational regions  
- legal entity classifications  
- mappings to external standards (ISO, UN, OECD, national registries)

This directory acts as a bridge between CEP vocabularies and external code systems.

### `domains/`
Contains vocabularies that are defined and curated within individual subject-matter domains:

```
domains/
  campaign-finance/
  procurement/
  education/
  environment/
  ...
```

Domain vocabularies capture concepts that are specific to a policy area or regulatory context.  
They may evolve more rapidly and do not need to align with other domains unless explicitly mapped.

---

## File Naming Convention

Vocabulary files follow a consistent naming pattern:

```
<resource-name>.v<semver>.json
```

Where:

- `<resource-name>` is a descriptive, lowercase, kebab-case identifier  
- `<semver>` is a semantic version number (`MAJOR.MINOR.PATCH`)  
- `.json` is the file format  

Examples:

- `entity-type.v1.0.0.json`  
- `relationship-type.v1.0.0.json`  
- `party-role.v1.0.0.json`  
- `resolution-method.v1.0.0.json`  
- `currency.v1.0.0.json`  
- `filing-type.v1.0.0.json` (domain example)

The file name describes **what** the vocabulary is.  
The directory path describes **where** it belongs in the CEP ecosystem.  
These two concerns remain independent.

---

## Versioning

Vocabulary versions are explicit in the filename.  
New versions may be added without removing or altering earlier versions.  
Schemas and data instances may reference any version appropriate to their use case.

Implementations may support:

- a fixed vocabulary version,  
- multiple versions concurrently, or  
- version negotiation, depending on their requirements.

---

## Referencing Vocabularies

Vocabulary files define canonical URIs used as `$id` values.  
Schemas and data instances refer to vocabularies by these URIs.

Implementations may load vocabulary files from:

- their published URI (e.g., Git-based raw URLs),  
- a local copy of this directory, or  
- any mirrored location that preserves the same identifiers.

Relative `$ref` paths are organized to follow the directory structure described above.

---

## Purpose

This directory organizes all controlled vocabularies used within CEP.  
Its structure supports clarity, reuse, internationalization, and domain-specific flexibility while maintaining stable, versioned identifiers for long-term interoperability.
