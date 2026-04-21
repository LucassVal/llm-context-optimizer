"""---
_genealogy:
  injected_at: '2026-04-16T00:24:00.262221'
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
NeoCortex Checkpoint Tool

MCP tool for neocortex_checkpoint using CheckpointService.
"""

from typing import Any, Dict

from ...core import get_checkpoint_service


def register_tool(mcp):
    """
    Register neocortex_checkpoint tool on MCP server.
    """

    @mcp.tool(name="neocortex_checkpoint")
    def tool_checkpoint(
        action: str, checkpoint_id: str = "", description: str = ""
    ) -> Dict[str, Any]:
        """Controle de checkpoint — get_current, set_current, complete_task, list_index, persist"""
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

        elif action == "persist":
            # T-12: escreve checkpoint atual em DIR-DS-002-audit-logs/
            import json as _json
            from datetime import datetime as _dt
            from pathlib import Path as _P
            cp_result = checkpoint_service.get_current_checkpoint()
            try:
                from ...config import get_config as _gc
                _cfg = _gc()
                audit_dir = _P(_cfg.project_root) / "DIR-DS-002-audit-logs"
                audit_dir.mkdir(parents=True, exist_ok=True)
                today = _dt.now().strftime("%Y-%m-%d-%H%M")
                record = {
                    "action": "checkpoint.persist",
                    "persisted_at": _dt.now().isoformat(),
                    "checkpoint": cp_result,
                    "description": description or "auto-persist",
                }
                out_path = audit_dir / f"NC-CHK-DS-{today}-checkpoint.json"
                with open(out_path, "w", encoding="utf-8") as fh:
                    _json.dump(record, fh, indent=2, default=str)
                return {"success": True, "action": action, "path": str(out_path), "checkpoint": cp_result}
            except Exception as exc:
                return {"success": False, "error": str(exc), "checkpoint": cp_result}

        return {"success": False, "error": f"Unknown action: {action}"}

    return tool_checkpoint
