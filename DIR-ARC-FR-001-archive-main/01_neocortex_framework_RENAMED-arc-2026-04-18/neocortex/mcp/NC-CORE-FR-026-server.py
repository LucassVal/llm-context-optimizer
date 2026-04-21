"""---
domain: "orchestration"
layer: "core"
type: "service"
tags: ["server"]
hash: "auto-generated"
---"""
#!/usr/bin/env python3
"""
MCP Server for NeoCortex Framework

Este servidor MCP expoe as ferramentas do NeoCortex para agentes.
"""

import atexit
import importlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Tools so carregadas dinamicamente via importlib na funo _load_tools (linha ~399)
# Nomes NC-TOOL-FR-XXX exigem importlib (R09)  importao esttica removida

# Configurao de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Session Manager para Pulso Cognitivo
class SessionManager:
    """Gerencia o ciclo de vida da sesso NeoCortex."""

    def __init__(self):
        self.session_start = datetime.now(timezone.utc).isoformat() + "Z"
        self.last_heartbeat = self.session_start
        self.active = True
        logger.info(f"Sesso NeoCortex iniciada em: {self.session_start}")

        # Registrar finalizao via atexit
        atexit.register(self.finalize_session)

        # Registrar heartbeat inicial no ledger
        self._update_ledger_heartbeat()

    def _update_ledger_heartbeat(self):
        """Atualiza heartbeat no ledger."""
        try:
            from ..core import get_ledger_service

            service = get_ledger_service()
            # Atualiza mtricas de sesso
            service.update_session_metrics(interaction_type="heartbeat", tokens_used=0)
            self.last_heartbeat = datetime.now(timezone.utc).isoformat() + "Z"
            logger.debug(f"Heartbeat atualizado: {self.last_heartbeat}")
        except Exception as e:
            logger.error(f"Erro ao atualizar heartbeat: {e}")

    def finalize_session(self):
        """Finaliza a sesso com consolidao e pruning."""
        if not self.active:
            return

        self.active = False
        logger.info("Finalizando sesso NeoCortex...")

        try:
            # 1. Forar checkpoint final
            from ..core import get_checkpoint_service

            checkpoint_service = get_checkpoint_service()
            checkpoint_result = checkpoint_service.force_checkpoint()
            if checkpoint_result.get("success"):
                logger.info("Checkpoint final criado com sucesso")

            # 2. Consolidar sesso
            from ..core import get_consolidation_service

            consolidation_service = get_consolidation_service()
            session_id = (
                f"session_{self.session_start.replace(':', '-').replace('.', '-')}"
            )
            consolidate_result = consolidation_service.summarize_session(
                session_id=session_id,
                summary="Sesso finalizada automaticamente via SessionManager",
            )
            if consolidate_result.get("success"):
                logger.info("Sesso consolidada com sucesso")

            # 3. Prune context (via ledger service)
            from ..core import get_ledger_service

            ledger_service = get_ledger_service()
            # Simulao de pruning - em produo chamaria mtodo especfico
            logger.info("Pruning de contexto simulado")

            # 4. Registrar trmino da sesso
            session_end = datetime.now(timezone.utc).isoformat() + "Z"
            logger.info(f"Sesso encerrada em: {session_end}")

        except Exception as e:
            logger.error(f"Erro durante finalizao da sesso: {e}")

    def heartbeat(self):
        """Executa heartbeat da sesso."""
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
            "error": "Sesso no est ativa",
        }


# Lazy init  NO instanciar aqui (bloqueia handshake stdio do MCP host)
# SessionManager  criado na primeira chamada via get_session_manager()
session_manager: "SessionManager | None" = None

def get_session_manager() -> "SessionManager":
    """Lazy singleton  cria SessionManager apenas quando necessrio."""
    global session_manager
    if session_manager is None:
        session_manager = SessionManager()
    return session_manager


# Global PulseScheduler instance (will be set in create_mcp_server)
pulse_scheduler_instance = None

# Global MetricsStore instance
metrics_store_instance = None

# Tentar importar FastMCP, se no estiver disponvel, usar modo de simulao
try:
    from mcp.server import FastMCP, NotificationOptions

    FAST_MCP_AVAILABLE = True
except ImportError:
    FAST_MCP_AVAILABLE = False
    print("WARNING: FastMCP no encontrado. Usando modo de simulao.", file=sys.stderr)

# Constantes
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Importar utilitrios de arquivo

# Lista de todas as ferramentas disponveis
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
    # Simulao para desenvolvimento sem FastMCP
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

    # MetricsStore: lazy init (DuckDB trava se arquivo .db j aberto por outra instncia)
    global metrics_store_instance
    metrics_store_instance = None  # lazy  criado na primeira chamada via get_metrics_store()

    # PulseScheduler: lazy init (no bloqueia handshake stdio)
    # Ser inicializado na primeira chamada  tool 'pulse' via set_pulse_scheduler_lazy()
    global pulse_scheduler_instance
    pulse_scheduler_instance = None  # lazy

    # Registrar cleanup (ser no-op se scheduler nunca foi iniciado)
    def _cleanup_pulse():
        if pulse_scheduler_instance:
            pulse_scheduler_instance.stop()
    atexit.register(_cleanup_pulse)

    # Registrar referencia lazy no mdulo pulse (R09: importlib para NC- name)
    import importlib as _il_srv
    _pulse_mod = _il_srv.import_module(".tools.NC-TOOL-FR-011-pulse", package="neocortex.mcp")
    if hasattr(_pulse_mod, "set_pulse_scheduler"):
        _pulse_mod.set_pulse_scheduler(None)  # ser setado quando primeiro chamado

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
    print(f"-> Iniciando NeoCortex MCP Server (transport={transport})", file=sys.stderr)

    # Instance server with explicit host and port parsed from args
    mcp = create_mcp_server(host=args.host, port=args.port)

    if transport == "sse":
        print(f"-> SSE Host: {args.host}:{args.port}", file=sys.stderr)
        if FAST_MCP_AVAILABLE:
            mcp.run(transport="sse")
        else:
            print("FastMCP indisponvel. Saindo.", file=sys.stderr)
    else:
        print("-> STDIO ativado (conexo direta com IDE/Antigravity)", file=sys.stderr)
        if FAST_MCP_AVAILABLE:
            mcp.run(transport="stdio")
        else:
            print("FastMCP indisponvel. Saindo.", file=sys.stderr)


if __name__ == "__main__":
    main()
