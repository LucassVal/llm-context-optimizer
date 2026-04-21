from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:00.960891'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SVC-FR-015
related_ssot:
  - NC-SVC-FR-015-task-broker
  - NC-TOOL-FR-023-orchestration
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-TOOL-FR-023-orchestration.py
FR-023  MCP Tool: neocortex_orchestration

Orquestrao de agentes efmeros e tasks via HTTP.
Aes disponveis:
  agent.spawn        inicia sub-servidor efmero via neocortex_subserver (HTTP, no stdio)
  agent.heartbeat    verifica status de agente em execuo
  agent.consume      consome resultado de agente efmero
  agent.list_ephemeral  lista agentes efmeros ativos
  task.execute       envia task para sub-servidor via HTTP POST /task
  task.get_result    recupera resultado de task executada
  peers.discover     descobre instncias NeoCortex disponveis na rede local
"""


import importlib.util
import json
import logging
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Task broker singleton (compatible with NC-SVC-FR-015)
_task_broker = None
try:
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

# Fallback in-memory registry
_task_registry: Dict[str, Dict[str, Any]] = {}


def _config():
    try:
        from neocortex.config import get_config

        return get_config()
    except Exception:
        return None


def _get_default_ports() -> Dict[str, int]:
    """Retorna mapeamento role->porta a partir da configurao."""
    cfg = _config()
    if cfg and hasattr(cfg, "agent_ports"):
        return cfg.agent_ports
    # Fallback padro
    return {
        "courier": 8767,
        "engineer": 8768,
        "guardian": 8769,
    }


# Registry de sub-servers ativos (port -> info)
_active_subservers: Dict[int, Dict[str, Any]] = {}


def _spawn_subserver(
    port: int, lobe_dir: str, tools: str, role: str = "courier"
) -> Dict[str, Any]:
    """Inicia um sub-servidor MCP isolado."""
    if port in _active_subservers:
        return {"success": False, "error": f"Porta {port} j em uso"}

    lobe_path = Path(lobe_dir)
    if not lobe_path.exists():
        return {"success": False, "error": f"Diretrio lobe no encontrado: {lobe_dir}"}

    script_path = Path(__file__).parent.parent / "sub_server.py"
    if not script_path.exists():
        return {
            "success": False,
            "error": f"Script sub_server no encontrado: {script_path}",
        }

    cmd = [
        "python",
        str(script_path),
        "--port",
        str(port),
        "--lobe-dir",
        lobe_dir,
        "--tools",
        tools,
        "--role",
        role,
        "--http-port",
        str(port),
    ]

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )
        time.sleep(2)  # aguarda inicializao

        if proc.poll() is not None:
            stdout, stderr = proc.communicate(timeout=1)
            return {
                "success": False,
                "error": f"Sub-servidor falhou ao iniciar: {stderr}",
                "stdout": stdout,
            }

        _active_subservers[port] = {
            "process": proc,
            "lobe_dir": lobe_dir,
            "tools": tools.split(",") if tools else [],
            "role": role,
            "http_port": port,
            "start_time": time.time(),
        }

        return {
            "success": True,
            "message": f"Sub-servidor '{role}' iniciado na porta {port}",
            "port": port,
            "role": role,
            "pid": proc.pid,
            "http_endpoint": f"http://127.0.0.1:{port}/task",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _http_health(host: str, port: int, timeout: int = 3) -> Dict[str, Any]:
    """Faz GET /health em um sub-servidor."""
    url = f"http://{host}:{port}/health"
    try:
        req = urllib.request.urlopen(url, timeout=timeout)
        data = json.loads(req.read().decode())
        return {"reachable": True, "status": data.get("status", "ok"), "data": data}
    except urllib.error.URLError as e:
        return {"reachable": False, "error": str(e.reason)}
    except Exception as e:
        return {"reachable": False, "error": str(e)}


def _send_task(port: int, task_data: str) -> Dict[str, Any]:
    """Envia task para sub-servidor via HTTP POST /task."""
    if port not in _active_subservers:
        return {"success": False, "error": f"Nenhum sub-servidor na porta {port}"}

    server_info = _active_subservers[port]
    http_port = server_info.get("http_port", port)
    url = f"http://127.0.0.1:{http_port}/task"

    try:
        task_dict = json.loads(task_data) if task_data else {}
    except json.JSONDecodeError:
        return {"success": False, "error": "JSON invlido em task_data"}

    payload = json.dumps(task_dict).encode("utf-8")

    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            response_body = resp.read().decode("utf-8")
            result = json.loads(response_body)
            return {
                "success": True,
                "port": port,
                "role": server_info.get("role", "unknown"),
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


_PICOCLAW_BASE = "http://localhost:18790"
_PICOCLAW_TIMEOUT = 5  # segundos — não bloquear o Core


def _send_task_picoclaw(
    ticket_id: str,
    task_type: str,
    payload: Dict[str, Any],
    agent_id: str = "T0-Antigravity",
    timeout: int = _PICOCLAW_TIMEOUT,
) -> Dict[str, Any]:
    """
    ORCH-301: HTTP POST real para PicoClaw :18790/dispatch.

    Args:
        ticket_id: ID do ticket a despachar
        task_type: tipo da task (ex: "execute", "review", "scan")
        payload: dados da task
        agent_id: agente que origina a chamada
        timeout: timeout em segundos (default: 5s)

    Returns:
        {task_id, status, agent_assigned} em caso de sucesso
        {status: "queued_offline", ...} como fallback gracioso quando PicoClaw DOWN
    """
    dispatch_payload = {
        "ticket_id": ticket_id,
        "task_type": task_type,
        "payload": payload,
        "agent_id": agent_id,
        "timeout": timeout,
    }

    body = json.dumps(dispatch_payload).encode("utf-8")
    url = f"{_PICOCLAW_BASE}/dispatch"

    try:
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return {
                "success": True,
                "task_id": result.get("task_id", str(uuid.uuid4())),
                "status": result.get("status", "queued"),
                "agent_assigned": result.get("agent_assigned", "unknown"),
                "picoclaw_response": result,
            }

    except (urllib.error.URLError, OSError):
        # Fallback gracioso — PicoClaw DOWN, encfileira localmente
        offline_task_id = f"offline-{ticket_id}-{uuid.uuid4().hex}"
        _task_registry[offline_task_id] = {
            "task_id": offline_task_id,
            "ticket_id": ticket_id,
            "task_type": task_type,
            "payload": payload,
            "agent_id": agent_id,
            "status": "queued_offline",
            "created_at": time.time(),
        }
        logger.warning(
            "PicoClaw DOWN em %s — task %s enfileirada offline", url, offline_task_id
        )
        return {
            "success": True,
            "task_id": offline_task_id,
            "status": "queued_offline",
            "agent_assigned": None,
            "note": "PicoClaw indisponível — task enfileirada localmente para retry",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def _get_peers_service():
    """Obtm servio de peers."""
    try:
        from neocortex.core import get_peers_service

        return get_peers_service()
    except Exception:
        return None


def register_tool(mcp) -> None:
    """Registra neocortex_orchestration no servidor MCP."""

    @mcp.tool(name="neocortex_orchestration")
    def neocortex_orchestration(
        action: str,
        port: int = 0,
        lobe_dir: str = "",
        tools: str = "",
        role: str = "courier",
        task_data: str = "",
        task_id: str = "",
    ) -> Dict[str, Any]:
        """Orquestração de agentes efêmeros e tasks via HTTP.

        Actions: agent.spawn, agent.heartbeat, agent.consume, agent.list_ephemeral,
                 task.execute, task.get_result, task.cancel, dispatch.create
        """
        #  agent.spawn
        if action == "agent.spawn":
            if not port or not lobe_dir:
                return {
                    "success": False,
                    "error": "Porta e lobe_dir so obrigatrios para spawn.",
                }
            return _spawn_subserver(port, lobe_dir, tools, role)

        #  agent.heartbeat
        elif action == "agent.heartbeat":
            if not port:
                # se no fornecer porta, usa porta padro da role
                ports = _get_default_ports()
                if role not in ports:
                    return {
                        "success": False,
                        "error": f"Role '{role}' desconhecida. Use: {list(ports.keys())}",
                    }
                port = ports[role]
            result = _http_health("localhost", port)
            return {
                "success": True,
                "action": action,
                "port": port,
                "role": role,
                "reachable": result.get("reachable", False),
                "status": result.get("status", "unknown"),
                "error": result.get("error"),
            }

        #  agent.consume
        elif action == "agent.consume":
            if not port:
                return {"success": False, "error": "Porta  obrigatria para consume."}
            # Consumir resultado de agente efmero: para simplificar, envia uma task vazia e retorna resultado
            # Esta ao pode ser expandida para consumir resultados especficos
            return _send_task(port, "{}")

        #  agent.list_ephemeral
        elif action == "agent.list_ephemeral":
            servers = []
            for p, info in _active_subservers.items():
                proc = info["process"]
                servers.append(
                    {
                        "port": p,
                        "pid": proc.pid,
                        "role": info.get("role", "unknown"),
                        "lobe_dir": info["lobe_dir"],
                        "tools": info["tools"],
                        "running": proc.poll() is None,
                        "http_endpoint": f"http://127.0.0.1:{info.get('http_port', p)}/task",
                        "uptime_seconds": round(time.time() - info["start_time"], 1),
                    }
                )
            return {
                "success": True,
                "action": action,
                "servers": servers,
                "total": len(servers),
            }

        #  task.execute
        elif action == "task.execute":
            if not port:
                return {
                    "success": False,
                    "error": "Porta  obrigatria para task.execute.",
                }
            if not task_data:
                return {"success": False, "error": "task_data  obrigatrio."}

            try:
                task_dict = json.loads(task_data) if task_data else {}
            except json.JSONDecodeError:
                return {"success": False, "error": "JSON invlido em task_data"}

            # Generate task ID
            task_id = str(uuid.uuid4())
            task_dict["task_id"] = task_id

            # Determine subserver role (from active_subservers if known)
            role = "unknown"
            if port in _active_subservers:
                role = _active_subservers[port].get("role", "unknown")

            # Register task in broker or inmemory registry
            if _task_broker:
                broker_result = _task_broker.register_task(
                    task_id=task_id,
                    port=port,
                    task_data=task_dict,
                    timeout_seconds=30,
                    subserver_role=role,
                )
                if not broker_result.get("success"):
                    return broker_result
            else:
                _task_registry[task_id] = {
                    "task_id": task_id,
                    "port": port,
                    "role": role,
                    "status": "queued",
                    "created_at": time.time(),
                    "data": task_dict,
                    "result": None,
                }

            # Send task via HTTP
            http_result = _send_task(port, json.dumps(task_dict))
            if not http_result.get("success"):
                # Mark as failed
                if _task_broker:
                    _task_broker.update_task_status(task_id, "failed", http_result)
                else:
                    _task_registry[task_id]["status"] = "failed"
                    _task_registry[task_id]["result"] = http_result
                return http_result

            # Success: update status to done with result
            if _task_broker:
                _task_broker.update_task_status(
                    task_id, "done", http_result.get("result")
                )
            else:
                _task_registry[task_id]["status"] = "done"
                _task_registry[task_id]["result"] = http_result.get("result")

            return {
                "success": True,
                "task_id": task_id,
                "status": "queued",
                "endpoint": f"http://127.0.0.1:{port}/task",
                "http_result": http_result,
            }

        #  task.get_result
        elif action == "task.get_result":
            if not task_id:
                return {
                    "success": False,
                    "error": "task_id  obrigatrio para task.get_result.",
                }

            if _task_broker:
                broker_result = _task_broker.get_task_status(task_id)
                if broker_result.get("success"):
                    return {
                        "success": True,
                        "action": action,
                        "task_id": task_id,
                        "status": broker_result.get("status", "unknown"),
                        "result": broker_result.get("result"),
                        "retrieved_at": time.time(),
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
                return {
                    "success": True,
                    "action": action,
                    "task_id": task_id,
                    "status": task.get("status", "unknown"),
                    "result": task.get("result"),
                    "retrieved_at": time.time(),
                }

        #  task.dispatch — ORCH-301: HTTP POST real para PicoClaw :18790/dispatch
        elif action == "task.dispatch":
            t_id = task_data  # reutiliza campo: ticket_id
            if not t_id:
                return {"success": False, "error": "task_data deve conter o ticket_id para task.dispatch."}
            try:
                extra = json.loads(task_id) if task_id else {}  # task_id reutilizado como JSON extra
            except json.JSONDecodeError:
                extra = {}
            return _send_task_picoclaw(
                ticket_id=t_id,
                task_type=role or "execute",
                payload=extra,
                agent_id="T0-Antigravity",
                timeout=_PICOCLAW_TIMEOUT,
            )

        #  peers.discover
        elif action == "peers.discover":
            service = _get_peers_service()
            if service is None:
                return {"success": False, "error": "Servio de peers indisponvel."}
            try:
                result = service.discover()
                return {"success": True, "action": action, "peers": result}
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  dispatch.create — T-14: gera YAML formal de dispatch (R24)
        elif action == "dispatch.create":
            from datetime import datetime, timezone
            from pathlib import Path
            cfg = _config()
            if cfg is None:
                return {"success": False, "error": "Config indisponível para dispatch.create"}
            ticket_id_arg = task_data or f"NC-DS-AGT-{uuid.uuid4().hex[:6].upper()}"
            task_type_arg = role or "execute"
            payload_arg: Dict[str, Any] = {}
            if task_id:
                try:
                    payload_arg = json.loads(task_id)
                except Exception:
                    payload_arg = {"raw": task_id}
            dispatch_content = {
                "ticket_id": ticket_id_arg,
                "task_type": task_type_arg,
                "agent_role": f"T1-{task_type_arg}",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "created_by": "T0-Antigravity",
                "status": "OPEN",
                "payload": payload_arg,
            }
            tickets_dir = Path(cfg.project_root) / "DIR-DS-001-tickets"
            tickets_dir.mkdir(parents=True, exist_ok=True)
            dispatch_filename = f"NC-DS-AGT-{ticket_id_arg}-dispatch.yaml"
            dispatch_path = tickets_dir / dispatch_filename
            try:
                import yaml as _yaml
                with open(dispatch_path, "w", encoding="utf-8") as fh:
                    _yaml.dump(dispatch_content, fh, allow_unicode=True, sort_keys=False)
                return {
                    "success": True,
                    "action": action,
                    "path": str(dispatch_path),
                    "ticket_id": ticket_id_arg,
                    "yaml_content": dispatch_content,
                }
            except ImportError:
                import json as _json
                dispatch_path_json = dispatch_path.with_suffix(".json")
                with open(dispatch_path_json, "w", encoding="utf-8") as fh:
                    _json.dump(dispatch_content, fh, indent=2, ensure_ascii=False)
                return {
                    "success": True,
                    "action": action,
                    "path": str(dispatch_path_json),
                    "ticket_id": ticket_id_arg,
                    "note": "yaml não disponível — salvo como JSON",
                }
            except Exception as exc:
                return {"success": False, "error": str(exc)}


        #  ao desconhecida
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'.",
                "available": [
                    "agent.spawn",
                    "agent.heartbeat",
                    "agent.consume",
                    "agent.list_ephemeral",
                    "task.execute",
                    "task.get_result",
                    "peers.discover",
                ],
            }
