# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3
# Fix encoding for Windows (UTF-8)


import sys

if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.707207'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-023-ssot-auditor
related_ssot:
  - NC-SCR-FR-023
  - NC-NAM-FR-001
  - NC-NAM-FR-001-naming-convention
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-023-ssot-auditor.py
Cruza a lista de arquivos reais mapeados pela KGS com o SSOT de Nomenclatura (NC-NAM-FR-001).
Gera relatorio agrupado por pastas para encontrar Arquivos Fantasma e Links Mortos.
Autor: T0 (NeoCortex)
Data: 2026-04-14
"""

import json
from collections import defaultdict
from pathlib import Path

# Configuraes
PROJECT_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main"
COVERAGE_REPORT_JSON = DOCS_DIR / "coverage_report.json"
SSOT_NAMING_MD = DOCS_DIR / "NC-NAM-FR-001-naming-convention.md"

SSOT_REPORT_JSON = DOCS_DIR / "ssot_audit_report.json"
SSOT_REPORT_MD = DOCS_DIR / "ssot_audit_report.md"


def load_coverage_files() -> list[dict]:
    if not COVERAGE_REPORT_JSON.exists():
        print(f"Erro: {COVERAGE_REPORT_JSON} no encontrado. Gerao abortada.")
        return []
    with open(COVERAGE_REPORT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("details", [])


def parse_ssot_table() -> list[str]:
    filenames = []
    if not SSOT_NAMING_MD.exists():
        return filenames

    with open(SSOT_NAMING_MD, "r", encoding="utf-8") as f:
        in_table = False
        for line in f:
            line = line.strip()
            if "| Nome |" in line and "| Local |" in line:
                in_table = True
                continue
            if in_table and line.startswith("|---"):
                continue
            if in_table and line.startswith("|"):
                parts = line.split("|")
                if len(parts) >= 3:
                    name = parts[1].strip()
                    if name:
                        filenames.append(name)
            elif in_table and not line:
                in_table = False  # Fim da tabela
    return filenames


def generate_report(coverage_details, ssot_filenames):
    ssot_set = set(ssot_filenames)

    physical_map = {}
    ghosts_by_folder = defaultdict(list)
    documented_by_folder = defaultdict(list)

    for detail in coverage_details:
        path_str = detail["path"]
        path_obj = Path(path_str)
        name = path_obj.name
        folder = str(path_obj.parent)

        physical_map[name] = path_str

        if name in ssot_set:
            documented_by_folder[folder].append(name)
        else:
            ghosts_by_folder[folder].append(name)

    # Dead Links
    physical_set = set(physical_map.keys())
    dead_links = [name for name in ssot_set if name not in physical_set]

    # Prepara relatorio
    total_physical = len(physical_set)
    total_ssot = len(ssot_set)
    total_ghosts = sum(len(x) for x in ghosts_by_folder.values())
    total_dead = len(dead_links)

    report_data = {
        "summary": {
            "total_arquivos_fisicos": total_physical,
            "total_entradas_ssot": total_ssot,
            "total_fantasmas": total_ghosts,
            "total_links_mortos": total_dead,
        },
        "dead_links": dead_links,
        "ghosts_by_folder": ghosts_by_folder,
        "documented_by_folder": documented_by_folder,
    }

    with open(SSOT_REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    md = f"""# Auditoria SSOT vs Materialidade (KGS)

**Data:** 2026-04-14
O relatrio cruza os {total_physical} arquivos materiais da Teia KGS com as {total_ssot} entradas na tabela oficial em `NC-NAM-FR-001`.

** Resumo Executivo**
- **Arquivos Fsicos Indexados:** {total_physical}
- **Entradas na Tabela SSOT:** {total_ssot}
- ** Arquivos Fantasmas (Fsicos NO listados no SSOT):** {total_ghosts}
- ** Links Mortos (Listados no SSOT, mas no existem no disco):** {total_dead}

---

##  Links Mortos (SSOT Defasado)
Estes arquivos constam na Bblia, mas no foram encontrados materialmente pela KGS.
"""
    if dead_links:
        for name in dead_links:
            md += f"- `{name}`\n"
    else:
        md += "Nenhum link morto detectado.\n"

    md += """
---

##  Arquivos Fantasmas (Trabalho Sujo)
Estes arquivos *existem materialmente* e esto na Teia Semntica, mas **no tm registro no SSOT NC-NAM-FR-001**.
Agrupados por Pasta:
"""
    if total_ghosts == 0:
        md += "Nenhum arquivo fantasma detectado. Perfeio arquitetural.\n"
    else:
        for folder, files in sorted(ghosts_by_folder.items()):
            md += f"\n### ` {folder}`\n"
            for f in files:
                md += f"- `{f}`\n"

    md += "\n---\n*Relatrio gerado por NC-SCR-FR-023-ssot-auditor.py*"

    with open(SSOT_REPORT_MD, "w", encoding="utf-8") as f:
        f.write(md)

    print(" NC-SCR-FR-023: Concludo.")
    print(f" Fsicos: {total_physical} | SSOT: {total_ssot}")
    print(f" Fantasmas (No-Documentados): {total_ghosts}")
    print(f" Links Mortos (Inexistentes): {total_dead}")
    print(f" Salvo em {SSOT_REPORT_MD}")


if __name__ == "__main__":
    coverage = load_coverage_files()
    ssot = parse_ssot_table()
    generate_report(coverage, ssot)
