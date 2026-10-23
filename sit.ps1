#Requires -Version 7.0

<#
============================================================
sit.ps1 (ALL-PY-SRC-REPOS)
============================================================
Updated: 2026-09-25

This is a PowerShell script for managing
the development environment of the project.

PowerShell (pwsh) is available for all major operating systems
and is a popular terminal for developers.

To get situated, run this script in your PowerShell terminal:

.\sit.ps1

#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# set up or update Python environment
uvx pup-clean --delete
uv self update
uv python install
uv lock --upgrade
uv sync
uv audit

# set up and run git hooks
uvx prek install --force
uvx prek update
git add -A
uvx prek run --all-files
# repeat if changes were made
uvx prek run --all-files

# run common chores
uv run ruff format .
uv run ruff check . --fix
uv run ty check
uv run python -m pytest
uv run python -m zensical build --strict

Write-Host "All commands executed successfully."
Write-Host "Run a Python module to verify .venv/ is working correctly."
