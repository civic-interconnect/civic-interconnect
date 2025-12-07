# Civic Interconnect

[![Python versions](https://img.shields.io/pypi/pyversions/civic-interconnect.svg)](https://pypi.org/project/civic-interconnect/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![CI Status](https://github.com/civic-interconnect/civic-interconnect/actions/workflows/ci-python.yml/badge.svg)](https://github.com/civic-interconnect/civic-interconnect/actions/workflows/ci-python.yml)
[![Docs](https://img.shields.io/badge/docs-mkdocs--material-blue)](https://civic-interconnect.github.io/civic-interconnect/)
[![Security Policy](https://img.shields.io/badge/security-policy-orange)](SECURITY.md)
[![Link Check](https://github.com/civic-interconnect/civic-interconnect/actions/workflows/weekly_link_checker.yml/badge.svg)](https://github.com/civic-interconnect/civic-interconnect/actions/workflows/weekly_link_checker.yml)

> Interoperable data standards for describing entities, relationships, and value exchanges across civic systems.

Civic Interconnect is a shared schema, vocabulary, and implementation platform for interoperable civic data.
It includes the Civic Exchange Protocol (CEP), which defines a set of reusable record types (Entity, Relationship, Exchange, and P3Tag), plus domain modules and adapters that connect existing public data standards and systems.

This repository is a monorepo that contains:

- JSON Schemas and vocabularies that define Civic Interconnect records  
- A Rust core library that implements builders, validators, and shared logic  
- Python bindings and packages for working with Civic Interconnect in data workflows  
- Tools for generating code from schemas (code that writes code)  
- Documentation including a browser-embedded validator using Ajv  

## Overview

The Civic Exchange Protocol defines a coherent, verifiable way to describe:

- **Entities** (organizations, agencies, districts, people)
- **Relationships** (grant awards, contracts, reporting relationships)
- **Exchanges** of value (payments, disbursements, transfers)

CEP records are:

- JSON Schema–validated
- Fully typed
- Deterministic and versioned
- Extensible across jurisdictions and data ecosystems
- Designed for cross-system interoperability

Documentation: <https://civic-interconnect.github.io/civic-interconnect/>

## Quick Start

Install the Civic Interconnect package:

```bash
pip install civic-interconnect
```

Validate a record or directory of records:

```bash
cx validate-json examples/entity --schema entity
```

Canonicalize inputs (SNFEI workflow):

```bash
cx canonicalize examples/snfei/v1.0/01_inputs.jsonl > canonical.jsonl
cx snfei canonical.jsonl > snfei.jsonl
```

Use Civic Interconnect in Python (the civic_interconnect package provides the cep module):

```python
from civic_interconnect.cep import Entity

record = Entity.model_validate_json("""
{
  "legalName": "City of Springfield",
  "entityTypeUri": "https://vocab.civic.org/entity-type/municipality"
}
""")

print(record.verifiableId)
```

See full documentation:

<https://civic-interconnect.github.io/civic-interconnect/>

## Core Concepts

Civic Interconnect is built around four primary record families:

- **Entity**: Describes people, organizations, districts, facilities, and other civic actors or units.
- **Relationship**: Describes how entities are connected (affiliation, control, governance, containment, membership, etc.).  
- **Exchange**: Describes flows between entities (funds, services, messages, events).
- **P3Tag**: Per-post or per-record tags that describe provenance, risk, narratives, or other interpretive signals attached to a subject.  

All four record families share a common envelope that owns IDs, attestation, status, and revisioning:

- A stable `verifiableId`  
- A `recordKind` and `recordTypeUri` rooted in vocabularies  
- Versioning (`schemaVersion`, `revisionNumber`)  
- Shared timestamps (`firstSeenAt`, `lastUpdatedAt`, `validFrom`, `validTo`)  
- Attestations describing who asserted the facts and how  

`x-cep-*` hints in the schemas provide information about:

- vocab-backed fields  
- entity references  
- money fields  
- fractional shares  
- jurisdiction fields  
- extension surfaces  

## Repository Layout

High-level structure:

```text
schemas/          # JSON Schemas (source of truth)
vocabularies/     # Controlled vocabularies
tools/            # Codegen and helper tools
crates/           # Rust crates (core logic and bindings)
src/python/       # Python packages (ci-cep, ci-p3tag, adapters)
```

## Schemas

Official schemas live under **/schemas** and are published with stable URLs such as:

```text
https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/schemas/cep.entity.schema.json
```

Documentation includes a browser-embedded validator using Ajv.

Schemas are used to:
- Generate Rust starting structs from *.schema.json.
- Generate Python dataclasses and pydantic models.
- A basic validation function that enforces required/optional fields, types, and enums.
- Builders that sit on top of generated types.

## Rust Core

The Rust core is organized by domain:

- entity/  
- relationship/  
- exchange/  
- p3tag/  

Each domain has generated code (from schemas) plus manual code for business rules.

## CEP Data Pipeline: Python Adapters to Rust Core

This pipeline outlines the definitive steps data takes from its raw source to a validated, final CEP record.
The **Builder** stage is the critical FFI boundary where control is passed from Python to Rust.

### 1. High-Level Data Flow

The diagram illustrates the path data takes, highlighting the FFI boundary between the Python facade and the Rust core.

```text
raw -> adapter -> localization -> normalized payload ->
builder (Python facade -> Rust cep_py) -> validator -> CEP dict
```

### 2. Python Adapter Responsibilities (Pre-Processing)

The Adapter's job is to clean, map, and localize raw data into a structured intermediate format (normalized payload).
It handles the variable, source-specific data engineering.

| Responsibility | Detail |
| ---------------| -------|
| Data Cleaning  | Knows how to parse and map fields from a specific raw data source (e.g., CSV, database). |
| Localization  | Applies cascading localization rules (e.g., source-specific formatting, standardizing abbreviations) that are pre-requisites for canonicalization.  |
| Structural Ignorance  | Does not know or care about the final CEP record envelope structure (e.g., Attestation, StatusEnvelope).  |
| Output | Produces only the normalized input payload required for the Builder (a clean data structure ready for canonical processing).  | 

### 3. Builder Facade & Rust Core (Canonicalization & Assembly)

The Builder Facade manages the FFI boundary.
The Rust Core executes the final, deterministic logic using its specialized modules (normalizer.rs and resolver.rs) within the single logical builder step.

| Stage | Location | Rust Module | Action Performed |
| --- | --- | --- | --- |
| Facade Call| Python | N/A | Receives the **`normalized payload`** from the Adapter and calls the Rust FFI function. |
| Builder Start | Rust Core | `manual.rs` | Orchestrates the record creation process and prepares the received payload for canonicalization. |
| Canonicalization | Rust Core | `normalizer.rs` | Applies **definitive, canonical rules** (e.g., lowercasing, universal abbreviation removal) to fields contributing to the identifier (Name, Address, Date). |
| ID Resolution | Rust Core | `resolver.rs` | Concatenates the canonical strings and runs the **SHA-256 hash** to generate the **SNFEI/Verifiable ID**. |
| Record Assembly | Rust Core | `manual.rs` | Constructs the full **`EntityRecord`** by combining the SNFEI/ID with the remaining payload data and the **`generated.rs`** envelope types. |
| Validator | Rust Core | N/A (Internal check) | The final assembled record is checked against the JSON Schema for compliance and type fidelity. |
| Output | Rust Core -> Python | N/A | The validated record is serialized to a JSON string (**`CEP dict`**) and returned across the FFI boundary. |

## Status

This project is under active early development.  
APIs, schemas, and package names may change.

## Security Policy

We support responsible disclosure through GitHub's **Private Vulnerability Report** feature.

See: [SECURITY.md](SECURITY.md)

## Contributions

Contributions are welcome once the core structure is in place.  

See `CONTRIBUTING.md` for guidelines.

## License

The Civic Interconnect project (schemas, vocabularies, reference implementations, and tools) is licensed under the Apache License, Version 2.0.

See the [`LICENSE`](./LICENSE) file for full text.
