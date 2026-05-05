"""---
@Module  mcp domain: "core" layer: "core" type: "file" tags: ["
---
"""


"""
Validadores de confiana para handoffs.
"""

import importlib as _il

# Importar mdulos hyphenated via importlib
_naming = _il.import_module(
    ".NC-VAL-FR-001-naming-validator", package="neocortex.core.review.validators"
)
_compile = _il.import_module(
    ".NC-VAL-FR-002-compile-validator", package="neocortex.core.review.validators"
)
_locks = _il.import_module(
    ".NC-VAL-FR-003-locks-validator", package="neocortex.core.review.validators"
)

NamingValidator = _naming.NamingValidator
CompileValidator = _compile.CompileValidator
LocksValidator = _locks.LocksValidator

__all__ = ["NamingValidator", "CompileValidator", "LocksValidator"]
