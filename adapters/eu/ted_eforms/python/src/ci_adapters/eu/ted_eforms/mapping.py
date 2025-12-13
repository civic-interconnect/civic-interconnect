"""Mapping helpers for EU TED eForms.

Keep pure mapping functions here (no I/O). This makes testing easy and stable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping


def map_record_to_minimal_envelope(record: Mapping[str, Any], adapter_id: str) -> Mapping[str, Any]:
    """Map a normalized record into a minimal envelope-like dict.

    Replace with core envelope builder once integrated.
    """
    return {
        "adapterId": adapter_id,
        "payload": dict(record),
    }
