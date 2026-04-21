from __future__ import annotations

"""---
domain: "orchestration"
layer: "core"
type: "service"
tags: ["tool", "022", "session"]
hash: "auto-generated"
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
        """
        Gerencia sesso NeoCortex: checkpoint, regression e savepoint.

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

        Args:
            action:        Ao desejada (ver lista acima)
            checkpoint_id: ID do checkpoint (para set_current, complete_task)
            description:   Descrio do checkpoint (para set_current)
            error:         Mensagem de erro (para regression.check/add_entry)
            attempt:       Tentativa de resoluo (para regression.add_entry)
            lesson:        Lio aprendida (para regression.add_entry)
            save_id:       ID do save point (para savepoint.rollback/discard)

        Returns:
            Dict com resultado da operao.
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

        #  ao desconhecida
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'.",
                "available": [
                    "checkpoint.get_current",
                    "checkpoint.set_current",
                    "checkpoint.complete_task",
                    "checkpoint.list_history",
                    "regression.check",
                    "regression.add_entry",
                    "regression.list_all",
                    "savepoint.list_active",
                    "savepoint.rollback",
                    "savepoint.discard",
                ],
            }

    return neocortex_session
