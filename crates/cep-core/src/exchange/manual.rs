// crates/cep-core/src/exchange/manual.rs

// Pull in the generated types.
use crate::exchange::generated::{
    ExchangeRecord, Exchangestatus, Recipiententity, Sourceentity, Value,
};

use crate::common::errors::CepResult;

// Ergonomic type aliases so downstream code can use nicer names if desired.
pub type SourceEntity = Sourceentity;
pub type RecipientEntity = Recipiententity;
pub type ExchangeValue = Value;
pub type ExchangeStatusLite = Exchangestatus;

// Re-export commonly used generated types so callers can just use `exchange::manual::*`.
pub use crate::exchange::generated::Attestation as GeneratedAttestation;

// Add ergonomic helpers on the generated ExchangeRecord.
impl ExchangeRecord {
    /// Returns the YYYY-MM-DD portion of occurredTimestamp.
    /// Note: this assumes occurredTimestamp is at least 10 characters long.
    pub fn occurred_date(&self) -> &str {
        &self.occurred_timestamp[..10]
    }

    /// Strongly-typed access to the source entity.
    pub fn source_entity_typed(&self) -> &SourceEntity {
        &self.source_entity
    }

    /// Strongly-typed access to the recipient entity.
    pub fn recipient_entity_typed(&self) -> &RecipientEntity {
        &self.recipient_entity
    }

    /// Strongly-typed access to the value block.
    pub fn value_typed(&self) -> &ExchangeValue {
        &self.value
    }

    /// Strongly-typed access to the exchange status.
    pub fn exchange_status_typed(&self) -> &ExchangeStatusLite {
        &self.exchange_status
    }
}

/// Temporary stub builder for exchanges.
/// For now this is a passthrough; future work can:
/// - validate against the schema
/// - hydrate into `ExchangeRecord`
/// - attach attestations / hashes, etc.
pub fn build_exchange_from_normalized_json(input_json: &str) -> CepResult<String> {
    Ok(input_json.to_string())
}
