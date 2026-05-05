#!/usr/bin/env python3
"""
Atualiza a tabela SSOT no NC-NAM-FR-001-naming-convention.md adicionando artefatos faltantes.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent


def load_drift_report():
    with open(BASE_DIR / "drift_report.json", "r", encoding="utf-8") as f:
        return json.load(f)


def find_physical_path(filename):
    """Encontra o caminho físico do arquivo, ignorando pasta RENAMED."""
    # Diretórios base para busca
    base_dirs = [
        BASE_DIR / "01_neocortex_framework",
        BASE_DIR / "neocortex",
        BASE_DIR / "scripts",
        BASE_DIR / "01_neocortex_framework" / "scripts",
        BASE_DIR / "01_neocortex_framework" / "neocortex",
        BASE_DIR / "01_neocortex_framework" / "neocortex" / "core" / "services",
        BASE_DIR / "01_neocortex_framework" / "neocortex" / "mcp" / "tools",
        BASE_DIR / "01_neocortex_framework" / "neocortex" / "core" / "hooks",
        BASE_DIR / "01_neocortex_framework" / "neocortex" / "core" / "utils",
        BASE_DIR
        / "01_neocortex_framework"
        / "neocortex"
        / "core"
        / "review"
        / "validators",
        BASE_DIR / "01_neocortex_framework" / "DIR-PRF-FR-001-profiles-main",
    ]
    for base in base_dirs:
        if not base.exists():
            continue
        for path in base.rglob(filename):
            if "RENAMED" not in str(path):
                rel_path = path.relative_to(BASE_DIR)
                return "\\" + str(rel_path).replace("/", "\\")
    # Se não encontrou, retorna None
    return None


def update_markdown_table(md_path, missing_svc, missing_tool, missing_scr):
    """Atualiza a tabela no arquivo markdown."""
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Encontrar linha de início da tabela: "## 📂 SSOT Geral do Sistema (Snapshot Local)"
    start_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == "## 📂 SSOT Geral do Sistema (Snapshot Local)":
            start_idx = i
            break

    if start_idx == -1:
        print("Não encontrou seção da tabela SSOT")
        return False

    # Encontrar linha onde a tabela termina (próximo '---' após start_idx)
    end_idx = -1
    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip().startswith("---"):
            end_idx = i
            break

    if end_idx == -1:
        print("Não encontrou fim da tabela")
        return False

    # A tabela está entre start_idx e end_idx.
    # Inserir novas linhas antes do end_idx.
    # Formato de linha: | nome | - | local | - |
    new_lines = []

    # Adicionar NC-SVC
    for filename in missing_svc:
        path = find_physical_path(filename)
        if path:
            new_lines.append(f"| {filename} | - | {path} | - |\n")
        else:
            print(f"AVISO: Arquivo não encontrado: {filename}")

    # Adicionar NC-TOOL
    for filename in missing_tool:
        # Ignorar duplicatas que contêm "nc-tool-fr-" como parte duplicada (ex: NC-TOOL-FR-033-nc-tool-fr-035-task.py)
        # Esses são arquivos renomeados na pasta RENAMED, que já temos versão original.
        # A função find_physical_path já ignora pasta RENAMED, então se não encontrar, não adiciona.
        path = find_physical_path(filename)
        if path:
            new_lines.append(f"| {filename} | - | {path} | - |\n")
        else:
            print(f"AVISO: Arquivo não encontrado: {filename}")

    # Adicionar NC-SCR
    for filename in missing_scr:
        path = find_physical_path(filename)
        if path:
            new_lines.append(f"| {filename} | - | {path} | - |\n")
        else:
            print(f"AVISO: Arquivo não encontrado: {filename}")

    # Inserir novas linhas antes da linha end_idx
    lines = lines[:end_idx] + new_lines + lines[end_idx:]

    # Escrever de volta
    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(lines)

    return True


def main():
    md_path = (
        BASE_DIR
        / "01_neocortex_framework"
        / "DIR-DOC-FR-001-docs-main"
        / "NC-NAM-FR-001-naming-convention.md"
    )
    if not md_path.exists():
        print(f"Arquivo não encontrado: {md_path}")
        return

    report = load_drift_report()
    missing_svc = report["svc"]["missing_in_table"]
    missing_tool = report["tool"]["missing_in_table"]
    missing_scr = report["scr"]["missing_in_table"]

    print(f"NC-SVC faltantes: {len(missing_svc)}")
    print(f"NC-TOOL faltantes: {len(missing_tool)}")
    print(f"NC-SCR faltantes: {len(missing_scr)}")

    # Não filtrar mais; a função find_physical_path já lida com duplicatas
    filtered_tool = missing_tool
    print(f"NC-TOOL após filtro: {len(filtered_tool)}")

    success = update_markdown_table(md_path, missing_svc, filtered_tool, missing_scr)
    if success:
        print("Tabela SSOT atualizada com sucesso.")
    else:
        print("Falha ao atualizar tabela.")


if __name__ == "__main__":
    main()
