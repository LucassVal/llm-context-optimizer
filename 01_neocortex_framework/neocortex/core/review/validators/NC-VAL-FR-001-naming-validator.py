"""---
@Module  mcp _genealogy:   injected_at: '2026-04-16T00:23:58.44
---
"""


"""
NC-VAL-FR-001-naming-validator.py
Validador de naming: verifica se arquivos seguem padro NC-TIPO-SIGLA-NUM.

Score 100 se todos OK, penalidade de 20 por arquivo fora do padro.
"""

import logging
import re
from pathlib import Path

from .. import ValidationResult

logger = logging.getLogger(__name__)

# Padro de naming NeoCortex (NC-TIPO-SIGLA-NUM-desc.ext)
PATTERN = re.compile(r"^NC-[A-Z]+-[A-Z]+-\d{3}")


def validate(data: dict) -> ValidationResult:
    """Valida que `files_modified` seguem padro `NC-TIPO-SIGLA-NUM-desc.ext`.

    Args:
        data: Dicionrio do handoff YAML.

    Returns:
        ValidationResult com score 0-100.
    """
    files = data.get("files_modified", [])
    if not files:
        return ValidationResult(
            validator_name="naming",
            passed=True,
            score=100,
            message="Nenhum arquivo modificado  nada a validar",
            details={"total_files": 0, "invalid_files": []},
        )

    invalid = []
    for file_path in files:
        file_name = Path(file_path).name
        if not PATTERN.match(file_name):
            invalid.append(file_path)

    total = len(files)
    invalid_count = len(invalid)
    score = max(0, 100 - 20 * invalid_count)
    passed = score == 100

    if passed:
        message = f"Todos os {total} arquivos seguem o padro de naming"
    else:
        message = f"{invalid_count}/{total} arquivos no seguem o padro: {invalid}"

    return ValidationResult(
        validator_name="naming",
        passed=passed,
        score=score,
        message=message,
        details={
            "total_files": total,
            "invalid_files": invalid,
            "pattern": PATTERN.pattern,
        },
    )
