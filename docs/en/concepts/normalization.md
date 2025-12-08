# Normalization

Normalization is the **first transformation step** in the CEP pipeline.  
Its purpose is to convert raw, heterogeneous civic data into a consistent structure before canonicalization and hashing.

In practice there are two layers:

- **Adapter-level normalization** - local, jurisdiction-aware cleaning and mapping from raw sources.
- **Core normalization** - a small, **international, script-preserving** pass implemented in the CEP core (Rust), applied just before SNFEI hashing.

This separation ensures:

- Adapters can reflect local domain knowledge and messy source quirks
- Core normalization remains stable and global across all jurisdictions
- Normalization rules can evolve without breaking the hash function, as long as the core contract is respected


---

## 1. Goals of Normalization

Normalization should:

- Produce **deterministic** strings (same input → same normalized form)
- Ensure **stable Unicode handling** across scripts
- Provide **predictable address strings** for hashing
- Remove noise (punctuation, obvious boilerplate) without erasing meaning
- Apply **jurisdiction-specific expansions** via configuration, not ad-hoc code

Normalization must **not**:

- Guess or infer missing values
- Perform record linkage or entity resolution
- Translate between languages
- Destroy information from non-Latin scripts just to satisfy ASCII-only constraints

Anything that changes semantic meaning or crosses those boundaries belongs outside the canonical SNFEI path.

---

## 2. Core Normalization Pipeline (International Policy)

The CEP core defines a **script-preserving** normalization policy used to build canonical inputs for SNFEI.
Adapters may do extra work, but they must not contradict this core behavior.

At a high level, core normalization does:

1. Unicode normalization and case folding  
2. Punctuation and spacing cleanup  
3. Safe abbreviation expansion  
4. Optional stop-word removal (language-aware)  
5. Address cleanup for hashing

### 2.1 Unicode Normalization and Case Folding

Core normalization applies Unicode normalization and converts text to a stable lowercase form. 

We use Normalization Form Compatibility Decomposition (NFKD) for the SNFEI canonicalization path.

**Understanding NFD vs. NFKD**

| Form | Full Name | Effect on Characters | Why We Use NFKD |
| ---- | --------- | -------------------- | --------------- |
| NFD | Normalization Form Decomposition | Separates base characters from combining marks/diacritics. | Preserves too much semantic variation. For example, it would treat compatibility characters differently from their base equivalents.
| NFKD | Normalization Form Compatibility Decomposition | Separates base characters,  and replaces compatibility characters (e.g.,  ligatures, Roman numerals) with their best plain text equivalent. | Addresses Entity Resolution. Compatibility characters often arise from rendering/typography and should be treated as equivalent for identity hashing (e.g., the KC in NFKC is too strict, but the KD in NFKD is perfect for eliminating visual noise). |


**The Core Process**

- Apply NFKD: The input string is converted to NFKD. This replaces ligatures and compatibility characters with their basic constituent letters.
- Strip **combining marks** where safe (é → e, ñ → n, ö → o) for Latin-based scripts.
- Preserve underlying letters in **all scripts** (Greek, Cyrillic, Han, Arabic, etc.).
- Apply lowercase / casefolding to get a consistent case-insensitive representation.

Examples:

- `"Société Générale"` → `"societe generale"`  
- `"Ελληνική Εταιρεία Δεδομένων"` → a lowercased Greek string with accents normalized, but **still in Greek**, not dropped or transliterated to ASCII.

**Key property:**  
Core normalization uses NFKD because it is the most aggressive form of decomposition that remains script-preserving (i.e., it doesn't try to turn Arabic into ASCII) while ensuring maximum equivalency for hashing identifiers, making two visually distinct inputs (due to font/encoding issues) hash to the same canonical ID.

### 2.2 Punctuation & Whitespace

All scripts share a common punctuation/whitespace policy:

- Replace punctuation (commas, periods, quotes, dashes, etc.) with spaces.
- Remove control characters.
- Collapse runs of whitespace to a single space.
- Trim leading/trailing spaces.

Examples:

- `"City of Springfield, Inc."` → `"city of springfield inc"`  
- `"123 N. Main St., Suite 400"` (before abbreviation expansion) → `"123 n main st suite 400"`

### 2.3 Abbreviation Expansion (Language- & Region-Aware)

Abbreviations are expanded **only** where we have explicit rules. Core provides a Latin-focused, international set; jurisdictions can add overlays (e.g. `us/mn.yaml`, `us/ma.yaml`).

Examples of core expansions:

- Legal forms:
  - `"inc"`, `"inc."` → `"incorporated"`
  - `"corp"`, `"corp."` → `"corporation"`
  - `"gmbh"` → `"gesellschaft mit beschrankter haftung"`
  - `"sa"`, `"s.a."` → `"sociedad anonima"` (by explicit rule)
- Organizational abbreviations:
  - `"sch"` → `"school"`
  - `"dist"` → `"district"`
  - `"univ"` → `"university"`

Address expansions (core US examples):

- `"st"`, `"st."` → `"street"`
- `"ave"`, `"ave."` → `"avenue"`
- `"n"`, `"n."` → `"north"`
- `"sw"` → `"southwest"`

For scripts outside that vocabulary, no attempt is made to transliterate or guess expansions; the text is left as cleaned lowercased Unicode.


### 2.4 Stop-Word Removal

Stop words are used cautiously and are **language-aware**:

- Core defines a small English set: `"the"`, `"of"`, `"and"`, `"for"`, `"in"`, etc.
- They may be removed after expansion and punctuation cleanup.
- For names beginning with a stop word, behavior can be configured (e.g. preserve `"the"` at the start vs. drop it).

Example (English):

- `"The City of Springfield"` → `"city springfield"`

For non-English scripts, stop-word lists must be defined explicitly; otherwise, core does **not** silently drop tokens.


### 2.5 Address Cleanup for Hashing

For SNFEI hashing, addresses are normalized into a minimal, stable form:

- Lowercase + Unicode normalization as above.
- Remove secondary unit designators (apt, suite, floor, room, etc.).
- Remove punctuation and collapse whitespace.
- Expand postal abbreviations (US: `st` → `street`, `rd` → `road`, directionals, etc.).
- Trim final result; empty or near-empty addresses become `None` in canonical form.

Example (US):

- Raw: `"123 N. Main St., Suite 400"`  
- Normalized: `"123 north main street"`

---

## 3. Canonical Input Shape

Core normalization produces a **canonical input struct** that feeds SNFEI hashing. Conceptually:

```json
{
  "legalNameNormalized": "springfield public schools",
  "addressNormalized": "123 north main street",
  "countryCode": "US",
  "registrationDate": "1985-01-15"
}
```

The canonical hash string is then built in a fixed order, e.g.:

`springfield public schools|123 north main street|US|1985-01-15`

Empty/unknown fields are represented as empty strings in the hash preimage, but stored as `null` / omitted in the JSON representation.

---

## 4. Example: From Raw to Normalized

Raw:
```json
{
  "legalName": "City of Springfield Unified Sch. Dist., Inc.",
  "address": "123 N. Main St., Suite 400",
  "countryCode": "US",
  "jurisdictionIso": "US-IL",
  "registrationDate": "01/15/1985"
}
```

Core-normalized canonical input:

```json
{
  "legalNameNormalized": "city springfield unified school district incorporated",
  "addressNormalized": "123 north main street",
  "countryCode": "US",
  "registrationDate": "1985-01-15"
}
```

International example (French):

```json
{
  "legalName": "Société Générale S.A.",
  "countryCode": "FR"
}
```

to:

```json
{
  "legalNameNormalized": "societe generale societe anonyme",
  "addressNormalized": null,
  "countryCode": "FR",
  "registrationDate": null
}
```

International example (Greek):

```json
{
  "legalName": "Ελληνική Εταιρεία Δεδομένων",
  "countryCode": "GR"
}
```

to: a lowercased Greek string with punctuation removed and whitespace collapsed;
the script remains Greek, not transliterated or dropped.



## 5. Normalization vs Canonicalization

| Stage            | Purpose    | Uses  |
| ---------------- | ---------- | ------|
| Adapter Normalization | Clean and map raw records into CEP-friendly fields   | Adapters / ETL code  |
| Core Normalization | Unicode-safe, script-preserving string cleanup | CEP Rust core |
| Canonicalization | Assemble final hash string and compute SNFEI | CEP Rust core (SNFEI) |


Notes:
- Adapter normalization may be jurisdiction-specific and can evolve quickly.
- Core normalization is global and stable; all implementations must match it.
- Canonicalization is purely structural: build the hash pre-image in the agreed order, then hash.

---

## 6. International Design

This design ensures that:

- The same entity produces the same SNFEI across jurisdictions and implementations.
- Latin-based names behave as expected (diacritics folded, legal suffixes expanded).
- Non-Latin scripts (Greek, Cyrillic, Han, Arabic, etc.) are first-class citizens, not collateral damage of ASCII-only assumptions.
- Future language- or country-specific tweaks (e.g. new legal forms) can be layered on via vocabularies and localization files, without rewriting the core.

Normalization is designed to be **transparent**, **domain-aware**, and **non-destructive**, serving as the reliable entrance to the CEP identity pipeline.
