#!/usr/bin/env python3
"""
NeoCortex File Utilities

Funções auxiliares para leitura/escrita de arquivos do framework.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configuração de logging
logger = logging.getLogger(__name__)

# Constantes
# PROJECT_ROOT: raiz do projeto (neocortex_framework)
# file_utils.py está em neocortex_framework/neocortex/core/file_utils.py
# Portanto, parent.parent.parent = neocortex_framework
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Caminhos para arquivos críticos do framework
CORTEX_PATH = (
    PROJECT_ROOT
    / "DIR-CORE-FR-001-core-central"
    / ".agents"
    / "rules"
    / "NC-CTX-FR-001-cortex-central.mdc"
)

LEDGER_PATH = (
    PROJECT_ROOT
    / "DIR-CORE-FR-001-core-central"
    / "NC-LED-FR-001-framework-ledger.json"
)

ARCHIVE_PATH = PROJECT_ROOT / "DIR-ARC-FR-001-archive-main"
BACKUP_PATH = PROJECT_ROOT / "DIR-BAK-FR-001-backup-main"
TEMPLATES_PATH = PROJECT_ROOT / "DIR-TMP-FR-001-templates-main"
DOCS_PATH = PROJECT_ROOT / "DIR-DOC-FR-001-docs-main"
SOURCE_PATH = PROJECT_ROOT / "DIR-SRC-FR-001-source-main"


def read_cortex() -> str:
    """Lê o conteúdo do arquivo cortex."""
    try:
        with open(CORTEX_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def write_cortex(content: str) -> bool:
    """Escreve conteúdo no arquivo cortex."""
    try:
        with open(CORTEX_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Erro ao escrever cortex: {e}")
        return False


def read_ledger() -> Dict[str, Any]:
    """Lê e parseia o ledger JSON."""
    try:
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_ledger(data: Dict[str, Any]) -> bool:
    """Escreve dados no ledger JSON."""
    try:
        with open(LEDGER_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Erro ao escrever ledger: {e}")
        return False


def find_lobes() -> List[str]:
    """Encontra todos os arquivos lobe (.mdc) no diretório de regras."""
    lobes_dir = PROJECT_ROOT / "DIR-CORE-FR-001-core-central" / ".agents" / "rules"
    if not lobes_dir.exists():
        return []

    return [f.name for f in lobes_dir.glob("*.mdc") if f.name != "00-cortex.mdc"]


def get_lobe_content(lobe_name: str) -> Optional[str]:
    """Obtém o conteúdo de um lobe específico."""
    lobe_path = (
        PROJECT_ROOT / "DIR-CORE-FR-001-core-central" / ".agents" / "rules" / lobe_name
    )
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
    return PROJECT_ROOT


def path_exists(relative_path: str) -> bool:
    """Verifica se um caminho relativo ao projeto existe."""
    return (PROJECT_ROOT / relative_path).exists()


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
