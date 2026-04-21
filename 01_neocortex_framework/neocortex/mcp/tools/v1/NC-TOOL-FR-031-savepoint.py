from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.274189'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TOOL-FR-031-savepoint
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-TOOL-FR-031-savepoint.py
SAVE-004  MCP Tool: neocortex_savepoint

Expe o SavePointService via MCP com 4 aes:
  - list_active   lista save points ativos (no expirados)
  - rollback      reverte para um save point por ID
  - discard       descarta save point sem rollback
  - get_status    retorna mtricas e status do servio (para HUD)
"""


import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def _get_sps():
    """Helper: retorna SavePointService ou None se indisponvel."""
    try:
        from neocortex.core import get_save_point_service
        return get_save_point_service()
    except Exception as e:
        logger.warning(f"[savepoint_tool] SavePointService no disponvel: {e}")
        return None


def register_tool(mcp) -> None:
    """Registra neocortex_savepoint no servidor MCP."""

    @mcp.tool(name="neocortex_savepoint")
    def neocortex_savepoint(
        action: str,
        save_id: str = "",
    ) -> Dict[str, Any]:
        """Gerencia Save Points do NeoCortex (STEP -1 / STEP +1).

        Actions: list_active, rollback, discard, get_status"""
        sps = _get_sps()
        if sps is None:
            return {
                "success": False,
                "error": "SavePointService indisponvel (Camada 3 no inicializada).",
                "action": action,
            }

        #  list_active
        if action == "list_active":
            active = sps.list_active()
            return {
                "success": True,
                "action": "list_active",
                "count": len(active),
                "save_points": active,
            }

        #  get_status
        elif action == "get_status":
            status = sps.get_compliance_status()
            return {
                "success": True,
                "action": "get_status",
                **status,
            }

        #  rollback
        elif action == "rollback":
            if not save_id:
                return {
                    "success": False,
                    "error": "save_id obrigatrio para ao 'rollback'.",
                    "action": action,
                }
            result = sps.rollback(save_id)
            return {
                "action": "rollback",
                **result,
            }

        #  discard
        elif action == "discard":
            if not save_id:
                return {
                    "success": False,
                    "error": "save_id obrigatrio para ao 'discard'.",
                    "action": action,
                }
            removed = sps.discard(save_id)
            return {
                "success": removed,
                "action": "discard",
                "save_id": save_id,
                "message": "Descartado com sucesso." if removed else "Save point no encontrado.",
            }

        #  ao desconhecida
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'. Use: list_active | rollback | discard | get_status",
                "action": action,
            }

