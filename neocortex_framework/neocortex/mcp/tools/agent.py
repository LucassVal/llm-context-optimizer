#!/usr/bin/env python3
"""
NeoCortex Agent Tool

Ferramenta MCP para neocortex_agent.
"""

from typing import Dict, Any
from ...core import get_agent_service


def register_tool(mcp):
    """
    Registra a ferramenta neocortex_agent no servidor MCP.
    """

    @mcp.tool(name="neocortex_agent")
    def tool_agent(action: str, agent_id: str = "", role: str = "") -> Dict[str, Any]:
        """
        Orquestracao de agentes efemeros.

        Actions:
        - spawn: Cria um novo agente efemero
        - heartbeat: Verifica status do agente
        - consume: Consome resultados do agente
        - list_ephemeral: Lista agentes efemeros ativos
        """
        service = get_agent_service()

        if action == "spawn":
            return service.spawn_agent(role)
        elif action == "list_ephemeral":
            return service.list_ephemeral()
        elif action == "heartbeat":
            return service.heartbeat(agent_id)
        elif action == "consume":
            return service.consume(agent_id)

        return {"success": False, "error": f"Acao desconhecida: {action}"}

    return tool_agent
