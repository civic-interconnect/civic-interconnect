"""Thin localization wrappers around the Rust core.

All localization logic lives in Rust (cep_core::common::localization) and is
exposed to Python via the `cep_py` extension module.

No business logic here; everything delegates to Rust.

This module exists for two reasons:
1) Provide a stable, ergonomic Python API for localization operations.
2) Tolerate minor Rust-FFI naming differences across builds (legacy vs current)
   WITHOUT changing call sites throughout the Python codebase.

Path: src/python/src/civic_interconnect/cep/snfei/localization.py
"""

import json
from typing import TypedDict, cast

import cep_py as _core

# =============================================================================
# Public result types (Python typing only)
# =============================================================================


class LocalizationProvenance(TypedDict):
    """Provenance information emitted by the Rust localization layer.

    Keys and meanings:
    - requested_key: The jurisdiction key requested by the caller.
      Examples: "US-IL", "us-il", "us/il". Rust may normalize this internally.
    - resolved_keys: The resolved cascade of jurisdiction keys actually applied.
    - resolved_config_hashes: Optional hashes for the resolved configs (same
      ordering as resolved_keys) to support audit/debugging and version pinning.
    """

    requested_key: str
    resolved_keys: list[str]
    resolved_config_hashes: list[str | None]


class LocalizationApplyResult(TypedDict):
    """Structured result for localization, including provenance.

    - output: The localized output string.
    - provenance: Details about which jurisdiction config(s) were applied.
    """

    output: str
    provenance: LocalizationProvenance


# =============================================================================
# Private helper: resolve an FFI function name safely
# =============================================================================


def _get_ffi(*names: str):
    """Return the first existing callable from `cep_py` among `names`.

    Why this exists:
    - The Python layer must remain stable even if the Rust-exported symbol name
      changes. This function centralizes that compatibility logic.

    Contract:
    - This module does NOT invent or emulate localization logic.
    - It only chooses which Rust-exported function to call, then returns results.

    Failure mode:
    - If none of the candidate names exist in the installed `cep_py` module,
      we raise AttributeError with a precise message listing expected names.
    """
    for n in names:
        fn = getattr(_core, n, None)
        if fn is not None:
            return fn
    raise AttributeError(f"cep_py is missing expected function(s): {', '.join(names)}")


# =============================================================================
# Public API (stable call surface for the Python package)
# =============================================================================


def apply_localization_name(name: str, jurisdiction: str) -> str:
    """Apply Rust localization to `name` for `jurisdiction` and return a string.

    Rust FFI compatibility:
    - Uses: cep_py.apply_localization_name(name, jurisdiction)
    - NOT: cep_py.apply_localization_name_py(name, jurisdiction)

    The output is expected to be a normalized/localized string produced by the
    Rust localization layer (often a "pre-normalization" rewrite stage).
    """
    fn = _get_ffi("apply_localization_name")
    return cast("str", fn(name, jurisdiction))


def apply_localization_name_detailed_json(name: str, jurisdiction: str) -> str:
    """Apply Rust localization and return detailed result as a JSON string.

    Uses Rust exports (if present):
    - cep_py.apply_localization_name_detailed_json(name, jurisdiction)  -> str

    Otherwise we adapt from the detailed non-JSON function:
    - cep_py.apply_localization_name_detailed(...)

    Important:
    - This function guarantees: return type is `str` containing JSON.
    - This makes it suitable for golden files, snapshots, and CLI output.
    """
    # Prefer an explicit JSON-returning FFI if it exists.
    fn = getattr(_core, "apply_localization_name_detailed_json", None)
    if fn is not None:
        raw = fn(name, jurisdiction)
        return cast("str", raw)

    # Otherwise adapt from the detailed function (JSON str OR dict).
    fn2 = _get_ffi("apply_localization_name_detailed")
    raw2 = fn2(name, jurisdiction)

    # If Rust already returned JSON, keep it verbatim.
    if isinstance(raw2, str):
        return raw2

    # If Rust returned a dict-like object, serialize deterministically.
    # Note: sort_keys=True makes snapshots stable across runs.
    return json.dumps(raw2, sort_keys=True)


def apply_localization_name_detailed(name: str, jurisdiction: str) -> LocalizationApplyResult:
    """Apply Rust localization and return a parsed dict with provenance.

    Implementation detail:
    - We call apply_localization_name_detailed_json(...) to ensure we always
      consume a JSON string, then json.loads it.

    This yields a stable Python shape:
    {
      "output": "...",
      "provenance": { ... }
    }
    """
    return cast(
        "LocalizationApplyResult",
        json.loads(apply_localization_name_detailed_json(name, jurisdiction)),
    )


__all__ = [
    "LocalizationApplyResult",
    "LocalizationProvenance",
    "apply_localization_name",
    "apply_localization_name_detailed",
    "apply_localization_name_detailed_json",
]
