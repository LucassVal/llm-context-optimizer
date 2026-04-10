#!/usr/bin/env python3
"""
NeoCortex Ledger Tool

MCP tool for neocortex_ledger.
"""

from typing import Dict, Any
from ...core.ledger_service import get_ledger_service


def register_tool(mcp):
    """
    Register the neocortex_ledger tool with the MCP server.
    """
    service = get_ledger_service()

    @mcp.tool(name="neocortex_ledger")
    def tool_ledger(action: str, metric: str = "") -> Dict[str, Any]:
        """
        Access to JSON ledger.

        Actions:
        - get_metrics: Returns session metrics
        - get_atomic_locks: Returns atomic locks
        - get_dependency_graph: Returns dependency graph
        - prune_context: Execute context pruning
        """
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
            # Context pruning simulation (to be moved to service)
            ledger = service.get_full_ledger()
            memory_temp = ledger.get("memory_temperature", {})
            hot_context = memory_temp.get("hot_context", {})
            interactions = hot_context.get("interactions", [])

            if len(interactions) > 5:
                # Move oldest to cold storage
                to_move = interactions[:-5]
                remaining = interactions[-5:]

                cold_storage = memory_temp.get("cold_storage", {})
                archived = cold_storage.get("archived_interactions", [])
                archived.extend(to_move)

                hot_context["interactions"] = remaining
                cold_storage["archived_interactions"] = archived
                memory_temp.update(
                    {"hot_context": hot_context, "cold_storage": cold_storage}
                )

                # Log compaction
                compaction_log = memory_temp.get("compaction_log", {})
                entries = compaction_log.get("entries", [])
                entries.append(
                    {
                        "timestamp": "auto_generated",
                        "moved_count": len(to_move),
                        "remaining_count": len(remaining),
                    }
                )
                compaction_log["entries"] = entries
                memory_temp["compaction_log"] = compaction_log

                ledger["memory_temperature"] = memory_temp
                # Write back using repository (service doesn't have direct write)
                from ...repositories import FileSystemLedgerRepository

                repo = FileSystemLedgerRepository()
                repo.write_ledger(ledger)

                return {
                    "success": True,
                    "moved_to_cold": len(to_move),
                    "remaining_in_hot": len(remaining),
                    "message": f"Context pruned: {len(to_move)} interactions moved to cold storage",
                }
            else:
                return {
                    "success": True,
                    "message": "No pruning needed (hot_context <= 5 interactions)",
                }

        return {"success": False, "error": f"Unknown action: {action}"}

    return tool_ledger
