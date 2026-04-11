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
import importlib
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone

from mcp.server import Server
from mcp.server.models import InitializationOptions

from ..core.pulse_scheduler import PulseScheduler
from ..infra.metrics_store import create_metrics_store

from .tools import (
    cortex,
    ledger,
    regression,
    checkpoint,
    config,
    init,
    export,
    lobes,
    manifest,
    kg,
    consolidation,
    akl,
    agent,
    benchmark,
    peers,
    security,
    pulse,
    search,
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Session Manager para Pulso Cognitivo
class SessionManager:
    """Gerencia o ciclo de vida da sessão NeoCortex."""

    def __init__(self):
        self.session_start = datetime.now(timezone.utc).isoformat() + "Z"
        self.last_heartbeat = self.session_start
        self.active = True
        logger.info(f"Sessão NeoCortex iniciada em: {self.session_start}")

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

        try:
            result = tool_func(*args, **kwargs)

            # Determine if call was successful
            if isinstance(result, dict) and result.get("success") is False:
                status = "failure"
                details = {"error": result.get("error", "unknown")}

            return result
        except Exception as e:
            status = "failure"
            details = {"error": str(e)}
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
    else:
        server = MockMCP("neocortex")

    # Create global metrics store
    global metrics_store_instance
    metrics_store_instance = create_metrics_store()

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
                    logger.debug(f"Ferramenta '{module_name}' carregada via {file.name}")
            except Exception as e:
                logger.error(f"Erro ao carregar ferramenta '{module_name}': {e}")
                
    logger.info(f"Carregadas dinamicamente {loaded_tools} ferramentas")
    return server

def get_metrics_store():
    global metrics_store_instance
    return metrics_store_instance


# Create global mcp instance
mcp = None # Will instantiate in main based on args

def main():
    import argparse
    global mcp
    
    parser = argparse.ArgumentParser(description="NeoCortex MCP Server")
    parser.add_argument("--transport", choices=["stdio", "websocket", "sse"], default="stdio", help="Transport mode")
    parser.add_argument("--host", default="127.0.0.1", help="Host for WebSocketMode")
    parser.add_argument("--port", type=int, default=8765, help="Port for WebSocketMode")
    args = parser.parse_args()

    # Apply fix as requested by user
    transport = "sse" if args.transport in ["websocket", "sse"] else "stdio"
    print(f"-> Iniciando NeoCortex MCP Server (Modo Selecionado: {args.transport} -> Adaptado para {transport})")
    
    # Instance server with explicit host and port parsed from args
    mcp = create_mcp_server(host=args.host, port=args.port)
    
    if transport == "sse":
        print(f"-> SSE Host: {args.host}:{args.port}")
        if FAST_MCP_AVAILABLE:
            mcp.run(transport="sse")
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
