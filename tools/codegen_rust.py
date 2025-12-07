"""Regenerate Rust generated.rs files from CEP JSON Schemas.

Lightweight helper that bypasses the full `cx` CLI so it does not depend
on SNFEI being fully wired up.

Run with:
uv run python tools/codegen_rust.py
"""

from pathlib import Path

from civic_interconnect.cep.codegen.rust_generated import write_generated_rust

BASE = Path(__file__).resolve().parent.parent

ENTITY_SCHEMA = BASE / "schemas" / "cep.entity.schema.json"
REL_SCHEMA = BASE / "schemas" / "cep.relationship.schema.json"
EXCH_SCHEMA = BASE / "schemas" / "cep.exchange.schema.json"

ENTITY_OUT = BASE / "crates" / "cep-core" / "src" / "entity" / "generated.rs"
REL_OUT = BASE / "crates" / "cep-core" / "src" / "relationship" / "generated.rs"
EXCH_OUT = BASE / "crates" / "cep-core" / "src" / "exchange" / "generated.rs"


def main() -> None:
    """Generate Rust types from CEP JSON Schemas into generated.rs files."""
    print(f"[codegen-rust] Using entity schema: {ENTITY_SCHEMA}")
    print(f"[codegen-rust] Using relationship schema: {REL_SCHEMA}")
    print(f"[codegen-rust] Using exchange schema: {EXCH_SCHEMA}")

    write_generated_rust(ENTITY_SCHEMA, "EntityRecord", ENTITY_OUT)
    write_generated_rust(REL_SCHEMA, "RelationshipRecord", REL_OUT)
    write_generated_rust(EXCH_SCHEMA, "ExchangeRecord", EXCH_OUT)

    print(f"[codegen-rust] Wrote {ENTITY_OUT}")
    print(f"[codegen-rust] Wrote {REL_OUT}")
    print(f"[codegen-rust] Wrote {EXCH_OUT}")


if __name__ == "__main__":
    main()
