from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:00.756505'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SVC-FR-005-event-bus
related_ssot:
  - NC-SVC-FR-005
  - NC-TOOL-FR-018-push-notification
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-TOOL-FR-018-push-notification.py
FR-018  MCP Tool: neocortex_push_notification (cannico)

Notificaes push com fallback gracioso para notifypy e integrao ao EventBus.
Absorve funcionalidades de FR-032 e FR-033.

Aes disponveis:
  push.send  envia notificao desktop com ttulo, mensagem e urgency
  push.status  verifica se o recurso est disponvel (notifypy + flag)

Feature flag: KAIROS_PUSH_NOTIFICATION (env var).
Urgency levels: low, normal, high, critical.
Evento publicado: 'notification_sent' via EventBus (NC-SVC-FR-005).
"""


import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Fallback gracioso para notifypy
try:
    from notifypy import Notify

    NOTIFY_AVAILABLE = True
except ImportError:
    NOTIFY_AVAILABLE = False
    logger.warning("notifypy no disponvel. Notificaes push sero silenciosas.")

# Feature flag
KAIROS_PUSH_NOTIFICATION = os.getenv("KAIROS_PUSH_NOTIFICATION", "false").lower() in (
    "true",
    "1",
    "yes",
    "on",
)

# Carga do EventBus (NCSVCFR005) usando spec_from_file_location para mdulos com hfen.
import importlib.util
from pathlib import Path

EVENT_BUS_AVAILABLE = False
NeoCortexEvent = None
_get_event_bus_func = None


def _load_event_bus():
    """Obtm a instncia do EventBus (NCSVCFR005)."""
    try:
        event_bus_path = (
            Path(__file__).parent.parent.parent
            / "core"
            / "services"
            / "NC-SVC-FR-005-event-bus.py"
        )
        if not event_bus_path.exists():
            logger.debug("EventBus module not found.")
            return None
        spec = importlib.util.spec_from_file_location(
            "NC_SVC_FR_005_event_bus", event_bus_path
        )
        if spec is None or spec.loader is None:
            logger.debug("Falha ao criar spec para EventBus.")
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.debug(f"EventBus no disponvel: {e}")
        return None


# Carregar mdulo uma vez
_event_bus_module = _load_event_bus()
if _event_bus_module:
    NeoCortexEvent = getattr(_event_bus_module, "NeoCortexEvent", None)
    _get_event_bus_func = getattr(_event_bus_module, "get_event_bus", None)
    EVENT_BUS_AVAILABLE = bool(_get_event_bus_func and NeoCortexEvent)


def get_event_bus():
    """Retorna instncia do EventBus se disponvel."""
    if _get_event_bus_func:
        return _get_event_bus_func()
    return None


def _publish_notification_sent(
    title: str,
    message: str,
    urgency: str,
    success: bool,
    error: Optional[str] = None,
) -> None:
    """Publica evento 'notification_sent' no EventBus."""
    bus = get_event_bus()
    if bus is None:
        return
    try:
        event = NeoCortexEvent(
            event_type="notification_sent",
            payload={
                "title": title,
                "message": message,
                "urgency": urgency,
                "success": success,
                "error": error,
                "timestamp": datetime.now().isoformat(),
            },
            timestamp=datetime.now(),
            source_tool="neocortex_push_notification",
        )
        bus.publish(event)
        logger.debug(
            f"Evento 'notification_sent' publicado (urgency={urgency}, success={success})"
        )
    except Exception as e:
        logger.debug(f"Falha ao publicar evento notification_sent: {e}")


def _send_notification_internal(
    title: str, message: str, urgency: str = "normal"
) -> Dict[str, Any]:
    """
    Envia notificao desktop usando notifypy (se disponvel e flag ativa).
    Retorna dict com resultado.
    """
    if not KAIROS_PUSH_NOTIFICATION:
        return {
            "sent": False,
            "reason": "feature_flag_disabled",
            "detail": "KAIROS_PUSH_NOTIFICATION est desativada.",
        }

    if not NOTIFY_AVAILABLE:
        return {
            "sent": False,
            "reason": "library_unavailable",
            "detail": "notifypy no est instalado.",
        }

    try:
        notification = Notify()
        notification.title = title
        notification.message = message

        # Mapeamento de urgency para timeout (segundos) e cone (se suportado)
        urgency_config = {
            "low": {"timeout": 3},
            "normal": {"timeout": 5},
            "high": {"timeout": 8},
            "critical": {"timeout": 10},
        }
        config = urgency_config.get(urgency, urgency_config["normal"])
        notification.timeout = config["timeout"]

        # Algumas plataformas suportam urgency via atributo (Linux: urgency level)
        if hasattr(notification, "urgency"):
            # notifypy suporta urgency: 0=low, 1=normal, 2=high, 3=critical
            urgency_map = {"low": 0, "normal": 1, "high": 2, "critical": 3}
            notification.urgency = urgency_map.get(urgency, 1)

        notification.send()
        logger.info(f"Notificao enviada: '{title}' (urgency={urgency})")
        return {"sent": True, "urgency": urgency, "timeout": config["timeout"]}
    except Exception as e:
        logger.error(f"Erro ao enviar notificao: {e}")
        return {"sent": False, "reason": "send_error", "detail": str(e)}


def register_tool(mcp) -> None:
    """Registra neocortex_push_notification no servidor MCP."""

    @mcp.tool(name="neocortex_push_notification")
    def neocortex_push_notification(
        action: str,
        title: str = "",
        message: str = "",
        urgency: str = "normal",
    ) -> Dict[str, Any]:
        """Notificaes push desktop com fallback gracioso.

        Actions: push.send, push.status"""
        timestamp = datetime.now().isoformat()

        #  push.status
        if action == "push.status":
            return {
                "success": True,
                "action": action,
                "timestamp": timestamp,
                "notify_available": NOTIFY_AVAILABLE,
                "feature_flag_enabled": KAIROS_PUSH_NOTIFICATION,
                "push_possible": NOTIFY_AVAILABLE and KAIROS_PUSH_NOTIFICATION,
                "urgency_levels": ["low", "normal", "high", "critical"],
                "event_bus_available": EVENT_BUS_AVAILABLE,
            }

        #  push.send
        elif action == "push.send":
            if not title or not message:
                return {
                    "success": False,
                    "action": action,
                    "timestamp": timestamp,
                    "error": "title e message so obrigatrios.",
                }

            urgency = urgency.lower()
            if urgency not in ("low", "normal", "high", "critical"):
                urgency = "normal"

            # Envia notificao
            send_result = _send_notification_internal(title, message, urgency)
            sent = send_result.get("sent", False)

            # Publica evento no EventBus
            _publish_notification_sent(
                title=title,
                message=message,
                urgency=urgency,
                success=sent,
                error=send_result.get("detail") if not sent else None,
            )

            # Retorna resultado consolidado
            result = {
                "success": True,  # sucesso na operao do tool (no necessariamente no envio)
                "action": action,
                "timestamp": timestamp,
                "title": title,
                "message": message,
                "urgency": urgency,
                **send_result,
            }
            if not sent:
                result["success"] = False
                result["error"] = send_result.get("detail", "unknown error")
            return result

        #  ao desconhecida
        else:
            return {
                "success": False,
                "action": action,
                "timestamp": timestamp,
                "error": f"Ao desconhecida: '{action}'.",
                "available": ["push.send", "push.status"],
            }
