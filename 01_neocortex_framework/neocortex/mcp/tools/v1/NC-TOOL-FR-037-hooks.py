from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.459662'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-HK-FR-002-simple-hook
related_ssot:
  - NC-HK-FR-001-hook-registry
  - NC-TOOL-FR-037-hooks
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-TOOL-FR-037-hooks.py
FR-037  MCP Tool: neocortex_hooks

Expe o HookRegistry como ferramenta chamvel via MCP.

Aes disponveis:
  hook.register    registra hook pr-fabricado por nome (logging, timing, ratelimit, audit)
  hook.unregister  remove hook de um evento por nome
  hook.trigger     trigera manualmente um evento com payload
  hook.list        lista todos os eventos e hooks registrados
  hook.stats       retorna estatsticas de timing por tool (via TimingHook)

Singleton: o HookRegistry  um singleton; LoggingHook e TimingHook so registrados automaticamente.
"""


import importlib.util
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Importao dinmica do HookRegistry e hooks simples
# -----------------------------------------------------------------------------


def _import_hook_registry():
    """Importa HookRegistry de NC-HK-FR-001-hook-registry.py."""
    hooks_dir = Path(__file__).parent.parent.parent / "core" / "hooks"
    registry_path = hooks_dir / "NC-HK-FR-001-hook-registry.py"
    if not registry_path.exists():
        logger.error(f"HookRegistry no encontrado em {registry_path}")
        return None
    try:
        spec = importlib.util.spec_from_file_location("hook_registry", registry_path)
        if spec is None or spec.loader is None:
            logger.error("Falha ao criar spec para HookRegistry")
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Erro ao importar HookRegistry: {e}")
        return None


def _import_simple_hooks():
    """Importa hooks pr-fabricados de NC-HK-FR-002-simple-hook.py."""
    hooks_dir = Path(__file__).parent.parent.parent / "core" / "hooks"
    simple_path = hooks_dir / "NC-HK-FR-002-simple-hook.py"
    if not simple_path.exists():
        logger.error(f"Hooks simples no encontrados em {simple_path}")
        return None
    try:
        spec = importlib.util.spec_from_file_location("simple_hooks", simple_path)
        if spec is None or spec.loader is None:
            logger.error("Falha ao criar spec para simple hooks")
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Erro ao importar hooks simples: {e}")
        return None


def _import_mission_control_hook():
    """Importa MissionControlHook de NC-HK-FR-003-mission-control-hook.py."""
    hooks_dir = Path(__file__).parent.parent.parent / "core" / "hooks"
    hook_path = hooks_dir / "NC-HK-FR-003-mission-control-hook.py"
    if not hook_path.exists():
        logger.error(f"Hook MissionControl não encontrado em {hook_path}")
        return None
    try:
        spec = importlib.util.spec_from_file_location("mission_control_hook", hook_path)
        if spec is None or spec.loader is None:
            logger.error("Falha ao criar spec para MissionControlHook")
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Erro ao importar MissionControlHook: {e}")
        return None


# -----------------------------------------------------------------------------
# Singleton do HookRegistry e registro automtico de hooks
# -----------------------------------------------------------------------------

_HOOK_REGISTRY = None
_HOOK_EVENT_ENUM = None
_HOOK_MODULE = None
_SIMPLE_HOOKS_MODULE = None
_MISSION_CONTROL_HOOK_MODULE = None
_MISSION_CONTROL_HOOK_INSTANCE = None
_AUTO_HOOK_INSTANCES = {}


def _get_hook_registry():
    """Singleton do HookRegistry."""
    global \
        _HOOK_REGISTRY, \
        _HOOK_EVENT_ENUM, \
        _HOOK_MODULE, \
        _SIMPLE_HOOKS_MODULE, \
        _MISSION_CONTROL_HOOK_MODULE, \
        _MISSION_CONTROL_HOOK_INSTANCE, \
        _AUTO_HOOK_INSTANCES
    if _HOOK_REGISTRY is not None:
        return (
            _HOOK_REGISTRY,
            _HOOK_EVENT_ENUM,
            _SIMPLE_HOOKS_MODULE,
            _AUTO_HOOK_INSTANCES,
        )
    _HOOK_MODULE = _import_hook_registry()
    if _HOOK_MODULE is None:
        raise RuntimeError("HookRegistry no pde ser carregado")
    _HOOK_REGISTRY = _HOOK_MODULE.get_hook_registry()
    _HOOK_EVENT_ENUM = _HOOK_MODULE.HookEvent
    _SIMPLE_HOOKS_MODULE = _import_simple_hooks()
    if _SIMPLE_HOOKS_MODULE is None:
        logger.warning(
            "Hooks simples no carregados; algumas funcionalidades podem estar limitadas."
        )
    # Registra automaticamente LoggingHook e TimingHook
    if _SIMPLE_HOOKS_MODULE:
        try:
            logging_hook = _SIMPLE_HOOKS_MODULE.LoggingHook()
            timing_hook = _SIMPLE_HOOKS_MODULE.TimingHook()
            # Guarda instncias para acesso posterior (ex: estatsticas)
            _AUTO_HOOK_INSTANCES["LoggingHook"] = logging_hook
            _AUTO_HOOK_INSTANCES["TimingHook"] = timing_hook
            # Registra para eventos padro (PreToolUse, PostToolUse, ToolError)
            _HOOK_REGISTRY.register(
                "logging_hook_before",
                _HOOK_EVENT_ENUM.PRE_TOOL_USE,
                logging_hook.on_before,
            )
            _HOOK_REGISTRY.register(
                "logging_hook_after",
                _HOOK_EVENT_ENUM.POST_TOOL_USE,
                logging_hook.on_after,
            )
            _HOOK_REGISTRY.register(
                "logging_hook_error", _HOOK_EVENT_ENUM.TOOL_ERROR, logging_hook.on_error
            )
            _HOOK_REGISTRY.register(
                "timing_hook_before",
                _HOOK_EVENT_ENUM.PRE_TOOL_USE,
                timing_hook.on_before,
            )
            _HOOK_REGISTRY.register(
                "timing_hook_after",
                _HOOK_EVENT_ENUM.POST_TOOL_USE,
                timing_hook.on_after,
            )
            logger.info("Hooks automticos (LoggingHook, TimingHook) registrados.")
        except Exception as e:
            logger.warning(f"Falha ao registrar hooks automticos: {e}")
    # Registra automaticamente MissionControlHook
    _MISSION_CONTROL_HOOK_MODULE = _import_mission_control_hook()
    if _MISSION_CONTROL_HOOK_MODULE:
        try:
            mission_control_hook = _MISSION_CONTROL_HOOK_MODULE.MissionControlHook()
            _AUTO_HOOK_INSTANCES["MissionControlHook"] = mission_control_hook
            logger.info("MissionControlHook carregado.")
        except Exception as e:
            logger.warning(f"Falha ao carregar MissionControlHook: {e}")
    return _HOOK_REGISTRY, _HOOK_EVENT_ENUM, _SIMPLE_HOOKS_MODULE, _AUTO_HOOK_INSTANCES


# -----------------------------------------------------------------------------
# Funes auxiliares para as aes
# -----------------------------------------------------------------------------


def _register_hook_by_name(
    hook_name: str, event_str: str, priority: int = 0
) -> Dict[str, Any]:
    """Registra um hook pr-fabricado por nome."""
    registry, event_enum, simple_hooks, auto_instances = _get_hook_registry()
    if simple_hooks is None:
        return {"success": False, "error": "Mdulo de hooks simples no carregado"}
    # Mapeamento de nomes simplificados para classes
    hook_map = {
        "logging": "LoggingHook",
        "timing": "TimingHook",
        "ratelimit": "RateLimitHook",
        "audit": "AuditHook",
    }
    class_name = hook_map.get(hook_name, hook_name)  # permite tambm o nome da classe
    hook_class = getattr(simple_hooks, class_name, None)
    if hook_class is None:
        return {
            "success": False,
            "error": f"Hook '{hook_name}' no encontrado. Opes: {list(hook_map.keys())}",
        }
    try:
        event = event_enum(event_str)
    except ValueError:
        return {
            "success": False,
            "error": f"Evento invlido: '{event_str}'. Opes: {[e.value for e in event_enum]}",
        }
    hook_instance = hook_class()
    # Determina qual mtodo registrar baseado no evento
    if event == event_enum.PRE_TOOL_USE:
        method = hook_instance.on_before
        suffix = "before"
    elif event == event_enum.POST_TOOL_USE:
        method = hook_instance.on_after
        suffix = "after"
    elif event == event_enum.TOOL_ERROR:
        method = getattr(hook_instance, "on_error", None)
        if method is None:
            method = hook_instance.on_after  # fallback
        suffix = "error"
    else:
        return {
            "success": False,
            "error": f"Evento no suportado para hook '{hook_name}'",
        }
    hook_id = f"{hook_name.lower()}_{suffix}_{event.value}"
    registry.register(hook_id, event, method)
    return {
        "success": True,
        "hook_id": hook_id,
        "hook_name": hook_name,
        "event": event_str,
        "priority": priority,
    }


def _unregister_hook(hook_id: str) -> Dict[str, Any]:
    """Remove um hook pelo ID."""
    registry, _, _, _ = _get_hook_registry()
    removed = registry.unregister(hook_id)
    return {"success": True, "removed": removed, "hook_id": hook_id}


def _trigger_event(event_str: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Triga manualmente um evento."""
    registry, event_enum, _, _ = _get_hook_registry()
    try:
        event = event_enum(event_str)
    except ValueError:
        return {
            "success": False,
            "error": f"Evento invlido: '{event_str}'. Opes: {[e.value for e in event_enum]}",
        }
    results = registry.trigger(event, payload)
    return {"success": True, "event": event_str, "results": results}


def _list_hooks() -> Dict[str, Any]:
    """Lista todos os hooks registrados, agrupados por evento."""
    registry, event_enum, _, _ = _get_hook_registry()
    hooks_by_event = {}
    for event in event_enum:
        hook_names = registry.list_hooks(event)
        hooks_by_event[event.value] = hook_names
    all_hooks = registry.list_hooks()
    return {"success": True, "hooks_by_event": hooks_by_event, "all_hooks": all_hooks}


def _get_timing_stats(tool_name: Optional[str] = None) -> Dict[str, Any]:
    """Retorna estatsticas do TimingHook."""
    _, _, _, auto_instances = _get_hook_registry()
    timing_hook = auto_instances.get("TimingHook")
    if timing_hook is None:
        return {"success": False, "error": "TimingHook no registrado automaticamente"}
    try:
        if tool_name:
            stats = timing_hook.get_stats(tool_name)
            return {"success": True, "tool": tool_name, "stats": stats}
        # Se nenhuma tool for fornecida, retorna stats de todas as tools
        # Isso requer acesso interno ao _latencies, que  privado.
        # Alternativa: iterar sobre todas as tools conhecidas (no ideal)
        return {
            "success": False,
            "error": "Especifique tool_name para obter estatsticas",
        }
    except Exception as e:
        return {"success": False, "error": f"Erro ao obter stats: {e}"}


# -----------------------------------------------------------------------------
# Registro da tool MCP
# -----------------------------------------------------------------------------


def register_tool(mcp) -> None:
    """Registra neocortex_hooks no servidor MCP."""

    @mcp.tool(name="neocortex_hooks")
    def neocortex_hooks(
        action: str,
        hook_name: str = "",
        event: str = "",
        hook_id: str = "",
        payload_json: str = "{}",
        tool_name: str = "",
        priority: int = 0,
    ) -> Dict[str, Any]:
        """Expe o HookRegistry como ferramenta chamvel via MCP.

        Actions: hook.register, hook.unregister, hook.trigger, hook.list, hook.stats"""
        import json

        #  hook.register
        if action == "register":
            if not hook_name or not event:
                return {
                    "success": False,
                    "error": "Para register, fornea hook_name e event.",
                }
            return _register_hook_by_name(hook_name, event, priority)

        #  hook.unregister
        elif action == "unregister":
            if not hook_id:
                return {"success": False, "error": "Para unregister, fornea hook_id."}
            return _unregister_hook(hook_id)

        #  hook.trigger
        elif action == "trigger":
            if not event:
                return {"success": False, "error": "Para trigger, fornea event."}
            try:
                payload = json.loads(payload_json)
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "payload_json invlido. Use JSON string.",
                }
            return _trigger_event(event, payload)

        #  hook.list
        elif action == "list":
            return _list_hooks()

        #  hook.stats
        elif action == "stats":
            return _get_timing_stats(tool_name)

        #  webhook.receive
        elif action == "webhook.receive":
            if not payload_json:
                return {
                    "success": False,
                    "error": "Para webhook.receive, forneça payload_json.",
                }
            try:
                payload = json.loads(payload_json)
                hook_action = payload.get("action")
                data = payload.get("data", {})
                if not hook_action:
                    return {
                        "success": False,
                        "error": "payload_json deve conter campo 'action'.",
                    }
                # Roteia para HookRegistry.emit
                registry, event_enum, _, _ = _get_hook_registry()
                # O HookRegistry não tem método emit, mas temos trigger.
                # Mapeia action para HookEvent
                event = None
                # Tenta encontrar pelo valor do enum (ex: "PreToolUse")
                for e in event_enum:
                    if e.value == hook_action:
                        event = e
                        break
                # Se não encontrou, tenta mapeamento comum
                if event is None:
                    mapping = {
                        "tool_call": event_enum.PRE_TOOL_USE,
                        "tool_result": event_enum.POST_TOOL_USE,
                        "tool_error": event_enum.TOOL_ERROR,
                    }
                    event = mapping.get(hook_action)
                # Se ainda não encontrou, usa PRE_TOOL_USE como padrão
                if event is None:
                    event = event_enum.PRE_TOOL_USE
                    logger.warning(
                        f"Action '{hook_action}' não mapeada, usando PRE_TOOL_USE"
                    )

                # Dispara hooks registrados para o evento
                results = registry.trigger(event, data)
                logger.info(
                    f"Webhook processado: action={hook_action}, event={event.value}, "
                    f"hooks_executados={len(results)}"
                )
                # Retorna resultados
                event_id = str(uuid.uuid4())
                return {
                    "status": "ok",
                    "event_id": event_id,
                    "success": True,
                    "event": event.value,
                    "results": results,
                }
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "payload_json inválido. Use JSON string.",
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro ao processar webhook: {str(e)}",
                }

        #  ao desconhecida
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'.",
                "available": [
                    "register",
                    "unregister",
                    "trigger",
                    "list",
                    "stats",
                    "webhook.receive",
                ],
            }
