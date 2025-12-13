# Civic Interconnect

[![PyPI](https://img.shields.io/pypi/v/civic-interconnect.svg)](https://pypi.org/project/civic-interconnect/)
[![Python versions](https://img.shields.io/pypi/pyversions/civic-interconnect.svg)](https://pypi.org/project/civic-interconnect/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![CI Status](https://github.com/civic-interconnect/civic-interconnect/actions/workflows/ci-python.yml/badge.svg)](https://github.com/civic-interconnect/civic-interconnect/actions/workflows/ci-python.yml)
[![Docs](https://img.shields.io/badge/docs-mkdocs--material-blue)](https://civic-interconnect.github.io/civic-interconnect/)
[![Security Policy](https://img.shields.io/badge/security-policy-orange)](SECURITY.md)
[![Link Check](https://github.com/civic-interconnect/civic-interconnect/actions/workflows/weekly_link_checker.yml/badge.svg)](https://github.com/civic-interconnect/civic-interconnect/actions/workflows/weekly_link_checker.yml)

> Interoperable data standards for describing entities, relationships, and value exchanges across civic systems.

Civic Interconnect is a shared schema, vocabulary, and implementation platform for interoperable civic data.
It includes the Civic Exchange Protocol (CEP), which defines a set of reusable record types (Entity, Relationship, Exchange, and Context Tag), plus domain modules and adapters that connect existing public data standards and systems.

This repository is a monorepo that contains:

-   JSON Schemas and vocabularies that define Civic Interconnect records
-   A Rust core library that implements builders, validators, and shared logic
-   Python bindings and packages for working with Civic Interconnect in data workflows
-   Tools for generating code from schemas (code that writes code)
-   Documentation including a browser-embedded validator using Ajv

## Overview

The Civic Exchange Protocol defines a coherent, verifiable way to describe:

-   **Entities** (organizations, agencies, districts, people)
-   **Relationships** (grant awards, contracts, reporting relationships)
-   **Exchanges** of value (payments, disbursements, transfers)

CEP records are:

-   JSON Schema–validated
-   Fully typed
-   Deterministic and versioned
-   Extensible across jurisdictions and data ecosystems
-   Designed for cross-system interoperability

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

Civic Interconnect is built around three primary record families:

-   **Entity**: Describes people, organizations, districts, facilities, and other civic actors or units.
-   **Relationship**: Describes how entities are connected (affiliation, control, governance, containment, membership, etc.).
-   **Exchange**: Describes flows between entities (funds, services, messages, events).

All record families share a common envelope that owns IDs, attestation, status, and revisioning:

-   stable `verifiableId`
-   `recordKind` and vocabulary-backed `recordTypeUri`
-   `schemaVersion` and `revisionNumber`
-   shared timestamps (`firstSeenAt`, `lastUpdatedAt`, `validFrom`, `validTo`)
-   attestations describing who asserted the facts and how
-   optional **ctags** (contextual annotations)

Schema annotations (`x-cep-*`) indicate vocabulary-backed fields, ID references, money types, jurisdiction fields, and extension surfaces.

## Repository Layout

```text
schemas/          # JSON Schemas (source of truth)
vocabulary/       # Controlled vocabularies
tools/            # Codegen and helper tools
crates/           # Rust crates (core logic and bindings)
src/python/       # Python packages (ci-cep, ci-ctag, adapters)
```

## Schemas

Official schemas live under **/schemas** and are published with stable URLs such as:

```text
https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/schemas/core/cep.entity.schema.json
```

Documentation includes a browser-embedded validator using Ajv.

Schemas are used to:

-   generate Rust types
-   generate Python models
-   validate data
-   anchor long-term stability and cross-system interoperability

## Rust Core

The Rust core is organized by domain:

-   entity/
-   relationship/
-   exchange/
-   ctag/

Each has generated types plus manual logic for rules, normalization, resolution, and ID creation (SNFEI).

## CEP Data Pipeline

This pipeline outlines the definitive steps data takes from its raw source to a validated, final CEP record.
The **Builder** stage is the critical FFI boundary where control is passed from Python to Rust.

The diagram illustrates the path data takes, highlighting the FFI boundary between the Python facade and the Rust core.

```text
raw -> adapter -> localization -> normalized payload ->
builder (Python facade -> Rust FFI) -> validator -> CEP record
```

### Python Adapter (Pre-Processing)

Prepares raw source data by:

-   cleaning and mapping source fields
-   applying localization rules
-   producing a minimal **normalized payload** |

### Rust Builder (FFI Boundary)

Rust performs:

-   canonical normalization (legal name, address, registration date)
-   SNFEI generation
-   record assembly using generated types
-   schema validation

The result is returned as a **validated CEP dict**.

## Status

Active early development.  
APIs, schemas, and vocabularies are stabilizing.

## Security Policy

We support responsible disclosure through GitHub's **Private Vulnerability Report** feature.

See: [SECURITY.md](SECURITY.md)

## Contributions

Contributions are welcome once the early structure is stable.

See `CONTRIBUTING.md`.

## License

Licensed under the Apache License, Version 2.0.

See the [`LICENSE`](./LICENSE) file for full text.
