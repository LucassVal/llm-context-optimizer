#!/usr/bin/env python3
"""
NeoCortex Init Tool

MCP tool for neocortex_init using InitService.
"""

from typing import Dict, Any
from ...core import get_init_service


def register_tool(mcp):
    """
    Register neocortex_init tool on MCP server.
    """

    @mcp.tool(name="neocortex_init")
    def tool_init(
        action: str, project_name: str = "", lobe_type: str = "phase"
    ) -> Dict[str, Any]:
        """
        Project initialization.

        Actions:
        - scan_project: Analyze current project structure
        - generate_cortex: Generate initial cortex
        - generate_lobe: Generate initial lobe for a module
        """
        # Get init service
        init_service = get_init_service()

        if action == "scan_project":
            result = init_service.scan_project()
            return result

        elif action == "generate_cortex":
            if not project_name:
                return {"success": False, "error": "project_name is required"}

            # Optional template parameter (could be passed as lobe_type for compatibility)
            template_type = (
                lobe_type
                if lobe_type in ["standard", "minimal", "full"]
                else "standard"
            )

            result = init_service.generate_cortex(project_name, template_type)
            return result

        elif action == "generate_lobe":
            if not project_name:
                return {
                    "success": False,
                    "error": "lobe_name (project_name parameter) is required",
                }

            result = init_service.generate_lobe(project_name, lobe_type)
            return result

        return {"success": False, "error": f"Unknown action: {action}"}

    return tool_init
