# src/python/tests/audit/test_us_il_vendor_audit.py
"""Audit test for US-IL vendor identity collisions.

This test runs the audit script end-to-end and asserts that it produces
a well-formed collisions CSV in an isolated temp directory.

Run:
  uv run pytest src/python/tests/audit/test_us_il_vendor_audit.py -s
"""

import csv
import importlib.util
import os
from pathlib import Path
import sys

import pytest

CHICAGO_SAMPLE_URL = (
    "https://raw.githubusercontent.com/"
    "civic-interconnect/civic-data-identity-us-il/"
    "refs/heads/main/data/identity/chicago_contracts_vendors_sample_20k.csv"
)

AUDIT_SCRIPT = Path("tools") / "audit_identity_collisions.py"


def _import_audit_module():
    if not AUDIT_SCRIPT.exists():
        raise AssertionError(f"Missing audit script at: {AUDIT_SCRIPT}")

    module_name = "audit_identity_collisions"
    spec = importlib.util.spec_from_file_location(module_name, AUDIT_SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Could not load module spec for: {AUDIT_SCRIPT}")

    mod = importlib.util.module_from_spec(spec)

    # Critical: make dataclasses (and similar) able to find the module during exec.
    sys.modules[module_name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        # Avoid leaving a partially-initialized module around.
        sys.modules.pop(module_name, None)
        raise

    return mod


@pytest.mark.parametrize("limit", [int(os.environ.get("CEP_AUDIT_LIMIT", "2000"))])
def test_us_il_vendor_identity_audit_produces_collisions_csv(tmp_path: Path, limit: int) -> None:
    audit = _import_audit_module()

    out_dir = tmp_path / "audit" / "us_il_vendor"
    out_dir.mkdir(parents=True, exist_ok=True)

    args = [
        "--input-url",
        CHICAGO_SAMPLE_URL,
        "--name-column",
        "Vendor Name",
        "--jurisdiction-iso",
        "US-IL",
        "--limit",
        str(limit),
        "--include-traces",
        "--out-dir",
        str(out_dir),
    ]

    # Assumes tools/audit_identity_collisions.py exposes main(argv: list[str] | None = None)
    audit.main(args)

    collisions_csv = out_dir / "collisions.csv"
    assert collisions_csv.exists(), f"Expected output file not found: {collisions_csv}"

    with collisions_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames is not None, "collisions.csv missing header row"
        fieldnames = list(reader.fieldnames)

        required = ["normalized", "count", "raw_variants_joined"]
        missing = [c for c in required if c not in fieldnames]
        assert not missing, f"collisions.csv missing columns: {missing} (found: {fieldnames})"


def main(argv: list[str] | None = None) -> None:
    """Run the audit script with provided arguments."""
    audit = _import_audit_module()
    audit.main(argv)


if __name__ == "__main__":
    main()
