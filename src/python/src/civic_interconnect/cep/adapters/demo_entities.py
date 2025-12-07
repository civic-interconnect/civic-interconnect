"""Demo adapters for CEP Entity examples.

This module provides helper functions for working with example "slice"
directories such as:

    examples/entity/municipality/us_il_01/

A slice is any directory that contains:

    01_raw_source.json

These helpers are used by the CLI, but are also importable by tests or
notebooks for experimentation.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

RAW_FILENAME = "01_raw_source.json"


def find_example_slices(root: Path) -> list[Path]:
    """Return all example slice directories that contain 01_raw_source.json.

    If `root` is itself a slice dir, include it. Otherwise, search recursively.

    This is intentionally file-system based so it works the same for CLI,
    tests, and notebooks.
    """
    slices: list[Path] = []

    if root.is_dir() and (root / "01_raw_source.json").is_file():
        slices.append(root)

    # Recurse for nested slices
    for raw_file in root.rglob("01_raw_source.json"):
        slices.append(raw_file.parent)

    # De-duplicate while preserving order
    seen: set[Path] = set()
    unique: list[Path] = []
    for s in slices:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique


def load_raw_source(slice_dir: Path) -> dict[str, Any]:
    """Load the 01_raw_source.json for a slice, with friendly errors.

    Raises:
        FileNotFoundError: if the raw file is missing.
        ValueError: if the file exists but is not valid JSON.
    """
    raw_path = slice_dir / RAW_FILENAME
    if not raw_path.is_file():
        raise FileNotFoundError(f"Raw source not found: {raw_path}")

    try:
        with raw_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Raw source {raw_path} is not valid JSON: {exc}") from exc


@dataclass
class ExampleEntityInputs:
    """Minimal inputs needed to drive the Entity pipeline for examples."""

    jurisdiction_iso: str
    legal_name: str
    country_code: str
    entity_type: str
    address: str | None
    registration_date: str | None


def extract_example_entity_inputs(raw: dict[str, Any], slice_dir: Path) -> ExampleEntityInputs:
    """Map messy raw shapes from example slices into normalized inputs.

    This is intentionally simple and example-focused. It supports the
    current demo shapes:

    - municipality: official_name + state + country
    - nonprofit: legalName, countryCode, registrationDate
    - pac: committee_name, fec_id, etc.
    - school_district: district_name + state + country

    If a required field is missing, it raises KeyError with a combined
    key hint so callers can emit friendly messages.
    """
    # jurisdictionIso: prefer explicit, then raw "jurisdiction",
    # otherwise derive from state + country.
    if "jurisdictionIso" in raw:
        jurisdiction_iso = str(raw["jurisdictionIso"])
    elif "jurisdiction" in raw:
        jurisdiction_iso = str(raw["jurisdiction"])
    else:
        state = raw.get("state")
        country_code_raw = raw.get("country") or raw.get("countryCode")
        if not state or not country_code_raw:
            raise KeyError("jurisdictionIso/jurisdiction/state/country")
        jurisdiction_iso = f"{country_code_raw}-{state}"

    # legalName: try the common example keys in order.
    legal_name = (
        raw.get("legalName")
        or raw.get("official_name")
        or raw.get("committee_name")
        or raw.get("district_name")
        or raw.get("name")
    )
    if not legal_name:
        raise KeyError("legalName/official_name/committee_name/district_name/name")
    legal_name_str = str(legal_name)

    # countryCode: explicit or from "country", default US for demos.
    country_code = str(raw.get("countryCode") or raw.get("country") or "US")

    # entityType: explicit or infer from folder name
    entity_type = str(raw.get("entityType") or slice_dir.parent.name)

    address = raw.get("address")
    registration_date = raw.get("registrationDate")

    return ExampleEntityInputs(
        jurisdiction_iso=jurisdiction_iso,
        legal_name=legal_name_str,
        country_code=country_code,
        entity_type=entity_type,
        address=address,
        registration_date=registration_date,
    )
