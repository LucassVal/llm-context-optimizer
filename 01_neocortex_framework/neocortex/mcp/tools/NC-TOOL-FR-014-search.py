#!/usr/bin/env python3
"""
NeoCortex Search Tool

MCP tool for advanced search across lobes using LobeIndex.
"""

from typing import Dict, Any, Optional, List
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
        """
        Advanced search across lobes with metadata filtering.

        Uses LobeIndex for fast full-text search with filtering by
        module, status, and tags.

        Args:
            query: Full-text search query (FTS5 syntax supported)
            module: Filter by module name (e.g., "testing", "core")
            status: Filter by status (e.g., "active", "archived")
            tags: Filter by tags (list of tags, AND logic)
            limit: Maximum number of results (default: 20)

        Returns:
            Dictionary with search results and metadata
        """
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
