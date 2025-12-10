# Environmental Vocabularies (CEP Domain Package)

This directory contains the **controlled vocabularies used in the Environmental domain** of the Civic Exchange Protocol (CEP). These vocabularies define stable identifiers and shared definitions for concepts such as sites, permits, emissions, monitoring activities, and regulatory actors.

Their purpose is to support **interoperable and canonical environmental data** across local, state, federal, tribal, and international reporting systems.

---

## Purpose

Environmental data can differ significantly between agencies and regulatory frameworks. These vocabularies help:

- establish **common semantic categories** for environmental entities and activities  
- provide **stable URIs** for use in CEP entities, relationships, and exchanges  
- enable **identity resolution and canonicalization** across disparate systems  
- support integration of data from environmental agencies, monitoring networks, and permitting authorities  
- give adapters consistent target terms for normalization

Each vocabulary in this folder is machine-readable and versioned according to CEP’s governance rules.

---

## Included Vocabularies

This directory may include vocabularies such as:

- **Permit Type** (e.g., air permit, water discharge permit, land use permit)  
- **Site Type** (e.g., facility, monitoring station, remediation site)  
- **Emission or Release Type**  
- **Regulatory Action Type**  
- **Monitoring Method Type**  
- **Compliance or Violation Categories**

These vocabularies may expand over time as environmental reporting domains are brought into CEP.

---

## Relationship to Core CEP Vocabularies

These vocabularies extend CEP’s global vocabulary suite by:

- providing environmental-specific **entity types** (sites, permits, processes)  
- defining **relationship types** relevant to regulatory oversight and monitoring  
- aligning with standardized environmental classifications when possible  
- enabling cross-domain interoperability with procurement, education, campaign finance, and other CEP areas

Mappings to global CEP vocabularies may be included where applicable.

---

## Environmental Entity Types

Environmental data frequently involves sites, facilities, permits, regulatory authorities, measurement systems, and enforcement actions.  
The CEP environmental domain refines the global `entity-type` vocabulary through:

- [`entity-type.v1.0.0.json`](entity-type.v1.0.0.json)

This includes entity classes such as:

- **ENV_SITE** — facility, monitoring station, or regulated location  
- **ENV_FACILITY_OPERATOR** — organization operating a site  
- **ENV_PERMIT** — environmental permit, license, or authorization  
- **ENV_MONITORING_ASSET** — sensors or assets gathering measurements  
- **ENV_MEASUREMENT_SERIES** — environmental readings over time  
- **ENV_REGULATOR** — authority overseeing environmental compliance  
- **ENV_ENFORCEMENT_ACTION** — notice, penalty, or compliance order  

These map back to CEP core entity types (`SITE`, `ORGANIZATION`, `PERMIT`, `ASSET`, `DATASET`, `EVENT`) allowing environmental data to interoperate cleanly with other domains.

Adapters should assign these types when emitting normalized environmental entities.

---

## Environmental Relationship Types

Environmental regulation and monitoring generate rich, structured relationships among sites, permits, operators, measurements, and enforcement actions.  
These are captured in:

- [`relationship-type.v1.0.0.json`](relationship-type.v1.0.0.json)

Key relationships include:

- **ENV_SITE_OPERATED_BY** — site → operator  
- **ENV_SITE_PERMITTED_BY** — site → permit  
- **ENV_PERMIT_ISSUED_BY** — permit → regulator  
- **ENV_MEASUREMENT_FOR_SITE** — measurement series → site  
- **ENV_MEASUREMENT_BY_ASSET** — measurement series → monitoring asset  
- **ENV_ENFORCEMENT_AGAINST** — enforcement action → entity  

These refine CEP’s core relationships (e.g., `CONTROL`, `GOVERNED_BY`, `OBSERVATION_OF`, `SANCTION`) and support cross-dataset integration across regulatory or scientific monitoring systems.

Adapters should produce environmental graphs using these relationship types.


## Usage in Adapters and Schemas

These vocabularies support:

- **environmental schemas** for permits, facilities, emissions, compliance events, and monitoring data  
- **adapters** that ingest data from environmental agencies and reporting systems  
- **canonicalization** of environmental records across jurisdictions  
- **validation** workflows in CEP pipelines  
- **context tagging and provenance annotations** where environmental semantics matter

Adapters should reference the term URIs defined here when normalizing source-system values.

---

## Versioning and Governance

All vocabulary files here follow CEP’s versioning and governance rules:

- filenames include the vocabulary version (e.g., `v1.0.0`)  
- vocabularies are immutable once published  
- updates follow the Vocabulary Governance Specification (VGS)  
- minor versions may add terms; major versions represent breaking changes

Organizations may publish additional environmental vocabularies as parallel files.

---

## Contributing

Contributions should include:

- justification for new terms  
- references to regulatory definitions or environmental standards  
- examples of usage from real data sources  
- consideration of cross-domain alignment with CEP’s core vocabularies

All proposals are reviewed under CEP governance.
