# Domain-Specific Vocabularies in CEP

Domain-specific vocabularies extend the **core CEP vocabulary layer** with additional semantic detail for particular civic and regulatory domains.  
They provide structured, stable identifiers for the concepts that matter within a domain while remaining compatible with CEP’s shared graph model.

These vocabularies do **not** redefine CEP data structures.  
Instead, they supply *specialized labels* that domain adapters, schemas, and analysis tools can use to describe:

- the types of entities present in a domain  
- the types of relationships that meaningfully link them  
- the terms used to classify events, roles, statuses, processes, or outcomes

This allows each domain to speak its own language without fragmenting the global model.

---

## Why Domain Vocabularies Exist

A single “universal” vocabulary cannot capture the detail required across all civic domains.  
Campaign finance, environmental regulation, education, procurement, elections, nonprofit filings, and transportation each involve:

- different classes of actors  
- different forms of interaction  
- different regulatory structures  
- different types of documents, permits, filings, or transactions

Domain vocabularies allow CEP to represent these differences *without changing the underlying schemas*.  
Every domain can introduce terms that matter locally while still interoperating globally.

---

## Relationship to Core CEP Vocabularies

Domain vocabularies **refine** the core vocabulary, not replace it.

- Core vocabularies define fundamental concepts:  
  `PERSON`, `ORGANIZATION`, `PROGRAM`, `PROCESS`, `EVENT`, `AGREEMENT`, `RELATIONSHIP_TYPE`, etc.

- Domain vocabularies introduce more specific versions:  
  campaign finance committees, procurement buyers, educational institutions, environmental permits, and so on.

Each domain term maps back to a **parent core term**, which ensures:

- cross-domain interoperability  
- consistent canonicalization and graph normalization  
- unified search, analytics, and reasoning across datasets  
- compatibility with shared identity resolution frameworks

This “refinement but not divergence” structure is central to CEP’s ability to unify heterogeneous civic data ecosystems.

---

## How Domain Vocabularies Are Used

Adapters, schemas, and validation logic may rely on domain vocabularies to:

- label entities and relationships with precise semantics  
- standardize classification across jurisdictions  
- ensure that normalized output follows a consistent, governed taxonomy  
- enable automated reasoning or validation (e.g., “only these entity types may appear in this schema”)  
- support crosswalks and interoperability with external standards

CEP itself does not prescribe which vocabularies must be used.  
Domains evolve independently through the Vocabulary Governance Specification (VGS) and may add or refine vocabularies over time.

---

## Principles for Domain Vocabulary Design

To ensure long-term usability and stability, domain vocabularies follow several principles:

- **Stability** — vocabularies are versioned and immutable once released  
- **Minimality** — include terms only when they serve identifiable modeling needs  
- **Extensibility** — new terms can be safely introduced without breaking existing data  
- **Interoperability** — domain terms map cleanly to CEP core and, when applicable, to external standards  
- **Clarity** — definitions aim to be domain-neutral, jurisdiction-neutral, and implementation-independent  

This keeps the vocabulary ecosystem manageable while allowing each domain to grow as needed.

---

## When to Introduce a New Domain Vocabulary

A new domain vocabulary is appropriate when:

- a domain contains entities or relationships not naturally expressible using only core vocabulary terms  
- adapters require finer-grained semantics to represent or normalize source data  
- a regulatory or analytical community uses a specialized taxonomy that merits a structured representation  
- interoperability with external standards benefits from explicit mappings  

CEP encourages domain vocabularies where they add real semantic value—and avoids them where core vocabularies suffice.

---

## Summary

Domain-specific vocabularies allow CEP to remain:

- **flexible** enough to model any civic domain  
- **stable** enough to maintain interoperability across domains  
- **extensible** enough to incorporate new sectors, jurisdictions, and standards  
- **coherent** as a unified rewriting and canonicalization framework

By refining rather than rewriting the core model, domain vocabularies keep CEP grounded in a single, shared semantic foundation while empowering rich domain-specific modeling.
