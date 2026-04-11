#!/usr/bin/env python3
"""
NeoCortex Checkpoint Tool

MCP tool for neocortex_checkpoint using CheckpointService.
"""

from typing import Dict, Any
from ...core import get_checkpoint_service


def register_tool(mcp):
    """
    Register neocortex_checkpoint tool on MCP server.
    """

    @mcp.tool(name="neocortex_checkpoint")
    def tool_checkpoint(
        action: str, checkpoint_id: str = "", description: str = ""
    ) -> Dict[str, Any]:
        """
        Checkpoint control.

        Actions:
        - get_current: Get current checkpoint
        - set_current: Set new current checkpoint
        - complete_task: Mark a task as complete
        - list_history: List checkpoint history
        - list_index: List global checkpoint index
        """
        # Get checkpoint service
        checkpoint_service = get_checkpoint_service()

        if action == "get_current":
            result = checkpoint_service.get_current_checkpoint()
            return result

        elif action == "set_current":
            if not checkpoint_id:
                return {"success": False, "error": "checkpoint_id is required"}

            result = checkpoint_service.set_current_checkpoint(
                checkpoint_id, description
            )
            return result

        elif action == "complete_task":
            # Using checkpoint_id as task name for backward compatibility
            task_name = checkpoint_id
            if not task_name:
                return {
                    "success": False,
                    "error": "task_name (checkpoint_id) is required",
                }

            result = checkpoint_service.complete_task(task_name)
            return result

        elif action == "list_history":
            result = checkpoint_service.list_checkpoint_history(limit=10)
            return result

        elif action == "list_index":
            result = checkpoint_service.get_global_checkpoint_index()
            return result

        return {"success": False, "error": f"Unknown action: {action}"}

    return tool_checkpoint
