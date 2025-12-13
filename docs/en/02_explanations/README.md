# How These Parts Fit Together

This document explains how the major parts of the system relate to one another.

Each part is defined independently. None requires the others to exist.
They can be adopted, implemented, or criticized separately.

This page exists only to explain how they align when used together.

---

## Overview

The system is organized as layered concerns:

-   What civic things are
-   How civic data is structured
-   How meaning is derived
-   How confidence is asserted

Each layer answers a different question.

No layer determines truth.

---

## CAE: Civic and Administrative Entities

CAE defines civic and administrative concepts as they exist in the world.

It answers:

What kinds of things exist, and what roles or authority they have.

CAE does not define data formats, processing rules, or interpretations.
It can be understood without knowing anything about CEP or CEE.

---

## CEP: Civic Exchange Protocol

CEP defines how civic data is structured and exchanged.

It answers:

How information about civic entities, relationships, and exchanges is represented
in a consistent, verifiable form.

CEP does not interpret meaning, assess impact, or resolve disputes.

---

## CEE: Contextual Evidence and Explanations

CEE defines how observations are connected to explanations and models.

It answers:

Why a claim is made, what evidence supports it, and how reasoning is structured.

CEE does not enforce correctness or consensus.

---

## Assurance

Assurance defines how claims of confidence are recorded.

It answers:

Who asserts that something holds, under what conditions, and based on what basis.

Assurance does not decide trustworthiness.

---

## Separation of Concerns

Each layer can disagree with the others.

A system may have:

-   Correct structure but contested interpretation
-   Strong explanations but weak assurance
-   High assurance over incomplete data

These conditions are preserved, not resolved.

---

## Why This Structure Exists

The goal is not agreement.

The goal is traceability:

-   of structure
-   of interpretation
-   of confidence

This allows disagreement to be explicit, inspectable, and durable.

---

This page explains alignment, not authority.
