"""---
_genealogy:
  injected_at: '2026-04-16T00:24:00.304771'
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
NeoCortex Export Tool

MCP tool for neocortex_export using ExportService.
"""

from typing import Any, Dict

from ...core import get_export_service


def register_tool(mcp):
    """
    Register neocortex_export tool on MCP server.
    """

    @mcp.tool(name="neocortex_export")
    def tool_export(action: str, format: str = "markdown") -> Dict[str, Any]:
        """Data export.

        Actions: to_markdown, to_json, to_graph, export_lobes"""
        # Get export service
        export_service = get_export_service()

        if action == "to_markdown":
            result = export_service.export_to_markdown(
                include_lobes=True, include_timeline=True
            )
            return result

        elif action == "to_json":
            pretty = format.lower() == "pretty"
            result = export_service.export_to_json(pretty=pretty)
            return result

        elif action == "to_graph":
            result = export_service.export_to_graph(graph_type=format)
            return result

        elif action == "export_lobes":
            # For simplicity, export all lobes
            # In a real implementation, could accept lobe names as parameters
            result = export_service.export_lobes_to_markdown()
            return result

        return {"success": False, "error": f"Unknown action: {action}"}

    return tool_export
