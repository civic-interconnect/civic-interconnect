# tools/fetch_procurement_it_anac_sample.py
#!/usr/bin/env python3
"""Fetch a small, reproducible OCDS JSONL sample for Italy ANAC (via OCP Data Registry).

and write it into the repo as a CI-safe fixture.

Default behavior:
- Download a year-sized .jsonl.gz (default: 2022) into out/cache/.
- Stream-decompress and select a deterministic sample of releases by hashing ocid.
- Write JSONL sample to: src/python/tests/data/procurement/it_anac/ocds_sample.jsonl
- Write metadata to:      src/python/tests/data/procurement/it_anac/ocds_sample.meta.json

Why hash-based sampling?
- "First N lines" is not stable if upstream ordering changes.
- Hash(ocid) sampling is deterministic and tends to remain stable across updates.

Examples:
  uv run python tools/fetch_procurement_it_anac_sample.py

  uv run python tools/fetch_procurement_it_anac_sample.py \
    --url "https://data.open-contracting.org/en/publication/117/download?name=2025.jsonl.gz" \
    --max-items 500

  uv run python tools/fetch_procurement_it_anac_sample.py \
    --max-items 200 \
    --threshold-per-10000 30 \
    --force-download \
    --force-write

Exit codes:
- 0: success
- 1: failure
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Any, Protocol
from urllib.parse import urlparse
import urllib.request

if TYPE_CHECKING:
    from collections.abc import Iterable

DEFAULT_URL = "https://data.open-contracting.org/en/publication/117/download?name=2022.jsonl.gz"


class HashLike(Protocol):
    """Update Hash-like object protocol."""

    def update(self, __data: bytes, /) -> None: ...  # noqa: D102


def _repo_root() -> Path:
    """Find the repo root directory.

    tools/ is at repo root/tools/, so parent of tools/ is repo root.
    """
    return Path(__file__).resolve().parent.parent


def _sha256_update(h: HashLike, b: bytes) -> None:
    h.update(b)


def _validate_url_for_download(url: str) -> None:
    """Validate that a URL is an http(s) URL with a network location.

    This is a deliberate security step to prevent unexpected schemes like
    file:, ftp:, etc. The urlopen call below is audited and then annotated
    for Ruff (S310).
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        raise ValueError(f"Unsupported URL scheme: {parsed.scheme!r}. Only https/http allowed.")
    if not parsed.netloc:
        raise ValueError("URL must include a network location (host).")
    if parsed.username or parsed.password:
        raise ValueError("URL must not contain embedded credentials.")


def _download_file(url: str, dest: Path, *, force: bool) -> tuple[str, int]:
    """Download url -> dest (binary). Returns (sha256_hex, bytes_written)."""
    _validate_url_for_download(url)

    if dest.exists() and not force:
        # If it already exists, compute sha so metadata is correct.
        h = hashlib.sha256()
        n = 0
        with dest.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                _sha256_update(h, chunk)
                n += len(chunk)
        return (h.hexdigest(), n)

    dest.parent.mkdir(parents=True, exist_ok=True)

    h = hashlib.sha256()
    n = 0

    req = urllib.request.Request(  # noqa: S310
        url,
        headers={
            # Some hosts reject default Python UA.
            "User-Agent": "civic-interconnect-fetch/1.0 (python urllib)",
            "Accept": "*/*",
        },
        method="GET",
    )

    # NOTE: urlopen is safe here because we validated scheme/netloc above in _validate_url_for_download.
    # The URL is guaranteed to be http/https only, with no credentials or custom schemes.
    # S310 is suppressed because _validate_url_for_download ensures only http/https schemes are allowed.
    with urllib.request.urlopen(req, timeout=300) as resp, dest.open("wb") as out:  # noqa: S310
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
            _sha256_update(h, chunk)
            n += len(chunk)

    return (h.hexdigest(), n)


def _hash_bucket_0_9999(s: str) -> int:
    # Stable integer bucket for deterministic sampling.
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % 10000


def _select_release(obj: dict[str, Any], threshold_per_10000: int) -> bool:
    ocid = obj.get("ocid")
    if not isinstance(ocid, str) or not ocid.strip():
        return False
    b = _hash_bucket_0_9999(ocid)
    return b < threshold_per_10000


def _iter_jsonl_gz(path: Path) -> Iterable[dict[str, Any]]:
    """Yield decoded JSON objects from a .jsonl.gz file (one JSON object per line)."""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except json.JSONDecodeError:
                # Skip malformed lines.
                continue
            if isinstance(obj, dict):
                yield obj


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]], *, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {path} (use --force-write)")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for obj in rows:
            f.write(json.dumps(obj, sort_keys=True))
            f.write("\n")


def _write_json(path: Path, obj: Any, *, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {path} (use --force-write)")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Fetch and sample Italy ANAC OCDS JSONL (.gz) into repo test fixtures."
    )
    p.add_argument("--url", type=str, default=DEFAULT_URL, help="URL to a .jsonl.gz OCDS download.")
    p.add_argument(
        "--cache-dir",
        type=str,
        default=str(Path("out") / "cache" / "procurement" / "it_anac"),
        help="Directory under repo root to store downloaded artifacts.",
    )
    p.add_argument(
        "--out-sample",
        type=str,
        default=str(
            Path("src")
            / "python"
            / "tests"
            / "data"
            / "procurement"
            / "it_anac"
            / "ocds_sample.jsonl"
        ),
        help="Path (relative to repo root) for the sampled JSONL fixture.",
    )
    p.add_argument(
        "--out-meta",
        type=str,
        default=str(
            Path("src")
            / "python"
            / "tests"
            / "data"
            / "procurement"
            / "it_anac"
            / "ocds_sample.meta.json"
        ),
        help="Path (relative to repo root) for metadata JSON.",
    )
    p.add_argument(
        "--max-items",
        type=int,
        default=300,
        help="Maximum number of releases to include in the sample.",
    )
    p.add_argument(
        "--threshold-per-10000",
        type=int,
        default=25,
        help="Sampling rate: include release if hash(ocid) mod 10000 < threshold. 25 ~= 0.25%.",
    )
    p.add_argument(
        "--force-download", action="store_true", help="Redownload even if cached file exists."
    )
    p.add_argument(
        "--force-write", action="store_true", help="Overwrite sample/meta outputs if they exist."
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Fetch and sample Italy ANAC OCDS JSONL (.gz) into repo test fixtures."""
    args = _parse_args(argv)

    root = _repo_root()
    cache_dir = root / Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Choose a deterministic cache file name from the URL.
    url_hash = hashlib.sha256(args.url.encode("utf-8")).hexdigest()[:12]
    gz_path = cache_dir / f"anac_ocds_{url_hash}.jsonl.gz"

    try:
        gz_sha256, gz_bytes = _download_file(args.url, gz_path, force=bool(args.force_download))
    except Exception as e:
        print(f"ERROR: download failed: {e}", file=sys.stderr)
        return 1

    picked: list[dict[str, Any]] = []
    scanned = 0

    try:
        for obj in _iter_jsonl_gz(gz_path):
            scanned += 1

            if not _select_release(obj, int(args.threshold_per_10000)):
                continue

            picked.append(obj)
            if len(picked) >= int(args.max_items):
                break

    except Exception as e:
        print(f"ERROR: failed to parse gz JSONL: {e}", file=sys.stderr)
        return 1

    out_sample = root / Path(args.out_sample)
    out_meta = root / Path(args.out_meta)

    try:
        _write_jsonl(out_sample, picked, force=bool(args.force_write))
        meta = {
            "source_url": args.url,
            "fetched_at_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "cached_gz_path": str(gz_path.relative_to(root)),
            "cached_gz_sha256": gz_sha256,
            "cached_gz_bytes": gz_bytes,
            "sample_max_items": int(args.max_items),
            "sample_threshold_per_10000": int(args.threshold_per_10000),
            "sample_items_written": len(picked),
            "lines_scanned_until_stop": scanned,
            "notes": "Sample selection is deterministic by hash(ocid).",
        }
        _write_json(out_meta, meta, force=bool(args.force_write))
    except Exception as e:
        print(f"ERROR: failed to write outputs: {e}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {"ok": True, "sample_items_written": len(picked), "out_sample": str(out_sample)},
            indent=2,
        )
    )
    print(f"Metadata written to: {out_meta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
