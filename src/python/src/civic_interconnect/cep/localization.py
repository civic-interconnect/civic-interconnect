"""Stable localization API (Rust-backed)."""

from civic_interconnect.cep.snfei.localization import (
    LocalizationApplyResult,
    LocalizationProvenance,
    apply_localization_name,
    apply_localization_name_detailed,
    apply_localization_name_detailed_json,
)

__all__ = [
    "LocalizationApplyResult",
    "LocalizationProvenance",
    "apply_localization_name",
    "apply_localization_name_detailed",
    "apply_localization_name_detailed_json",
]
