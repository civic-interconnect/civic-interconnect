# Exchange Records

An **ExchangeRecord** represents the flow of value between entities. This includes grants, payments, reimbursements, procurement transactions, or any transfer of resources with a defined purpose.

Exchanges are fundamental for understanding public spending, contract chains, and money movement across civic systems.

---

## 1. Structure

| Field | Description |
|-------|-------------|
| `fromEntityId` | Sender of value |
| `toEntityId` | Receiver of value |
| `exchangeTypeUri` | Vocabulary classification of the exchange |
| `amount` | Monetary or unit amount |
| `currency` | ISO 4217 currency code |
| `timestamps` | When the exchange occurred |
| `attestations` | Proofs, metadata, or verification |

The ExchangeRecord inherits the full CEP envelope and hash integrity features.

---

## 2. Exchange Types

Common vocabularies include:

- `#grant`
- `#contract-fee`
- `#payment`
- `#reimbursement`
- `#in-kind-support`

These are governed by CEP vocabulary rules (see `/en/governance/vocabulary-process.md`).

---

## 3. Example ExchangeRecord

```json
{
  "recordKind": "Exchange",
  "exchangeTypeUri": ".../exchange-type.json#grant",
  "fromEntityId": "cep-entity:snfei:abc...",
  "toEntityId": "cep-entity:snfei:def...",
  "amount": 250000,
  "currency": "USD",
  "timestamps": {
    "validFrom": "2024-01-01"
  },
  "attestations": [
    { "attestationTimestamp": "2024-03-05T00:00:00Z", "proofType": "ManualAttestation" }
  ],
  "revisionNumber": 1
}
```

---

## 4. Use Cases

- Federal to State grant flows  
- School district reimbursements  
- Contract payments  
- Campaign to vendor disbursements  
- Nonprofit expenditure chains  

Exchanges form the backbone of **money-flow reconstruction** across civic systems.

---

## 5. Exchange Provenance

Attestations allow:

- Auditable approvals  
- Documentation references  
- Review dates  
- Verification status  

This ensures high-trust public data suitable for transparency and analysis.
