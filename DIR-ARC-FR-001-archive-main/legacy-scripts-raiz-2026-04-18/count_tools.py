#!/usr/bin/env python3
from pathlib import Path

BASE = Path(__file__).parent / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"
if not BASE.exists():
    BASE = Path(__file__).parent / "neocortex" / "mcp" / "tools"

tool_files = []
for f in BASE.glob("NC-TOOL-FR-*.py"):
    if "RENAMED" not in str(f):
        tool_files.append(f)

print(f"Total de arquivos NC-TOOL-FR-*.py (excluindo RENAMED): {len(tool_files)}")

# Extrair número e nome
for f in sorted(tool_files):
    print(f.name)

# Verificar se tem register_tool
import importlib.util

count_register = 0
for f in tool_files:
    spec = importlib.util.spec_from_file_location(f.stem, f)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        if hasattr(module, "register_tool"):
            count_register += 1
        else:
            print(f"  {f.name} SEM register_tool")
    except Exception as e:
        print(f"  {f.name} erro ao carregar: {e}")

print(f"Arquivos com register_tool: {count_register}")
