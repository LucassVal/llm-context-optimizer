"""
cascade_consolidator.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-105-cascade-consolidator.py
Preserved for backward compatibility with existing importers.
DO NOT add new imports here. Use NC-CORE-FR-105-cascade-consolidator.py directly.
"""
# NC-DS-122: backward-compat shim
import importlib.util as _util
import sys as _sys
from pathlib import Path as _Path

_NC_FILE = _Path(__file__).parent / "NC-CORE-FR-105-cascade-consolidator.py"
_spec = _util.spec_from_file_location(__name__ + "_impl", _NC_FILE)
_mod = _util.module_from_spec(_spec)
_mod.__package__ = __package__
_spec.loader.exec_module(_mod)
# Re-export all public symbols into this namespace
_sys.modules[__name__].__dict__.update(
    {k: v for k, v in _mod.__dict__.items() if not k.startswith("_")}
)
del _util, _sys, _Path, _NC_FILE, _spec, _mod
