"""---
domain: "orchestration"
layer: "core"
type: "service"
tags: ["tool", "035", "task"]
hash: "auto-generated"
---"""
"""
NC-TOOL-FR-035-task.py
MCP Tool: neocortex_task  execuo de tasks via HTTP com polling real.

Actions:
- execute: Envia task para sub-servidor e registra UUID no broker
- poll: Consulta status de task via GET /health ou resultado via GET /task/{id}
- cancel: Cancela task pendente (marca no broker como "cancelled")
- list_queued: Lista tasks em fila para um port especfico

Integrao com NC-SVC-FR-015-task-broker.py se disponvel.
Fallback: dict em memria `_task_registry`.
"""

import json
import logging
import time
import urllib.error
import urllib.request
import uuid
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Registry de tasks em memria (fallback)
_task_registry: Dict[str, Dict[str, Any]] = {}

# Tenta importar TaskBroker se disponvel
_task_broker = None
try:
    import importlib.util
    from pathlib import Path

    broker_path = (
        Path(__file__).parent.parent.parent
        / "core"
        / "services"
        / "NC-SVC-FR-015-task-broker.py"
    )
    if broker_path.exists():
        spec = importlib.util.spec_from_file_location("task_broker", broker_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "TaskBroker"):
                _task_broker = module.TaskBroker()
                logger.info("TaskBroker carregado: persistncia ativada")
            else:
                logger.warning("TaskBroker no encontrado no mdulo")
        else:
            logger.debug("No foi possvel criar spec para TaskBroker")
    else:
        logger.debug("Arquivo TaskBroker no encontrado")
except Exception as e:
    logger.debug(f"TaskBroker indisponvel: {e}")


def _generate_task_id() -> str:
    """Gera ID curto para task."""
    return str(uuid.uuid4())[:8]


def _http_post_task(
    port: int, task_data: Dict[str, Any], timeout: int = 30
) -> Dict[str, Any]:
    """Envia task para sub-servidor via HTTP POST /task."""
    url = f"http://127.0.0.1:{port}/task"
    payload = json.dumps(task_data).encode("utf-8")

    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            response_body = resp.read().decode("utf-8")
            result = json.loads(response_body)
            return {
                "success": True,
                "http_status": resp.status,
                "result": result,
            }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"HTTP connection failed to {url}: {e.reason}",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _http_get_health(port: int, timeout: int = 5) -> Dict[str, Any]:
    """Consulta status do sub-servidor via GET /health."""
    url = f"http://127.0.0.1:{port}/health"
    try:
        req = urllib.request.urlopen(url, timeout=timeout)
        data = json.loads(req.read().decode())
        return {"reachable": True, "status": data.get("status", "ok"), "data": data}
    except urllib.error.URLError as e:
        return {"reachable": False, "error": str(e.reason)}
    except Exception as e:
        return {"reachable": False, "error": str(e)}


def _poll_task_result(task_id: str, port: int, timeout_seconds: int) -> Dict[str, Any]:
    """Polling de resultado de task com timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        # Verifica se task j est concluda no registry
        task = _task_registry.get(task_id)
        if task and task.get("status") in ("done", "failed"):
            return {
                "task_id": task_id,
                "status": task["status"],
                "result": task.get("result"),
                "elapsed": time.time() - start_time,
            }

        # Verifica health do sub-servidor
        health = _http_get_health(port, timeout=5)
        if not health.get("reachable"):
            return {
                "task_id": task_id,
                "status": "failed",
                "error": f"Sub-servidor na porta {port} inacessvel",
                "elapsed": time.time() - start_time,
            }

        time.sleep(1)  # polling interval

    return {
        "task_id": task_id,
        "status": "timeout",
        "error": f"Timeout de {timeout_seconds} segundos atingido",
        "elapsed": timeout_seconds,
    }


def register_tool(mcp) -> None:
    """Registra a tool neocortex_task no servidor MCP."""

    @mcp.tool(name="neocortex_task")
    def neocortex_task(
        action: str,
        port: int = 0,
        task_data: str = "",
        timeout_seconds: int = 30,
        task_id: str = "",
    ) -> Dict[str, Any]:
        """
        Execuo de tasks via HTTP com polling real.

        Args:
            action: ao desejada (execute, poll, cancel, list_queued)
            port: porta do sub-servidor (para execute, poll, list_queued)
            task_data: JSON string com dados da task (para execute)
            timeout_seconds: timeout para polling (para execute e poll)
            task_id: identificador da task (para poll, cancel)
        """
        #  execute
        if action == "execute":
            if not port:
                return {"success": False, "error": "Porta  obrigatria para execute."}
            if not task_data:
                return {"success": False, "error": "task_data  obrigatrio."}

            try:
                task_dict = json.loads(task_data) if task_data else {}
            except json.JSONDecodeError:
                return {"success": False, "error": "JSON invlido em task_data"}

            # Gera ID da task
            new_task_id = _generate_task_id()

            # Registra task como queued
            task_entry = {
                "task_id": new_task_id,
                "port": port,
                "status": "queued",
                "created_at": time.time(),
                "data": task_dict,
                "result": None,
            }

            if _task_broker:
                # Registra no broker (se disponvel)
                broker_result = _task_broker.register_task(
                    task_id=new_task_id,
                    port=port,
                    task_data=task_dict,
                    timeout_seconds=timeout_seconds,
                )
                if not broker_result.get("success"):
                    return broker_result
            else:
                _task_registry[new_task_id] = task_entry

            # Envia task via HTTP
            http_result = _http_post_task(port, task_dict, timeout_seconds)
            if not http_result.get("success"):
                return http_result

            # Atualiza status para done (se sucesso) e armazena resultado
            task_entry["status"] = "done"
            task_entry["result"] = http_result.get("result")
            if _task_broker:
                _task_broker.update_task_status(
                    new_task_id, "done", http_result.get("result")
                )
            else:
                _task_registry[new_task_id] = task_entry

            return {
                "success": True,
                "task_id": new_task_id,
                "status": "queued",
                "endpoint": f"http://127.0.0.1:{port}/task",
                "http_result": http_result,
            }

        #  poll
        elif action == "poll":
            if not task_id:
                return {"success": False, "error": "task_id  obrigatrio para poll."}
            if not port:
                return {"success": False, "error": "port  obrigatrio para poll."}

            # Consulta broker ou registry
            if _task_broker:
                broker_result = _task_broker.get_task_status(task_id)
                if broker_result.get("success"):
                    return {
                        "success": True,
                        "task_id": task_id,
                        "status": broker_result.get("status", "unknown"),
                        "result": broker_result.get("result"),
                    }
                else:
                    return broker_result
            else:
                task = _task_registry.get(task_id)
                if not task:
                    return {
                        "success": False,
                        "error": f"Task no encontrada: {task_id}",
                    }

                # Se task ainda est queued, faz polling real
                if task.get("status") == "queued":
                    return _poll_task_result(task_id, port, timeout_seconds)
                else:
                    return {
                        "success": True,
                        "task_id": task_id,
                        "status": task.get("status", "unknown"),
                        "result": task.get("result"),
                    }

        #  cancel
        elif action == "cancel":
            if not task_id:
                return {"success": False, "error": "task_id  obrigatrio para cancel."}

            if _task_broker:
                broker_result = _task_broker.cancel_task(task_id)
                return broker_result
            else:
                task = _task_registry.get(task_id)
                if not task:
                    return {
                        "success": False,
                        "error": f"Task no encontrada: {task_id}",
                    }

                if task.get("status") in ("done", "failed"):
                    return {
                        "success": False,
                        "error": f"No  possvel cancelar task com status '{task['status']}'",
                    }

                task["status"] = "cancelled"
                _task_registry[task_id] = task
                return {
                    "success": True,
                    "task_id": task_id,
                    "cancelled": True,
                }

        #  list_queued
        elif action == "list_queued":
            if _task_broker:
                broker_result = _task_broker.list_queued_tasks(port if port else None)
                return broker_result
            else:
                tasks = []
                for _tid, t in _task_registry.items():
                    if t.get("status") == "queued":
                        if not port or t.get("port") == port:
                            tasks.append(t)
                return {
                    "success": True,
                    "tasks": tasks,
                    "total": len(tasks),
                    "port_filter": port if port else "all",
                }

        #  ao desconhecida
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'.",
                "available": ["execute", "poll", "cancel", "list_queued"],
            }
