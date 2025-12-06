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
- Architecture foundations for Entity, Relationship, Exchange, and P3Tag record families.
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

[Unreleased]: https://github.com/civic-interconnect/civic-interconnect/compare/v0.0.1...HEAD  
[0.0.1]: https://github.com/civic-interconnect/civic-interconnect/releases/tag/v0.0.1