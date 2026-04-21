"""---
domain: "core"
layer: "core"
type: "file"
tags: ["init"]
hash: "auto-generated"
---"""

"""
NeoCortex Core Utilities.
"""

import importlib as _il

# Importar mdulos hyphenated via importlib
_yaml_parser = _il.import_module(
    ".NC-UTL-FR-001-yaml-safe-parser", package="neocortex.core.utils"
)
_id_validator = _il.import_module(
    ".NC-UTL-FR-004-id-validator", package="neocortex.core.utils"
)

# Exportar funcionalidades do yaml parser
safe_load = _yaml_parser.safe_load
safe_dump = _yaml_parser.safe_dump
get_field = _yaml_parser.get_field
set_field = _yaml_parser.set_field
validate_schema = _yaml_parser.validate_schema
load_yaml = _yaml_parser.load_yaml

# Exportar IDValidator e constantes
IDValidator = _id_validator.IDValidator
EXIT_CODE_PERMANENT = _id_validator.EXIT_CODE_PERMANENT
get_id_validator = _id_validator.get_id_validator

# Importar yaml inheritance module
_yaml_inheritance = _il.import_module(
    ".yaml_inheritance", package="neocortex.core.utils"
)

# Exportar funcionalidades do yaml inheritance
deep_merge = _yaml_inheritance.deep_merge
resolve_inheritance = _yaml_inheritance.resolve_inheritance
load_yaml_with_inheritance = _yaml_inheritance.load_yaml_with_inheritance
validate_inheritance_chain = _yaml_inheritance.validate_inheritance_chain

__all__ = [
    "safe_load",
    "safe_dump",
    "get_field",
    "set_field",
    "validate_schema",
    "load_yaml",
    "IDValidator",
    "EXIT_CODE_PERMANENT",
    "get_id_validator",
    "deep_merge",
    "resolve_inheritance",
    "load_yaml_with_inheritance",
    "validate_inheritance_chain",
]
