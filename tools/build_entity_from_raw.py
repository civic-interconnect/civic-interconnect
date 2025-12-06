"""Script to build an entity from raw data dictionary.

This module demonstrates building an entity using the build_entity_from_raw
function from the ci_cep.entity.api module with sample municipality data.

File: tools/build_entity_from_raw.py
"""

import json
import sys

from civic_interconnect.cep.entity.api import HAS_NATIVE_BACKEND, build_entity_from_raw


def main() -> None:
    """Demonstrate building an entity from raw municipality data."""
    raw = {
        "jurisdictionIso": "US-MN",
        "legalName": "City of Springfield",
        "legalNameNormalized": "city of springfield",
        "snfei": "deadbeef",
        "entityType": "municipality",
    }

    backend = "Rust (cep_py)" if HAS_NATIVE_BACKEND else "pure Python"
    print(f"[build_entity_from_raw] Using backend: {backend}")

    try:
        entity = build_entity_from_raw(raw)
    except Exception as exc:
        print(
            "[build_entity_from_raw] ERROR: Failed to build entity.\n"
            f"Reason: {exc!r}\n"
            "If you expected the Rust backend, make sure you have built and "
            "installed the cep_py extension, for example:\n"
            "    uv run maturin develop --release",
            file=sys.stderr,
        )
        sys.exit(1)

    print("\n[build_entity_from_raw] Resulting CEP Entity:")
    print(json.dumps(entity, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
