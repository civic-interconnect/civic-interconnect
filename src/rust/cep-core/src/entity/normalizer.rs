use std::collections::{HashMap, HashSet};

use chrono::NaiveDate;
use regex::Regex;
use serde::{Deserialize, Serialize};
use unicode_normalization::UnicodeNormalization;

/// Detects Unicode combining marks (accents) after NFD decomposition.
/// We strip these so that accented Latin letters lose diacritics.
/// Non-Latin scripts are preserved (Greek, Cyrillic, etc.).
fn is_combining_mark(c: char) -> bool {
    matches!(
        c,
        '\u{0300}'..='\u{036F}'
            | '\u{1AB0}'..='\u{1AFF}'
            | '\u{1DC0}'..='\u{1DFF}'
            | '\u{20D0}'..='\u{20FF}'
            | '\u{FE20}'..='\u{FE2F}'
    )
}

// =============================================================================
// UNIVERSAL EXPANSION MAPS (using lazy_static for global static HashMaps)
// =============================================================================

//
// Notes:
// - All keys are lowercase and intended to be matched on token boundaries.
// - The pipeline strips punctuation before token expansion, so dotted variants
//   (e.g. "inc.") should generally be handled by pre-pass normalization below,
//   not by adding dotted keys everywhere.
// - We alphabetize keys and detect duplicates at init time to prevent silent
//   overrides.
//

lazy_static::lazy_static! {
    /// Dotted / spaced legal-form normalizations performed before punctuation stripping.
    ///
    /// These reduce multi-token forms like "l.l.c." or "s.a." into a single token
    /// so they can be expanded reliably by LEGAL_SUFFIX_EXPANSIONS.
    static ref DOTTED_LEGAL_FORM_REWRITES: Vec<(Regex, &'static str)> = {
        let mut v: Vec<(Regex, &'static str)> = Vec::new();

        // Keep patterns ASCII-only in source by using \u{...} escapes when needed.
        // (?i) makes them case-insensitive.
        v.push((Regex::new(r"(?i)\bb\s*\.\s*v\s*\.?\b").unwrap(), "bv"));
        v.push((Regex::new(r"(?i)\bg\s*\.\s*p\s*\.?\b").unwrap(), "gp"));
        v.push((Regex::new(r"(?i)\bl\s*\.\s*l\s*\.\s*c\s*\.?\b").unwrap(), "llc"));
        v.push((Regex::new(r"(?i)\bl\s*\.\s*l\s*\.\s*p\s*\.?\b").unwrap(), "llp"));
        v.push((Regex::new(r"(?i)\bl\s*\.\s*p\s*\.?\b").unwrap(), "lp"));
        v.push((Regex::new(r"(?i)\bn\s*\.\s*v\s*\.?\b").unwrap(), "nv"));
        v.push((Regex::new(r"(?i)\bp\s*\.\s*a\s*\.?\b").unwrap(), "pa"));
        v.push((Regex::new(r"(?i)\bp\s*\.\s*c\s*\.?\b").unwrap(), "pc"));
        v.push((Regex::new(r"(?i)\bp\s*\.\s*l\s*\.\s*c\s*\.?\b").unwrap(), "plc"));
        v.push((Regex::new(r"(?i)\bp\s*\.\s*l\s*\.\s*l\s*\.\s*c\s*\.?\b").unwrap(), "pllc"));
        v.push((Regex::new(r"(?i)\bs\s*\.\s*a\s*\.?\b").unwrap(), "sa"));

        // Common spaced form "s a" (seen in some datasets).
        v.push((Regex::new(r"(?i)\bs\s+a\b").unwrap(), "sa"));

        v
    };

    /// Legal entity suffixes and legal forms: ALWAYS expand to full form.
    static ref LEGAL_SUFFIX_EXPANSIONS: HashMap<&'static str, &'static str> = {
        let mut m: HashMap<&'static str, &'static str> = HashMap::new();

        // Keys must be lowercase; keep sorted by key.
        let entries: [(&'static str, &'static str); 22] = [
            ("ag",   "aktiengesellschaft"),
            ("bv",   "besloten vennootschap"),
            ("co",   "company"),
            ("corp", "corporation"),
            ("cos",  "companies"),
            ("gmbh", "gesellschaft mit beschrankter haftung"),
            ("gp",   "general partnership"),
            ("inc",  "incorporated"),
            ("incorp","incorporated"),
            ("llc",  "limited liability company"),
            ("llp",  "limited liability partnership"),
            ("lp",   "limited partnership"),
            ("ltd",  "limited"),
            ("ltda", "limitada"),
            ("ltee", "limitee"),
            ("na",   "national association"),
            ("nv",   "naamloze vennootschap"),
            ("pa",   "professional association"),
            ("pc",   "professional corporation"),
            ("plc",  "public limited company"),
            ("pllc", "professional limited liability company"),
            ("sa",   "societe anonyme"),
        ];

        for (k, v) in entries.iter() {
            if m.insert(*k, *v).is_some() {
                panic!("Duplicate LEGAL_SUFFIX_EXPANSIONS key: {}", k);
            }
        }

        m
    };

 /// Common abbreviations: ALWAYS expand (non-legal).
    static ref COMMON_ABBREVIATIONS: HashMap<&'static str, &'static str> = {
        let mut m: HashMap<&'static str, &'static str> = HashMap::new();

        // Keys sorted by key.
        let entries: [(&'static str, &'static str); 62] = [
            ("acad",  "academy"),
            ("admin", "administration"),
            ("assn",  "association"),
            ("assoc", "association"),
            ("auth",  "authority"),
            ("bd",    "board"),
            ("bio",   "biological"),
            ("boro",  "borough"),
            ("bros",  "brothers"),
            ("chem",  "chemical"),
            ("coll",  "college"),
            ("comm",  "commission"),
            ("ctr",   "center"),
            ("ctre",  "centre"),
            ("cty",   "county"),
            ("dept",  "department"),
            ("dist",  "district"),
            ("div",   "division"),
            ("elec",  "electric"),
            ("elem",  "elementary"),
            ("ent",   "enterprises"),
            ("fed",   "federal"),
            ("fin",   "financial"),
            ("ft",    "fort"),
            ("govt",  "government"),
            ("grp",   "group"),
            ("hlth",  "health"),
            ("hldgs", "holdings"),
            ("ind",   "industries"),
            ("inds",  "industries"),
            ("ins",   "insurance"),
            ("inst",  "institute"),
            ("intl",  "international"),
            ("inv",   "investment"),
            ("invs",  "investments"),
            ("isd",   "independent school district"),
            ("jr",    "junior"),
            ("med",   "medical"),
            ("mfg",   "manufacturing"),
            ("mgmt",  "management"),
            ("mgt",   "management"),
            ("mfr",   "manufacturer"),
            ("metro", "metropolitan"),
            ("mt",    "mount"),
            ("muni",  "municipal"),
            ("natl",  "national"),
            ("org",   "organization"),
            ("pharm", "pharmaceutical"),
            ("props", "properties"),
            ("pt",    "point"),
            ("regl",  "regional"),
            ("sch",   "school"),
            ("sr",    "senior"),
            ("svc",   "service"),
            ("svcs",  "services"),
            ("sys",   "systems"),
            ("tech",  "technology"),
            ("twp",   "township"),
            ("univ",  "university"),
            ("usd",   "unified school district"),
            ("util",  "utilities"),
            ("vlg",   "village"),
        ];

        for (k, v) in entries.iter() {
            if m.insert(*k, *v).is_some() {
                panic!("Duplicate COMMON_ABBREVIATIONS key: {}", k);
            }
        }

        m
    };

    /// Stop words to remove (after normalization). Keys sorted.
    static ref STOP_WORDS: HashSet<&'static str> = {
        let mut s: HashSet<&'static str> = HashSet::new();
        let entries: [&'static str; 11] = [
            "a",
            "an",
            "and",
            "at",
            "by",
            "for",
            "in",
            "of",
            "on",
            "the",
            "to",
        ];
        for w in entries.iter() {
            s.insert(*w);
        }
        s
    };

    /// US Postal abbreviations (subset of common USPS expansions). Keys sorted.
    static ref US_ADDRESS_EXPANSIONS: HashMap<&'static str, &'static str> = {
        let mut m: HashMap<&'static str, &'static str> = HashMap::new();

        let entries: [(&'static str, &'static str); 31] = [
            ("ave",  "avenue"),
            ("blvd", "boulevard"),
            ("cir",  "circle"),
            ("ct",   "court"),
            ("dr",   "drive"),
            ("e",    "east"),
            ("expy", "expressway"),
            ("hwy",  "highway"),
            ("ln",   "lane"),
            ("n",    "north"),
            ("ne",   "northeast"),
            ("nw",   "northwest"),
            ("pkwy", "parkway"),
            ("pl",   "place"),
            ("rd",   "road"),
            ("s",    "south"),
            ("se",   "southeast"),
            ("sq",   "square"),
            ("st",   "street"),
            ("sw",   "southwest"),
            ("ter",  "terrace"),
            ("trl",  "trail"),
            ("w",    "west"),
            ("way",  "way"),
            // TODO: Review extras that occur frequently:
            ("ctr",  "center"),
            ("ctrs", "centers"),
            ("ste",  "suite"),
            ("fl",   "floor"),
            ("bldg", "building"),
            ("apt",  "apartment"),
            ("rm",   "room"),
        ];

        for (k, v) in entries.iter() {
            if m.insert(*k, *v).is_some() {
                panic!("Duplicate US_ADDRESS_EXPANSIONS key: {}", k);
            }
        }

        m
    };

    /// Regex for secondary unit designators to remove (apartment, suite, etc.).
    static ref SECONDARY_UNIT_REGEX: Regex = {
        let patterns: [&'static str; 11] = [
            r"\bapt\.?\s*#?\s*\w+",
            r"\bapartment\s*#?\s*\w+",
            r"\bbldg\.?\s*#?\s*\w+",
            r"\bbuilding\s*#?\s*\w+",
            r"\bfl\.?\s*#?\s*\d+",
            r"\bfloor\s*#?\s*\d+",
            r"\b#\s*\d+\w*",
            r"\brm\.?\s*#?\s*\w+",
            r"\broom\s*#?\s*\w+",
            r"\bste\.?\s*#?\s*\w+",
            r"\bsuite\s*#?\s*\w+",
        ];
        let full_pattern = format!("(?i){}", patterns.join("|"));
        Regex::new(&full_pattern).unwrap()
    };
}

// =============================================================================
// NORMALIZATION PIPELINE
// =============================================================================

/// Normalize Unicode and strip diacritics where safe.
///
/// Steps:
/// - NFD decomposition
/// - remove combining marks (diacritics)
/// - replace a small set of punctuation-like Unicode chars with ASCII
/// - remove control characters
///
/// This does NOT transliterate non-Latin scripts to ASCII. They are preserved.
/// Only Latin letters lose diacritics.
fn normalize_unicode_basic(text: &str) -> String {
    // 1) NFD and strip combining marks
    let mut s: String = text.nfd().filter(|c| !is_combining_mark(*c)).collect();

    // 2) Targeted Unicode punctuation normalization (ASCII-only replacements).
    // Use \u{...} escapes so the source file stays ASCII-only.
    let replacements: [(char, &'static str); 9] = [
        ('\u{2018}', ""),    // left single quote
        ('\u{2019}', ""),    // right single quote
        ('\u{201C}', ""),    // left double quote
        ('\u{201D}', ""),    // right double quote
        ('\u{2013}', "-"),   // en dash
        ('\u{2014}', "-"),   // em dash
        ('\u{2212}', "-"),   // minus sign
        ('\u{2026}', "..."), // ellipsis
        ('\u{00A0}', " "),   // non-breaking space
    ];

    for (old, new) in replacements.iter() {
        s = s.replace(*old, new);
    }

    // 3) Drop control chars, keep everything else (including non-ASCII letters).
    s.chars().filter(|c| !c.is_control()).collect()
}

/// Normalize dotted and spaced legal forms before punctuation stripping.
///
/// This helps cases like:
/// - "L.L.C." -> "llc"
/// - "S.A."   -> "sa"
fn normalize_dotted_legal_forms(text: &str) -> String {
    let mut out = text.to_string();
    for (re, replacement) in DOTTED_LEGAL_FORM_REWRITES.iter() {
        out = re.replace_all(&out, *replacement).to_string();
    }
    out
}

/// Replace punctuation with spaces to preserve word boundaries.
/// Keeps letters/digits (including non-ASCII alphanumerics) and whitespace.
fn remove_punctuation(text: &str) -> String {
    text.chars()
        .map(|c| {
            if c.is_alphanumeric() || c.is_whitespace() {
                c
            } else {
                ' '
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

    if let Some(expansion) = LEGAL_SUFFIX_EXPANSIONS.get(lower.as_str()) {
        return expansion.to_string();
    }
    if let Some(expansion) = COMMON_ABBREVIATIONS.get(lower.as_str()) {
        return expansion.to_string();
    }

    lower
}

/// Expand all abbreviations in the text.
fn expand_abbreviations(text: &str) -> String {
    text.split_whitespace()
        .map(expand_token)
        .collect::<Vec<String>>()
        .join(" ")
}

/// Remove stop words from text.
fn remove_stop_words(text: &str, preserve_initial: bool) -> String {
    let tokens: Vec<&str> = text.split_whitespace().collect();
    if tokens.is_empty() {
        return String::new();
    }

    let mut out: Vec<&str> = Vec::with_capacity(tokens.len());
    for (i, token) in tokens.iter().enumerate() {
        if STOP_WORDS.contains(token) {
            if i == 0 && preserve_initial {
                out.push(*token);
            }
            continue;
        }
        out.push(*token);
    }

    out.join(" ")
}

pub fn normalize_legal_name(
    name: &str,
    remove_stop_words_flag: bool,
    preserve_initial_stop: bool,
) -> String {
    if name.is_empty() {
        return String::new();
    }

    // 1) Lowercase early
    let mut text = name.to_lowercase();

    // 2) Pre-pass for dotted/spaced legal forms (llc, sa, pllc, etc.)
    text = normalize_dotted_legal_forms(&text);

    // 3) Unicode normalization (strip diacritics, normalize some punctuation)
    text = normalize_unicode_basic(&text);

    // 4) Punctuation to spaces
    text = remove_punctuation(&text);

    // 5) Collapse whitespace
    text = collapse_whitespace(&text);

    // 6) Expand abbreviations (legal + common)
    text = expand_abbreviations(&text);

    // 7) Optional stop-word removal
    if remove_stop_words_flag {
        text = remove_stop_words(&text, preserve_initial_stop);
    }

    // 8) Final collapse
    collapse_whitespace(&text)
}

// =============================================================================
// ADDRESS NORMALIZATION
// =============================================================================

fn expand_address_abbreviations(text: &str) -> String {
    text.split_whitespace()
        .map(|t| {
            let lower = t.to_lowercase();
            if let Some(expansion) = US_ADDRESS_EXPANSIONS.get(lower.as_str()) {
                expansion.to_string()
            } else {
                lower
            }
        })
        .collect::<Vec<String>>()
        .join(" ")
}

pub fn normalize_address(address: &str, remove_secondary: bool) -> String {
    if address.is_empty() {
        return String::new();
    }

    // 1) Lowercase
    let mut text = address.to_lowercase();

    // 2) Unicode normalization
    text = normalize_unicode_basic(&text);

    // 3) Remove secondary unit designators
    if remove_secondary {
        text = SECONDARY_UNIT_REGEX.replace_all(&text, " ").to_string();
    }

    // 4) Punctuation to spaces
    text = remove_punctuation(&text);

    // 5) Collapse whitespace
    text = collapse_whitespace(&text);

    // 6) Expand address abbreviations
    text = expand_address_abbreviations(&text);

    // 7) Final collapse
    collapse_whitespace(&text)
}

// =============================================================================
// REGISTRATION DATE NORMALIZATION
// =============================================================================

pub fn normalize_registration_date(date_str: &str) -> Option<String> {
    let s = date_str.trim();
    if s.is_empty() {
        return None;
    }

    let patterns: [&'static str; 4] = [
        "%Y-%m-%d", // ISO
        "%m/%d/%Y", // US
        "%m-%d-%Y", // US dashes
        "%d/%m/%Y", // common EU
    ];

    for fmt in patterns.iter() {
        if let Ok(dt) = NaiveDate::parse_from_str(s, fmt) {
            return Some(dt.format("%Y-%m-%d").to_string());
        }
    }

    // Year only
    if let Ok(year) = s.parse::<i32>() {
        if (1000..=9999).contains(&year) {
            return Some(format!("{:04}-01-01", year));
        }
    }

    None
}

// =============================================================================
// CANONICAL INPUT BUILDER
// =============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CanonicalInput {
    pub legal_name_normalized: String,
    pub address_normalized: Option<String>,
    pub country_code: String,
    pub registration_date: Option<String>,
}

impl CanonicalInput {
    pub fn to_hash_string(&self) -> String {
        format!(
            "{}|{}|{}|{}",
            self.legal_name_normalized,
            self.address_normalized.as_deref().unwrap_or(""),
            self.country_code,
            self.registration_date.as_deref().unwrap_or(""),
        )
    }
}

pub fn build_canonical_input(
    legal_name: &str,
    country_code: &str,
    address: Option<&str>,
    registration_date: Option<&str>,
) -> CanonicalInput {
    CanonicalInput {
        legal_name_normalized: normalize_legal_name(legal_name, true, false),
        address_normalized: address.and_then(|a| {
            let normalized = normalize_address(a, true);
            if normalized.is_empty() {
                None
            } else {
                Some(normalized)
            }
        }),
        country_code: country_code.to_uppercase(),
        registration_date: registration_date.and_then(normalize_registration_date),
    }
}

#[cfg(test)]
mod normalizer_tests {
    use super::*;

    #[test]
    fn legal_name_normalization_matches_example() {
        let s = normalize_legal_name("The Springfield Unified Sch. Dist., Inc.", true, false);
        assert_eq!(s, "springfield unified school district incorporated");
    }

    #[test]
    fn legal_name_dotted_llc_is_recognized() {
        let s = normalize_legal_name("Acme L.L.C.", true, false);
        assert_eq!(s, "acme limited liability company");
    }

    #[test]
    fn address_normalization_matches_example() {
        let s = normalize_address("123 N. Main St., Suite 400", true);
        assert_eq!(s, "123 north main street");
    }
}
