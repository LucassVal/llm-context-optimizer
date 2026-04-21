"""---
_genealogy:
  injected_at: '2026-04-16T00:24:00.514004'
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
NeoCortex Regression Tool

MCP tool for neocortex_regression using RegressionService.
"""

from typing import Any, Dict

from ...core import get_regression_service


def register_tool(mcp):
    """
    Register neocortex_regression tool on MCP server.
    """

    @mcp.tool(name="neocortex_regression")
    def tool_regression(
        action: str, error: str = "", attempt: str = "", lesson: str = ""
    ) -> Dict[str, Any]:
        """STEP 0 and regression buffer.

        Actions: check, add_entry, list_all, clear, stats"""
        # Get regression service
        regression_service = get_regression_service()

        if action == "check":
            result = regression_service.check_similar_errors(error)
            # T-11: bloquear ativamente se regressão CRITICAL encontrada
            block = False
            block_reason = ""
            entries = result.get("similar_errors", result.get("matches", []))
            if isinstance(entries, list):
                for entry in entries:
                    sev = str(entry.get("severity", "")).upper()
                    if sev in ("CRITICAL", "HIGH"):
                        block = True
                        block_reason = entry.get("error", entry.get("description", "Regressão crítica detectada"))
                        break
            result["block"] = block
            result["block_reason"] = block_reason if block else ""
            return result


        elif action == "add_entry":
            if not error or not attempt or not lesson:
                return {
                    "success": False,
                    "error": "error, attempt and lesson are required",
                }

            result = regression_service.add_regression_entry(error, attempt, lesson)
            return result

        elif action == "list_all":
            result = regression_service.list_all_entries()
            return result

        elif action == "clear":
            # For safety, we require explicit confirmation
            # In real usage, confirmation would come from client
            result = regression_service.clear_regression_buffer(confirm=False)
            return result

        elif action == "stats":
            result = regression_service.get_buffer_stats()
            return result

        return {"success": False, "error": f"Unknown action: {action}"}

    return tool_regression
