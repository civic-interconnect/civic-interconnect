#!/usr/bin/env python
"""Update CEP localization metadata (version, updatedTimestamp, configHash).

Update version, updatedTimestamp, and configHash for all YAML configs
under localization/.

Usage examples:

    # Recompute hashes and timestamps, keep version as-is if content unchanged
    uv run python tools/update_localization_meta.py

    # Bump patch version when content changes
    uv run python tools/update_localization_meta.py --bump patch

    # Bump minor version when content changes
    uv run python tools/update_localization_meta.py --bump minor
"""

import argparse
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml  # requires PyYAML


def canonical_json_bytes(obj: Any) -> bytes:
    """Return a canonical JSON representation as bytes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compute_config_hash(config: dict[str, Any]) -> str:
    """Compute SHA-256 hash of config dict, excluding the configHash field."""
    config_copy = copy.deepcopy(config)
    if "configHash" in config_copy:
        del config_copy["configHash"]
    data = canonical_json_bytes(config_copy)
    return hashlib.sha256(data).hexdigest()


def bump_version(version: str, mode: str) -> str:
    """Bump semantic version string according to mode: major/minor/patch."""
    if not version:
        return "1.0.0"
    parts = version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"Invalid version string: {version}")
    major, minor, patch = map(int, parts)
    if mode == "major":
        major += 1
        minor = 0
        patch = 0
    elif mode == "minor":
        minor += 1
        patch = 0
    elif mode == "patch":
        patch += 1
    else:
        # no bump
        return version
    return f"{major}.{minor}.{patch}"


def update_file(path: Path, bump: str) -> tuple[str, str, str]:
    """Update a single localization YAML file.

    Returns (status, old_version, new_version) where status is one of:
    - "CHANGED": content changed and metadata updated
    - "OK": no content change, metadata refreshed
    - "SKIP": file not a mapping / empty / comment-only
    - "ERROR": could not parse or update
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(f"[ERROR] {path} - YAML parse error: {exc}")
        return "ERROR", "?", "?"

    if config is None:
        # Empty or comment-only file
        print(f"[SKIP]  {path} - file is empty or contains only comments.")
        return "SKIP", "?", "?"

    if not isinstance(config, dict):
        print(
            f"[SKIP]  {path} - top-level YAML is not a mapping "
            f"(found {type(config).__name__}); skipping."
        )
        return "SKIP", "?", "?"

    old_version = str(config.get("version") or "0.0.0")
    old_hash = config.get("configHash")

    # Compute new hash without configHash
    new_hash = compute_config_hash(config)

    # If hash is unchanged and configHash exists, we can skip version bump
    content_changed = old_hash != new_hash

    if content_changed:
        # Bump version according to requested mode
        if bump in ("major", "minor", "patch"):
            new_version = bump_version(old_version, bump)
        else:
            new_version = old_version if old_version != "0.0.0" else "1.0.0"
    else:
        new_version = old_version

    # Always ensure version is set to something sane
    if "version" not in config:
        config["version"] = new_version

    # Always update timestamp when we run, so we know when metadata was refreshed
    now_utc = dt.datetime.now(dt.UTC).replace(microsecond=0)
    config["updatedTimestamp"] = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Set configHash to the newly computed value
    config["configHash"] = new_hash

    # Write back
    try:
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(
                config,
                f,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=False,
            )
    except OSError as exc:
        print(f"[ERROR] {path} - could not write file: {exc}")
        return "ERROR", old_version, new_version

    status = "CHANGED" if content_changed or (old_version != new_version) else "OK"
    return status, old_version, new_version


def find_localization_files(root: Path) -> dict[Path, None]:
    """Find all localization YAML files under root/localization, excluding schemas."""
    loc_dir = root / "localization"
    files: dict[Path, None] = {}
    if not loc_dir.exists():
        return files

    for path in loc_dir.rglob("*.yaml"):
        # Skip schema files
        if "schemas" in path.parts:
            continue
        files[path] = None
    return files


def main() -> None:
    """Update localization metadata for all YAML files."""
    parser = argparse.ArgumentParser(description="Update CEP localization metadata.")
    parser.add_argument(
        "--bump",
        choices=["none", "patch", "minor", "major"],
        default="patch",
        help="How to bump semantic version when content changes (default: patch).",
    )
    args = parser.parse_args()
    bump_mode = args.bump

    repo_root = Path(__file__).resolve().parent.parent
    files = find_localization_files(repo_root)

    if not files:
        print("No localization YAML files found.")
        return

    counts: dict[str, int] = {"CHANGED": 0, "OK": 0, "SKIP": 0, "ERROR": 0}

    for path in sorted(files):
        status, old_ver, new_ver = update_file(
            path,
            bump_mode if bump_mode != "none" else "none",
        )
        counts[status] = counts.get(status, 0) + 1

        if status in ("CHANGED", "OK"):
            print(f"[{status}] {path} (version {old_ver} -> {new_ver})")
        elif status == "SKIP":
            # Message already printed inside update_file; no extra detail needed.
            continue
        else:
            # ERROR: already printed details, but echo the path
            print(f"[ERROR] {path} (version {old_ver} -> {new_ver})")

    print(
        f"\nSummary: "
        f"{counts['CHANGED']} changed, "
        f"{counts['OK']} up-to-date, "
        f"{counts['SKIP']} skipped, "
        f"{counts['ERROR']} errors."
    )


if __name__ == "__main__":
    main()
