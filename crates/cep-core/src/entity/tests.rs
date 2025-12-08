// crates/cep-core/src/entity/tests.rs
// run with
// cargo test -p cep-core entity

use super::normalizer::normalize_legal_name;
use super::*;
use serde_json;

/// Basic sanity check: normalized input -> EntityRecord with our defaults.
#[test]
fn build_entity_from_normalized_json_produces_entity_record() {
    let input_json = r#"{
        "jurisdictionIso": "US-MN",
        "legalName": "Example School District 123",
        "legalNameNormalized": "example school district 123",
        "snfei": "34486b382c620747883952d6fb4c0ccdbf25388dfb0bb99231f33a93ad5ca5b3",
        "entityType": "educational-institution"
    }"#;

    let out_json = build_entity_from_normalized_json(input_json).expect("builder should succeed");

    let record: EntityRecord =
        serde_json::from_str(&out_json).expect("output should be valid EntityRecord JSON");

    // Envelope-level checks
    assert!(record.is_active());
    assert!(matches!(record.record_kind, RecordKind::Entity));
    assert_eq!(
        record.record_schema_uri,
        "https://raw.githubusercontent.com/\
civic-interconnect/civic-interconnect/main/\
schemas/cep.entity.schema.json"
    );
    assert_eq!(record.schema_version, "1.0.0");
    assert_eq!(record.revision_number, 1);

    // ID and type wiring
    assert_eq!(
        record.verifiable_id,
        "cep-entity:snfei:34486b382c620747883952d6fb4c0ccdbf25388dfb0bb99231f33a93ad5ca5b3"
    );
    assert_eq!(
        record.record_type_uri,
        "https://raw.githubusercontent.com/\
civic-interconnect/civic-interconnect/main/\
vocabularies/entity-type.json#educational-institution"
    );

    // Domain fields
    assert_eq!(record.jurisdiction_iso, "US-MN");
    assert_eq!(record.legal_name, "Example School District 123");

    // identifiers must contain an SNFEI entry with the expected value.
    let ids = record
        .identifiers
        .as_ref()
        .expect("identifiers should be present");

    let snfei_identifier = ids
        .iter()
        .find(|id| {
            id.scheme_uri
                == "https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabularies/entity-identifier-scheme.v1.0.0.json#snfei"
        })
        .expect("snfei identifier should exist");

    assert_eq!(
        snfei_identifier.identifier,
        "34486b382c620747883952d6fb4c0ccdbf25388dfb0bb99231f33a93ad5ca5b3"
    );
}

/// Timestamps and attestation defaults are at least present and non-empty where required.
#[test]
fn build_entity_sets_basic_envelope_defaults() {
    let input_json = r#"{
        "jurisdictionIso": "US-MN",
        "legalName": "Minimal Entity",
        "legalNameNormalized": "minimal entity",
        "snfei": "abc123",
        "entityType": "federal-agency"
    }"#;

    let out_json = build_entity_from_normalized_json(input_json).expect("builder should succeed");

    let record: EntityRecord =
        serde_json::from_str(&out_json).expect("output should be valid EntityRecord JSON");

    // Status defaults
    assert!(matches!(record.status.status_code, StatusCode::Active));
    assert!(!record.status.status_effective_date.is_empty());

    // Timestamps defaults
    assert!(!record.timestamps.first_seen_at.is_empty());
    assert!(!record.timestamps.last_updated_at.is_empty());
    assert!(!record.timestamps.valid_from.is_empty());

    // Attestations: at least one default attestation
    assert!(!record.attestations.is_empty());
}

#[test]
fn normalize_french_name_societe_generale() {
    let normalized =
        crate::entity::normalizer::normalize_legal_name("Societe Generale S.A.", true, false);
    assert_eq!(normalized, "societe generale societe anonyme");
}

#[test]
fn normalize_greek_name_preserves_script() {
    // "Ελληνική Εταιρεία Δεδομένων"
    let raw = concat!(
        "\u{0395}\u{03BB}\u{03BB}\u{03B7}\u{03BD}\u{03B9}\u{03BA}\u{03AE}", // Ελληνική
        " ",
        "\u{0395}\u{03C4}\u{03B1}\u{03B9}\u{03C1}\u{03B5}\u{03AF}\u{03B1}", // Εταιρεία
        " ",
        "\u{0394}\u{03B5}\u{03B4}\u{03BF}\u{03BC}\u{03AD}\u{03BD}\u{03C9}\u{03BD}", // Δεδομένων
    );

    let normalized = normalize_legal_name(raw, true, false);

    assert!(!normalized.is_empty());
    assert!(normalized.chars().any(|c| !c.is_ascii()));
}

#[test]
fn normalize_german_legal_form_gmbh() {
    // "GmbH & Co. KG"
    let raw = "GmbH & Co. KG";
    let normalized = normalize_legal_name(raw, true, false);

    // Given LEGAL_SUFFIX_EXPANSIONS has:
    //   "gmbh" -> "gesellschaft mit beschrankter haftung"
    // and COMMON_ABBREVIATIONS / STOP_WORDS as in normalizer.rs,
    // we expect:
    assert_eq!(
        normalized,
        "gesellschaft mit beschrankter haftung company kg"
    );
}

#[test]
fn canonical_input_hash_string_international_example() {
    let canonical = crate::entity::normalizer::build_canonical_input(
        "Societe Generale S.A.",
        "FR",
        Some("10 Boulevard Haussmann, Paris"),
        Some("2010-05-01"),
    );

    let hash_input = canonical.to_hash_string();

    assert_eq!(
        hash_input,
        "societe generale societe anonyme|10 boulevard haussmann paris|FR|2010-05-01"
    );
}
