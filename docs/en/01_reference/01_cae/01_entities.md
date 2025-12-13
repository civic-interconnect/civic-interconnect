# CAE Entities

This page defines the six CAE entity kinds and the boundary conditions that keep the partition disjoint.

CAE entity kinds:

Actors (A)
Sites (S)
Instruments (I)
Events (E)
Jurisdictions (J)
Observables (O)

---

## Actors (A)

Actors are entities that can bear accountability-relevant participation.

Actors include persons, organizations, public bodies, and collective entities when treated as participants in civic processes.

Actors are not defined by legal form. They are defined by their role as participants that can be referenced across records.

---

## Sites (S)

Sites are entities that represent where something is situated.

Sites include addresses, parcels, facilities, jurisdictions-as-places when treated as locations, and other location-bearing entities.

Sites are not events and do not act. They are referents for spatial attribution.

---

## Instruments (I)

Instruments are entities that mediate action, authority, or obligation.

Instruments include permits, contracts, licenses, grants, programs, policies, regulations, and other artifacts that structure what can be done or what is required.

An instrument may be created, modified, or terminated by events, but it is not itself an event.

---

## Events (E)

Events are entities that occur in time.

Events include actions, decisions, filings, transactions, inspections, adjudications, transfers, and other time-indexed occurrences.

Events are the primary anchor for provenance and sequencing. An event may involve actors, sites, and instruments.

---

## Jurisdictions (J)

Jurisdictions are entities that define scope of authority and governance context.

Jurisdictions include governmental units and other authority-bearing contexts, treated as normative scopes rather than physical locations.

A jurisdiction may also have a geographic footprint, but in CAE that footprint is represented via Sites when location is the concern.

---

## Observables (O)

Observables are entities that represent measured or reported values and indicators.

Observables include metrics, measurements, scores, rates, counts, environmental readings, and other reportable quantities.

Observables are not explanations. They are the kinds of things explanations may refer to.

---

## Disjointness Rules

The partition is maintained by intent and usage:

- If something is primarily "a participant", it is an Actor.
- If something is primarily "a place", it is a Site.
- If something is primarily "a governing scope", it is a Jurisdiction.
- If something is primarily "a mediating artifact", it is an Instrument.
- If something is primarily "a happening", it is an Event.
- If something is primarily "a measured value", it is an Observable.

CAE does not require the world to fit perfectly. It requires a stable choice so systems can interoperate without reclassifying entities as interpretations evolve.
