// src/rust/cep-core/src/entity/manual.rs
//
// Contract:
// - cep-core does NOT manufacture default attestations.
// - Builders MUST reject missing or empty attestations.
// - Attestations are created upstream (adapter/ingest/CLI) and passed in.

use super::identifiers::SNFEI_SCHEME_URI;
use crate::common::attestations::deserialize_nonempty_vec;
use crate::common::errors::{CepError, CepResult, map_json_input_error};
use serde::Deserialize;

// Keep entity type URI generation in one place so recordTypeUri stays consistent.
pub(crate) const ENTITY_TYPE_VOCAB_URI_BASE: &str = "https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabulary/core/entity-type.v1.0.0.json#";

// Re-export generated types for Python use.
pub use super::generated::{
    Attestation, EntityRecord, Identifier, Identifiers, RecordKind, StatusCode, StatusEnvelope,
    Timestamps,
};

impl EntityRecord {
    pub fn is_active(&self) -> bool {
        matches!(self.status.status_code, StatusCode::Active)
    }
}

/// Normalized input payload from adapters.
///
/// This is the builder input the Python / ETL side will emit.
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NormalizedEntityInput {
    /// Logical entity type (for example: "school_district", "federal_agency").
    /// Used to derive recordTypeUri (and, if present in your schema, entityTypeUri).
    pub entity_type: String,

    pub jurisdiction_iso: String,

    pub legal_name: String,

    pub legal_name_normalized: Option<String>,

    pub snfei: String,

    // Enforce: present and non-empty.
    // Missing field => serde error "missing field `attestations`".
    // Empty array => custom error from deserialize_nonempty_vec.
    #[serde(deserialize_with = "deserialize_nonempty_vec")]
    pub attestations: Vec<Attestation>,
}

/// Public entry point used by FFI / Python.
///
/// Accepts a JSON string containing the normalized adapter payload,
/// returns a JSON string representing a CEP EntityRecord.
///
/// Today: enforces attestations presence/non-empty and builds a record.
/// Later: add full schema validation + canonicalization as needed.
pub fn build_entity_from_normalized_json(input_json: &str) -> CepResult<String> {
    let normalized: NormalizedEntityInput =
        serde_json::from_str(input_json).map_err(map_json_input_error)?;

    let record = build_entity_from_normalized(normalized);

    serde_json::to_string(&record).map_err(|e| CepError::BuilderError(e.to_string()))
}

/// Internal helper: map NormalizedEntityInput to EntityRecord.
/// Keep wiring in one place.
fn build_entity_from_normalized(input: NormalizedEntityInput) -> EntityRecord {
    let et_uri = entity_type_uri(&input.entity_type);

    EntityRecord {
        // Envelope-level / structural fields
        record_kind: RecordKind::Entity,
        record_schema_uri: entity_record_schema_uri(),
        schema_version: "1.0.0".to_string(),
        revision_number: 1,

        verifiable_id: format!("cep-entity:snfei:{}", input.snfei),

        // Keep recordTypeUri consistent by deriving from the same function.
        record_type_uri: et_uri,

        status: default_status_envelope(),
        timestamps: default_timestamps(),

        // Option A: MUST come from upstream; do not manufacture in core.
        attestations: input.attestations,

        ctags: None,

        // Domain-specific fields
        jurisdiction_iso: input.jurisdiction_iso,
        legal_name: input.legal_name,
        legal_name_normalized: input.legal_name_normalized,
        short_name: None,

        identifiers: Some(build_identifiers_snfei(&input.snfei)),

        // Filled later by upstream systems as desired.
        inception_date: None,
        dissolution_date: None,

        // Lifecycle wiring (present in generated type; left unset for now).
        status_termination_date: None,
        successor_entity_id: None,
    }
}

// ---------- Helpers / defaults ----------

fn entity_record_schema_uri() -> String {
    "https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/schemas/core/cep.entity.schema.json"
        .to_string()
}

/// Normalize an entity-type token into a kebab-case vocabulary fragment.
///
/// Examples:
/// - "school_district" -> "school-district"
/// - "School District" -> "school-district"
/// - "school-district" -> "school-district"
fn entity_type_fragment(entity_type: &str) -> String {
    let mut out = String::new();
    let mut prev_dash = false;

    for ch in entity_type.trim().chars() {
        let c = ch.to_ascii_lowercase();
        let is_sep = c == '_' || c == '-' || c.is_whitespace();

        if is_sep {
            if !out.is_empty() && !prev_dash {
                out.push('-');
                prev_dash = true;
            }
            continue;
        }

        if c.is_ascii_alphanumeric() {
            out.push(c);
            prev_dash = false;
            continue;
        }

        // Any other punctuation becomes a separator
        if !out.is_empty() && !prev_dash {
            out.push('-');
            prev_dash = true;
        }
    }

    while out.ends_with('-') {
        out.pop();
    }

    out
}

/// Build the entity-type URI from a short code, for example "school_district".
fn entity_type_uri(entity_type: &str) -> String {
    let frag = entity_type_fragment(entity_type);
    format!("{}{}", ENTITY_TYPE_VOCAB_URI_BASE, frag)
}

fn default_status_envelope() -> StatusEnvelope {
    StatusEnvelope {
        status_code: StatusCode::Active,
        status_reason: None,
        status_effective_date: "1900-01-01".to_string(),
    }
}

fn default_timestamps() -> Timestamps {
    let ts = "1900-01-01T00:00:00.000000Z".to_string();
    Timestamps {
        first_seen_at: ts.clone(),
        last_updated_at: ts.clone(),
        valid_from: ts,
        valid_to: None,
    }
}

/// Build the identifiers array using the CEP Identifier Scheme vocabulary.
fn build_identifiers_snfei(snfei: &str) -> Identifiers {
    vec![Identifier {
        scheme_uri: SNFEI_SCHEME_URI.to_string(),
        identifier: snfei.to_string(),
        source_reference: None,
    }]
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::{Value, json};

    fn assert_minimal_status_shape(status: &Value) {
        assert_eq!(status["statusCode"], Value::String("ACTIVE".to_string()));
        assert_eq!(
            status["statusEffectiveDate"],
            Value::String("1900-01-01".to_string())
        );
    }

    fn one_attestation_json() -> Value {
        json!({
            "attestationTimestamp": "1900-01-01T00:00:00.000000Z",
            "attestorId": "cep-entity:example:ingest",
            "verificationMethodUri": "urn:cep:attestor:cep-entity:example:ingest",
            "proofType": "ManualAttestation",
            "proofPurpose": "assertionMethod",
            "proofValue": null,
            "sourceSystem": null,
            "sourceReference": null
        })
    }

    #[test]
    fn entity_type_fragment_normalizes() {
        assert_eq!(entity_type_fragment("school_district"), "school-district");
        assert_eq!(entity_type_fragment("School District"), "school-district");
        assert_eq!(entity_type_fragment("school-district"), "school-district");
        assert_eq!(
            entity_type_fragment("  school__district  "),
            "school-district"
        );
    }

    #[test]
    fn school_district_vertical_slice_minimal() {
        let snfei_64 = "deadbeef".repeat(8);

        let input = json!({
            "jurisdictionIso": "US-MN",
            "legalName": "Springfield Public Schools",
            "legalNameNormalized": "springfield public schools",
            "snfei": snfei_64,
            "entityType": "school_district",
            "attestations": [ one_attestation_json() ]
        });

        let input_json = serde_json::to_string(&input).expect("to_string should not fail");
        let output_json =
            build_entity_from_normalized_json(&input_json).expect("builder should succeed");

        let entity: Value = serde_json::from_str(&output_json).expect("output must be valid JSON");

        assert_eq!(entity["schemaVersion"], Value::String("1.0.0".to_string()));
        assert_eq!(
            entity["jurisdictionIso"],
            Value::String("US-MN".to_string())
        );
        assert_eq!(
            entity["legalName"],
            Value::String("Springfield Public Schools".to_string())
        );

        let status = entity.get("status").expect("status block must be present");
        assert_minimal_status_shape(status);

        let rt = entity["recordTypeUri"]
            .as_str()
            .expect("recordTypeUri must be a string");
        assert!(rt.contains("vocabulary/core/entity-type.v1.0.0.json#school-district"));

        // Enforced and preserved:
        assert!(entity["attestations"].as_array().unwrap().len() >= 1);
    }

    #[test]
    fn missing_attestations_is_rejected() {
        let snfei_64 = "deadbeef".repeat(8);

        let input = json!({
            "jurisdictionIso": "US-MN",
            "legalName": "Springfield Public Schools",
            "legalNameNormalized": "springfield public schools",
            "snfei": snfei_64,
            "entityType": "school_district"
        });

        let input_json = serde_json::to_string(&input).expect("to_string should not fail");
        let err = build_entity_from_normalized_json(&input_json).unwrap_err();
        let msg = err.to_string();
        assert!(msg.contains("missing field") || msg.contains("attestations"));
    }

    #[test]
    fn empty_attestations_is_rejected() {
        let snfei_64 = "deadbeef".repeat(8);

        let input = json!({
            "jurisdictionIso": "US-MN",
            "legalName": "Springfield Public Schools",
            "legalNameNormalized": "springfield public schools",
            "snfei": snfei_64,
            "entityType": "school_district",
            "attestations": []
        });

        let input_json = serde_json::to_string(&input).expect("to_string should not fail");
        let err = build_entity_from_normalized_json(&input_json).unwrap_err();
        let msg = err.to_string();
        assert!(msg.contains("attestations must contain at least 1 item"));
    }
}
