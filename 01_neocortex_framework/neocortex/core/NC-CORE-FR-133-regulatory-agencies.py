"""---
@Service NC-CORE-FR-133-regulatory-agencies mcp NC-CORE-FR-133-regulatory-agencies.py — Agências R
---
"""


import logging
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RateLimiter:
    """ANATEL Digital — controle de tráfego de requisições."""

    def __init__(self, max_per_minute: int = 60, max_per_hour: int = 1000):
        self.max_per_minute = max_per_minute
        self.max_per_hour = max_per_hour
        self._minute_requests: dict[str, list[float]] = defaultdict(list)
        self._hour_requests: dict[str, list[float]] = defaultdict(list)
        self._banned: dict[str, float] = {}
        self._lock = threading.Lock()

    def check(self, agent_id: str) -> tuple[bool, str]:
        """Verificar se agente excedeu limite de requisições."""
        now = time.time()
        with self._lock:
            # Check if banned
            if agent_id in self._banned:
                if now - self._banned[agent_id] < 3600:
                    return False, f"ANATEL: {agent_id} banido por excesso de requisições"
                del self._banned[agent_id]

            # Clean old requests
            self._minute_requests[agent_id] = [
                t for t in self._minute_requests[agent_id] if now - t < 60]
            self._hour_requests[agent_id] = [
                t for t in self._hour_requests[agent_id] if now - t < 3600]

            # Check limits
            if len(self._minute_requests[agent_id]) >= self.max_per_minute:
                self._banned[agent_id] = now
                return False, f"ANATEL: {agent_id} excedeu {self.max_per_minute} req/min"

            if len(self._hour_requests[agent_id]) >= self.max_per_hour:
                self._banned[agent_id] = now
                return False, f"ANATEL: {agent_id} excedeu {self.max_per_hour} req/hora"

            # Record request
            self._minute_requests[agent_id].append(now)
            self._hour_requests[agent_id].append(now)
            return True, "ANATEL: OK"

    def get_stats(self) -> dict[str, Any]:
        """Estatísticas de tráfego."""
        return {
            "active_agents": len(self._minute_requests),
            "banned_agents": len(self._banned),
            "total_requests_minute": sum(len(v) for v in self._minute_requests.values()),
        }


class HealthInspector:
    """ANVISA Digital — inspeção sanitária do sistema."""

    HEALTH_CHECKS = [
        "mcp_port_8766",
        "litellm_port_4000",
        "picoclaw_port_18790",
        "ollama_port_11434",
        "disk_space",
        "memory_usage",
        "cpu_usage",
    ]

    def __init__(self):
        self.last_inspection: dict[str, dict[str, Any]] = {}
        self.alerts: list[dict[str, Any]] = []

    def inspect(self, root: Path) -> dict[str, Any]:
        """Inspeção completa de saúde."""
        import shutil
        import socket

        import psutil

        results = {}
        ts = datetime.now().isoformat()

        # Port checks
        ports = {"mcp_port_8766": 8766, "litellm_port_4000": 4000,
                 "picoclaw_port_18790": 18790, "ollama_port_11434": 11434}
        for name, port in ports.items():
            try:
                s = socket.create_connection(("localhost", port), timeout=1)
                s.close()
                results[name] = {"status": "healthy", "port": port}
            except Exception:
                results[name] = {"status": "down", "port": port}
                self.alerts.append({"check": name, "status": "down", "timestamp": ts})

        # System checks
        try:
            disk = shutil.disk_usage(str(root))
            results["disk_space"] = {
                "status": "healthy" if disk.free > 1_000_000_000 else "critical",
                "free_gb": disk.free / (1024**3),
                "total_gb": disk.total / (1024**3),
            }
        except Exception:
            results["disk_space"] = {"status": "unavailable"}

        try:
            mem = psutil.virtual_memory()
            results["memory_usage"] = {
                "status": "healthy" if mem.percent < 90 else "critical",
                "percent": mem.percent,
            }
            cpu = psutil.cpu_percent(interval=1)
            results["cpu_usage"] = {
                "status": "healthy" if cpu < 90 else "critical",
                "percent": cpu,
            }
        except Exception:
            results["memory_usage"] = {"status": "unavailable"}

        self.last_inspection[ts] = results
        return {"timestamp": ts, "results": results, "alerts": len(self.alerts)}

    def get_certification(self, system_name: str) -> dict[str, Any]:
        """Emitir certificado de conformidade sanitária."""
        total = len(self.HEALTH_CHECKS)
        healthy = sum(
            1 for v in self.last_inspection.values()
            for c in self.HEALTH_CHECKS
            if c in v and v[c].get("status") == "healthy"
        ) if self.last_inspection else 0

        score = (healthy / total * 100) if total > 0 else 0
        certified = score >= 80

        return {
            "system": system_name,
            "certification": "ANVISA-DIGITAL-CERT",
            "score": score,
            "certified": certified,
            "grade": "A" if score >= 95 else "B" if score >= 80 else "C" if score >= 60 else "F",
            "valid_until": (datetime.now() + timedelta(days=7)).isoformat(),
        }


class CompetitionAuditor:
    """CADE Digital — auditoria de concorrência entre agentes."""

    def __init__(self):
        self._agent_actions: dict[str, int] = defaultdict(int)

    def track_agent(self, agent_id: str) -> None:
        """Registrar ação de agente para análise de mercado."""
        self._agent_actions[agent_id] += 1

    def check_monopoly(self) -> dict[str, Any]:
        """Verificar se algum agente tem monopólio de ações."""
        total = sum(self._agent_actions.values())
        if total == 0:
            return {"monopoly_detected": False, "note": "sem dados"}

        max_agent = max(self._agent_actions, key=self._agent_actions.get)
        max_share = self._agent_actions[max_agent] / total * 100

        return {
            "monopoly_detected": max_share > 70,
            "dominant_agent": max_agent,
            "market_share": f"{max_share:.1f}%",
            "action": "CADE: investigar" if max_share > 70 else "CADE: OK",
        }


class StandardsValidator:
    """INMETRO Digital — validação de padrões e normas."""

    def validate_naming(self, filename: str) -> dict[str, Any]:
        """Validar se arquivo segue padrão NC- (norma técnica)."""
        if not filename.startswith("NC-"):
            return {"valid": False, "standard": "NBR-NC-001",
                    "error": "Não segue NC-<TIPO>-<SIGLA>-<NUM>-<desc>.<ext>"}

        parts = filename.split("-")
        if len(parts) < 4:
            return {"valid": False, "standard": "NBR-NC-001",
                    "error": "Formato incompleto"}

        return {"valid": True, "standard": "NBR-NC-001",
                "tipo": parts[1], "sigla": parts[2], "numero": parts[3]}


class RegulatoryAgencies:
    """Todas as agências reguladoras unificadas."""

    def __init__(self):
        self.anat = RateLimiter()       # ANATEL
        self.anv = HealthInspector()    # ANVISA
        self.cade = CompetitionAuditor() # CADE
        self.inmetro = StandardsValidator()  # INMETRO

    def full_audit(self, root: Path) -> dict[str, Any]:
        """Auditoria regulatória completa."""
        return {
            "anatel_rate_limit": self.anat.get_stats(),
            "anvisa_health": self.anv.inspect(root),
            "cade_competition": self.cade.check_monopoly(),
            "timestamp": datetime.now().isoformat(),
        }


# Singleton
_regulatory_instance: RegulatoryAgencies | None = None


def get_regulatory() -> RegulatoryAgencies:
    global _regulatory_instance
    if _regulatory_instance is None:
        _regulatory_instance = RegulatoryAgencies()
    return _regulatory_instance
