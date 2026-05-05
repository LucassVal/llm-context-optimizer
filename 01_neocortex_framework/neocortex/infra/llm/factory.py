# Strangler Fig wrapper - re-exports from NC-LLM-FR-005-factory.py
# Keep for backward compatibility. Migrate imports to NC- name.
# R09: importlib for hyphenated module names.
import importlib.util, sys, pathlib
_nc = pathlib.Path(__file__).parent / "NC-LLM-FR-005-factory.py"
_spec = importlib.util.spec_from_file_location("factory", str(_nc))
_mod = importlib.util.module_from_spec(_spec)
sys.modules["factory"] = _mod
_spec.loader.exec_module(_mod)
__all__ = [x for x in dir(_mod) if not x.startswith('_')]
for _a in __all__: globals()[_a] = getattr(_mod, _a)
