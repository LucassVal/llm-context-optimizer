"""
NC-TOOL-FR-033-push-notification.py
MCP Tool: Envia notificaes push via notifypy com fallback gracioso.

Actions: push.send | push.status
Integra com NC-SVC-FR-005-event-bus.py (publicar evento POST_NOTIFICATION).
Feature flag: KAIROS_PUSH_NOTIFICATION (env var, default=False).
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)

KAIROS_PUSH = os.getenv("KAIROS_PUSH_NOTIFICATION", "false").lower() in (
    "true",
    "1",
    "yes",
)

# Tenta importar notifypy com fallback
notifypy = None
try:
    import notifypy

    NOTIFYPY_AVAILABLE = True
except ImportError:
    NOTIFYPY_AVAILABLE = False
    notifypy = None
    logger.warning("notifypy no instalado  notificaes push desabilitadas")

# Importar EventBus para publicar evento NOTIFICATION_SENT via importlib (mdulo com hfen)
import importlib.util
from pathlib import Path

EVENT_BUS_AVAILABLE = False
NOTIFICATION_SENT = "notification_sent"
NeoCortexEvent = None
_get_event_bus_func = None


def _load_event_bus():
    """Obtm a instncia do EventBus (NCSVCFR005) usando spec_from_file_location para mdulos com hfen."""
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
    NOTIFICATION_SENT = getattr(
        _event_bus_module, "NOTIFICATION_SENT", "notification_sent"
    )
    NeoCortexEvent = getattr(_event_bus_module, "NeoCortexEvent", None)
    _get_event_bus_func = getattr(_event_bus_module, "get_event_bus", None)
    EVENT_BUS_AVAILABLE = bool(_get_event_bus_func and NeoCortexEvent)


def get_event_bus():
    """Retorna instncia do EventBus se disponvel."""
    if _get_event_bus_func:
        return _get_event_bus_func()
    return None


def register_tool(server) -> None:
    """Registra tool no servidor MCP."""

    @server.tool()
    async def push_notification(
        action: str, title: str = "", message: str = "", urgency: str = "normal"
    ) -> Dict[str, Any]:
        """Envia notificao push desktop (ao: push.send | push.status).

        - push.send: Envia notificao via notifypy. Requer KAIROS_PUSH_NOTIFICATION=true.
        - push.status: Retorna disponibilidade sem enviar.
        """
        # Ao push.status: retorna status atual
        if action == "push.status":
            return {
                "sent": False,
                "action": "push.status",
                "available": NOTIFYPY_AVAILABLE,
                "kairos_push_enabled": KAIROS_PUSH,
                "event_bus_available": EVENT_BUS_AVAILABLE,
                "message": "Status da funcionalidade de notificao push",
            }

        # Ao push.send: enviar notificao
        if action != "push.send":
            return {
                "sent": False,
                "action": action,
                "error": f"Ao desconhecida: '{action}'. Use 'push.send' ou 'push.status'",
            }

        # Verificar feature flag
        if not KAIROS_PUSH:
            return {
                "sent": False,
                "action": "push.send",
                "reason": "feature_flag_disabled",
                "message": "KAIROS_PUSH_NOTIFICATION est desabilitado",
            }

        # Verificar notifypy disponvel
        if not NOTIFYPY_AVAILABLE:
            return {
                "sent": False,
                "action": "push.send",
                "reason": "notifypy_not_installed",
                "message": "notifypy no est instalado  no  possvel enviar notificaes",
            }

        # Validar ttulo e mensagem
        if not title and not message:
            return {
                "sent": False,
                "action": "push.send",
                "error": "Pelo menos um de 'title' ou 'message' deve ser fornecido",
            }

        try:
            # Criar notificao
            assert notifypy is not None
            notification = notifypy.Notify()
            notification.title = title or "NeoCortex"
            notification.message = message or "Notificao"
            notification.urgency = urgency  # low, normal, critical

            # Enviar
            notification.send()
            logger.info(f"Notificao push enviada: {title} - {message}")

            # Publicar evento NOTIFICATION_SENT se EventBus disponvel
            if EVENT_BUS_AVAILABLE:
                assert NeoCortexEvent is not None
                assert _get_event_bus_func is not None
                event = NeoCortexEvent(
                    event_type=NOTIFICATION_SENT,
                    payload={
                        "title": title,
                        "message": message,
                        "urgency": urgency,
                        "sent_at": datetime.now().isoformat(),
                    },
                    timestamp=datetime.now(),
                    source_tool="push_notification",
                )
                _get_event_bus_func().publish(event)
                logger.debug("Evento NOTIFICATION_SENT publicado")

            return {
                "sent": True,
                "action": "push.send",
                "title": title,
                "message": message,
                "urgency": urgency,
            }

        except Exception as e:
            logger.error(f"Erro ao enviar notificao push: {e}")
            return {
                "sent": False,
                "action": "push.send",
                "error": str(e),
                "message": "Falha ao enviar notificao push",
            }
