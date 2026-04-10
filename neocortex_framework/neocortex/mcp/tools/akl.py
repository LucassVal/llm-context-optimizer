#!/usr/bin/env python3
"""
NeoCortex Akl Tool

Ferramenta MCP para neocortex_akl.
"""

from typing import Dict, Any
from ...core import get_akl_service


def register_tool(mcp):
    """
    Registra a ferramenta neocortex_akl no servidor MCP.
    """

    @mcp.tool(name="neocortex_akl")
    def tool_akl(
        action: str,
        target: str = "",
        metadata: str = "",
    ) -> Dict[str, Any]:
        """
        Adaptive Knowledge Lifecycle  gerencia relevancia do conhecimento.

        Actions:
        - assess_importance: Avalia importancia de regras com base no uso
        - decay_knowledge: Aplica decaimento a regras nao utilizadas
        - suggest_cleanup: Lista regras candidatas a arquivamento
        """
        service = get_akl_service()

        if action == "assess_importance":
            return service.assess_importance(target)
        elif action == "decay_knowledge":
            return service.decay_knowledge()
        elif action == "suggest_cleanup":
            # Use threshold from metadata if provided
            threshold = 20
            if metadata:
                try:
                    threshold = int(metadata)
                except ValueError:
                    pass
            return service.suggest_cleanup(threshold)

        return {"success": False, "error": f"Acao desconhecida: {action}"}

    return tool_akl
