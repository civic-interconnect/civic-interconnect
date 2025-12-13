// crates/cep-py/src/lib.rs

/// Python FFI (Foreign Function Interface) for CEP functionality.
///
/// Exposes Rust CEP builders and utilities to Python via PyO3.
///
/// Design contract:
/// - Thin wrappers only: error mapping + type conversion.
/// - No business logic here (no normalization logic, no schema logic, no policy).
/// - Python-visible function names are stable and match the published .pyi surface.
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyAny;
use pyo3::wrap_pyfunction;

use serde::Serialize;

// CEP builders (JSON-in, JSON-out)
use cep_core::ctag::build_ctag_from_normalized_json;
use cep_core::entity::build_entity_from_normalized_json;
use cep_core::exchange::build_exchange_from_normalized_json;
use cep_core::relationship::build_relationship_from_normalized_json;

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct PyCanonicalInput {
    legal_name_normalized: String,
    address_normalized: Option<String>,
    country_code: String,
    registration_date: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct PySnfei {
    value: String,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct PySnfeiResult {
    snfei: PySnfei,
    canonical: PyCanonicalInput,
    confidence_score: f64,
    tier: u8,
    fields_used: Vec<String>,
}

impl From<SnfeiResult> for PySnfeiResult {
    fn from(r: SnfeiResult) -> Self {
        Self {
            snfei: PySnfei {
                value: r.snfei.value().to_string(),
            },
            canonical: PyCanonicalInput {
                legal_name_normalized: r.canonical.legal_name_normalized,
                address_normalized: r.canonical.address_normalized,
                country_code: r.canonical.country_code,
                registration_date: r.canonical.registration_date,
            },
            confidence_score: r.confidence_score,
            tier: r.tier,
            fields_used: r.fields_used,
        }
    }
}

// Core functions (aliased to avoid name collisions with Python-exported wrappers)
use cep_core::common::localization::{
    apply_localization_name as core_apply_localization_name,
    apply_localization_name_detailed_json as core_apply_localization_name_detailed_json,
};
use cep_core::common::normalizer::{
    normalize_address as core_normalize_address, normalize_legal_name as core_normalize_legal_name,
    normalize_registration_date as core_normalize_registration_date,
};
use cep_core::common::snfei::{generate_snfei_with_confidence, SnfeiResult};

/// Helper: parse JSON text into a Python object (dict/list/etc).
///
/// Returns an owned Python object (`Py<PyAny>`), suitable as a PyO3 return type.
/// This avoids deprecated `PyObject` and avoids calling `.into_py()` on `Bound`.
fn py_json_loads(py: Python<'_>, json_text: &str) -> PyResult<Py<PyAny>> {
    let json_mod = py.import("json")?;
    let obj = json_mod.call_method1("loads", (json_text,))?;
    Ok(obj.unbind())
}

/// Python wrapper around the Rust CTag builder.
///
/// Python signature:
///   build_ctag_json(input_json: str) -> str
#[pyfunction]
fn build_ctag_json(input_json: &str) -> PyResult<String> {
    build_ctag_from_normalized_json(input_json).map_err(|e| PyValueError::new_err(e.to_string()))
}

/// Python wrapper around the Rust entity builder.
///
/// Python signature:
///   build_entity_json(input_json: str) -> str
#[pyfunction]
fn build_entity_json(input_json: &str) -> PyResult<String> {
    build_entity_from_normalized_json(input_json).map_err(|e| PyValueError::new_err(e.to_string()))
}

/// Python wrapper around the Rust exchange builder.
///
/// Python signature:
///   build_exchange_json(input_json: str) -> str
#[pyfunction]
fn build_exchange_json(input_json: &str) -> PyResult<String> {
    build_exchange_from_normalized_json(input_json)
        .map_err(|e| PyValueError::new_err(e.to_string()))
}

/// Python wrapper around the Rust relationship builder.
///
/// Python signature:
///   build_relationship_json(input_json: str) -> str
#[pyfunction]
fn build_relationship_json(input_json: &str) -> PyResult<String> {
    build_relationship_from_normalized_json(input_json)
        .map_err(|e| PyValueError::new_err(e.to_string()))
}

/// Apply localization rules to a name (runtime fast path).
///
/// Python signature:
///   apply_localization_name(name: str, jurisdiction: str) -> str
#[pyfunction]
fn apply_localization_name(name: &str, jurisdiction: &str) -> PyResult<String> {
    core_apply_localization_name(name, jurisdiction).map_err(PyValueError::new_err)
}

/// Apply localization rules and return output + provenance as JSON.
///
/// This is the audit/test-friendly variant; the return value is a JSON string
/// produced by the core localization layer.
///
/// Python signature:
///   apply_localization_name_detailed_json(name: str, jurisdiction: str) -> str
#[pyfunction]
fn apply_localization_name_detailed_json(name: &str, jurisdiction: &str) -> PyResult<String> {
    core_apply_localization_name_detailed_json(name, jurisdiction).map_err(PyValueError::new_err)
}

/// Apply localization rules and return output + provenance as a parsed Python object (dict).
///
/// Thin wrapper around `apply_localization_name_detailed_json`:
/// - calls core to get JSON
/// - returns json.loads(JSON)
///
/// Python signature:
///   apply_localization_name_detailed(name: str, jurisdiction: str) -> dict[str, Any]
#[pyfunction]
fn apply_localization_name_detailed(
    py: Python<'_>,
    name: &str,
    jurisdiction: &str,
) -> PyResult<Py<PyAny>> {
    let json_text = core_apply_localization_name_detailed_json(name, jurisdiction)
        .map_err(PyValueError::new_err)?;
    py_json_loads(py, &json_text)
}

/// Generate an SNFEI from raw attributes using the Rust core SNFEI pipeline.
///
/// Python signature:
///   generate_snfei(
///       legal_name: str,
///       country_code: str,
///       address: str | None = None,
///       registration_date: str | None = None,
///   ) -> str
#[pyfunction(signature = (legal_name, country_code, address=None, registration_date=None))]
fn generate_snfei(
    legal_name: &str,
    country_code: &str,
    address: Option<&str>,
    registration_date: Option<&str>,
) -> PyResult<String> {
    let result = generate_snfei_with_confidence(
        legal_name,
        country_code,
        address,
        registration_date,
        None,
        None,
    );
    Ok(result.snfei.value().to_string())
}

/// Generate an SNFEI and return full pipeline metadata as JSON.
///
/// This returns a JSON string (serialized `SnfeiResult`).
///
/// Python signature:
///   generate_snfei_detailed_json(
///       legal_name: str,
///       country_code: str,
///       address: str | None = None,
///       registration_date: str | None = None,
///       lei: str | None = None,
///       sam_uei: str | None = None,
///   ) -> str
#[pyfunction(signature = (
    legal_name,
    country_code,
    address=None,
    registration_date=None,
    lei=None,
    sam_uei=None
))]
fn generate_snfei_detailed_json(
    legal_name: &str,
    country_code: &str,
    address: Option<&str>,
    registration_date: Option<&str>,
    lei: Option<&str>,
    sam_uei: Option<&str>,
) -> PyResult<String> {
    let result: SnfeiResult = generate_snfei_with_confidence(
        legal_name,
        country_code,
        address,
        registration_date,
        lei,
        sam_uei,
    );

    let py_result: PySnfeiResult = result.into();
    serde_json::to_string(&py_result).map_err(|e| PyValueError::new_err(e.to_string()))
}

/// Generate an SNFEI and return full pipeline metadata as a parsed Python object (dict).
///
/// Thin wrapper:
/// - serializes `SnfeiResult` to JSON
/// - returns json.loads(JSON)
///
/// Python signature:
///   generate_snfei_detailed(
///       legal_name: str,
///       country_code: str,
///       address: str | None = None,
///       registration_date: str | None = None,
///       lei: str | None = None,
///       sam_uei: str | None = None,
///   ) -> dict[str, Any]
#[pyfunction(signature = (
    legal_name,
    country_code,
    address=None,
    registration_date=None,
    lei=None,
    sam_uei=None
))]
fn generate_snfei_detailed(
    py: Python<'_>,
    legal_name: &str,
    country_code: &str,
    address: Option<&str>,
    registration_date: Option<&str>,
    lei: Option<&str>,
    sam_uei: Option<&str>,
) -> PyResult<Py<PyAny>> {
    let result: SnfeiResult = generate_snfei_with_confidence(
        legal_name,
        country_code,
        address,
        registration_date,
        lei,
        sam_uei,
    );

    let py_result: PySnfeiResult = result.into();
    let json_text =
        serde_json::to_string(&py_result).map_err(|e| PyValueError::new_err(e.to_string()))?;
    py_json_loads(py, &json_text)
}

/// Normalize a legal name via the Rust Normalizing Functor.
///
/// Python signature:
///   normalize_legal_name(value: str) -> str
#[pyfunction]
fn normalize_legal_name(value: &str) -> PyResult<String> {
    Ok(core_normalize_legal_name(value))
}

/// Normalize an address via the Rust Normalizing Functor.
///
/// Python signature:
///   normalize_address(value: str) -> str
#[pyfunction]
fn normalize_address(value: &str) -> PyResult<String> {
    Ok(core_normalize_address(value))
}

/// Normalize a registration date using the CEP core normalizer.
///
/// Python signature:
///   normalize_registration_date(value: str) -> str | None
#[pyfunction]
fn normalize_registration_date(value: &str) -> PyResult<Option<String>> {
    Ok(core_normalize_registration_date(value))
}

/// Python module definition.
///
/// Imported as:
///   import cep_py
#[pymodule]
fn cep_py(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(build_ctag_json, m)?)?;
    m.add_function(wrap_pyfunction!(build_entity_json, m)?)?;
    m.add_function(wrap_pyfunction!(build_exchange_json, m)?)?;
    m.add_function(wrap_pyfunction!(build_relationship_json, m)?)?;

    m.add_function(wrap_pyfunction!(apply_localization_name, m)?)?;
    m.add_function(wrap_pyfunction!(apply_localization_name_detailed_json, m)?)?;
    m.add_function(wrap_pyfunction!(apply_localization_name_detailed, m)?)?;

    m.add_function(wrap_pyfunction!(generate_snfei, m)?)?;
    m.add_function(wrap_pyfunction!(generate_snfei_detailed_json, m)?)?;
    m.add_function(wrap_pyfunction!(generate_snfei_detailed, m)?)?;

    m.add_function(wrap_pyfunction!(normalize_legal_name, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_address, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_registration_date, m)?)?;

    Ok(())
}
