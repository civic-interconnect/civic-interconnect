# typings/cep_py/__init__.pyi
#
# Typing stubs for the `cep_py` PyO3 extension module.
#
# Design goals:
# - Stable, minimal surface area that mirrors the Rust FFI exactly.
# - Two flavors for detailed operations:
#     * *_detailed_json(...) -> str   (fast, FFI-friendly, auditable; caller parses if desired)
#     * *_detailed(...)      -> dict  (ergonomic; uses json.loads inside the extension)
# - Keep return types permissive (dict[str, Any]) so the Rust-side JSON schema can evolve
#   without forcing a stub update for every additive field.

from typing import Any, Final

# ---- CEP builders (JSON-in, JSON-out) ----------------------------------------

def build_entity_json(input_json: str) -> str: ...
def build_exchange_json(input_json: str) -> str: ...
def build_relationship_json(input_json: str) -> str: ...
def build_ctag_json(input_json: str) -> str: ...

# ---- Localization (YAML-driven, Rust source of truth) ------------------------

def apply_localization_name_py(*args: Any, **kwargs: Any) -> str: ...
def apply_localization_name_detailed_py(*args: Any, **kwargs: Any) -> Any: ...
def apply_localization_name_detailed_json_py(*args: Any, **kwargs: Any) -> Any: ...
def normalize_legal_name_py(*args: Any, **kwargs: Any) -> str: ...
def normalize_address_py(*args: Any, **kwargs: Any) -> str: ...
def normalize_registration_date_py(*args: Any, **kwargs: Any) -> str: ...

# ---- SNFEI (core pipeline) ---------------------------------------------------

def generate_snfei(
    legal_name: str,
    country_code: str,
    address: str | None = ...,
    registration_date: str | None = ...,
) -> str: ...
def generate_snfei_detailed_json(
    legal_name: str,
    country_code: str,
    address: str | None = ...,
    registration_date: str | None = ...,
    lei: str | None = ...,
    sam_uei: str | None = ...,
) -> str: ...
def generate_snfei_detailed(
    legal_name: str,
    country_code: str,
    address: str | None = ...,
    registration_date: str | None = ...,
    lei: str | None = ...,
    sam_uei: str | None = ...,
) -> dict[str, Any]: ...

# ---- Normalizers -------------------------------------------------------------

def normalize_legal_name(value: str) -> str: ...
def normalize_address(value: str) -> str: ...
def normalize_registration_date(value: str) -> str | None: ...

# ---- Module metadata ---------------------------------------------------------
#
# NOTE: In a .pyi, `__all__` is for editor/typing discovery, not runtime export.
# Keep it in sync with the stable FFI surface above.

__all__: Final[list[str]] = [
    # builders
    "build_entity_json",
    "build_exchange_json",
    "build_relationship_json",
    "build_ctag_json",
    # localization
    "apply_localization_name_py",
    "apply_localization_name_detailed_py",
    "apply_localization_name_detailed_json_py",
    # normalizers
    "normalize_legal_name",
    "normalize_address",
    "normalize_registration_date",
    # snfei
    "generate_snfei",
    "generate_snfei_detailed",
    "generate_snfei_detailed_json",
]

__doc__: str
