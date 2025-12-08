use crate::common::errors::CepResult;

/// Temporary stub builder for CTag records.
pub fn build_ctag_from_normalized_json(input_json: &str) -> CepResult<String> {
    Ok(input_json.to_string())
}
