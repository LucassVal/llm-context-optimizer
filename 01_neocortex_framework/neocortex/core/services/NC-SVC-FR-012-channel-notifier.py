"""---
@Module NC-SVC-FR-012-channel-notifier mcp _genealogy:   injected_at: '2026-04-16T00:23:58.97
---
"""


"""
NC-SVC-FR-012-channel-notifier.py
FR-012  ChannelNotifier: Sistema de canais de notificao para NeoCortex.

Roteador de notificaes por canal (log, console, eventbus).
Feature flag: KAIROS_CHANNELS (env var, default=False).
Integra com EventBus (NC-SVC-FR-005) para publicar eventos de notificao.

Restriction: server.py, sub_server.py are @LOCKS.
This module is a standalone service that can be imported by any module.
"""

import importlib
import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

# Dynamic import for hyphenated module name (EventBus)
spec = importlib.util.spec_from_file_location(
    "event_bus", Path(__file__).parent / "NC-SVC-FR-005-event-bus.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
get_event_bus = module.get_event_bus
NeoCortexEvent = module.NeoCortexEvent


logger = logging.getLogger(__name__)


# Optional rich import for colored console output
try:
    from rich.console import Console
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class ChannelNotifier:
    """Roteador de notificaes por canal.

    Canais disponveis: log, console, eventbus
    Extendvel via register_channel().
    """

    _instance: Optional["ChannelNotifier"] = None
    _lock: threading.Lock

    # Feature flag
    KAIROS_CHANNELS = os.getenv("KAIROS_CHANNELS", "false").lower() in (
        "true",
        "1",
        "yes",
    )

    def __new__(cls) -> "ChannelNotifier":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._lock = threading.Lock()
            cls._instance._channels: Dict[str, Callable] = {}
            cls._instance._event_bus = get_event_bus()
            cls._instance._register_default_channels()
        return cls._instance

    def _register_default_channels(self) -> None:
        """Registra os canais padro (log, console, eventbus)."""
        # Canal "log"  usa logger do Python
        self.register_channel("log", self._log_channel)
        # Canal "console"  output colorido (rich) ou simples
        self.register_channel("console", self._console_channel)
        # Canal "eventbus"  publica evento no EventBus
        self.register_channel("eventbus", self._eventbus_channel)

    def _log_channel(
        self, message: str, level: str = "info", metadata: Dict = None
    ) -> Dict:
        """Handler do canal 'log'  escreve no logger."""
        log_method = getattr(logger, level.lower(), logger.info)
        extra = {"metadata": metadata} if metadata else {}
        log_method(message, extra=extra)
        return {"status": "logged", "level": level}

    def _console_channel(
        self, message: str, level: str = "info", metadata: Dict = None
    ) -> Dict:
        """Handler do canal 'console'  output colorido ou simples."""
        if not self.KAIROS_CHANNELS:
            # Fallback: apenas log
            return self._log_channel(message, level, metadata)

        if RICH_AVAILABLE:
            console = Console()
            color_map = {
                "info": "green",
                "warning": "yellow",
                "error": "red",
                "critical": "bold red",
                "debug": "blue",
            }
            color = color_map.get(level, "white")
            text = Text(message, style=color)
            console.print(text)
        else:
            # Fallback para print simples com prefixo de nvel
            prefix = f"[{level.upper()}]"
            print(f"{prefix} {message}")

        return {"status": "printed", "level": level, "rich_used": RICH_AVAILABLE}

    def _eventbus_channel(
        self, message: str, level: str = "info", metadata: Dict = None
    ) -> Dict:
        """Handler do canal 'eventbus'  publica evento 'channel.notification'."""
        if not self.KAIROS_CHANNELS:
            # Fallback: apenas log
            return self._log_channel(message, level, metadata)

        payload = {
            "message": message,
            "level": level,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
        event = NeoCortexEvent(
            event_type="channel.notification",
            payload=payload,
            timestamp=datetime.now(),
            source_tool="ChannelNotifier",
        )
        self._event_bus.publish(event)
        return {"status": "published", "event_type": "channel.notification"}

    def notify(
        self, channel: str, message: str, level: str = "info", metadata: Dict = None
    ) -> Dict:
        """Envia uma notificao para um canal especfico.

        Args:
            channel: Nome do canal (ex.: "log", "console", "eventbus").
            message: Mensagem a ser notificada.
            level: Nvel de severidade ("info", "warning", "error", "debug", "critical").
            metadata: Dicionrio opcional com metadados adicionais.

        Returns:
            Dicionrio com resultado da operao.
        """
        if metadata is None:
            metadata = {}

        with self._lock:
            handler = self._channels.get(channel)
            if handler is None:
                return {"error": f"Canal '{channel}' no registrado."}

        try:
            result = handler(message, level, metadata)
            result["channel"] = channel
            return result
        except Exception as e:
            logger.error(f"Erro no canal '{channel}': {e}")
            return {"error": str(e), "channel": channel}

    def register_channel(self, name: str, handler: Callable) -> None:
        """Registra um novo canal de notificao.

        Args:
            name: Nome do canal.
            handler: Funo que aceita (message: str, level: str, metadata: Dict) -> Dict.
        """
        with self._lock:
            self._channels[name] = handler
        logger.debug(f"Canal '{name}' registrado.")

    def list_channels(self) -> List[str]:
        """Retorna lista de canais registrados.

        Returns:
            Lista de nomes de canais.
        """
        with self._lock:
            return list(self._channels.keys())


def get_channel_notifier() -> ChannelNotifier:
    """Retorna a instncia singleton do ChannelNotifier."""
    return ChannelNotifier()
