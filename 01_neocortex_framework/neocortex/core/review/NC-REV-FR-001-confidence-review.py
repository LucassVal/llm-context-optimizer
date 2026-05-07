# @UBL @UBL @REV-FR | LEXICO: #SYSTEM
"""
NC-REV-FR-001-confidence-review.py
FR-REV-001  ConfidenceReviewService: Validador de handoffs com score 0-100.

Agrega mltiplos validadores e retorna score de confiana.
Score >= 80: APPROVED | Score 50-79: NEEDS_REVIEW | Score < 50: REJECTED
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ReviewVerdict(StrEnum):
    APPROVED = "APPROVED"  # score >= 80
    NEEDS_REVIEW = "NEEDS_REVIEW"  # 50-79
    REJECTED = "REJECTED"  # < 50


@dataclass
class ValidationResult:
    validator_name: str
    passed: bool
    score: int  # 0-100
    message: str
    details: dict = field(default_factory=dict)


@dataclass
class ReviewReport:
    ticket_id: str
    final_score: int  # mdia ponderada
    verdict: ReviewVerdict
    validations: list[ValidationResult] = field(default_factory=list)
    timestamp: str = ""


class ConfidenceReviewService:
    """Valida handoffs com score 0-100 agregando mltiplos validadores.

    Interface pblica:
      review(handoff_path: Path) -> ReviewReport
      review_dict(data: Dict) -> ReviewReport
      add_validator(name, validator_func, weight) -> None
    """

    def __init__(self):
        self.validators: dict[str, dict[str, Any]] = {}  # name -> {func, weight}

    def review(self, handoff_path: Path) -> ReviewReport:
        """Valida um handoff YAML e retorna ReviewReport."""
        try:
            with open(handoff_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Erro ao carregar handoff YAML: {e}")
            return ReviewReport(
                ticket_id="unknown",
                final_score=0,
                verdict=ReviewVerdict.REJECTED,
                validations=[],
                timestamp="",
            )
        return self.review_dict(data, str(handoff_path))

    def review_dict(self, data: dict, ticket_id: str = "unknown") -> ReviewReport:
        """Valida dicionrio de handoff diretamente."""
        validations = []
        total_weight = 0
        weighted_score = 0

        for name, info in self.validators.items():
            validator_func = info["func"]
            weight = info["weight"]
            try:
                result = validator_func(data)
                if not isinstance(result, ValidationResult):
                    logger.error(f"Validador {name} retornou tipo invlido")
                    result = ValidationResult(
                        validator_name=name,
                        passed=False,
                        score=0,
                        message="Validador retornou tipo invlido",
                        details={},
                    )
            except Exception as e:
                logger.error(f"Erro no validador {name}: {e}")
                result = ValidationResult(
                    validator_name=name,
                    passed=False,
                    score=0,
                    message=f"Erro durante validao: {e}",
                    details={"error": str(e)},
                )
            validations.append(result)
            total_weight += weight
            weighted_score += result.score * weight

        final_score = (
            round(weighted_score / total_weight) if total_weight > 0 else 0
        )
        if final_score >= 80:
            verdict = ReviewVerdict.APPROVED
        elif final_score >= 50:
            verdict = ReviewVerdict.NEEDS_REVIEW
        else:
            verdict = ReviewVerdict.REJECTED

        return ReviewReport(
            ticket_id=ticket_id,
            final_score=final_score,
            verdict=verdict,
            validations=validations,
            timestamp="",  # preencher com timestamp atual se necessrio
        )

    def add_validator(
        self,
        name: str,
        validator_func: Callable[[dict], ValidationResult],
        weight: float = 1.0,
    ) -> None:
        """Registra validador customizado."""
        self.validators[name] = {"func": validator_func, "weight": weight}


_review_service_instance = None


def get_review_service() -> ConfidenceReviewService:
    """Singleton."""
    global _review_service_instance
    if _review_service_instance is None:
        _review_service_instance = ConfidenceReviewService()
    return _review_service_instance
