# Contributing

This document describes the recommended workflow for developing in this Civic Interconnect repository.
It applies to our schemas, Rust, Python packages, adapters, and tools.

## 1. Prerequisites

Install the following.

### Required

- **Git** (configure `user.name` and `user.email`)
- **uv** Python environment + package manager
- **Rust toolchain** (`rustc --version`)
- **VS Code** (recommended)

### Rust Install/Update for Windows PowerShell

Important: Accept the default MSVC toolchain.
If the installer prompts for Microsoft C++ build tools,
install them, including the Desktop development with C++ workload
and Windows SDK.
This provides the native linker needed to compile Rust extensions on Windows.

```pwsh
# Install the official Rust toolchain manager.
winget install --id Rustlang.Rustup --exact

# After installation, open a NEW PowerShell terminal.

# Verify Rust and Cargo are available.
rustup --version
rustc --version
cargo --version

# Verify the active toolchain.
rustup show active-toolchain

# Install Microsoft C++ Build Tools with the required workload.
winget install --id Microsoft.VisualStudio.2022.BuildTools --exact --override "--passive --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"

# Open a new terminal and run existing project checks.
.\rel.ps1

# Periodically: Update the installed Rust toolchains.
rustup update
```

### Rust Install/Update for mac and Linux

```bash
# Install the official Rust toolchain manager.
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Verify the installation in a new terminal.
rustup --version
rustc --version
cargo --version

# Periodically: Update the installed Rust toolchains.
rustup update
```

### Optional (if building wrappers)

C# Wrapper

- [Build Tools for VS 2022 (as needed)](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)
- [C# dev kit by Microsoft](https://learn.microsoft.com/en-us/dotnet/core/install/windows#install-with-visual-studio-code)

Java Wrapper

- JDK

## 2. Fork and Clone

1. Fork the repository on GitHub.
2. Clone your fork and open it in VS Code.

```shell
git clone https://github.com/YOUR_USERNAME/civic-interconnect.git
cd civic-interconnect
```

Open the repo in VS Code.

## 3. One-Time Setup

Create a local environment and install dependencies.

```shell
uv sync
```

## 4. Validate Changes

Run the commands relevant to the changes being made.
Some commands validate existing work;
others regenerate files, update datasets, or perform maintenance.

```shell
git pull origin main

# after changing about.yaml files (for vertical slice examples)
uv run python tools/validate_verticals.py

# after changing localization/ yaml files
uv run python tools/sync_localization_assets.py

# after changing schemas or vocabs, revalidate
uv run python tools/validate_schemas.py

# regenerate rust
uv run python tools/codegen_rust.py

# build and install cep_py for cx commands
cd src/rust/cep-py
cargo build
uv run maturin develop --release
cd ../../../

# regenerate constants
uv run cx codegen-python-constants

cargo fmt
cargo check

# clean and fix rust as needed
cargo clean -p cep-core
cargo clean -p cep-py
cargo fix --lib -p cep-core --allow-dirty --allow-staged
cargo fix --lib -p cep-domains --allow-dirty --allow-staged
cargo fix --lib -p cep-py --allow-dirty --allow-staged

# build rust
cargo build -p cep-core
cargo build -p cep-domains
cargo build -p cep-py
cargo build

# run rust tests
cargo test -p cep-core entity
cargo test -p cep-core -q
cargo test -- --nocapture -q

# regenerate example records
uv run cx generate-example examples/entity --overwrite

# test the chicago identity localization
uv run pytest src/python/tests/identity/test_us_il_vendor_snfei.py -s

# run audit tool to get collisions (e.g. out/audit/us_il_vendor/collisions.csv)
uv run python tools/audit_identity_collisions.py   --input-url "https://raw.githubusercontent.com/civic-interconnect/civic-data-identity-us-il/refs/heads/main/data/identity/chicago_contracts_vendors_sample_20k.csv"   --name-column "Vendor Name"   --jurisdiction-iso US-IL   --limit 20000   --include-traces   --out-dir out/audit/us_il_vendor

uv run pytest src/python/tests/audit/test_us_il_vendor_audit.py -s

# fetch Italy OCDS sample to
# src/python/tests/data/procurement/it_anac/ocds_sample.jsonl
uv run python tools/fetch_procurement_it_anac_sample.py

# install adapters and test
uv pip install -e adapters/eu/ted_eforms/python

uv run pytest adapters/eu/ted_eforms/python/tests -q
uv run pytest adapters/eu/ted_eforms/python/tests -s

uv run python -c "from ci_adapters.eu.ted_eforms import TedEformsAdapter; a=TedEformsAdapter(); r=a.adapt_records([{'notice_id':'N1'}]); print(r.envelopes[0])"

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
uv run python -m zensical build
```

## 5. Commit and Push

```shell
git add .
git commit -m "Your message"
git push -u origin main
```

## 6. Open a Pull Request

Open a PR from your fork to the `main` branch of the target repository.

Guidelines for good PRs are here: `REF_PULL_REQUESTS.md`

## Licensing

This project is licensed under the MIT License.
By submitting a pull request, issue, or other contribution to this repository, you agree that your contribution will be licensed under the MIT License.

This ensures that all schemas, vocabularies, code, documentation, and other materials in the Civic Interconnect ecosystem can be freely used, extended, and implemented by governments, nonprofits, researchers, companies, and individuals.

## Questions

If you have questions, please open an issue in this repository.

Thank you for contributing.
