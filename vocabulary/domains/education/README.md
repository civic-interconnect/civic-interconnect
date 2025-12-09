# Education Vocabularies (CEP Domain Package)

This directory contains the **controlled vocabularies used in the Education domain** of the Civic Exchange Protocol (CEP). These vocabularies provide stable identifiers, shared definitions, and cross-domain mappings for key concepts involving institutions, programs, administrative roles, and education-related entities.

The goal of these vocabularies is to enable **interoperable, canonical representation of education data** across school districts, state agencies, higher education systems, and independent institutions.

---

## Purpose

Education data often comes from a wide range of systems—K–12 districts, universities, credentialing bodies, regulatory agencies, and program accreditors. These vocabularies help:

- define **common semantic categories** for education entities and relationships  
- provide **stable URIs** for use within CEP entities, relationships, and exchanges  
- support **canonicalization** and **identity resolution** across heterogeneous datasets  
- facilitate data **interoperability** between jurisdictions and institutions  
- give adapters a consistent set of target terms for normalization

Each vocabulary in this folder is machine-readable and follows CEP’s versioning and governance rules.

---

## Included Vocabularies

This directory may include vocabularies such as:

- **Institution Type** (e.g., district, school, university, research center)  
- **Program Type** (e.g., degree program, certification, curriculum track)  
- **Role Type** (e.g., superintendent, principal, dean, instructor)  
- **Accreditation or Licensing Types**  
- **Education Sector Mappings** (public, private, charter, tribal, etc.)

The specific files included may evolve as the domain is expanded and standardized.

---

## Relationship to Core CEP Vocabularies

These vocabularies extend the global CEP vocabulary suite by:

- specializing **entity types** for education institutions and programs  
- introducing **relationship types** relevant to governance, accreditation, and staffing  
- aligning with authoritative external terminology where applicable  
- enabling consistent semantics across CEP domains that interact with education data

Mappings to global CEP vocabularies are included where appropriate.

---

## Education Entity Types

The Education domain refines CEP’s global `entity-type` vocabulary to represent institutions, programs, roles, and learning artifacts with precision across K–12 and higher education systems.

The vocabulary file:

- [`ed-entity-type.v1.0.0.json`](ed-entity-type.v1.0.0.json)

includes entity classes such as:

- **ED_INSTITUTION** — school, district, college, university  
- **ED_PROGRAM** — a structured program or course of study  
- **ED_COURSE_INSTANCE** — a specific class offered in a term  
- **ED_PERSON** — a learner, instructor, or administrator  
- **ED_CREDENTIAL** — diploma, certificate, degree, or license  
- **ED_ASSESSMENT** — evaluation instrument or event  
- **ED_GOVERNANCE_BODY** — board, council, or committee  

Each maps back to core CEP entity types (`ORGANIZATION`, `PERSON`, `PROGRAM`, `DOCUMENT`, `EVENT`) to ensure cross-domain consistency.

Adapters should use these entity types when normalizing education datasets.

---

## Education Relationship Types

Education systems involve structured relationships among institutions, programs, people, and credentials.  
The CEP education domain defines these interactions via the vocabulary:

- [`ed-relationship-type.v1.0.0.json`](ed-relationship-type.v1.0.0.json)

Key relationships include:

- **ED_OFFERS_PROGRAM** — institution → program  
- **ED_RUNS_COURSE_INSTANCE** — institution → course instance  
- **ED_ENROLLED_IN_PROGRAM** — person → program  
- **ED_ENROLLED_IN_COURSE_INSTANCE** — person → course instance  
- **ED_TEACHES_COURSE_INSTANCE** — instructor → course instance  
- **ED_HOLDS_CREDENTIAL** — person → credential  
- **ED_ACCREDITED_BY** — institution → accreditation body  

These specialize CEP’s core relationships (e.g., `PARTICIPATION`, `EMPLOYMENT`, `ACCREDITATION`) while honoring the structural differences across education systems.

Adapters should use these to emit consistent education graphs.

---

## Usage in Adapters and Schemas

These vocabularies are intended to support:

- **education-specific schemas** (institutions, staff, programs, enrollments)  
- **data adapters** for districts, state agencies, universities, and accreditation systems  
- **canonicalization processes** that produce normalized education records  
- **validation** workflows in CEP pipelines  
- **context tags and provenance metadata** where education semantics are relevant

Adapters should reference the term URIs in these vocabulary files and document any mappings from source systems.

---

## Versioning and Governance

All vocabulary files follow CEP’s standard versioning model:

- filenames include the version (`v1.0.0`, etc.)  
- vocabularies are immutable once released  
- updates follow the Vocabulary Governance Specification (VGS)  
- new terms may be added in minor versions; breaking changes require a major version  

Organizations adopting these vocabularies may publish extensions as separate files using the same structure.

---

## Contributing

Contributions are welcome and should include:

- rationale for new terms or refinements  
- references to regulatory or institutional definitions when available  
- examples of real-world usage  
- compatibility considerations with CEP’s core vocabularies  

All changes are reviewed under CEP governance.
