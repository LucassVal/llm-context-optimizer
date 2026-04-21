#!/usr/bin/env python3
import io
import sys

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
domain: "governance"
layer: "infra"
type: "SCR"
tags: ["courier", "discrepancy", "validation", "renaming", "nc-ds-061"]
hash: "auto-generated"
---

NC-SCR-FR-061-courier-discrepancy-fix.py
Agente Courier: Corrige discrepncia de escopo (87 vs 178 arquivos) e gera plano de renomeao completo.
Autor: T0 (NeoCortex)
Data: 2026-04-14
Status: Fase 2/3 - Validao cruzada e atualizao do plano
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

# Configuraes
PROJECT_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main"
AUDIT_REPORT = DOCS_DIR / "structural_audit_report.md"
RENAMING_PLAN = DOCS_DIR / "renaming_plan.yaml"
DISCREPANCY_REPORT = DOCS_DIR / "discrepancy_report.json"
RENAMING_PLAN_V2 = DOCS_DIR / "renaming_plan_v2.yaml"

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Mapeamento de tipos baseado em NC-NAM-FR-001
TYPE_MAPPING = {
    "core": "CORE",
    "infra": "INFRA",
    "mcp/tools": "TOOL",
    "agent": "AGENT",
    "cli": "CLI",
    "repositories": "REPO",
    "schemas": "SCHEMA",
    "config": "CFG",
    "services": "SVC",
    "utils": "UTL",
    "hooks": "HK",
    "adapters": "ADP",
    "review": "REV",
}


def extract_legacy_files_robust() -> List[str]:
    """
    Extrai TODAS as menes a arquivos em quarentena do relatrio de auditoria.
    Captura qualquer formato: listas com '-', blocos de cdigo, caminhos entre crases, tabelas markdown.
    """
    logger.info(f"Extraindo arquivos legados de forma robusta de {AUDIT_REPORT}")

    if not AUDIT_REPORT.exists():
        logger.error(f"Arquivo de auditoria no encontrado: {AUDIT_REPORT}")
        return []

    content = AUDIT_REPORT.read_text(encoding="utf-8")
    lines = content.split("\n")

    extracted_files = []

    # Padres para capturar caminhos de arquivo
    patterns = [
        r"`(neocortex\\.+?)`",  # Caminhos entre crases
        r"\(neocortex\\.+?\)",  # Caminhos entre parnteses
        r"neocortex\\[a-zA-Z0-9_\\\-\.]+\.py",  # Caminhos diretos (com .py)
        r"neocortex\\[a-zA-Z0-9_\\\-\.]+\.md",  # Caminhos diretos (com .md)
        r"neocortex\\[a-zA-Z0-9_\\\-\.]+\.yaml",  # Caminhos diretos (com .yaml)
        r"neocortex\\[a-zA-Z0-9_\\\-\.]+\.yml",  # Caminhos diretos (com .yml)
        r"neocortex\\[a-zA-Z0-9_\\\-\.]+\.json",  # Caminhos diretos (com .json)
    ]

    for line_num, line in enumerate(lines, 1):
        for pattern in patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                # Se o padro tem grupos, pegar o primeiro grupo
                if isinstance(match, tuple) and len(match) > 0:
                    file_path = match[0]
                else:
                    file_path = match

                # Normalizar separadores (garantir que file_path  string)
                if isinstance(file_path, str):
                    file_path = file_path.replace("/", "\\")
                else:
                    file_path = str(file_path)
                extracted_files.append((file_path, line_num))

    # Tambm procurar por listas com '- neocortex\...'
    list_pattern = r"^\s*-\s+(neocortex\\.+?\.\w+)"
    for line_num, line in enumerate(lines, 1):
        match = re.search(list_pattern, line)
        if match:
            file_path = match.group(1).replace("/", "\\")
            extracted_files.append((file_path, line_num))

    # Remover duplicatas mantendo a primeira ocorrncia
    unique_files = []
    seen = set()
    for file_path, _line_num in extracted_files:
        if file_path not in seen:
            seen.add(file_path)
            unique_files.append(file_path)

    logger.info(
        f"Extrados {len(unique_files)} arquivos nicos (com validao robusta)"
    )

    # Salvar para auditoria
    audit_log = []
    for file_path, line_num in extracted_files:
        audit_log.append({"file": file_path, "line": line_num})

    with open(DOCS_DIR / "extraction_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit_log, f, indent=2)

    return sorted(unique_files)


def load_current_plan() -> Tuple[List[str], Dict]:
    """
    Carrega o plano atual de renomeao e retorna lista de arquivos no plano.
    """
    if not RENAMING_PLAN.exists():
        logger.warning(f"Plano de renomeao no encontrado: {RENAMING_PLAN}")
        return [], {}

    with open(RENAMING_PLAN, "r", encoding="utf-8") as f:
        plan_data = yaml.safe_load(f)

    if not plan_data or "renaming_plan" not in plan_data:
        logger.warning("Plano de renomeao vazio ou mal formatado")
        return [], {}

    current_files = []
    for entry in plan_data["renaming_plan"]:
        if "old_path" in entry:
            current_files.append(entry["old_path"])

    return current_files, plan_data


def cross_validate(extracted_files: List[str], current_files: List[str]) -> Dict:
    """
    Validao cruzada entre arquivos extrados e arquivos no plano atual.
    Retorna relatrio de discrepncia.
    """
    extracted_set = set(extracted_files)
    current_set = set(current_files)

    discrepancy_report = {
        "metadata": {
            "generated": "2026-04-14",
            "extracted_count": len(extracted_files),
            "current_count": len(current_files),
        },
        "missing_files": sorted(extracted_set - current_set),
        "extra_files": sorted(current_set - extracted_set),
        "common_files": sorted(extracted_set & current_set),
        "summary": {
            "missing_count": len(extracted_set - current_set),
            "extra_count": len(current_set - extracted_set),
            "common_count": len(extracted_set & current_set),
        },
    }

    return discrepancy_report


def analyze_file_type(file_path: str) -> Tuple[str, str, str]:
    """
    Analisa o caminho do arquivo e retorna (tipo_canonico, sigla, descricao)
    baseado nas regras do NC-NAM-FR-001.
    """
    # Normalizar caminho
    normalized = file_path.replace("\\", "/")

    # Extrair partes do caminho
    parts = normalized.split("/")

    # Determinar tipo baseado na estrutura de diretrios
    if len(parts) >= 2:
        dir_level = parts[1]  # neocortex/[dir_level]

        # Mapear diretrio para tipo cannico
        canonical_type = TYPE_MAPPING.get(dir_level, "CORE")

        # Para subdiretrios especficos
        if dir_level == "mcp" and len(parts) >= 3 and parts[2] == "tools":
            canonical_type = "TOOL"
        elif dir_level == "core":
            canonical_type = "CORE"
        elif dir_level == "infra":
            canonical_type = "INFRA"

        # Extrair nome do arquivo sem extenso
        filename = parts[-1]
        basename = Path(filename).stem

        # Gerar descrio kebab-case
        desc = basename.lower().replace("_", "-").replace(".", "-")

        # Determinar sigla (FR para framework, WL para white-label, etc.)
        sigla = "FR"  # Padro para framework

        return canonical_type, sigla, desc

    return "CORE", "FR", "unknown"


def propose_canonical_name(file_path: str, existing_plan: Dict) -> str:
    """
    Propor novo nome cannico para um arquivo legado.
    Verifica se j existe no plano atual para manter consistncia.
    """
    # Primeiro, verificar se este arquivo j est no plano atual
    if "renaming_plan" in existing_plan:
        for entry in existing_plan["renaming_plan"]:
            if entry.get("old_path") == file_path.replace("\\", "/"):
                new_path = entry.get("new_path", "")
                if new_path:
                    return Path(new_path).name

    # Se no encontrado, gerar novo nome
    canonical_type, sigla, desc = analyze_file_type(file_path)

    # Determinar nmero sequencial (buscar mximo existente)
    max_num = 0
    if "renaming_plan" in existing_plan:
        for entry in existing_plan["renaming_plan"]:
            new_path = entry.get("new_path", "")
            if new_path:
                match = re.search(
                    r"NC-" + canonical_type + r"-" + sigla + r"-(\d{3})", new_path
                )
                if match:
                    num = int(match.group(1))
                    if num > max_num:
                        max_num = num

    # Incrementar para novo arquivo
    num = max_num + 1

    # Extrair extenso
    ext = Path(file_path).suffix

    # Construir novo nome
    new_name = f"NC-{canonical_type}-{sigla}-{num:03d}-{desc}{ext}"

    logger.debug(f"Proposto: {file_path} -> {new_name}")
    return new_name


def find_import_dependencies(file_path: str) -> List[str]:
    """
    Encontra todos os arquivos que importam o arquivo especificado.
    """
    dependencies = []
    normalized_path = file_path.replace("\\", "/")

    # Extrair nome do mdulo (sem extenso .py)
    module_name = Path(normalized_path).stem

    # Buscar em todos os arquivos Python do projeto
    python_files = list(PROJECT_ROOT.rglob("*.py"))

    for py_file in python_files:
        try:
            content = py_file.read_text(encoding="utf-8")

            # Padres de importao
            patterns = [
                f"import.*{module_name}",
                f"from.*{module_name}.*import",
            ]

            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    rel_path = py_file.relative_to(PROJECT_ROOT)
                    dependencies.append(str(rel_path).replace("\\", "/"))
                    break

        except Exception as e:
            logger.warning(f"Erro ao ler {py_file}: {e}")

    return sorted(set(dependencies))


def update_renaming_plan(
    extracted_files: List[str], current_plan: Dict, discrepancy_report: Dict
) -> Dict:
    """
    Atualiza o plano de renomeao com os arquivos faltantes.
    """
    logger.info("Atualizando plano de renomeao com arquivos faltantes")

    # Inicializar novo plano
    new_plan = current_plan.copy()
    if "renaming_plan" not in new_plan:
        new_plan["renaming_plan"] = []

    # Mapear arquivos existentes no plano
    existing_files = {}
    for entry in new_plan["renaming_plan"]:
        if "old_path" in entry:
            existing_files[entry["old_path"]] = entry

    # Adicionar arquivos faltantes
    missing_files = discrepancy_report.get("missing_files", [])
    for file_path in missing_files:
        if file_path not in existing_files:
            # Propor novo nome
            new_name = propose_canonical_name(file_path, current_plan)

            # Construir novo caminho
            old_dir = str(Path(file_path).parent).replace("\\", "/")
            new_path = f"{old_dir}/{new_name}"

            # Encontrar dependncias
            imports_affected = find_import_dependencies(file_path)

            # Adicionar entrada ao plano
            entry = {
                "old_path": file_path.replace("\\", "/"),
                "new_path": new_path,
                "imports_affected": imports_affected,
            }

            new_plan["renaming_plan"].append(entry)
            existing_files[file_path] = entry

    # Atualizar metadados
    if "metadata" not in new_plan:
        new_plan["metadata"] = {}

    new_plan["metadata"]["total_files"] = len(new_plan["renaming_plan"])
    new_plan["metadata"]["status"] = "UPDATED"
    new_plan["metadata"]["updated"] = "2026-04-14"
    new_plan["metadata"]["discrepancy_fixed"] = True

    return new_plan


def main() -> None:
    """
    Fluxo principal do Agente Courier para correo de discrepncia.
    """
    logger.info("=== INCIO: Agente Courier - Correo de Discrepncia ===")

    # 1. Extrao robusta de arquivos
    extracted_files = extract_legacy_files_robust()

    if not extracted_files:
        logger.error("Nenhum arquivo legado extrado. Abortando.")
        return

    logger.info(f"Arquivos extrados (robusto): {len(extracted_files)}")

    # 2. Carregar plano atual
    current_files, current_plan = load_current_plan()
    logger.info(f"Arquivos no plano atual: {len(current_files)}")

    # 3. Validao cruzada
    discrepancy_report = cross_validate(extracted_files, current_files)

    # 4. Salvar relatrio de discrepncia
    with open(DISCREPANCY_REPORT, "w", encoding="utf-8") as f:
        json.dump(discrepancy_report, f, indent=2)

    logger.info(f"Relatrio de discrepncia salvo em {DISCREPANCY_REPORT}")

    # 5. Exibir resumo
    summary = discrepancy_report["summary"]
    logger.info(
        f"Resumo: {summary['missing_count']} faltantes, {summary['extra_count']} extras, {summary['common_count']} comuns"
    )

    # 6. Atualizar plano se necessrio
    if summary["missing_count"] > 0:
        logger.info(
            f"Adicionando {summary['missing_count']} arquivos faltantes ao plano"
        )
        updated_plan = update_renaming_plan(
            extracted_files, current_plan, discrepancy_report
        )

        # Salvar plano atualizado
        with open(RENAMING_PLAN_V2, "w", encoding="utf-8") as f:
            yaml.dump(updated_plan, f, default_flow_style=False, allow_unicode=True)

        logger.info(f"Plano atualizado salvo em {RENAMING_PLAN_V2}")

        # Comparao
        old_count = len(current_files)
        new_count = len(updated_plan["renaming_plan"])
        logger.info(f"Plano expandido: {old_count} -> {new_count} arquivos")
    else:
        logger.info("Nenhum arquivo faltante encontrado. Plano j est completo.")
        # Copiar plano atual para v2
        with open(RENAMING_PLAN_V2, "w", encoding="utf-8") as f:
            yaml.dump(current_plan, f, default_flow_style=False, allow_unicode=True)

    # 7. Instrues para prximo agente
    print("\n" + "=" * 60)
    print("INSTRUES PARA PRXIMO AGENTE (Engineer):")
    print("=" * 60)
    print("1. Plano de renomeao completo gerado em:")
    print(f"   {RENAMING_PLAN_V2}")
    print(f"2. Relatrio de discrepncia em: {DISCREPANCY_REPORT}")
    print("3. Arquivos faltantes adicionados:", summary["missing_count"])
    print("4. Arquivos extras identificados:", summary["extra_count"])
    print("5. Validar imports antes de executar renomeao.")
    print("=" * 60)

    logger.info("=== FIM: Agente Courier - Correo de Discrepncia concluda ===")


if __name__ == "__main__":
    main()
