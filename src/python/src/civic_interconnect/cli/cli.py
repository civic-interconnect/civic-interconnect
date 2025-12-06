"""Command-line interface for the Civic Exchange Protocol.

This module provides CLI commands for:
- snfei: Generate an SNFEI for an entity name and country
- version: Display the package version
- validate-json: Validate JSON files against CEP schemas
- codegen-rust: Generate Rust types from CEP JSON Schemas
"""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import typer

from civic_interconnect.cep.codegen.rust_generated import write_generated_rust
from civic_interconnect.cep.snfei.generator import generate_snfei_with_confidence
from civic_interconnect.cep.validation.json_validator import (
    ValidationSummary,
    validate_json_path,
)

app = typer.Typer(help="Civic Exchange Protocol CLI")

DEFAULT_ENTITY_SCHEMA = Path("schemas/cep.entity.schema.json")
DEFAULT_RELATIONSHIP_SCHEMA = Path("schemas/cep.relationship.schema.json")
DEFAULT_EXCHANGE_SCHEMA = Path("schemas/cep.exchange.schema.json")

DEFAULT_ENTITY_OUT = Path("crates/cep-core/src/entity/generated.rs")
DEFAULT_RELATIONSHIP_OUT = Path("crates/cep-core/src/relationship/generated.rs")
DEFAULT_EXCHANGE_OUT = Path("crates/cep-core/src/exchange/generated.rs")


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

    # Adjust struct names here if your Rust crates use different ones.
    write_generated_rust(entity_schema, "EntityRecord", entity_out)
    write_generated_rust(relationship_schema, "RelationshipRecord", relationship_out)
    write_generated_rust(exchange_schema, "ExchangeRecord", exchange_out)

    typer.echo(f"Wrote {entity_out}")
    typer.echo(f"Wrote {relationship_out}")
    typer.echo(f"Wrote {exchange_out}")


@app.command()
def snfei(
    legal_name: str = typer.Argument(..., help="Raw legal name"),
    country_code: str = typer.Option("US", "--country-code", "-c", help="ISO country code"),
) -> None:
    """Generate an SNFEI for an entity name and country."""
    result = generate_snfei_with_confidence(
        legal_name=legal_name,
        country_code=country_code,
    )
    typer.echo(f"SNFEI: {result.snfei.value}")
    typer.echo(f"Tier: {result.tier}, confidence: {result.confidence_score}")


@app.command()
def version_cmd() -> None:
    """Show package version."""
    try:
        v = version("civic-interconnect")
    except PackageNotFoundError:
        v = "0.0.0"
    typer.echo(v)


@app.command()
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
    """Validate JSON file(s) against a CEP JSON Schema.

    Behavior:
    - If PATH is a file, validates that single JSON file.
    - If PATH is a directory, validates all *.json files within it.
      Use --recursive to walk subdirectories.
    """
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
