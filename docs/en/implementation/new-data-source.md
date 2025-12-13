# Adding a New External Data Source

This document defines the **required steps** for adding any new external dataset to
the Civic Interconnect project. These steps ensure consistent documentation,
provenance, licensing, reproducibility, and adapter integration across all
verticals and implementations.

This guide applies to all external data used for:

- adapter development  
- canonicalization (EFS v1) testing  
- SNFEI identity evaluation  
- example input records  
- vertical demonstrations  
- validation pipelines  
- CEE evidence construction  

---

## 1. Add an Entry to `DATA_SOURCES.md`

All datasets must be listed in the global catalog at:

```
docs/en/reference/DATA_SOURCES.md
```

Each dataset entry must include:

- dataset title  
- publisher  
- URL  
- license  
- retrieval date  
- short description of how CEP uses it  
- a link to its PROV-YAML provenance file  
- embedded JSON citation block (see below)

Example block:

```markdown
### City of Chicago – Contracts Dataset
- URL: https://data.cityofchicago.org/Administration-Finance/Contracts/rsxa-ify5  
- Publisher: City of Chicago  
- License: Public Domain  
- Used for: canonicalization tests, adapter validation, SNFEI clustering  
- Provenance: [chicago_contracts.prov.yaml](../provenance/chicago_contracts.prov.yaml)
```

---

## 2. Create a PROV-YAML File

Each dataset must have a machine-readable provenance description following
**W3C PROV-DM**. Place this file in:

```
docs/en/provenance/<dataset_name>.prov.yaml
```

This file must contain:

- `prov:Entity` (the dataset)  
- `prov:Agent` (publisher or maintainer)  
- `prov:Activity` (retrieval/download event)  

Example:

```yaml
entity:
  chicago_contracts_dataset:
    prov:type: "prov:Entity"
    dct:title: "City of Chicago Contracts Dataset"
    dct:identifier: "https://data.cityofchicago.org/Administration-Finance/Contracts/rsxa-ify5"
    dct:publisher: "City of Chicago"
    dct:license: "Public Domain"

agent:
  city_of_chicago:
    prov:type: "prov:Agent"
    foaf:name: "City of Chicago, Department of Procurement Services"

activity:
  retrieve_chicago_contracts_2025_12_11:
    prov:type: "prov:Activity"
    prov:startedAtTime: "2025-12-11T00:00:00Z"
    prov:wasAssociatedWith: city_of_chicago
    prov:used: chicago_contracts_dataset
```

---

## 3. Add a Local `SOURCE.json` Next to Example Records

Whenever sample data or test fixtures depend on this dataset, place a minimal
citation/provenance descriptor **in the same folder** as the example files:

```
examples/<domain>/<entity>/SOURCE.json
```

Required fields:

```json
{
  "type": "dataset",
  "title": "City of Chicago Contracts Dataset",
  "publisher": "City of Chicago",
  "url": "https://data.cityofchicago.org/Administration-Finance/Contracts/rsxa-ify5",
  "license": "Public Domain",
  "retrievedAt": "2025-12-11T00:00:00Z",
  "provenance": {
    "entity": "chicago_contracts_dataset",
    "activity": "retrieve_chicago_contracts_2025_12_11",
    "agent": "city_of_chicago"
  }
}
```

This ensures example entity records are portable and self-describing.

---

## 4. Add the Dataset to `CITATION.cff` Under `references`

External datasets must appear only in the `references:` section of the root
`CITATION.cff`.

Example:

```yaml
references:
  - type: dataset
    title: "City of Chicago Contracts Dataset"
    authors:
      - name: "City of Chicago"
    year: 2025
    url: "https://data.cityofchicago.org/Administration-Finance/Contracts/rsxa-ify5"
    license: "Public Domain"
    notes: "Used for canonicalization tests, SNFEI identity resolution, and adapter development."
```

This supports reproducible research and automated citation tools.

---

## 5. Document Any Adapter-Specific Notes

If the dataset feeds a new adapter:

- describe any quirks  
- list which fields map to CEP entity properties  
- include normalization notes relevant to:
  - `legalName`
  - `legalNameNormalized`
  - identifiers
  - jurisdiction logic
  - address processing

Add this to:

```
docs/en/implementation/adapters.md
```

or create a short README in:

```
examples/<domain>/<entity>/README.md
```

---

## 6. Add or Update Tests

If the dataset is used for testing:

- ensure test fixtures reference the correct `SOURCE.json`  
- ensure example entity records contain embedded provenance  
- optionally add SNFEI clustering tests to validate normalization behavior

Typical file locations:

```
src/python/tests/adapters/
src/python/tests/identity/
examples/<domain>/<entity>/tests/
```

---

## 7. Confirm License Compatibility

Always verify:

- dataset license allows reuse, or  
- only sanitized examples are stored locally if redistribution is restricted  

Chicago Open Data → **Public Domain**, safe.  
Some state datasets → restrictive, only store small samples + manifests.

---

## Quick Checklist

- [ ] Add entry to `DATA_SOURCES.md`  
- [ ] Create PROV-YAML file under `docs/en/provenance/`  
- [ ] Add local `SOURCE.json` next to example data  
- [ ] Add dataset to `CITATION.cff` → `references:`  
- [ ] Document adapter rules or notes (if relevant)  
- [ ] Ensure tests reference the dataset correctly  
- [ ] Confirm licensing and sample handling  

---

Following these steps ensures CEP and CEE maintain strong provenance,
reproducibility, and academic transparency across all data pipelines.
