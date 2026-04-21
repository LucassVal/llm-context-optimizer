#!/usr/bin/env python3
"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.772647'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-064
related_ssot:
  - NC-SCR-FR-065-rename-impact-analyzer
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

import sys

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation', 'analysis', 'renaming']
hash: "auto-generated"
---

NC-SCR-FR-065-rename-impact-analyzer.py
Analisador de Impacto de Renomeao

Este script cruza o Catlogo de Artefatos com o Plano de Renomeao
para identificar impactos completos de cada mudana de nome.

Entradas:
1. artifact_catalog.json (gerado por NC-SCR-FR-064)
2. renaming_plan.yaml

Sadas:
1. Relatrio de impacto detalhado (JSON e Markdown)
2. Lista de arquivos que precisam ter imports atualizados
3. Estatsticas de complexidade da renomeao
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Configurao de caminhos
BASE_DIR = Path(__file__).parent.parent.parent  # TURBOQUANT_V42
CATALOG_PATH = BASE_DIR / "DIR-DOC-FR-001-docs-main" / "artifact_catalog.json"
RENAMING_PATH = (
    BASE_DIR
    / "01_neocortex_framework"
    / "DIR-DOC-FR-001-docs-main"
    / "renaming_plan.yaml"
)
OUTPUT_DIR = BASE_DIR / "DIR-DOC-FR-001-docs-main"
JSON_OUTPUT = OUTPUT_DIR / "rename_impact_analysis.json"
MD_OUTPUT = OUTPUT_DIR / "rename_impact_analysis.md"


def load_catalog() -> Dict[str, Any]:
    """Carrega o catlogo de artefatos."""
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_renaming_plan() -> Dict[str, Any]:
    """Carrega o plano de renomeao."""
    with open(RENAMING_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_module_name_from_path(path: str) -> str:
    """Extrai o nome do mdulo Python de um caminho."""
    # Converter caminho para formato de import Python
    # Ex: "neocortex/agent/executor.py" -> "neocortex.agent.executor"
    path = path.replace("\\", "/")

    # Remover extenso
    if path.endswith(".py"):
        path = path[:-3]

    # Remover prefixo de diretrio se existir
    if path.startswith("01_neocortex_framework/"):
        path = path[len("01_neocortex_framework/") :]

    # Substituir barras por pontos
    return path.replace("/", ".")


def extract_filename_from_path(path: str) -> str:
    """Extrai apenas o nome do arquivo de um caminho."""
    return Path(path).name


def find_import_references(
    catalog: Dict[str, Any], module_name: str
) -> List[Dict[str, Any]]:
    """Encontra todos os arquivos que importam um determinado mdulo."""
    references = []

    # Buscar em arquivos Python
    for item in catalog.get("python_files", []):
        imports = item.get("imports", [])

        for imp in imports:
            # Verificar se o import refere-se ao mdulo alvo
            if module_name in imp or imp.endswith(f".{module_name}"):
                references.append(
                    {"file": item["path"], "import": imp, "type": "python_import"}
                )

    # Buscar em arquivos YAML (referncias a caminhos)
    for item in catalog.get("yaml_files", []):
        refs = item.get("references", [])

        for ref in refs:
            if module_name in ref or extract_filename_from_path(module_name) in ref:
                references.append(
                    {"file": item["path"], "reference": ref, "type": "yaml_reference"}
                )

    return references


def analyze_rename_impact(
    renaming_item: Dict[str, Any], catalog: Dict[str, Any]
) -> Dict[str, Any]:
    """Analisa o impacto de uma nica renomeao."""
    old_path = renaming_item.get("old_path", "")
    new_path = renaming_item.get("new_path", "")
    imports_affected = renaming_item.get("imports_affected", [])

    # Extrair nomes de mdulo
    old_module = extract_module_name_from_path(old_path)
    new_module = extract_module_name_from_path(new_path)

    # Encontrar referncias no catlogo
    all_references = find_import_references(catalog, old_module)

    # Filtrar referncias que no esto j listadas em imports_affected
    additional_references = []
    for ref in all_references:
        ref_path = ref["file"]
        # Verificar se j est na lista de imports_affected
        if ref_path not in imports_affected:
            additional_references.append(ref)

    return {
        "old_path": old_path,
        "new_path": new_path,
        "old_module": old_module,
        "new_module": new_module,
        "imports_affected": imports_affected,
        "additional_references_found": additional_references,
        "total_references": len(imports_affected) + len(additional_references),
        "direct_renames": len(imports_affected),
        "indirect_updates_needed": len(additional_references),
    }


def generate_impact_report(
    renaming_plan: Dict[str, Any], catalog: Dict[str, Any]
) -> Dict[str, Any]:
    """Gera relatrio completo de impacto."""
    print("[ANALYSIS] Analisando impacto de renomeao...")

    report = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "total_renames": len(renaming_plan.get("renaming_plan", [])),
            "catalog_files": catalog["metadata"]["total_py"]
            + catalog["metadata"]["total_yaml"],
        },
        "summary": {
            "total_files_to_rename": 0,
            "total_imports_to_update": 0,
            "total_additional_references": 0,
            "complexity_score": 0,  # Pontuao de complexidade (0-100)
        },
        "detailed_analysis": [],
        "files_needing_updates": [],
        "high_impact_renames": [],
    }

    total_direct = 0
    total_indirect = 0

    for i, item in enumerate(renaming_plan.get("renaming_plan", [])):
        print(
            f"  Analisando renomeao {i + 1}/{len(renaming_plan.get('renaming_plan', []))}: {item.get('old_path', '')}"
        )

        impact = analyze_rename_impact(item, catalog)
        report["detailed_analysis"].append(impact)

        # Atualizar totais
        total_direct += len(impact["imports_affected"])
        total_indirect += len(impact["additional_references_found"])

        # Identificar renomeaes de alto impacto
        if len(impact["additional_references_found"]) > 5:
            report["high_impact_renames"].append(
                {
                    "old_path": impact["old_path"],
                    "new_path": impact["new_path"],
                    "direct_affected": len(impact["imports_affected"]),
                    "indirect_affected": len(impact["additional_references_found"]),
                    "risk_level": "HIGH",
                }
            )

        # Coletar arquivos que precisam de atualizao
        for ref in impact["imports_affected"]:
            if ref not in report["files_needing_updates"]:
                report["files_needing_updates"].append(ref)

        for ref in impact["additional_references_found"]:
            file_path = ref["file"]
            if file_path not in report["files_needing_updates"]:
                report["files_needing_updates"].append(file_path)

    # Calcular estatsticas
    report["summary"]["total_files_to_rename"] = len(
        renaming_plan.get("renaming_plan", [])
    )
    report["summary"]["total_imports_to_update"] = total_direct
    report["summary"]["total_additional_references"] = total_indirect

    # Calcular pontuao de complexidade
    if report["summary"]["total_files_to_rename"] > 0:
        complexity = (total_indirect * 100) / (total_direct + total_indirect + 1)
        report["summary"]["complexity_score"] = min(100, int(complexity))

    return report


def save_json_report(report: Dict[str, Any]) -> None:
    """Salva o relatrio em JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"[OK] JSON salvo em: {JSON_OUTPUT}")


def save_markdown_report(report: Dict[str, Any]) -> None:
    """Gera relatrio Markdown."""
    with open(MD_OUTPUT, "w", encoding="utf-8") as f:
        f.write("# Anlise de Impacto de Renomeao\n\n")
        f.write(f"*Gerado em: {report['metadata']['generated']}*\n\n")

        f.write("## Resumo Executivo\n")
        f.write(
            f"- **Total de renomeaes:** {report['summary']['total_files_to_rename']}\n"
        )
        f.write(
            f"- **Arquivos com imports afetados:** {report['summary']['total_imports_to_update']}\n"
        )
        f.write(
            f"- **Referncias adicionais encontradas:** {report['summary']['total_additional_references']}\n"
        )
        f.write(
            f"- **Score de complexidade:** {report['summary']['complexity_score']}/100\n\n"
        )

        f.write("> **Interpretao do Score:**\n")
        f.write("> - 0-30: Baixa complexidade (poucas dependncias)\n")
        f.write("> - 31-70: Mdia complexidade (algumas dependncias crticas)\n")
        f.write("> - 71-100: Alta complexidade (muitas dependncias, risco alto)\n\n")

        if report["high_impact_renames"]:
            f.write("##  Renomeaes de Alto Impacto\n")
            f.write("| Arquivo Antigo | Arquivo Novo | Diretos | Indiretos | Risco |\n")
            f.write("|----------------|--------------|---------|-----------|-------|\n")

            for item in report["high_impact_renames"]:
                f.write(
                    f"| `{item['old_path']}` | `{item['new_path']}` | {item['direct_affected']} | {item['indirect_affected']} | {item['risk_level']} |\n"
                )
            f.write("\n")

        f.write("## Arquivos que Precisam de Atualizao\n")
        f.write(f"Total: {len(report['files_needing_updates'])} arquivos\n\n")

        # Agrupar por tipo de arquivo
        python_files = [f for f in report["files_needing_updates"] if f.endswith(".py")]
        yaml_files = [
            f for f in report["files_needing_updates"] if f.endswith((".yaml", ".yml"))
        ]
        other_files = [
            f
            for f in report["files_needing_updates"]
            if not f.endswith((".py", ".yaml", ".yml"))
        ]

        if python_files:
            f.write("### Arquivos Python\n")
            for file in sorted(python_files)[:50]:  # Limitar a 50
                f.write(f"- `{file}`\n")
            if len(python_files) > 50:
                f.write(f"\n*... e mais {len(python_files) - 50} arquivos Python.*\n")

        if yaml_files:
            f.write("\n### Arquivos YAML\n")
            for file in sorted(yaml_files)[:20]:  # Limitar a 20
                f.write(f"- `{file}`\n")
            if len(yaml_files) > 20:
                f.write(f"\n*... e mais {len(yaml_files) - 20} arquivos YAML.*\n")

        if other_files:
            f.write("\n### Outros Arquivos\n")
            for file in sorted(other_files):
                f.write(f"- `{file}`\n")

        f.write("\n## Anlise Detalhada por Renomeao\n")
        f.write("Para detalhes completos, consulte o arquivo JSON:\n")
        f.write(f"`{JSON_OUTPUT.relative_to(BASE_DIR)}`\n")

        # Mostrar algumas anlises detalhadas
        f.write("\n### Exemplos de Impacto\n")
        for i, analysis in enumerate(report["detailed_analysis"][:5]):  # Primeiras 5
            f.write(
                f"\n#### {i + 1}. `{analysis['old_path']}`  `{analysis['new_path']}`\n"
            )
            f.write(
                f"- **Mdulo:** {analysis['old_module']}  {analysis['new_module']}\n"
            )
            f.write(f"- **Imports diretos:** {len(analysis['imports_affected'])}\n")
            f.write(
                f"- **Referncias adicionais:** {len(analysis['additional_references_found'])}\n"
            )

            if analysis["additional_references_found"]:
                f.write("- **Referncias crticas:**\n")
                for ref in analysis["additional_references_found"][:3]:
                    f.write(f"  - `{ref['file']}` ({ref['type']})\n")
                if len(analysis["additional_references_found"]) > 3:
                    f.write(
                        f"  *... e mais {len(analysis['additional_references_found']) - 3} referncias.*\n"
                    )

    print(f"[OK] Markdown salvo em: {MD_OUTPUT}")


def main():
    """Funo principal."""
    print("=" * 60)
    print("Analisador de Impacto de Renomeao")
    print("=" * 60)

    # Carregar dados
    print("[LOAD] Carregando catlogo de artefatos...")
    catalog = load_catalog()

    print("[LOAD] Carregando plano de renomeao...")
    renaming_plan = load_renaming_plan()

    # Gerar anlise
    report = generate_impact_report(renaming_plan, catalog)

    # Salvar resultados
    save_json_report(report)
    save_markdown_report(report)

    print("\n[SUMMARY] Resumo da Anlise:")
    print(f"   Renomeaes analisadas: {report['summary']['total_files_to_rename']}")
    print(
        f"   Imports diretos afetados: {report['summary']['total_imports_to_update']}"
    )
    print(
        f"   Referncias adicionais: {report['summary']['total_additional_references']}"
    )
    print(f"   Score de complexidade: {report['summary']['complexity_score']}/100")
    print(f"   Arquivos a atualizar: {len(report['files_needing_updates'])}")
    print(f"   Sada JSON: {JSON_OUTPUT.relative_to(BASE_DIR)}")
    print(f"   Sada Markdown: {MD_OUTPUT.relative_to(BASE_DIR)}")

    # Recomendaes baseadas no score
    print("\n[RECOMMENDATIONS] Recomendaes:")
    score = report["summary"]["complexity_score"]
    if score < 30:
        print("    Renomeao de baixo risco. Pode proceder em lote.")
    elif score < 70:
        print("     Renomeao de risco moderado. Faa em fases.")
        print("   Considere usar ferramentas de refatorao automatizada.")
    else:
        print("    Renomeao de alto risco. Requer planejamento cuidadoso.")
        print("   Execute testes extensivos aps cada renomeao.")
        print("   Considere manter compatibilidade reversa temporria.")


if __name__ == "__main__":
    main()
