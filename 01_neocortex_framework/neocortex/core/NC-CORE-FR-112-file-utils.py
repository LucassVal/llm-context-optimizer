# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
#!/usr/bin/env python3
"""
NeoCortex File Utilities

Funes auxiliares para leitura/escrita de arquivos do framework.
"""

import json
import logging
from pathlib import Path
from typing import Any

from ..config import get_config

# Configurao de logging
logger = logging.getLogger(__name__)

# Cache da configurao
_config_instance = None


def _get_config():
    """Retorna a instncia de configurao (singleton)."""
    global _config_instance
    if _config_instance is None:
        _config_instance = get_config()
    return _config_instance


def _project_root() -> Path:
    """Retorna o caminho raiz do projeto conforme configurao."""
    return _get_config().project_root


def _cortex_path() -> Path:
    """Retorna o caminho do arquivo cortex conforme configurao."""
    return _get_config().cortex_path


def _ledger_path() -> Path:
    """Retorna o caminho do arquivo ledger conforme configurao."""
    return _get_config().ledger_path


def _archive_path() -> Path:
    """Retorna o caminho do diretrio de arquivo conforme configurao."""
    return _get_config().archive_path


def _backup_path() -> Path:
    """Retorna o caminho do diretrio de backup conforme configurao."""
    return _get_config().backup_path


def _templates_path() -> Path:
    """Retorna o caminho do diretrio de templates conforme configurao."""
    return _get_config().templates_path


def _docs_path() -> Path:
    """Retorna o caminho do diretrio de docs conforme configurao."""
    return _get_config().docs_path


def _source_path() -> Path:
    """Retorna o caminho do diretrio de source conforme configurao."""
    return _get_config().source_path


# Constantes para compatibilidade com importaes existentes
PROJECT_ROOT = _project_root()
CORTEX_PATH = _cortex_path()
LEDGER_PATH = _ledger_path()
ARCHIVE_PATH = _archive_path()
BACKUP_PATH = _backup_path()
TEMPLATES_PATH = _templates_path()
DOCS_PATH = _docs_path()
SOURCE_PATH = _source_path()


def read_cortex() -> str:
    """L o contedo do arquivo cortex."""
    try:
        with open(_cortex_path(), encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def write_cortex(content: str) -> bool:
    """Escreve contedo no arquivo cortex."""
    try:
        with open(_cortex_path(), "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Erro ao escrever cortex: {e}")
        return False


def read_ledger() -> dict[str, Any]:
    """L e parseia o ledger JSON."""
    try:
        with open(_ledger_path(), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_ledger(data: dict[str, Any]) -> bool:
    """Escreve dados no ledger JSON."""
    try:
        with open(_ledger_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Erro ao escrever ledger: {e}")
        return False


def find_lobes() -> list[str]:
    """Encontra todos os arquivos lobe (.mdc) no diretrio de regras."""
    lobes_dir = _get_config().core_central / ".agents" / "rules"
    if not lobes_dir.exists():
        return []

    return [f.name for f in lobes_dir.glob("*.mdc") if f.name != "00-cortex.mdc"]


def get_lobe_content(lobe_name: str) -> str | None:
    """Obtm o contedo de um lobe especfico."""
    lobe_path = _get_config().core_central / ".agents" / "rules" / lobe_name
    if not lobe_path.exists():
        return None

    try:
        with open(lobe_path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


# Funes adicionais teis
def get_project_root() -> Path:
    """Retorna o caminho raiz do projeto."""
    return _project_root()


def get_lobes_path() -> Path:
    """Retorna o caminho dinamico de memory_lobes configurado na arquitetura cortical."""
    return _get_config().memory_lobes


def path_exists(relative_path: str) -> bool:
    """Verifica se um caminho relativo ao projeto existe."""
    return (_project_root() / relative_path).exists()


def read_json_file(filepath: Path) -> dict[str, Any]:
    """L um arquivo JSON genrico."""
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_json_file(filepath: Path, data: dict[str, Any]) -> bool:
    """Escreve dados em um arquivo JSON."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Erro ao escrever JSON em {filepath}: {e}")
        return False
