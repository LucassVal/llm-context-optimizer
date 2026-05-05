"""---
domain: "core"
layer: "core"
type: "file"
tags: ["val", "003", "locks", "validator"]
hash: "auto-generated"
---"""
"""
NC-VAL-FR-003-locks-validator.py
Validador de locks: verifica que nenhum arquivo modificado est em @LOCKS.

Carrega lista de locks de NC-SEC-FR-001-atomic-locks.yaml.
Score 100 se nenhum lock violado, 0 se qualquer lock modificado.
`metrics.locks_respected` deve ser `true`.
"""

import fnmatch
import logging
from pathlib import Path
from typing import Dict, List

import yaml

from .. import ValidationResult

logger = logging.getLogger(__name__)


def _load_locked_paths() -> List[str]:
    """Carrega lista de paths bloqueados do arquivo atomic-locks.yaml."""
    locks_file = (
        Path(__file__).parent.parent.parent.parent
        / "DIR-DOC-FR-001-docs-main"
        / "NC-SEC-FR-001-atomic-locks.yaml"
    )
    if not locks_file.exists():
        logger.warning(f"Arquivo de locks no encontrado: {locks_file}")
        return []
    try:
        with open(locks_file, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo de locks: {e}")
        return []

    locked_paths = []
    atomic_locks = data.get("atomic_locks", {})
    for _section, config in atomic_locks.items():
        if isinstance(config, dict) and "paths" in config:
            paths = config["paths"]
            if isinstance(paths, list):
                locked_paths.extend(paths)
    return locked_paths


def validate(data: Dict) -> ValidationResult:
    """Valida que `files_modified` NO contm arquivos da lista @LOCKS.

    Args:
        data: Dicionrio do handoff YAML.

    Returns:
        ValidationResult com score 0 ou 100.
    """
    # Verifica mtrica locks_respected
    metrics = data.get("metrics", {})
    locks_respected = metrics.get("locks_respected")
    if locks_respected is not None and not locks_respected:
        return ValidationResult(
            validator_name="locks",
            passed=False,
            score=0,
            message="Handoff indica que locks no foram respeitados (metrics.locks_respected=false)",
            details={"locks_respected": False},
        )

    files = data.get("files_modified", [])
    if not files:
        return ValidationResult(
            validator_name="locks",
            passed=True,
            score=100,
            message="Nenhum arquivo modificado  nada a validar",
            details={"locked_files_found": []},
        )

    locked_paths = _load_locked_paths()
    if not locked_paths:
        logger.warning("Lista de locks vazia  validao ignorada")
        return ValidationResult(
            validator_name="locks",
            passed=True,
            score=100,
            message="Lista de locks vazia  validao ignorada",
            details={"locked_files_found": []},
        )

    locked_found = []
    for file_path in files:
        for pattern in locked_paths:
            # Usar fnmatch para correspondncia de padres glob
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(
                Path(file_path).name, pattern
            ):
                locked_found.append(file_path)
                break

    if locked_found:
        return ValidationResult(
            validator_name="locks",
            passed=False,
            score=0,
            message=f"Arquivos bloqueados (@LOCKS) modificados: {locked_found}",
            details={"locked_files_found": locked_found},
        )

    return ValidationResult(
        validator_name="locks",
        passed=True,
        score=100,
        message="Nenhum arquivo bloqueado (@LOCKS) modificado",
        details={"locked_files_found": []},
    )
