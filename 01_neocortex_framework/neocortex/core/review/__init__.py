"""---
@Module  mcp domain: "core" layer: "core" type: "file" tags: ["
---
"""


"""
Mdulo de reviso por confiana (Confidence Review).
"""

import importlib as _il

# Importar mdulo hyphenated via importlib
_rev = _il.import_module(
    ".NC-REV-FR-001-confidence-review", package="neocortex.core.review"
)

BaseValidator = _rev.BaseValidator
ValidatorResult = _rev.ValidatorResult
ValidationResult = _rev.ValidationResult
ConfidenceReviewService = _rev.ConfidenceReviewService
ReviewReport = _rev.ReviewReport
VALIDATOR_WEIGHTS = _rev.VALIDATOR_WEIGHTS
get_review_service = _rev.get_review_service

__all__ = [
    "VALIDATOR_WEIGHTS",
    "BaseValidator",
    "ConfidenceReviewService",
    "ReviewReport",
    "ValidationResult",
    "ValidatorResult",
    "get_review_service",
]
