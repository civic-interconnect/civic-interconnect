# Public Procurement Domain

The public procurement domain models buyers, suppliers, procedures, awards, and
contracts in a way that is compatible with the Civic Exchange Protocol (CEP).

This domain is intended to serve as a bridge between:

- heterogeneous procurement sources (e.g., OCDS releases, EU TED notices,
  local tender portals),
- CEP core entities and relationships,
- and cross-domain identity resolution for suppliers and buyers.

## Scope

The initial scope covers:

- **Buyers** (procuring entities)
- **Suppliers** (economic operators)
- **Procedures** (tenders / competitive processes)
- **Awards** (award decisions)
- **Contracts** (signed agreements)

These are defined via:

- domain vocabularies under `vocabulary/procurement/`
- domain schemas under `schemas/domains/procurement/`

## Relationship to CEP Core

Domain records are produced by source-specific adapters and then mapped into
CEP core entity and relationship envelopes. The public procurement domain
exercises:

- canonicalization of legal names and identifiers,
- entity fingerprinting for buyers and suppliers,
- graph construction and normalization for procedures → awards → contracts,
- cross-domain identity resolution (CDIRA) for suppliers and buyers that appear
  across multiple systems.

Future work will add:

- concrete adapters (e.g., OCDS, EU TED),
- example pipelines,
- and reference graphs annotated with CTags and provenance.
