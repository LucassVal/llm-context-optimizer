# Strangler wrapper → NC-REP-FR-001-file-system-repository.py (T0-fixed 2026-05-04)
import importlib.util, sys
from pathlib import Path
_path = Path(__file__).parent / "NC-REP-FR-001-file-system-repository.py"
_name = "neocortex.repositories.file_system_repository"
_spec = importlib.util.spec_from_file_location(_name, str(_path))
_mod = importlib.util.module_from_spec(_spec)
_mod.__package__ = "neocortex.repositories"
sys.modules[_name] = _mod
_spec.loader.exec_module(_mod)
for _attr in dir(_mod):
    if not _attr.startswith('_'):
        globals()[_attr] = getattr(_mod, _attr)
