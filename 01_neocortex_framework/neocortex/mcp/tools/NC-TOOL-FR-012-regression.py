#!/usr/bin/env python3
"""
NeoCortex Regression Tool

MCP tool for neocortex_regression using RegressionService.
"""

from typing import Dict, Any
from ...core import get_regression_service


def register_tool(mcp):
    """
    Register neocortex_regression tool on MCP server.
    """

    @mcp.tool(name="neocortex_regression")
    def tool_regression(
        action: str, error: str = "", attempt: str = "", lesson: str = ""
    ) -> Dict[str, Any]:
        """
        STEP 0 and regression buffer.

        Actions:
        - check: Check for similar regression errors
        - add_entry: Add new entry to regression buffer
        - list_all: List all entries in buffer
        - clear: Clear regression buffer (requires confirm=True)
        - stats: Get buffer statistics
        """
        # Get regression service
        regression_service = get_regression_service()

        if action == "check":
            result = regression_service.check_similar_errors(error)
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
