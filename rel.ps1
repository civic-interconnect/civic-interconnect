#Requires -Version 7.0

<#
============================================================
rel.ps1 (CIVIC-INTERCONNECT)
============================================================
Updated: 2026-10-22

Run from the repository root:

.\rel.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Set up Python 3.14.
# uvx pup-clean --delete
# uv self update
# uv python install
uv lock --upgrade
uv sync
uv audit
if ($LASTEXITCODE -ne 0) { throw "uv sync failed" }

# Build and install the Rust Python extension.
Push-Location src/rust/cep-py
try {
    uv run --no-sync maturin develop --release
    if ($LASTEXITCODE -ne 0) { throw "maturin develop failed" }
}
finally {
    Pop-Location
}

# Install the local adapter used by tests.
uv pip install -e adapters/eu/ted_eforms/python
if ($LASTEXITCODE -ne 0) { throw "adapter installation failed" }

# Verify Python 3.14 and the Rust extension.
uv run --no-sync python -c "import sys, cep_py; assert sys.version_info[:2] == (3, 14); print(sys.version); print(cep_py.__file__)"
if ($LASTEXITCODE -ne 0) { throw "Python 3.14 or cep_py import failed" }

# Run the Rust tests.
cargo test --locked --workspace
if ($LASTEXITCODE -ne 0) { throw "Rust tests failed" }

# Run Python tests without coverage output; skip the test that overwrites out/us_il_normalized_sample.csv.
uv run --no-sync python -m pytest --no-cov -p no:cacheprovider --deselect src/python/tests/identity/test_us_il_vendor_snfei.py::test_snfei_chicago_vendors_subset
if ($LASTEXITCODE -ne 0) { throw "Python tests failed" }

# Build and check a temporary wheel, then remove it.
$verifyDir = ".verify-py314"
if (Test-Path $verifyDir) { throw "$verifyDir already exists; refusing to overwrite it" }
try {
    uv build --out-dir "$verifyDir/dist"
    if ($LASTEXITCODE -ne 0) { throw "wheel build failed" }
    # Validate only the generated Python distributions.
    uvx twine check ".verify-py314/dist/*.whl" ".verify-py314/dist/*.tar.gz"
    if ($LASTEXITCODE -ne 0) { throw "distribution check failed" }
    $wheel = (Get-ChildItem "$verifyDir/dist/*.whl" | Select-Object -First 1).FullName
    uv run --no-project --python 3.14 --with $wheel python -c "import civic_interconnect, cep_py; print('Installed Python 3.14 wheel works')"
    if ($LASTEXITCODE -ne 0) { throw "installed wheel cannot import civic_interconnect and cep_py" }
}
finally {
    if (Test-Path $verifyDir) { Remove-Item $verifyDir -Recurse -Force }
}

# Set up and run git hooks.
uvx prek install --force
if ($LASTEXITCODE -ne 0) { throw "prek installation failed" }

uvx prek update
if ($LASTEXITCODE -ne 0) { throw "prek update failed" }

git add -A
if ($LASTEXITCODE -ne 0) { throw "git add failed" }

# First pass may modify files.
uvx prek run --all-files

# Second pass must pass without modifications.
uvx prek run --all-files
if ($LASTEXITCODE -ne 0) { throw "prek checks failed" }

# Format Python code.
uv run ruff format .
if ($LASTEXITCODE -ne 0) { throw "Ruff formatting failed" }

# Lint Python code and apply fixes.
uv run ruff check . --fix
if ($LASTEXITCODE -ne 0) { throw "Ruff linting failed" }

# Type-check Python code.
uv run ty check
if ($LASTEXITCODE -ne 0) { throw "ty check failed" }

# Run Python tests with coverage, excluding the CSV-writing test.
uv run python -m pytest --deselect src/python/tests/identity/test_us_il_vendor_snfei.py::test_snfei_chicago_vendors_subset
if ($LASTEXITCODE -ne 0) { throw "Python tests failed" }

# Build documentation.
uv run python -m zensical build --strict
if ($LASTEXITCODE -ne 0) { throw "Zensical build failed" }

# Show any tracked-file changes.
git status --short
if ($LASTEXITCODE -ne 0) { throw "git status failed" }
