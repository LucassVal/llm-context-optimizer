"""
NC-HK-FR-002-example-hook.py
FR-HK-002  Example Hook: Hook de exemplo que valida naming convention R01 no PostToolUse.

Implementa hook_handler(context) -> Dict com validao de naming convention.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def hook_handler(context: Dict[str, Any]) -> Dict[str, Any]:
    """Valida que arquivos criados/modificados seguem a naming convention NC-.

    Espera que o contexto contenha:
        tool: nome da tool (ex.: 'Write', 'Edit', 'MultiEdit')
        params: dicionrio com 'filePath' ou 'filePaths'
        result: resultado da execuo (se PostToolUse)

    Retorna:
        Dict com status, mensagem e lista de violaes.
    """
    tool = context.get("tool", "")
    params = context.get("params", {})

    violations = []

    if tool in ("Write", "Edit", "MultiEdit"):
        file_paths = []
        if "filePath" in params:
            file_paths.append(params["filePath"])
        if "filePaths" in params:
            file_paths.extend(params["filePaths"])
        for file_path in file_paths:
            if not _follows_naming_convention(file_path):
                violations.append(f"Arquivo '{file_path}' no segue padro NC-")

    if tool == "Bash":
        command = params.get("command", "")
        if "mv" in command or "cp" in command or "rename" in command:
            match = re.search(r"(\S+\.\w+)$", command)
            if match:
                file_path = match.group(1)
                if not _follows_naming_convention(file_path):
                    violations.append(
                        f"Arquivo renomeado '{file_path}' no segue padro NC-"
                    )

    if violations:
        logger.warning(f"Violaes de naming convention detectadas: {violations}")
        return {
            "status": "warning",
            "message": "Arquivos no seguem naming convention NC-",
            "violations": violations,
            "valid": False,
        }
    logger.debug("Naming convention vlida.")
    return {
        "status": "ok",
        "message": "Todos os arquivos seguem naming convention NC-",
        "violations": [],
        "valid": True,
    }


def _follows_naming_convention(file_path: str) -> bool:
    """Verifica se o caminho do arquivo segue o padro NC- (R01)."""
    path = Path(file_path)
    name = path.name
    # Verifica se comea com NC- (case-insensitive)
    return name.upper().startswith("NC-")
