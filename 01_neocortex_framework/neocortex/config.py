# Strangler Fig wrapper - re-exports from NC-CFG-FR-002-config.py
# Keep for backward compatibility. Migrate imports to NC- name.
# R09: importlib for hyphenated module names.
import importlib.util
import pathlib
import sys

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    def get_config() -> Any: ...

_nc = pathlib.Path(__file__).parent / "NC-CFG-FR-002-config.py"
_spec = importlib.util.spec_from_file_location("config", str(_nc))
_mod = importlib.util.module_from_spec(_spec)
sys.modules["config"] = _mod
_spec.loader.exec_module(_mod)
__all__ = [x for x in dir(_mod) if not x.startswith('_')]
for _a in __all__: globals()[_a] = getattr(_mod, _a)
