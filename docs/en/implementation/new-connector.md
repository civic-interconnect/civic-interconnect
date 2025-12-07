# Building a New Connector

All connectors involve:

-   Vocab & schemas
-   Core types / builders
-   Validators
-   Adapters
-   Output, tests

Rust handles:

-   all canonical types,
-   ID rules,
-   validation rules,
-   end-to-end build and validate pipeline.

## Logical Development

1. Define mapping from source → CEP core: How do we get: legalName, jurisdiction, entityType, local IDs, etc.?

2. ID logic: How do we detect "we've seen this entity before"? How do we generate or look up verifiableId?

3. Fact completeness rules: What can be missing at first ingest (e.g., inceptionDate)? When is a record considered "provisional" vs "solid"?

4. Validation: What must be true before we can emit a CEP-compliant entity?

5. Attestation: How do we record "who said this, based on what, and when"?

## Implementation Notes

-   ID must not depend on entity enception date as it is very often not included in the raw data.

## Phase 1: Walk skeleton for entity path

Write a test where an example (e.g. a School District) goes all the way through the process.

Example tasks:

-   Define EntityId, first_seen_date, and minimal Entity struct in core/entity.rs.
-   Implement EntityBuilder with required fields and optional inception_date.
-   Implement simple EntityValidator (e.g., legal_name not empty, jurisdiction present).

Write an end-to-end test:

-   Input JSON with a raw entity name, e.g. US-MN School District x
-   Run through the builder and validator
-   Assert it gets a stable ID, no panic, and inception_date is None.

At the end of Phase 1, a complete vertical slice that works.

## Phase 2: Add Implementation Notes

-   Note implementation details in docs.

## Phase 3: Strengthen reliability

Add more tests:

-   Invalid input (missing legalName)
-   Duplicate entity
-   Updates when new facts arrive (e.g., add inceptionDate later).

Add CI:

-   Run tests on push/PR.

Add a couple of property tests or fuzz tests for deserialization.

## Common Workflow

1. Update the schema in `schemas`.
2. Run `uv run python tools/codegen_rust.py` to regen rust types.
3. Update `build_identifiers_snfei` (or associated build function) in associatied manual.rs.
4. Update the Python fallback builder in the Python `api.py`.
5. Update all references to associated .json files and tests.
   