// Module for manual construction of exchange records
// Path: rust/cep-core/src/exchange/manual.rs
//
// Contract:
// - cep-core does NOT manufacture default attestations.
// - Builders MUST reject missing or empty attestations.
// - Attestations are created upstream (adapter/ingest/CLI) and passed in.

use crate::common::attestations::deserialize_nonempty_vec;
use crate::common::errors::{CepResult, map_json_input_error};
use serde::Deserialize;

use crate::exchange::generated::{
    Attestation, ExchangeRecord, ExchangeRecordExchangeStatus, ExchangeRecordRecipientEntity,
    ExchangeRecordSourceEntity, ExchangeRecordValue,
};

// Add ergonomic helpers on the generated ExchangeRecord.
impl ExchangeRecord {
    /// Returns the YYYY-MM-DD portion of occurredTimestamp.
    /// Note: this assumes occurredTimestamp is at least 10 characters long.
    pub fn occurred_date(&self) -> &str {
        &self.occurred_timestamp[..10]
    }

    pub fn source_entity_typed(&self) -> &ExchangeRecordSourceEntity {
        &self.source_entity
    }

    pub fn recipient_entity_typed(&self) -> &ExchangeRecordRecipientEntity {
        &self.recipient_entity
    }

    pub fn value_typed(&self) -> &ExchangeRecordValue {
        &self.value
    }

    pub fn exchange_status_typed(&self) -> &ExchangeRecordExchangeStatus {
        &self.exchange_status
    }
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct NormalizedExchangeInput {
    // Enforce: present and non-empty.
    // Missing field => serde error "missing field `attestations`".
    // Empty array => custom error from deserialize_nonempty_vec.
    #[serde(deserialize_with = "deserialize_nonempty_vec")]
    attestations: Vec<Attestation>,
}

/// Temporary stub builder.
///
/// Today: validates input and enforces non-empty attestations, then passes through.
/// TODO: build a fully validated CEP exchange record (envelope + payload).
pub fn build_exchange_from_normalized_json(input_json: &str) -> CepResult<String> {
    let _normalized: NormalizedExchangeInput =
        serde_json::from_str(input_json).map_err(map_json_input_error)?;
    let _attestations = &_normalized.attestations;
    Ok(input_json.to_string())
}
