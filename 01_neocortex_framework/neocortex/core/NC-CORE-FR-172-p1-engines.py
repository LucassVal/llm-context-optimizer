# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
"""---
NC-CORE-FR-172-p1-engines.py — P1: R60 Stakeholder Map + R62 Lean + R95 Self-Healing
Stakeholder: privilege mapping by hierarchy
Lean: context pruner + response trimmer
Self-Healing: auto-restart MCP on 500 errors
---
"""
import os
import pathlib
import subprocess
import sys
import time
from datetime import datetime


# R60 — Stakeholder Map
class StakeholderMap:
    """Mapeia privilegios por hierarquia nos tools."""

    def __init__(self, root: pathlib.Path | None = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self._roles = {"T0": "supreme_judge", "T1": "senior_agent", "T2": "junior_agent", "T3": "observer"}

    def get_privileges(self, agent_role: str) -> dict:
        role = self._roles.get(agent_role, "unknown")
        privs = {
            "supreme_judge": {"read": "all", "write": "all", "delete": "supervised", "config": "all", "approve": "all"},
            "senior_agent": {"read": "all", "write": "sandbox", "delete": "forbidden", "config": "read_only", "approve": "none"},
            "junior_agent": {"read": "sandbox", "write": "sandbox", "delete": "forbidden", "config": "forbidden", "approve": "none"},
            "observer": {"read": "public", "write": "forbidden", "delete": "forbidden", "config": "forbidden", "approve": "none"},
        }
        return {"role": role, "privileges": privs.get(role, privs["observer"]), "agent": agent_role}

    def audit_tools(self) -> dict:
        """Verifica quais tools cada role pode acessar."""
        tools_dir = self.root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"
        tools = [t.stem for t in sorted(tools_dir.glob("NC-SUPER-*.py"))] if tools_dir.exists() else []
        permissions = {}
        for role in self._roles:
            privs = self.get_privileges(role)
            permissions[role] = len(tools) if privs["privileges"]["read"] == "all" else min(5, len(tools))
        return {"tools_total": len(tools), "permissions": permissions, "timestamp": datetime.now().isoformat()}


# R62 — Lean (Context Pruner)
class LeanContextPruner:
    """Reduz desperdicio no contexto — trim respostas, remove metadados inuteis."""

    MAX_CONTEXT_CHARS = 50000
    MAX_RESPONSE_CHARS = 2500

    def __init__(self, root: pathlib.Path | None = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))

    def check_hot_context(self) -> dict:
        """Verifica se hot context esta dentro do limite."""
        hc = self.root / ".neocortex" / "hot_context" / "hot-context.md"
        if not hc.exists():
            return {"status": "MISSING", "size": 0, "limit": self.MAX_CONTEXT_CHARS}
        size = hc.stat().st_size
        if size > self.MAX_CONTEXT_CHARS:
            hc.unlink()
            return {"status": "PRUNED", "size_was": size, "limit": self.MAX_CONTEXT_CHARS}
        return {"status": "OK", "size": size, "limit": self.MAX_CONTEXT_CHARS}

    def trim_response(self, text: str) -> str:
        """Trima resposta para limite KISS."""
        if len(text) > self.MAX_RESPONSE_CHARS:
            return text[:self.MAX_RESPONSE_CHARS - 100] + "... [truncated by LeanContextPruner R62]"
        return text

    def audit_verbosity(self) -> dict:
        """Audita verbosidade dos arquivos."""
        fw = self.root / "01_neocortex_framework" / "neocortex"
        verbose_files = []
        for f in fw.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            lines = len(f.read_text("utf-8", errors="ignore").split("\n"))
            if lines > 500:
                verbose_files.append({"file": f.name, "lines": lines})
        return {"verbose_files": len(verbose_files), "top_5": sorted(verbose_files, key=lambda x: -x["lines"])[:5],
                "recommendation": "Split files >500 lines" if verbose_files else "All files lean"}


# R95 — Self-Healing
class SelfHealingMCP:
    """Auto-restart MCP container on 500 errors."""

    def __init__(self, root: pathlib.Path | None = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self._failures = {}

    def check_mcp_health(self) -> dict:
        """Verifica se MCP esta respondendo."""
        try:
            import socket
            s = socket.create_connection(("localhost", 8766), timeout=1)
            s.close()
            return {"status": "HEALTHY", "port": 8766}
        except Exception:
            return {"status": "DOWN", "port": 8766, "action": "RESTART_NEEDED"}

    def auto_heal(self) -> dict:
        """Tenta auto-recuperacao se MCP down."""
        health = self.check_mcp_health()
        if health["status"] == "HEALTHY":
            return {"healed": False, "reason": "already_healthy"}

        # Tentar restart
        try:
            subprocess.Popen(
                [sys.executable, "-m", "neocortex.mcp.server", "--transport", "sse", "--port", "8766"],
                cwd=str(self.root / "01_neocortex_framework"),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            time.sleep(5)
            health2 = self.check_mcp_health()
            self._failures[datetime.now().isoformat()] = health
            return {"healed": health2["status"] == "HEALTHY", "attempted_restart": True, "result": health2["status"]}
        except Exception as e:
            return {"healed": False, "error": str(e)}


_p1 = None
def get_p1_engines():
    global _p1
    if _p1 is None:
        _p1 = {"stakeholder": StakeholderMap(), "lean": LeanContextPruner(), "selfheal": SelfHealingMCP()}
    return _p1
