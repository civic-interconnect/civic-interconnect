// crates/cep-core/src/entity/manual.rs

use crate::common::errors::{CepError, CepResult};
use serde::{Deserialize, Serialize};
use serde_json;

pub(crate) const SNFEI_SCHEME_URI: &str = "https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabulary/core/entity-identifier-scheme.v1.0.0.json#snfei";

// Re-export generated types you want applications to use.
pub use super::generated::{
    Attestation, EntityRecord, Identifier, Identifiers, RecordKind, StatusCode, StatusEnvelope,
    Timestamps,
};

impl EntityRecord {
    pub fn is_active(&self) -> bool {
        matches!(self.status.status_code, StatusCode::Active)
    }
}

impl From<(&str, &str)> for Identifier {
    fn from((scheme_uri, value): (&str, &str)) -> Self {
        Identifier {
            scheme_uri: scheme_uri.to_string(),
            identifier: value.to_string(),
            source_reference: None,
        }
    }
}

/// Normalized input payload from adapters.
///
/// This is the builder input the Python / ETL side will emit.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NormalizedEntityInput {
    /// Logical entity type (e.g. "federal-agency", "nonprofit-501c3").
    /// Used to derive an entityTypeUri / recordTypeUri.
    #[serde(rename = "entityType")]
    pub entity_type: String,

    #[serde(rename = "jurisdictionIso")]
    pub jurisdiction_iso: String,

    #[serde(rename = "legalName")]
    pub legal_name: String,

    #[serde(rename = "legalNameNormalized")]
    pub legal_name_normalized: Option<String>,

    #[serde(rename = "snfei")]
    pub snfei: String,
}

/// Public entry point used by FFI / Python.
///
/// Accepts a JSON string containing the normalized adapter payload,
/// returns a JSON string representing a full CEP `EntityRecord`.
pub fn build_entity_from_normalized_json(input_json: &str) -> CepResult<String> {
    let normalized: NormalizedEntityInput =
        serde_json::from_str(input_json).map_err(|e| CepError::InvalidJson(e.to_string()))?;

    let record = build_entity_from_normalized(normalized);

    serde_json::to_string(&record).map_err(|e| CepError::BuilderError(e.to_string()))
}

/// Internal helper: map NormalizedEntityInput → EntityRecord.
/// Keeps all the wiring in one place so you can test it directly.
fn build_entity_from_normalized(input: NormalizedEntityInput) -> EntityRecord {
    EntityRecord {
        // Envelope-level / structural fields
        record_kind: RecordKind::Entity,
        record_schema_uri: entity_record_schema_uri(),
        schema_version: "1.0.0".to_string(),
        revision_number: 1,

        verifiable_id: format!("cep-entity:snfei:{}", input.snfei),

        // For now, treat the entity type as the record type URI anchor.
        // Can change to a dedicated record-type vocabulary later.
        record_type_uri: entity_type_uri(&input.entity_type),

        status: default_status_envelope(),
        status_termination_date: None,
        successor_entity_id: None,
        timestamps: default_timestamps(),
        attestations: vec![default_ingest_attestation()],

        // Domain-specific fields
        jurisdiction_iso: input.jurisdiction_iso,
        legal_name: input.legal_name,
        legal_name_normalized: input.legal_name_normalized,
        short_name: None,

        identifiers: Some(build_identifiers_snfei(&input.snfei)),
        ctags: None,

        // Filled later by upstream systems as desired.
        inception_date: None,
        dissolution_date: None,
    }
}

// ---------- Small helpers / defaults ----------

fn entity_record_schema_uri() -> String {
    "https://raw.githubusercontent.com/\
civic-interconnect/civic-interconnect/main/\
schemas/cep.entity.schema.json"
        .to_string()
}

/// Build the entity-type URI from a short code, e.g. "federal-agency".
fn entity_type_uri(entity_type: &str) -> String {
    let base = "https://raw.githubusercontent.com/\
civic-interconnect/civic-interconnect/main/\
vocabularies/entity-type.json#";

    format!("{}{}", base, entity_type.replace(' ', "-"))
}

fn default_status_envelope() -> StatusEnvelope {
    StatusEnvelope {
        status_code: StatusCode::Active,
        status_reason: None,
        // You can swap this to a canonical "now" helper later.
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

/// Default ingest attestation matching the CEP examples.
/// You can later parameterize this (different attestors, timestamps, etc.).
fn default_ingest_attestation() -> Attestation {
    Attestation {
        attestation_timestamp: "1900-01-01T00:00:00.000000Z".to_string(),
        attestor_id: "cep-entity:example:ingest".to_string(),
        verification_method_uri: "urn:cep:attestor:cep-entity:example:ingest".to_string(),
        proof_type: "ManualAttestation".to_string(),
        proof_purpose: "assertionMethod".to_string(),
        proof_value: None,
        source_system: None,
        source_reference: None,
    }
}

/// Build the identifiers array using the CEP Identifier Scheme vocabulary.
///
/// Produces:
/// [
///   {
///     "schemeUri": "https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabulary/entity-identifier-scheme.v1.0.0.json#snfei",
///     "identifier": "<hash>",
///     "sourceReference": null
///   }
/// ]
fn build_identifiers_snfei(snfei: &str) -> Identifiers {
    vec![Identifier {
        scheme_uri: SNFEI_SCHEME_URI.to_string(),
        identifier: snfei.to_string(),
        source_reference: None,
    }]
}

#[cfg(test)]
mod tests {
    use super::SNFEI_SCHEME_URI;
    use super::*;
    use serde_json::{Value, json};

    fn assert_minimal_status_shape(status: &Value) {
        // Always required
        assert_eq!(status["statusCode"], Value::String("ACTIVE".to_string()));
        assert_eq!(
            status["statusEffectiveDate"],
            Value::String("1900-01-01".to_string())
        );

        // Optional fields: allow either missing or explicit null.
        if let Some(v) = status.get("statusTerminationDate") {
            assert!(
                v.is_null(),
                "statusTerminationDate must be null if present in minimal entities"
            );
        }

        if let Some(v) = status.get("successorEntityId") {
            assert!(
                v.is_null(),
                "successorEntityId must be null if present in minimal entities"
            );
        }
    }

    #[test]
    fn school_district_vertical_slice_minimal() {
        // 1. Normalized input (what adapters + localization would produce)
        let input = json!({
            "jurisdictionIso": "US-MN",
            "legalName": "Springfield Public Schools",
            "legalNameNormalized": "springfield public schools",
            "snfei": "deadbeefcafebabe0011223344556677",
            "entityType": "school_district"
        });

        let input_json = serde_json::to_string(&input).expect("to_string should not fail");

        // 2. Run through the builder (which includes validation)
        let output_json_1 =
            build_entity_from_normalized_json(&input_json).expect("builder should succeed");

        // 3. Parse back to JSON
        let entity_1: Value =
            serde_json::from_str(&output_json_1).expect("output must be valid JSON");

        // 4. Basic shape sanity checks
        assert_eq!(
            entity_1["schemaVersion"],
            Value::String("1.0.0".to_string())
        );
        assert_eq!(
            entity_1["jurisdictionIso"],
            Value::String("US-MN".to_string())
        );
        assert_eq!(
            entity_1["legalName"],
            Value::String("Springfield Public Schools".to_string())
        );
        assert_eq!(
            entity_1["legalNameNormalized"],
            Value::String("springfield public schools".to_string())
        );

        // 5. Stable ID check: verifiableId based on SNFEI should be deterministic
        let verifiable_id_1 = entity_1["verifiableId"]
            .as_str()
            .expect("verifiableId must be a string")
            .to_owned();

        // Call the builder again with the same normalized payload
        let output_json_2 =
            build_entity_from_normalized_json(&input_json).expect("builder should succeed again");
        let entity_2: Value =
            serde_json::from_str(&output_json_2).expect("second output must be valid JSON");
        let verifiable_id_2 = entity_2["verifiableId"]
            .as_str()
            .expect("verifiableId must be a string");

        assert_eq!(
            verifiable_id_1, verifiable_id_2,
            "verifiableId must be stable for identical normalized input"
        );

        // 6. Inception date is optional: for this minimal slice it must not be a non-null date.
        // Allow either missing OR explicitly null.
        if let Some(v) = entity_1.get("inceptionDate") {
            assert!(
                v.is_null(),
                "inceptionDate must be null if present for minimal entities"
            );
        }

        // 7. Status should be present and active (matches current builder behavior)
        let status = entity_1
            .get("status")
            .expect("status block must be present");

        assert_minimal_status_shape(status);
    }

    #[test]
    fn snfei_scheme_uri_matches_vocabulary_term() {
        use serde_json::Value;
        use std::fs;
        use std::path::PathBuf;

        // Build path to: <repo-root>/vocabulary/core/entity-identifier-scheme.v1.0.0.json
        let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        path.push("..");
        path.push("..");
        path.push("vocabulary");
        path.push("core");
        path.push("entity-identifier-scheme.v1.0.0.json");

        let text = fs::read_to_string(&path)
            .unwrap_or_else(|e| panic!("failed to read vocab file {:?}: {}", path, e));

        let json: Value =
            serde_json::from_str(&text).expect("vocabulary file should be valid JSON");

        let terms = json
            .get("terms")
            .and_then(|v| v.as_array())
            .expect("vocabulary should contain a terms array");

        let snfei_term = terms
            .iter()
            .find(|term| term.get("code").and_then(Value::as_str) == Some("snfei"))
            .expect("vocabulary should contain a term with code 'snfei'");

        let term_uri = snfei_term
            .get("termUri")
            .and_then(Value::as_str)
            .expect("snfei term should have a termUri");

        assert_eq!(
            term_uri, SNFEI_SCHEME_URI,
            "SNFEI_SCHEME_URI constant must match vocabulary termUri"
        );
    }
}
