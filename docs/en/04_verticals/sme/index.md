# SME-Friendly Procurement Opportunities

Vertical ID: `sme`  
About file: `docs/en/04_verticals/sme/about.yaml`  
Explanations: `docs/en/04_verticals/sme/explanations.md`

This vertical slice explores how CEP and CEE can identify and explain
**public procurement opportunities that are friendly to small and medium
enterprises (SMEs)**.

The goal is to support **SME access, fair competition, and positive
market development**.

## Who this vertical is for

This example is designed for:

- SME founders and small business owners
- Contracting authorities and procurement officers
- SME support organizations and business associations
- Policy and research teams studying SME participation in procurement

See `about.yaml` for detailed user stories and data-source notes.

## What this vertical demonstrates

- **CEP side**
  - Modeling buyers, tenders, lots, contracts, and suppliers from
    TED/OCDS-like procurement data
  - Relationships:
    - buyer issues tender
    - tender includes lot
    - lot results in contract
    - contract awarded to supplier
  - SNFEI-style identity for buyers, lots, and contracts across sources

- **CEE side**
  - An explanation type: `SME_FRIENDLY_PROCUREMENT`, implemented in
    `civic_interconnect.cee.procurement.sme_explanations`.
  - Answers:
    > Why is this tender or lot highlighted as SME-friendly?
  - Evidence such as:
    - estimated value vs SME thresholds
    - procedure type
    - lot structure and bundling
    - optional historic SME win patterns

## Files in this vertical

- Definition and intent:
  - `docs/en/04_verticals/sme/about.yaml`
  - `docs/en/04_verticals/sme/index.md` (this file)
  - `docs/en/04_verticals/sme/explanations.md`

- Example data (planned structure):
  - `examples/procurement/eu_sme/raw/`
    - Small OCDS-style releases representing EU procurement cases
  - `examples/procurement/eu_sme/cep/`
    - CEP entities and relationships for buyers, tenders, lots, contracts
  - `examples/procurement/eu_sme/cee/`
    - Example `ExplanationBundle` instances for SME-friendly lots

- Tests (planned structure):
  - `src/python/tests/cee/test_procurement_sme_explanations.py`
  - `src/python/tests/adapters/test_procurement_sme_adapter.py`
  - `src/python/tests/examples/test_examples_procurement_eu_sme_roundtrip.py`

## How to read this vertical

1. Start with `about.yaml` for user stories and the SME-access framing.
2. Read `explanations.md` and the `sme_explanations` module to understand
   how SME-friendliness is evaluated and explained.
3. Inspect CEP and CEE example JSON under `examples/procurement/eu_sme/`.
4. Use the test modules as executable documentation of the SME vertical
   slice end-to-end.
