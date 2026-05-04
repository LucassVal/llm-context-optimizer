"""
@Service: mcp | domain: "orchestration" | layer: "core" | type: "tool-loader"
NC-TOOL-FR-000-init — MCP Tools Auto-Loader v2.0
Maps short names to NC-SUPER tool modules for importlib dynamic loading.
Replaces fossil v1.0 that referenced deleted NC-TOOL-FR-001..020 files.
"""
import importlib
import sys
from pathlib import Path

_TOOL_MAPPING = {
    "governance":     "NC-SUPER-001-governance",
    "orchestration":  "NC-SUPER-002-orchestration",
    "memory":         "NC-SUPER-003-memory",
    "state":          "NC-SUPER-004-state",
    "llm_router":     "NC-SUPER-005-llm-router",
    "system":         "NC-SUPER-006-system",
    "brain":          "NC-SUPER-007-brain",
    "context":        "NC-SUPER-008-context",
    "security":       "NC-SUPER-009-security",
    "benchmark":      "NC-SUPER-010-benchmark",
    "notification":   "NC-SUPER-011-notification",
    "akl":            "NC-SUPER-012-akl",
    "health":         "NC-SUPER-013-health",
    "ledger":         "NC-SUPER-014-ledger",
    "memory_auto":    "NC-SUPER-015-memory-auto",
    "picoclaw":       "NC-SUPER-016-picoclaw",
    "replication":    "NC-SUPER-019-replication",
    "evolution":      "NC-SUPER-020-evolution",
    "openclaude":     "NC_TOOL_FR_020_openclaude_bridge",
    "vscode":         "NC_TOOL_FR_021_vscode_bridge",
    "pulse":          "NC-MCP-FR-001-pulse",
}

for short_name, stem in _TOOL_MAPPING.items():
    try:
        module = importlib.import_module(f".{stem}", package="neocortex.mcp.tools")
        globals()[short_name] = module
    except ModuleNotFoundError:
        pass
