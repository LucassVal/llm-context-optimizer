#!/usr/bin/env python3
"""
NeoCortex File Utilities

Funções auxiliares para leitura/escrita de arquivos do framework.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..config import get_config

# Configuração de logging
logger = logging.getLogger(__name__)

# Cache da configuração
_config_instance = None


def _get_config():
    """Retorna a instância de configuração (singleton)."""
    global _config_instance
    if _config_instance is None:
        _config_instance = get_config()
    return _config_instance


def _project_root() -> Path:
    """Retorna o caminho raiz do projeto conforme configuração."""
    return _get_config().project_root


def _cortex_path() -> Path:
    """Retorna o caminho do arquivo cortex conforme configuração."""
    return _get_config().cortex_path


def _ledger_path() -> Path:
    """Retorna o caminho do arquivo ledger conforme configuração."""
    return _get_config().ledger_path


def _archive_path() -> Path:
    """Retorna o caminho do diretório de arquivo conforme configuração."""
    return _get_config().archive_path


def _backup_path() -> Path:
    """Retorna o caminho do diretório de backup conforme configuração."""
    return _get_config().backup_path


def _templates_path() -> Path:
    """Retorna o caminho do diretório de templates conforme configuração."""
    return _get_config().templates_path


def _docs_path() -> Path:
    """Retorna o caminho do diretório de docs conforme configuração."""
    return _get_config().docs_path


def _source_path() -> Path:
    """Retorna o caminho do diretório de source conforme configuração."""
    return _get_config().source_path


# Constantes para compatibilidade com importações existentes
PROJECT_ROOT = _project_root()
CORTEX_PATH = _cortex_path()
LEDGER_PATH = _ledger_path()
ARCHIVE_PATH = _archive_path()
BACKUP_PATH = _backup_path()
TEMPLATES_PATH = _templates_path()
DOCS_PATH = _docs_path()
SOURCE_PATH = _source_path()


def read_cortex() -> str:
    """Lê o conteúdo do arquivo cortex."""
    try:
        with open(_cortex_path(), "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def write_cortex(content: str) -> bool:
    """Escreve conteúdo no arquivo cortex."""
    try:
        with open(_cortex_path(), "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Erro ao escrever cortex: {e}")
        return False


def read_ledger() -> Dict[str, Any]:
    """Lê e parseia o ledger JSON."""
    try:
        with open(_ledger_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_ledger(data: Dict[str, Any]) -> bool:
    """Escreve dados no ledger JSON."""
    try:
        with open(_ledger_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Erro ao escrever ledger: {e}")
        return False


def find_lobes() -> List[str]:
    """Encontra todos os arquivos lobe (.mdc) no diretório de regras."""
    lobes_dir = _get_config().core_central / ".agents" / "rules"
    if not lobes_dir.exists():
        return []

    return [f.name for f in lobes_dir.glob("*.mdc") if f.name != "00-cortex.mdc"]


def get_lobe_content(lobe_name: str) -> Optional[str]:
    """Obtém o conteúdo de um lobe específico."""
    lobe_path = _get_config().core_central / ".agents" / "rules" / lobe_name
    if not lobe_path.exists():
        return None

    try:
        with open(lobe_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


# Funções adicionais úteis
def get_project_root() -> Path:
    """Retorna o caminho raiz do projeto."""
    return _project_root()


def path_exists(relative_path: str) -> bool:
    """Verifica se um caminho relativo ao projeto existe."""
    return (_project_root() / relative_path).exists()


def read_json_file(filepath: Path) -> Dict[str, Any]:
    """Lê um arquivo JSON genérico."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_json_file(filepath: Path, data: Dict[str, Any]) -> bool:
    """Escreve dados em um arquivo JSON."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Erro ao escrever JSON em {filepath}: {e}")
        return False
