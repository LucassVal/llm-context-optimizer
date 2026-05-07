# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
"""---
@Guard NC-CORE-FR-144-bash-guard mcp NC-CORE-FR-144-bash-guard.py — Bash Command Guard
---
"""


import json
import logging
import re
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

FORBIDDEN = [
    (r'\brm\s+-rf\b', "R05: rm -rf bloqueado. Use arquivamento."),
    (r'\brm\s+\S', "R05: rm bloqueado. Use Move-Item para DIR-ARC."),
    (r'\bdel\s+/[fq]\b', "R05: del /f bloqueado. Use arquivamento."),
    (r'\bdel\s+\S', "R05: del bloqueado. Use Move-Item para DIR-ARC."),
    (r'\bRemove-Item\s+-?.*(Force|Recurse)', "R05: Remove-Item -Force bloqueado. Use -WhatIf primeiro."),
    (r'\bRemove-Item\b(?!.*-WhatIf)', "R05: Remove-Item sem -WhatIf bloqueado."),
    (r'\brmdir\b', "R05: rmdir bloqueado."),
    (r'\.unlink\(\)', "R05: .unlink() bloqueado. Use arquivamento."),
    (r'\bos\.remove\(', "R05: os.remove() bloqueado."),
    (r'\bshutil\.rmtree\(', "R05: shutil.rmtree() bloqueado."),
    (r'>\s*/dev/null.*\brm\b', "R05: redirecionamento com rm bloqueado."),
]

WARNINGS = [
    (r'\bgit\s+push\s+--force', "⚠️ git push --force detectado. Confirme."),
    (r'\bgit\s+reset\s+--hard', "⚠️ git reset --hard detectado. Confirme."),
]

class BashGuard:
    """R05: Bloqueia comandos destrutivos no bash/terminal."""

    def __init__(self, root: Path | None = None):
        import os
        self.root = root or Path(os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.log_file = self.root / "DIR-DS-002-audit-logs" / "NC-WAL-BASH-GUARD.jsonl"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.blocked_count = 0
        self.warned_count = 0
        self.override_tokens = set()

    def check(self, command: str, agent_id: str = "T0") -> tuple[bool, str]:
        """Verificar comando bash. Retorna (permitido, mensagem)."""
        if not command or not command.strip():
            return True, ""

        # Override token (one-time)
        if agent_id in self.override_tokens:
            self.override_tokens.discard(agent_id)
            self._log(command, agent_id, "OVERRIDE")
            return True, "R05 override autorizado (one-time)"

        # Check forbidden patterns
        for pattern, msg in FORBIDDEN:
            if re.search(pattern, command, re.IGNORECASE):
                self.blocked_count += 1
                self._log(command, agent_id, f"BLOCKED: {msg}")
                return False, msg

        # Check warnings
        for pattern, msg in WARNINGS:
            if re.search(pattern, command, re.IGNORECASE):
                self.warned_count += 1
                self._log(command, agent_id, f"WARN: {msg}")
                return True, msg  # Warning não bloqueia

        return True, ""

    def grant_override(self, agent_id: str, reason: str = "") -> str:
        """Conceder override único para operação de deleção autorizada."""
        self.override_tokens.add(agent_id)
        token = f"OVERRIDE-{hash(reason) % 10000}"
        logger.warning(f"[BashGuard] Override granted to {agent_id}: {reason}")
        return token

    def _log(self, command: str, agent_id: str, result: str):
        entry = json.dumps({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_id,
            "command": command[:500],
            "result": result,
        }, ensure_ascii=False)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")

    def stats(self):
        return {"blocked": self.blocked_count, "warned": self.warned_count}


_guard = BashGuard()

def check_bash(command: str, agent_id: str = "T0") -> tuple[bool, str]:
    return _guard.check(command, agent_id)

def grant_bash_override(agent_id: str, reason: str = "") -> str:
    return _guard.grant_override(agent_id, reason)
