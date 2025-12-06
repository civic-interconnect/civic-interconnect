"""Top-level package for Civic Interconnect CEP Python helpers.

This module intentionally avoids importing submodules at import time to
prevent circular imports. Callers should import subpackages explicitly, e.g.:

    from ci_cep.localization import load_localization
    from ci_cep.adapters.us_mn_municipality import build_municipality_entity
    from ci_cep.entity.api import build_entity_from_raw
"""
