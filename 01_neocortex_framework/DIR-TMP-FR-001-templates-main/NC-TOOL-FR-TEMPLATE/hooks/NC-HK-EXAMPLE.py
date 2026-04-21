"""---
_genealogy:
  injected_at: '2026-04-16T00:23:57.162874'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: templates
level: 3
tags:
  - templates
  - level-3
  - nc-prefix
  - python
---"""

"""
NC-HK-EXAMPLE.py  Exemplo de hook Python para NeoCortex.
Evento: PostToolUse
Objetivo: Demonstrar estrutura de um hook.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


def hook_handler(context: Dict) -> Dict:
    """Handler do hook de exemplo.

    Args:
        context: {tool_name, action, result, timestamp}
    Returns:
        {status: "ok"|"warning"|"error", message: str}
    """
    tool_name = context.get("tool_name", "unknown")
    logger.debug(f"Hook PostToolUse disparado para tool: {tool_name}")
    return {"status": "ok", "message": f"Hook executado para {tool_name}"}
