#!/usr/bin/env python3
import json
from pathlib import Path

BASE_DIR = Path.cwd()
CORE_DIR = BASE_DIR / "01_neocortex_framework" / "neocortex"

json_files = list(CORE_DIR.rglob("*.json"))
# Remover arquivos em __pycache__ se houver
json_files = [f for f in json_files if "__pycache__" not in str(f)]

print(f"Processando {len(json_files)} arquivos JSON")

for filepath in json_files:
    print(f"  {filepath.relative_to(BASE_DIR)}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"    ERRO leitura: {e}")
        continue

    # Determinar metadata
    rel = filepath.relative_to(BASE_DIR)
    path_str = str(rel).lower()
    name = filepath.stem.lower()

    domain = "schemas" if "schemas" in path_str else "core"
    layer = "core"
    type_ = "schema" if "schemas" in path_str else "manifest"
    tags = []
    # extrair tags do nome
    import re

    clean = re.sub(
        r"^(nc|fr|ds|int|svc|cfg|hk|utl|tool|scr|arc|bak|boot|aln|aud|tst|dpl|api|lib|prf|nam)-",
        "",
        name,
    )
    parts = re.split(r"[-_.]", clean)
    for p in parts:
        if len(p) > 2 and p not in ["json", "md", "mdc"]:
            tags.append(p)
    tags = tags[:10]

    meta = {
        "_meta": {
            "domain": domain,
            "layer": layer,
            "type": type_,
            "tags": tags,
            "hash": "auto-generated",
        }
    }

    # Se j tem _meta, atualizar, seno adicionar como primeira chave
    if "_meta" in data:
        data["_meta"].update(meta["_meta"])
        new_data = data
    else:
        new_data = meta
        new_data.update(data)  # mantm outras chaves aps _meta

    # Escrever de volta com indentao 2
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    print("    OK")

print("Concludo.")
