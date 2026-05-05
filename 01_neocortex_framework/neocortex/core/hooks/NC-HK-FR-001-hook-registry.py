"""---
@Module NC-HK-FR-001-hook-registry mcp _genealogy:   injected_at: '2026-04-16T00:24:02.15
---
"""


"""
NC-HK-FR-001-hook-registry.py
FR-HK-001  HookRegistry: Sistema de hooks reativos ps-ao para NeoCortex.

Suporta hooks YAML (declarativos) e Python (programticos).
Eventos: PreToolUse, PostToolUse, ToolError (padro MCP).
"""

import concurrent.futures
import importlib.util
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

logger = logging.getLogger(__name__)


class HookEvent(StrEnum):
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    TOOL_ERROR = "ToolError"


@dataclass
class HookDefinition:
    """Definio de um hook (YAML ou Python)."""

    name: str
    event: HookEvent
    handler: Callable  # funo Python
    timeout_seconds: float = 2.0
    enabled: bool = True
    metadata: dict = field(default_factory=dict)


class HookRegistry:
    """Registry de hooks reativos para eventos de tools MCP.

    Interface pblica:
      register(name, event, handler, timeout, enabled) -> None
      unregister(name) -> bool
      trigger(event, context) -> List[Dict]   # executa todos hooks do evento
      load_yaml(path) -> int                  # carrega hooks de arquivo YAML
      list_hooks(event=None) -> List[str]
    """

    def __init__(self):
        self._hooks: dict[str, HookDefinition] = {}
        self._lock = threading.Lock()
        self._executor = concurrent.futures.ThreadPoolExecutor()
        self._yaml = YAML()

    def register(
        self,
        name: str,
        event: HookEvent,
        handler: Callable,
        timeout_seconds: float = 2.0,
        enabled: bool = True,
    ) -> None:
        """Registra um hook Python."""
        with self._lock:
            if name in self._hooks:
                logger.warning(f"Hook '{name}' j registrado. Substituindo.")
            hook_def = HookDefinition(
                name=name,
                event=event,
                handler=handler,
                timeout_seconds=timeout_seconds,
                enabled=enabled,
            )
            self._hooks[name] = hook_def
        logger.info(f"Hook registrado: {name} para evento {event.value}")

    def unregister(self, name: str) -> bool:
        """Remove um hook. Retorna True se existia."""
        with self._lock:
            existed = name in self._hooks
            if existed:
                del self._hooks[name]
                logger.info(f"Hook removido: {name}")
            return existed

    def trigger(self, event: HookEvent, context: dict[str, Any]) -> list[dict]:
        """Dispara todos os hooks do evento. Timeout por hook: 2s.

        Returns:
            Lista de resultados [{name, status, result/error, duration_ms}]
        """
        hooks_to_run = []
        with self._lock:
            for hook in self._hooks.values():
                if hook.event == event and hook.enabled:
                    hooks_to_run.append(hook)
        if not hooks_to_run:
            logger.debug(f"Nenhum hook habilitado para evento {event.value}")
            return []

        logger.info(f"Disparando {len(hooks_to_run)} hooks para evento {event.value}")
        results = []
        for hook in hooks_to_run:
            result = self._execute_hook(hook, context)
            results.append(result)

        self._publish_hook_triggered(event, context, results)
        return results

    def _execute_hook(self, hook: HookDefinition, context: dict[str, Any]) -> dict:
        """Executa um hook individual com timeout."""
        import time

        start = time.perf_counter()
        hook_name = hook.name
        try:
            future = self._executor.submit(hook.handler, **context)
            result = future.result(timeout=hook.timeout_seconds)
            status = "success"
            error = None
        except concurrent.futures.TimeoutError:
            status = "timeout"
            result = None
            error = f"Timeout aps {hook.timeout_seconds}s"
            logger.warning(f"Hook {hook_name} timeout")
        except Exception as e:
            status = "error"
            result = None
            error = str(e)
            logger.error(f"Hook {hook_name} erro: {e}", exc_info=True)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"Hook {hook_name} executado em {duration_ms:.2f}ms, status: {status}"
        )
        return {
            "name": hook_name,
            "status": status,
            "result": result,
            "error": error,
            "duration_ms": duration_ms,
        }

    def load_yaml(self, path: Path) -> int:
        """Carrega hooks de um arquivo YAML. Retorna N hooks carregados."""
        if not path.exists():
            logger.warning(f"Arquivo de hooks no encontrado: {path}")
            return 0
        try:
            data = self._yaml.load(path)
        except Exception as e:
            logger.error(f"Erro ao carregar YAML {path}: {e}")
            return 0
        hooks = data.get("hooks", [])
        count = 0
        for hook_def in hooks:
            name = hook_def.get("name")
            event_str = hook_def.get("event")
            script_path = hook_def.get("script")
            enabled = hook_def.get("enabled", True)
            if not name or not event_str or not script_path:
                logger.warning(f"Definio de hook incompleta: {hook_def}")
                continue
            try:
                event = HookEvent(event_str)
            except ValueError:
                logger.warning(f"Evento invlido: {event_str}")
                continue
            script_path = Path(script_path)
            if not script_path.is_absolute():
                script_path = path.parent / script_path
            handler = self._load_handler_from_script(script_path)
            if handler is None:
                continue
            self.register(name, event, handler, enabled=enabled)
            count += 1
        logger.info(f"Carregados {count} hooks de {path}")
        return count

    def _load_handler_from_script(self, script_path: Path) -> Callable | None:
        """Carrega uma funo de um script Python usando importlib."""
        if not script_path.exists():
            logger.error(f"Script no encontrado: {script_path}")
            return None
        try:
            spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
            if spec is None or spec.loader is None:
                logger.error(f"No foi possvel criar spec para {script_path}")
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            handler = getattr(module, "hook_handler", None)
            if handler is None:
                logger.error(f"Script {script_path} no define funo 'hook_handler'")
                return None
            return handler
        except Exception as e:
            logger.error(f"Erro ao carregar script {script_path}: {e}")
            return None

    def list_hooks(self, event: HookEvent | None = None) -> list[str]:
        """Lista nomes de hooks registrados (filtrado por evento se fornecido)."""
        with self._lock:
            if event is None:
                return list(self._hooks.keys())
            return [name for name, hook in self._hooks.items() if hook.event == event]

    def _publish_hook_triggered(
        self, event: HookEvent, context: dict[str, Any], results: list[dict]
    ) -> None:
        """Publica evento HOOK_TRIGGERED no EventBus."""
        try:
            event_bus = self._get_event_bus()
            event_bus.publish(
                self._create_neocortex_event(
                    event_type="HOOK_TRIGGERED",
                    payload={
                        "event": event.value,
                        "context": context,
                        "results": results,
                    },
                    source_tool="HookRegistry",
                )
            )
        except Exception as e:
            logger.warning(f"Falha ao publicar HOOK_TRIGGERED no EventBus: {e}")

    def _get_event_bus(self):
        """Carrega dinamicamente o EventBus."""
        if not hasattr(self, "_event_bus_instance"):
            spec = importlib.util.spec_from_file_location(
                "event_bus",
                Path(__file__).parent.parent
                / "services"
                / "NC-SVC-FR-005-event-bus.py",
            )
            if spec is None or spec.loader is None:
                raise ImportError("Failed to load event bus module")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._event_bus_instance = module.get_event_bus()
        return self._event_bus_instance

    def _create_neocortex_event(self, event_type: str, payload: Any, source_tool: str):
        """Cria um NeoCortexEvent."""
        spec = importlib.util.spec_from_file_location(
            "event_bus",
            Path(__file__).parent.parent / "services" / "NC-SVC-FR-005-event-bus.py",
        )
        if spec is None or spec.loader is None:
            raise ImportError("Failed to load event bus module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        NeoCortexEvent = module.NeoCortexEvent
        return NeoCortexEvent(
            event_type=event_type,
            payload=payload,
            timestamp=datetime.now(),
            source_tool=source_tool,
        )
        if spec is None:
            raise ImportError("Failed to load event bus module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        NeoCortexEvent = module.NeoCortexEvent
        return NeoCortexEvent(
            event_type=event_type,
            payload=payload,
            timestamp=datetime.now(),
            source_tool=source_tool,
        )


_hook_registry: HookRegistry | None = None


def get_hook_registry() -> HookRegistry:
    """Singleton do HookRegistry."""
    global _hook_registry
    if _hook_registry is None:
        _hook_registry = HookRegistry()
    return _hook_registry
