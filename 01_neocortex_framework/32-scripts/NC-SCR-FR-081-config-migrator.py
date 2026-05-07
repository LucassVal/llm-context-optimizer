# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""---
NC-SCR-FR-081-config-migrator.py
---
"""

"""---
NC-SCR-FR-081-config-migrator.py
---
"""

"""
NC-SCR-FR-081-config-migrator.py
Migrador de Configurao por Projeto NeoCortex

Migra a configurao global (neocortex_config.yaml) para configurao por projeto
(.nc/config.yaml) seguindo o padro Claude Code (.claude/).

Funcionalidades:
1. Detecta configurao atual (neocortex_config.yaml)
2. Cria diretrio .nc/ na raiz do projeto
3. Migra configurao para .nc/config.yaml com schema atualizado
4. Opcionalmente atualiza config.py para suportar herana .nc/  global
5. Gera relatrio de migrao

Uso:
    python NC-SCR-FR-081-config-migrator.py --dry-run
    python NC-SCR-FR-081-config-migrator.py --execute
    python NC-SCR-FR-081-config-migrator.py --rollback

Ciclo de vida (Dupla Mordaa):
    Criao  Abertura  Verificao  Execuo  Fechamento
"""

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

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
GLOBAL_CONFIG_PATH = (
    PROJECT_ROOT / "DIR-CFG-FR-001-config-main" / "neocortex_config.yaml"
)
NC_DIR = PROJECT_ROOT / ".nc"
NC_CONFIG_PATH = NC_DIR / "config.yaml"
CONFIG_PY_PATH = PROJECT_ROOT / "neocortex" / "config.py"
BACKUP_DIR = PROJECT_ROOT / ".nc_backup"
SCHEMA_VERSION = "1.0"


# ------------------------------------------------------------------------------
# FUNES DE MIGRAO
# ------------------------------------------------------------------------------
def load_yaml_config(path: Path) -> Dict[str, Any]:
    """Carrega configurao YAML."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Erro ao carregar YAML {path}: {e}")
        return {}


def save_yaml_config(path: Path, config: Dict[str, Any]) -> bool:
    """Salva configurao YAML com formatao preservada."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        logger.info(f"Configurao salva em {path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar YAML {path}: {e}")
        return False


def create_nc_schema(global_config: Dict[str, Any]) -> Dict[str, Any]:
    """Cria schema .nc/config.yaml com metadados e herana."""
    # Extrair metadados da configurao global
    meta = global_config.get("_meta", {})

    # Schema base para .nc/config.yaml
    nc_config = {
        "_schema": {
            "version": SCHEMA_VERSION,
            "generated_at": datetime.now().isoformat(),
            "generated_by": "NC-SCR-FR-081-config-migrator.py",
            "inherits_from": str(GLOBAL_CONFIG_PATH.relative_to(PROJECT_ROOT)),
        },
        "_meta": {
            **meta,
            "domain": "configuration",
            "hash": "auto-generated",
            "layer": "config",
            "tags": ["config", "yaml", "configuration", "per-project"],
            "type": "CFG",
        },
        # Configurao real (copia da global com possveis ajustes)
        **{k: v for k, v in global_config.items() if k != "_meta"},
    }

    # Adicionar seo de plugins vazia para futuro
    if "plugins" not in nc_config:
        nc_config["plugins"] = {
            "enabled": [],
            "disabled": [],
            "auto_discovery": True,
            "plugin_dirs": [".nc/plugins"],
        }

    # Adicionar seo de feature flags
    if "features" not in nc_config:
        nc_config["features"] = {
            "kairos_channels": False,
            "kairos_push_notification": False,
            "session_buddy": True,
            "hookify": True,
            "per_project_config": True,
        }

    return nc_config


def backup_file(path: Path, suffix: str = ".backup") -> Optional[Path]:
    """Cria backup de um arquivo."""
    if not path.exists():
        return None
    backup_path = BACKUP_DIR / f"{path.name}{suffix}"
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
        logger.info(f"Backup criado: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Erro ao criar backup de {path}: {e}")
        return None


def update_config_py_for_nc_support() -> bool:
    """Atualiza config.py para suportar .nc/config.yaml com herana.

    Modifica _load_configuration() para procurar .nc/config.yaml primeiro,
    depois neocortex_config.yaml global.
    """
    if not CONFIG_PY_PATH.exists():
        logger.error(f"config.py no encontrado em {CONFIG_PY_PATH}")
        return False

    try:
        with open(CONFIG_PY_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # Verificar se j tem suporte a .nc/
        if ".nc/config.yaml" in content:
            logger.warning("config.py j tem suporte a .nc/config.yaml")
            return True

        # Encontrar a funo _load_configuration
        lines = content.splitlines()
        new_lines = []
        in_load_config = False
        found_yaml_section = False

        for i, line in enumerate(lines):
            new_lines.append(line)

            # Detectar incio da funo _load_configuration
            if line.strip().startswith(
                "def _load_configuration(self) -> Dict[str, Any]:"
            ):
                in_load_config = True

            # Dentro da funo, aps a docstring, encontrar seo YAML
            if in_load_config and line.strip().startswith(
                'yaml_path = self._project_root / "neocortex_config.yaml"'
            ):
                # Inserir cdigo para .nc/config.yaml antes da configurao global
                indent = " " * 8  # 8 espaos (dentro da funo)
                nc_code = f"""
{indent}# Load from .nc/config.yaml if exists (per-project configuration)
{indent}nc_config_path = self._project_root / ".nc" / "config.yaml"
{indent}if nc_config_path.exists():
{indent}    try:
{indent}        with open(nc_config_path, "r", encoding="utf-8") as f:
{indent}            nc_config = yaml.safe_load(f) or {{}}
{indent}            config.update(nc_config)
{indent}            logger = logging.getLogger(__name__)
{indent}            logger.info(f"Loaded per-project configuration from {{nc_config_path}}")
{indent}    except Exception as e:
{indent}        logger = logging.getLogger(__name__)
{indent}        logger.warning(f"Failed to load .nc/config.yaml: {{e}}")"""

                # Adicionar aps a linha atual
                new_lines.append(nc_code)
                found_yaml_section = True

        if not found_yaml_section:
            logger.error(
                "No foi possvel encontrar a seo YAML em _load_configuration"
            )
            return False

        # Escrever arquivo atualizado
        backup_path = backup_file(CONFIG_PY_PATH, suffix=".pre_nc_migration")
        if backup_path:
            with open(CONFIG_PY_PATH, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines))
            logger.info("config.py atualizado com suporte a .nc/config.yaml")
            logger.info(f"Backup original em {backup_path}")
            return True
        else:
            logger.error("Falha ao criar backup do config.py, abortando atualizao")
            return False

    except Exception as e:
        logger.error(f"Erro ao atualizar config.py: {e}")
        return False


def validate_migration(nc_config: Dict[str, Any]) -> bool:
    """Valida a migrao comparando configuraes."""
    # Carregar configurao global original
    global_config = load_yaml_config(GLOBAL_CONFIG_PATH)

    # Remover metadados e campos adicionados para comparao
    global_clean = {k: v for k, v in global_config.items() if not k.startswith("_")}
    nc_clean = {
        k: v
        for k, v in nc_config.items()
        if not k.startswith("_") and k not in ["plugins", "features"]
    }

    # Comparar sees essenciais
    essential_sections = ["llm", "paths", "cache", "scheduler", "vector_store"]
    issues = []

    for section in essential_sections:
        if section in global_clean and section not in nc_clean:
            issues.append(f"Seo '{section}' no migrada")
        elif section in global_clean and section in nc_clean:
            # Comparao superficial (pode ser expandida)
            pass

    if issues:
        logger.warning(f"Problemas na validao: {issues}")
        return False

    return True


# ------------------------------------------------------------------------------
# FLUXO PRINCIPAL
# ------------------------------------------------------------------------------
def dry_run_migration() -> Dict[str, Any]:
    """Executa migrao em modo dry-run."""
    logger.info("=== MIGRAO DRY-RUN ===")

    # Verificar configurao atual
    if not GLOBAL_CONFIG_PATH.exists():
        logger.error(f"Configurao global no encontrada: {GLOBAL_CONFIG_PATH}")
        return {"success": False, "error": "Global config not found"}

    global_config = load_yaml_config(GLOBAL_CONFIG_PATH)
    logger.info(f"Configurao global carregada ({len(global_config)} sees)")

    # Gerar schema .nc/config.yaml
    nc_config = create_nc_schema(global_config)
    logger.info(f"Schema .nc/config.yaml gerado ({len(nc_config)} sees)")

    # Verificar se .nc/ j existe
    if NC_DIR.exists():
        logger.warning(f"Diretrio .nc/ j existe: {NC_DIR}")

    # Validar migrao
    is_valid = validate_migration(nc_config)

    # Verificar config.py
    config_py_needs_update = True
    if CONFIG_PY_PATH.exists():
        with open(CONFIG_PY_PATH, "r", encoding="utf-8") as f:
            if ".nc/config.yaml" in f.read():
                config_py_needs_update = False
                logger.info("config.py j tem suporte a .nc/config.yaml")

    return {
        "success": True,
        "dry_run": True,
        "global_config_path": str(GLOBAL_CONFIG_PATH),
        "nc_config_path": str(NC_CONFIG_PATH),
        "global_config_sections": list(global_config.keys()),
        "nc_config_sections": list(nc_config.keys()),
        "validation_passed": is_valid,
        "config_py_needs_update": config_py_needs_update,
        "backup_dir": str(BACKUP_DIR),
    }


def execute_migration() -> Dict[str, Any]:
    """Executa migrao real."""
    logger.info("=== EXECUTANDO MIGRAO ===")

    # Criar backup da configurao global
    global_backup = backup_file(GLOBAL_CONFIG_PATH, suffix=".pre_nc_migration")
    if not global_backup and GLOBAL_CONFIG_PATH.exists():
        logger.error("Falha ao criar backup da configurao global")
        return {"success": False, "error": "Backup failed"}

    # Carregar configurao global
    global_config = load_yaml_config(GLOBAL_CONFIG_PATH)
    if not global_config:
        logger.error("Configurao global vazia ou no carregada")
        return {"success": False, "error": "Empty global config"}

    # Criar diretrio .nc/
    NC_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Diretrio .nc/ criado: {NC_DIR}")

    # Gerar e salvar .nc/config.yaml
    nc_config = create_nc_schema(global_config)
    if not save_yaml_config(NC_CONFIG_PATH, nc_config):
        return {"success": False, "error": "Failed to save .nc/config.yaml"}

    # Validar migrao
    if not validate_migration(nc_config):
        logger.warning("Validao da migrao falhou, continuando...")

    # Atualizar config.py para suportar .nc/config.yaml
    config_py_updated = update_config_py_for_nc_support()

    # Gerar relatrio de migrao
    report = {
        "schema_version": SCHEMA_VERSION,
        "migration_timestamp": datetime.now().isoformat(),
        "global_config_backup": str(global_backup) if global_backup else None,
        "nc_config_created": str(NC_CONFIG_PATH),
        "nc_config_sections": list(nc_config.keys()),
        "config_py_updated": config_py_updated,
        "validation_passed": validate_migration(nc_config),
    }

    # Salvar relatrio
    report_path = BACKUP_DIR / "migration_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Relatrio de migrao salvo em: {report_path}")
    logger.info("=== MIGRAO CONCLUDA ===")

    return {
        "success": True,
        "dry_run": False,
        **report,
    }


def rollback_migration() -> Dict[str, Any]:
    """Reverte a migrao restaurando backups."""
    logger.info("=== REVERTENDO MIGRAO ===")

    # Restaurar config.py do backup
    config_py_backup = BACKUP_DIR / "config.py.pre_nc_migration"
    if config_py_backup.exists():
        try:
            shutil.copy2(config_py_backup, CONFIG_PY_PATH)
            logger.info(f"config.py restaurado de {config_py_backup}")
        except Exception as e:
            logger.error(f"Erro ao restaurar config.py: {e}")

    # Remover .nc/config.yaml se existir
    if NC_CONFIG_PATH.exists():
        try:
            NC_CONFIG_PATH.unlink()
            logger.info(f".nc/config.yaml removido: {NC_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"Erro ao remover .nc/config.yaml: {e}")

    # Remover diretrio .nc/ se vazio
    if NC_DIR.exists() and not any(NC_DIR.iterdir()):
        try:
            NC_DIR.rmdir()
            logger.info(f"Diretrio .nc/ removido: {NC_DIR}")
        except Exception as e:
            logger.error(f"Erro ao remover diretrio .nc/: {e}")

    # Restaurar configurao global do backup
    global_backup = BACKUP_DIR / "neocortex_config.yaml.pre_nc_migration"
    if global_backup.exists() and GLOBAL_CONFIG_PATH.exists():
        try:
            shutil.copy2(global_backup, GLOBAL_CONFIG_PATH)
            logger.info(f"Configurao global restaurada de {global_backup}")
        except Exception as e:
            logger.error(f"Erro ao restaurar configurao global: {e}")

    logger.info("=== REVERSO CONCLUDA ===")
    return {"success": True, "rollback": True}


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Migrador de Configurao por Projeto NeoCortex"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa migrao em modo dry-run (sem alteraes)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Executa migrao real",
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Reverte migrao restaurando backups",
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
    action_count = sum([args.dry_run, args.execute, args.rollback])
    if action_count != 1:
        parser.error("Escolha exatamente uma ao: --dry-run, --execute, ou --rollback")

    try:
        if args.dry_run:
            result = dry_run_migration()
        elif args.execute:
            result = execute_migration()
        elif args.rollback:
            result = rollback_migration()
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
