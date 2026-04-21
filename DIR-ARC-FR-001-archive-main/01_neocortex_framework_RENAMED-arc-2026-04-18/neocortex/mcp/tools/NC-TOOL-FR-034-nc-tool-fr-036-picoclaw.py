"""---
domain: "orchestration"
layer: "core"
type: "service"
tags: ["tool", "036", "picoclaw"]
hash: "auto-generated"
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
    ) -> Dict[str, Any]:
        """
        Bridge T0PicoClaw gateway via HTTP.

        Actions:
        - task.send: Envia task para gateway PicoClaw via POST /message
        - gateway.health: Verifica sade do gateway via GET /health
        - gateway.status: Verifica status de prontido via GET /ready (fallback /health)

        Args:
            action: ao desejada (task.send, gateway.health, gateway.status)
            task: descrio da tarefa (para task.send)
            context: contexto adicional dos lobos (para task.send)
            session_id: ID da sesso (para task.send)
            timeout_sec: timeout da requisio (default 60s para task.send, 5s para health/status)
        """
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

        #  ao desconhecida
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'.",
                "available": ["task.send", "gateway.health", "gateway.status"],
            }

    return neocortex_picoclaw
