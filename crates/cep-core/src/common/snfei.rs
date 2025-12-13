// crates/cep-core/src/common/snfei.rs
//
// Module for computing and validating SNFEI (Structured Non-Fungible Entity Identifier).

use sha2::{Digest, Sha256};

use serde::{Deserialize, Serialize};

use super::normalizer::{CanonicalInput, build_canonical_input};

/// A validated SNFEI (64-character lowercase hex string).
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Snfei {
    pub value: String,
}

impl Snfei {
    /// The prefix for a Verifiable ID derived from an SNFEI.
    pub const VERIFIABLE_ID_PREFIX: &'static str = "cep-entity:snfei:";

    /// Create from an existing hash string.
    pub fn from_hash(hash: &str) -> Option<Self> {
        if hash.len() == 64 && hash.chars().all(|c| c.is_ascii_hexdigit()) {
            Some(Self {
                value: hash.to_lowercase(),
            })
        } else {
            None
        }
    }

    /// Get the hash value.
    pub fn value(&self) -> &str {
        &self.value
    }

    /// Get a shortened version for display.
    pub fn short(&self, length: usize) -> String {
        if self.value.len() <= length {
            self.value.clone()
        } else {
            format!("{}...", &self.value[..length])
        }
    }

    /// Generates the full Verifiable ID string (e.g., "cep-entity:snfei:<hash>").
    pub fn to_verifiable_id(&self) -> String {
        format!("{}{}", Self::VERIFIABLE_ID_PREFIX, self.value)
    }
}

impl std::fmt::Display for Snfei {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.value)
    }
}

/// Result of SNFEI generation with metadata.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SnfeiResult {
    /// The generated SNFEI
    pub snfei: Snfei,
    /// Canonical input used for generation
    pub canonical: CanonicalInput,
    /// Confidence score (0.0 to 1.0)
    pub confidence_score: f64,
    /// Tier classification (1, 2, or 3)
    pub tier: u8,
    /// Fields that contributed to the SNFEI
    pub fields_used: Vec<String>,
}

/// Compute SNFEI from canonical input.
pub fn compute_snfei(canonical: &CanonicalInput) -> Snfei {
    let hash_input = canonical.to_hash_string();
    let mut hasher = Sha256::new();
    hasher.update(hash_input.as_bytes());
    let result = hasher.finalize();
    Snfei {
        value: format!("{:x}", result),
    }
}

/// Generate SNFEI with confidence scoring and tier classification.
///
/// Tier Classification:
/// - Tier 1: Entity has LEI (global identifier) - confidence 1.0
/// - Tier 2: Entity has SAM UEI (federal identifier) - confidence 0.95
/// - Tier 3: Entity uses SNFEI (computed hash) - confidence varies
pub fn generate_snfei_with_confidence(
    legal_name: &str,
    country_code: &str,
    address: Option<&str>,
    registration_date: Option<&str>,
    lei: Option<&str>,
    sam_uei: Option<&str>,
) -> SnfeiResult {
    let canonical = build_canonical_input(legal_name, country_code, address, registration_date);
    let snfei = compute_snfei(&canonical);

    // Tier 1: LEI available
    if let Some(lei_val) = lei {
        if lei_val.len() == 20 {
            return SnfeiResult {
                snfei,
                canonical,
                confidence_score: 1.0,
                tier: 1,
                fields_used: vec![
                    "lei".to_string(),
                    "legal_name".to_string(),
                    "country_code".to_string(),
                ],
            };
        }
    }

    // Tier 2: SAM UEI available
    if let Some(uei_val) = sam_uei {
        if uei_val.len() == 12 {
            return SnfeiResult {
                snfei,
                canonical,
                confidence_score: 0.95,
                tier: 2,
                fields_used: vec![
                    "sam_uei".to_string(),
                    "legal_name".to_string(),
                    "country_code".to_string(),
                ],
            };
        }
    }

    // Tier 3: Computed SNFEI
    let has_address = canonical
        .address_normalized
        .as_deref()
        .map_or(false, |s| !s.is_empty());

    let has_registration_date = canonical
        .registration_date
        .as_deref()
        .map_or(false, |s| !s.is_empty());

    let mut fields_used = vec!["legal_name".to_string(), "country_code".to_string()];
    if has_address {
        fields_used.push("address".to_string());
    }
    if has_registration_date {
        fields_used.push("registration_date".to_string());
    }

    let mut confidence: f64 = 0.5;
    if has_address {
        confidence += 0.2;
    }
    if has_registration_date {
        confidence += 0.2;
    }
    let word_count = canonical.legal_name_normalized.split_whitespace().count();
    if word_count > 3 {
        confidence += 0.1;
    }
    confidence = confidence.min(0.9).max(0.0);

    SnfeiResult {
        snfei,
        canonical,
        confidence_score: (confidence * 100.0).round() / 100.0,
        tier: 3,
        fields_used,
    }
}

/// Simple SNFEI generation without metadata.
pub fn generate_snfei_simple(
    legal_name: &str,
    country_code: &str,
    address: Option<&str>,
) -> String {
    let result =
        generate_snfei_with_confidence(legal_name, country_code, address, None, None, None);
    result.snfei.value
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn snfei_allows_digits_and_lowercase_hex() {
        let s = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
        let sn = Snfei::from_hash(s).expect("should be valid hex");
        assert_eq!(sn.value(), s);
    }
}
