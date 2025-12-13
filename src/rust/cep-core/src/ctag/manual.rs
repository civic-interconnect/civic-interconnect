// Module for manual construction of CTag records
// Path: src/rust/cep-core/src/ctag/manual.rs
//
// Contract:
// - cep-core does NOT manufacture default attestations.
// - Builders MUST reject missing or empty attestations.
// - Attestations are created upstream (adapter/ingest/CLI) and passed in.

use crate::common::attestations::deserialize_nonempty_vec;
use crate::common::errors::{CepResult, map_json_input_error};
use serde::Deserialize;
use serde_json::Value as JsonValue;

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct NormalizedCtagInput {
    // Enforce: present and non-empty.
    // Missing field => serde error "missing field `attestations`".
    // Empty array => custom error from deserialize_nonempty_vec.
    #[serde(deserialize_with = "deserialize_nonempty_vec")]
    attestations: Vec<JsonValue>,
}

/// Temporary stub builder.
///
/// Today: validates input and enforces non-empty attestations, then passes through.
/// TODO: build a fully validated CEP CTag record (envelope + payload).
pub fn build_ctag_from_normalized_json(input_json: &str) -> CepResult<String> {
    let _normalized: NormalizedCtagInput =
        serde_json::from_str(input_json).map_err(map_json_input_error)?;
    let _attestations = &_normalized.attestations;
    Ok(input_json.to_string())
}
