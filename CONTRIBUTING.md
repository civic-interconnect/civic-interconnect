# Contributing

This document describes the recommended workflow for developing in this Civic Interconnect repository.  
It applies to our schemas, Rust crates, Python packages, adapters, and tools.

---

## 1. Prerequisites

Install the following.

### Required

- **Git** (configure `user.name` and `user.email`)
- **uv** – Python environment + package manager  
- **Rust toolchain** (`rustc --version`)
- **VS Code** (recommended)

### Recommended VS Code Extensions

- charliermarsh.ruff - Python linting/formatting
- fill-labs.dependi - check dependencies
- ms-python.python - Python support
- ms-python.vscode-pylance - Fast, strict language server
- rust-lang.rust-analyzer – Rust language support
- streetsidesoftware.code-spell-checker – Spell checking in code/docs
- tamasfe.even-better-toml – TOML editing (pyproject, config)
- usernamehw.errorlens – Inline diagnostics (optional, but helpful)

You can see your installed extensions by running: `code.cmd --list-extensions`

### Optional (if building wrappers)

C# Wrapper

- [Build Tools for VS 2022 (as needed)](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)
- [C# dev kit by Microsoft](https://learn.microsoft.com/en-us/dotnet/core/install/windows#install-with-visual-studio-code)

Java Wrapper

- JDK

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
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # Mac or Linux

uv sync --extra dev --extra docs --upgrade
uv run pre-commit install
```

---

## 4. Validate Changes

Before committing, pull code, run Python checks, run Rust checks.

```shell
git pull origin main

# after changing schemas, regenerate rust 
uv run python tools/codegen_rust.py
uv run cx codegen-python-constants
cargo fmt
cargo build
cargo test -p cep-core
uv run maturin develop --release

uvx ruff check . --fix
uvx ruff format .
uvx deptry .
uv run pyright
uv run pytest
uvx pre-commit autoupdate
uvx pre-commit run --all-files
```

In Windows, Open root in File Explorer and then open a PowerShell terminal if needed.
Test rust logic until there are no errors and all tests pass.

```shell
rustc --version

# fix crates
cargo fix --lib -p cep-core --allow-dirty --allow-staged
cargo fix --lib -p cep-py --allow-dirty --allow-staged
cargo fix --lib  --allow-dirty --allow-staged -q

# build crates
cargo build -p cep-core
cargo build

# run tests
cargo test -p cep-core entity
cargo test -p cep-core -q
cargo test -- --nocapture -q

# build and install cep_py
cargo build
cd crates/cep-py
cargo build
uv run maturin develop --release
cd ../../

uv run cx generate-example examples/entity --overwrite

```

---

## 5. Build Package and/or Docs

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

Guidelines for good PRs are here:  `REF_PULL_REQUESTS.md`

---

## Licensing

This project is licensed under the Apache License, Version 2.0.  
By submitting a pull request, issue, or other contribution to this repository, you agree that your contribution will be licensed under the Apache License, Version 2.0.

This ensures that all schemas, vocabularies, code, documentation, and other materials in the Civic Interconnect ecosystem can be freely used, extended, and implemented by governments, nonprofits, researchers, companies, and individuals.

---

## Questions

If you have questions, open an issue in the target repository.  

Thank you for contributing.
