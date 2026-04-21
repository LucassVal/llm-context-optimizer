#!/usr/bin/env python3
"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.767104'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-064-artifact-catalog
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

# Fix encoding for Windows (UTF-8)
import sys

if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation', 'catalog', 'analysis']
hash: "auto-generated"
---

NC-SCR-FR-064-artifact-catalog.py
Catlogo Semntico de Artefatos (.py e .yaml)

Este script gera um catlogo de todos os arquivos .py e .yaml no projeto,
extraindo:
1. Propsito (docstring ou primeiro comentrio)
2. Dependncias/imports (para .py)
3. Referncias internas (para .yaml)
4. Metadados (tamanho, data)

O resultado  um arquivo JSON estruturado e um relatrio Markdown.
"""

import ast
import importlib.util
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Configurao de caminhos
BASE_DIR = Path(__file__).parent.parent.parent  # TURBOQUANT_V42
OUTPUT_DIR = BASE_DIR / "DIR-DOC-FR-001-docs-main"
JSON_OUTPUT = OUTPUT_DIR / "artifact_catalog.json"
MD_OUTPUT = OUTPUT_DIR / "artifact_catalog.md"

# Import WALService
_wal_path = (
    BASE_DIR
    / "01_neocortex_framework/neocortex/core/services/NC-SVC-FR-016-wal-service.py"
)
_spec = importlib.util.spec_from_file_location("wal_service", _wal_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
WALService = _mod.WALService

# Ignorar diretrios
IGNORE_DIRS = {
    "__pycache__",
    ".git",
    ".ruff_cache",
    ".neocortex",
    ".nc",
    ".kilocode",
    "node_modules",
    "venv",
    "env",
    "dist",
    "build",
}


def find_files(extensions: List[str]) -> List[Path]:
    """Encontra todos os arquivos com as extenses fornecidas."""
    files = []
    for root, dirs, filenames in os.walk(BASE_DIR):
        # Filtrar diretrios ignorados
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(Path(root) / filename)
    return files


def extract_python_info(filepath: Path) -> Dict[str, Any]:
    """Extrai informaes de um arquivo Python."""
    info = {
        "purpose": "",
        "imports": [],
        "functions": [],
        "classes": [],
        "metadata": {},
    }

    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))

        # Extrair docstring do mdulo
        docstring = ast.get_docstring(tree)
        if docstring:
            info["purpose"] = docstring.strip()[:500]  # Limitar tamanho

        # Extrair imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    info["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    info["imports"].append(
                        f"{module}.{alias.name}" if module else alias.name
                    )

            # Extrair funes e classes
            if isinstance(node, ast.FunctionDef):
                func_doc = ast.get_docstring(node)
                info["functions"].append(
                    {"name": node.name, "purpose": func_doc[:200] if func_doc else ""}
                )
            elif isinstance(node, ast.ClassDef):
                class_doc = ast.get_docstring(node)
                info["classes"].append(
                    {"name": node.name, "purpose": class_doc[:200] if class_doc else ""}
                )

    except (SyntaxError, UnicodeDecodeError) as e:
        info["error"] = str(e)

    return info


def extract_yaml_info(filepath: Path) -> Dict[str, Any]:
    """Extrai informaes de um arquivo YAML."""
    info = {"purpose": "", "references": [], "keys": [], "metadata": {}}

    try:
        content = filepath.read_text(encoding="utf-8")
        data = yaml.safe_load(content)

        # Extrair propsito do primeiro comentrio
        lines = content.split("\n")
        for line in lines[:10]:  # Verificar primeiras 10 linhas
            if line.strip().startswith("#"):
                info["purpose"] = line.strip()[1:].strip()[:500]
                break

        # Extrair referncias (caminhos de arquivo)
        def find_references(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    info["keys"].append(new_path)
                    # Verificar se o valor parece um caminho de arquivo
                    if isinstance(value, str):
                        if any(
                            value.endswith(ext)
                            for ext in [".py", ".yaml", ".json", ".md", ".txt"]
                        ):
                            if "/" in value or "\\" in value:
                                info["references"].append(value)
                    find_references(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_references(item, f"{path}[{i}]")

        find_references(data)

    except (yaml.YAMLError, UnicodeDecodeError) as e:
        info["error"] = str(e)

    return info


def analyze_file(filepath: Path) -> Dict[str, Any]:
    """Analisa um arquivo e retorna metadados."""
    stat = filepath.stat()
    rel_path = filepath.relative_to(BASE_DIR)

    base_info = {
        "path": str(rel_path),
        "name": filepath.name,
        "extension": filepath.suffix.lower(),
        "size_bytes": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
    }

    if filepath.suffix.lower() == ".py":
        analysis = extract_python_info(filepath)
    elif filepath.suffix.lower() in [".yaml", ".yml"]:
        analysis = extract_yaml_info(filepath)
    else:
        analysis = {"purpose": "", "imports": [], "references": []}

    base_info.update(analysis)
    return base_info


def generate_catalog() -> Dict[str, Any]:
    """Gera o catlogo completo."""
    print("[SEARCH] Procurando arquivos .py e .yaml...")
    py_files = find_files([".py"])
    yaml_files = find_files([".yaml", ".yml"])

    print(
        f"[INFO] Encontrados: {len(py_files)} arquivos .py, {len(yaml_files)} arquivos .yaml"
    )

    catalog = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "base_dir": str(BASE_DIR),
            "total_py": len(py_files),
            "total_yaml": len(yaml_files),
        },
        "python_files": [],
        "yaml_files": [],
    }

    # Analisar arquivos Python
    print("[ANALYSIS] Analisando arquivos Python...")
    for i, filepath in enumerate(py_files):
        if i % 50 == 0:
            print(f"  Progresso: {i}/{len(py_files)}")
        catalog["python_files"].append(analyze_file(filepath))

    # Analisar arquivos YAML
    print("[ANALYSIS] Analisando arquivos YAML...")
    for i, filepath in enumerate(yaml_files):
        if i % 20 == 0:
            print(f"  Progresso: {i}/{len(yaml_files)}")
        catalog["yaml_files"].append(analyze_file(filepath))

    return catalog


def save_json(catalog: Dict[str, Any]) -> None:
    """Salva o catlogo em JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print(f"[OK] JSON salvo em: {JSON_OUTPUT}")


def save_markdown(catalog: Dict[str, Any]) -> None:
    """Gera um relatrio Markdown."""
    with open(MD_OUTPUT, "w", encoding="utf-8") as f:
        f.write("# Catlogo de Artefatos\n\n")
        f.write(f"*Gerado em: {catalog['metadata']['generated']}*\n\n")

        f.write("## Estatsticas\n")
        f.write(f"- Arquivos Python: {catalog['metadata']['total_py']}\n")
        f.write(f"- Arquivos YAML: {catalog['metadata']['total_yaml']}\n\n")

        f.write("## Arquivos Python\n")
        f.write("| Arquivo | Propsito | Importaes |\n")
        f.write("|---------|-----------|-------------|\n")

        for item in catalog["python_files"][:100]:  # Limitar a 100 para legibilidade
            purpose = item.get("purpose", "")
            if len(purpose) > 100:
                purpose = purpose[:97] + "..."

            imports = ", ".join(item.get("imports", [])[:5])
            if len(item.get("imports", [])) > 5:
                imports += f" ... (+{len(item.get('imports', [])) - 5} mais)"

            f.write(f"| `{item['path']}` | {purpose} | {imports} |\n")

        if len(catalog["python_files"]) > 100:
            f.write(
                f"\n*... e mais {len(catalog['python_files']) - 100} arquivos Python.*\n\n"
            )

        f.write("\n## Arquivos YAML\n")
        f.write("| Arquivo | Propsito | Referncias |\n")
        f.write("|---------|-----------|-------------|\n")

        for item in catalog["yaml_files"][:50]:  # Limitar a 50
            purpose = item.get("purpose", "")
            if len(purpose) > 100:
                purpose = purpose[:97] + "..."

            refs = ", ".join(item.get("references", [])[:3])
            if len(item.get("references", [])) > 3:
                refs += f" ... (+{len(item.get('references', [])) - 3} mais)"

            f.write(f"| `{item['path']}` | {purpose} | {refs} |\n")

        if len(catalog["yaml_files"]) > 50:
            f.write(
                f"\n*... e mais {len(catalog['yaml_files']) - 50} arquivos YAML.*\n"
            )

        f.write("\n## Metadados Completos\n")
        f.write("Os dados completos esto disponveis em formato JSON:\n")
        f.write(f"`{JSON_OUTPUT.relative_to(BASE_DIR)}`\n")

    print(f"[OK] Markdown salvo em: {MD_OUTPUT}")


def main():
    """Funo principal."""
    print("=" * 60)
    print("Catlogo Semntico de Artefatos")
    print("=" * 60)

    catalog = generate_catalog()
    # WAL transaction
    wal = WALService()
    session_id = f"ciclo3-artifact-catalog-{datetime.now().strftime('%Y%m%dT%H%M%S')}"
    with wal.transaction(session_id, "NC-SCR-FR-064", ticket_id="NC-DS-089") as txn:
        # Save JSON
        before_json = txn.before_write(JSON_OUTPUT)
        save_json(catalog)
        txn.after_write(JSON_OUTPUT, before_json)
        # Save Markdown
        before_md = txn.before_write(MD_OUTPUT)
        save_markdown(catalog)
        txn.after_write(MD_OUTPUT, before_md)

    print("\n[SUMMARY] Resumo:")
    print(f"   Arquivos Python analisados: {len(catalog['python_files'])}")
    print(f"   Arquivos YAML analisados: {len(catalog['yaml_files'])}")
    print(f"   Sada JSON: {JSON_OUTPUT.relative_to(BASE_DIR)}")
    print(f"   Sada Markdown: {MD_OUTPUT.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
