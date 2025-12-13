"""
Tests for SNFEI identity normalization of US-IL vendor names.

Run with:
    uv run pytest src/python/tests/identity/test_us_il_vendor_snfei.py -s
"""

import csv
import json
from pathlib import Path

from civic_interconnect.cep.adapters.procurement.us_il_vendor import UsIlVendorAdapter
from civic_interconnect.cep.localization import (
    apply_localization_name,
    apply_localization_name_detailed_json,
)
import pandas as pd

DEBUG = True  # Set False in CI if needed

CHICAGO_SAMPLE_URL = (
    "https://raw.githubusercontent.com/"
    "civic-interconnect/civic-data-identity-us-il/"
    "refs/heads/main/data/identity/chicago_contracts_vendors_sample_20k.csv"
)


def test_us_il_localization_known_case_cleaned_up_marker_removed_via_adapter() -> None:
    """
    End-to-end pin: adapter.canonicalize() must apply US-IL localization rules.
    """
    adapter = UsIlVendorAdapter()

    raw = {"vendor_name": "MCDERMOTT CENTER|CLEANED-UP", "jurisdiction_iso": "US-IL"}
    canonical = adapter.canonicalize(raw)

    # Pass if localization YAML rules are being applied (in Rust).
    assert canonical["legalNameNormalized"] == "mcdermott center"


def test_us_il_localization_known_case_cleaned_up_marker_removed_via_ffi() -> None:
    """
    Direct pin: Rust FFI fast path must remove Chicago dataset cleaned-up marker.
    """
    out = apply_localization_name("MCDERMOTT CENTER|CLEANED-UP", "US-IL")
    assert out == "mcdermott center"


def test_us_il_localization_known_case_provenance_json_shape() -> None:
    """
    Audit pin: Rust FFI detailed JSON must return output + provenance fields.
    """
    detailed_json = apply_localization_name_detailed_json(
        "MCDERMOTT CENTER|CLEANED-UP",
        "US-IL",
    )
    obj = json.loads(detailed_json)

    assert isinstance(obj, dict)
    assert obj.get("output") == "mcdermott center"

    prov = obj.get("provenance")
    assert isinstance(prov, dict)

    # Keep these assertions intentionally minimal to avoid brittleness if the
    # parent-chain strategy evolves.
    assert prov.get("requested_key") in {"us/il", "us-il", "US-IL"}
    assert isinstance(prov.get("resolved_keys"), list)
    assert isinstance(prov.get("resolved_config_hashes"), list)

    if DEBUG:
        print("\nPinned localization provenance:\n" + json.dumps(obj, indent=2, ensure_ascii=False))


def test_snfei_chicago_vendors_subset() -> None:
    adapter = UsIlVendorAdapter()

    df = pd.read_csv(CHICAGO_SAMPLE_URL, dtype=str)
    assert not df.empty

    col = "Vendor Name" if "Vendor Name" in df.columns else "vendor_name"
    assert col in df.columns

    names = df[col].dropna().head(2000)
    assert not names.empty

    rows: list[dict[str, str]] = []

    for raw_name in names:
        raw = {"vendor_name": raw_name, "jurisdiction_iso": "US-IL"}

        canonical = adapter.canonicalize(raw)
        aligned = adapter.align_schema(canonical)
        with_id = adapter.compute_identity(aligned)

        sn = with_id["identifiers"]["snfei"]["value"]
        assert isinstance(sn, str)
        assert len(sn) == 64

        assert canonical["legalNameNormalized"]

        if DEBUG:
            rows.append(
                {
                    "raw_vendor_name": raw_name,
                    "normalized_vendor_name": canonical["legalNameNormalized"],
                    "snfei": sn,
                }
            )

    if DEBUG:
        out_dir = Path("out")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "us_il_normalized_sample.csv"

        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["raw_vendor_name", "normalized_vendor_name", "snfei"],
            )
            writer.writeheader()
            writer.writerows(rows)

        print(f"\nWrote {len(rows)} rows to {out_path}\n")
