#!/usr/bin/env python3
"""
NeoCortex MCP Server v4.2-cortex

Servidor MCP (Model Context Protocol) modularizado que expõe as 16 ferramentas
multi-ação para integração com IDEs (VS Code, Cursor, Antigravity, etc.).

Baseado no protocolo MCP da Anthropic (FastMCP).
"""

import asyncio
import importlib
import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# NeoCortex security utilities
try:
    from NC_SEC_FR_001_security_utils import can_access, load_profile

    SECURITY_UTILS_AVAILABLE = True
except ImportError:
    SECURITY_UTILS_AVAILABLE = False
    print(
        "WARNING: Security utilities not found. Using simulated access control.",
        file=sys.stderr,
    )

# Tentar importar FastMCP, se não estiver disponível, usar modo de simulação
try:
    from mcp.server import FastMCP, NotificationOptions

    FAST_MCP_AVAILABLE = True
except ImportError:
    FAST_MCP_AVAILABLE = False
    print("WARNING: FastMCP não encontrado. Usando modo de simulação.", file=sys.stderr)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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


def create_mcp_server():
    """
    Create and configure an MCP server instance.

    Returns:
        Configured MCP server instance (FastMCP or MockMCP)
    """
    if FAST_MCP_AVAILABLE:
        server = FastMCP("neocortex")
    else:
        server = MockMCP("neocortex")

    # Importar e registrar todas as ferramentas
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
    ]

    # Registrar cada ferramenta
    for module_name in TOOL_MODULES:
        try:
            # Importação dinâmica usando importlib
            module = importlib.import_module(
                f".tools.{module_name}", package="neocortex.mcp"
            )
            # Chama register_tool passando a instância server
            module.register_tool(server)
            logger.info(f"Ferramenta '{module_name}' registrada com sucesso")
        except ImportError as e:
            logger.error(f"Erro ao importar ferramenta '{module_name}': {e}")
        except AttributeError as e:
            logger.error(f"Erro ao registrar ferramenta '{module_name}': {e}")

    return server


# Create global mcp instance for backward compatibility
mcp = create_mcp_server()

# ==================== MAIN ====================


def main():
    """Função principal do servidor MCP."""
    logger.info("Iniciando NeoCortex MCP Server v4.2-cortex")
    logger.info(f"Cortex path: {CORTEX_PATH}")
    logger.info(f"Ledger path: {LEDGER_PATH}")

    if FAST_MCP_AVAILABLE:
        # Executa o servidor FastMCP
        try:
            mcp.run(transport="stdio")
        except KeyboardInterrupt:
            logger.info("Servidor interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no servidor FastMCP: {e}")
            raise
    else:
        # Modo de simulação
        mcp.run()

        # Loop simples para testes
        print("\n=== Modo Simulação ===")
        print("Ferramentas disponíveis:")
        for tool_name, tool_func in mcp.tools.items():
            print(f"  - {tool_name}")

        print("\nExemplo de uso via CLI:")
        print("  python neocortex_cli.py call neocortex_cortex get_full")
        print("  python neocortex_cli.py call neocortex_checkpoint get_current")


if __name__ == "__main__":
    main()
