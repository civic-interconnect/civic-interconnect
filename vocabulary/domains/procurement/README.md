# Public Procurement Vocabularies (CEP Domain Package)

This directory contains the **controlled vocabularies used in the Public Procurement domain** of the Civic Exchange Protocol (CEP). These vocabularies provide stable identifiers and consistent terminology for procurement procedures, awards, contracts, suppliers, buyers, and related concepts.

Their purpose is to support **interoperable procurement data** across jurisdictions, agencies, platforms, and e-procurement systems.

---

## Purpose

Procurement data structures and terminology vary widely between local, national, and international systems. These vocabularies help:

- define **shared semantic categories** for procurement entities and processes  
- offer **stable URIs** used throughout CEP entities, relationships, and exchanges  
- support **canonicalization** and **identity resolution** for suppliers, buyers, and award records  
- facilitate data integration from procurement portals, transparency platforms, and regulatory systems  
- provide adapters with a consistent normalization target

Each vocabulary follows CEP’s standard machine-readable format and governance model.

---

## Included Vocabularies

This directory may include vocabularies such as:

- **Procedure Type** (open, restricted, negotiated, direct award, framework agreement, etc.)  
- **Award Type**  
- **Contract Type**  
- **Buyer Type** (e.g., agency, municipality, SOE, ministry)  
- **Supplier Role / Supplier Type**  
- **Procurement Category or Sector Codes**  
- **Notice, Tender, or Contract Status Terms**

The set of vocabularies may expand as procurement use cases develop within CEP.

---

## Relationship to Core CEP Vocabularies

These vocabularies extend CEP’s global categories by:

- specializing **entity types** for procurement records (buyers, suppliers, tenders, contracts)  
- defining **relationship types** that capture procurement flows (awards, contracts, frameworks)  
- aligning with recognized procurement standards when applicable (e.g., OCDS classifications)  
- enabling cross-domain integration with environmental, campaign finance, or education data where procurement interactions occur

Term mappings may be provided for interoperability across standards.

---

## Public Procurement Entity Types

This domain defines a set of **procurement-specific entity types** that refine CEP’s global `entity-type` vocabulary. These types allow adapters and schemas to represent procurement structures using stable, domain-appropriate categories.

The vocabulary file:

- [`entity-type.v1.0.0.json`](entity-type.v1.0.0.json)

includes entity classes such as:

- **PP_BUYER** — a contracting authority or purchasing body  
- **PP_SUPPLIER** — an economic operator, company, nonprofit, or consortium  
- **PP_PROCEDURE** — the procurement procedure itself  
- **PP_LOT** — a subdivision of the procurement scope  
- **PP_AWARD** — an award decision  
- **PP_CONTRACT** — the resulting legal agreement  
- **PP_IMPLEMENTATION** — payments, milestones, amendments, and related records  

Each of these maps back to a **core CEP entity class** (e.g., `ORGANIZATION`, `PROCESS`, `EVENT`, `AGREEMENT`) ensuring cross-domain interoperability and consistent graph normalization.

Adapters consuming procurement data should assign each entity a domain-specific entity type from this vocabulary.

---

## Public Procurement Relationship Types

Procurement processes involve structured interactions among buyers, suppliers, procedures, awards, and contracts.  
The CEP procurement domain models these interactions using a dedicated relationship-type vocabulary:

- [`relationship-type.v1.0.0.json`](relationship-type.v1.0.0.json)

This vocabulary defines relationships such as:

- **PP_BUYER_RUNS_PROCEDURE** — buyer → procedure  
- **PP_SUPPLIER_PARTICIPATES** — supplier → procedure or lot  
- **PP_PROCEDURE_INCLUDES_LOT** — procedure → lot  
- **PP_LOT_AWARDED_TO_SUPPLIER** — award → supplier  
- **PP_CONTRACT_BASED_ON_AWARD** — contract → award  
- **PP_CONTRACT_IMPLEMENTED_BY_SUPPLIER** — supplier → contract  
- **PP_IMPLEMENTATION_EVENT_FOR_CONTRACT** — implementation event → contract  

These map to CEP core relationships (e.g., `RESPONSIBLE_FOR`, `PARTICIPATION`, `AWARD`, `FULFILLS`) while providing the precision needed for procurement analytics and cross-jurisdictional harmonization.

Adapters should emit these relationship types in normalized procurement graphs.

---

## Usage in Adapters and Schemas

These vocabularies support:

- **procurement schemas** for notices, procedures, awards, contracts, and organizations  
- **adapters** ingesting procurement data from portals and regulatory systems  
- **canonicalization** of procurement records for clean analytical models  
- **validation** workflows inside CEP pipelines  
- **context tagging and provenance annotations** where procurement semantics matter

Adapters should normalize to the term URIs defined in these vocabulary files.

---

## Versioning and Governance

All vocabulary files follow CEP’s governance process:

- filenames include a version number (e.g., `v1.0.0`)  
- released vocabularies are immutable  
- updates follow the Vocabulary Governance Specification (VGS)  
- additive changes occur in minor versions; breaking changes require major versions

Organizations may publish additional procurement vocabularies as separate files.

---

## Contributing

To propose updates or additions:

- provide a clear rationale for new terms  
- reference relevant procurement regulations or standards where possible  
- include examples of usage from real procurement datasets  
- consider alignment with CEP core vocabularies and related domains

All changes are subject to CEP governance review.
