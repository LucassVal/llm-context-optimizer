#!/usr/bin/env python3
"""
NeoCortex Consolidation Tool

Ferramenta MCP para neocortex_consolidation.
"""

import json
from typing import Dict, Any
from ...core import get_consolidation_service


def register_tool(mcp):
    """
    Registra a ferramenta neocortex_consolidation no servidor MCP.
    """

    @mcp.tool(name="neocortex_consolidation")
    def tool_consolidation(
        action: str,
        session_id: str = "",
        summary: str = "",
        target: str = "",
        metadata: str = "",
    ) -> Dict[str, Any]:
        """
        Consolidacao Semantica  transforma experiencia efemera em regras permanentes.

        Actions:
        - summarize_session: Resume uma sessao em regras concisas
        - merge_learnings: Combina aprendizados de multiplos agentes
        - promote_to_rule: Promove entrada do Regression Buffer a regra permanente
        """
        service = get_consolidation_service()

        if action == "summarize_session":
            metadata_dict = json.loads(metadata) if metadata else None
            return service.summarize_session(session_id, summary, metadata_dict)
        elif action == "merge_learnings":
            return service.merge_learnings()
        elif action == "promote_to_rule":
            return service.promote_to_rule(target)

        return {"success": False, "error": f"Acao desconhecida: {action}"}

    return tool_consolidation
