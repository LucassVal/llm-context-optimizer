"""---
domain: "orchestration"
layer: "core"
type: "service"
tags: ["tool", "009", "lobes"]
hash: "auto-generated"
---"""
#!/usr/bin/env python3
"""
NeoCortex Lobes Tool

MCP tool for neocortex_lobes using LobeService.
"""

from typing import Any, Dict

from ...core import get_lobe_service


def register_tool(mcp):
    """
    Register neocortex_lobes tool on MCP server.
    """

    @mcp.tool(name="neocortex_lobes")
    def tool_lobes(action: str, lobe_name: str = "") -> Dict[str, Any]:
        """Lobe management — list_active, get_content, get_checkpoint_tree, activate, deactivate, list_all, search, boot.load_active"""
        # Get lobe service
        lobe_service = get_lobe_service()

        if action == "list_active":
            # Get all lobes
            all_lobes_result = lobe_service.list_lobes()
            # Get active lobes
            active_lobes_result = lobe_service.get_active_lobes()

            return {
                "success": True,
                "all_lobes": all_lobes_result.get("lobes", []),
                "active_lobes": active_lobes_result.get("active_lobes", []),
                "active_lobes_details": active_lobes_result.get("lobe_details", []),
                "total_lobes": all_lobes_result.get("total", 0),
                "total_active": active_lobes_result.get("total_active", 0),
            }

        elif action == "list_all":
            result = lobe_service.list_lobes()
            return result

        elif action == "get_content":
            if not lobe_name:
                return {"success": False, "error": "lobe_name is required"}

            result = lobe_service.get_lobe(lobe_name)
            return result

        elif action == "get_checkpoint_tree":
            if not lobe_name:
                return {"success": False, "error": "lobe_name is required"}

            result = lobe_service.get_checkpoint_tree(lobe_name)
            return result

        elif action == "activate":
            if not lobe_name:
                return {"success": False, "error": "lobe_name is required"}

            result = lobe_service.activate_lobe(lobe_name)
            return result

        elif action == "deactivate":
            if not lobe_name:
                return {"success": False, "error": "lobe_name is required"}

            result = lobe_service.deactivate_lobe(lobe_name)
            return result

        elif action == "search":
            # For search, lobe_name can be used as query parameter
            query = lobe_name  # Using lobe_name as query for backward compatibility
            if not query:
                return {"success": False, "error": "search query is required"}

            result = lobe_service.search_lobes(query, case_sensitive=False)
            return result

        elif action == "boot.load_active":
            # T-15: carrega todos os lobes ativos referenciados no boot manifest
            active_result = lobe_service.get_active_lobes()
            active_names = active_result.get("active_lobes", [])
            loaded = []
            errors = []
            for lobe_nm in active_names:
                try:
                    content_result = lobe_service.get_lobe(lobe_nm)
                    if content_result.get("success"):
                        content = content_result.get("content", "")
                        loaded.append({
                            "lobe": lobe_nm,
                            "size_chars": len(content),
                            "preview": content[:200] + "..." if len(content) > 200 else content,
                        })
                    else:
                        errors.append({"lobe": lobe_nm, "error": content_result.get("error", "unknown")})
                except Exception as exc:
                    errors.append({"lobe": lobe_nm, "error": str(exc)})
            return {
                "success": True,
                "action": action,
                "lobes_loaded": len(loaded),
                "lobes": loaded,
                "errors": errors,
            }

        return {"success": False, "error": f"Unknown action: {action}"}

    return tool_lobes
