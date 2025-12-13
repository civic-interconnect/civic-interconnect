# Tradeoffs and Alternatives

Every architectural choice implies tradeoffs.

This framework favors explicit structure, layered responsibility, and auditability.
As a result, it may appear more verbose or formal than systems optimized for rapid ingestion or ad hoc analysis.

Alternative approaches often collapse layers:

-   embedding interpretation into ingestion,
-   encoding policy assumptions directly into schemas,
-   or conflating evidence with outcomes.

Those approaches can be effective in closed systems.
They tend to break down when data must be shared across institutions, time horizons, or value systems.

The framework makes different tradeoffs to support longevity and cross-context reuse.
