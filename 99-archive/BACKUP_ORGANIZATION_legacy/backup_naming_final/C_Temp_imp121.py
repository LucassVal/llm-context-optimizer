import importlib.util
from pathlib import Path

try:
    script_path = Path(r'NC-SCR-FR-146-hook-boot-loader.py')
    spec = importlib.util.spec_from_file_location('scr146', str(script_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    has_main = hasattr(mod, 'main')
    has_load_hooks = hasattr(mod, 'load_hooks')
    
    print(f'IMPORT OK {has_main or has_load_hooks}')
except Exception as e:
    print(f'IMPORT FAIL: {e}')