"""---
_genealogy:
  injected_at: '2026-04-16T00:24:00.388668'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
#!/usr/bin/env python3
"""
NeoCortex Ledger Tool

MCP tool for neocortex_ledger.
"""

from typing import Any, Dict

from ...core.ledger_service import get_ledger_service


def register_tool(mcp):
    """
    Register the neocortex_ledger tool with the MCP server.
    """
    service = get_ledger_service()

    @mcp.tool(name="neocortex_ledger")
    def tool_ledger(action: str, metric: str = "") -> Dict[str, Any]:
        """Access to JSON ledger.

        Actions: get_metrics, get_atomic_locks, get_dependency_graph, prune_context"""
        if action == "get_metrics":
            metrics = service.get_session_metrics()
            return {"success": True, "metrics": metrics}

        elif action == "get_atomic_locks":
            ledger = service.get_full_ledger()
            granular_state = ledger.get("granular_state_management", {})
            atomic_locks = granular_state.get("atomic_locks", {})
            return {"success": True, "atomic_locks": atomic_locks}

        elif action == "get_dependency_graph":
            # Simulation - returns empty structure
            return {
                "success": True,
                "dependency_graph": {
                    "active_module": "",
                    "first_degree": [],
                    "second_degree": [],
                },
            }

        elif action == "prune_context":
            # Delegate to service
            result = service.prune_context()
            # Adapt service response to expected format
            if result["success"]:
                return {
                    "success": True,
                    "moved_to_cold": result.get("pruned_count", 0),
                    "remaining_in_hot": result.get("hot_remaining", 0),
                    "message": result.get("message", "Context pruned"),
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Pruning failed"),
                }

        return {"success": False, "error": f"Unknown action: {action}"}

    return tool_ledger
