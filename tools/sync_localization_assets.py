#!/usr/bin/env python3
"""Sync protocol localization assets into the Python package tree.

Source of truth:
  repo_root/localization/

Destination (Python package data):
  repo_root/src/python/src/civic_interconnect/cep/localization/

Behavior:
- Deletes the destination directory if it exists.
- Copies the entire tree from source to destination.
- Preserves directory structure and filenames.

Run:
  uv run python tools/sync_localization_assets.py
"""

from pathlib import Path
import shutil


def find_repo_root(start: Path) -> Path:
    """Walk upward from `start` to find the repository root.

    We treat the first directory containing pyproject.toml as repo root.
    """
    current = start.resolve()
    for _ in range(20):
        if (current / "pyproject.toml").is_file():
            return current
        if current.parent == current:
            break
        current = current.parent
    raise RuntimeError("Could not find repo root (pyproject.toml not found).")


def sync_tree(src: Path, dst: Path) -> None:
    """Delete dst if it exists, then copy src tree to dst."""
    if not src.is_dir():
        raise RuntimeError(f"Source localization directory not found: {src}")

    if dst.exists():
        shutil.rmtree(dst)

    dst.parent.mkdir(parents=True, exist_ok=True)

    # copytree preserves structure; copy_function=copy2 preserves metadata
    shutil.copytree(src, dst, copy_function=shutil.copy2)


def main() -> int:
    """Sync localization assets into the Python package tree."""
    repo_root = find_repo_root(Path(__file__).parent)
    src = repo_root / "localization"
    dst = repo_root / "src" / "python" / "src" / "civic_interconnect" / "cep" / "localization"

    sync_tree(src, dst)

    print("Synced localization assets:")
    print(f"  from: {src}")
    print(f"  to:   {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
