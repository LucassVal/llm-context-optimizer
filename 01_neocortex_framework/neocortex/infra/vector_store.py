# Strangler Fig wrapper — re-exports from NC-INFRA-FR-*
# This file kept for backward compatibility. Migrate imports to NC- name.
# See R09: importlib for hyphenated module names.
import importlib.util, sys, pathlib
_nc_module = pathlib.Path(__file__).parent / "NC-INFRA-FR-009-vector-store.py"
spec = importlib.util.spec_from_file_location("vector_store", _nc_module)
_mod = importlib.util.module_from_spec(spec)
sys.modules["vector_store"] = _mod
spec.loader.exec_module(_mod)
# Re-export all public names
__all__ = [x for x in dir(_mod) if not x.startswith('_')]
for _attr in __all__:
    globals()[_attr] = getattr(_mod, _attr)
