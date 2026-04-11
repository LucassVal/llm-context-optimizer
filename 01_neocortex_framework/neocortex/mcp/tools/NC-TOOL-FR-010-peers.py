#!/usr/bin/env python3
"""
NeoCortex Peers Tool

Ferramenta MCP para neocortex_peers.
"""

from typing import Dict, Any
from ...core import get_peers_service


def register_tool(mcp):
    """
    Registra a ferramenta neocortex_peers no servidor MCP.
    """

    @mcp.tool(name="neocortex_peers")
    def tool_peers(
        action: str, peer_id: str = "", state_data: str = ""
    ) -> Dict[str, Any]:
        """
        Gerenciamento de peers  coordenacao entre multiplas instancias NeoCortex.

        Actions:
        - discover: Descobrir peers disponiveis
        - sync_state: Sincronizar estado entre peers
        - resolve_conflict: Resolver conflitos de estado
        """
        service = get_peers_service()

        if action == "discover":
            return service.discover()
        elif action == "sync_state":
            return service.sync_state(peer_id, state_data)
        elif action == "resolve_conflict":
            return service.resolve_conflict(peer_id)

        return {"success": False, "error": f"Acao desconhecida: {action}"}

    return tool_peers
