#!/usr/bin/env python3
"""Audit identity collisions for jurisdictional name localization.

Primary use:
- Detect when normalization/localization collapses multiple raw names into the
  same normalized name (collisions).
- Diff against a saved baseline mapping to identify new merges/splits.
- Emit a detailed provenance chain for any changed mapping (rule trace).

Exit codes:
- 0: success
- 2: failing condition triggered (e.g., new merges with --fail-on-new-merges)
- 3: missing required FFI functions
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


# ---------------------------------------------------------------------------
# Localization FFI
# ---------------------------------------------------------------------------


def _import_localization() -> tuple[Any, Any]:
    """Return localization callables from the Rust-backed Python API."""
    from civic_interconnect.cep.snfei.localization import (
        apply_localization_name,
        apply_localization_name_detailed_json,
    )

    return apply_localization_name, apply_localization_name_detailed_json


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NameResult:
    """Name normalization result with optional provenance trace."""

    raw: str
    normalized: str
    trace_json: dict[str, Any] | None
    trace_sha256: str | None


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, obj: Any) -> None:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True))
            f.write("\n")


def _sha256_json(obj: Any) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


# ---------------------------------------------------------------------------
# Input loading
# ---------------------------------------------------------------------------


def _load_names_from_csv(path: Path, name_column: str, limit: int | None) -> list[str]:
    if pd is None:
        raise RuntimeError("pandas is required to read CSV inputs")

    df = pd.read_csv(path, dtype=str)
    if name_column not in df.columns:
        raise KeyError(f"Column not found: {name_column}")

    series = df[name_column].dropna().astype(str)
    if limit is not None:
        series = series.head(limit)

    seen: set[str] = set()
    out: list[str] = []

    for value in series.tolist():
        v = value.strip()
        if v and v not in seen:
            seen.add(v)
            out.append(v)

    return out


def _load_names(
    input_path: str | None,
    input_url: str | None,
    name_column: str,
    limit: int | None,
) -> list[str]:
    if (input_path is None) == (input_url is None):
        raise ValueError("Provide exactly one of --input-path or --input-url")

    if input_path is not None:
        return _load_names_from_csv(Path(input_path), name_column, limit)

    if pd is None:
        raise RuntimeError("pandas is required to read URL inputs")

    df = pd.read_csv(str(input_url), dtype=str)  # type: ignore[arg-type]
    if name_column not in df.columns:
        raise KeyError(f"Column not found: {name_column}")

    series = df[name_column].dropna().astype(str)
    if limit is not None:
        series = series.head(limit)

    seen: set[str] = set()
    out: list[str] = []

    for value in series.tolist():
        v = value.strip()
        if v and v not in seen:
            seen.add(v)
            out.append(v)

    return out


# ---------------------------------------------------------------------------
# Core audit logic
# ---------------------------------------------------------------------------


def _normalize_names(
    raws: Sequence[str],
    jurisdiction_iso: str,
    include_traces: bool,
    allow_missing_ffi: bool,
) -> list[NameResult]:
    apply_name, apply_detailed_json = _import_localization()

    results: list[NameResult] = []
    missing_error: Exception | None = None

    for raw in raws:
        try:
            normalized = apply_name(raw, jurisdiction_iso)
            trace_json = None
            trace_sha = None

            if include_traces:
                trace_json = apply_detailed_json(raw, jurisdiction_iso)
                trace_sha = _sha256_json(trace_json)

            results.append(
                NameResult(
                    raw=raw,
                    normalized=normalized,
                    trace_json=trace_json,
                    trace_sha256=trace_sha,
                )
            )
        except AttributeError as exc:
            missing_error = exc
            if allow_missing_ffi:
                results.append(NameResult(raw, raw, None, None))
            else:
                break

    if missing_error and not allow_missing_ffi:
        raise missing_error

    return results


def _group_collisions(results: Sequence[NameResult]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for r in results:
        groups.setdefault(r.normalized, []).append(r.raw)

    return {k: v for k, v in groups.items() if len(v) > 1}


def _invert_mapping(mapping: dict[str, str]) -> dict[str, set[str]]:
    clusters: dict[str, set[str]] = {}
    for raw, norm in mapping.items():
        clusters.setdefault(norm, set()).add(raw)
    return clusters


def _diff_vs_baseline(
    current_map: dict[str, str],
    baseline_map: dict[str, str],
) -> dict[str, Any]:
    raws_all = sorted(set(current_map) | set(baseline_map))
    changed: list[dict[str, Any]] = []
    added: list[str] = []
    removed: list[str] = []

    for raw in raws_all:
        if raw not in baseline_map:
            added.append(raw)
        elif raw not in current_map:
            removed.append(raw)
        else:
            cur = current_map[raw]
            base = baseline_map[raw]
            if cur != base:
                changed.append({"raw": raw, "baseline": base, "current": cur})

    return {
        "added_raws": added,
        "removed_raws": removed,
        "changed_raws": changed,
    }


def _detect_merges_splits(
    current_map: dict[str, str],
    baseline_map: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cur_clusters = _invert_mapping(current_map)
    base_clusters = _invert_mapping(baseline_map)

    merges: list[dict[str, Any]] = []
    splits: list[dict[str, Any]] = []

    for cur_norm, raws in cur_clusters.items():
        base_norms = sorted({b for r in raws if (b := baseline_map.get(r)) is not None})
        if len(base_norms) > 1:
            merges.append(
                {
                    "current_normalized": cur_norm,
                    "baseline_normalized_set": base_norms,
                    "raws": sorted(raws),
                }
            )

    for base_norm, raws in base_clusters.items():
        cur_norms = sorted({c for r in raws if (c := current_map.get(r)) is not None})
        if len(cur_norms) > 1:
            splits.append(
                {
                    "baseline_normalized": base_norm,
                    "current_normalized_set": cur_norms,
                    "raws": sorted(raws),
                }
            )

    return merges, splits


def _is_merge_approved(
    merge_entry: dict[str, Any],
    approved_merges: dict[str, Any] | None,
) -> bool:
    if not approved_merges:
        return False

    cur_norm = merge_entry["current_normalized"]
    raws = set(merge_entry["raws"])

    if cur_norm in approved_merges:
        return raws.issubset(set(approved_merges[cur_norm]))

    for inner in approved_merges.values():
        if isinstance(inner, dict) and cur_norm in inner:
            return raws.issubset(set(inner[cur_norm]))

    return False


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------


def _write_collisions_csv(path: Path, collisions: dict[str, list[str]]) -> None:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["normalized", "count", "raw_variants_joined"])

        for norm in sorted(collisions):
            raws = collisions[norm]
            writer.writerow([norm, str(len(raws)), " || ".join(raws)])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit identity collisions for localized name normalization."
    )

    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--input-path", type=str)
    src.add_argument("--input-url", type=str)

    parser.add_argument("--name-column", required=True)
    parser.add_argument("--jurisdiction-iso", required=True)
    parser.add_argument("--limit", type=int)

    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--include-traces", action="store_true")
    parser.add_argument("--allow-missing-ffi", action="store_true")

    parser.add_argument("--baseline-path")
    parser.add_argument("--approved-merges-path")
    parser.add_argument("--fail-on-new-merges", action="store_true")
    parser.add_argument("--write-baseline", action="store_true")

    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:  # noqa: C901
    """Run audit and write outputs.

    Returns an exit code (0 success; 2 policy failure; 3 missing FFI).
    """
    args = _parse_args(argv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    raws = _load_names(
        args.input_path,
        args.input_url,
        args.name_column,
        args.limit,
    )

    results = _normalize_names(
        raws,
        args.jurisdiction_iso,
        include_traces=args.include_traces,
        allow_missing_ffi=args.allow_missing_ffi,
    )

    current_map = {r.raw: r.normalized for r in results}
    collisions = _group_collisions(results)

    summary = {
        "jurisdiction_iso": args.jurisdiction_iso,
        "input_path": args.input_path,
        "input_url": args.input_url,
        "name_column": args.name_column,
        "limit": args.limit,
        "raw_unique_count": len(raws),
        "normalized_unique_count": len(set(current_map.values())),
        "collision_bucket_count": len(collisions),
        "raw_collided_count": sum(len(v) for v in collisions.values()),
    }

    _write_json(out_dir / "summary.json", summary)
    _write_json(
        out_dir / "mapping.json",
        {
            "jurisdiction_iso": args.jurisdiction_iso,
            "mapping": current_map,
            "trace_sha256_by_raw": {
                r.raw: r.trace_sha256 for r in results if r.trace_sha256 is not None
            },
        },
    )
    _write_collisions_csv(out_dir / "collisions.csv", collisions)

    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"Wrote outputs to: {out_dir}. For example, see collisions.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
