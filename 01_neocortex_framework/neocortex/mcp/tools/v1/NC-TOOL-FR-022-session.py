from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:00.919989'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TOOL-FR-022-session
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-TOOL-FR-022-session.py
FR-022  MCP Tool: neocortex_session

Consolida checkpoint, regression e savepoint em uma nica tool de sesso.
Aes disponveis:
  checkpoint.get_current    retorna checkpoint ativo da sesso
  checkpoint.set_current    define novo checkpoint com ID e descrio
  checkpoint.complete_task  marca tarefa como concluda no checkpoint
  checkpoint.list_history   histrico de checkpoints da sesso
  regression.check          verifica se erro atual  similar a regresso conhecida
  regression.add_entry      adiciona nova entrada no buffer de regresso
  regression.list_all       lista todas as regresses registradas
  savepoint.list_active     lista save points ativos (TTL 10min)
  savepoint.rollback        reverte ao save point indicado por save_id
  savepoint.discard         descarta save point sem rollback
"""


import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def _get_checkpoint_service():
    """Helper: retorna CheckpointService ou None se indisponvel."""
    try:
        from neocortex.core import get_checkpoint_service

        return get_checkpoint_service()
    except Exception as e:
        logger.warning(f"[session_tool] CheckpointService indisponvel: {e}")
        return None


def _get_regression_service():
    """Helper: retorna RegressionService ou None se indisponvel."""
    try:
        from neocortex.core import get_regression_service

        return get_regression_service()
    except Exception as e:
        logger.warning(f"[session_tool] RegressionService indisponvel: {e}")
        return None


def _get_save_point_service():
    """Helper: retorna SavePointService ou None se indisponvel."""
    try:
        from neocortex.core import get_save_point_service

        return get_save_point_service()
    except Exception as e:
        logger.warning(f"[session_tool] SavePointService indisponvel: {e}")
        return None


def register_tool(mcp) -> None:
    """Registra neocortex_session no servidor MCP."""

    @mcp.tool(name="neocortex_session")
    def neocortex_session(
        action: str,
        checkpoint_id: str = "",
        description: str = "",
        error: str = "",
        attempt: str = "",
        lesson: str = "",
        save_id: str = "",
    ) -> Dict[str, Any]:
        """Gerencia sessão NeoCortex: checkpoint, regression e savepoint.

        Actions: checkpoint.get_current, checkpoint.set_current, checkpoint.complete_task,
                 checkpoint.list_history, regression.check, regression.add_entry,
                 regression.list_all, savepoint.list_active, savepoint.rollback,
                 savepoint.discard, session.end
        """
        #  checkpoint.get_current
        if action == "checkpoint.get_current":
            cp_service = _get_checkpoint_service()
            if cp_service is None:
                return {
                    "success": False,
                    "error": "CheckpointService indisponvel.",
                    "action": action,
                }
            result = cp_service.get_current_checkpoint()
            return {"success": True, "action": action, **result}

        #  checkpoint.set_current
        elif action == "checkpoint.set_current":
            if not checkpoint_id:
                return {
                    "success": False,
                    "error": "checkpoint_id obrigatrio para ao 'checkpoint.set_current'.",
                    "action": action,
                }
            cp_service = _get_checkpoint_service()
            if cp_service is None:
                return {
                    "success": False,
                    "error": "CheckpointService indisponvel.",
                    "action": action,
                }
            result = cp_service.set_current_checkpoint(checkpoint_id, description)
            return {"success": True, "action": action, **result}

        #  checkpoint.complete_task
        elif action == "checkpoint.complete_task":
            task_name = checkpoint_id  # para compatibilidade
            if not task_name:
                return {
                    "success": False,
                    "error": "checkpoint_id (task_name) obrigatrio para ao 'checkpoint.complete_task'.",
                    "action": action,
                }
            cp_service = _get_checkpoint_service()
            if cp_service is None:
                return {
                    "success": False,
                    "error": "CheckpointService indisponvel.",
                    "action": action,
                }
            result = cp_service.complete_task(task_name)
            return {"success": True, "action": action, **result}

        #  checkpoint.list_history
        elif action == "checkpoint.list_history":
            cp_service = _get_checkpoint_service()
            if cp_service is None:
                return {
                    "success": False,
                    "error": "CheckpointService indisponvel.",
                    "action": action,
                }
            result = cp_service.list_checkpoint_history(limit=10)
            return {"success": True, "action": action, "history": result}

        #  regression.check
        elif action == "regression.check":
            if not error:
                return {
                    "success": False,
                    "error": "error obrigatrio para ao 'regression.check'.",
                    "action": action,
                }
            reg_service = _get_regression_service()
            if reg_service is None:
                return {
                    "success": False,
                    "error": "RegressionService indisponvel.",
                    "action": action,
                }
            result = reg_service.check_similar_errors(error)
            return {"success": True, "action": action, **result}

        #  regression.add_entry
        elif action == "regression.add_entry":
            if not error or not attempt or not lesson:
                return {
                    "success": False,
                    "error": "error, attempt e lesson obrigatrios para ao 'regression.add_entry'.",
                    "action": action,
                }
            reg_service = _get_regression_service()
            if reg_service is None:
                return {
                    "success": False,
                    "error": "RegressionService indisponvel.",
                    "action": action,
                }
            result = reg_service.add_regression_entry(error, attempt, lesson)
            return {"success": True, "action": action, **result}

        #  regression.list_all
        elif action == "regression.list_all":
            reg_service = _get_regression_service()
            if reg_service is None:
                return {
                    "success": False,
                    "error": "RegressionService indisponvel.",
                    "action": action,
                }
            result = reg_service.list_all_entries()
            return {"success": True, "action": action, "entries": result}

        #  savepoint.list_active
        elif action == "savepoint.list_active":
            sp_service = _get_save_point_service()
            if sp_service is None:
                return {
                    "success": False,
                    "error": "SavePointService indisponvel (Camada 3 no inicializada).",
                    "action": action,
                }
            active = sp_service.list_active()
            return {
                "success": True,
                "action": action,
                "count": len(active),
                "save_points": active,
            }

        #  savepoint.rollback
        elif action == "savepoint.rollback":
            if not save_id:
                return {
                    "success": False,
                    "error": "save_id obrigatrio para ao 'savepoint.rollback'.",
                    "action": action,
                }
            sp_service = _get_save_point_service()
            if sp_service is None:
                return {
                    "success": False,
                    "error": "SavePointService indisponvel.",
                    "action": action,
                }
            result = sp_service.rollback(save_id)
            return {"action": "savepoint.rollback", **result}

        #  savepoint.discard
        elif action == "savepoint.discard":
            if not save_id:
                return {
                    "success": False,
                    "error": "save_id obrigatrio para ao 'savepoint.discard'.",
                    "action": action,
                }
            sp_service = _get_save_point_service()
            if sp_service is None:
                return {
                    "success": False,
                    "error": "SavePointService indisponvel.",
                    "action": action,
                }
            removed = sp_service.discard(save_id)
            return {
                "success": removed,
                "action": "savepoint.discard",
                "save_id": save_id,
                "message": "Descartado com sucesso."
                if removed
                else "Save point no encontrado.",
            }

        #  session.end — T-13: encerra sessão formalmente (persist+list+clear)
        elif action == "session.end":
            from datetime import datetime as _dt
            end_report: dict = {"ended_at": _dt.now().isoformat(), "action": action}
            # 1) persist checkpoint
            cp_service = _get_checkpoint_service()
            if cp_service:
                try:
                    cp_result = cp_service.get_current_checkpoint()
                    end_report["checkpoint"] = cp_result
                except Exception as exc:
                    end_report["checkpoint_error"] = str(exc)
            # 2) list all regressions
            reg_service = _get_regression_service()
            if reg_service:
                try:
                    reg_entries = reg_service.list_all_entries()
                    end_report["regression_count"] = len(reg_entries) if isinstance(reg_entries, list) else "n/a"
                except Exception as exc:
                    end_report["regression_error"] = str(exc)
            # 3) discard all save points (TTL cleanup)
            sp_service = _get_save_point_service()
            discarded = 0
            if sp_service:
                try:
                    active_sps = sp_service.list_active()
                    for sp in active_sps:
                        sp_id = sp.get("id") or sp.get("save_id", "")
                        if sp_id:
                            sp_service.discard(sp_id)
                            discarded += 1
                except Exception as exc:
                    end_report["savepoint_error"] = str(exc)
            end_report["savepoints_discarded"] = discarded
            end_report["status"] = "session_closed"
            return {"success": True, **end_report}

        #  ação desconhecida
        else:
            return {
                "success": False,
                "error": f"Ação desconhecida: '{action}'.",
                "available": [
                    "checkpoint.get_current", "checkpoint.set_current",
                    "checkpoint.complete_task", "checkpoint.list_history",
                    "regression.check", "regression.add_entry", "regression.list_all",
                    "savepoint.list_active", "savepoint.rollback", "savepoint.discard",
                    "session.end",
                ],
            }

    return neocortex_session
