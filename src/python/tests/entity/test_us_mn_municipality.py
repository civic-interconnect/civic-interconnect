# src/python/tests/entity/test_us_mn_municipality.py

import json
from pathlib import Path

from civic_interconnect.cep.adapters.us_mn_municipality import build_municipality_entity
from civic_interconnect.cep.localization import load_localization


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_mn_municipality_example_round_trip() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    print(f"Repo root: {repo_root}")

    raw_path = repo_root / "examples" / "entity" / "raw" / "municipality_us_mn_01_source.json"
    cep_path = repo_root / "examples" / "entity" / "cep" / "municipality_us_mn_01.cep.json"

    # verify raw_path and cep_path exist
    assert raw_path.exists(), f"Raw path does not exist: {raw_path}"
    assert cep_path.exists(), f"CEP path does not exist: {cep_path}"

    raw = _load_json(raw_path)
    expected = _load_json(cep_path)

    # Ensure localization loads without error
    _ = load_localization("US-MN")

    actual = build_municipality_entity(raw, localization_jurisdiction="US-MN")

    # For this first test, ignore attestationTimestamp details if you like,
    # or assert field-by-field. Here we compare the whole dict:
    assert actual == expected
