#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path.cwd()
CORE_DIR = BASE_DIR / "01_neocortex_framework" / "neocortex"

py_files = list(CORE_DIR.rglob("*.py"))
py_files = [f for f in py_files if "__pycache__" not in str(f)]

errors = []
for f in py_files:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(f)], capture_output=True, text=True
    )
    if result.returncode != 0:
        errors.append((f, result.stderr))

if errors:
    print("[ERROR] Erros de compilao:")
    for f, err in errors:
        print(f"  {f.relative_to(BASE_DIR)}: {err[:200]}")
    sys.exit(1)
else:
    print("[OK] Todos os arquivos Python compilam.")
    sys.exit(0)
