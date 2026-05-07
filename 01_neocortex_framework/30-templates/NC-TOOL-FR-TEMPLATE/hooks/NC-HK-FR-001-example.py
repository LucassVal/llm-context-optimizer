# @UBL @UBL @HK-FR | LEXICO: #SYSTEM
"""
NC-HK-FR-001-example.py  Exemplo de hook Python para NeoCortex.
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
