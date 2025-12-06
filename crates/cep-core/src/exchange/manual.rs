// crates/cep-core/src/exchange/manual.rs
use serde::{Deserialize, Serialize};
use crate::common::errors::{CepResult};

pub use super::generated::{
    ExchangeRecord,
    RecordKind,
    StatusEnvelope,
    StatusCode,
    Timestamps,
    Attestation,
};



// Add ergonomic helpers
impl ExchangeRecord {
    pub fn occurred_date(&self) -> &str {
        &self.occurred_timestamp[..10]
    }
}

/// Temporary stub builder for exchanges.
pub fn build_exchange_from_normalized_json(input_json: &str) -> CepResult<String> {
    Ok(input_json.to_string())
}





#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SourceEntity {
    pub entity_id: String,
    pub role_uri: Option<String>,
    pub account_identifier: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RecipientEntity {
    pub entity_id: String,
    pub role_uri: Option<String>,
    pub account_identifier: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ExchangeValue {
    pub amount: f64,
    #[serde(rename = "currencyCode")]
    pub currency_code: Option<String>,
    #[serde(rename = "valueTypeUri")]
    pub value_type_uri: Option<String>,
    #[serde(rename = "inKindDescription")]
    pub in_kind_description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ExchangeStatusLite {
    #[serde(rename = "statusCode")]
    pub status_code: String,
    #[serde(rename = "statusEffectiveTimestamp")]
    pub status_effective_timestamp: String,
}

impl ExchangeRecord {
    pub fn source_entity_typed(&self) -> Option<SourceEntity> {
        serde_json::from_value(self.source_entity.clone()).ok()
    }

    pub fn recipient_entity_typed(&self) -> Option<RecipientEntity> {
        serde_json::from_value(self.recipient_entity.clone()).ok()
    }

    pub fn value_typed(&self) -> Option<ExchangeValue> {
        serde_json::from_value(self.value.clone()).ok()
    }

    pub fn exchange_status_typed(&self) -> Option<ExchangeStatusLite> {
        serde_json::from_value(self.exchange_status.clone()).ok()
    }
}
