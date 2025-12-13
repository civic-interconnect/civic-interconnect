"""EU TED eForms adapter package.

Import root is intentionally stable and short: ci_adapter.
Adapter identity lives in about.yaml at the adapter unit root.
"""

from .adapter import TedEformsAdapter

__all__ = ["TedEformsAdapter"]
