# Missing and Null Values

Missing and null values are treated explicitly.

Rules:
- Absence is not inferred
- Null is not equivalent to empty
- Defaults must be declared, not assumed

Downstream consumers must be able to distinguish omission from declaration.
