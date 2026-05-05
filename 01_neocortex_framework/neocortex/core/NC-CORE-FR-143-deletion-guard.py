"""---
@Guard NC-CORE-FR-143-deletion-guard mcp NC-CORE-FR-143-deletion-guard.py — R05 Enforcement
---
"""


import logging
import re
from typing import Tuple

logger = logging.getLogger(__name__)

FORBIDDEN_PATTERNS = [
    r'\brm\s+-rf\b', r'\bdel\s+/[fq]\b', r'\bRemove-Item\b',
    r'\brmdir\b', r'\bunlink\b', r'\.unlink\(\)', r'os\.remove\(',
    r'shutil\.rmtree\(', r'>\s*/dev/null.*rm\b',
]

class DeletionGuard:
    """R05: NUNCA deletar — apenas arquivar."""

    def __init__(self):
        self.blocked_count = 0
        self.override_tokens: set = set()

    def check_command(self, command: str, agent_id: str = "unknown") -> Tuple[bool, str]:
        """Verificar se comando contém operação de deleção."""
        if agent_id in self.override_tokens:
            self.override_tokens.discard(agent_id)
            return True, "R05 override autorizado (one-time token)"

        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                self.blocked_count += 1
                logger.warning(f"[R05] BLOCKED deletion by {agent_id}: {command[:100]}")
                return False, f"R05 VIOLATION: deleção bloqueada. Use arquivamento (DIR-ARC-FR-001-archive-main). Token: {agent_id}_override"

        return True, "R05 OK"

    def grant_override(self, agent_id: str, reason: str = "") -> str:
        """Conceder token de override único para deleção autorizada."""
        token = f"{agent_id}_override_{hash(reason) % 10000}"
        self.override_tokens.add(agent_id)
        logger.info(f"[R05] Override granted to {agent_id}: {reason}")
        return token

_deletion_guard = DeletionGuard()

def check_deletion(command: str, agent_id: str = "unknown") -> Tuple[bool, str]:
    return _deletion_guard.check_command(command, agent_id)
