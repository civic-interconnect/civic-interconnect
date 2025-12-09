"""Regenerate Rust generated.rs files from CEP JSON Schemas.

Lightweight helper that bypasses the full `cx` CLI so it does not depend
on SNFEI being fully wired up.

Run with:
uv run python tools/codegen_rust.py
"""

from pathlib import Path

from civic_interconnect.cep.codegen.rust_generated import write_generated_rust

BASE = Path(__file__).resolve().parent.parent
SCHEMAS = BASE / "schemas"
CRATES = BASE / "crates"


def schema_name_to_record_name(schema_path: Path) -> str:
    """Derive Rust record name from schema filename.

    Examples:
        cep.entity.schema.json -> EntityRecord
        cf.contribution.schema.json -> ContributionRecord
        env.facility.schema.json -> FacilityRecord
    """
    stem = schema_path.stem.removesuffix(".schema")  # "cep.entity"
    parts = stem.split(".")
    name = parts[-1] if parts else stem

    # Convert kebab-case to PascalCase and append "Record"
    pascal = "".join(word.capitalize() for word in name.split("-"))
    return f"{pascal}Record"


def get_output_mapping() -> dict[Path, Path]:
    """Build mapping from schema files to output generated.rs paths."""
    mapping: dict[Path, Path] = {}

    # Core schemas -> cep-core/src/{name}/generated.rs
    core_schemas = {
        "cep.entity.schema.json": "entity",
        "cep.relationship.schema.json": "relationship",
        "cep.exchange.schema.json": "exchange",
        "cep.ctag.schema.json": "ctag",
    }
    for schema_file, module in core_schemas.items():
        schema_path = SCHEMAS / "core" / schema_file
        if schema_path.exists():
            mapping[schema_path] = CRATES / "cep-core" / "src" / module / "generated.rs"

    # Domain schemas -> cep-domains/src/{domain}/{name}/generated.rs
    domains_dir = SCHEMAS / "domains"
    if domains_dir.exists():
        for domain_dir in sorted(domains_dir.iterdir()):
            if not domain_dir.is_dir():
                continue
            domain_name = domain_dir.name.replace("-", "_")

            for schema_file in sorted(domain_dir.glob("*.schema.json")):
                # Skip empty files
                if schema_file.stat().st_size == 0:
                    continue

                stem = schema_file.stem.removesuffix(".schema")
                parts = stem.split(".")
                module_name = parts[-1].replace("-", "_") if parts else stem

                output = CRATES / "cep-domains" / "src" / domain_name / module_name / "generated.rs"
                mapping[schema_file] = output

    return mapping


def main() -> None:
    """Generate Rust types from CEP JSON Schemas into generated.rs files."""
    mapping = get_output_mapping()

    if not mapping:
        print("[codegen-rust] No schemas found to process")
        return

    print(f"[codegen-rust] Found {len(mapping)} schema(s) to process\n")

    generated = 0
    skipped = 0

    for schema_path, output_path in sorted(mapping.items()):
        record_name = schema_name_to_record_name(schema_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"  {schema_path.relative_to(BASE)}")
        print(f"    -> {output_path.relative_to(BASE)} ({record_name})")

        try:
            write_generated_rust(schema_path, record_name, output_path)
            generated += 1
        except Exception as e:
            print(f"    ERROR: {e}")
            skipped += 1
            continue

    print(f"\n[codegen-rust] Done! Generated {generated} file(s), skipped {skipped}")


if __name__ == "__main__":
    main()
