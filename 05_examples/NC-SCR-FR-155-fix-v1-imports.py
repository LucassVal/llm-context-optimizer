#!/usr/bin/env python3
"""
NC-SCR-FR-155 - Fix relative imports in v1/ tools
Corrige os imports relativos nas tools v1/ para imports absolutos.
"""

import os
import re
import sys
from pathlib import Path

def fix_imports_in_file(file_path):
    """Corrigir imports relativos em um arquivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrões de import a corrigir
    patterns = [
        (r'from \.\.\.core\.(\w+) import', r'from neocortex.core import \1'),
        (r'from \.\.\.core\.(\w+_service) import', r'from neocortex.core import get_\1'),
        (r'from \.\.\.infra\.(\w+) import', r'from neocortex.infra import \1'),
        (r'from \.\.\.repositories\.(\w+) import', r'from neocortex.repositories import \1'),
        (r'from \.\.\.config import', r'from neocortex.config import'),
        (r'from \.\.\.utils import', r'from neocortex.utils import'),
    ]
    
    original = content
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Corrigir imports em todas as tools v1/."""
    project_root = Path(__file__).parent.parent
    tools_dir = project_root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools" / "v1"
    
    if not tools_dir.exists():
        print(f"Diretório não encontrado: {tools_dir}")
        return False
    
    fixed_count = 0
    total_count = 0
    
    for file in tools_dir.glob("*.py"):
        total_count += 1
        if fix_imports_in_file(file):
            print(f"  [FIXED] {file.name}")
            fixed_count += 1
        else:
            print(f"  [OK] {file.name}")
    
    print(f"\n[RESULT] Arquivos corrigidos: {fixed_count}/{total_count}")
    
    # Testar um arquivo corrigido
    if fixed_count > 0:
        print("\n[TEST] Testando import de um arquivo corrigido...")
        test_file = list(tools_dir.glob("*.py"))[0]
        try:
            import sys
            sys.path.insert(0, str(project_root / "01_neocortex_framework"))
            spec = __import__('importlib').util.spec_from_file_location(
                'test_tool', test_file
            )
            module = __import__('importlib').util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"  [PASS] {test_file.name} importado com sucesso!")
        except Exception as e:
            print(f"  [FAIL] {test_file.name}: {e}")
    
    return fixed_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)