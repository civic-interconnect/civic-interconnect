# src/python/ci_cep/localization.py
"""Apply localization configurations for different jurisdictions."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class LocalizationConfig:
    """Configuration for jurisdiction-specific localization settings.

    Attributes:
    jurisdiction : str
        The jurisdiction code (e.g., 'BASE', 'US', 'US-MN').
    parent : str | None
        The parent jurisdiction from which this config inherits.
    version : str
        The version of this localization configuration.
    updated_timestamp : str
        ISO timestamp of when this configuration was last updated.
    config_hash : str | None
        Optional hash of the configuration for versioning.
    abbreviations : dict[str, str]
        Mapping of abbreviations to their expanded forms.
    agency_names : dict[str, str]
        Mapping of agency name aliases to canonical names.
    entity_types : dict[str, str]
        Mapping of entity type aliases to canonical types.
    rules : list[dict[str, Any]]
        List of jurisdiction-specific rules.
    stop_words : list[str]
        List of words to ignore during normalization.
    """

    jurisdiction: str
    parent: str | None
    version: str
    updated_timestamp: str
    config_hash: str | None
    abbreviations: dict[str, str]
    agency_names: dict[str, str]
    entity_types: dict[str, str]
    rules: list[dict[str, Any]]
    stop_words: list[str]


def _find_repo_root() -> Path:
    """Find the repository root by walking up until we see 'localization/'."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "localization").is_dir():
            return parent
    raise RuntimeError("Could not locate 'localization' directory relative to this file.")


_REPO_ROOT = _find_repo_root()
_LOCALIZATION_DIR = _REPO_ROOT / "localization"

# In-memory cache so we do not reread the same YAML over and over.
_LOCALIZATION_CACHE: dict[str, LocalizationConfig] = {}


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Localization file {path} must contain a mapping at top level.")
    return data


def _config_path_for_jurisdiction(jurisdiction: str) -> Path | None:
    """Map a jurisdiction code to a YAML file path.

    For example:
    - 'BASE'   -> localization/base.yaml
    - 'US'     -> localization/us/base.yaml (or localization/us.yaml, depending on how you organize)
    - 'US-MN'  -> localization/us/mn.yaml

    For now we assume:
    - BASE:     localization/base.yaml
    - US:       localization/us/base.yaml
    - US-XX:    localization/us/xx.yaml  (lowercase state code)
    """
    if jurisdiction == "BASE":
        candidate = _LOCALIZATION_DIR / "base.yaml"
        return candidate if candidate.exists() else None

    if jurisdiction == "US":
        # US-wide config in localization/us/base.yaml
        candidate = _LOCALIZATION_DIR / "us" / "base.yaml"
        return candidate if candidate.exists() else None

    if "-" in jurisdiction:
        country, region = jurisdiction.split("-", 1)
        if country == "US":
            candidate = _LOCALIZATION_DIR / "us" / f"{region.lower()}.yaml"
            return candidate if candidate.exists() else None

    # Fallback: try "<jurisdiction>.yaml" at root
    candidate = _LOCALIZATION_DIR / f"{jurisdiction}.yaml"
    return candidate if candidate.exists() else None


def _merge_dict(parent: dict[str, Any], child: dict[str, Any]) -> dict[str, Any]:
    """Shallow merge two dicts with child overriding parent keys."""
    merged = dict(parent)
    merged.update(child)
    return merged


def _merge_lists(parent: list[Any], child: list[Any]) -> list[Any]:
    """Concatenate parent and child lists."""
    return list(parent) + list(child)


def _build_localization_config(jurisdiction: str) -> LocalizationConfig:
    """Load and cascade localization configs for a jurisdiction.

    Example cascade:
        BASE -> US -> US-MN
    """
    path = _config_path_for_jurisdiction(jurisdiction)
    if path is None:
        raise FileNotFoundError(f"No localization config found for jurisdiction '{jurisdiction}'.")

    raw = _load_yaml(path)

    # Read current config's metadata
    parent_jur = raw.get("parent")
    version = str(raw.get("version", "1.0.0"))
    updated = str(raw.get("updatedTimestamp", "1970-01-01T00:00:00Z"))
    config_hash = raw.get("configHash")

    # Load parent first (if any), then merge this config on top.
    if parent_jur:
        parent_cfg = load_localization(parent_jur)
        # Merge dict fields
        abbreviations = _merge_dict(parent_cfg.abbreviations, raw.get("abbreviations", {}) or {})
        agency_names = _merge_dict(parent_cfg.agency_names, raw.get("agency_names", {}) or {})
        entity_types = _merge_dict(parent_cfg.entity_types, raw.get("entity_types", {}) or {})
        # Merge list fields
        rules = _merge_lists(parent_cfg.rules, raw.get("rules", []) or [])
        stop_words = _merge_lists(parent_cfg.stop_words, raw.get("stop_words", []) or [])
    else:
        abbreviations = raw.get("abbreviations", {}) or {}
        agency_names = raw.get("agency_names", {}) or {}
        entity_types = raw.get("entity_types", {}) or {}
        rules = raw.get("rules", []) or []
        stop_words = raw.get("stop_words", []) or []

    # Normalize types
    if not isinstance(abbreviations, dict):
        raise ValueError(f"'abbreviations' must be an object in {path}")
    if not isinstance(agency_names, dict):
        raise ValueError(f"'agency_names' must be an object in {path}")
    if not isinstance(entity_types, dict):
        raise ValueError(f"'entity_types' must be an object in {path}")
    if not isinstance(rules, list):
        raise ValueError(f"'rules' must be an array in {path}")
    if not isinstance(stop_words, list):
        raise ValueError(f"'stop_words' must be an array in {path}")

    return LocalizationConfig(
        jurisdiction=jurisdiction,
        parent=parent_jur,
        version=version,
        updated_timestamp=updated,
        config_hash=config_hash,
        abbreviations=abbreviations,
        agency_names=agency_names,
        entity_types=entity_types,
        rules=rules,
        stop_words=stop_words,
    )


def load_localization(jurisdiction: str) -> LocalizationConfig:
    """Public entry point: get a cascaded LocalizationConfig, with caching."""
    if jurisdiction in _LOCALIZATION_CACHE:
        return _LOCALIZATION_CACHE[jurisdiction]
    cfg = _build_localization_config(jurisdiction)
    _LOCALIZATION_CACHE[jurisdiction] = cfg
    return cfg


def normalize_name(raw_name: str, config: LocalizationConfig) -> str:
    """Very simple first-pass normalizer.

    - lowercases
    - strips leading/trailing whitespace
    - replaces abbreviations as whole-word tokens when possible
    - trims stop words
    - applies simple agency_names mapping if exact match
    """
    if not raw_name:
        return ""

    text = raw_name.strip().lower()

    # Exact agency name override first (common for "nyc", "mn", etc.).
    if text in config.agency_names:
        return config.agency_names[text]

    # Tokenize on whitespace.
    tokens = text.split()

    # Expand abbreviations and drop stop words.
    expanded_tokens: list[str] = []
    for tok in tokens:
        if tok in config.stop_words:
            continue
        if tok in config.abbreviations:
            expanded_tokens.extend(config.abbreviations[tok].split())
        else:
            expanded_tokens.append(tok)

    normalized = " ".join(expanded_tokens)

    # Apply agency_names again in case expansion matched a known alias.
    if normalized in config.agency_names:
        return config.agency_names[normalized]

    return normalized
