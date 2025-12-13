# Implementation

This section describes how the Civic Exchange Protocol is implemented in practice.

It is not a tutorial and not a walkthrough. It defines the stable structure, responsibilities, and boundaries of the implementation layers so that multiple codebases, languages, and deployments can remain compatible over time.

Implementation guidance here is normative where it affects interoperability and deliberately non-prescriptive where local engineering choices do not.

---

## Scope

The implementation layer covers:

- How CEP concepts are realized in code and data
- How raw source data is transformed into CEP-compliant records
- How normalization, localization, and identity preparation are applied
- How provenance and validation requirements are enforced

It does **not** define:
- Business logic or policy decisions
- Domain-specific analytics
- User interfaces or storage systems

Those concerns sit outside CEP.

---

## Layered structure

Implementation is organized into a small number of layers with explicit contracts between them:

- **Components**: Core building blocks and shared services
- **Pipelines**: Deterministic data flows that transform inputs into records
- **Policies**: Cross-cutting rules that must be applied consistently
- **Adapters**: Boundary modules that translate external data into CEP form

Each layer is documented independently to avoid duplication and drift.

---

## Determinism and reproducibility

All CEP implementations must support:

- Deterministic execution given the same inputs
- Explicit handling of missing, null, and unknown values
- Stable serialization suitable for hashing and comparison
- Reproducible results across time, platforms, and languages

If a behavior cannot be made deterministic, it must be explicitly surfaced in provenance.

---

## Versioning and compatibility

Implementation details evolve, but compatibility is preserved through:

- Versioned schemas and vocabularies
- Explicit adapter versions
- Backward-compatible defaults
- Provenance fields that record which rules and configurations were applied

Code may change. Meaning must not.

---

## Relationship to specifications

This section operationalizes the specifications defined elsewhere:

- CEP reference defines *what* structures exist
- Implementation defines *how* they are produced
- Validation defines *whether* outputs conform

No implementation detail should contradict the reference specifications.

---

## Where to find code

Concrete implementations, examples, and test fixtures live in the repository:

- Python adapters and pipelines under `src/python/`
- Rust core and FFI under `src/rust/`
- Test vectors under `test_vectors/`
- Audit and analysis tools under `tools/`

Documentation describes contracts. Code demonstrates them.

---

## Stability

The high-level structure described in this section is intended to remain stable over the life of the project.

Details may be refined and names may be clarified as the ecosystem matures, but the layering and responsibilities defined here have been deliberately reviewed and stress-tested.

Implementations built against this structure are expected to remain understandable and evolvable over the foreseeable future, even as specific components, adapters, and policies continue to develop.
