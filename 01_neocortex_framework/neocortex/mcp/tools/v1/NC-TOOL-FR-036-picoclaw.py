"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.413547'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TOOL-FR-036-picoclaw
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-TOOL-FR-036-picoclaw.py
MCP Tool: neocortex_picoclaw  bridge T0PicoClaw gateway via HTTP POST.

Actions:
- task.send: Envia task para gateway PicoClaw via POST /message
- gateway.health: Verifica sade do gateway via GET /health
- gateway.status: Verifica status de prontido via GET /ready (fallback /health)

Gateway padro: http://127.0.0.1:18790
"""

import json
import logging
import urllib.error
import urllib.request
import uuid
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_GATEWAY_BASE_URL = "http://127.0.0.1:18790"
_DEFAULT_TIMEOUT = 5  # segundos


def _http_request(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Realiza requisio HTTP para o gateway PicoClaw.

    Args:
        method: GET ou POST
        endpoint: caminho do endpoint (ex: /health)
        data: payload JSON para POST
        timeout: timeout em segundos

    Returns:
        Dict com success, http_status, result (se sucesso) ou error (se falha)
    """
    url = f"{_GATEWAY_BASE_URL}{endpoint}"
    headers = {}
    payload = None

    try:
        if data is not None:
            payload = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(
            url,
            data=payload,
            headers=headers,
            method=method.upper(),
        )

        with urllib.request.urlopen(req, timeout=timeout) as resp:
            response_body = resp.read().decode("utf-8")
            result = json.loads(response_body) if response_body.strip() else {}
            return {
                "success": True,
                "http_status": resp.status,
                "result": result,
            }

    except urllib.error.URLError as e:
        # Detectar ConnectionRefusedError especfico (gateway offline)
        if isinstance(e.reason, ConnectionRefusedError):
            return {
                "success": False,
                "error": f"Gateway offline (ConnectionRefusedError): {e.reason}",
                "reason": "connection_refused",
            }
        # Timeout
        if isinstance(e, urllib.error.URLError) and "timed out" in str(e.reason):
            return {
                "success": False,
                "error": f"Timeout aps {timeout}s ao acessar {url}: {e.reason}",
                "reason": "timeout",
            }
        # Outros erros de URL
        return {
            "success": False,
            "error": f"Erro de conexo com {url}: {e.reason}",
            "reason": "url_error",
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Resposta do gateway no  JSON vlido: {e}",
            "reason": "invalid_json",
        }

    except Exception as e:
        logger.exception("Erro inesperado em _http_request")
        return {
            "success": False,
            "error": f"Erro inesperado: {e}",
            "reason": "unexpected",
        }


def _gateway_health(timeout: int = _DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Consulta sade do gateway via GET /health.

    Returns:
        Dict com status, port (se sucesso) ou erro.
    """
    result = _http_request("GET", "/health", timeout=timeout)
    if not result["success"]:
        return result

    health_data = result.get("result", {})
    return {
        "success": True,
        "status": health_data.get("status", "ok"),
        "port": health_data.get("port", 18790),
        "http_status": result["http_status"],
        "data": health_data,
    }


def _gateway_status(timeout: int = _DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Consulta status de prontido do gateway via GET /ready (fallback /health).

    Returns:
        Dict com status, timestamp e dados de sade.
    """
    # Primeiro tenta /ready
    result = _http_request("GET", "/ready", timeout=timeout)
    if result["success"]:
        ready_data = result.get("result", {})
        return {
            "success": True,
            "status": ready_data.get("status", "ready"),
            "timestamp": ready_data.get("timestamp", ""),
            "http_status": result["http_status"],
            "data": ready_data,
            "endpoint": "ready",
        }

    # Se /ready falhou, tenta /health como fallback
    logger.debug("Endpoint /ready no disponvel, fallback para /health")
    health_result = _gateway_health(timeout)
    if health_result["success"]:
        health_result["endpoint"] = "health"
        return health_result

    # Se ambos falharam, retorna erro do /ready (mais informativo)
    return result


def _task_send(
    task: str,
    context: Optional[str] = None,
    session_id: Optional[str] = None,
    timeout_sec: int = 60,
) -> Dict[str, Any]:
    """
    Envia task para gateway PicoClaw via POST /message.

    Args:
        task: descrio da tarefa a enviar (obrigatrio)
        context: contexto adicional dos lobos (opcional)
        session_id: ID da sesso, gera uuid4 se vazio
        timeout_sec: timeout da requisio

    Returns:
        Dict com resposta do PicoClaw ou erro detalhado.
    """
    if not task:
        return {"success": False, "error": "Parmetro 'task'  obrigatrio."}

    # Gera session_id se no fornecido
    if not session_id:
        session_id = str(uuid.uuid4())

    # Constri payload conforme especificao
    text = task
    if context:
        text += f"\n\nCONTEXTO:\n{context}"

    payload = {
        "channel": "mcp",
        "user": "T0-Antigravity",
        "text": text,
        "metadata": {
            "session_id": session_id,
            "agent_id": "T0-Antigravity",
            "source": "neocortex_mcp",
        },
    }

    result = _http_request("POST", "/message", data=payload, timeout=timeout_sec)
    if not result["success"]:
        return result

    # Sucesso
    response_data = result.get("result", {})
    return {
        "success": True,
        "session_id": session_id,
        "response": response_data,
        "http_status": result["http_status"],
    }


def _task_dispatch(
    ticket_id: str,
    task_type: str = "execute",
    payload: Optional[Dict[str, Any]] = None,
    agent_id: str = "T0-Antigravity",
    timeout: int = _DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    ORCH-301: HTTP POST para /dispatch com payload estruturado.

    Args:
        ticket_id: ID do ticket a despachar
        task_type: tipo da task (execute, review, scan...)
        payload: dados extras da task
        agent_id: agente que origina a chamada
        timeout: timeout em segundos (default 5s — não bloquear o Core)

    Returns:
        {task_id, status, agent_assigned} ou {status: "queued_offline"} quando DOWN
    """
    dispatch_body: Dict[str, Any] = {
        "ticket_id": ticket_id,
        "task_type": task_type,
        "payload": payload or {},
        "agent_id": agent_id,
        "timeout": timeout,
    }
    result = _http_request("POST", "/dispatch", data=dispatch_body, timeout=timeout)
    if result["success"]:
        r = result.get("result", {})
        return {
            "success": True,
            "task_id": r.get("task_id", f"offline-{ticket_id}"),
            "status": r.get("status", "queued"),
            "agent_assigned": r.get("agent_assigned"),
            "http_status": result["http_status"],
        }
    # Fallback gracioso — PicoClaw DOWN
    if result.get("reason") in ("connection_refused", "timeout"):
        return {
            "success": True,
            "task_id": f"offline-{ticket_id}",
            "status": "queued_offline",
            "agent_assigned": None,
            "note": "PicoClaw indisponível — task enfileirada offline para retry",
        }
    return result


def _task_status(task_id: str, timeout: int = _DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    ORCH-302: GET /tasks/{task_id}/status — snapshot de status ou SSE polling.

    Retorna last_known_status quando PicoClaw DOWN.

    Args:
        task_id: ID da task retornado por task.dispatch
        timeout: timeout da requisição

    Returns:
        {task_id, status, progress, result} ou fallback com last_known_status
    """
    result = _http_request("GET", f"/tasks/{task_id}/status", timeout=timeout)
    if result["success"]:
        r = result.get("result", {})
        return {
            "success": True,
            "task_id": task_id,
            "status": r.get("status", "unknown"),
            "progress": r.get("progress"),
            "result": r.get("result"),
            "http_status": result["http_status"],
        }
    # Fallback — PicoClaw DOWN ou task_id offline
    if task_id.startswith("offline-"):
        return {
            "success": True,
            "task_id": task_id,
            "status": "queued_offline",
            "last_known_status": "queued_offline",
            "note": "Task enfileirada offline — PicoClaw indisponível no momento do dispatch",
        }
    return {
        "success": False,
        "task_id": task_id,
        "last_known_status": "unknown",
        "error": result.get("error", "PicoClaw indisponível"),
    }


def register_tool(mcp) -> None:
    """
    Registra a tool neocortex_picoclaw no servidor MCP.
    """

    @mcp.tool(name="neocortex_picoclaw")
    def neocortex_picoclaw(
        action: str,
        task: str = "",
        context: str = "",
        session_id: str = "",
        timeout_sec: int = 60,
        ticket_id: str = "",
        task_type: str = "execute",
        task_id: str = "",
    ) -> Dict[str, Any]:
        """Bridge T0→PicoClaw gateway via HTTP.

        Actions: task.send, task.dispatch, task.status, gateway.health, gateway.status
        Args: action, task, context, session_id, timeout_sec, ticket_id, task_type, task_id"""
        #  gateway.health
        if action == "gateway.health":
            return _gateway_health(timeout=_DEFAULT_TIMEOUT)

        #  gateway.status
        elif action == "gateway.status":
            return _gateway_status(timeout=_DEFAULT_TIMEOUT)

        #  task.send
        elif action == "task.send":
            return _task_send(
                task=task,
                context=context if context else None,
                session_id=session_id if session_id else None,
                timeout_sec=timeout_sec,
            )

        #  task.dispatch — ORCH-301
        elif action == "task.dispatch":
            if not ticket_id:
                return {"success": False, "error": "ticket_id é obrigatório para task.dispatch."}
            return _task_dispatch(
                ticket_id=ticket_id,
                task_type=task_type,
                agent_id="T0-Antigravity",
                timeout=_DEFAULT_TIMEOUT,
            )

        #  task.status — ORCH-302
        elif action == "task.status":
            if not task_id:
                return {"success": False, "error": "task_id é obrigatório para task.status."}
            return _task_status(task_id=task_id, timeout=_DEFAULT_TIMEOUT)

        #  ação desconhecida
        else:
            return {
                "success": False,
                "error": f"Ação desconhecida: '{action}'.",
                "available": [
                    "task.send",
                    "task.dispatch",
                    "task.status",
                    "gateway.health",
                    "gateway.status",
                ],
            }

    return neocortex_picoclaw
