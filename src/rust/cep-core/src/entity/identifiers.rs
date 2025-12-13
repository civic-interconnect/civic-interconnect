// src/rust/cep-core/src/entity/identifiers.rs

use crate::common::canonical::{Canonicalize, insert_if_present};
use crate::common::snfei::Snfei;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

pub const LEI_SCHEME_URI: &str = "https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabulary/core/entity-identifier-scheme.v1.0.0.json#lei";
pub const SAM_UEI_SCHEME_URI: &str = "https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabulary/core/entity-identifier-scheme.v1.0.0.json#sam-uei";
pub const SNFEI_SCHEME_URI: &str = "https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabulary/core/entity-identifier-scheme.v1.0.0.json#snfei";
pub const CANADIAN_BN_SCHEME_URI: &str = "https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabulary/core/entity-identifier-scheme.v1.0.0.json#canadian-bn";
pub const UK_COMPANIES_HOUSE_SCHEME_URI: &str = "https://raw.githubusercontent.com/civic-interconnect/civic-interconnect/main/vocabulary/core/entity-identifier-scheme.v1.0.0.json#uk-companies-house";

pub const LEI_VID_PREFIX: &str = "cep-entity:lei:";
pub const SAM_UEI_VID_PREFIX: &str = "cep-entity:sam-uei:";
pub const SNFEI_VID_PREFIX: &str = "cep-entity:snfei:";
pub const CANADIAN_BN_VID_PREFIX: &str = "cep-entity:canadian-bn:";
pub const UK_COMPANIES_HOUSE_VID_PREFIX: &str = "cep-entity:uk-companies-house:";

/// SAM.gov Unique Entity Identifier (12 alphanumeric characters).
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct SamUei(String);

impl SamUei {
    pub fn new(value: &str) -> Option<Self> {
        let v = value.trim().to_ascii_uppercase();
        if v.len() == 12
            && v.chars()
                .all(|c| c.is_ascii_uppercase() || c.is_ascii_digit())
        {
            Some(Self(v))
        } else {
            None
        }
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Legal Entity Identifier per ISO 17442 (20 alphanumeric characters).
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Lei(String);

impl Lei {
    pub fn new(value: &str) -> Option<Self> {
        let v = value.trim().to_ascii_uppercase();
        if v.len() == 20 && v.chars().all(|c| c.is_ascii_alphanumeric()) {
            Some(Self(v))
        } else {
            None
        }
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Canadian Business Number with program account (example: 123456789RC0001).
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct CanadianBn(String);

impl CanadianBn {
    pub fn new(value: &str) -> Option<Self> {
        let v = value.trim().to_ascii_uppercase();
        if v.len() != 15 {
            return None;
        }
        let (digits1, rest) = v.split_at(9);
        let (letters, digits2) = rest.split_at(2);
        if digits1.chars().all(|c| c.is_ascii_digit())
            && letters.chars().all(|c| c.is_ascii_uppercase())
            && digits2.chars().all(|c| c.is_ascii_digit())
        {
            Some(Self(v))
        } else {
            None
        }
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AdditionalScheme {
    pub scheme_uri: String,
    pub value: String,
}

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct EntityIdentifiers {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sam_uei: Option<SamUei>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub lei: Option<Lei>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub snfei: Option<Snfei>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub canadian_bn: Option<CanadianBn>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub additional_schemes: Option<Vec<AdditionalScheme>>,
}

impl EntityIdentifiers {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn with_sam_uei(mut self, uei: SamUei) -> Self {
        self.sam_uei = Some(uei);
        self
    }

    pub fn with_lei(mut self, lei: Lei) -> Self {
        self.lei = Some(lei);
        self
    }

    pub fn with_snfei(mut self, snfei: Snfei) -> Self {
        self.snfei = Some(snfei);
        self
    }

    pub fn with_canadian_bn(mut self, bn: CanadianBn) -> Self {
        self.canadian_bn = Some(bn);
        self
    }

    pub fn has_any(&self) -> bool {
        self.sam_uei.is_some()
            || self.lei.is_some()
            || self.snfei.is_some()
            || self.canadian_bn.is_some()
            || self
                .additional_schemes
                .as_ref()
                .map_or(false, |v| !v.is_empty())
    }

    /// Returns the "best" verifiable ID string.
    /// Priority: LEI > SAM UEI > SNFEI > Canadian BN > first additional.
    pub fn primary_identifier(&self) -> Option<String> {
        if let Some(ref lei) = self.lei {
            return Some(format!("{}{}", LEI_VID_PREFIX, lei.as_str()));
        }
        if let Some(ref uei) = self.sam_uei {
            return Some(format!("{}{}", SAM_UEI_VID_PREFIX, uei.as_str()));
        }
        if let Some(ref snfei) = self.snfei {
            return Some(format!("{}{}", SNFEI_VID_PREFIX, snfei.value()));
        }
        if let Some(ref bn) = self.canadian_bn {
            return Some(format!("{}{}", CANADIAN_BN_VID_PREFIX, bn.as_str()));
        }
        if let Some(ref schemes) = self.additional_schemes {
            if let Some(first) = schemes.first() {
                return Some(format!(
                    "cep-entity:other:{}:{}",
                    first.scheme_uri, first.value
                ));
            }
        }
        None
    }
}

impl Canonicalize for EntityIdentifiers {
    fn canonical_fields(&self) -> BTreeMap<String, String> {
        let mut map = BTreeMap::new();

        if let Some(ref schemes) = self.additional_schemes {
            if !schemes.is_empty() {
                let mut sorted: Vec<&AdditionalScheme> = schemes.iter().collect();
                sorted.sort_by(|a, b| {
                    let k = a.scheme_uri.cmp(&b.scheme_uri);
                    if k == std::cmp::Ordering::Equal {
                        a.value.cmp(&b.value)
                    } else {
                        k
                    }
                });
                let json = serde_json::to_string(&sorted).unwrap_or_else(|_| "[]".to_string());
                map.insert("additionalSchemes".to_string(), json);
            }
        }

        insert_if_present(
            &mut map,
            "canadianBn",
            self.canadian_bn.as_ref().map(|x| x.as_str()),
        );
        insert_if_present(&mut map, "lei", self.lei.as_ref().map(|x| x.as_str()));
        insert_if_present(
            &mut map,
            "samUei",
            self.sam_uei.as_ref().map(|x| x.as_str()),
        );
        insert_if_present(&mut map, "snfei", self.snfei.as_ref().map(|x| x.value()));

        map
    }
}
