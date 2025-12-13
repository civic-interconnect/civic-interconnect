"""Command-line interface for the Civic Exchange Protocol.

This module provides CLI commands for:
- snfei: Generate an SNFEI for an entity name and country
- version: Display the package version
- validate-json: Validate JSON files against CEP schemas
- codegen-rust: Generate Rust types from CEP JSON Schemas
- codegen-python-constants: Generate Python field-name constants from CEP schemas
- generate-example: Generate example data files from raw sources.

Examples:
uv run cx codegen-rust
uv run cx codegen-python-constants
uv run cx generate-example examples/entity
uv run cx generate-example examples/entity --overwrite
"""

from collections.abc import Iterable
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
from typing import Annotated, Any

import typer

from civic_interconnect.cep.adapters.demo_entities import (
    extract_example_entity_inputs,
    find_example_slices,
    load_raw_source,
)
from civic_interconnect.cep.codegen.python_constants import (
    DEFAULT_ENTITY_CONSTANTS_OUT,
    write_entity_constants,
)
from civic_interconnect.cep.codegen.python_constants import (
    DEFAULT_ENTITY_SCHEMA as DEFAULT_ENTITY_SCHEMA_FOR_CONSTANTS,
)
from civic_interconnect.cep.codegen.rust_generated import write_generated_rust
from civic_interconnect.cep.entity.api import build_entity_from_raw
from civic_interconnect.cep.snfei import generate_snfei_detailed
from civic_interconnect.cep.validation.json_validator import (
    ValidationSummary,
    validate_json_path,
)

app = typer.Typer(help="Civic Exchange Protocol CLI")

DEFAULT_ENTITY_SCHEMA = Path("schemas/core/cep.entity.schema.json")
DEFAULT_RELATIONSHIP_SCHEMA = Path("schemas/core/cep.relationship.schema.json")
DEFAULT_EXCHANGE_SCHEMA = Path("schemas/core/cep.exchange.schema.json")

DEFAULT_ENTITY_OUT = Path("crates/cep-core/src/entity/generated.rs")
DEFAULT_RELATIONSHIP_OUT = Path("crates/cep-core/src/relationship/generated.rs")
DEFAULT_EXCHANGE_OUT = Path("crates/cep-core/src/exchange/generated.rs")


def _canonical_snapshot_from_result(snfei_result: dict[str, Any]) -> dict[str, Any]:
    canonical = snfei_result.get("canonical")
    if not isinstance(canonical, dict):
        canonical = {}

    legal_name_normalized = _get_first(
        canonical,
        ["legal_name_normalized", "legalNameNormalized"],
        "",
    )
    address_normalized = _get_first(
        canonical,
        ["address_normalized", "addressNormalized"],
        None,
    )
    country_code = _get_first(
        canonical,
        ["country_code", "countryCode"],
        None,
    )
    registration_date = _get_first(
        canonical,
        ["registration_date", "registrationDate"],
        None,
    )

    return {
        "legalNameNormalized": legal_name_normalized,
        "addressNormalized": address_normalized,
        "countryCode": country_code,
        "registrationDate": registration_date,
    }


def _example_attestations(raw: dict[str, Any], slice_dir: Path) -> list[dict[str, Any]]:
    # TODO: Change in production - Deterministic timestamp for examples (keeps git diffs stable).
    ts = "1900-01-01T00:00:00Z"

    source_system = ""
    v = raw.get("source_system")
    if isinstance(v, str):
        source_system = v

    try:
        source_ref = slice_dir.relative_to(Path.cwd()).as_posix()
    except Exception:
        source_ref = slice_dir.as_posix()

    return [
        {
            "attestationTimestamp": ts,
            "attestorId": "urn:ci:attestor:example",
            "verificationMethodUri": "urn:ci:verification-method:manual",
            "proofType": "ManualAttestation",
            "proofPurpose": "assertionMethod",
            "proofValue": "",
            "sourceSystem": source_system or "examples",
            "sourceReference": source_ref,
            "anchorUri": None,
        }
    ]


def _get_first(mapping: dict[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    for k in keys:
        if k in mapping:
            return mapping[k]
    return default


def _snfei_value_from_result(snfei_result: dict[str, Any]) -> str:
    snfei_obj = snfei_result.get("snfei")
    if isinstance(snfei_obj, dict):
        v = snfei_obj.get("value")
        if isinstance(v, str) and v:
            return v
    if isinstance(snfei_obj, str) and snfei_obj:
        return snfei_obj
    raise ValueError("SNFEI result missing expected field: snfei.value (or snfei string)")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


@app.command("codegen-python-constants")
def codegen_python_constants(
    entity_schema: Path | None = None,
    entity_out: Path | None = None,
) -> None:
    """Generate Python field-name constants from CEP JSON Schemas.

    Currently generates:
    - civic_interconnect.cep.constants.entity_fields
    """
    if entity_schema is None:
        entity_schema = DEFAULT_ENTITY_SCHEMA_FOR_CONSTANTS
    if entity_out is None:
        entity_out = DEFAULT_ENTITY_CONSTANTS_OUT

    write_entity_constants(entity_schema, entity_out)
    typer.echo(f"Wrote {entity_out}")


@app.command("codegen-rust")
def codegen_rust(
    entity_schema: Path | None = None,
    relationship_schema: Path | None = None,
    exchange_schema: Path | None = None,
    entity_out: Path | None = None,
    relationship_out: Path | None = None,
    exchange_out: Path | None = None,
) -> None:
    """Generate Rust types from CEP JSON Schemas into generated.rs files."""
    if entity_schema is None:
        entity_schema = DEFAULT_ENTITY_SCHEMA
    if relationship_schema is None:
        relationship_schema = DEFAULT_RELATIONSHIP_SCHEMA
    if exchange_schema is None:
        exchange_schema = DEFAULT_EXCHANGE_SCHEMA
    if entity_out is None:
        entity_out = DEFAULT_ENTITY_OUT
    if relationship_out is None:
        relationship_out = DEFAULT_RELATIONSHIP_OUT
    if exchange_out is None:
        exchange_out = DEFAULT_EXCHANGE_OUT

    write_generated_rust(entity_schema, "EntityRecord", entity_out)
    write_generated_rust(relationship_schema, "RelationshipRecord", relationship_out)
    write_generated_rust(exchange_schema, "ExchangeRecord", exchange_out)

    typer.echo(f"Wrote {entity_out}")
    typer.echo(f"Wrote {relationship_out}")
    typer.echo(f"Wrote {exchange_out}")


@app.command("generate-example")
def generate_example(
    path: Annotated[
        Path,
        typer.Argument(
            help=(
                "Path to an example slice or a directory containing slices "
                "(e.g. examples/entity or examples/entity/municipality/us_il_01)"
            ),
        ),
    ],
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Overwrite existing 02/03/04 files instead of skipping them.",
        ),
    ] = False,
) -> None:
    """Generate 02_normalized, 03_canonical, and 04_entity_record JSON files.

    Pipeline:
        raw -> normalized -> canonical -> EntityRecord
    """
    slices = find_example_slices(path)
    if not slices:
        typer.echo(f"No example slices found under {path}")
        raise typer.Exit(code=1)

    typer.echo(f"Found {len(slices)} example slice(s) under {path}")
    for slice_dir in slices:
        typer.echo(f"\n[example] {slice_dir}")

        f02 = slice_dir / "02_normalized.json"
        f03 = slice_dir / "03_canonical.json"
        f04 = slice_dir / "04_entity_record.json"

        if not overwrite and f02.exists() and f03.exists() and f04.exists():
            typer.echo("  - 02/03/04 already exist, skipping (use --overwrite to regenerate)")
            continue

        try:
            raw = load_raw_source(slice_dir)
        except (FileNotFoundError, ValueError) as exc:
            typer.echo(f"  ! {exc}, skipping slice")
            continue

        try:
            inputs = extract_example_entity_inputs(raw, slice_dir)
        except KeyError as exc:
            typer.echo(f"  ! missing required raw field(s): {exc!r}, skipping slice")
            continue

        # 1) SNFEI + canonical inputs via Rust core
        snfei_result = generate_snfei_detailed(
            legal_name=inputs.legal_name,
            country_code=inputs.country_code,
            address=inputs.address,
            registration_date=inputs.registration_date,
            lei=None,
            sam_uei=None,
        )

        snfei_value = _snfei_value_from_result(snfei_result)
        canonical_json = _canonical_snapshot_from_result(snfei_result)
        legal_name_normalized = canonical_json.get("legalNameNormalized", "")

        # 2) NormalizedEntityInput (02_normalized.json)
        normalized: dict[str, Any] = {
            "jurisdictionIso": inputs.jurisdiction_iso,
            "legalName": inputs.legal_name,
            "legalNameNormalized": legal_name_normalized,
            "snfei": snfei_value,
            "entityType": inputs.entity_type,
            "attestations": _example_attestations(raw, slice_dir),
        }
        _write_json(f02, normalized)
        typer.echo(f"  - wrote {f02.name}")

        # 3) Canonical snapshot (03_canonical.json)
        _write_json(f03, canonical_json)
        typer.echo(f"  - wrote {f03.name}")

        # 4) Final EntityRecord via builder (04_entity_record.json)
        entity_record = build_entity_from_raw(normalized)
        _write_json(f04, entity_record)
        typer.echo(f"  - wrote {f04.name}")


@app.command("snfei")
def snfei_cmd(
    legal_name: str = typer.Argument(..., help="Raw legal name"),
    country_code: str = typer.Option("US", "--country-code", "-c", help="ISO country code"),
) -> None:
    """Generate an SNFEI for an entity name and country."""
    result = generate_snfei_detailed(
        legal_name=legal_name,
        country_code=country_code,
        address=None,
        registration_date=None,
        lei=None,
        sam_uei=None,
    )

    snfei_value = _snfei_value_from_result(result)
    tier = _get_first(result, ["tier"], None)
    confidence = _get_first(result, ["confidence_score", "confidenceScore"], None)

    typer.echo(f"SNFEI: {snfei_value}")
    typer.echo(f"Tier: {tier}, confidence: {confidence}")


@app.command("validate-json")
def validate_json(
    path: Path | None = None,
    schema: str = typer.Option(
        ...,
        "--schema",
        "-s",
        help="Schema name (for example: entity, exchange, relationship, snfei).",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Recurse into subdirectories when validating a directory.",
    ),
) -> None:
    """Validate JSON file(s) against a CEP JSON Schema."""
    if path is None:
        typer.echo("Error: Path argument is required.")
        raise typer.Exit(code=1)

    summary: ValidationSummary = validate_json_path(
        path=path,
        schema_name=schema,
        recursive=recursive,
    )

    if not summary.results:
        typer.echo("No JSON files found to validate.")
        raise typer.Exit(code=1)

    errors_found = False
    for result in summary.results:
        if result.ok:
            typer.echo(f"[OK] {result.path}")
        else:
            errors_found = True
            typer.echo(f"[ERROR] {result.path}")
            for err in result.errors:
                typer.echo(f"  - {err}")

    if errors_found:
        typer.echo("Validation completed with errors.")
        raise typer.Exit(code=1)

    typer.echo("All files validated successfully.")
    raise typer.Exit(code=0)


@app.command("version")
def version_cmd() -> None:
    """Show package version."""
    try:
        v = version("civic-interconnect")
    except PackageNotFoundError:
        v = "0.0.0"
    typer.echo(v)
