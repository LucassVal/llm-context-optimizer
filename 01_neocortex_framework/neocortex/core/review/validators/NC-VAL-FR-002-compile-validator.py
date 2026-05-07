# @UBL @UBL @VAL-FR | LEXICO: #SYSTEM
"""
NC-VAL-FR-002-compile-validator.py
Validador de compilao: verifica se arquivos Python compilam sem erro.

Valida que `metrics.py_compile == "PASS"` e `metrics.ruff_check == "PASS"` no handoff.
Tenta tambm `python -m py_compile` real em cada arquivo listado.
Score 100 se PASS, 0 se FAIL em qualquer arquivo.
"""

import logging
import py_compile
from pathlib import Path

from .. import ValidationResult

logger = logging.getLogger(__name__)


def validate(data: dict) -> ValidationResult:
    """Valida compilao de arquivos Python.

    Args:
        data: Dicionrio do handoff YAML.

    Returns:
        ValidationResult com score 0 ou 100.
    """
    # Verifica mtricas no handoff
    metrics = data.get("metrics", {})
    py_compile_metric = metrics.get("py_compile")
    ruff_check_metric = metrics.get("ruff_check")

    if py_compile_metric != "PASS" or ruff_check_metric != "PASS":
        return ValidationResult(
            validator_name="compile",
            passed=False,
            score=0,
            message=f"Handoff metrics indicam falha: py_compile={py_compile_metric}, ruff_check={ruff_check_metric}",
            details={
                "py_compile_metric": py_compile_metric,
                "ruff_check_metric": ruff_check_metric,
            },
        )

    files = data.get("files_modified", [])
    py_files = [f for f in files if f.endswith(".py")]
    if not py_files:
        return ValidationResult(
            validator_name="compile",
            passed=True,
            score=100,
            message="Nenhum arquivo Python modificado  nada a validar",
            details={"total_py_files": 0, "failed_files": []},
        )

    failed = []
    for file_path in py_files:
        path = Path(file_path)
        if not path.exists():
            failed.append(f"{file_path} (no encontrado)")
            continue
        try:
            py_compile.compile(file_path, doraise=True)
            logger.debug(f"Arquivo {file_path} compila com sucesso")
        except py_compile.PyCompileError as e:
            failed.append(f"{file_path}: {e}")
        except Exception as e:
            failed.append(f"{file_path}: erro inesperado ({e})")

    if failed:
        return ValidationResult(
            validator_name="compile",
            passed=False,
            score=0,
            message=f"{len(failed)}/{len(py_files)} arquivos com erro de compilao",
            details={"total_py_files": len(py_files), "failed_files": failed},
        )

    return ValidationResult(
        validator_name="compile",
        passed=True,
        score=100,
        message=f"Todos os {len(py_files)} arquivos Python compilam",
        details={"total_py_files": len(py_files), "failed_files": []},
    )
