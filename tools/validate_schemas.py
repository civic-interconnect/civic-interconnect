#!/usr/bin/env python
"""Validate JSON schema files and vocabulary instances.

- Validates all *.schema.json files under schemas/ and vocabulary/ as JSON Schemas
  against Draft 2020-12.
- Additionally validates vocabulary instance files under vocabulary/ (e.g.
  committee-type.v1.0.0.json) against the CEP vocabulary meta-schema.

Path: tools/validate_schemas.py
"""

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, ValidationError

EXPECTED_META = "https://json-schema.org/draft/2020-12/schema"


def find_schema_files():
    """Find all JSON schema files in schemas/ and vocabulary/ directories.

    Returns:
        list[Path]: Sorted list of paths to *.schema.json files found under
        schemas/ and vocabulary/.
    """
    roots = [Path("schemas"), Path("vocabulary")]
    files = []
    for root in roots:
        if root.exists():
            files.extend(root.rglob("*.schema.json"))
    return sorted(files)


def find_vocab_instance_files():
    """Find vocabulary instance files under vocabulary/ (non-schema JSON files).

    Returns:
        list[Path]: Sorted list of paths to *.json files under vocabulary/
        that are NOT *.schema.json.
    """
    root = Path("vocabulary")
    if not root.exists():
        return []

    files = []
    for path in root.rglob("*.json"):
        if path.name.endswith(".schema.json"):
            continue
        files.append(path)
    return sorted(files)


def validate_schema(schema):
    """Validate a single non-empty schema against draft 2020-12.

    Returns:
        None if valid, otherwise an error string.
    """
    meta = schema.get("$schema")
    if meta != EXPECTED_META:
        return f"Invalid $schema {meta!r}. Expected {EXPECTED_META!r}."

    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        return f"Invalid schema structure: {exc}"

    return None


def load_vocab_meta_schema():
    """Load the CEP vocabulary meta-schema, if present.

    Returns:
        Draft202012Validator | None
    """
    meta_path = Path("schemas") / "vocabulary" / "cep.vocabulary.schema.json"
    if not meta_path.exists():
        return None

    raw = meta_path.read_text(encoding="utf-8")
    meta_schema = json.loads(raw)
    return Draft202012Validator(meta_schema)


def run_schema_validation(schema_files):
    """Validate all schema files and collect results.

    Returns:
        tuple:
            empty_files (list[str])
            parse_errors (list[tuple[str, str]])
            invalid_schemas (list[tuple[str, str]])
    """
    empty_files = []
    parse_errors = []
    invalid_schemas = []

    for path in schema_files:
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
            schema = json.loads(raw)
        except Exception as exc:
            parse_errors.append((path_str, f"JSON parse error: {exc}"))
            continue

        error = validate_schema(schema)
        if error:
            invalid_schemas.append((path_str, error))

    return empty_files, parse_errors, invalid_schemas


def run_vocab_validation(vocab_files, vocab_validator):
    """Validate all vocabulary instance files against the vocab meta-schema.

    Returns:
        tuple:
            vocab_parse_errors (list[tuple[str, str]])
            vocab_invalid_files (list[tuple[str, str]])
    """
    vocab_parse_errors = []
    vocab_invalid_files = []

    if not vocab_files:
        return vocab_parse_errors, vocab_invalid_files

    if vocab_validator is None:
        # We log a warning in main; here we just skip validation.
        return vocab_parse_errors, vocab_invalid_files

    for path in vocab_files:
        path_str = path.as_posix()

        try:
            raw = path.read_text(encoding="utf-8")
        except Exception as exc:
            vocab_parse_errors.append((path_str, f"Failed to read file: {exc}"))
            continue

        if not raw.strip():
            vocab_invalid_files.append((path_str, "Vocabulary file is empty."))
            continue

        try:
            instance = json.loads(raw)
        except Exception as exc:
            vocab_parse_errors.append((path_str, f"JSON parse error: {exc}"))
            continue

        try:
            vocab_validator.validate(instance)
        except ValidationError as exc:
            vocab_invalid_files.append((path_str, f"Vocabulary validation error: {exc.message}"))

    return vocab_parse_errors, vocab_invalid_files


def print_schema_summary(schema_files, empty_files, parse_errors, invalid_schemas):
    """Print summary for schema validation."""
    print("\nJSON Schema Validation Summary")
    print("--------------------------------")
    print(f"Total schema files found: {len(schema_files)}")

    if empty_files:
        print(f"Empty (TODO) schemas: {len(empty_files)}")
        for path in empty_files:
            print(f"  - {path}")

    if parse_errors:
        print(f"\nFiles with JSON parse errors: {len(parse_errors)}")
        for path, msg in parse_errors:
            print(f"  - {path}: {msg}")

    if invalid_schemas:
        print(f"\nFiles with invalid schemas: {len(invalid_schemas)}")
        for path, msg in invalid_schemas:
            print(f"  - {path}: {msg}")


def print_vocab_summary(vocab_files, vocab_parse_errors, vocab_invalid_files):
    """Print summary for vocabulary instance validation."""
    if vocab_files:
        print(f"\nVocabulary instance files found: {len(vocab_files)}")

    if vocab_parse_errors:
        print(f"\nVocabulary files with JSON parse errors: {len(vocab_parse_errors)}")
        for path, msg in vocab_parse_errors:
            print(f"  - {path}: {msg}")

    if vocab_invalid_files:
        print(f"\nVocabulary files failing validation: {len(vocab_invalid_files)}")
        for path, msg in vocab_invalid_files:
            print(f"  - {path}: {msg}")


def main():
    """Validate JSON schemas and vocabulary instances."""
    schema_files = find_schema_files()
    vocab_files = find_vocab_instance_files()

    if not schema_files and not vocab_files:
        print("No schema or vocabulary files found.")
        return 0

    vocab_validator = load_vocab_meta_schema()

    if vocab_files and vocab_validator is None:
        print(
            "Warning: vocabulary files found, but "
            "schemas/vocabulary/cep.vocabulary.schema.json is missing; "
            "skipping vocabulary instance validation."
        )

    empty_files, parse_errors, invalid_schemas = run_schema_validation(schema_files)
    vocab_parse_errors, vocab_invalid_files = run_vocab_validation(vocab_files, vocab_validator)

    print_schema_summary(schema_files, empty_files, parse_errors, invalid_schemas)
    print_vocab_summary(vocab_files, vocab_parse_errors, vocab_invalid_files)

    # Emit simple counts
    print(f"\nSchemas processed: {len(schema_files)}")
    print(f"Vocabularies processed: {len(vocab_files)}")

    has_hard_errors = bool(
        parse_errors or invalid_schemas or vocab_parse_errors or vocab_invalid_files
    )

    if not has_hard_errors:
        print("\nAll non-empty schemas and vocabulary instances are valid.")
        return 0

    print("\nSchema or vocabulary validation failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
