# Record Envelopes

A record envelope wraps a civic record with metadata required for transport,
validation, and interpretation.

Envelopes separate _content_ from _context_.

---

## Envelope Purpose

The envelope provides:

-   Version information
-   Schema references
-   Source metadata
-   Optional integrity material

The enclosed record remains unchanged across envelopes.

---

## Validation Boundary

Validation occurs at the envelope level.

CEP treats envelope validation as orthogonal to semantic correctness.

---

## Durability

Envelopes are designed to remain interpretable even as schemas evolve,
through explicit versioning and references.

---

This page defines how CEP records are packaged and moved safely.
