"""CEP Exchange builder facade.

This module defines the Python-facing API for constructing CEP Exchange records
from normalized adapter payloads.

Adapters should call build_exchange_from_raw()
instead of constructing CEP envelopes directly.

This module uses the Rust core (via the cep_py extension) when
available, and falls back to a pure Python implementation otherwise.
"""
