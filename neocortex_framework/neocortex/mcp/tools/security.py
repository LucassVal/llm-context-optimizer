#!/usr/bin/env python3
"""
NeoCortex Security Tool

Ferramenta MCP para neocortex_security.
"""

from typing import Dict, Any
from ...core import get_security_service


def register_tool(mcp):
    """
    Registra a ferramenta neocortex_security no servidor MCP.
    """

    @mcp.tool(name="neocortex_security")
    def tool_security(
        action: str,
        resource: str = "",
        audit_data: str = "",
        current_user_id: str = "",
        target_user_id: str = "",
        access_type: str = "read",
    ) -> Dict[str, Any]:
        """
        Seguranca e controle de acesso  validacao, auditoria e criptografia.

        Actions:
        - validate_access: Validar acesso a recursos
        - audit_changes: Auditoria de alteracoes
        - encrypt_sensitive: Criptografar dados sensiveis

        Parameters for validate_access:
        - current_user_id: ID do usuario atual (se vazio, usa do ledger)
        - target_user_id: ID do usuario alvo (se vazio, usa resource como alvo)
        - access_type: 'read' ou 'write' (padrao: read)
        - resource: Recurso a ser acessado (alternativo a target_user_id)
        """
        service = get_security_service()

        if action == "validate_access":
            return service.validate_access(
                current_user_id=current_user_id,
                target_user_id=target_user_id,
                access_type=access_type,
                resource=resource,
            )
        elif action == "audit_changes":
            return service.audit_changes()
        elif action == "encrypt_sensitive":
            return service.encrypt_sensitive(resource)

        return {"success": False, "error": f"Acao desconhecida: {action}"}

    return tool_security
