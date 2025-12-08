/// Python FFI (Foreign Function Interface) for CEP functionality.
/// Exposes Rust CEP builders and utilities to Python via PyO3.
/// Thin wrappers around core Rust functions.
/// No business logic here; just error mapping and type conversion.
/// Path: crates/cep-py/src/lib.rs
use cep_core::ctag::build_ctag_from_normalized_json;
use cep_core::entity::build_entity_from_normalized_json;
use cep_core::exchange::build_exchange_from_normalized_json;
use cep_core::relationship::build_relationship_from_normalized_json;

// SNFEI and normalization from the common core
use cep_core::common::normalizer::{
    normalize_address, normalize_legal_name, normalize_registration_date,
};
use cep_core::common::snfei::{generate_snfei_with_confidence, SnfeiResult};

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use serde_json;

/// Python wrapper around the Rust CTag builder.
///
/// Accepts a JSON string for the normalized adapter payload and returns
/// a JSON string containing a full CEP Context Tag record.
#[pyfunction]
fn build_ctag_json(input_json: &str) -> PyResult<String> {
    match build_ctag_from_normalized_json(input_json) {
        Ok(output) => Ok(output),
        Err(e) => Err(PyValueError::new_err(e.to_string())),
    }
}

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
    // Core function returns SnfeiResult, not Result<SnfeiResult, E>.
    let result = generate_snfei_with_confidence(
        legal_name,
        country_code,
        address,
        registration_date,
        None,
        None,
    );

    // Expose just the hex string to Python
    Ok(result.snfei.value().to_string())
}

/// Generate an SNFEI and return full pipeline metadata as JSON.
///
/// Python signature:
///     generate_snfei_detailed(
///         legal_name: str,
///         country_code: str,
///         address: str | None = None,
///         registration_date: str | None = None,
///     ) -> str
///
/// The returned string is a JSON object with fields:
/// {
///   "snfei": { "value": "..." },
///   "canonical": { ... },
///   "confidence_score": 0.87,
///   "tier": 3,
///   "fields_used": ["legal_name", "country_code", ...]
/// }
#[pyfunction]
fn generate_snfei_detailed(
    legal_name: &str,
    country_code: &str,
    address: Option<&str>,
    registration_date: Option<&str>,
) -> PyResult<String> {
    let result: SnfeiResult = generate_snfei_with_confidence(
        legal_name,
        country_code,
        address,
        registration_date,
        None,
        None,
    );

    serde_json::to_string(&result).map_err(|e| PyValueError::new_err(e.to_string()))
}

/// Normalize a legal name via the Rust Normalizing Functor.
///
/// Python:
///     normalize_legal_name(value: str) -> str
#[pyfunction(name = "normalize_legal_name")]
fn py_normalize_legal_name(value: &str) -> PyResult<String> {
    Ok(normalize_legal_name(value))
}

/// Normalize an address via the Rust Normalizing Functor.
///
/// Python:
///     normalize_address(value: str) -> str
#[pyfunction(name = "normalize_address")]
fn py_normalize_address(value: &str) -> PyResult<String> {
    Ok(normalize_address(value))
}

/// Normalize a registration date using the CEP core normalizer.
///
/// Python signature:
///     normalize_registration_date(value: str) -> str | None
///
/// Returns:
///   - a normalized ISO date string (e.g. "2020-01-31"), or
///   - None if the value cannot be normalized.
#[pyfunction]
fn normalize_registration_date_py(value: &str) -> PyResult<Option<String>> {
    Ok(normalize_registration_date(value))
}

/// Python module definition.
///
/// This will be imported in Python as:
///
///    import cep_py
///    cep_py.build_entity_json("...json...")
#[pymodule]
fn cep_py(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(build_ctag_json, m)?)?;
    m.add_function(wrap_pyfunction!(build_entity_json, m)?)?;
    m.add_function(wrap_pyfunction!(build_exchange_json, m)?)?;
    m.add_function(wrap_pyfunction!(build_relationship_json, m)?)?;

    m.add_function(wrap_pyfunction!(generate_snfei, m)?)?;
    m.add_function(wrap_pyfunction!(generate_snfei_detailed, m)?)?;

    m.add_function(wrap_pyfunction!(py_normalize_legal_name, m)?)?;
    m.add_function(wrap_pyfunction!(py_normalize_address, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_registration_date_py, m)?)?;

    Ok(())
}
