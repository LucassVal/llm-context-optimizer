#!/usr/bin/env python3
import re
import json
import sys
from pathlib import Path

BASE_DIR = Path.cwd()
CORE_DIR = BASE_DIR / "01_neocortex_framework" / "neocortex"


def get_metadata(filepath: Path):
    rel = filepath.relative_to(BASE_DIR)
    path_str = str(rel).lower()
    name = filepath.stem.lower()

    # defaults
    domain = "core"
    layer = "core"
    type_ = "file"

    if "mcp/tools" in path_str:
        domain = "orchestration"
        layer = "core"
        type_ = "tool"
    elif "core/services" in path_str:
        domain = "core"
        layer = "core"
        type_ = "service"
    elif "core/config" in path_str:
        domain = "configuration"
        layer = "core"
        type_ = "config"
    elif "core/hooks" in path_str:
        domain = "hooks"
        layer = "core"
        type_ = "hook"
    elif "core/utils" in path_str:
        domain = "utils"
        layer = "core"
        type_ = "utility"
    elif "infra" in path_str:
        domain = "infrastructure"
        layer = "infra"
        type_ = "service"
    elif "repositories" in path_str:
        domain = "persistence"
        layer = "infra"
        type_ = "repository"
    elif "schemas" in path_str:
        domain = "schemas"
        layer = "core"
        type_ = "schema"
    elif "cli" in path_str:
        domain = "cli"
        layer = "core"
        type_ = "cli"
    elif "agent" in path_str:
        domain = "agent"
        layer = "core"
        type_ = "service"
    elif "mcp" in path_str:
        domain = "orchestration"
        layer = "core"
        type_ = "service"

    # tags simples
    tags = []
    # extrair partes do nome
    clean = re.sub(
        r"^(nc|fr|ds|int|svc|cfg|hk|utl|tool|scr|arc|bak|boot|aln|aud|tst|dpl|api|lib|prf|nam)-",
        "",
        name,
    )
    parts = re.split(r"[-_.]", clean)
    for p in parts:
        if len(p) > 2 and p not in ["py", "json", "md", "mdc"]:
            tags.append(p)
    # limitar
    tags = tags[:10]

    return {
        "domain": domain,
        "layer": layer,
        "type": type_,
        "tags": tags,
        "hash": "auto-generated",
    }


def has_frontmatter(content: str):
    return content.lstrip().startswith('"""---')


def add_frontmatter(content: str, metadata: dict):
    front = ['"""---']
    front.append(f"domain: {json.dumps(metadata['domain'])}")
    front.append(f"layer: {json.dumps(metadata['layer'])}")
    front.append(f"type: {json.dumps(metadata['type'])}")
    front.append(f"tags: {json.dumps(metadata['tags'])}")
    front.append(f"hash: {json.dumps(metadata['hash'])}")
    front.append('---"""')
    front.append("")
    return "\n".join(front) + content


def process_py(filepath: Path):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  ERRO leitura {filepath}: {e}")
        return False

    if has_frontmatter(content):
        print(f"  [SKIP] {filepath.relative_to(BASE_DIR)} j tem frontmatter")
        return False

    metadata = get_metadata(filepath)
    new_content = add_frontmatter(content, metadata)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  [OK] {filepath.relative_to(BASE_DIR)} frontmatter adicionado")
    return True


def main():
    py_files = list(CORE_DIR.rglob("*.py"))
    # remover __pycache__
    py_files = [f for f in py_files if "__pycache__" not in str(f)]
    print(f"Processando {len(py_files)} arquivos Python...")
    modified = 0
    for f in py_files:
        if process_py(f):
            modified += 1
    print(f"Modificados: {modified}")

    # validar com py_compile
    print("\nValidando Python com py_compile...")
    import subprocess

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
        return 1
    else:
        print("[OK] Todos os arquivos Python compilam.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
