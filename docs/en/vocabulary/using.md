# Using Domain Vocabularies in CEP Schemas

Domain vocabularies play a central role in how CEP schemas represent civic data.  
They provide **governed identifiers** for entity types, relationship types, roles, statuses, and other semantic categories that appear within domain schemas and adapters.

This document summarizes how domain vocabularies integrate with CEP schemas without listing any specific files, ensuring the guidance remains valid as domains evolve.

---

## 1. Entities in Domain Schemas

When defining or normalizing entities in a domain schema:

- Assign an **entity type URI** from the appropriate domain vocabulary  
- Ensure each domain entity type maps to a parent **core entity type**  
- Use the domain vocabulary to disambiguate between similar classes of entities that require distinct normalization or identity rules  

This allows schemas to remain domain-specific in meaning while structurally consistent across CEP.

---

## 2. Relationships in Domain Schemas

Domain schemas use **relationship type URIs** to express how entities connect.  
Using vocabulary-governed relationship types ensures:

- relationship meaning is unambiguous  
- analytical systems can group or reason about relationships consistently  
- graph normalization (GNS) can enforce allowed structures  
- adapters avoid inventing ad-hoc or inconsistent names  

Domain relationships inherit from core CEP relationship categories, supporting both specificity and interoperability.

---

## 3. Avoiding Hard-Coded Strings

Schemas and adapters should never introduce arbitrary new strings to represent types.  
Instead:

- import term URIs from the domain vocabulary  
- reference them in JSON Schemas, model definitions, and adapter logic  
- rely on governance processes to introduce new terms when needed  

This prevents drift, reduces validation failures, and keeps domain logic aligned with CEP core rules.

---

## 4. Using Vocabularies in Normalization Pipelines

Normalization steps typically:

1. **Classify** source records using domain vocabulary terms  
2. **Rewrite** or canonicalize values into stable term URIs  
3. **Validate** the result against domain and core schemas  
4. **Construct** canonical entities and relationships using vocabulary-driven types  

Because vocabulary terms are globally known and versioned, normalized data becomes:

- portable across jurisdictions  
- comparable across datasets  
- durable over time  

This is essential for CEP's multi-domain crosswalking and identity-resolution capabilities.

---

## 5. Domain Vocabularies and Adapter Design

Adapters should:

- import vocabulary terms directly  
- enforce vocabulary selection rules  
- avoid emitting entities or relationships without an assigned vocabulary-based type  

Adapter manifests may declare which domain vocabularies they rely on, enabling:

- automated validation  
- compatibility checks  
- dependency resolution in multi-adapter pipelines  

Domain schemas remain concise because semantics live in the vocabularies, not in the schema structure.

---

## 6. Domain Vocabularies and Canonicalization

CEP's canonicalization rules (CEC, GNS, EFS, GIC, etc.) rely on stable term URIs.  
Domain vocabularies support canonicalization by:

- constraining allowable entity and relationship types  
- enabling cross-domain reasoning (“this entity is a subtype of ORGANIZATION”)  
- giving canonicalization functions predictable input categories  
- informing identity rules (e.g., a PP_SUPPLIER and CF_CONTRIBUTOR may share identity logic as ORGANIZATION types)  

Canonicalization becomes *domain-aware* without losing global coherence.

---

## 7. Schema Stability Through Vocabulary Versioning

Because vocabulary files:

- are versioned  
- immutable once released  
- governed through VGS

domain schemas can remain stable even as domains evolve.  
Schema definitions rarely require modification; instead, vocabularies grow via:

- new term additions  
- deprecations (rare, carefully governed)  
- mappings to external standards  

This separation of concerns protects schemas from churn while allowing domain communities to refine semantics over time.

---

## Summary

Domain vocabularies enable CEP schemas to express rich, domain-specific semantics while preserving the structural, canonical, and graph-theoretic integrity of the core model.

By relying on vocabulary-governed identifiers:

- schemas stay stable  
- adapters stay compatible  
- canonicalization stays predictable  
- cross-domain analytics become possible  

Domain vocabularies are the key to extending CEP *without fragmenting it*.
