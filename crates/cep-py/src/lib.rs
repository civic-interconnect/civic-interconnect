// crates/cep-py/src/lib.rs

use cep_core::entity::build_entity_from_normalized_json;
use cep_core::exchange::build_exchange_from_normalized_json;
use cep_core::p3tag::build_p3tag_from_normalized_json;
use cep_core::relationship::build_relationship_from_normalized_json;
use cep_core::entity::resolver::generate_snfei_with_confidence;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

/// Python wrapper around the Rust entity builder.
///
/// Accepts a JSON string for the normalized adapter payload and returns
/// a JSON string containing a full CEP Entity record.
#[pyfunction]
fn build_entity_json(input_json: &str) -> PyResult<String> {
    match build_entity_from_normalized_json(input_json) {
        Ok(output) => Ok(output),
        Err(e) => Err(PyValueError::new_err(e.to_string())),
    }
}

/// Python wrapper around the Rust exchange builder.
///
/// Accepts a JSON string for the normalized adapter payload and returns
/// a JSON string containing a full CEP Exchange record.
#[pyfunction]
fn build_exchange_json(input_json: &str) -> PyResult<String> {
    match build_exchange_from_normalized_json(input_json) {
        Ok(output) => Ok(output),
        Err(e) => Err(PyValueError::new_err(e.to_string())),
    }
}

/// Python wrapper around the Rust relationship builder.
///
/// Accepts a JSON string for the normalized adapter payload and returns
/// a JSON string containing a full CEP Relationship record.
#[pyfunction]
fn build_relationship_json(input_json: &str) -> PyResult<String> {
    match build_relationship_from_normalized_json(input_json) {
        Ok(output) => Ok(output),
        Err(e) => Err(PyValueError::new_err(e.to_string())),
    }
}

/// Python wrapper around the Rust p3tag builder.
///
/// Accepts a JSON string for the normalized adapter payload and returns
/// a JSON string containing a full CEP p3tag record.
#[pyfunction]
fn build_p3tag_json(input_json: &str) -> PyResult<String> {
    match build_p3tag_from_normalized_json(input_json) {
        Ok(output) => Ok(output),
        Err(e) => Err(PyValueError::new_err(e.to_string())),
    }
}

/// Generate an SNFEI from raw attributes using the Rust core SNFEI pipeline.
///
/// Python signature:
///     generate_snfei(
///         legal_name: str,
///         country_code: str,
///         address: str | None = None,
///         registration_date: str | None = None,
///     ) -> str
#[pyfunction]
fn generate_snfei(
    legal_name: &str,
    country_code: &str,
    address: Option<&str>,
    registration_date: Option<&str>,
) -> PyResult<String> {
   // Delegate to the Rust "with confidence" API and map the Result into PyResult.
    // We ignore LEI and SAM UEI here for now (pass None).
    match generate_snfei_with_confidence(
        legal_name,
        country_code,
        address,
        registration_date,
        None,
        None,
    ) {
        Ok(result) => {
            // Return just the 64-character lowercase hex value.
            Ok(result.snfei.as_str().to_string())
        }
        Err(e) => {
            // Propagate as a Python ValueError, not as a "successful" string.
            Err(pyo3::exceptions::PyValueError::new_err(e.to_string()))
        }
    }
}


/// Python module definition.
///
/// This will be imported in Python as:
///
///    import cep_py
///    cep_py.build_entity_json("...json...")
#[pymodule]
fn cep_py(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(build_entity_json, m)?)?;
    m.add_function(wrap_pyfunction!(build_exchange_json, m)?)?;
    m.add_function(wrap_pyfunction!(build_relationship_json, m)?)?;
    m.add_function(wrap_pyfunction!(build_p3tag_json, m)?)?;
    m.add_function(wrap_pyfunction!(generate_snfei, m)?)?;

    Ok(())
}
