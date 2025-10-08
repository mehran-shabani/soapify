"""Compatibility package exposing the summarizer app via the project namespace."""
from __future__ import annotations

from importlib import import_module
import sys

_module = import_module("summarizer")

# Expose the underlying module's namespace and path for submodule lookups.
__all__ = getattr(_module, "__all__", [])
if not __all__:
    __all__ = [name for name in dir(_module) if not name.startswith("_")]
__path__ = getattr(_module, "__path__", [])

globals().update({name: getattr(_module, name) for name in __all__})
sys.modules[__name__] = _module
