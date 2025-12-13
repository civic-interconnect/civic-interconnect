// File: rust/cep-core/src/common/localization.rs
//
// YAML-driven Localization Functor (no built-ins, no filesystem).
//
// L: RawLocal -> IntermediateCanonical
// N: IntermediateCanonical -> FinalCanonical
// SNFEI = Hash(N(L(raw_data)))
//
// This module loads localization configs from embedded YAML assets generated
// by build.rs (LOCALIZATION_YAMLS), merges parent configs, and applies
// transforms deterministically.
//
// NOTE: This module intentionally does not validate YAML against JSON Schema
// at runtime. Schema validation is done in tooling/tests.

use crate::common::assets::LOCALIZATION_YAMLS;
use regex::{Regex, RegexBuilder};
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::sync::{Mutex, OnceLock};

static GLOBAL_REGISTRY: OnceLock<Mutex<Result<LocalizationRegistry, String>>> = OnceLock::new();

fn registry_mutex() -> &'static Mutex<Result<LocalizationRegistry, String>> {
    GLOBAL_REGISTRY.get_or_init(|| Mutex::new(LocalizationRegistry::new()))
}

fn with_registry_mut<T>(
    f: impl FnOnce(&mut LocalizationRegistry) -> Result<T, String>,
) -> Result<T, String> {
    let m = registry_mutex();
    let mut guard = m
        .lock()
        .map_err(|_| "Localization registry mutex poisoned".to_string())?;

    match guard.as_mut() {
        Ok(reg) => f(reg),
        Err(e) => Err(e.clone()),
    }
}

// =============================================================================
// YAML FILE SHAPES
// =============================================================================

#[derive(Debug, Clone, Deserialize)]
struct LocalizationRuleFile {
    pattern: String,
    replacement: String,

    #[serde(default)]
    is_regex: bool,

    #[serde(default)]
    scope: Option<String>,

    #[serde(default)]
    case_sensitive: bool,

    #[serde(default = "default_rule_enabled")]
    enabled: bool,

    #[serde(default)]
    order: Option<i64>,

    #[serde(default)]
    id: Option<String>,

    #[serde(default)]
    description: Option<String>,
}

fn default_rule_enabled() -> bool {
    true
}

#[derive(Debug, Clone, Deserialize)]
struct LocalizationConfigFile {
    jurisdiction: String,

    #[serde(default)]
    parent: Option<String>,

    #[serde(default)]
    version: Option<String>,

    #[serde(default)]
    updated_timestamp: Option<String>,

    #[serde(default)]
    config_hash: Option<String>,

    #[serde(default)]
    abbreviations: HashMap<String, String>,

    #[serde(default)]
    agency_names: HashMap<String, String>,

    #[serde(default)]
    entity_types: HashMap<String, String>,

    #[serde(default)]
    rules: Vec<LocalizationRuleFile>,

    #[serde(default)]
    stop_words: Vec<String>,
}

// =============================================================================
// RESOLVED / RUNTIME STRUCTS
// =============================================================================

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct LocalizationRule {
    pub pattern: String,
    pub replacement: String,
    pub is_regex: bool,
    pub scope: Option<String>,
    pub case_sensitive: bool,
    pub enabled: bool,
    pub order: Option<i64>,
    pub id: Option<String>,
    pub description: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct LocalizationConfig {
    pub jurisdiction: String,
    pub parent: Option<String>,
    pub version: Option<String>,
    pub updated_timestamp: Option<String>,
    pub config_hash: Option<String>,
    pub abbreviations: HashMap<String, String>,
    pub agency_names: HashMap<String, String>,
    pub entity_types: HashMap<String, String>,
    pub rules: Vec<LocalizationRule>,
    pub stop_words: HashSet<String>,
}

impl Default for LocalizationConfig {
    fn default() -> Self {
        Self {
            jurisdiction: "unknown".to_string(),
            parent: None,
            version: None,
            updated_timestamp: None,
            config_hash: None,
            abbreviations: HashMap::new(),
            agency_names: HashMap::new(),
            entity_types: HashMap::new(),
            rules: Vec::new(),
            stop_words: HashSet::new(),
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct LocalizationApplyProvenance {
    // Requested jurisdiction (normalized to internal key style)
    pub requested_key: String,
    // Which embedded YAML keys were used (after parent merge)
    pub resolved_keys: Vec<String>,
    // Config hashes (if present in YAML) in the same order as resolved_keys
    pub resolved_config_hashes: Vec<Option<String>>,
}

#[derive(Debug, Clone, Serialize)]
pub struct LocalizationApplyResult {
    pub output: String,
    pub provenance: LocalizationApplyProvenance,
}

// Internal compiled form (avoid recompiling regex each call)
#[derive(Debug, Clone)]
struct CompiledRule {
    rule: LocalizationRule,
    regex: Option<Regex>,
}

#[derive(Debug, Clone)]
pub struct CompiledConfig {
    cfg: LocalizationConfig,
    // agency_names + entity_types are word-boundary regex substitutions
    agency_regexes: Vec<(Regex, String)>,
    entity_type_regexes: Vec<(Regex, String)>,
    compiled_rules: Vec<CompiledRule>,
}

// =============================================================================
// KEY NORMALIZATION
// =============================================================================

fn normalize_key(input: &str) -> String {
    let s = input.trim();

    if s.eq_ignore_ascii_case("base") {
        return "base".to_string();
    }

    // Allow ISO 3166-2 inputs like "US-IL" and also already-path-like "us/il".
    // Normalize to lower with "/" separators.
    let s = s.replace('-', "/");
    s.to_lowercase()
}

// =============================================================================
// PARSING AND MERGING
// =============================================================================

fn parse_yaml_to_config(key: &str, yaml_text: &str) -> Result<LocalizationConfig, String> {
    let file_cfg: LocalizationConfigFile =
        serde_yaml::from_str(yaml_text).map_err(|e| format!("YAML parse error for {key}: {e}"))?;

    // Canonicalize parent/jurisdiction values to internal lookup keys.
    let jurisdiction_key = normalize_key(&file_cfg.jurisdiction);
    let parent_key = file_cfg.parent.as_ref().map(|p| normalize_key(p));

    // Normalize maps/stop words to lowercase tokens.
    let abbreviations = file_cfg
        .abbreviations
        .into_iter()
        .map(|(k, v)| (k.to_lowercase(), v.to_lowercase()))
        .collect();

    let agency_names = file_cfg
        .agency_names
        .into_iter()
        .map(|(k, v)| (k.to_lowercase(), v.to_lowercase()))
        .collect();

    let entity_types = file_cfg
        .entity_types
        .into_iter()
        .map(|(k, v)| (k.to_lowercase(), v.to_lowercase()))
        .collect();

    let rules = file_cfg
        .rules
        .into_iter()
        .map(|r| LocalizationRule {
            pattern: r.pattern,
            replacement: r.replacement,
            is_regex: r.is_regex,
            scope: r.scope,
            case_sensitive: r.case_sensitive,
            enabled: r.enabled,
            order: r.order,
            id: r.id,
            description: r.description,
        })
        .collect();

    let stop_words: HashSet<String> = file_cfg
        .stop_words
        .into_iter()
        .map(|s| s.to_lowercase())
        .collect();

    Ok(LocalizationConfig {
        jurisdiction: jurisdiction_key,
        parent: parent_key,
        version: file_cfg.version,
        updated_timestamp: file_cfg.updated_timestamp,
        config_hash: file_cfg.config_hash,
        abbreviations,
        agency_names,
        entity_types,
        rules,
        stop_words,
    })
}

fn merge_configs(child: &LocalizationConfig, parent: &LocalizationConfig) -> LocalizationConfig {
    let mut merged_abbrevs = parent.abbreviations.clone();
    merged_abbrevs.extend(child.abbreviations.clone());

    let mut merged_agencies = parent.agency_names.clone();
    merged_agencies.extend(child.agency_names.clone());

    let mut merged_types = parent.entity_types.clone();
    merged_types.extend(child.entity_types.clone());

    // Rules: parent first then child
    let mut merged_rules = parent.rules.clone();
    merged_rules.extend(child.rules.clone());

    let merged_stop_words: HashSet<String> = parent
        .stop_words
        .union(&child.stop_words)
        .cloned()
        .collect();

    LocalizationConfig {
        jurisdiction: child.jurisdiction.clone(),
        parent: child.parent.clone().or_else(|| parent.parent.clone()),
        version: child.version.clone().or_else(|| parent.version.clone()),
        updated_timestamp: child
            .updated_timestamp
            .clone()
            .or_else(|| parent.updated_timestamp.clone()),
        config_hash: child
            .config_hash
            .clone()
            .or_else(|| parent.config_hash.clone()),
        abbreviations: merged_abbrevs,
        agency_names: merged_agencies,
        entity_types: merged_types,
        rules: merged_rules,
        stop_words: merged_stop_words,
    }
}

// =============================================================================
// APPLY LOGIC
// =============================================================================

fn collapse_whitespace(s: &str) -> String {
    s.split_whitespace().collect::<Vec<&str>>().join(" ")
}

fn compile_config(cfg: LocalizationConfig) -> Result<CompiledConfig, String> {
    // Precompile agency_name substitutions with word boundaries and case-insensitive matching.
    let mut agency_regexes = Vec::with_capacity(cfg.agency_names.len());
    for (k, v) in cfg.agency_names.iter() {
        let escaped = regex::escape(k);
        let pat = format!(r"\b{}\b", escaped);
        let re = RegexBuilder::new(&pat)
            .case_insensitive(true)
            .build()
            .map_err(|e| format!("Failed compiling agency_names regex {pat}: {e}"))?;
        agency_regexes.push((re, v.clone()));
    }

    // Precompile entity_type substitutions similarly.
    let mut entity_type_regexes = Vec::with_capacity(cfg.entity_types.len());
    for (k, v) in cfg.entity_types.iter() {
        let escaped = regex::escape(k);
        let pat = format!(r"\b{}\b", escaped);
        let re = RegexBuilder::new(&pat)
            .case_insensitive(true)
            .build()
            .map_err(|e| format!("Failed compiling entity_types regex {pat}: {e}"))?;
        entity_type_regexes.push((re, v.clone()));
    }

    // Respect optional explicit order; stable sort by (order, original_index).
    let mut rules_indexed: Vec<(usize, LocalizationRule)> =
        cfg.rules.iter().cloned().enumerate().collect();
    rules_indexed.sort_by(|(ia, ra), (ib, rb)| {
        let oa = ra.order.unwrap_or(i64::MAX);
        let ob = rb.order.unwrap_or(i64::MAX);
        oa.cmp(&ob).then(ia.cmp(ib))
    });

    let mut compiled_rules = Vec::with_capacity(rules_indexed.len());
    for (_idx, rule) in rules_indexed.into_iter() {
        if !rule.enabled {
            compiled_rules.push(CompiledRule { rule, regex: None });
            continue;
        }

        if rule.is_regex {
            let re = RegexBuilder::new(&rule.pattern)
                .case_insensitive(!rule.case_sensitive)
                .build()
                .map_err(|e| format!("Failed compiling rule regex {}: {e}", rule.pattern))?;
            compiled_rules.push(CompiledRule {
                rule,
                regex: Some(re),
            });
        } else {
            compiled_rules.push(CompiledRule { rule, regex: None });
        }
    }

    Ok(CompiledConfig {
        cfg,
        agency_regexes,
        entity_type_regexes,
        compiled_rules,
    })
}

impl CompiledConfig {
    fn apply_to_name(&self, name: &str) -> String {
        // Start by lowercasing.
        // All rules/maps are case-insensitive or normalized to lowercase.
        let mut result = name.to_lowercase();

        // 1) Agency names (word boundary, case-insensitive)
        for (re, full) in self.agency_regexes.iter() {
            result = re.replace_all(&result, full.as_str()).to_string();
        }
        result = collapse_whitespace(&result);

        // 2) Abbreviations (token-based expansion)
        let tokens: Vec<&str> = result.split_whitespace().collect();
        let mut expanded = Vec::with_capacity(tokens.len());
        for tok in tokens.iter() {
            if let Some(v) = self.cfg.abbreviations.get(*tok) {
                expanded.push(v.as_str());
            } else {
                expanded.push(*tok);
            }
        }
        result = expanded.join(" ");
        result = collapse_whitespace(&result);

        // 3) Entity types (word boundary, case-insensitive)
        for (re, canonical) in self.entity_type_regexes.iter() {
            result = re.replace_all(&result, canonical.as_str()).to_string();
        }
        result = collapse_whitespace(&result);

        // 4) Custom rules (ordered; regex or literal)
        for cr in self.compiled_rules.iter() {
            if !cr.rule.enabled {
                continue;
            }

            if cr.rule.is_regex {
                if let Some(re) = cr.regex.as_ref() {
                    result = re
                        .replace_all(&result, cr.rule.replacement.as_str())
                        .to_string();
                }
            } else {
                // Literal replace. If rule is case_sensitive, apply to the original casing would matter,
                // but at this stage we are already in lowercase. This matches typical CEP behavior.
                result = result.replace(
                    &cr.rule.pattern.to_lowercase(),
                    &cr.rule.replacement.to_lowercase(),
                );
            }

            result = collapse_whitespace(&result);
        }

        // 5) Stop words (token removal)
        if !self.cfg.stop_words.is_empty() {
            let tokens: Vec<&str> = result.split_whitespace().collect();
            let mut kept = Vec::with_capacity(tokens.len());
            for tok in tokens.iter() {
                if !self.cfg.stop_words.contains(*tok) {
                    kept.push(*tok);
                }
            }
            result = kept.join(" ");
            result = collapse_whitespace(&result);
        }

        result
    }
}

// =============================================================================
// REGISTRY (embedded assets, cached resolved configs)
// =============================================================================

#[derive(Debug)]
pub struct LocalizationRegistry {
    // Base configs loaded from embedded YAML by key, e.g. "us", "us/il", "base"
    base_by_key: HashMap<String, LocalizationConfig>,
    // Compiled + merged cache for requested jurisdiction keys
    compiled_cache: HashMap<String, CompiledConfig>,
    // For provenance: keep parent chain resolution keys
    resolved_key_chains: HashMap<String, Vec<String>>,
}

impl LocalizationRegistry {
    pub fn new() -> Result<Self, String> {
        let mut base_by_key: HashMap<String, LocalizationConfig> = HashMap::new();

        for (key, yaml_text) in LOCALIZATION_YAMLS.iter() {
            let k = normalize_key(key);
            let cfg = parse_yaml_to_config(&k, yaml_text)?;

            // Sanity: if YAML says jurisdiction "US" but key is "us", normalize and accept.
            base_by_key.insert(k, cfg);
        }

        Ok(Self {
            base_by_key,
            compiled_cache: HashMap::new(),
            resolved_key_chains: HashMap::new(),
        })
    }

    fn get_base(&self, key: &str) -> Option<&LocalizationConfig> {
        self.base_by_key.get(key)
    }

    fn resolve_chain(&self, requested_key: &str) -> Vec<String> {
        // Preferred: follow parent field if present.
        // Fallback: if missing and contains '/', fall back to truncation.
        // Final fallback: "base" if present.
        let mut chain: Vec<String> = Vec::new();
        let mut current = requested_key.to_string();

        let mut safety = 0;
        while safety < 50 {
            safety += 1;

            if let Some(cfg) = self.get_base(&current) {
                // Add this key and then walk parent if present
                chain.push(current.clone());

                if let Some(parent) = cfg.parent.as_ref() {
                    let parent_key = normalize_key(parent);
                    if parent_key == current {
                        break;
                    }
                    current = parent_key;
                    continue;
                }
                break;
            }

            // No config at this key; path fallback
            if current.contains('/') {
                current = current.rsplit('/').nth(1).unwrap_or("").to_string();
                continue;
            }

            // Try global base last
            if current != "base" && self.get_base("base").is_some() {
                current = "base".to_string();
                continue;
            }

            break;
        }

        // We built from child->parent; we want merge order parent->child.
        chain.reverse();
        chain
    }

    fn merged_config_for_chain(&self, chain: &[String], requested_key: &str) -> LocalizationConfig {
        // If chain is empty, return empty config with the requested_key.
        if chain.is_empty() {
            return LocalizationConfig {
                jurisdiction: requested_key.to_string(),
                ..Default::default()
            };
        }

        // Start from first (parent-most) then merge down to child-most
        let mut merged = self
            .get_base(&chain[0])
            .cloned()
            .unwrap_or_else(|| LocalizationConfig {
                jurisdiction: requested_key.to_string(),
                ..Default::default()
            });

        for key in chain.iter().skip(1) {
            if let Some(child) = self.get_base(key) {
                merged = merge_configs(child, &merged);
            }
        }

        merged.jurisdiction = requested_key.to_string();
        merged
    }

    pub fn get_compiled(
        &mut self,
        jurisdiction_input: &str,
    ) -> Result<(CompiledConfig, LocalizationApplyProvenance), String> {
        let requested_key = normalize_key(jurisdiction_input);

        if let Some(existing) = self.compiled_cache.get(&requested_key) {
            let chain = self
                .resolved_key_chains
                .get(&requested_key)
                .cloned()
                .unwrap_or_else(|| vec![]);

            let hashes = chain
                .iter()
                .map(|k| self.get_base(k).and_then(|c| c.config_hash.clone()))
                .collect::<Vec<_>>();

            return Ok((
                existing.clone(),
                LocalizationApplyProvenance {
                    requested_key,
                    resolved_keys: chain,
                    resolved_config_hashes: hashes,
                },
            ));
        }

        let chain = self.resolve_chain(&requested_key);
        let merged = self.merged_config_for_chain(&chain, &requested_key);
        let compiled = compile_config(merged)?;

        self.compiled_cache.insert(requested_key.clone(), compiled);
        self.resolved_key_chains
            .insert(requested_key.clone(), chain.clone());

        let hashes = chain
            .iter()
            .map(|k| self.get_base(k).and_then(|c| c.config_hash.clone()))
            .collect::<Vec<_>>();

        let compiled_ref = self
            .compiled_cache
            .get(&requested_key)
            .expect("compiled cache just inserted");

        Ok((
            compiled_ref.clone(),
            LocalizationApplyProvenance {
                requested_key,
                resolved_keys: chain,
                resolved_config_hashes: hashes,
            },
        ))
    }
}

// =============================================================================
// PUBLIC API
// =============================================================================

pub fn apply_localization_name(name: &str, jurisdiction: &str) -> Result<String, String> {
    with_registry_mut(|reg| {
        let (compiled, _prov) = reg.get_compiled(jurisdiction)?;
        Ok(compiled.apply_to_name(name))
    })
}

pub fn apply_localization_name_detailed(
    name: &str,
    jurisdiction: &str,
) -> Result<LocalizationApplyResult, String> {
    with_registry_mut(|reg| {
        let (compiled, prov) = reg.get_compiled(jurisdiction)?;
        Ok(LocalizationApplyResult {
            output: compiled.apply_to_name(name),
            provenance: prov,
        })
    })
}

// Convenience: JSON for FFI
pub fn apply_localization_name_detailed_json(
    name: &str,
    jurisdiction: &str,
) -> Result<String, String> {
    let res = apply_localization_name_detailed(name, jurisdiction)?;
    serde_json::to_string(&res).map_err(|e| e.to_string())
}

// =============================================================================
// TESTS
// =============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn key_normalization_accepts_us_il() {
        assert_eq!(normalize_key("US-IL"), "us/il");
        assert_eq!(normalize_key("us/il"), "us/il");
        assert_eq!(normalize_key("US"), "us");
        assert_eq!(normalize_key("BASE"), "base");
    }
}
