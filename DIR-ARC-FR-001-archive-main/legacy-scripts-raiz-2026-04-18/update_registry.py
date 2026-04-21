#!/usr/bin/env python3
import yaml
from pathlib import Path

BASE_DIR = Path(__file__).parent
REGISTRY_PATH = (
    BASE_DIR
    / "01_neocortex_framework"
    / "DIR-DOC-FR-001-docs-main"
    / "NC-GOV-FR-004-fr-artifacts-registry.yaml"
)
TOOLS_DIR = BASE_DIR / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"


def load_yaml():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def save_yaml(data):
    with open(REGISTRY_PATH, "w", encoding="utf-8", newline="\n") as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120,
        )


def get_existing_tool_paths(data):
    existing = []
    if "fr_artifacts_mapping" in data and "TOOL" in data["fr_artifacts_mapping"]:
        for entry in data["fr_artifacts_mapping"]["TOOL"]:
            if isinstance(entry, dict) and "path" in entry:
                existing.append(entry["path"])
    return existing


def main():
    if not REGISTRY_PATH.exists():
        print("Registry não encontrado")
        return

    data = load_yaml()
    existing_paths = get_existing_tool_paths(data)

    # Coletar todos os arquivos NC-TOOL-FR-*.py
    tool_files = []
    for f in TOOLS_DIR.glob("NC-TOOL-FR-*.py"):
        if "RENAMED" not in str(f):
            # Caminho relativo a partir da raiz do projeto
            rel_path = f.relative_to(BASE_DIR)
            path_str = str(rel_path).replace("\\", "/")
            tool_files.append(path_str)

    print(f"Total de tools físicas: {len(tool_files)}")
    print(f"Paths já no registry: {len(existing_paths)}")

    # Adicionar as que faltam
    added = 0
    for path in tool_files:
        if path not in existing_paths:
            # Criar entrada básica
            entry = {
                "path": path,
                "purpose": "Ferramenta MCP NeoCortex",
                "governance_rules": ["R04", "R07", "R14"],
            }
            data["fr_artifacts_mapping"]["TOOL"].append(entry)
            added += 1

    # Ordenar por nome de arquivo
    if added > 0:
        data["fr_artifacts_mapping"]["TOOL"] = sorted(
            data["fr_artifacts_mapping"]["TOOL"], key=lambda x: x["path"]
        )
        print(f"Adicionadas {added} novas tools ao registry.")

    # Atualizar contagem total
    if "current_state" in data:
        data["current_state"]["total_fr_files_mapped"] = len(existing_paths) + added
        # Atualizar coverage_percentage? Não temos total_fr_files_found atualizado.
        # Podemos manter.

    save_yaml(data)
    print("Registry atualizado.")


if __name__ == "__main__":
    main()
