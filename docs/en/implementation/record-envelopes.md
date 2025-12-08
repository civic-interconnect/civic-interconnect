# Common Record Envelope

A shared CEP record envelope is reused for all domains:

- Entity
- Relationship
- Exchange
- CTag

## Attributes

- recordKind is the top-level discriminator: "entity", "relationship", "exchange", "ctag".
- verifiableId is the stable key, never changes once assigned.
- recordTypeUri always points into a vocabulary:
- entity-type, relationship-type, exchange-type, ctag-type, etc.
- timestamps are shared so all records can be compared on the same axes.
- attestations are identical in shape across domains.
  