// src/rust/cep-core/src/common/mod.rs

//! Common utilities and types shared across the `cep-core` crate.
//!
//! Purpose
//! -------
//! This module is the shared "spine" of cep-core. Anything that must behave
//! identically across record families (Entity, Relationship, Exchange, CTag)
//! should live here, so that:
//! - there is exactly one authoritative implementation of canonicalization
//!   primitives (normalization, hashing, timestamps, schema resolution);
//! - Rust and Python bindings route through the same logic;
//! - domain modules (entity/, relationship/, exchange/, ctag/) stay focused on
//!   record-family semantics rather than re-implementing shared utilities.
//!
//! Design boundaries
//! -----------------
//! Belongs in common/:
//! - Deterministic normalization primitives used for identity and hashing.
//! - Canonical serialization and hash helpers.
//! - Timestamp utilities and formatting conventions.
//! - Schema registry / schema resolution utilities used by builders/validators.
//! - Shared error types and error mapping helpers.
//! - Localization "pre-normalization" utilities that depend on a jurisdiction key.
//!
//! Does NOT belong in common/:
//! - Domain-specific mapping from raw source data into normalized payloads
//!   (that is adapter responsibility, typically in Python or domain rust).
//! - Record-family assembly rules (how an EntityRecord is built vs an ExchangeRecord).
//! - Any policy choices that are not universal and deterministic.
//!
//! Attestations
//! -----------
//! Attestations are envelope metadata ("who asserted what, how").
//! They are required by the record-envelope schema, but cep-core does not
//! invent attestations. Ingest/adapters/CLI must supply them; cep-core
//! validates shape and carries them into the final record.
//!
//! Key invariants (source-of-truth contracts)
//! -----------------------------------------
//! 1) Normalization source of truth
//!    `common::normalizer` is the single source of truth for normalization and for
//!    building the CanonicalInput used by SNFEI hashing.
//!    No other module should define its own name/address/date normalization pipeline.
//!
//! 2) SNFEI source of truth
//!    `common::snfei` is the single source of truth for SNFEI computation and validation,
//!    and it must only hash CanonicalInput produced by `common::normalizer`.
//!
//! 3) Hashing primitives
//!    Low-level hash utilities (sha256 helpers, canonical byte inputs, etc.) belong in
//!    `common::hash` and are reused by SNFEI and any other hashing needs.
//!
//! 4) Jurisdiction and locality
//!    Jurisdiction-aware rewriting belongs in `common::localization` (pre-normalization).
//!    If jurisdiction is part of an identity hash input, it must be represented explicitly
//!    in CanonicalInput and reflected in the SNFEI hash-string construction.
//!
//! NOTE ON JURISDICTION IN SNFEI
//! ----------------------------
//! Today, `CanonicalInput::to_hash_string()` (as currently implemented) is:
//!   legal_name_normalized|address_normalized|country_code|registration_date
//! If we decide that civic identity requires a finer jurisdiction key (e.g. ISO 3166-2
//! like "US-MN"), that change must happen in exactly two places:
//! - `common::normalizer::CanonicalInput` (add `jurisdiction_iso: Option<String>` or similar)
//! - `common::normalizer::CanonicalInput::to_hash_string()` (include it in the stable position)
//! and then `common::snfei` automatically follows because it hashes `to_hash_string()`.
//!
//! Keeping this wiring explicit is the reason we document the common module here.

/// Embedded or bundled resources needed by core logic (for example, lookup tables
/// used by localization or validation). This should remain deterministic and
/// version-controlled with the crate.
pub mod assets;

/// Attestation types and validation logic shared across record families.
/// Construction of attestations happens outside cep-core.
pub mod attestations;

/// Canonicalization helpers that operate on structured values (for example,
/// canonical JSON representations used for hashing or stable comparisons).
pub mod canonical;

/// Shared Context Tag (CTag) helpers used by record families. Record-family-specific
/// CTag assembly logic belongs in the top-level ctag/ module; shared primitives belong here.
pub mod ctag;

/// Shared error types and error mapping utilities used across cep-core.
pub mod errors;

/// Hash primitives (sha256 helpers, canonical byte-string construction, etc.).
/// SNFEI and any other hashed identifiers should depend on this layer.
pub mod hash;

/// Jurisdiction-aware rewriting / localization ("pre-normalization") that should run
/// before universal normalization when a jurisdiction key is available.
pub mod localization;

/// Universal normalization pipeline and canonical input construction.
/// This is the single source of truth for:
/// - normalize_legal_name
/// - normalize_address
/// - normalize_registration_date
/// - CanonicalInput (and its to_hash_string)
pub mod normalizer;

/// Schema resolution and registry utilities used by builders and validators.
pub mod schema_registry;

/// SNFEI computation and validation. This must hash ONLY the canonical input string
/// produced by common::normalizer (CanonicalInput::to_hash_string()).
pub mod snfei;

/// Timestamp and time-format utilities shared across record families.
pub mod timestamp;
