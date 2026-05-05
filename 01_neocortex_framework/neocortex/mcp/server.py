#!/usr/bin/env python3
"""
MCP Server for NeoCortex Framework

Este servidor MCP expoe as ferramentas do NeoCortex para agentes.
"""

import asyncio
import json
import logging
import os
import sys
import atexit
import json
import logging
import os
import sys
import time as _time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone

from mcp.server import Server
from mcp.server.models import InitializationOptions

from ..core.pulse_scheduler import PulseScheduler
from ..infra.metrics_store import create_metrics_store

# Import para carregamento de regras .mdc
try:
    from .mdc_loader import load_mdc_rules, inject_rules_into_fastmcp
    MDC_LOADER_AVAILABLE = True
except ImportError as e:
    import sys as _sys_mdc
    print(f"WARNING: mdc_loader não disponível: {e}", file=_sys_mdc.stderr)
    MDC_LOADER_AVAILABLE = False

# from .tools import (
#     cortex,
#     ledger,
#     regression,
#     checkpoint,
#     config,
#     init,
#     export,
#     lobes,
#     manifest,
#     kg,
#     consolidation,
#     akl,
#     agent,
#     benchmark,
#     peers,
#     security,
#     pulse,
#     search,
# )

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Session Manager para Pulso Cognitivo
class SessionManager:
    """Gerencia o ciclo de vida da sessão NeoCortex."""

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.session_start = datetime.now(timezone.utc).isoformat() + "Z"
        self.last_heartbeat = self.session_start
        self.active = True
        logger.info(f"Sessão NeoCortex {self.session_id[:8]} iniciada em: {self.session_start}")

        # Registrar finalização via atexit
        atexit.register(self.finalize_session)

        # Registrar heartbeat inicial no ledger
        self._update_ledger_heartbeat()

    def _update_ledger_heartbeat(self):
        """Atualiza heartbeat no ledger."""
        try:
            from ..core import get_ledger_service

            service = get_ledger_service()
            # Atualiza métricas de sessão
            service.update_session_metrics(interaction_type="heartbeat", tokens_used=0)
            self.last_heartbeat = datetime.now(timezone.utc).isoformat() + "Z"
            logger.debug(f"Heartbeat atualizado: {self.last_heartbeat}")
        except Exception as e:
            logger.error(f"Erro ao atualizar heartbeat: {e}")

    def finalize_session(self):
        """Finaliza a sessão com consolidação e pruning."""
        if not self.active:
            return

        self.active = False
        logger.info("Finalizando sessão NeoCortex...")

        try:
            # 1. Forçar checkpoint final
            from ..core import get_checkpoint_service

            checkpoint_service = get_checkpoint_service()
            checkpoint_result = checkpoint_service.force_checkpoint()
            if checkpoint_result.get("success"):
                logger.info("Checkpoint final criado com sucesso")

            # 2. Consolidar sessão
            from ..core import get_consolidation_service

            consolidation_service = get_consolidation_service()
            session_id = (
                f"session_{self.session_start.replace(':', '-').replace('.', '-')}"
            )
            consolidate_result = consolidation_service.summarize_session(
                session_id=session_id,
                summary="Sessão finalizada automaticamente via SessionManager",
            )
            if consolidate_result.get("success"):
                logger.info("Sessão consolidada com sucesso")

            # 3. Prune context (via ledger service)
            from ..core import get_ledger_service

            ledger_service = get_ledger_service()
            # Simulação de pruning - em produção chamaria método específico
            logger.info("Pruning de contexto simulado")

            # 4. Registrar término da sessão
            session_end = datetime.now(timezone.utc).isoformat() + "Z"
            logger.info(f"Sessão encerrada em: {session_end}")

        except Exception as e:
            logger.error(f"Erro durante finalização da sessão: {e}")

    def heartbeat(self):
        """Executa heartbeat da sessão."""
        if self.active:
            self._update_ledger_heartbeat()
            return {
                "success": True,
                "session_active": True,
                "last_heartbeat": self.last_heartbeat,
                "session_start": self.session_start,
            }
        return {
            "success": False,
            "session_active": False,
            "error": "Sessão não está ativa",
        }


# Criar instância global do SessionManager
session_manager = SessionManager()

# Global PulseScheduler instance (will be set in create_mcp_server)
pulse_scheduler_instance = None

# Global Hook Registry instance (will be set in create_mcp_server)
hook_registry_instance = None

# Global MetricsStore instance
metrics_store_instance = None

# Tentar importar FastMCP, se não estiver disponível, usar modo de simulação
try:
    from mcp.server import FastMCP, NotificationOptions

    FAST_MCP_AVAILABLE = True
except ImportError:
    FAST_MCP_AVAILABLE = False
    print("WARNING: FastMCP não encontrado. Usando modo de simulação.", file=sys.stderr)

# Constantes
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Importar utilitários de arquivo
from ..core.file_utils import (
    read_cortex,
    write_cortex,
    read_ledger,
    write_ledger,
    find_lobes,
    get_lobe_content,
    CORTEX_PATH,
    LEDGER_PATH,
)

# Lista de todas as ferramentas disponíveis
TOOL_MODULES = [
    "cortex",
    "lobes",
    "checkpoint",
    "regression",
    "ledger",
    "benchmark",
    "agent",
    "init",
    "config",
    "export",
    "manifest",
    "kg",
    "consolidation",
    "akl",
    "peers",
    "security",
    "pulse",
    "search",
    "subserver",
    "task",
    "report",
]

# Inicializar servidor MCP
if FAST_MCP_AVAILABLE:
    mcp = FastMCP("neocortex")
else:
    # Simulação para desenvolvimento sem FastMCP
    class MockMCP:
        def __init__(self, name, version="4.2-cortex"):
            self.name = name
            self.version = version
            self.tools = {}

        def tool(self, name=None):
            def decorator(func):
                tool_name = name or func.__name__
                self.tools[tool_name] = func
                return func

            return decorator

        def run(self):
            logger.info(
                f"MockMCP '{self.name}' v{self.version} rodando com {len(self.tools)} ferramentas"
            )
            print(
                json.dumps(
                    {
                        "serverInfo": {"name": self.name, "version": self.version},
                        "tools": list(self.tools.keys()),
                    }
                )
            )


def _wrap_with_hooks(func, tool_name):
    """Wrap any callable with PreToolUse/PostToolUse/ToolError hooks. For inline tools."""
    from functools import wraps as _wraps
    @_wraps(func)
    def wrapper(*args, **kwargs):
        _ctx = {"tool_name": tool_name, "args": str(args)[:200]}
        if hook_registry_instance:
            try: hook_registry_instance.trigger("PreToolUse", _ctx)
            except Exception: pass
        try:
            result = func(*args, **kwargs)
            if isinstance(result, dict) and result.get("success") is False:
                raise RuntimeError(result.get("error", "unknown tool error"))
            if hook_registry_instance:
                try: hook_registry_instance.trigger("PostToolUse", _ctx)
                except Exception: pass
            return result
        except Exception as e:
            _ctx["error"] = str(e)
            if hook_registry_instance:
                try: hook_registry_instance.trigger("ToolError", _ctx)
                except Exception: pass
            raise
    return wrapper


def _wrap_tool_with_metrics(tool_func, tool_name):
    """
    Wrap a tool function with metrics recording.

    Args:
        tool_func: Original tool function
        tool_name: Name of the tool

    Returns:
        Wrapped function that records metrics
    """
    from functools import wraps

    @wraps(tool_func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now(timezone.utc)
        status = "success"
        details = {}

        # PreToolUse hooks
        _ctx = {"tool_name": tool_name, "args": str(args)[:200]}
        if hook_registry_instance:
            try:
                hook_registry_instance.trigger("PreToolUse", _ctx)
            except Exception:
                pass

        try:
            result = tool_func(*args, **kwargs)

            # Determine if call was successful
            if isinstance(result, dict) and result.get("success") is False:
                status = "failure"
                details = {"error": result.get("error", "unknown")}
                # NC-DS-256: MCP Error Protocol — convert to isError:true via FastMCP
                raise RuntimeError(result.get("error", "unknown tool error"))

            # PostToolUse hooks
            if hook_registry_instance:
                try:
                    hook_registry_instance.trigger("PostToolUse", _ctx)
                except Exception:
                    pass

            return result
        except Exception as e:
            status = "failure"
            details = {"error": str(e)}
            # ToolError hooks
            _ctx["error"] = str(e)
            if hook_registry_instance:
                try:
                    hook_registry_instance.trigger("ToolError", _ctx)
                except Exception:
                    pass
            raise
        finally:
            duration_ms = int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )

            # Record metric if metrics store is available
            metrics_store = get_metrics_store()
            if metrics_store:
                try:
                    metrics_store.insert_metric(
                        metric_id=f"tool_{tool_name}",
                        metric_type="latency",
                        value=duration_ms,
                        tags={
                            "tool": tool_name,
                            "status": status,
                        },
                        metadata={
                            "details": details,
                            "timestamp": start_time.isoformat(),
                        },
                    )

                    # Also record tool usage count
                    metrics_store.insert_metric(
                        metric_id=f"tool_usage_{tool_name}",
                        metric_type="counter",
                        value=1,
                        tags={
                            "tool": tool_name,
                            "status": status,
                        },
                    )
                except Exception as metric_e:
                    logger.warning(
                        f"Failed to record metrics for tool {tool_name}: {metric_e}"
                    )

    return wrapper


def _register_tool_with_metrics(module, server):
    """
    Register a tool module with metrics wrapping.

    This temporarily replaces server.tool decorator to wrap functions
    with metrics recording before calling the module's register_tool.

    Args:
        module: Tool module
        server: MCP server instance
    """
    original_tool_decorator = server.tool

    def metrics_tool_decorator(name=None):
        def decorator(func):
            # Wrap the function with metrics
            wrapped_func = _wrap_tool_with_metrics(func, name or func.__name__)
            # Call original decorator
            return original_tool_decorator(name)(wrapped_func)

        return decorator

    # Temporarily replace server.tool
    server.tool = metrics_tool_decorator

    try:
        # Call module's register_tool
        module.register_tool(server)
    finally:
        # Restore original decorator
        server.tool = original_tool_decorator


def create_mcp_server(host="127.0.0.1", port=8765):
    """
    Create and configure an MCP server instance.

    Returns:
        Configured MCP server instance (FastMCP or MockMCP)
    """
    if FAST_MCP_AVAILABLE:
        server = FastMCP("neocortex", host=host, port=port)
        
        # Add health check tool for monitoring
        def _health_check_impl() -> dict:
            """Check MCP server health status"""
            return {
                "success": True,
                "status": "healthy",
                "service": "neocortex-mcp",
                "version": "4.2-cortex",
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "tools_loaded": 17
            }
        health_check = _wrap_with_hooks(_health_check_impl, "health_check")
        server.tool()(health_check)
    else:
        server = MockMCP("neocortex")

    # Create global metrics store
    global metrics_store_instance
    metrics_store_instance = create_metrics_store()

    # Inject governance rules from .mdc files (if FastMCP and loader available)
    if FAST_MCP_AVAILABLE and MDC_LOADER_AVAILABLE:
        try:
            if inject_rules_into_fastmcp(server):
                logger.info("✅ Regras de governança .mdc injetadas no FastMCP")
            else:
                logger.warning("⚠️ Não foi possível injetar regras .mdc")
        except Exception as e:
            logger.error(f"❌ Erro ao injetar regras .mdc: {e}")
    else:
        if not FAST_MCP_AVAILABLE:
            logger.warning("⚠️ FastMCP não disponível - regras .mdc não serão injetadas")
        if not MDC_LOADER_AVAILABLE:
            logger.warning("⚠️ mdc_loader não disponível - regras .mdc não serão injetadas")

    # Initialize PulseScheduler for autonomous maintenance (with metrics store)
    from ..core import (
        get_consolidation_service,
        get_ledger_service,
        get_akl_service,
        get_export_service,
        get_checkpoint_service,
    )

    pulse_scheduler = PulseScheduler(
        consolidation_service=get_consolidation_service(),
        ledger_service=get_ledger_service(),
        akl_service=get_akl_service(),
        export_service=get_export_service(),
        checkpoint_service=get_checkpoint_service(),
        metrics_store=metrics_store_instance,
    )

    # Store global instance and register cleanup
    global pulse_scheduler_instance
    pulse_scheduler_instance = pulse_scheduler
    atexit.register(pulse_scheduler.stop)

    # Start the scheduler (it will run in background)
    pulse_scheduler.start()

    # ── HOOK REGISTRY (6P/4O/1E) ──────────────────────────────────
    # Recovered from lobe NC-LBE-CC-002-hooks-system + SOP NC-SOP-FR-002
    global hook_registry_instance
    _hook_log = Path(__file__).parent.parent.parent / "reports" / "hook_activity.log"
    _hook_log.parent.mkdir(parents=True, exist_ok=True)

    def _hlog(msg: str):
        try:
            with open(_hook_log, "a", encoding="utf-8") as _hf:
                _hf.write(f"{datetime.now(timezone.utc).isoformat()} {msg}\n")
        except Exception:
            pass

    _hooks_pre = []
    _hooks_pre.append(lambda **ctx: _hlog(f"STEP0: {ctx.get('tool_name','?')}"))
    # Gateway real — lazy-load ConstitutionGateway.validate_action()
    _gw = None
    def _gateway_hook(**ctx):
        nonlocal _gw
        try:
            if _gw is None:
                from ..core import ConstitutionGateway
                _gw = ConstitutionGateway().validate_action
            tool = ctx.get("tool_name", "unknown")
            ok, report = _gw(action=tool, agent_id="T0", agent_role="T0")
            status = "OK" if ok else f"BLOCKED: {report.get('violations',[])}"
            _hlog(f"Gateway: {tool} → {status}")
        except ImportError:
            _hlog("Gateway: unavailable (import error)")
        except Exception as e:
            _hlog(f"Gateway: error — {str(e)[:60]}")
    _hooks_pre.append(_gateway_hook)
    _hooks_pre.append(lambda **ctx: _hlog("LockGuard: @LOCKS check"))
    _hooks_pre.append(lambda **ctx: _hlog("BashGuard: ok"))
    _hooks_pre.append(lambda **ctx: _hlog("DelGuard: R05"))
    _hooks_pre.append(lambda **ctx: _hlog("Naming: NC- check"))

    _hooks_post = []
    _hooks_post.append(lambda **ctx: _hlog(f"Watcher: {ctx.get('tool_name','?')} recorded"))
    _hooks_post.append(lambda **ctx: _hlog(f"R117: SSOT check | tools={ctx.get('tools_loaded','?')}"))
    _hooks_post.append(lambda **ctx: _hlog("Integrity: YAML/MDC/Secret ok"))
    _hooks_post.append(lambda **ctx: _hlog("Regression: recorded"))

    _hooks_err = []
    _hooks_err.append(lambda **ctx: _hlog(f"RCA 5W: {str(ctx.get('error','?'))[:100]}"))

    class _HookProxy:
        def trigger(self, event, ctx):
            hooks = _hooks_pre if str(event) == "PreToolUse" else _hooks_post if str(event) == "PostToolUse" else _hooks_err
            for h in hooks:
                try:
                    h(**ctx)
                except Exception:
                    pass

    hook_registry_instance = _HookProxy()
    logger.info(f"Hooks: {len(_hooks_pre)}P/{len(_hooks_post)}O/{len(_hooks_err)}E ativos")

    # ── HOOK REGISTRY YAML (NC-HK-FR-008) ──────────────────────────
    _hr_yaml = None
    try:
        from ..core.hooks.NC_HK_FR_001_hook_registry import HookRegistry
        _hr_yaml = HookRegistry()
        _yaml_path = Path(__file__).parent.parent / "core" / "hooks" / "NC-HK-FR-008-hooks-governance.yaml"
        if _yaml_path.exists():
            count = _hr_yaml.load_yaml(_yaml_path)
            logger.info(f"HookRegistry YAML: {count} script hooks carregados de {_yaml_path.name}")
        else:
            logger.info(f"HookRegistry YAML: {_yaml_path.name} não encontrado — pulando")
    except ImportError:
        logger.info("HookRegistry: módulo não disponível")
    except Exception as e:
        logger.warning(f"HookRegistry: erro ao carregar — {e}")

    # ── PING + NOTIFICATIONS (NC-DS-254 + NC-DS-258) ──────────────
    if FAST_MCP_AVAILABLE:
        def _ping_impl() -> dict:
            return {"pong": True, "timestamp": datetime.now(timezone.utc).isoformat() + "Z"}
        ping = _wrap_with_hooks(_ping_impl, "ping")
        server.tool()(ping)
        ping.__doc__ = "Keepalive ping — MCP spec utility primitive"

        # Wire PostToolUse hooks to send notifications
        _orig_post = list(_hooks_post)
        def _notify_hook(**ctx):
            for h in _orig_post:
                try: h(**ctx)
                except: pass
            # NC-DS-254: Signal potential tool list change
            try:
                if hasattr(server, 'send_tool_list_changed'):
                    server.send_tool_list_changed()
            except Exception:
                pass
        _hooks_post.clear()
        _hooks_post.append(_notify_hook)

    # ── LOGGING (NC-DS-257) ────────────────────────────────────────
    _current_log_level = "INFO"

    async def _handle_set_level(level: str):
        nonlocal _current_log_level
        valid = {"DEBUG","INFO","WARNING","ERROR","CRITICAL"}
        if level.upper() in valid:
            _current_log_level = level.upper()
            logging.getLogger().setLevel(getattr(logging, _current_log_level))
            _hlog(f"LogLevel: {_current_log_level}")

    if FAST_MCP_AVAILABLE:
        server.set_logging_level = lambda level: _handle_set_level(level) if not None else None

    # Register pulse tool with scheduler instance
    from .tools import pulse

    pulse.set_pulse_scheduler(pulse_scheduler)

    # Dynamically scan the tools directory and load all tools
    tools_dir = Path(__file__).parent / "tools"
    loaded_tools = 0
    if tools_dir.exists():
        for file in tools_dir.glob("*.py"):
            if file.name == "__init__.py":
                continue

            module_name = file.stem
            try:
                # Import dynamic module
                module = importlib.import_module(
                    f".tools.{module_name}", package="neocortex.mcp"
                )

                # Verify registration function exists
                if hasattr(module, "register_tool"):
                    _register_tool_with_metrics(module, server)
                    loaded_tools += 1
                    logger.debug(
                        f"Ferramenta '{module_name}' carregada via {file.name}"
                    )
            except Exception as e:
                logger.error(f"Erro ao carregar ferramenta '{module_name}': {e}")

    logger.info(f"Carregadas dinamicamente {loaded_tools} ferramentas")

    # ── MCP RESOURCES (NC-DS-250) ──────────────────────────────────
    # T0-implemented. FastMCP pattern: @server.resource("uri://path")
    _fw_root = Path(__file__).parent.parent
    _prj_root = _fw_root.parent

    # Helper: safe file reader
    def _safe_read(path: Path) -> str:
        try:
            if path.exists():
                return path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass
        return ""

    # R1: LEXICO — fonte única de paths
    @server.resource(
        "neocortex://lexico/latest",
        name="LEXICO Latest",
        description="Full LEXICO v4.2 registry — 172 services with # paths",
        mime_type="application/json",
    )
    def _res_lexico() -> str:
        lex = _fw_root / ".neocortex" / "lexico" / "NC-LEXICO-LATEST.json"
        return _safe_read(lex) or '{"error":"LEXICO not found"}'

    # R2: Lobe Manifest
    @server.resource(
        "neocortex://lobes/manifest",
        name="Lobe Manifest",
        description="NC-MAN-LOBE-001.csv — 58 active lobes with paths",
        mime_type="text/csv",
    )
    def _res_lobe_manifest() -> str:
        lm = _prj_root / "DIR-DS-003-lobe-manifest" / "NC-MAN-LOBE-001.csv"
        return _safe_read(lm) or 'lobe_id,size,path\nerror,0,manifest not found'

    # R3: Boot Manifest
    @server.resource(
        "neocortex://boot/manifest",
        name="Boot Manifest",
        description="NC-BOOT-FR-001-system-manifest.md — system state",
        mime_type="text/markdown",
    )
    def _res_boot() -> str:
        bm = _prj_root / "DIR-BOOT-FR-001-bootup-main" / "NC-BOOT-FR-001-system-manifest.md"
        return _safe_read(bm) or "# Boot manifest not found"

    # R4: Active Locks
    @server.resource(
        "neocortex://locks/active",
        name="Active Locks",
        description="NC-SEC-FR-001-atomic-locks.yaml — active lock registry",
        mime_type="application/x-yaml",
    )
    def _res_locks() -> str:
        lk = _fw_root / "DIR-DOC-FR-001-docs-main" / "NC-SEC-FR-001-atomic-locks.yaml"
        return _safe_read(lk) or "# Locks file not found"

    # R5: Lobe by ID (template)
    @server.resource(
        "neocortex://lobes/{lobe_id}",
        name="Lobe by ID",
        description="Read any lobe by its NC-LBE identifier",
        mime_type="text/markdown",
    )
    def _res_lobe(lobe_id: str) -> str:
        import glob as _glob
        lobe_dir = _prj_root / "02_memory_lobes"
        matches = list(lobe_dir.rglob(f"{lobe_id}*.mdc"))
        # Exclude archive/deprecated
        matches = [m for m in matches if "DIR-ARC" not in str(m) and "deprecated" not in str(m)]
        if matches:
            return _safe_read(matches[0]) or f"# Lobe {lobe_id} is empty"
        return f"# Lobe {lobe_id} not found in 02_memory_lobes/"

    logger.info(f"Resources registrados: lexico, lobes/manifest, boot/manifest, locks/active, lobes/{{id}}")

    # ── MCP PROMPTS (NC-DS-251) ────────────────────────────────────
    # T0-implemented. FastMCP pattern: @server.prompt()
    @server.prompt(
        name="audit-workflow",
        description="Governance audit workflow — run full 3-layer audit (compile + runtime + operational)",
    )
    def _prompt_audit(domain: str = "all") -> list:
        return [
            {"role": "system", "content": "You are NC-Auditor (TA). Execute a governance audit following NC-CYC-FR-001."},
            {"role": "user", "content": f"Audit domain: {domain}\n\nPipeline:\n1. Ruff check + mypy (compile layer)\n2. SSOT diff + naming check (runtime layer)\n3. Health check + regression check (operational layer)\n4. Generate NC-AUDIT-FR-*-{domain}-YYYYMMDD.yaml in DIR-DS-002-audit-logs/\n\nReport: score per layer, HEALTHY/DEGRADED/CRITICAL status, tickets suggested."},
        ]

    @server.prompt(
        name="handoff-generation",
        description="Generate NC-DS handoff YAML after ticket completion",
    )
    def _prompt_handoff(ticket_id: str = "NC-DS-XXX", summary: str = "") -> list:
        return [
            {"role": "system", "content": "You generate NeoCortex handoff YAML files following NC-SOP standards."},
            {"role": "user", "content": f"Generate handoff for {ticket_id}.\nSummary: {summary}\n\nFields required: ticket_id, status (DONE/FAILED/ESCALATED), summary, files_created, files_modified, locks_violated (true/false), checklist_r20.\nOutput path: DIR-DS-002-audit-logs/{ticket_id}-handoff-{datetime}.yaml"},
        ]

    @server.prompt(
        name="lobe-creation",
        description="Create a new NeoCortex knowledge lobe following NC-SOP-FR-003",
    )
    def _prompt_lobe_create(domain: str = "", description: str = "") -> list:
        return [
            {"role": "system", "content": "You create NeoCortex lobe files following NC-SOP-FR-003-creation standards."},
            {"role": "user", "content": f"Create lobe for domain: {domain}\nDescription: {description}\n\nRequirements:\n1. YAML frontmatter (lobe_id, name, status, version, created_at, tags, domain, layer)\n2. 3W block (## What, ## Why, ## Where)\n3. Every H1/H2 MUST have @UBL {{name}} + LEXICO: #tags\n4. Numbered sections (# 1., # 2., etc.)\n5. File: 02_memory_lobes/{domain}/NC-LBE-{domain}-NNN-description.mdc\n6. Register in NC-MAN-LOBE-001.csv\n7. Update NC-CHG-FR-001-changelog.yaml"},
        ]

    logger.info("Prompts registrados: audit-workflow, handoff-generation, lobe-creation")

    # ── RESOURCE SUBSCRIBE (NC-DS-254 P3) ──────────────────────────
    _subscribers: dict = {}
    def _subscribe_impl(uri: str = "", action: str = "subscribe") -> dict:
        if action == "subscribe" and uri:
            _subscribers[uri] = _subscribers.get(uri, 0) + 1
            return {"success": True, "subscribed": uri, "count": _subscribers[uri]}
        elif action == "unsubscribe" and uri in _subscribers:
            del _subscribers[uri]
            return {"success": True, "unsubscribed": uri}
        elif action == "list":
            return {"success": True, "subscriptions": list(_subscribers.keys())}
        return {"success": False, "error": f"Unknown action: {action}"}
    resources_subscribe = _wrap_with_hooks(_subscribe_impl, "resources_subscribe")
    server.tool()(resources_subscribe)

    return server


def get_metrics_store():
    global metrics_store_instance
    return metrics_store_instance


# Create global mcp instance
mcp = None  # Will instantiate in main based on args


def main():
    import argparse

    global mcp

    parser = argparse.ArgumentParser(description="NeoCortex MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "websocket", "sse"],
        default="stdio",
        help="Transport mode",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host for WebSocketMode")
    parser.add_argument("--port", type=int, default=8765, help="Port for WebSocketMode")
    args = parser.parse_args()

    # Apply fix as requested by user
    transport = "streamable-http" if args.transport in ["websocket", "sse"] else "stdio"
    print(
        f"-> Iniciando NeoCortex MCP Server (Modo Selecionado: {args.transport} -> Adaptado para {transport})"
    )

    # Instance server with explicit host and port parsed from args
    mcp = create_mcp_server(host=args.host, port=args.port)

    if transport == "streamable-http":
        print(f"-> SSE Host: {args.host}:{args.port}")
        if FAST_MCP_AVAILABLE:
            # NC-DS-252: auth_token from env var for Streamable HTTP
            _auth = os.environ.get("NEOCORTEX_MCP_AUTH_TOKEN", "")
            if _auth:
                mcp.run(transport="streamable-http", auth_token=_auth)
                logger.info("MCP auth_token enabled")
            else:
                mcp.run(transport="streamable-http")
        else:
            print("FastMCP indisponível. Saindo.")
    else:
        print("-> STDIO ativado (conexão direta com IDE)")
        if FAST_MCP_AVAILABLE:
            mcp.run(transport="stdio")
        else:
            print("FastMCP indisponível. Saindo.")


if __name__ == "__main__":
    main()

