#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NC-SCR-FR-075-genealogy-injector.py
Injetor de Tags Genealgicas NeoCortex

Injeta tags genealgicas (topology, parent_ssot, level) nos arquivos Python
baseado no genealogy_graph.json e na estrutura de diretrios.

Funcionalidades:
1. Carrega genealogy_graph.json
2. Mapeia diretrios para topology automaticamente
3. Identifica parent_ssot baseado em referncias no grafo
4. Calcula level baseado na profundidade hierrquica
5. Opes: --dry-run (apenas relatrio), --execute (injeta), --validate (valida tags existentes)

Uso:
    python NC-SCR-FR-075-genealogy-injector.py --dry-run
    python NC-SCR-FR-075-genealogy-injector.py --execute
    python NC-SCR-FR-075-genealogy-injector.py --validate

Ciclo de vida (Dupla Mordaa):
    Criao  Abertura  Verificao  Execuo  Fechamento
"""

import argparse
import ast
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Tentar importar ruamel.yaml (obrigatrio para injeo)
try:
    from ruamel.yaml import YAML
except ImportError:
    YAML = None
    logger = logging.getLogger(__name__)
    logger.warning("ruamel.yaml no instalado. A injeo real no funcionar.")

# Fix encoding for Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# CONSTANTES
# ------------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
GENEALOGY_GRAPH_PATH = PROJECT_ROOT.parent / "genealogy_graph.json"
REPORT_DIR = PROJECT_ROOT.parent / "reports" / "genealogy_injection"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Mapeamento de diretrios para topology (Arquitetura DDD Hierrquica)
DIRECTORY_TO_TOPOLOGY = {
    # Nvel 0: Raiz/Governana
    "neocortex/": "neocortex-root",
    "01_neocortex_framework/": "neocortex-other",
    "DIR-BOOT-FR-001-bootup-main/": "boot",
    "DIR-GOV-FR-001-governance-main/": "governance",
    # Nvel 1: Core e Domnios Centrais
    "neocortex/core/": "core",
    "DIR-CORE-FR-001-core-central/": "core-central",
    "neocortex/infra/": "infra-store",
    "neocortex/services/": "services",
    "neocortex/hooks/": "hooks",
    # Nvel 2: Interfaces e Adaptadores
    "neocortex/mcp/": "mcp",
    "neocortex/agents/": "agents",
    "neocortex/cli/": "cli",
    "neocortex/utils/": "utils",
    # Nvel 3: Configurao e Scripts
    "scripts/": "scripts",
    "DIR-CFG-FR-001-config-main/": "config",
    "DIR-MCP-FR-001-mcp-server/": "mcp-server",
    "DIR-PRF-FR-001-profiles-main/": "profiles",
    "DIR-TMP-FR-001-templates-main/": "templates",
    # Nvel 4: Documentao e Referncia
    "DIR-DOC-FR-001-docs-main/": "docs",
    "DIR-REF-FR-001-reference-main/": "reference",
    # Nvel 5: Testes e Validao
    "DIR-TEST-FR-001-tests-main/": "tests",
    "lobes/": "lobes",
    # Nvel 6: Archive e Backup
    "DIR-ARC-FR-001-archive-main/": "archive",
    "DIR-BAK-FR-001-backup-main/": "backup",
    "DIR-RES-CC-001-claude-leak-workzone/": "claude-leak",
}

# Mapeamento de topology para level (Hierarquia DDD)
TOPOLOGY_TO_LEVEL = {
    # Nvel 0: Raiz/Governana
    "neocortex-root": 0,
    "neocortex-other": 0,
    "boot": 0,
    "governance": 0,
    # Nvel 1: Core e Domnios Centrais
    "core": 1,
    "core-central": 1,
    "infra-store": 1,
    "services": 1,
    "hooks": 1,
    # Nvel 2: Interfaces e Adaptadores
    "mcp": 2,
    "agents": 2,
    "cli": 2,
    "utils": 2,
    # Nvel 3: Configurao e Scripts
    "scripts": 3,
    "config": 3,
    "mcp-server": 3,
    "profiles": 3,
    "templates": 3,
    # Nvel 4: Documentao e Referncia
    "docs": 4,
    "reference": 4,
    # Nvel 5: Testes e Validao
    "tests": 5,
    "lobes": 5,
    # Nvel 6: Archive e Backup
    "archive": 6,
    "backup": 6,
    "claude-leak": 6,
    # Fallbacks (no devem ocorrer com mapeamento completo)
    "framework-artifact": 4,
    "unknown": 7,
}


# ------------------------------------------------------------------------------
# FUNES DE CARREGAMENTO
# ------------------------------------------------------------------------------
def load_genealogy_graph() -> Dict[str, Any]:
    """Carrega genealogy_graph.json."""
    if not GENEALOGY_GRAPH_PATH.exists():
        logger.error(f"Genealogy graph no encontrado: {GENEALOGY_GRAPH_PATH}")
        return {"nodes": [], "edges": []}

    try:
        with open(GENEALOGY_GRAPH_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar genealogy graph: {e}")
        return {"nodes": [], "edges": []}


def get_file_nodes(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Retorna todos os nodes do tipo 'file'."""
    return [node for node in graph.get("nodes", []) if node.get("type") == "file"]


def extract_ssot_references(graph: Dict[str, Any], file_id: str) -> List[str]:
    """Extrai referncias SSOT para um arquivo a partir das edges."""
    ssot_refs = []
    for edge in graph.get("edges", []):
        if edge.get("source") == file_id or edge.get("target") == file_id:
            other_id = (
                edge.get("target")
                if edge.get("source") == file_id
                else edge.get("source")
            )
            # Verifica se  referncia SSOT
            if "ssot:" in other_id:
                ssot_refs.append(other_id.replace("ssot:", ""))
    return ssot_refs


def determine_topology(file_path: Path) -> Tuple[str, int]:
    """Determina topology e level baseado no caminho do arquivo (DDD Hierrquico)."""
    path_str = str(file_path).replace("\\", "/")

    # 1. Verifica mapeamento de diretrios (mais especfico primeiro)
    # Ordena por tamanho do padro para priorizar correspondncias mais especficas
    sorted_patterns = sorted(
        DIRECTORY_TO_TOPOLOGY.items(), key=lambda x: len(x[0]), reverse=True
    )

    for dir_pattern, topology in sorted_patterns:
        if dir_pattern in path_str:
            level = TOPOLOGY_TO_LEVEL.get(topology, 3)
            return topology, level

    # 2. Fallback mnimo (no deve acontecer com mapeamento completo)
    if "DIR-" in path_str:
        return "framework-artifact", 4
    else:
        return "unknown", 7


def generate_frontmatter(
    file_path: Path, topology: str, level: int, ssot_refs: List[str]
) -> Dict[str, Any]:
    """Gera frontmatter YAML para injeo."""
    # Metadados bsicos
    frontmatter = {
        "_genealogy": {
            "injected_at": datetime.now().isoformat(),
            "injected_by": "NC-SCR-FR-075-genealogy-injector.py",
            "version": "1.0",
        },
        "topology": topology,
        "level": level,
    }

    # Adiciona parent_ssot se houver referncias
    if ssot_refs:
        frontmatter["parent_ssot"] = ssot_refs[0]  # Usa o primeiro como principal
        if len(ssot_refs) > 1:
            frontmatter["related_ssot"] = ssot_refs[1:]

    # Adiciona tags baseadas em topology e level
    tags = [topology, f"level-{level}"]
    if "nc-" in file_path.name.lower():
        tags.append("nc-prefix")
    if file_path.suffix == ".py":
        tags.append("python")

    frontmatter["tags"] = tags

    # Adiciona domain e layer para compatibilidade com outros sistemas
    if topology in ["core", "core-central"]:
        frontmatter["domain"] = "framework"
        frontmatter["layer"] = "core"
    elif topology in ["infra-store", "services"]:
        frontmatter["domain"] = "infrastructure"
        frontmatter["layer"] = "services"
    elif topology == "mcp":
        frontmatter["domain"] = "interface"
        frontmatter["layer"] = "mcp"
    elif topology == "scripts":
        frontmatter["domain"] = "orchestration"
        frontmatter["layer"] = "scripts"

    return frontmatter


def read_existing_frontmatter(file_path: Path) -> Optional[Dict[str, Any]]:
    """L frontmatter YAML existente de um arquivo Python."""
    if not file_path.exists() or file_path.suffix != ".py":
        return None

    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Procura por bloco YAML frontmatter
        in_frontmatter = False
        frontmatter_lines = []

        for line in lines:
            if line.strip() == '"""---' or line.strip() == "'''---":
                in_frontmatter = True
                continue
            elif in_frontmatter and (
                line.strip() == '---"""' or line.strip() == "---'''"
            ):
                break
            elif in_frontmatter:
                frontmatter_lines.append(line)

        if frontmatter_lines:
            frontmatter_text = "\n".join(frontmatter_lines)
            return yaml.safe_load(frontmatter_text)
    except Exception as e:
        logger.debug(f"Erro ao ler frontmatter existente de {file_path}: {e}")

    return None


def validate_frontmatter(frontmatter: Dict[str, Any]) -> List[str]:
    """Valida se o frontmatter contm campos obrigatrios."""
    issues = []

    required_fields = ["topology", "level"]
    for field in required_fields:
        if field not in frontmatter:
            issues.append(f"Campo obrigatrio '{field}' ausente")

    # Valida valores
    valid_topologies = set(DIRECTORY_TO_TOPOLOGY.values()) | {
        "unknown",
        "framework-artifact",
    }
    if "topology" in frontmatter and frontmatter["topology"] not in valid_topologies:
        issues.append(f"Topology '{frontmatter['topology']}' no reconhecida")

    if "level" in frontmatter and not isinstance(frontmatter["level"], int):
        issues.append("Level deve ser inteiro")
    elif "level" in frontmatter and (
        frontmatter["level"] < 0 or frontmatter["level"] > 7
    ):
        issues.append("Level deve estar entre 0 e 7")

    return issues


def inject_yaml_frontmatter(file_path: Path, new_frontmatter: dict) -> bool:
    """
    Injeta ou atualiza o bloco YAML Frontmatter no incio de um arquivo Python.
    Usa parser em texto (linhas) mas valida a sintaxe final via AST.
    Modo Non-Destructive (Falha de Parsing Aborta a Escrita).
    Baseado em NC-SCR-FR-020-yaml-injector.py
    """
    if not file_path.exists() or file_path.suffix != ".py":
        return False

    if YAML is None:
        logger.error("ruamel.yaml no instalado. No  possvel injetar frontmatter.")
        return False

    try:
        content = file_path.read_text(encoding="utf-8")
        # Valida que o arquivo original j  vlido.
        ast.parse(content)
    except SyntaxError:
        logger.error(
            f"AST SyntaxError (arquivo original corrompido ou python legado): {file_path.name}"
        )
        return False
    except UnicodeDecodeError:
        logger.error(f"Erro de Encoding em {file_path.name}. No  UTF-8.")
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
        new_lines = lines[:start_idx] + [new_docstring_text] + lines[end_idx + 1 :]
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
        logger.error(
            f"A injeo do YAML quebrou a sintaxe AST de {file_path.name}. Mutao Descartada!"
        )
        return False

    file_path.write_text(final_content, encoding="utf-8")
    return True


# ------------------------------------------------------------------------------
# FLUXO PRINCIPAL
# ------------------------------------------------------------------------------
def dry_run_injection() -> Dict[str, Any]:
    """Executa injeo em modo dry-run, apenas gerando relatrio."""
    logger.info("=== INJEO DRY-RUN (Nenhuma modificao) ===")

    # Carregar genealogy graph
    graph = load_genealogy_graph()
    if not graph.get("nodes"):
        logger.error("Genealogy graph vazio ou no carregado")
        return {"success": False, "error": "Empty graph"}

    file_nodes = get_file_nodes(graph)
    logger.info(f"Encontrados {len(file_nodes)} arquivos no genealogy graph")

    # Processar cada arquivo
    injection_plan = []
    validation_issues = []

    for node in file_nodes:
        file_id = node.get("id", "")
        if not file_id.endswith(".py"):
            continue

        # Construir caminho do arquivo
        file_path = PROJECT_ROOT / file_id
        if not file_path.exists():
            # Tenta encontrar em subdiretrios
            found = False
            for py_file in PROJECT_ROOT.rglob("*.py"):
                if py_file.name == file_id or py_file.name in file_id:
                    file_path = py_file
                    found = True
                    break

            if not found:
                logger.warning(f"Arquivo no encontrado: {file_id}")
                continue

        # Determinar topology e level
        topology, level = determine_topology(file_path)

        # Extrair referncias SSOT
        ssot_refs = extract_ssot_references(graph, file_id)

        # Gerar frontmatter proposto
        proposed_frontmatter = generate_frontmatter(
            file_path, topology, level, ssot_refs
        )

        # Ler frontmatter existente (se houver)
        existing_frontmatter = read_existing_frontmatter(file_path)

        # Validar frontmatter proposto
        issues = validate_frontmatter(proposed_frontmatter)
        if issues:
            validation_issues.append(
                {
                    "file": str(file_path),
                    "issues": issues,
                    "proposed_frontmatter": proposed_frontmatter,
                }
            )

        injection_plan.append(
            {
                "file": str(file_path),
                "file_id": file_id,
                "proposed_topology": topology,
                "proposed_level": level,
                "ssot_references": ssot_refs,
                "proposed_frontmatter": proposed_frontmatter,
                "existing_frontmatter": existing_frontmatter,
                "has_existing_frontmatter": existing_frontmatter is not None,
                "validation_issues": issues,
            }
        )

    # Gerar relatrio
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_files_processed": len(injection_plan),
        "files_with_existing_frontmatter": sum(
            1 for item in injection_plan if item["has_existing_frontmatter"]
        ),
        "validation_issues_count": len(validation_issues),
        "topology_distribution": {},
        "injection_plan": injection_plan,
        "validation_issues": validation_issues,
    }

    # Calcular distribuio de topology
    for item in injection_plan:
        topology = item["proposed_topology"]
        report["topology_distribution"][topology] = (
            report["topology_distribution"].get(topology, 0) + 1
        )

    # Salvar relatrio
    report_path = (
        REPORT_DIR / f"dry_run_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Relatrio dry-run salvo em: {report_path}")
    logger.info(f"Arquivos processados: {len(injection_plan)}")
    logger.info(
        f"Arquivos com frontmatter existente: {report['files_with_existing_frontmatter']}"
    )
    logger.info(f"Problemas de validao: {len(validation_issues)}")
    logger.info(f"Distribuio de topology: {report['topology_distribution']}")

    return {"success": True, "dry_run": True, "report_path": str(report_path), **report}


def execute_injection() -> Dict[str, Any]:
    """Executa injeo real (modifica arquivos)."""
    logger.info("=== EXECUTANDO INJEO DE TAGS GENEALGICAS ===")
    logger.warning("Esta operao MODIFICAR arquivos Python com frontmatter YAML")

    # Primeiro, executar dry-run para planejamento
    dry_run_result = dry_run_injection()
    if not dry_run_result.get("success"):
        return dry_run_result

    injection_plan = dry_run_result.get("injection_plan", [])
    if not injection_plan:
        logger.error("Nenhum arquivo para injetar no plano")
        return {"success": False, "error": "No files to inject"}

    logger.info(f"Processando {len(injection_plan)} arquivos para injeo")

    injected_count = 0
    skipped_count = 0
    failed_count = 0
    validation_errors = []

    for item in injection_plan:
        file_path = Path(item["file"])
        proposed_frontmatter = item["proposed_frontmatter"]
        existing_frontmatter = item["existing_frontmatter"]
        validation_issues = item["validation_issues"]

        if validation_issues:
            validation_errors.append(
                {"file": str(file_path), "issues": validation_issues}
            )
            logger.warning(
                f"Problemas de validao em {file_path.name}: {validation_issues}"
            )
            # ainda pode injetar? vamos pular para segurana
            failed_count += 1
            continue

        # Se j existe frontmatter e  igual ao proposto, pular
        if existing_frontmatter and existing_frontmatter == proposed_frontmatter:
            logger.debug(f"Frontmatter j existe e  igual em {file_path.name}")
            skipped_count += 1
            continue

        # Tentar injetar
        logger.info(f"Injetando frontmatter em {file_path.name}")
        success = inject_yaml_frontmatter(file_path, proposed_frontmatter)
        if success:
            injected_count += 1
        else:
            logger.error(f"Falha ao injetar frontmatter em {file_path.name}")
            failed_count += 1

    logger.info(
        f"Injeo concluda: {injected_count} injetados, {skipped_count} pulados, {failed_count} falhas"
    )

    result = {
        "success": True,
        "injected_count": injected_count,
        "skipped_count": skipped_count,
        "failed_count": failed_count,
        "validation_errors": validation_errors,
        "dry_run_report": dry_run_result.get("report_path"),
    }

    if failed_count > 0:
        result["success"] = False
        result["error"] = f"{failed_count} arquivos falharam na injeo"

    return result


def validate_existing_tags() -> Dict[str, Any]:
    """Valida tags genealgicas existentes nos arquivos."""
    logger.info("=== VALIDANDO TAGS EXISTENTES ===")

    # Carregar genealogy graph
    graph = load_genealogy_graph()
    file_nodes = get_file_nodes(graph)

    validation_results = []

    for node in file_nodes:
        file_id = node.get("id", "")
        if not file_id.endswith(".py"):
            continue

        file_path = PROJECT_ROOT / file_id
        if not file_path.exists():
            continue

        existing_frontmatter = read_existing_frontmatter(file_path)
        if not existing_frontmatter:
            continue

        # Validar campos genealgicos
        issues = validate_frontmatter(existing_frontmatter)

        # Verificar consistncia com diretrio
        expected_topology, expected_level = determine_topology(file_path)
        actual_topology = existing_frontmatter.get("topology")
        actual_level = existing_frontmatter.get("level")

        if actual_topology and actual_topology != expected_topology:
            issues.append(
                f"Topology inconsistente: esperado '{expected_topology}', encontrado '{actual_topology}'"
            )

        if actual_level and actual_level != expected_level:
            issues.append(
                f"Level inconsistente: esperado {expected_level}, encontrado {actual_level}"
            )

        if issues:
            validation_results.append(
                {
                    "file": str(file_path),
                    "existing_frontmatter": existing_frontmatter,
                    "issues": issues,
                    "expected_topology": expected_topology,
                    "expected_level": expected_level,
                }
            )

    report_path = (
        REPORT_DIR
        / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(validation_results, f, indent=2, ensure_ascii=False)

    logger.info(f"Relatrio de validao salvo em: {report_path}")
    logger.info(f"Arquivos com problemas: {len(validation_results)}")

    return {
        "success": True,
        "validation": True,
        "report_path": str(report_path),
        "files_with_issues": len(validation_results),
        "issues": validation_results,
    }


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Injetor de Tags Genealgicas NeoCortex"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa injeo em modo dry-run (sem alteraes)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Executa injeo real (modifica arquivos)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Valida tags genealgicas existentes",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Habilita logging detalhado"
    )

    args = parser.parse_args()

    # Configurar logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Validar argumentos
    action_count = sum([args.dry_run, args.execute, args.validate])
    if action_count != 1:
        parser.error("Escolha exatamente uma ao: --dry-run, --execute, ou --validate")

    try:
        if args.dry_run:
            result = dry_run_injection()
        elif args.execute:
            result = execute_injection()
        elif args.validate:
            result = validate_existing_tags()
        else:
            result = {"success": False, "error": "No action specified"}

        # Output result as JSON
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if not result.get("success", False):
            sys.exit(1)

    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        print(json.dumps({"success": False, "error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
