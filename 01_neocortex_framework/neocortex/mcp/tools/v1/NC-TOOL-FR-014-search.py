"""---
_genealogy:
  injected_at: '2026-04-16T00:24:00.595235'
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
NeoCortex Search Tool

MCP tool for advanced search across lobes using LobeIndex.
"""

from typing import Any, Dict, List, Optional

from ...core import get_lobe_service


def register_tool(mcp):
    """
    Register neocortex_search tool on MCP server.
    """

    @mcp.tool(name="neocortex_search")
    def tool_search(
        query: str,
        module: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Advanced search across lobes with metadata filtering.

        Args: query (FTS5), module, status, tags, limit=20"""
        # Get lobe service
        lobe_service = get_lobe_service()

        # Perform advanced search
        result = lobe_service.search_lobes_advanced(
            query=query,
            module=module,
            status=status,
            tags=tags,
            limit=limit,
        )

        return result

    return tool_search
