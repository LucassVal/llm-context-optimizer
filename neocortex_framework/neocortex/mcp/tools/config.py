#!/usr/bin/env python3
"""
NeoCortex Config Tool

MCP tool for neocortex_config using ConfigService.
"""

from typing import Dict, Any
from ...core import get_config_service


def register_tool(mcp):
    """
    Register neocortex_config tool on MCP server.
    """

    @mcp.tool(name="neocortex_config")
    def tool_config(action: str, key: str = "", value: str = "") -> Dict[str, Any]:
        """
        System configuration.

        Actions:
        - get_config: Get current configuration
        - set_model: Set LLM model to use
        - list_models: List available models
        - set_constraint: Set system constraint (key=constraint, value=new_value)
        - list_constraints: List system constraints
        """
        # Get config service
        config_service = get_config_service()

        if action == "get_config":
            result = config_service.get_system_config()
            return result

        elif action == "set_model":
            if not key:
                return {"success": False, "error": "key (model name) is required"}

            result = config_service.set_model(key)
            return result

        elif action == "list_models":
            result = config_service.list_available_models()
            return result

        elif action == "set_constraint":
            if not key or not value:
                return {
                    "success": False,
                    "error": "key (constraint) and value are required",
                }

            # Convert value to appropriate type
            try:
                # Try integer first
                typed_value = int(value)
            except ValueError:
                try:
                    # Try float
                    typed_value = float(value)
                except ValueError:
                    # Keep as string
                    typed_value = value

            result = config_service.update_system_constraint(key, typed_value)
            return result

        elif action == "list_constraints":
            result = config_service.get_constraint_summary()
            return result

        return {"success": False, "error": f"Unknown action: {action}"}

    return tool_config
