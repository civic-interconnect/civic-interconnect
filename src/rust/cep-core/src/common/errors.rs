use thiserror::Error;

#[derive(Debug, Error)]
pub enum CepError {
    #[error("builder logic error: {0}")]
    BuilderError(String),

    #[error("configuration error: {0}")]
    Configuration(String),

    #[error("hash verification failed: expected {expected}, got {actual}")]
    HashMismatch { expected: String, actual: String },

    #[error("invalid hash: expected 64 hex characters, got {0}")]
    InvalidHash(String),

    #[error("invalid identifier: {0}")]
    InvalidIdentifier(String),

    #[error("invalid JSON input: {0}")]
    InvalidJson(String),

    #[error("invalid timestamp: {0}")]
    InvalidTimestamp(String),

    #[error("missing required field: {0}")]
    MissingField(String),

    #[error("revision chain error: {0}")]
    RevisionChain(String),

    #[error("serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    #[error("unknown schema: {0}")]
    UnknownSchema(String),

    #[error("unsupported schema version: {0}")]
    UnsupportedVersion(String),

    /// Well-formed input that fails CEP validation (missing required fields, wrong shapes, etc.).
    #[error("validation error: {0}")]
    Validation(String),
}

/// Use this when deserializing *input payload JSON* (adapter -> builder).
/// - Syntax/Eof => InvalidJson
/// - Data       => Validation (well-formed JSON, wrong shape/values)
/// - Io         => Configuration (should be rare for from_str)
pub fn map_json_input_error(e: serde_json::Error) -> CepError {
    use serde_json::error::Category;

    match e.classify() {
        Category::Syntax | Category::Eof => CepError::InvalidJson(e.to_string()),
        Category::Data => CepError::Validation(e.to_string()),
        Category::Io => CepError::Configuration(e.to_string()),
    }
}

/// Result type for CEP operations.
pub type CepResult<T> = Result<T, CepError>;
