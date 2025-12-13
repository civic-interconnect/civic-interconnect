# Graph Normalization Specification (GNS v1)

Version: 1.0.0  
Status: Draft  
Applies to: CEP entity graphs, provenance graphs, and merged graphs  
Purpose: Define a deterministic normal form for CEP graphs so that equivalent graphs produce identical canonical representations and hashes.

---

## 1. Overview

CEP represents civic data as graphs:

- **Entity graphs**: entities, relationships, and their links.  
- **Provenance graphs**: entities, activities, and agents (PROV-style).  
- **Merged graphs**: combined views over multiple sources and versions.

The Graph Normalization Specification (GNS) defines how to:

1. Represent graphs in a uniform structural model.  
2. Canonically label nodes that lack global identifiers.  
3. Order nodes and edges deterministically.  
4. Serialize graphs via CEC v1 for hashing and verification.  
5. Guarantee that semantically equivalent graphs normalize to the same form.

GNS is versioned independently from CEC, schemas, and vocabularies.

---

## 2. Graph Model

### 2.1 Nodes

Each node has:

- `nodeId`: a string identifier (global or canonical local)  
- `nodeType`: one of  
  - `entity`  
  - `relationship`  
  - `activity`  
  - `agent`  
  - `envelope` (optional, for packaging)  
- `payload`: a CEC-compatible JSON object containing the node's attributes

Entity nodes should carry their `verifiableId` (from EFS) in the payload.

### 2.2 Edges

Each edge has:

- `sourceNodeId`  
- `targetNodeId`  
- `edgeType`: a label (e.g., `used`, `wasGeneratedBy`, `wasAttributedTo`, `hasRelationship`, `participatesIn`, domain-specific relationship types)  
- `edgePayload`: optional attributes (e.g., role labels, qualifiers)

### 2.3 Graph

A graph `G` is:

```json
{
  "graphId": "<optional, see hashing>",
  "nodes": [ ... ],
  "edges": [ ... ],
  "graphMetadata": {
    "gnsVersion": "1.0.0",
    "cecVersion": "1.0.0",
    "schemaVersions": { "...": "..." },
    "vocabularyVersions": { "...": "..." }
  }
}
```

The normalization process produces a canonical graph object of this shape.

---

## 3. Goals of Graph Normalization

GNS aims to ensure that:

**Determinism**  
For a fixed input graph semantics and version tuple, every implementation produces the same normalized graph.

**Idempotence**  
Normalizing an already normalized graph yields the identical graph.

**Equivalence**  
Graphs that differ only by node-labeling or edge ordering but represent the same structure normalize to the same canonical form.

**Hash stability**  
The normalized graph can be CEC-serialized and hashed to yield a stable graph-level CTag.

---

## 4. Node Identity and Labeling

### 4.1 Entity Nodes

Entity nodes have stable global identifiers.

The payload **MUST** include:

- `verifiableId` (from the Entity Fingerprint Specification)  
- `entityTypeUri`

The `nodeId` for entity nodes **MUST** be set to `verifiableId`.

No relabeling is required for entity nodes.

### 4.2 Non-Entity Nodes (Activities, Agents, Relationships, Envelopes)

Non-entity nodes may not have globally stable IDs. For such nodes, GNS defines a canonical local ID computed from:

- The node's type  
- A deterministic summary of its payload  
- The multiset of incident edges (types + endpoint identifiers)  
- Optional timestamps where present  

Canonical local ID:

```
canonicalLocalId = "gns:" || base64url( H( summary(node) ) )
```

Where `summary(node)` is a CEC-serialized JSON object:

- `nodeType`  
- `payload` (CEC-normalized)  
- `incidentEdges`: a sorted list of `{ edgeType, direction, otherNodeId }`

Hash function `H` is typically SHA-256.

`base64url` is standard URL-safe Base64 encoding.

**incidentEdges** sorting order:

1. `edgeType`  
2. `direction` ("in" or "out")  
3. `otherNodeId`

### 4.3 Labeling Procedure and Fixed Point

Because non-entity node labels depend on incident edges and incident edges depend on node labels, GNS defines a fixed-point procedure:

**Initial labeling**

- Entity nodes: `nodeId = verifiableId`  
- Non-entity nodes: temporary IDs (internal indices)

**Procedure**

1. Compute summaries for all non-entity nodes using current IDs.  
2. Compute canonicalLocalId for each non-entity node.  
3. Replace temporary IDs with canonicalLocalId.  
4. Rebuild edges with updated sourceNodeId / targetNodeId.

This converges in one iteration because:

- entity IDs are stable  
- each non-entity ID depends only on:
  - node type  
  - payload  
  - incident edges with stable entity IDs and previously computed local IDs  

Implementations **MUST** perform at least one full pass.  
A second pass **MUST** produce identical results (idempotence).

---

## 5. Edge Normalization

After node IDs are canonical:

For each edge:

- Ensure `sourceNodeId` and `targetNodeId` use canonical IDs.  
- Canonicalize `edgePayload` via CEP normalization + CEC.  

Sort edges by:

1. `edgeType`  
2. `sourceNodeId`  
3. `targetNodeId`  
4. `CEC(edgePayload)`  

If `edgePayload` is absent, treat it as `{}` for CEC.

---

## 6. Node List Normalization

After node IDs are canonical:

- Canonicalize each `payload` via CEP normalization + CEC.  
- Sort nodes by:

1. `nodeType`  
2. `nodeId`  
3. `CEC(payload)`  

---

## 7. Canonical Graph Serialization

Construct the graph object:

```json
{
  "graphMetadata": {
    "gnsVersion": "1.0.0",
    "cecVersion": "<cecVersion used>",
    "schemaVersions": { ... },
    "vocabularyVersions": { ... }
  },
  "nodes": [ ... ],
  "edges": [ ... ]
}
```

Serialize via **CEC v1**:

- lexicographic key ordering  
- omit `null` values  
- normalize numbers, strings, lists per CEC  

The result is the canonical graph JSON.

---

## 8. Graph Hash and Graph-Level CTag

```
graphHash = H( CEC(graphObject) )
graphTag  = "cep-graph:" || base64url(graphHash)
```

Uses:

- as a `graphId`  
- as a provenance reference  
- for caching and deduplication  

---

## 9. Recursion Guards and Idempotence

Implementations **MUST** ensure:

- **Idempotence**: normalizing a normalized graph yields identical output.  
- **No recursive expansion**: do not re-run canonicalization or adapters.  
- **Finite behavior**: normalization must terminate for all finite graphs.  
- **Order of operations**: all canonicalization must occur *before* graph normalization begins.

---

## 10. Relationship to Other CEP Specifications

GNS builds upon:

- **Canonical Encoding (CEC v1)**  
- **Entity Fingerprint Specification (EFS v1)**  
- **Adapter Algebra Specification (AAS v1)**  

GNS ensures graph-level determinism and hashing; it does **not** redefine canonicalization or adapter semantics.

---

## 11. Versioning

Semantic versioning:

- **MAJOR**: breaking changes  
- **MINOR**: backward-compatible additions  
- **PATCH**: clarifications, editorial fixes  

Every normalized graph MUST include:

```json
"graphMetadata": {
  "gnsVersion": "1.0.0",
  ...
}
```

---

## 12. Summary

GNS v1 defines:

- a uniform CEP graph model  
- canonical labeling for non-entity nodes  
- deterministic node and edge ordering  
- CEC-based canonical serialization  
- a graph-level CTag mechanism  

These together provide a stable foundation for provenance, merges, cross-source entity graphs, and higher-level CEP reasoning.

