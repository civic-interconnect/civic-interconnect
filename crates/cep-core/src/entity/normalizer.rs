use std::collections::{HashMap, HashSet};

use chrono::NaiveDate;
use regex::Regex;
use unicode_normalization::UnicodeNormalization;

/// Detects Unicode combining marks (accents) after NFD decomposition.
/// We strip these so that "é" → "e", "ñ" → "n", etc.
fn is_combining_mark(c: char) -> bool {
    matches!(
        c,
        '\u{0300}'..='\u{036F}' |
        '\u{1AB0}'..='\u{1AFF}' |
        '\u{1DC0}'..='\u{1DFF}' |
        '\u{20D0}'..='\u{20FF}' |
        '\u{FE20}'..='\u{FE2F}'
    )
}

// =============================================================================
// UNIVERSAL EXPANSION MAPS (using lazy_static for global static HashMaps)
// =============================================================================

// We use `lazy_static` for complex static initializations like HashMaps.
// Note: Rust often prefers `phf` crate for faster, compile-time perfect hash maps,
// but for simplicity, we'll use `lazy_static` with standard `HashMap`.
lazy_static::lazy_static! {
    /// Legal entity suffixes: ALWAYS expand to full form
    static ref LEGAL_SUFFIX_EXPANSIONS: HashMap<&'static str, &'static str> = {
        let mut m = HashMap::new();
        // Corporations
        m.insert("inc", "incorporated");
        m.insert("inc.", "incorporated");
        m.insert("incorp", "incorporated");
        m.insert("corp", "corporation");
        m.insert("corp.", "corporation");
        // Limited Liability
        m.insert("llc", "limited liability company");
        m.insert("l.l.c.", "limited liability company");
        m.insert("l.l.c", "limited liability company");
        m.insert("llp", "limited liability partnership");
        m.insert("l.l.p.", "limited liability partnership");
        m.insert("lp", "limited partnership");
        m.insert("l.p.", "limited partnership");
        // Limited
        m.insert("ltd", "limited");
        m.insert("ltd.", "limited");
        m.insert("ltda", "limitada");         // Spanish/Portuguese
        m.insert("ltee", "limitee");         // French (will be ASCII-ified)
        // Professional
        m.insert("pc", "professional corporation");
        m.insert("p.c.", "professional corporation");
        m.insert("pllc", "professional limited liability company");
        m.insert("p.l.l.c.", "professional limited liability company");
        m.insert("pa", "professional association");
        m.insert("p.a.", "professional association");
        // Company
        m.insert("co", "company");
        m.insert("co.", "company");
        m.insert("cos", "companies");
        // Partnership
        m.insert("gp", "general partnership");
        m.insert("g.p.", "general partnership");
        // Other
        m.insert("plc", "public limited company");
        m.insert("p.l.c.", "public limited company");
        m.insert("sa", "sociedad anonima");     // Spanish
        m.insert("s.a.", "sociedad anonima");
        m.insert("ag", "aktiengesellschaft");  // German
        m.insert("gmbh", "gesellschaft mit beschrankter haftung"); // German
        m.insert("bv", "besloten vennootschap"); // Dutch
        m.insert("b.v.", "besloten vennootschap");
        m.insert("nv", "naamloze vennootschap");  // Dutch
        m.insert("n.v.", "naamloze vennootschap");
        m.insert("pty", "proprietary");       // Australian
        m.insert("pty.", "proprietary");
        m
    };

    /// Common abbreviations: ALWAYS expand
    static ref COMMON_ABBREVIATIONS: HashMap<&'static str, &'static str> = {
        let mut m = HashMap::new();
        // Organizational
        m.insert("assn", "association");
        m.insert("assoc", "association");
        m.insert("dept", "department");
        // ... (All other COMMON_ABBREVIATIONS from Python code)
        m.insert("mfg", "manufacturing");
        m.insert("mfr", "manufacturer");
        m.insert("bros", "brothers");
        m.insert("sys", "systems");
        m.insert("tech", "technology");
        m.insert("ind", "industries");
        m.insert("inds", "industries");
        m.insert("ent", "enterprises");
        m.insert("hldgs", "holdings");
        m.insert("props", "properties");
        m.insert("invs", "investments");
        m.insert("inv", "investment");
        m.insert("fin", "financial");
        m.insert("ins", "insurance");
        m.insert("med", "medical");
        m.insert("hlth", "health");
        m.insert("pharm", "pharmaceutical");
        m.insert("bio", "biological");
        m.insert("chem", "chemical");
        m.insert("elec", "electric");
        m.insert("util", "utilities");
        // Junior/Senior (for schools, orgs)
        m.insert("jr", "junior");
        m.insert("sr", "senior");
        m
    };

    /// Stop words to remove (after normalization)
    static ref STOP_WORDS: HashSet<&'static str> = {
        let mut s = HashSet::new();
        s.insert("the");
        s.insert("of");
        s.insert("a");
        s.insert("an");
        s.insert("and");
        s.insert("for");
        s.insert("in");
        s.insert("on");
        s.insert("at");
        s.insert("to");
        s.insert("by");
        s
    };

    /// US Postal abbreviations (USPS standard)
    static ref US_ADDRESS_EXPANSIONS: HashMap<&'static str, &'static str> = {
        let mut m = HashMap::new();
        // Street types
        m.insert("st", "street");
        m.insert("st.", "street");
        m.insert("ave", "avenue");
        m.insert("ave.", "avenue");
        // ... (All other US_ADDRESS_EXPANSIONS from Python code)
        m.insert("blvd", "boulevard");
        m.insert("blvd.", "boulevard");
        m.insert("dr", "drive");
        m.insert("dr.", "drive");
        m.insert("rd", "road");
        m.insert("rd.","road");
        m.insert("ln", "lane");
        m.insert("ln.", "lane");
        m.insert("ct", "court");
        m.insert("ct.","court");
        m.insert("cir", "circle");
        m.insert("cir.","circle");
        m.insert("pl", "place");
        m.insert("pl.","place");
        m.insert("sq", "square");
        m.insert("sq.","square");
        m.insert("pkwy", "parkway");
        m.insert("hwy", "highway");
        m.insert("trl", "trail");
        m.insert("way", "way");
        m.insert("ter", "terrace");
        m.insert("ter.", "terrace");
        // Directionals
        m.insert("n", "north");
        m.insert("n.", "north");
        m.insert("s", "south");
        m.insert("s.", "south");
        m.insert("e", "east");
        m.insert("e.","east");
        m.insert("w", "west");
        m.insert("w.","west");
        m.insert("ne", "northeast");
        m.insert("nw", "northwest");
        m.insert("se", "southeast");
        m.insert("sw", "southwest");
        m
    };

    /// Regex for secondary unit designators to REMOVE (apartment, suite, etc.)
    static ref SECONDARY_UNIT_REGEX: Regex = {
        let patterns = vec![
            r"\bapt\.?\s*#?\s*\w+",
            r"\bsuite\s*#?\s*\w+",
            r"\bste\.?\s*#?\s*\w+",
            r"\bunit\s*#?\s*\w+",
            r"\b#\s*\d+\w*",
            r"\bfloor\s*\d+",
            r"\bfl\.?\s*\d+",
            r"\broom\s*\d+",
            r"\brm\.?\s*\d+",
            r"\bbldg\.?\s*\w+",
            r"\bbuilding\s*\w+",
        ];
        // Combine all patterns into one OR-separated regex
        let full_pattern = format!("(?i){}", patterns.join("|"));
        Regex::new(&full_pattern).unwrap()
    };
}

// =============================================================================
// NORMALIZATION PIPELINE
// =============================================================================

/// Convert Unicode to ASCII equivalent.
///
/// Handles accented characters, special quotes, etc.
fn normalize_unicode_basic(text: &str) -> String {
    // 1. NFD normalization and removal of combining marks (accents)
    let mut normalized_text: String = text.nfd().filter(|c| !is_combining_mark(*c)).collect();

    // 2. Custom replacements for punctuation / ligatures etc.
    // Note: all non-ASCII chars are expressed with \u{...} escapes
    // so the source file itself stays ASCII-only.
    let replacements = [
        // Ligatures / special letters
        ('\u{00E6}', "ae"), // æ
        ('\u{0153}', "oe"), // œ
        ('\u{00F8}', "o"),  // ø
        ('\u{00DF}', "ss"), // ß
        ('\u{00F0}', "d"),  // ð
        ('\u{00FE}', "th"), // þ
        // Quotes and dashes
        ('\u{2018}', ""),    // ‘
        ('\u{2019}', ""),    // ’
        ('\u{201C}', ""),    // “
        ('\u{201D}', ""),    // ”
        ('\u{2013}', "-"),   // –
        ('\u{2014}', "-"),   // —
        ('\u{2026}', "..."), // …
    ];

    for (old, new) in replacements.iter() {
        normalized_text = normalized_text.replace(*old, new);
    }

    // 3. Do NOT drop non-ASCII now; Greek, Cyrillic, etc. remain.
    // Strip control characters:
    normalized_text
        .chars()
        .filter(|c| !c.is_control())
        .collect()
}

/// Remove all punctuation from text.
///
/// Only alphanumeric and spaces remain. Punctuation is replaced by a space
/// to maintain word boundaries.
fn remove_punctuation(text: &str) -> String {
    text.chars()
        .map(|c| {
            if c.is_alphanumeric() || c.is_whitespace() {
                c
            } else {
                ' ' // Replace punctuation with space
            }
        })
        .collect()
}

/// Collapse multiple spaces to single space, trim ends.
fn collapse_whitespace(text: &str) -> String {
    text.split_whitespace().collect::<Vec<&str>>().join(" ")
}

/// Expand a single token if it matches known abbreviations.
fn expand_token(token: &str) -> String {
    let lower = token.to_lowercase();

    // 1. Check legal suffixes first
    if let Some(expansion) = LEGAL_SUFFIX_EXPANSIONS.get(lower.as_str()) {
        return expansion.to_string();
    }

    // 2. Check common abbreviations
    if let Some(expansion) = COMMON_ABBREVIATIONS.get(lower.as_str()) {
        return expansion.to_string();
    }

    lower
}

/// Expand all abbreviations in the text.
fn expand_abbreviations(text: &str) -> String {
    let tokens: Vec<&str> = text.split_whitespace().collect();
    let expanded: Vec<String> = tokens.iter().map(|&t| expand_token(t)).collect();
    expanded.join(" ")
}

/// Remove stop words from text.
fn remove_stop_words(text: &str, preserve_initial: bool) -> String {
    let tokens: Vec<&str> = text.split_whitespace().collect();
    if tokens.is_empty() {
        return "".to_string();
    }

    let mut result = Vec::with_capacity(tokens.len());
    for (i, token) in tokens.iter().enumerate() {
        // If it's a stop word...
        if STOP_WORDS.contains(token) {
            // ...preserve if it's the first word and flag is set
            if i == 0 && preserve_initial {
                result.push(*token);
            }
            // Otherwise, skip (don't push to result)
        } else {
            result.push(*token);
        }
    }

    result.join(" ")
}

pub fn normalize_legal_name(
    name: &str,
    remove_stop_words_flag: bool,
    preserve_initial_stop: bool,
) -> String {
    if name.is_empty() {
        return "".to_string();
    }

    // 1. Lowercase (done implicitly during token expansion, but better upfront)
    let mut text = name.to_lowercase();

    // 2. ASCII transliteration
    text = normalize_unicode_basic(&text);

    // 3. Remove punctuation
    text = remove_punctuation(&text);

    // 4. Collapse whitespace
    text = collapse_whitespace(&text);

    // 5. Expand abbreviations
    text = expand_abbreviations(&text);

    // 6. Remove stop words
    if remove_stop_words_flag {
        text = remove_stop_words(&text, preserve_initial_stop);
    }

    // 7. Final collapse and trim
    collapse_whitespace(&text)
}

// =============================================================================
// ADDRESS NORMALIZATION
// =============================================================================

fn expand_address_abbreviations(text: &str) -> String {
    let tokens: Vec<&str> = text.split_whitespace().collect();
    let expanded: Vec<String> = tokens
        .iter()
        .map(|&t| {
            // Check US postal abbreviations first, then fall back to the token itself
            if let Some(expansion) = US_ADDRESS_EXPANSIONS.get(t) {
                expansion.to_string()
            } else {
                t.to_string()
            }
        })
        .collect();
    expanded.join(" ")
}

pub fn normalize_address(address: &str, remove_secondary: bool) -> String {
    if address.is_empty() {
        return "".to_string();
    }

    // 1. Lowercase
    let mut text = address.to_lowercase();

    // 2. ASCII transliteration
    text = normalize_unicode_basic(&text);

    // 3. Remove secondary unit designators using the combined Regex
    if remove_secondary {
        text = SECONDARY_UNIT_REGEX.replace_all(&text, " ").to_string();
    }

    // 4. Remove punctuation
    text = remove_punctuation(&text);

    // 5. Collapse whitespace
    text = collapse_whitespace(&text);

    // 6. Expand postal abbreviations
    text = expand_address_abbreviations(&text);

    // 7. Final trim
    text.trim().to_string()
}

// =============================================================================
// REGISTRATION DATE NORMALIZATION
// =============================================================================

/// Normalize a registration date to ISO 8601 format (YYYY-MM-DD).
///
/// Returns None if date cannot be parsed.
pub fn normalize_registration_date(date_str: &str) -> Option<String> {
    if date_str.is_empty() {
        return None;
    }

    let date_str = date_str.trim();

    // Try to parse using a list of common formats
    let patterns = [
        "%Y-%m-%d", // ISO format
        "%m/%d/%Y", // US format
        "%m-%d-%Y", // US format (dashes)
        "%d/%m/%Y", // European format
    ];

    for fmt in patterns.iter() {
        if let Ok(dt) = NaiveDate::parse_from_str(date_str, fmt) {
            return Some(dt.format("%Y-%m-%d").to_string());
        }
    }

    // Handle Year only format
    if let Ok(year) = date_str.parse::<i32>() {
        if year >= 1000 && year <= 9999 {
            // Year only - use January 1
            return Some(format!("{}-01-01", date_str));
        }
    }

    None
}

// =============================================================================
// CANONICAL INPUT BUILDER
// =============================================================================

/// Normalized input for SNFEI hashing.
#[derive(Debug, Clone)]
pub struct CanonicalInput {
    pub legal_name_normalized: String,
    pub address_normalized: Option<String>,
    pub country_code: String,
    pub registration_date: Option<String>,
}

impl CanonicalInput {
    /// Generate the concatenated string for hashing.
    ///
    /// Format: `legal_name_normalized|address_normalized|country_code|registration_date`
    /// Empty/None fields are included as empty strings to maintain consistent field positions.
    pub fn to_hash_string(&self) -> String {
        format!(
            "{}|{}|{}|{}",
            self.legal_name_normalized,
            self.address_normalized.as_deref().unwrap_or(""), // Option<String> to &str, default ""
            self.country_code,
            self.registration_date.as_deref().unwrap_or(""),
        )
    }

    /// Alternative format that omits empty fields.
    pub fn to_hash_string_v2(&self) -> String {
        let mut parts = vec![self.legal_name_normalized.clone()];

        if let Some(addr) = &self.address_normalized {
            parts.push(addr.clone());
        }

        parts.push(self.country_code.clone());

        if let Some(date) = &self.registration_date {
            parts.push(date.clone());
        }

        parts.join("|")
    }
}

/// Build a canonical input structure from raw entity data.
pub fn build_canonical_input(
    legal_name: &str,
    country_code: &str,
    address: Option<&str>,
    registration_date: Option<&str>,
) -> CanonicalInput {
    // Rust typically uses `&str` for inputs and `String` for owned, mutated/returned data.
    CanonicalInput {
        legal_name_normalized: normalize_legal_name(legal_name, true, false),
        address_normalized: address.and_then(|a| {
            // Only normalize if the address string is not empty after trimming
            let normalized = normalize_address(a, true);
            if normalized.is_empty() {
                None
            } else {
                Some(normalized)
            }
        }),
        country_code: country_code.to_uppercase(),
        registration_date: registration_date.and_then(|d| normalize_registration_date(d)),
    }
}
