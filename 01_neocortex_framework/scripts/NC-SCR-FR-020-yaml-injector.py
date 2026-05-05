#!/usr/bin/env python3

# Fix encoding for Windows (UTF-8)
"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.688921'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-020-yaml-injector
---
"""

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.688921'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-020-yaml-injector

---
"""

if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.688921'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-020-yaml-injector
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

import ast
import sys
from pathlib import Path

# Exigir bibliotecas estritas do projeto
try:
    from ruamel.yaml import YAML
except ImportError:
    print("Erro: ruamel.yaml  obrigatrio. Instale no ambiente Qwen 1.5B/3B.")
    sys.exit(1)

def inject_yaml_frontmatter(file_path: Path, new_frontmatter: dict) -> bool:
    """
    Injeta ou atualiza o bloco YAML Frontmatter no incio de um arquivo Python.
    Usa parser em texto (linhas) mas valida a sintaxe final via AST.
    Modo Non-Destructive (Falha de Parsing Aborta a Escrita).
    """
    if not file_path.exists() or file_path.suffix != ".py":
        return False

    try:
        content = file_path.read_text(encoding="utf-8")
        # Valida que o file_path original j  vlido.
        ast.parse(content)
    except SyntaxError:
        print(f"[!] AST SyntaxError (arquivo original corrompido ou python legado): {file_path.name}")
        return False
    except UnicodeDecodeError:
        print(f"[!] Erro de Encoding em {file_path.name}. No  UTF-8.")
        return False

    lines = content.splitlines(keepends=True)
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    import io
    yaml_buffer = io.StringIO()
    yaml_buffer.write('"""---\n')
    yaml.dump(new_frontmatter, yaml_buffer)
    yaml_buffer.write('---"""\n')
    new_docstring_text = yaml_buffer.getvalue()

    replaced = False
    in_docstring = False
    start_idx = -1
    end_idx = -1

    # 1. Busca por frontmatter existente (ruamel type) envolto em docstrings Mltiplas.
    for i, line in enumerate(lines):
        if '"""---' in line or "'''---" in line:
            if not in_docstring:
                in_docstring = True
                start_idx = i
        if in_docstring and ('---"""' in line or "---'''" in line):
            if i > start_idx:
                end_idx = i
                break

    if start_idx != -1 and end_idx != -1:
        # Substitui bloco exato
        new_lines = lines[:start_idx] + [new_docstring_text] + lines[end_idx+1:]
        replaced = True
    else:
        # 2. Injeta no topo, ignorando shebang ou encoding.
        insert_idx = 0

        while insert_idx < len(lines):
            line = lines[insert_idx]
            if line.startswith("#!") or line.startswith("# -*- coding:"):
                insert_idx += 1
            elif line.strip() == "":
                insert_idx += 1
            else:
                break

        new_lines = lines[:insert_idx] + [new_docstring_text, "\n"] + lines[insert_idx:]

    final_content = "".join(new_lines)

    # 3. VALIDAO RIGOROSA AST DA MUTAO (Previne Corrupo Total)
    try:
        ast.parse(final_content)
    except SyntaxError:
        print(f"[CRITICAL] A injeo do YAML quebrou a sintaxe AST de {file_path.name}. Mutao Descartada!")
        return False

    file_path.write_text(final_content, encoding="utf-8")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AST Injector Seguro de Labels Topolgicas (NC-DS-047).")
    parser.add_argument("--test-file", type=str, help="Caminho do arquivo python base para injeo unitria.")
    args = parser.parse_args()

    if args.test_file:
        target = Path(args.test_file)
        # Mock Semntico Experimental
        sample_meta = {
            "domain": "infrastructure",
            "layer": "core_engine",
            "type": "SCRIPT",
            "tier": "T2",
            "parent": [""],
            "children": [],
            "dependence": [""],
            "tags": ["ast", "yaml-injection"]
        }
        print(f"[*] Injetando em: {target.name}")
        success = inject_yaml_frontmatter(target, sample_meta)
        if success:
            print("[+] Injeo concluda e AST do arquivo validado com sucesso.")
        else:
            print("[-] Falha na injeo. Verifique alertas AST.")
    else:
        print("Uso: python NC-SCR-FR-020-yaml-injector.py --test-file foo.py")
