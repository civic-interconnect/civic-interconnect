// Module for computing and validating SNFEI
// (Sub-National Fixed Entity Identifier)

use sha2::{Digest, Sha256};

// Import structs and functions from the sibling normalizer module
use super::normalizer::{CanonicalInput, build_canonical_input};

// =============================================================================
// SNFEI STRUCT AND VALIDATION
// =============================================================================

/// A validated SNFEI (64-character lowercase hex string).
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Snfei {
    value: String,
}

impl Snfei {
    /// The prefix for a Verifiable ID derived from an SNFEI.
    const VERIFIABLE_ID_PREFIX: &'static str = "cep-entity:snfei:";

    /// Private constructor that performs validation.
    fn new(value: String) -> Result<Self, ValueError> {
        if value.len() != 64 {
            return Err(ValueError(format!(
                "SNFEI must be 64 characters, got {}",
                value.len()
            )));
        }

        if !value
            .chars()
            .all(|c| c.is_ascii_hexdigit() && c.is_lowercase())
        {
            return Err(ValueError("SNFEI must be lowercase hex".to_string()));
        }

        Ok(Snfei { value })
    }

    /// Generates the full Verifiable ID string (e.g., "cep-entity:snfei:a1b2c3d4...").
    pub fn to_verifiable_id(&self) -> String {
        format!("{}{}", Self::VERIFIABLE_ID_PREFIX, self.value)
    }

    /// Return string slice of SNFEI.
    pub fn as_str(&self) -> &str {
        &self.value
    }
}

/// A simple custom error type for SNFEI validation.
#[derive(Debug)]
pub struct ValueError(String);

impl std::fmt::Display for ValueError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "SNFEI Validation Error: {}", self.0)
    }
}

impl std::error::Error for ValueError {}

// =============================================================================
// SNFEI RESULT AND METADATA
// =============================================================================

/// Result of SNFEI generation with confidence metadata.
#[derive(Debug, Clone)]
pub struct SnfeiResult {
    pub snfei: Snfei,
    pub canonical: CanonicalInput,
    pub confidence_score: f32,
    pub tier: u8,
    pub fields_used: Vec<String>,
}

// =============================================================================
// SNFEI COMPUTATION LOGIC
// =============================================================================

/// Compute SNFEI from canonical input.
pub fn compute_snfei(canonical: &CanonicalInput) -> Result<Snfei, ValueError> {
    // 1. Get the concatenated hash input string (e.g., name|address|country|date)
    let hash_input = canonical.to_hash_string();

    // 2. Encode to bytes (UTF-8)
    let hash_bytes = hash_input.as_bytes();

    // 3. Compute SHA-256 hash
    let mut hasher = Sha256::new();
    hasher.update(hash_bytes);
    let result = hasher.finalize();

    // 4. Convert the hash result to a 64-character lowercase hex string
    let hex_digest = format!("{:x}", result);

    // 5. Validate and return Snfei struct
    Snfei::new(hex_digest)
}

// =============================================================================
// MAIN ENTRY POINT
// =============================================================================

/// Generate SNFEI with confidence scoring and tier classification.
///
/// This is the main entry point for combining normalization and hashing.
pub fn generate_snfei_with_confidence(
    legal_name: &str,
    country_code: &str,
    address: Option<&str>,
    registration_date: Option<&str>,
    lei: Option<&str>,
    sam_uei: Option<&str>,
) -> Result<SnfeiResult, ValueError> {
    // 1. Apply Normalizing Functor to all inputs
    let canonical = build_canonical_input(legal_name, country_code, address, registration_date);

    let mut fields_used: Vec<String> = vec!["legal_name".to_string(), "country_code".to_string()];
    let mut confidence: f32 = 0.5;
    let mut _tier: u8 = 3;

    // --- Tier 1 & 2 Checks (Tier 3 is default) ---

    // Tier 1: LEI available (Confidence 1.0)
    if let Some(l) = lei {
        if l.len() == 20 {
            let snfei = compute_snfei(&canonical)?;
            fields_used.insert(0, "lei".to_string());
            return Ok(SnfeiResult {
                snfei,
                canonical,
                confidence_score: 1.0,
                tier: 1,
                fields_used,
            });
        }
    }

    // Tier 2: SAM UEI available (Confidence 0.95)
    if let Some(u) = sam_uei {
        if u.len() == 12 {
            let snfei = compute_snfei(&canonical)?;
            fields_used.insert(0, "sam_uei".to_string());
            return Ok(SnfeiResult {
                snfei,
                canonical,
                confidence_score: 0.95,
                tier: 2,
                fields_used,
            });
        }
    }

    // --- Tier 3: Compute SNFEI from attributes (Confidence Varies) ---
    let snfei = compute_snfei(&canonical)?;

    if canonical.address_normalized.is_some() {
        fields_used.push("address".to_string());
        confidence += 0.2;
    }

    if canonical.registration_date.is_some() {
        fields_used.push("registration_date".to_string());
        confidence += 0.2;
    }

    let word_count = canonical.legal_name_normalized.split_whitespace().count();
    if word_count > 3 {
        confidence += 0.1;
    }

    // Cap at 0.9 for Tier 3
    confidence = confidence.min(0.9);

    Ok(SnfeiResult {
        snfei,
        canonical,
        confidence_score: (confidence * 100.0).round() / 100.0,
        tier: 3,
        fields_used,
    })
}

/// Convenience function to generate SNFEI as a simple hex string.
pub fn generate_snfei_simple(
    legal_name: &str,
    country_code: &str,
    address: Option<&str>,
) -> Result<String, ValueError> {
    let result =
        generate_snfei_with_confidence(legal_name, country_code, address, None, None, None)?;
    Ok(result.snfei.value)
}


/// Convenience helper for FFI (Python / other bindings).
///
/// Returns the SNFEI as a bare 64-character lowercase hex string.
/// All normalization + tier logic is handled here; errors are propagated.
pub fn generate_snfei_for_ffi(
    legal_name: &str,
    country_code: &str,
    address: Option<&str>,
    registration_date: Option<&str>,
) -> Result<String, ValueError> {
    let result = generate_snfei_with_confidence(
        legal_name,
        country_code,
        address,
        registration_date,
        None,  // lei
        None,  // sam_uei
    )?;
    Ok(result.snfei.as_str().to_string())
}
