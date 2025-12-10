# Campaign Finance Vocabularies (CEP Domain Package)

This directory contains the **controlled vocabularies used in the Campaign Finance (CF) domain** of the Civic Exchange Protocol (CEP). These vocabularies provide stable identifiers, consistent definitions, and cross-domain mappings for key concepts such as committee types, contribution types, expenditures, parties, and public offices.

The purpose of these vocabularies is to make campaign-finance data **interoperable, canonical, and comparable** across jurisdictions, time periods, and source systems.

---

## Purpose

Campaign finance data varies widely across federal, state, and local reporting frameworks. These vocabularies serve to:

-   define **common semantic categories** shared across jurisdictions
-   provide **stable URIs** for reference in CEP entities, relationships, and exchanges
-   support **canonicalization and fingerprinting** in CEP pipelines
-   enable **cross-walking** between heterogeneous systems (e.g., FEC, state agencies, local filings)
-   give adapters a clear target space for normalization and enrichment

Each file in this directory is a **machine-readable vocabulary** in CEP’s standard format, versioned according to the Vocabulary Governance Specification (VGS).

---

## Included Vocabularies

This directory currently includes domain vocabularies for:

-   **Committee Type** (`committee-type.v1.0.0.json`)
-   **Contribution Type** (`contribution-type.v1.0.0.json`)
-   **Expenditure Type** (`expenditure-type.v1.0.0.json`)
-   **Party** (`party.v1.0.0.json`)
-   **Office** (`office.v1.0.0.json`)
-   **Filing Type** (`filing-type.v1.0.0.json`)
-   **Entity Type (specific)** (`entity-type.v1.0.0.json`)
-   **Relationship Type (specific)** (`relationship-type.v1.0.0.json`)

These vocabularies may be expanded over time as additional regulatory concepts, filing structures, or jurisdictional distinctions are incorporated into CEP.

---

## Relationship to Core CEP Vocabularies

CEP defines several **global vocabularies** (such as `entity-type`, `relationship-type`, and `source-system`).  
The CF domain vocabularies extend this system by:

-   refining global types with **campaign-finance-specific subcategories**
-   providing **mappings** back to global CEP types when appropriate
-   aligning with standardized external sources (e.g., FEC codes, state reporting codes) where possible
-   offering a unified domain-level semantic layer for CF adapters and validators

This layered approach allows the CF domain to remain interoperable with other CEP domains while still capturing necessary detail.

---

## Campaign Finance Entity Types

This domain defines a set of **campaign-finance-specific entity types** that refine CEP’s global `entity-type` vocabulary. These types allow adapters to represent committees, contributors, filings, and transactions with consistent semantics across jurisdictions.

The vocabulary file:

-   [`entity-type.v1.0.0.json`](entity-type.v1.0.0.json)

includes entity classes such as:

-   **CF_COMMITTEE** — a political committee (candidate, party, PAC, etc.)
-   **CF_CANDIDATE** — an individual running for office
-   **CF_CONTRIBUTOR** — a natural person or organization making contributions
-   **CF_VENDOR** — an entity receiving expenditures
-   **CF_FILING** — a regulatory filing or report
-   **CF_TRANSACTION** — a contribution, expenditure, loan, or other financial event
-   **CF_OFFICE** — an office sought or held
-   **CF_PARTY** — a political party organization

These map back to core CEP entity classes (e.g., `PERSON`, `ORGANIZATION`, `EVENT`, `DOCUMENT`) enabling consistent graph modeling.

Adapters should assign each campaign-finance entity a domain-specific entity type from this vocabulary.

---

## Campaign Finance Relationship Types

Campaign finance data involves structured interactions among committees, contributors, candidates, vendors, and regulatory bodies.  
The CEP campaign-finance domain models these interactions using a dedicated relationship-type vocabulary:

-   [`relationship-type.v1.0.0.json`](relationship-type.v1.0.0.json)

Key relationships include:

-   **CF_COMMITTEE_SUPPORTS_CANDIDATE** — committee → candidate
-   **CF_CONTRIBUTION_TO_COMMITTEE** — contributor → committee
-   **CF_EXPENDITURE_TO_VENDOR** — committee → vendor
-   **CF_FILING_SUBMITTED_BY** — filing → committee or candidate
-   **CF_OFFICE_SOUGHT_BY** — candidate → office
-   **CF_PARTY_AFFILIATION** — committee or person → party

These refine CEP’s core relationships (e.g., `TRANSFER`, `PARTICIPATION`, `RESPONSIBLE_FOR`) while supporting jurisdictional differences in reporting formats.

Adapters should use these relationships when emitting normalized CF graphs.

---

## Usage in Adapters and Schemas

These vocabularies are intended for use in:

-   **CF domain schemas** (e.g., committee, filing, transaction)
-   **adapters** that normalize data from jurisdictions or agencies
-   **canonicalization routines** that produce normalized entities and relationships
-   **validation** of CF data inside CEP pipelines
-   **context tagging (CTags)** and provenance annotations where type-level semantics matter

Adapters should reference the **term URIs** defined in these JSON files and, when appropriate, include mappings from their source systems to these controlled terms.

---

## Versioning and Governance

All vocabulary files here follow CEP’s standard versioning model:

-   filenames include the version number (e.g., `v1.0.0`)
-   vocabularies are immutable once published
-   revisions occur according to the Vocabulary Governance Specification (VGS)
-   new terms may be added in minor versions; breaking changes require a new major version

Jurisdictions or organizations that extend the CF vocabularies should publish their additions as separate vocabulary files, following the same format and naming conventions.

---

## Contributing

Contributions, corrections, and expansions to these vocabularies are welcome.  
Proposed changes should include:

-   justification for new terms or mappings
-   references to regulatory definitions when available
-   examples of real-world usage
-   compatibility considerations with global CEP vocabularies

All contributions are reviewed under CEP’s governance process.
