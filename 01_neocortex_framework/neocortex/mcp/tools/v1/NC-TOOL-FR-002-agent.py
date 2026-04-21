"""---
_genealogy:
  injected_at: '2026-04-16T00:24:00.186078'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
#!/usr/bin/env python3
"""
NeoCortex Agent Tool

Ferramenta MCP para neocortex_agent.
"""

from typing import Any, Dict

from ...core import get_agent_service


def register_tool(mcp):
    """
    Registra a ferramenta neocortex_agent no servidor MCP.
    """

    @mcp.tool(name="neocortex_agent")
    def tool_agent(
        action: str, agent_id: str = "", role: str = "", backend: str = ""
    ) -> Dict[str, Any]:
        """Orquestracao de agentes efemeros.

        Actions:
        - spawn: Cria um novo agente efemero
        - heartbeat: Verifica status do agente
        - consume: Consome resultados do agente
        - list_ephemeral: Lista agentes efemeros ativos"""
        service = get_agent_service()

        if action == "spawn":
            return service.spawn_agent(
                role, backend_override=backend if backend else None
            )
        elif action == "list_ephemeral":
            return service.list_ephemeral()
        elif action == "heartbeat":
            return service.heartbeat(agent_id)
        elif action == "consume":
            return service.consume(agent_id)

        return {"success": False, "error": f"Acao desconhecida: {action}"}

    return tool_agent
