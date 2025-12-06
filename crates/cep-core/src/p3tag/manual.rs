use crate::common::errors::{ CepResult};

/// Temporary stub builder for P3Tag records.
pub fn build_p3tag_from_normalized_json(input_json: &str) -> CepResult<String> {
    Ok(input_json.to_string())
}
