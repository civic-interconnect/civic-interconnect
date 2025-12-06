// crates/cep-core/src/relationship/manual.rs

use crate::common::errors::{ CepResult};

pub use super::generated::{
    RelationshipRecord,
    RecordKind,
    StatusEnvelope,
    StatusCode,
    Timestamps,
    Attestation,
};

/// Temporary stub builder for relationships.
///
/// Accepts a normalized JSON string and returns it unchanged.
/// Replace this with real logic once the relationship schema is wired up.
pub fn build_relationship_from_normalized_json(input_json: &str) -> CepResult<String> {
    // For now, just echo back the input to satisfy bindings/tests.
    Ok(input_json.to_string())
}
