# Changelog

All notable changes to this project will be documented in this file.

The format follows **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

---

## [Unreleased] - yyyy-mm-dd

### Added

### Changed

### Deleted

---

## [0.0.6] - 2025-12-12

This release focuses on locking down the Rust-first localization path and making the Python layer a thin, stable facade. It clarifies the "attestations are required but not created by core" boundary,
and provides end-to-end correctness for localization and SNFEI tests.

### Major Additions

-   Rust-first localization facade (Python)

    -   Standardized a thin wrapper module that delegates localization to the `cep_py` extension module and exposes a stable Python API:
        -   `apply_localization_name(...)`
        -   `apply_localization_name_detailed(...)`
        -   `apply_localization_name_detailed_json(...)`
    -   Wrapper explicitly avoids business logic and exists to provide an ergonomic, stable Python surface.

-   Typing and toolchain alignment
    -   Added `stubPath = "./typings"` to Pyright config so `typings/cep_py/__init__.pyi` is used during type checking.
    -   Updated the `cep_py` stub surface to match the Rust-exported symbols (no `_py` suffixes in the Python-facing API).

### Adapters & Examples

-   Migration direction established: adapters/examples call the Rust-wrapper localization in `canonicalize()`.

### Tests & Quality

-   Removed any calls to `_py` FFI names that no longer exist at runtime (e.g., `apply_localization_name_py`).
-   Verified full local quality gate success:
    -   pre-commit all-files: B1-B7 passed
    -   pytest identity suite passed (including new Chicago vendor SNFEI batch test output writing using a partial City of Chicago, Contracts Dataset from <https://github.com/civic-interconnect/civic-data-identity-us-il>.

### Architecture / Governance Notes

-   Re-affirmed boundary: 1+ attestations are required by record-envelope schemas; cep-core does not invent them.
-   Ingest/adapters/CLI supply attestations; core validates and carries them.

---

## [0.0.5] - 2025-12-10

This release introduces the vertical-slice architecture for CEP/CEE and unifies
multiple governance, documentation, and validation layers.
The system can formally describe and validate cross-domain verticals
(e.g., community assets, education access, environmental compliance, SME-friendly
procurement).

### Major Additions

-   Vertical Slice Framework

    -   Added `about.yaml` governance schema (`schemas/governance/about.schema.json`).
    -   Introduced five initial verticals under `docs/en/verticals/`:
        `community`, `edaccess`, `env`, `resilience`, and `sme`.
    -   Each vertical includes:
        -   `about.yaml` (schema-validated roadmap and modeling contract)
        -   `index.md` (overview)
        -   `explanations.md` (CEE explanation catalog)

-   Vertical Validation Tooling
    -   New command: `tools/validate_verticals.py`
    -   Validates `about.yaml` files against the new governance schema.
    -   Ensures required fields, actor motivations, actions, data sources, CEP/CEE scopes,
        user stories, and test declarations are complete and consistent.

### CEE (Civic Explanation Engine)

-   Added scaffolding for SME-Friendly Procurement explanations:
    -   `build_sme_evidence`
    -   `build_sme_attribution`
    -   `build_sme_explanation_bundle`
-   Added test suite structure for SME explanations:
    -   `test_procurement_sme_explanations.py`
    -   `test_sme_roundtrip.py`
-   Introduced example bundles for verticals:
    -   `examples/verticals/sme/…`

### Adapters & Pipeline

-   Formalized adapter layout:
    `src/python/src/civic_interconnect/cep/adapters/<domain>/<vertical>/adapter.py`
-   Added Procurement SME adapter scaffold using example OCDS releases as input.
-   Strengthened identity-construction patterns (SNFEI projections for buyer, lot, contract).

### Documentation Structure

-   Added nav entries for each vertical.
-   Standardized initial vertical documentation format:
    -   Overview (`index.md`)
    -   Explanation catalogue (`explanations.md`)
    -   Schema-typed roadmap (`about.yaml`)

### Governance & Modeling Improvements

-   Extended `about.schema.json` with:
    -   `id`, `userStories`, and `tests` as required sections
    -   Stricter regex requirements for identifiers
    -   Explicit modeling of CEP entities, relationships, identity notes, and envelope usage
    -   Explicit CEE explanation types and vertical outputs

### Quality & Consistency

-   Five verticals validate cleanly.
-   Directory layouts for examples, adapters, tests, and documentation are settling out.

---

## [0.0.4] – 2025-12-09

This release stabilizes several foundational components across Python and Rust.  
It consolidates schema-driven generation, domain scaffolding, adapters, and  
cross-language consistency. Work continues, but the following items are now in place  
and functioning across multiple domains.

-   Updated schemas across multiple domains and regenerated Rust + Python code.
-   Added Python adapters (`us_ca_municipality`, `us_mn_municipality`, `fec_csv`, etc.).
-   Introduced `codegen` layer for Rust and Python constants to eliminate hand-typed identifiers.
-   Integrated `cep-core` with generated Rust types and manual helpers.
-   Added domain crate `cep-domains` with generated records in structured module layout.
-   Expanded Python CEP core (`attestation`, `canonical`, `hash`, `schema_registry`, etc.).
-   CLI runs normally (`cx normalize`, codegen commands, example generation).
-   Packaging works: `maturin develop` installs Python bindings cleanly.
-   Current tests in `cep-core` pass after regeneration.

---

## [0.0.3] – 2025-12-08

### Added

-   Rust–Python FFI stabilization:
    -   New generate_snfei_detailed wrapper exposed cleanly through the Python cep_py extension module.
    -   Python snfei package exports normalized function names with correct .pyi stubs.
-   Improved international normalization behavior:
    -   Legal-name normalization now preserves non-ASCII scripts (e.g., Greek) instead of ASCII-stripping entire strings.
    -   Added targeted compatibility handling for dotted legal forms (e.g., S.A. to sa) before punctuation removal.

### Changed

-   Normalization pipeline (Rust):
    -   Revised abbreviation expansion ordering to prevent accidental s to south expansions in international names.
    -   Updated French S.A. handling to resolve correctly to societe anonyme during canonicalization.
    -   Deterministic alignment of canonical hash strings across Rust and Python paths.
-   Removed Python normalizers:
    -   Python-side normalization logic removed in favor of the authoritative Rust implementation.
    -   Updated CLI (cx) and Python package imports to route through FFI-backed functions only.
-   Typing:
    -   Consolidated Python stub files **init**.pyi) so Pylance correctly resolves exported symbols.

### Deleted

-   Removed legacy Python SNFEI and normalization implementations in place of Rust logic.

---

## [0.0.2] – 2025-12-07

### Added

-   End-to-end **example slice generation pipeline**:
    -   `cx generate-example` produces `02_normalized.json`, `03_canonical.json`, and `04_entity_record.json`.
    -   Example documentation pages under `docs/en/examples/...`.
-   **Entity shape normalizer** in Python:
    -   Guarantees presence of `entityTypeUri`.
    -   Normalizes `identifiers` so `identifiers["snfei"]` is always a dict with `{"value": ...}`.
-   Improved error messages in SNFEI pipeline.

### Changed

-   **Rust SNFEI validator**:  
    Corrected lowercase-hex predicate so digits (`0–9`) are accepted and only uppercase hex is rejected.
-   Python SNFEI generator:
    -   Uses native Rust backend when available.
    -   Falls back to Python implementation with clear warnings.
-   Updated Rust `entityType` vocabulary URI:
    -   Ensured alignment between Rust builder output and Python expectations.
-   Python Entity builder normalized output shape so downstream clients and tests are stable across native/Python paths.
-   Simplified adapter mapping and fatal-error handling in `cx generate-example`.

---

## [0.0.1] – 2025-12-06

### Added

-   Initial pre-alpha release of Civic Interconnect.
-   Baseline monorepo structure:
    -   JSON Schemas (source of truth)
    -   Controlled vocabularies
    -   Rust core (cep-core) with builders, validators, canonicalization, and FFI
    -   Python bindings and CLI (cx)
-   Initial documentation and MkDocs site scaffolding.
-   First SNFEI canonicalization pipeline:
    -   Unicode normalization
    -   Abbreviation expansion
    -   Address canonicalization
    -   Deterministic hash construction
-   First canonicalization test vectors for French, German, Greek, and international cases.
-   Architecture foundations for Entity, Relationship, Exchange, and Context Tag record families.
-   Initial FFI boundary design (python to Rust) with validated JSON record output.
-   Initial CI workflows and package metadata for PyPI distribution.

---

## Notes on versioning and releases

-   **SemVer policy**
    -   **MAJOR** - breaking API/schema or CLI changes.
    -   **MINOR** - backward-compatible additions and enhancements.
    -   **PATCH** - documentation, tooling, or non-breaking fixes.
-   Versions are driven by git tags via `setuptools_scm`.
    Tag the repository with `vX.Y.Z` to publish a release.
-   Documentation and badges are updated per tag and aliased to **latest**.

[Unreleased]: https://github.com/civic-interconnect/civic-interconnect/compare/v0.0.6...HEAD
[0.0.6]: https://github.com/civic-interconnect/civic-interconnect/releases/tag/v0.0.6
[0.0.5]: https://github.com/civic-interconnect/civic-interconnect/releases/tag/v0.0.5
[0.0.4]: https://github.com/civic-interconnect/civic-interconnect/releases/tag/v0.0.4
[0.0.3]: https://github.com/civic-interconnect/civic-interconnect/releases/tag/v0.0.3
[0.0.2]: https://github.com/civic-interconnect/civic-interconnect/releases/tag/v0.0.2
[0.0.1]: https://github.com/civic-interconnect/civic-interconnect/releases/tag/v0.0.1
