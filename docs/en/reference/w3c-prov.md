# W3C PROV Provenance Standard

W3C PROV formalizes provenance as a causal graph that captures how digital or real-world artifacts are produced, modified, and influenced over time.
By expressing the relationships among entities, activities, and agents, PROV provides a common framework for tracing lineage, validating data integrity, and supporting auditability across systems.
Its simplicity makes it compatible with JSON-based workflows, Linked Data environments, and domain-specific standards such as Civic Interconnect.

PROV encourages systems to represent not only what exists but how it came to exist.
This enables reproducibility, version tracking, trust assessment, and rigorous reasoning about the origins and transformations of information.

There are three fundamental node types:

1. Entity - a thing in some state (a dataset version, a file, a record, a JSON document)
2. Activity - something that happens over time (an ingestion process, a transformation, a merge)
3. Agent - something responsible (a human, an organization, a software system)

There are three fundamental relation types:

- wasGeneratedBy (Entity wasGeneratedBy Activity)
- used (Activity used prior Entity)
- wasAttributedTo (Entity wasAttributedTo Agent)

 Agent -> performed  -> Activity -> generated -> Entity


## Interface to Civic Interconnect Civic Exchange Protocol

Civic Interconnect mirrors core PROV concepts:

- Entities correspond to CEP Entity Records, Relationship Records, Vocab Terms, and transformed dataset snapshots.
- Activities map cleanly to CEP ingest steps, validation passes, transformations, merges, exports, and publication workflows.
- Agents align with CEP attestors, ingestion identities, organizations, and software systems that produce or modify records.

CEP's attestation block functions as a structured, PROV-compatible expression of responsibility and origin, capturing who created or updated a record and under what method.
By keeping CEP's entity life cycle parallel to PROV's activity graph, implementations gain a clear, interoperable provenance layer that can integrate with open data catalogs, regulatory reporting systems, and scientific reproducibility frameworks.

A PROV-compliant layer would formalize:

- which steps are activities
- which outputs are entities
- which systems or people are agents
- and the edges connecting them.

## PROV Components

### PROV-DM

Data Model. 
The ontology that defines the conceptual graph (entity, activity, agent, and their relations).

### PROV-N

A simple human-readable notation (like Turtle).
Good for examples, academic papers.

### PROV-O

An RDF/OWL ontology.
When we express provenance in Linked Data form, use this.

### PROV-JSON / PROV-XML

Concrete serializations.
Most practical systems use PROV-JSON.

## PROV Ecosystem

PROV works with:

### 1. SKOS

A vocabulary framework for controlled terms.
CEP vocabularies (entity types, relationship types) reference SKOS mappings.

### 1. JSON Schema / XML Schema

Define shape and validation rules.
These are not provenance - they are structure contracts.
PROV complements them, it does not replace them.

### 3. Linked Data / RDF / OWL

Semantic frameworks like PROV-O, for when provenance needs to interoperate on the semantic web.

### 4. W3C Verifiable Credentials (VC)

Where attestation comes in.
When we attach provenance and add cryptographic signatures, we get VCs.
The CEP attestation field is parallel to this, just simplified.

### 5. PROV extensions used in scientific computing

Like PROV-One (workflow-focused).
Used to describe complex multi-step pipelines.

### 6. Data catalogs (CKAN, DCAT)

Metadata catalogs that can store PROV graphs about datasets.
When publishing dataset metadata, DCAT is the companion standard.
[CKAN](https://ckan.org/) is an open source data management system used by US [data.gov](https://data.gov/), the government of Canada, and more. 