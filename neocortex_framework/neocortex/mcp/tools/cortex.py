#!/usr/bin/env python3
"""
NeoCortex Cortex Tool

MCP tool for neocortex_cortex.
"""

from typing import Dict, Any
from ...core.cortex_service import get_cortex_service


def register_tool(mcp):
    """
    Register the neocortex_cortex tool with the MCP server.
    """
    service = get_cortex_service()

    @mcp.tool(name="neocortex_cortex")
    def tool_cortex(action: str, section: str = "") -> Dict[str, Any]:
        """
        Access to central cortex.

        Actions:
        - get_full: Return full cortex content with metadata
        - get_section: Return a specific section
        - get_aliases: Return all defined aliases
        - get_workflows: Return defined workflows
        - validate_alias: Validate if an alias is correct
        """
        if action == "get_full":
            result = service.get_full_cortex()
            return {
                "success": True,
                "content": result["content"],
                "metadata": result["metadata"],
                "aliases": result["aliases"],
                "workflows": result["workflows"],
            }

        elif action == "get_section":
            if not section:
                return {"success": False, "error": "Section parameter required"}
            result = service.get_cortex_section(section)
            if result.get("found"):
                return {
                    "success": True,
                    "section": result["section"],
                    "content": result["content"],
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Section not found"),
                }

        elif action == "get_aliases":
            aliases = service.get_aliases()
            # Convert dict to list of {symbol, path}
            alias_list = [{"symbol": k, "path": v} for k, v in aliases.items()]
            return {"success": True, "aliases": alias_list}

        elif action == "get_workflows":
            workflows = service.get_workflows()
            return {"success": True, "workflows": workflows, "count": len(workflows)}

        elif action == "validate_alias":
            if not section:
                return {
                    "success": False,
                    "error": "Alias parameter required (use section parameter)",
                }
            result = service.validate_alias(section)
            if result["valid"]:
                return {
                    "success": True,
                    "valid": True,
                    "exists": result["exists"],
                    "alias": result.get("alias"),
                    "value": result.get("value"),
                }
            else:
                return {
                    "success": False,
                    "valid": False,
                    "error": result.get("error", "Alias not found"),
                }

        return {"success": False, "error": f"Unknown action: {action}"}

    return tool_cortex
