import py_compile
from pathlib import Path
import sys

try:
    script_path = Path(r'NC-SCR-FR-146-hook-boot-loader.py')
    py_compile.compile(str(script_path), doraise=True)
    print('OK')
except Exception as e:
    print(f'FAIL: {e}')
    sys.exit(1)