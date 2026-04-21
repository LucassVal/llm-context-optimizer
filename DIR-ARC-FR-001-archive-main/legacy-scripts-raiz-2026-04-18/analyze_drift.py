#!/usr/bin/env python3
"""
Script para mapear artefatos NC-SVC/TOOL/SCR declarados no NC-NAM-FR-001 vs arquivos físicos existentes.
Gera relatório de drift e atualiza SSOT.
"""

import json
from pathlib import Path
import sys

BASE_DIR = Path(__file__).parent


def extract_table_from_md(md_path):
    """Extrai tabela SSOT do arquivo markdown."""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # A tabela começa após "## 📂 SSOT Geral do Sistema (Snapshot Local)"
    # e termina antes do próximo "---"
    # Vamos extrair linhas da tabela usando regex simples
    # Cada linha da tabela tem formato | nome | desc | local | palavras |
    # Vamos buscar todas as linhas que começam com "|" e têm pelo menos 3 pipes
    lines = content.split("\n")
    in_table = False
    table_rows = []
    for line in lines:
        if line.strip().startswith("## 📂 SSOT Geral do Sistema (Snapshot Local)"):
            in_table = True
            continue
        if in_table and line.strip().startswith("---"):
            break
        if in_table and line.strip().startswith("|"):
            # Limpar espaços e dividir por pipe
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 3:
                # nome, desc, local, palavras (opcional)
                name = parts[0]
                desc = parts[1] if len(parts) > 1 else ""
                location = parts[2] if len(parts) > 2 else ""
                keywords = parts[3] if len(parts) > 3 else ""
                table_rows.append(
                    {
                        "name": name,
                        "description": desc,
                        "location": location,
                        "keywords": keywords,
                    }
                )
    return table_rows


def filter_artifacts(table_rows):
    """Filtra apenas artefatos NC-SVC, NC-TOOL, NC-SCR."""
    svc = []
    tool = []
    scr = []
    for row in table_rows:
        name = row["name"]
        if name.startswith("NC-SVC-"):
            svc.append(row)
        elif name.startswith("NC-TOOL-"):
            tool.append(row)
        elif name.startswith("NC-SCR-"):
            scr.append(row)
    return svc, tool, scr


def check_file_exists(location):
    """Verifica se o arquivo físico existe."""
    # location é relativo ao diretório raiz do projeto? Parece ser caminho absoluto relativo à raiz do projeto.
    # Exemplo: \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-000-brain.py
    # Remover a barra inicial
    if location.startswith("\\"):
        location = location[1:]
    path = BASE_DIR / location.replace("\\", "/")
    return path.exists(), path


def scan_physical_files():
    """Varre o sistema de arquivos para encontrar todos os arquivos NC-SVC, NC-TOOL, NC-SCR."""
    svc_files = []
    tool_files = []
    scr_files = []

    # Padrões de busca
    for svc_path in BASE_DIR.rglob("NC-SVC-*.py"):
        svc_files.append(str(svc_path.relative_to(BASE_DIR)))
    for tool_path in BASE_DIR.rglob("NC-TOOL-*.py"):
        tool_files.append(str(tool_path.relative_to(BASE_DIR)))
    for scr_path in BASE_DIR.rglob("NC-SCR-*.py"):
        scr_files.append(str(scr_path.relative_to(BASE_DIR)))

    return svc_files, tool_files, scr_files


def generate_drift_report(
    table_svc, table_tool, table_scr, physical_svc, physical_tool, physical_scr
):
    """Gera relatório de drift entre tabela SSOT e arquivos físicos."""
    report = {
        "svc": {"missing_in_physical": [], "missing_in_table": [], "matched": []},
        "tool": {"missing_in_physical": [], "missing_in_table": [], "matched": []},
        "scr": {"missing_in_physical": [], "missing_in_table": [], "matched": []},
    }

    # Mapear nomes de arquivos da tabela (apenas nome, sem caminho)
    table_svc_names = {row["name"] for row in table_svc}
    table_tool_names = {row["name"] for row in table_tool}
    table_scr_names = {row["name"] for row in table_scr}

    # Mapear nomes de arquivos físicos (extrair nome do caminho)
    physical_svc_names = {Path(f).name for f in physical_svc}
    physical_tool_names = {Path(f).name for f in physical_tool}
    physical_scr_names = {Path(f).name for f in physical_scr}

    # Comparar
    for row in table_svc:
        if row["name"] not in physical_svc_names:
            report["svc"]["missing_in_physical"].append(row)
        else:
            report["svc"]["matched"].append(row)

    for filename in physical_svc_names:
        if filename not in table_svc_names:
            report["svc"]["missing_in_table"].append(filename)

    for row in table_tool:
        if row["name"] not in physical_tool_names:
            report["tool"]["missing_in_physical"].append(row)
        else:
            report["tool"]["matched"].append(row)

    for filename in physical_tool_names:
        if filename not in table_tool_names:
            report["tool"]["missing_in_table"].append(filename)

    for row in table_scr:
        if row["name"] not in physical_scr_names:
            report["scr"]["missing_in_physical"].append(row)
        else:
            report["scr"]["matched"].append(row)

    for filename in physical_scr_names:
        if filename not in table_scr_names:
            report["scr"]["missing_in_table"].append(filename)

    return report


def main():
    md_path = (
        BASE_DIR
        / "01_neocortex_framework"
        / "DIR-DOC-FR-001-docs-main"
        / "NC-NAM-FR-001-naming-convention.md"
    )
    if not md_path.exists():
        print(f"Arquivo não encontrado: {md_path}")
        sys.exit(1)

    print("Extraindo tabela SSOT...")
    table_rows = extract_table_from_md(md_path)
    print(f"Total de linhas na tabela: {len(table_rows)}")

    svc_table, tool_table, scr_table = filter_artifacts(table_rows)
    print(f"NC-SVC na tabela: {len(svc_table)}")
    print(f"NC-TOOL na tabela: {len(tool_table)}")
    print(f"NC-SCR na tabela: {len(scr_table)}")

    print("\nVarrendo arquivos físicos...")
    physical_svc, physical_tool, physical_scr = scan_physical_files()
    print(f"NC-SVC físicos: {len(physical_svc)}")
    print(f"NC-TOOL físicos: {len(physical_tool)}")
    print(f"NC-SCR físicos: {len(physical_scr)}")

    print("\nGerando relatório de drift...")
    report = generate_drift_report(
        svc_table, tool_table, scr_table, physical_svc, physical_tool, physical_scr
    )

    # Exibir relatório
    for artifact_type in ["svc", "tool", "scr"]:
        print(f"\n=== NC-{artifact_type.upper()} ===")
        data = report[artifact_type]
        print(f"  Matched: {len(data['matched'])}")
        print(f"  Missing in physical: {len(data['missing_in_physical'])}")
        for item in data["missing_in_physical"][:5]:
            print(f"    - {item['name']} (local: {item['location']})")
        if len(data["missing_in_physical"]) > 5:
            print(f"    ... e mais {len(data['missing_in_physical']) - 5}")
        print(f"  Missing in table: {len(data['missing_in_table'])}")
        for item in data["missing_in_table"][:5]:
            print(f"    - {item}")
        if len(data["missing_in_table"]) > 5:
            print(f"    ... e mais {len(data['missing_in_table']) - 5}")

    # Salvar relatório em JSON
    report_path = BASE_DIR / "drift_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nRelatório salvo em: {report_path}")

    # Atualizar SSOT (NC-NAM-FR-001) - adicionar seções missing?
    # Por enquanto, apenas gerar relatório.
    # A atualização do SSOT será feita manualmente com base no relatório.

    return report


if __name__ == "__main__":
    main()
