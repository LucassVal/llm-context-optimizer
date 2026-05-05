"""---
@Module NC-CORE-FR-141-secretariats mcp NC-CORE-FR-141-secretariats.py — Secretarias do Po
---
"""


import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class HealthSecretariat:
    """Ministério da Saúde — saúde do sistema e agentes."""
    def system_health(self, root: Path) -> Dict[str, Any]:
        import shutil
        import socket
        ports = {"MCP": 8766, "LiteLLM": 4000, "Ollama": 11434}
        results = {}
        for name, port in ports.items():
            try:
                s = socket.create_connection(("localhost", port), timeout=1); s.close()
                results[name] = "UP"
            except: results[name] = "DOWN"
        try:
            disk = shutil.disk_usage(str(root))
            results["disk_free_gb"] = round(disk.free / (1024**3), 1)
        except: pass
        return {"timestamp": datetime.now().isoformat(), "services": results,
                "healthy": all(v == "UP" for v in results.values() if v in ("UP","DOWN"))}


class LaborSecretariat:
    """Ministério do Trabalho — gestão de agentes (CLT Digital)."""
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
    def register_agent(self, agent_id: str, role: str = "T2") -> Dict[str, Any]:
        self.agents[agent_id] = {"id": agent_id, "role": role, "tasks": 0,
                                  "registered_at": datetime.now().isoformat(), "status": "active"}
        return {"success": True, "agent": self.agents[agent_id]}
    def get_agent_stats(self) -> Dict[str, Any]:
        return {"total": len(self.agents),
                "by_role": {r: sum(1 for a in self.agents.values() if a.get("role") == r)
                           for r in {a.get("role","?") for a in self.agents.values()}}}


class TreasurySecretariat:
    """Ministério da Fazenda — orçamento e tokens."""
    def __init__(self):
        self.budget = 1_000_000
        self.spent = 0
    def check_budget(self, amount: int = 0) -> Dict[str, Any]:
        available = self.budget - self.spent
        return {"budget": self.budget, "spent": self.spent, "available": available,
                "can_afford": amount <= available, "health": "OK" if available > self.budget * 0.1 else "CRITICAL"}


class Secretariats:
    def __init__(self):
        self.saude = HealthSecretariat()
        self.trabalho = LaborSecretariat()
        self.fazenda = TreasurySecretariat()

_secretariats: Optional[Secretariats] = None
def get_secretariats() -> Secretariats:
    global _secretariats
    if _secretariats is None: _secretariats = Secretariats()
    return _secretariats
