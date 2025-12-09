# What is SNFEI?

**SNFEI** stands for **Structured Non-Fungible Entity Identifier**.  
It is a deterministic, recomputable identifier designed for civic, educational, nonprofit, and other public-interest entities that **lack a national or global registry identifier** such as LEI or SAM-UEI.

SNFEI is *not* a proprietary ID and does not rely on any external registry.  
Instead, it provides an **open, stable, cross-dataset linking key** that any system can compute locally.

---

## Why SNFEI Exists

Many organizations—school districts, conservation districts, townships, cooperatives, special districts, community nonprofits—do not have a canonical global identifier.  
As a result:

- datasets frequently cannot be joined,
- names vary across sources,
- entities appear duplicated or fragmented,
- matching becomes ad-hoc and error-prone.

SNFEI introduces a **consistent, transparent, and reproducible identifier** that enables reliable linking without a central authority.

---

## How SNFEI Is Computed

An SNFEI is defined as:

> **SHA-256 hash of (normalized legal name + jurisdiction).**

This produces a **fixed, deterministic identifier** using inputs that are:

- already present in nearly all civic datasets,
- stable over time,
- easy to normalize and verify.

Because the process is deterministic, *any* system can recompute SNFEI and confirm whether two records refer to the same entity.

---

## Example

For an entity with:

- legal name = `Example School District 123`  
- jurisdiction = `US-MN`

The SNFEI is the SHA-256 hash of:

```
example school district 123 + us-mn
```

Example output:

```
34486b382c620747883952d6fb4c0ccdbf25388dfb0bb99231f33a93ad5ca5b3
```

This value becomes the entity's SNFEI and forms part of its **CEP verifiableId**:

```
cep-entity:snfei:<hash>
```

---

## When to Use SNFEI

Use SNFEI when:

- an entity does not have a recognized national/global identifier (LEI, SAM-UEI, etc.),
- datasets must be joined or deduplicated,
- building entity registries for transparency, civic data, or public-interest analytics,
- ensuring reproducible, provenance-aware entity referencing.

SNFEI complements, and does NOT replace, official identifiers.  
If a primary ID exists, CEP includes it; if not, SNFEI provides a consistent fallback.

---

## Vocabulary Reference

The SNFEI scheme is defined in the **CEP Identifier Scheme Vocabulary**:

```
https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabulary/entity-identifier-scheme.v1.0.0.json#snfei
```

This URI is the canonical value used in CEP records under:

```
identifiers[].schemeUri
```

SNFEI is versioned, openly described, and governed under the CEP Vocabulary Process.

