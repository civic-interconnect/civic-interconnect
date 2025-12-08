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

## [0.0.3] – 2025-12-08

### Added

- Rust–Python FFI stabilization:
  - New generate_snfei_detailed wrapper exposed cleanly through the Python cep_py extension module.
  - Python snfei package exports normalized function names with correct .pyi stubs.
- Improved international normalization behavior:
  - Legal-name normalization now preserves non-ASCII scripts (e.g., Greek) instead of ASCII-stripping entire strings.
  - Added targeted compatibility handling for dotted legal forms (e.g., S.A. to sa) before punctuation removal.

### Changed

- Normalization pipeline (Rust):
  - Revised abbreviation expansion ordering to prevent accidental s to south expansions in international names.
  - Updated French S.A. handling to resolve correctly to societe anonyme during canonicalization.
  - Deterministic alignment of canonical hash strings across Rust and Python paths.
- Removed Python normalizers:
  - Python-side normalization logic removed in favor of the authoritative Rust implementation.
  - Updated CLI (cx) and Python package imports to route through FFI-backed functions only.
- Typing:
  - Consolidated Python stub files  __init__.pyi) so Pylance correctly resolves exported symbols.

### Deleted
- Removed legacy Python SNFEI and normalization implementations in place of Rust logic.

---

## [0.0.2] – 2025-12-07

### Added
- End-to-end **example slice generation pipeline**:
  - `cx generate-example` produces `02_normalized.json`, `03_canonical.json`, and `04_entity_record.json`.
  - Example documentation pages under `docs/en/examples/...`.
- **Entity shape normalizer** in Python:
  - Guarantees presence of `entityTypeUri`.
  - Normalizes `identifiers` so `identifiers["snfei"]` is always a dict with `{"value": ...}`.
- Improved error messages in SNFEI pipeline.

### Changed
- **Rust SNFEI validator**:  
  Corrected lowercase-hex predicate so digits (`0–9`) are accepted and only uppercase hex is rejected.  
- Python SNFEI generator:
  - Uses native Rust backend when available.
  - Falls back to Python implementation with clear warnings.
- Updated Rust `entityType` vocabulary URI:
  - Ensured alignment between Rust builder output and Python expectations.
- Python Entity builder normalized output shape so downstream clients and tests are stable across native/Python paths.
- Simplified adapter mapping and fatal-error handling in `cx generate-example`.

---

## [0.0.1] – 2025-12-06

### Added

- Initial pre-alpha release of Civic Interconnect.
- Baseline monorepo structure:
  - JSON Schemas (source of truth)
  - Controlled vocabularies
  - Rust core (cep-core) with builders, validators, canonicalization, and FFI
  - Python bindings and CLI (cx)
- Initial documentation and MkDocs site scaffolding.
- First SNFEI canonicalization pipeline:
  - Unicode normalization
  - Abbreviation expansion
  - Address canonicalization
  - Deterministic hash construction
- First canonicalization test vectors for French, German, Greek, and international cases.
- Architecture foundations for Entity, Relationship, Exchange, and Context Tag record families.
- Initial FFI boundary design (python to Rust) with validated JSON record output.
- Initial CI workflows and package metadata for PyPI distribution.

---

## Notes on versioning and releases

- **SemVer policy**
  - **MAJOR** - breaking API/schema or CLI changes.
  - **MINOR** - backward-compatible additions and enhancements.
  - **PATCH** - documentation, tooling, or non-breaking fixes.
- Versions are driven by git tags via `setuptools_scm`.
  Tag the repository with `vX.Y.Z` to publish a release.
- Documentation and badges are updated per tag and aliased to **latest**.

[Unreleased]: https://github.com/civic-interconnect/civic-interconnect/compare/v0.0.3...HEAD  
[0.0.3]: https://github.com/civic-interconnect/civic-interconnect/releases/tag/v0.0.2
[0.0.2]: https://github.com/civic-interconnect/civic-interconnect/releases/tag/v0.0.2
[0.0.1]: https://github.com/civic-interconnect/civic-interconnect/releases/tag/v0.0.1