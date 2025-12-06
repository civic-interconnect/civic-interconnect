// crates/cep-core/src/entity/manual.rs

use crate::common::errors::{CepError, CepResult};
use serde::{Deserialize, Serialize};
use serde_json;

// Re-export generated types you want applications to use.
pub use super::generated::{
    Attestation,
    EntityRecord,
    RecordKind,
    StatusCode,
    StatusEnvelope,
    Timestamps,
    Identifiers,
};

impl EntityRecord {
    pub fn is_active(&self) -> bool {
        matches!(self.status.status_code, StatusCode::Active)
    }
}

/// Normalized input payload from adapters.
///
/// This is the “builder input” your Python / ETL side will emit.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NormalizedEntityInput {
    #[serde(rename = "jurisdictionIso")]
    pub jurisdiction_iso: String,

    #[serde(rename = "legalName")]
    pub legal_name: String,

    #[serde(rename = "legalNameNormalized")]
    pub legal_name_normalized: String,

    #[serde(rename = "snfei")]
    pub snfei: String,

    /// Logical entity type (e.g. "federal-agency", "nonprofit-501c3").
    /// Used to derive an entityTypeUri / recordTypeUri.
    #[serde(rename = "entityType")]
    pub entity_type: String,
}

/// Public entry point used by FFI / Python.
///
/// Accepts a JSON string containing the normalized adapter payload,
/// returns a JSON string representing a full CEP `EntityRecord`.
pub fn build_entity_from_normalized_json(input_json: &str) -> CepResult<String> {
    let normalized: NormalizedEntityInput = serde_json::from_str(input_json)
        .map_err(|e| CepError::InvalidJson(e.to_string()))?;

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
        // You can change this to a dedicated record-type vocabulary later.
        record_type_uri: entity_type_uri(&input.entity_type),

        status: default_status_envelope(),
        timestamps: default_timestamps(),
        attestations: vec![default_ingest_attestation()],

        // Domain-specific fields
        jurisdiction_iso: input.jurisdiction_iso,
        legal_name: input.legal_name,
        short_name: None,

        identifiers: Some(build_identifiers_snfei(&input.snfei)),

        // These can be filled later by upstream systems if desired.
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
vocabulary/entity-type.json#";

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
        verification_method_uri:
            "urn:cep:attestor:cep-entity:example:ingest".to_string(),
        proof_type: "ManualAttestation".to_string(),
        proof_purpose: "assertionMethod".to_string(),
        proof_value: None,
        source_system: None,
        source_reference: None,
    }
}

/// Build the nested identifiers map:
/// { "snfei": { "value": "<hash>" } }
fn build_identifiers_snfei(snfei: &str) -> Identifiers {
    use std::collections::HashMap;

    let mut inner = HashMap::new();
    inner.insert("value".to_string(), snfei.to_string());

    let mut outer = HashMap::new();
    outer.insert("snfei".to_string(), inner);

    outer
}
