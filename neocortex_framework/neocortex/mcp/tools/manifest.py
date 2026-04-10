#!/usr/bin/env python3
"""
NeoCortex Manifest Tool

MCP tool for neocortex_manifest using ManifestService.
"""

import json
from typing import Dict, Any
from ...core import get_manifest_service


def register_tool(mcp):
    """
    Register neocortex_manifest tool on MCP server.
    """

    @mcp.tool(name="neocortex_manifest")
    def tool_manifest(
        action: str, target: str = "", metadata: str = ""
    ) -> Dict[str, Any]:
        """
        Manifest management (lightweight indices for lobes/cortex).

        Actions:
        - generate: Generate manifest for a lobe or cortex
        - update: Update metadata of an existing manifest
        - query: Query manifests by tags, domain or entities
        - get: Get specific manifest
        - list: List all manifests
        - delete: Delete a manifest
        - generate_all: Generate manifests for all lobes and cortex
        """
        # Get manifest service
        manifest_service = get_manifest_service()

        if action == "generate":
            if not target:
                return {
                    "success": False,
                    "error": "target is required (cortex or lobe name)",
                }

            result = manifest_service.generate_manifest(target)
            return result

        elif action == "update":
            if not target:
                return {"success": False, "error": "target is required (manifest ID)"}

            # Parse metadata JSON if provided
            metadata_dict = None
            if metadata:
                try:
                    metadata_dict = json.loads(metadata)
                except json.JSONDecodeError:
                    return {"success": False, "error": "metadata must be valid JSON"}

            result = manifest_service.update_manifest(target, metadata_dict)
            return result

        elif action == "query":
            # Parse metadata as search term or tags
            search_term = None
            tags = None

            if metadata:
                # Try to parse as JSON for tags
                try:
                    metadata_dict = json.loads(metadata)
                    if isinstance(metadata_dict, list):
                        tags = metadata_dict
                    elif isinstance(metadata_dict, dict) and "tags" in metadata_dict:
                        tags = metadata_dict["tags"]
                    elif isinstance(metadata_dict, dict) and "search" in metadata_dict:
                        search_term = metadata_dict["search"]
                    else:
                        search_term = str(metadata_dict)
                except json.JSONDecodeError:
                    # Use as search term
                    search_term = metadata

            result = manifest_service.query_manifests(
                search_term=search_term, tags=tags, limit=100
            )
            return result

        elif action == "get":
            if not target:
                return {"success": False, "error": "target is required (manifest ID)"}

            result = manifest_service.get_manifest(target)
            return result

        elif action == "list":
            result = manifest_service.list_all_manifests()
            return result

        elif action == "delete":
            if not target:
                return {"success": False, "error": "target is required (manifest ID)"}

            result = manifest_service.delete_manifest(target)
            return result

        elif action == "generate_all":
            result = manifest_service.generate_all_manifests()
            return result

        return {"success": False, "error": f"Unknown action: {action}"}

    return tool_manifest
