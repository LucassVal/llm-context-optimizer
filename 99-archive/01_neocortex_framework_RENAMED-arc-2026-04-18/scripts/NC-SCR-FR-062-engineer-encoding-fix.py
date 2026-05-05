#!/usr/bin/env python3
"""---
domain: "governance"
layer: "infra"
type: "SCR"
tags: ["engineer", "encoding", "utf8", "windows", "dependencies", "dryrun", "nc-ds-062"]
hash: "auto-generated"
---

NC-SCR-FR-062-engineer-encoding-fix.py
Agente Engineer: Prepara ambiente com encoding UTF-8 para Windows, verifica dependncias e simula renomeao.
Autor: T0 (NeoCortex)
Data: 2026-04-14
Status: Fase 3/3 - Preparao e simulao
"""

import ast
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Configuraes
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "01_neocortex_framework" / "scripts"
DOCS_DIR = PROJECT_ROOT / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main"
RENAMING_PLAN_V2 = DOCS_DIR / "renaming_plan_v2.yaml"
DRY_RUN_LOG = DOCS_DIR / "rename_dryrun.log"
MISSING_DEPS_FILE = DOCS_DIR / "missing_dependencies.txt"
PYTHON_FILES_GLOB = [
    "**/*.py",
    "!**/__pycache__/**",
    "!**/.venv/**",
    "!**/node_modules/**",
]

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bloco de correo de encoding para Windows
ENCODING_FIX_BLOCK = """# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""


def find_python_scripts() -> List[Path]:
    """
    Encontra todos os scripts Python relevantes no projeto.
    """
    scripts = []

    # Scripts principais mencionados
    main_scripts = [
        SCRIPTS_DIR / "NC-SCR-FR-060-courier-saneamento.py",
        SCRIPTS_DIR / "NC-SCR-FR-061-courier-discrepancy-fix.py",
        SCRIPTS_DIR / "NC-SCR-FR-062-tester-vector.py",
        SCRIPTS_DIR / "NC-SCR-FR-063-tester-vector-fix.py",  # ser criado
    ]

    # Adicionar scripts existentes
    for script in main_scripts:
        if script.exists():
            scripts.append(script)

    # Buscar outros scripts Python no diretrio de scripts
    for py_file in SCRIPTS_DIR.rglob("*.py"):
        if py_file not in scripts:
            scripts.append(py_file)

    return scripts


def script_needs_encoding_fix(script_path: Path) -> bool:
    """
    Verifica se o script j possui o bloco de correo de encoding.
    """
    try:
        content = script_path.read_text(encoding="utf-8")

        # Verificar se j tem o bloco de encoding
        if 'sys.platform == "win32"' in content and "io.TextIOWrapper" in content:
            return False

        # Verificar se j tem imports de sys e io
        if "import sys" in content and "import io" in content:
            # Verificar se h configurao de encoding
            if "encoding='utf-8'" in content:
                return False

        return True
    except Exception as e:
        logger.error(f"Erro ao ler {script_path}: {e}")
        return False


def inject_encoding_fix(script_path: Path) -> bool:
    """
    Injeta o bloco de correo de encoding no script, se necessrio.
    Retorna True se modificado, False se j estava correto.
    """
    if not script_needs_encoding_fix(script_path):
        logger.info(f"Script {script_path.name} j tem encoding configurado")
        return False

    try:
        content = script_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Encontrar posio aps imports iniciais
        insert_line = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                insert_line = i + 1
            elif line.strip() and not line.strip().startswith("#"):
                # Parar na primeira linha no-import no-comentrio
                if insert_line == 0:
                    insert_line = i
                break

        # Inserir bloco de encoding
        lines.insert(insert_line, ENCODING_FIX_BLOCK)

        # Garantir que sys est importado
        if "import sys" not in content:
            # Adicionar import sys no incio
            for i, line in enumerate(lines):
                if line.strip().startswith("import "):
                    # Inserir aps este import
                    lines.insert(i + 1, "import sys")
                    break
            else:
                # Se no encontrou imports, adicionar no incio
                lines.insert(0, "import sys")

        # Escrever de volta
        script_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info(f"Encoding fix injetado em {script_path.name}")
        return True

    except Exception as e:
        logger.error(f"Erro ao injetar encoding fix em {script_path}: {e}")
        return False


def analyze_dependencies(script_path: Path) -> Set[str]:
    """
    Analisa os imports de um script Python e retorna dependncias faltantes.
    """
    dependencies = set()

    try:
        content = script_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.add(node.module.split(".")[0])

    except Exception as e:
        logger.warning(f"Erro ao analisar dependncias de {script_path}: {e}")

    return dependencies


def check_missing_dependencies() -> List[str]:
    """
    Verifica dependncias faltantes nos scripts de teste.
    """
    logger.info("Verificando dependncias faltantes")

    # Scripts de teste especficos
    test_scripts = [
        SCRIPTS_DIR / "NC-SCR-FR-062-tester-vector.py",
        PROJECT_ROOT / "01_neocortex_framework" / "tests" / "test_vector_engine.py",
    ]

    all_deps = set()
    for script in test_scripts:
        if script.exists():
            deps = analyze_dependencies(script)
            all_deps.update(deps)

    # Dependncias conhecidas que podem faltar
    potential_missing = {
        "lancedb",
        "pyarrow",
        "pytest_asyncio",
        "pytest",
        "numpy",
        "asyncio",
        "aiohttp",
        "httpx",
        "pydantic",
        "msgpack",
    }

    missing = []
    for dep in potential_missing:
        if dep in all_deps:
            try:
                importlib.import_module(
                    dep.replace("_", "-") if dep == "pytest_asyncio" else dep
                )
            except ImportError:
                missing.append(dep)

    return missing


def simulate_renaming() -> Tuple[List[Dict], List[str]]:
    """
    Simula a renomeao baseada no plano YAML.
    Retorna lista de operaes simuladas e lista de conflitos.
    """
    import yaml

    operations = []
    conflicts = []

    if not RENAMING_PLAN_V2.exists():
        logger.error(f"Plano de renomeao no encontrado: {RENAMING_PLAN_V2}")
        return operations, conflicts

    try:
        with open(RENAMING_PLAN_V2, "r", encoding="utf-8") as f:
            plan_data = yaml.safe_load(f)

        if not plan_data or "renaming_plan" not in plan_data:
            logger.warning("Plano de renomeao vazio ou mal formatado")
            return operations, conflicts

        for entry in plan_data["renaming_plan"]:
            old_path = entry.get("old_path", "")
            new_path = entry.get("new_path", "")

            if not old_path or not new_path:
                continue

            # Converter para Path absoluto
            old_abs = PROJECT_ROOT / old_path
            new_abs = PROJECT_ROOT / new_path

            # Verificar conflitos
            conflict_messages = []

            # 1. Arquivo origem existe?
            if not old_abs.exists():
                conflict_messages.append(f"Arquivo origem no existe: {old_path}")

            # 2. Arquivo destino j existe?
            if new_abs.exists():
                conflict_messages.append(f"Arquivo destino j existe: {new_path}")

            # 3. Diretrio destino existe?
            new_dir = new_abs.parent
            if not new_dir.exists():
                conflict_messages.append(f"Diretrio destino no existe: {new_dir}")

            # Registrar operao
            op = {
                "old_path": old_path,
                "new_path": new_path,
                "conflicts": conflict_messages,
                "simulated": True,
            }
            operations.append(op)

            if conflict_messages:
                conflicts.extend(
                    [f"{old_path} -> {new_path}: {msg}" for msg in conflict_messages]
                )

    except Exception as e:
        logger.error(f"Erro ao simular renomeao: {e}")

    return operations, conflicts


def generate_dryrun_log(operations: List[Dict], conflicts: List[str]) -> None:
    """
    Gera log de simulao (dry run).
    """
    with open(DRY_RUN_LOG, "w", encoding="utf-8") as f:
        f.write("=== SIMULAO DE RENOMEO (DRY RUN) ===\n")
        f.write("Data: 2026-04-14\n")
        f.write(f"Total de operaes: {len(operations)}\n")
        f.write(f"Total de conflitos: {len(conflicts)}\n\n")

        f.write("--- OPERAES SIMULADAS ---\n")
        for i, op in enumerate(operations, 1):
            f.write(f"{i}. {op['old_path']} -> {op['new_path']}\n")
            if op["conflicts"]:
                f.write("   CONFLITOS:\n")
                for conflict in op["conflicts"]:
                    f.write(f"   - {conflict}\n")
            f.write("\n")

        f.write("--- RESUMO DE CONFLITOS ---\n")
        if conflicts:
            for conflict in conflicts:
                f.write(f"- {conflict}\n")
        else:
            f.write("Nenhum conflito detectado.\n")

        f.write("\n--- PRXIMOS PASSOS ---\n")
        f.write("1. Resolver conflitos listados acima\n")
        f.write("2. Executar renomeao real com git mv\n")
        f.write("3. Atualizar imports nos arquivos afetados\n")
        f.write("4. Executar testes de regresso\n")

    logger.info(f"Log de simulao salvo em {DRY_RUN_LOG}")


def main() -> None:
    """
    Fluxo principal do Agente Engineer.
    """
    logger.info("=== INCIO: Agente Engineer - Preparao de Ambiente ===")

    modifications = 0

    # 1. Injeo de encoding UTF-8 em scripts Python
    logger.info("1. Verificando e injetando correo de encoding UTF-8...")
    scripts = find_python_scripts()

    for script in scripts:
        if inject_encoding_fix(script):
            modifications += 1

    logger.info(f"Scripts modificados: {modifications}")

    # 2. Verificao de dependncias faltantes
    logger.info("2. Verificando dependncias faltantes...")
    missing_deps = check_missing_dependencies()

    if missing_deps:
        logger.warning(f"Dependncias faltantes encontradas: {missing_deps}")
        with open(MISSING_DEPS_FILE, "w", encoding="utf-8") as f:
            f.write("# Dependncias faltantes identificadas\n")
            f.write("# Adicione ao requirements.txt ou pyproject.toml\n\n")
            for dep in missing_deps:
                f.write(f"{dep}\n")

        logger.info(f"Lista de dependncias salva em {MISSING_DEPS_FILE}")
    else:
        logger.info("Todas as dependncias esto instaladas.")

    # 3. Simulao de renomeao (dry run)
    logger.info("3. Simulando renomeao (dry run)...")
    operations, conflicts = simulate_renaming()

    logger.info(f"Operaes simuladas: {len(operations)}")
    logger.info(f"Conflitos detectados: {len(conflicts)}")

    # 4. Gerar log de simulao
    generate_dryrun_log(operations, conflicts)

    # 5. Relatrio final
    logger.info("=== RELATRIO FINAL ===")
    logger.info(f"Scripts com encoding corrigido: {modifications}")
    logger.info(f"Dependncias faltantes: {len(missing_deps)}")
    logger.info(f"Conflitos na renomeao: {len(conflicts)}")
    logger.info(f"Log de simulao: {DRY_RUN_LOG}")

    if conflicts:
        logger.warning("CONFLITOS DETECTADOS! Resolver antes da renomeao real.")
        for conflict in conflicts[:5]:  # Mostrar apenas os 5 primeiros
            logger.warning(f"  {conflict}")
        if len(conflicts) > 5:
            logger.warning(f"  ... e mais {len(conflicts) - 5} conflitos")

    # 6. Instrues para prximo agente
    print("\n" + "=" * 60)
    print("INSTRUES PARA PRXIMO AGENTE (Tester):")
    print("=" * 60)
    print("1. Ambiente preparado com encoding UTF-8 para Windows.")
    print(f"2. Dependncias faltantes listadas em: {MISSING_DEPS_FILE}")
    print(f"3. Simulao de renomeao registrada em: {DRY_RUN_LOG}")
    print("4. Conflitos detectados:", len(conflicts))
    print("5. Resolver conflitos ANTES de prosseguir com testes.")
    print("=" * 60)

    logger.info("=== FIM: Agente Engineer concludo ===")


if __name__ == "__main__":
    main()
