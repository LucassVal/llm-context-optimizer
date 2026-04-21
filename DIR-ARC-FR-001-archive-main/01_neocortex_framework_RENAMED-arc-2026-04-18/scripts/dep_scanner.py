# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation']
hash: "auto-generated"
---"""

"""
dep_scanner.py - Mapeia todos os imports externos usados no projeto
e verifica quais esto instalados / podem ser importados.
"""
import ast
import importlib
import os
import sys
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).parent.parent
EXCLUDE_DIRS = {"__pycache__", ".venv", "DIR-ARC-FR-001-archive-main", "DIR-BAK-FR-001-backup-main", "backup_root"}

STDLIB = set(sys.stdlib_module_names)  # Python 3.10+

def collect_files():
    files = []
    for dirpath, dirnames, filenames in os.walk(BASE):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS
                       and "backup_root" not in dirpath]
        for f in filenames:
            if f.endswith(".py"):
                files.append(Path(dirpath) / f)
    return sorted(files)

def extract_imports(filepath):
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return set()
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                imports.add(node.module.split(".")[0])
    return imports

def test_import(module_name):
    try:
        importlib.import_module(module_name)
        return True, None
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def main():
    files = collect_files()
    print(f"Scanning {len(files)} Python files...\n")

    # Map: module -> list of files that use it
    module_files = defaultdict(list)
    for f in files:
        for imp in extract_imports(f):
            rel = str(f).replace(str(BASE) + os.sep, "")
            module_files[imp].append(rel)

    # Separate stdlib vs external
    external = {m: fs for m, fs in module_files.items()
                if m not in STDLIB and not m.startswith("neocortex") and m not in ("__future__", "")}

    print("=== EXTERNAL IMPORTS FOUND ===")
    ok_mods = []
    fail_mods = []

    for mod in sorted(external.keys()):
        ok, err = test_import(mod)
        files_using = external[mod]
        if ok:
            ok_mods.append(mod)
            print(f"  [OK ] {mod:<30} ({len(files_using)} files)")
        else:
            fail_mods.append((mod, err, files_using))
            print(f"  [ERR] {mod:<30} -> {err}")
            for fu in files_using[:5]:
                print(f"         used in: {fu}")

    print("\n=== SUMMARY ===")
    print(f"External modules: {len(external)}")
    print(f"  Importable (OK):  {len(ok_mods)}")
    print(f"  MISSING (ERR):    {len(fail_mods)}")

    if fail_mods:
        print("\n=== MISSING DEPENDENCIES ===")
        for mod, err, files_using in fail_mods:
            print(f"  MISSING: {mod}")
            print(f"    Error: {err}")
            print(f"    Used in ({len(files_using)} files): {', '.join(files_using[:3])}")
        print("\n  pip install: " + " ".join(m for m, _, _ in fail_mods))

if __name__ == "__main__":
    main()
