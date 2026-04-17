"""---
domain: "orchestration"
layer: "core"
type: "service"
tags: ["init"]
hash: "auto-generated"
---
Dynamic import of NC-TOOL-FR-* modules.
"""

import importlib
import sys
from pathlib import Path

# Mapping from short names to filename stems (without .py)
_TOOL_MAPPING = {
    "cortex": "NC-TOOL-FR-001-cortex",
    "ledger": "NC-TOOL-FR-008-ledger",
    "regression": "NC-TOOL-FR-012-regression",
    "checkpoint": "NC-TOOL-FR-004-checkpoint",
    "config": "NC-TOOL-FR-005-config",
    "init": "NC-TOOL-FR-007-init",
    "export": "NC-TOOL-FR-006-export",
    "lobes": "NC-TOOL-FR-009-lobes",
    "manifest": "NC-TOOL-FR-019-project-manifest",
    "kg": "NC-TOOL-FR-020-knowledge",
    "agent": "NC-TOOL-FR-002-agent",
    "benchmark": "NC-TOOL-FR-003-benchmark",
    "peers": "NC-TOOL-FR-010-peers",
    "security": "NC-TOOL-FR-015-security",
    "pulse": "NC-TOOL-FR-011-pulse",
    "search": "NC-TOOL-FR-014-search",
}

# Import each module and expose it under its short name
for short_name, stem in _TOOL_MAPPING.items():
    try:
        module = importlib.import_module(f".{stem}", package="neocortex.mcp.tools")
        globals()[short_name] = module
    except ModuleNotFoundError:
        # If module not found, leave it undefined (will cause ImportError if used)
        pass
