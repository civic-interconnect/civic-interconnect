# Contributing

This document describes the recommended workflow for developing in this Civic Interconnect repository.  
It applies to our schemas, Rust rust, Python packages, adapters, and tools.

---

## 1. Prerequisites

Install the following.

### Required

-   **Git** (configure `user.name` and `user.email`)
-   **uv** – Python environment + package manager
-   **Rust toolchain** (`rustc --version`)
-   **VS Code** (recommended)

### Recommended VS Code Extensions

-   charliermarsh.ruff - Python linting/formatting
-   fill-labs.dependi - check dependencies
-   ms-python.python - Python support
-   ms-python.vscode-pylance - Fast, strict language server
-   rust-lang.rust-analyzer – Rust language support
-   streetsidesoftware.code-spell-checker – Spell checking in code/docs
-   tamasfe.even-better-toml – TOML editing (pyproject, config)
-   usernamehw.errorlens – Inline diagnostics (optional, but helpful)

You can see your installed extensions by running: `code.cmd --list-extensions`

### Optional (if building wrappers)

C# Wrapper

-   [Build Tools for VS 2022 (as needed)](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)
-   [C# dev kit by Microsoft](https://learn.microsoft.com/en-us/dotnet/core/install/windows#install-with-visual-studio-code)

Java Wrapper

-   JDK

---

## 2. Fork and Clone

1. Fork the repository on GitHub.
2. Clone your fork and open it in VS Code.

```shell
git clone https://github.com/YOUR_USERNAME/civic-interconnect.git
cd civic-interconnect
```

Open the repo in VS Code.

---

## 3. One-Time Setup

Create a local environment and install dependencies.

```shell
uv python pin 3.12
uv venv

.venv\Scripts\activate # Windows
# source .venv/bin/activate  # Mac/Linux/WSL

uv sync --extra dev --extra docs --upgrade
uvx pre-commit install
```

---

## 4. Validate Changes

Before committing, pull code, run Python checks, run Rust checks.

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



# Python quality checks
git add .
uvx ruff check . --fix
uvx ruff format .
uvx deptry .
uv run pyright
uv run pytest
uvx pre-commit autoupdate
uvx pre-commit run --all-files
```

---

## 5. Build Package and Docs

```shell
uv build
uv run mkdocs build --strict
uv run mkdocs serve
```

---

## 6. Commit and Push

```shell
git add .
git commit -m "Your message"
git push -u origin main
```

---

## 7. Open a Pull Request

Open a PR from your fork to the `main` branch of the target repository.

Guidelines for good PRs are here: `REF_PULL_REQUESTS.md`

---

## Licensing

This project is licensed under the Apache License, Version 2.0.  
By submitting a pull request, issue, or other contribution to this repository, you agree that your contribution will be licensed under the Apache License, Version 2.0.

This ensures that all schemas, vocabularies, code, documentation, and other materials in the Civic Interconnect ecosystem can be freely used, extended, and implemented by governments, nonprofits, researchers, companies, and individuals.

---

## Questions

If you have questions, please open an issue in this repository.

Thank you for contributing.
