# External Data Sources Used in Civic Interconnect

This document lists datasets used during development, testing, and validation of
the Civic Exchange Protocol (CEP), the Contextual Evidence and Explanations (CEE)
layer, and associated adapters.

All external datasets include provenance, licensing information, and machine-
readable citations following the W3C PROV standard.

---

## City of Chicago – Contracts Dataset

**URL:**  
https://data.cityofchicago.org/Administration-Finance/Contracts/rsxa-ify5

**Publisher:**  
City of Chicago, Department of Procurement Services

**License:**  
Public Domain (Chicago Open Data Portal)

**Usage in CEP:**  
This dataset is used for testing:
- name normalization (EFS v1)
- SNFEI cross-source entity identity resolution
- adapter behavior for real-world procurement verticals
- canonicalization stress tests

**Embedded JSON Citation Block:**
```json
{
  "type": "dataset",
  "title": "City of Chicago Contracts Dataset",
  "publisher": "City of Chicago",
  "url": "https://data.cityofchicago.org/Administration-Finance/Contracts/rsxa-ify5",
  "license": "Public Domain (Chicago Open Data Portal)",
  "retrievedAt": "2025-12-11T00:00:00Z"
}
```

**PROV (YAML):**
```yaml
entity:
  chicago_contracts_dataset:
    prov:type: "prov:Entity"
    dct:title: "City of Chicago Contracts Dataset"
    dct:publisher: "City of Chicago"
    dct:identifier: "https://data.cityofchicago.org/Administration-Finance/Contracts/rsxa-ify5"
    dct:license: "Public Domain (Chicago Open Data Portal)"

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

## Future Datasets

Add additional datasets used for CEP/CEE validation here with their:
- citation information  
- license  
- provenance  
- JSON source descriptor  
