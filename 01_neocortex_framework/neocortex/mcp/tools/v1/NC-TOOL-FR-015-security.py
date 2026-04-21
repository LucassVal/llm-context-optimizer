"""---
_genealogy:
  injected_at: '2026-04-16T00:24:00.636682'
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
NeoCortex Security Tool

Ferramenta MCP para neocortex_security.
"""

from typing import Any, Dict

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
        """Seguranca e controle de acesso — validacao, auditoria e criptografia.

        Actions: validate_access, audit_changes, encrypt_sensitive"""
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
