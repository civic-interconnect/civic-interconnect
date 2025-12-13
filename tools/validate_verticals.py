#!/usr/bin/env python
r"""Validate YAML about files for vertical slices.

- Validates all about.yaml files under docs/en/04_verticals/ against
  the schemas/governance/about.schema.json schema.

Path: tools/validate_verticals.py
"""

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, ValidationError
import yaml

EXPECTED_META = "https://json-schema.org/draft/2020-12/schema"
ABOUT_SCHEMA_PATH = Path("schemas/governance/about.schema.json")


def find_about_yaml_files():
    """Find about.yaml files under docs/en/04_verticals/ directories.

    Returns:
        list[Path]: Sorted list of paths to about.yaml files found under
        docs/en/04_verticals/.
    """
    root = Path("docs/en/04_verticals")
    if not root.exists():
        return []

    files = []
    for path in root.rglob("about.yaml"):
        files.append(path)
    return sorted(files)


def load_about_validator():
    """Load and validate the about.schema.json file.

    Returns:
        Draft202012Validator | None: A validator instance if the schema is
        present and valid; otherwise None.
    """
    if not ABOUT_SCHEMA_PATH.exists():
        print(
            f"Error: about schema not found at {ABOUT_SCHEMA_PATH.as_posix()}.",
            file=sys.stderr,
        )
        return None

    try:
        raw = ABOUT_SCHEMA_PATH.read_text(encoding="utf-8")
    except Exception as exc:
        print(
            f"Error: failed to read about schema at {ABOUT_SCHEMA_PATH.as_posix()}: {exc}",
            file=sys.stderr,
        )
        return None

    try:
        schema = json.loads(raw)
    except Exception as exc:
        print(
            f"Error: about schema is not valid JSON: {exc}",
            file=sys.stderr,
        )
        return None

    meta = schema.get("$schema")
    if meta != EXPECTED_META:
        print(
            f"Warning: about schema $schema is {meta!r}, expected "
            f"{EXPECTED_META!r}. Validation will still run.",
            file=sys.stderr,
        )

    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        print(
            f"Error: about schema structure is invalid: {exc}",
            file=sys.stderr,
        )
        return None

    return Draft202012Validator(schema)


def validate_about_files(about_files, validator):
    """Validate all about.yaml files against the about schema.

    Returns:
        tuple:
            empty_files (list[str])
            parse_errors (list[tuple[str, str]])
            invalid_instances (list[tuple[str, str]])
    """
    empty_files = []
    parse_errors = []
    invalid_instances = []

    if not about_files:
        return empty_files, parse_errors, invalid_instances

    for path in about_files:
        path_str = path.as_posix()

        try:
            raw = path.read_text(encoding="utf-8")
        except Exception as exc:
            parse_errors.append((path_str, f"Failed to read file: {exc}"))
            continue

        if not raw.strip():
            empty_files.append(path_str)
            continue

        try:
            instance = yaml.safe_load(raw)
        except Exception as exc:
            parse_errors.append((path_str, f"YAML parse error: {exc}"))
            continue

        # Require a mapping at the top level
        if not isinstance(instance, dict):
            invalid_instances.append((path_str, "Top-level YAML value must be a mapping (object)."))
            continue

        try:
            validator.validate(instance)
        except ValidationError as exc:
            invalid_instances.append((path_str, f"Validation error: {exc.message}"))

    return empty_files, parse_errors, invalid_instances


def print_summary(about_files, empty_files, parse_errors, invalid_instances):
    """Print summary for about.yaml validation."""
    print("\nVertical About YAML Validation Summary")
    print("--------------------------------------")
    print(f"Total about.yaml files found: {len(about_files)}")

    if empty_files:
        print(f"\nEmpty about.yaml files: {len(empty_files)}")
        for path in empty_files:
            print(f"  - {path}")

    if parse_errors:
        print(f"\nFiles with YAML parse errors: {len(parse_errors)}")
        for path, msg in parse_errors:
            print(f"  - {path}: {msg}")

    if invalid_instances:
        print(f"\nFiles with invalid content: {len(invalid_instances)}")
        for path, msg in invalid_instances:
            print(f"  - {path}: {msg}")


def main():
    """Validate about.yaml files for vertical slices."""
    about_files = find_about_yaml_files()

    if not about_files:
        print("No about.yaml files found under docs/en/verticals/.")
        return 0

    validator = load_about_validator()
    if validator is None:
        print("\nAbout.yaml validation failed (schema not available or invalid).")
        return 1

    empty_files, parse_errors, invalid_instances = validate_about_files(about_files, validator)

    print_summary(about_files, empty_files, parse_errors, invalid_instances)

    print(f"\nAbout files processed: {len(about_files)}")

    has_hard_errors = bool(parse_errors or invalid_instances)

    if not has_hard_errors:
        print("\nAll non-empty about.yaml files are valid.")
        return 0

    print("\nAbout.yaml validation failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
