# Identity Tiers and External IDs

> Civic Interconnect is building a unifying model for SNFEI, UEI, LEI, and domain-specific identifiers.

Modern civic data ecosystems contain a patchwork of identity systems.  
Some are globally regulated (LEI), some are national (UEI), and others are local or domain-specific (state vendor IDs, FEC committee IDs, IRS EINs, school district codes).  
The Civic Exchange Protocol (CEP) models these as **Identity Tiers**, each with different governance, scope, and persistence guarantees.

CEP's identity architecture organizes all IDs into a **three-tier model**, with the **SNFEI** (Structured Non-Fungible Entity Identifier) providing a stable, open, globally usable Tier-3 identifier that can employ and coexist with all external identifiers.

---

# 1. The Three Identity Tiers

## Tier 1: Global Regulated Identity (LEI, ISIN, etc.)

Examples:

-   LEI (Legal Entity Identifier)
-   CUSIP (Committee on Uniform Security Identification Procedures)
    -   Identifies securities in the US and Canada for trading, clearing, and settlement
    -   9 characters (alphanumeric)
    -   Managed by the CUSIP organization (operated by S&P)
-   ISIN (International Securities Identification Number)
    -   A universal code for cross-border transactions, identifying securities globally
    -   12 alphanumeric characters (2 country, 9 security, 1 check)
-   IBAN ( International Bank Account Number)
    -   Identifies a specific bank account.
    -   A long alphanumeric string (20-34 characters) that includes the country code, checksum, and account number.
    -   Used in countries with the IBAN system, primarily in Europe, the Middle East, and parts of the Caribbean and Latin America.
-   SWIFT (Society for Worldwide Interbank Financial Telecommunication)
    -   Identifies a specific bank.
    -   An 8 or 11-character code that includes bank, country, and location codes.
    -   Used globally to route transactions between financial institutions.

Characteristics:

-   Governed by global bodies (G20, ROC, ISO).
-   Designed for financial regulation, risk management, and reporting.
-   Strong persistence guarantees.
-   Difficult for civic and local entities to obtain.

Fit with CEP:

-   Tier-1 identifiers are linked via **Identifier objects** and treated as authoritative when present.
-   CEP never replaces them - it uses them.

---

## Tier 2: National or Federal Identity (UEI, EIN, FEC IDs)

Examples:

-   UEI (U.S. Government's Unique Entity Identifier)
-   EIN (IRS Employer Identification Number)
-   FEC Committee IDs (Federal Election Commission)
-   SAM Vendor IDs (System for Award Management Vendor Identifiers)
-   State corporate registry numbers

Characteristics:

-   Mandated for federal contracting, tax records, and campaign finance.
-   Highly structured but inconsistent across domains.
-   Often missing for municipalities, school districts, and NGOs.

Fit with CEP:

-   Tier-2 identifiers appear as authoritative external IDs attached to the Entity record.
-   They improve match confidence but are not universal or canonical.

---

## Tier 3: Open, Cross-Domain Identity (SNFEI)

The SNFEI is CEP's open identity layer, created from:

-   normalized legal name
-   optional address
-   country code
-   optional registration date

SNFEI solves the key problem Tier-1 and Tier-2 systems cannot:  
**a single, globally computable identifier for every civic entity**, even when no formal identifier exists.

Characteristics:

-   Fully open and reproducible (no central authority needed).
-   Deterministic: same input yields same output.
-   Bridges siloed systems (campaign finance -> procurement -> education -> nonprofits -> municipalities).
-   Coexists with all external IDs; never overrides them.

In the CEP envelope:

-   SNFEI always appears in the identifiers array and is embedded in the **verifiableId**.

---

# 2. Why Tiering Matters

### Interoperability

Allows systems with different authority models to share a coherent identity graph.

### Progressive Enhancement

Agencies with weak identity data can start with SNFEI and later link regulated IDs.

### Auditability & Provenance

All identifiers - Tier-1, Tier-2, and SNFEI - participate in:

-   provenance chains
-   confidence scoring
-   link reconciliation
-   graph reconstruction

### Avoids ID Fragility

If national systems change (UEI replaced the DUNS; EIN rules evolve), CEP identity remains stable.

---

# 3. Identifier Objects in CEP

CEP represents all identifiers - internal or external - using a uniform structure:

```json
{
    "schemeUri": "https://.../entity-identifier-scheme.v1.0.0.json#snfei",
    "identifier": "34486b382c620747883952d6fb4c0ccdbf25388dfb0bb99231f33a93ad5ca5b3",
    "sourceReference": null
}
```

Every identifier has:

| Field               | Meaning                                                                           |
| ------------------- | --------------------------------------------------------------------------------- |
| **schemeUri**       | Vocabulary URI specifying the identifier system (SNFEI, LEI, UEI, EIN, FEC, etc.) |
| **identifier**      | The actual ID value                                                               |
| **sourceReference** | Optional pointer to the authority or document asserting the ID                    |

This structure supports:

-   multiple coexisting IDs per Entity
-   crosswalks between ID ecosystems
-   automated resolution pipelines

---

# 4. How SNFEI Bridges External IDs

SNFEI is designed to:

-   connect disparate IDs,
-   anchor entities that lack regulated identifiers,
-   resolve duplicates across systems,
-   link historical and modern representations of the same entity,
-   provide a universal identity for graph-based analytics.

External IDs (LEI, UEI, EIN, FEC) are then attached as sibling identifiers.

Example:

```json
"identifiers": [
  { "schemeUri": "...#snfei", "identifier": "<hash>" },
  { "schemeUri": "...#uei",   "identifier": "ABC123DEF456" },
  { "schemeUri": "...#ein",   "identifier": "41-1234567" }
]
```

---

# 5. Summary Table

| Tier   | Examples                 | Authority                               | Purpose                           | CEP Role                                              |
| ------ | ------------------------ | --------------------------------------- | --------------------------------- | ----------------------------------------------------- |
| Tier 1 | LEI, ISIN, IBAN          | Global regulators (G20, ROC, ISO)       | Financial compliance & global KYC | Treated as authoritative external IDs                 |
| Tier 2 | UEI, EIN, FEC, State IDs | National or domain-specific authorities | Program compliance & reporting    | Supplementary identifiers with confidence attribution |
| Tier 3 | SNFEI                    | Open, reproducible                      | Universal identity across domains | Canonical internal identifier for CEP records         |

---

# 6. How This Helps the Research Community

-   CS researchers gain a unified identity graph with formal semantics.
-   Policy analysts can follow money and influence across institutions.
-   Open data ecosystems obtain a durable, globally interoperable identifier.
-   Auditors & compliance teams get cryptographically stable provenance.
