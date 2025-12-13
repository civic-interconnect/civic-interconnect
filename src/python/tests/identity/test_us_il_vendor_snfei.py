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


def test_debug_loaded_modules_and_paths() -> None:
    import civic_interconnect
    import civic_interconnect.cep
    import civic_interconnect.cep.localization as loc

    print("\nPython package paths:")
    print("civic_interconnect.__file__ =", getattr(civic_interconnect, "__file__", None))
    print("civic_interconnect.cep.__file__ =", getattr(civic_interconnect.cep, "__file__", None))
    print("civic_interconnect.cep.localization.__file__ =", getattr(loc, "__file__", None))

    # If you have a compiled extension module, it will typically be a .pyd on Windows.
    # Try a couple common names; adjust if yours differs.
    candidates = [
        "civic_interconnect._rust",
        "civic_interconnect.cep._rust",
        "civic_interconnect.cep.snfei._rust",
    ]
    for name in candidates:
        try:
            mod = __import__(name, fromlist=["*"])
        except Exception as e:
            print(f"{name} import: {type(e).__name__}: {e}")
            continue
        print(f"{name}.__file__ = {getattr(mod, '__file__', None)}")


def _get_localization_provenance(input_name: str, jurisdiction_iso: str) -> dict:
    detailed_json = apply_localization_name_detailed_json(input_name, jurisdiction_iso)
    obj = json.loads(detailed_json)
    assert isinstance(obj, dict), "FFI detailed_json must decode to a dict"
    prov = obj.get("provenance")
    assert isinstance(prov, dict), "FFI detailed_json must include provenance dict"
    return obj


def test_localization_assets_present_and_nonempty_for_us_il() -> None:
    """
    Diagnostic: prove that the Rust crate actually loaded localization YAML
    assets and resolved at least one config for US-IL.

    If this fails, build.rs likely did not embed/copy localization assets,
    or repo_root resolution is wrong, or the runtime resolver can't see them.
    """
    obj = _get_localization_provenance("MCDERMOTT CENTER|CLEANED-UP", "US-IL")
    prov = obj["provenance"]

    resolved_keys = prov.get("resolved_keys")
    resolved_hashes = prov.get("resolved_config_hashes")

    assert isinstance(resolved_keys, list), "resolved_keys must be a list"
    assert isinstance(resolved_hashes, list), "resolved_config_hashes must be a list"

    # The key check is intentionally flexible, but we require it to resolve *something*.
    assert len(resolved_keys) > 0, (
        "No localization configs were resolved. "
        "This usually means localization YAML assets were not found/embedded."
    )
    assert len(resolved_hashes) > 0, (
        "No localization config hashes were reported. "
        "This usually means configs were not loaded or provenance is broken."
    )

    # Stronger: require that some resolved key looks like it targets US and IL.
    lowered = [str(k).lower() for k in resolved_keys]
    assert any(k in {"us/il", "us-il", "us_il"} or k.endswith("/il") for k in lowered), (
        f"Resolved keys did not include an IL-specific entry. resolved_keys={resolved_keys}"
    )

    # Useful in debug mode
    if DEBUG:
        print("\nResolved localization keys:", resolved_keys)
        print("Resolved localization hashes:", resolved_hashes)


def test_localization_rule_effect_is_observable_in_output() -> None:
    """
    Diagnostic: verify that at least one rule actually changed the string
    in a way we expect (marker removal), not just 'resolved something'.
    """
    raw = "MCDERMOTT CENTER|CLEANED-UP"
    out = apply_localization_name(raw, "US-IL")

    assert out != raw.lower(), (
        "Localization appears to have done no work (output equals lowercased input). "
        "If assets aren't loaded, you often see only trivial normalization."
    )
    assert "|cleaned-up" not in out, (
        "The cleaned-up marker was not removed. "
        "Either the IL rule set wasn't loaded or the marker-stripping rule isn't present."
    )


def test_localization_detailed_json_has_minimum_expected_fields() -> None:
    """
    Diagnostic: makes failures clearer by asserting the provenance payload contains
    the fields we depend on for debugging asset loading.
    """
    obj = _get_localization_provenance("MCDERMOTT CENTER|CLEANED-UP", "US-IL")
    prov = obj["provenance"]

    # Minimum fields that help pinpoint failures
    for field in ["requested_key", "resolved_keys", "resolved_config_hashes"]:
        assert field in prov, f"provenance missing required field '{field}': {prov}"

    # requested_key should be jurisdiction-ish
    req = prov.get("requested_key")
    assert isinstance(req, str) and req, f"requested_key must be a non-empty string: {req!r}"

    if DEBUG:
        print(
            "\nPinned localization detailed JSON:\n" + json.dumps(obj, indent=2, ensure_ascii=False)
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
