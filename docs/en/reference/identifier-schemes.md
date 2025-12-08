# Identifier Schemes

CEP uses a structured approach to identity, allowing multiple identifiers to coexist, link, or be mapped across systems.
Identifier schemes define how these IDs are interpreted, validated, and transformed across jurisdictions.

---

## 1. SNFEI (Sub-National Fixed Entity Identifier)

Scheme URI:

```
.../vocabularies/entity-identifier-scheme.v1.0.0.json#snfei
```

Characteristics:

-   Deterministic
-   Canonicalization-based
-   Cryptographic (SHA-256)
-   Stable across datasets and time
-   Designed to bridge to LEI, UEI, and EIN

Usage:

```json
"identifiers": {
  "snfei": { "value": "<hash>" }
}
```

---

## 2. External Identifier Schemes

CEP supports mapping to external IDs:

| Scheme    | Use Case                      | Notes                        |
| --------- | ----------------------------- | ---------------------------- |
| LEI       | Global financial identity     | ISO 17442 standard           |
| UEI       | U.S. federal awardees         | SAM.gov system               |
| EIN       | U.S. nonprofits & IRS filings | Numeric tax ID               |
| FEC ID    | Campaign committees           | U.S. federal election system |
| State IDs | Local entities                | Vary by state and domain     |

Each scheme is represented via:

```json
{
    "schemeUri": "<scheme-uri>",
    "identifier": "<id-value>",
    "sourceReference": null
}
```

---

## 3. Why Schemes Matter

Identifier schemes enable:

-   Cross-dataset linking
-   Disambiguation
-   Provenance tracking
-   Confidence scoring
-   Multi-jurisdiction integration

SNFEI is the **Tier 3 fallback** when LEI/UEI/EIN is missing or ambiguous.

---

## 4. Relationship to Identity Tiers

See `/en/reference/identity-tiers.md` for:

-   Tier 1 - Global IDs (LEI, UEI)
-   Tier 2 - National IDs
-   Tier 3 - SNFEI (canonical fallback)

Identifier schemes provide a common framing for linking these layers.

---

## 5. Mapping & Vocabulary Governance

Identifier scheme vocabularies are governed through:

-   Versioned JSON vocabularies
-   Change control via ISB governance
-   Mapping types: exactMatch, broadMatch, narrowMatch, relatedMatch

This ensures that identifier interactions remain stable and interpretable over time.
