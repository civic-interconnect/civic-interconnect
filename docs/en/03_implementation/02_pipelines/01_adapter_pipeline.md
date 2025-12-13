# Adapter Pipeline

The adapter pipeline is the primary ingestion path.

It typically includes:
- Source parsing
- Field alignment
- Structural validation
- Canonicalization
- Identity fingerprinting
- Provenance attachment

Adapters may omit steps that are not applicable, but must not reorder declared stages.
