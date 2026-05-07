# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3


"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.724225'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-NAM-FR-001
related_ssot:
  - NC-SCR-FR-060-courier-saneamento
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

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
tags: ["courier", "saneamento", "renaming", "legacy", "nc-ds-060"]
hash: "auto-generated"
---

NC-SCR-FR-060-courier-saneamento.py
Agente Courier: Prepara plano de saneamento para renomeao de arquivos legados.
Autor: T0 (NeoCortex)
Data: 2026-04-14
Status: Fase 1/3 - Extrao e anlise inicial
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
PROGRESS_FILE = DOCS_DIR / "courier_progress.json"
LEGACY_FILES_LIST = DOCS_DIR / "legacy_files_complete.txt"

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

# Contadores sequenciais por tipo (sero incrementados conforme necessidade)
type_counters = dict.fromkeys(TYPE_MAPPING.values(), 1)


def extract_legacy_files() -> List[str]:
    r"""
    Extrai todos os caminhos de arquivos legados do relatrio de auditoria.
    Retorna lista de caminhos no formato 'neocortex\...'
    """
    logger.info(f"Extraindo arquivos legados de {AUDIT_REPORT}")

    if not AUDIT_REPORT.exists():
        logger.error(f"Arquivo de auditoria no encontrado: {AUDIT_REPORT}")
        return []

    content = AUDIT_REPORT.read_text(encoding="utf-8")

    # Padro para capturar caminhos entre crases (inclui Erro de Diretrio e Legado Vigiado)
    pattern = r"`(neocortex\\.+?)`"
    matches = re.findall(pattern, content)

    # Remover duplicatas e ordenar
    unique_matches = sorted(set(matches))

    logger.info(f"Extrados {len(unique_matches)} arquivos nicos")

    # Salvar lista completa
    LEGACY_FILES_LIST.write_text("\n".join(unique_matches), encoding="utf-8")
    logger.info(f"Lista salva em {LEGACY_FILES_LIST}")

    return unique_matches


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


def propose_canonical_name(file_path: str) -> str:
    """
    Propor novo nome cannico para um arquivo legado.
    Formato: NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext
    """
    # Analisar tipo e descrio
    canonical_type, sigla, desc = analyze_file_type(file_path)

    # Incrementar contador para este tipo
    global type_counters
    if canonical_type not in type_counters:
        type_counters[canonical_type] = 1

    num = f"{type_counters[canonical_type]:03d}"
    type_counters[canonical_type] += 1

    # Extrair extenso
    ext = Path(file_path).suffix

    # Construir novo nome
    new_name = f"NC-{canonical_type}-{sigla}-{num}-{desc}{ext}"

    logger.debug(f"Proposto: {file_path} -> {new_name}")
    return new_name


def find_import_dependencies(file_path: str) -> List[str]:
    """
    Encontra todos os arquivos que importam o arquivo especificado.
    Usa grep simples para buscar importaes.
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
                f"import.*{module_name.replace('_', '')}",
                f"from.*{module_name.replace('_', '')}.*import",
            ]

            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    rel_path = py_file.relative_to(PROJECT_ROOT)
                    dependencies.append(str(rel_path).replace("\\", "/"))
                    break

        except Exception as e:
            logger.warning(f"Erro ao ler {py_file}: {e}")

    return sorted(set(dependencies))


def generate_renaming_plan(legacy_files: List[str]) -> Dict:
    """
    Gera plano de renomeao no formato YAML especificado.
    """
    plan = []

    logger.info(f"Gerando plano de renomeao para {len(legacy_files)} arquivos")

    for i, old_path in enumerate(legacy_files, 1):
        logger.info(f"Processando {i}/{len(legacy_files)}: {old_path}")

        # Propor novo nome
        new_name = propose_canonical_name(old_path)

        # Construir novo caminho (mesmo diretrio, novo nome)
        old_dir = str(Path(old_path).parent).replace("\\", "/")
        new_path = f"{old_dir}/{new_name}"

        # Encontrar dependncias
        imports_affected = find_import_dependencies(old_path)

        # Adicionar entrada ao plano
        entry = {
            "old_path": old_path.replace("\\", "/"),
            "new_path": new_path,
            "imports_affected": imports_affected,
        }

        plan.append(entry)

    # Estrutura final do plano
    plan_dict = {
        "metadata": {
            "generated": "2026-04-14",
            "total_files": len(legacy_files),
            "status": "PENDING_REVIEW",
        },
        "renaming_plan": plan,
    }

    return plan_dict


def save_progress(legacy_files: List[str], processed_count: int) -> None:
    """
    Salva progresso atual para permitir continuao por outro agente.
    """
    progress = {
        "total_files": len(legacy_files),
        "processed_files": processed_count,
        "legacy_files": legacy_files,
        "type_counters": type_counters,
        "timestamp": "2026-04-14",
    }

    PROGRESS_FILE.write_text(json.dumps(progress, indent=2), encoding="utf-8")
    logger.info(f"Progresso salvo em {PROGRESS_FILE}")


def main() -> None:
    """
    Fluxo principal do Agente Courier.
    """
    logger.info("=== INCIO: Agente Courier - Plano de Saneamento ===")

    # 1. Extrair arquivos legados
    legacy_files = extract_legacy_files()

    if not legacy_files:
        logger.error("Nenhum arquivo legado extrado. Abortando.")
        return

    logger.info(f"Total de arquivos legados identificados: {len(legacy_files)}")

    # 2. Verificar discrepncia com relatrio
    if len(legacy_files) != 178:
        logger.warning(
            f"Discrepncia: relatrio cita 178 arquivos, extrados {len(legacy_files)}"
        )
        logger.warning(
            "Alguns arquivos podem no ter sido capturados pelo padro regex."
        )

    # 3. Gerar plano de renomeao
    plan_dict = generate_renaming_plan(legacy_files)

    # 4. Salvar plano YAML
    with open(RENAMING_PLAN, "w", encoding="utf-8") as f:
        yaml.dump(plan_dict, f, default_flow_style=False, allow_unicode=True)

    logger.info(f"Plano de renomeao salvo em {RENAMING_PLAN}")

    # 5. Salvar progresso
    save_progress(legacy_files, len(legacy_files))

    # 6. Relatrio final
    logger.info("=== RELATRIO FINAL ===")
    logger.info(f"Arquivos processados: {len(legacy_files)}")
    logger.info(f"Plano gerado: {RENAMING_PLAN}")
    logger.info(f"Progresso salvo: {PROGRESS_FILE}")
    logger.info("=== FIM: Agente Courier concludo ===")

    # 7. Instrues para prximo agente
    print("\n" + "=" * 60)
    print("INSTRUES PARA PRXIMO AGENTE (Engineer/Tester):")
    print("=" * 60)
    print("1. Revisar o plano de renomeao em:")
    print(f"   {RENAMING_PLAN}")
    print("2. Validar as dependncias de importao listadas.")
    print("3. Executar a renomeao apenas aps aprovao do T0.")
    print("4. Atualizar imports nos arquivos afetados.")
    print("5. Executar testes de regresso aps renomeao.")
    print("=" * 60)


if __name__ == "__main__":
    main()
