import json
from pathlib import Path

EXAMPLES_DIR = Path("examples/verticals/sme")


def test_example_files_exist() -> None:
    paths = [
        EXAMPLES_DIR / "raw" / "sample_ocds_release.json",
        EXAMPLES_DIR / "cep" / "lot.entity.json",
        EXAMPLES_DIR / "cee" / "explanation_bundle.sme.json",
    ]
    for path in paths:
        assert path.exists(), f"Missing example file: {path}"


def test_raw_release_is_valid_json() -> None:
    raw_path = EXAMPLES_DIR / "raw" / "sample_ocds_release.json"
    if not raw_path.exists():
        # If the example is missing, let the existence test fail instead of this one.
        return

    with raw_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Very light sanity check so the file is not just arbitrary junk.
    assert isinstance(data, (dict, list)), (
        "Expected JSON object or array in sample_ocds_release.json"
    )


def test_example_explanation_links_to_lot_and_has_core_fields() -> None:
    cee_path = EXAMPLES_DIR / "cee" / "explanation_bundle.sme_friendly.example.json"
    lot_path = EXAMPLES_DIR / "cep" / "lot.entity.json"

    if not (cee_path.exists() and lot_path.exists()):
        # Let the existence test handle failures.
        return

    with cee_path.open("r", encoding="utf-8") as f:
        bundle = json.load(f)
    with lot_path.open("r", encoding="utf-8") as f:
        lot = json.load(f)

    # Linkage: explanation must point at the lot entity.
    assert bundle["subjectEntityId"] == lot["id"]

    # Core CEE shape checks (adapt keys as CEE schema finalizes).
    assert bundle.get("explanationType") == "SME_FRIENDLY_PROCUREMENT"
    assert "evidenceSet" in bundle, "ExplanationBundle should include an evidenceSet"
    assert "attributionSet" in bundle, "ExplanationBundle should include an attributionSet"
