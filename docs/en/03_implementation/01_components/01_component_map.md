# Component Map

The core implementation components are:

- Schemas: define structural contracts
- Vocabularies: define controlled terms
- Adapters: transform external data into CEP-conformant records
- Canonicalization: normalize structure and representation
- Identity: compute declared fingerprints
- Provenance: record how data was produced
- Validation: check conformance to declared rules

No component assumes the internal behavior of another.  
All coordination occurs through explicit artifacts.
