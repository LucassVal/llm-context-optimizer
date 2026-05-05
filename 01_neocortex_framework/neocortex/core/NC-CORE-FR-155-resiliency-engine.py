"""---
@Engine NC-CORE-FR-155-resiliency-engine mcp NC-CORE-FR-155-resiliency-engine.py — Bloco 4: Inf
---
"""


import json
import os
import pathlib
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════
# R65 — Bulkhead (Isolamento de Servidores MCP)
# ═══════════════════════════════════════════════════════════════

class Bulkhead:
    """Isola servidores MCP por domínio. Falha em um não afeta outros."""

    def __init__(self, root: Optional[pathlib.Path] = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self._partitions: Dict[str, Dict] = {}
        self._init_partitions()

    def _init_partitions(self):
        tools_dir = self.root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"
        for f in sorted(tools_dir.glob("NC-SUPER-*.py")) if tools_dir.exists() else []:
            try:
                name = f.stem.replace("-", " ").replace("NC SUP", "")
                num = int(f.stem.split("-")[2]) if "-" in f.stem else 0
                if num <= 6: domain = "CORE_GOVERNANCE"
                elif num <= 10: domain = "INFRA_MONITOR"
                elif num <= 14: domain = "DATA_KNOWLEDGE"
                elif num <= 18: domain = "AUTOMATION"
                else: domain = "EVOLUTION"
                self._partitions[name] = {"domain": domain, "status": "healthy", "failures": 0, "last_heartbeat": datetime.now().isoformat()}
            except: pass

    def check(self) -> Dict:
        return {
            "partitions": len(self._partitions),
            "domains": list({p["domain"] for p in self._partitions.values()}),
            "healthy": sum(1 for p in self._partitions.values() if p.get("status") == "healthy"),
            "unhealthy": sum(1 for p in self._partitions.values() if p.get("status") != "healthy"),
            "principle": "Falha em um domínio NÃO afeta os outros — isolamento total",
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════
# R66 — CQRS (Command Query Responsibility Segregation)
# ═══════════════════════════════════════════════════════════════

class CQRSRouter:
    """Separa ferramentas em Query (read) e Command (write)."""

    QUERIES = {"search", "health.check", "kpi.report", "roi.analyze", "compliance.gaps",
               "rule.list", "audit.full", "audit.replay", "pulse.status", "lobe.list",
               "knowledge.search", "manifest.list", "ticket.list", "handoff.list",
               "lock.list", "config.get", "genome.children", "drift.status",
               "agent.list", "rca.list", "checkpoint.list", "session.stats"}
    COMMANDS = {"lobes.create", "lobes.update", "lobes.delete", "tickets.create", "tickets.close",
                "savepoint.create", "savepoint.rollback", "handoff.create", "agent.spawn",
                "compliance.fix", "config.set", "pulse.start", "pulse.stop",
                "genome.fork", "mutation.propose", "instance.switch"}

    def classify(self, action: str) -> str:
        if action in self.QUERIES or action.endswith(".get") or action.endswith(".list") or action.endswith(".status"):
            return "QUERY"
        if action in self.COMMANDS or action.endswith(".create") or action.endswith(".update") or action.endswith(".delete") or action.endswith(".set"):
            return "COMMAND"
        return "UNKNOWN"

    def route(self, action: str) -> Dict:
        cls = self.classify(action)
        return {
            "action": action,
            "type": cls,
            "recommended_transport": "HTTP GET (cache)" if cls == "QUERY" else "SSE (transactional)",
            "cacheable": cls == "QUERY",
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════
# R69 — Feature Toggle (Testes A/B sem redeploy)
# ═══════════════════════════════════════════════════════════════

class FeatureToggle:
    """Habilita/desabilita ferramentas MCP dinamicamente."""

    def __init__(self, root: Optional[pathlib.Path] = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self._config_file = self.root / ".neocortex" / "feature_toggles.json"
        self._toggles: Dict[str, bool] = {}
        self._load()

    def _load(self):
        if self._config_file.exists():
            try:
                self._toggles = json.loads(self._config_file.read_text(encoding="utf-8"))
            except: pass

    def _save(self):
        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        self._config_file.write_text(json.dumps(self._toggles, indent=2), encoding="utf-8")

    def is_enabled(self, feature: str) -> bool:
        return self._toggles.get(feature, True)  # Default: enabled

    def set(self, feature: str, enabled: bool) -> bool:
        self._toggles[feature] = enabled
        self._save()
        return True

    def list_all(self) -> Dict:
        return {"toggles": self._toggles, "count": len(self._toggles),
                "active": sum(1 for v in self._toggles.values() if v),
                "inactive": sum(1 for v in self._toggles.values() if not v)}


# ═══════════════════════════════════════════════════════════════
# R71 — Graceful Degradation (Degradação Controlada)
# ═══════════════════════════════════════════════════════════════

class GracefulDegradation:
    """Fallbacks quando servidores primários caem."""

    FALLBACKS = {
        "llm_router": ["ollama_local", "qwen_backup"],
        "search_service": ["lobe_direct_scan", "fts5_fallback"],
        "knowledge_graph": ["json_cache", "memory_lobe_fallback"],
        "picoclaw": ["picoclaw_stub", "direct_dispatch"],
        "litellm_gateway": ["ollama_local", "static_responses"],
    }

    def __init__(self, root: Optional[pathlib.Path] = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self._degraded_services: Dict[str, str] = {}

    def degrade(self, service: str, reason: str = "health_check_failed") -> str:
        fallbacks = self.FALLBACKS.get(service, ["none_available"])
        active = fallbacks[0] if self._degraded_services.get(service) is None else fallbacks[min(
            fallbacks.index(self._degraded_services.get(service, fallbacks[0])) + 1, len(fallbacks) - 1
        )]
        self._degraded_services[service] = active
        return active

    def restore(self, service: str) -> bool:
        self._degraded_services.pop(service, None)
        return True

    def status(self) -> Dict:
        return {
            "degraded_services": self._degraded_services,
            "count": len(self._degraded_services),
            "principle": "Sistema NUNCA aborta — degrada para modo reduzido",
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════
# R72 — Backpressure (Controle de Fluxo)
# ═══════════════════════════════════════════════════════════════

class Backpressure:
    """Rate limiter — sinaliza ao LLM para desacelerar sob carga alta."""

    def __init__(self, max_calls_per_second: int = 10, window_seconds: int = 5):
        self.max_calls = max_calls_per_second
        self.window = window_seconds
        self._calls: List[float] = []
        self._lock = threading.Lock()
        self._blocked_until: Optional[float] = None

    def allow(self) -> tuple[bool, str]:
        now = time.monotonic()
        with self._lock:
            if self._blocked_until and now < self._blocked_until:
                return False, f"BACKPRESSURE: blocked until {datetime.fromtimestamp(self._blocked_until).isoformat()}"

            self._calls = [c for c in self._calls if now - c < self.window]
            self._calls.append(now)

            rate = len(self._calls) / self.window
            if rate > self.max_calls:
                self._blocked_until = now + self.window
                return False, f"BACKPRESSURE: rate {rate:.1f}/s exceeds limit {self.max_calls}/s. Cooldown {self.window}s."
            return True, "OK"

    def status(self) -> Dict:
        now = time.monotonic()
        recent = len([c for c in self._calls if now - c < self.window])
        return {
            "current_rate_per_s": round(recent / self.window, 1),
            "max_allowed": self.max_calls,
            "window_seconds": self.window,
            "blocked": self._blocked_until is not None and time.monotonic() < self._blocked_until,
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════
# Combined Resiliency Engine
# ═══════════════════════════════════════════════════════════════

class ResiliencyEngine:
    def __init__(self, root: Optional[pathlib.Path] = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self.bulkhead = Bulkhead(root=self.root)
        self.cqrs = CQRSRouter()
        self.feature_toggle = FeatureToggle(root=self.root)
        self.graceful = GracefulDegradation(root=self.root)
        self.backpressure = Backpressure()

    def full_audit(self) -> Dict:
        return {
            "bulkhead": self.bulkhead.check(),
            "cqrs_sample": self.cqrs.route("lobes.create"),
            "feature_toggles": self.feature_toggle.list_all(),
            "graceful_degradation": self.graceful.status(),
            "backpressure": self.backpressure.status(),
            "generated_at": datetime.now().isoformat(),
        }


_res = None
def get_resiliency() -> ResiliencyEngine:
    global _res
    if _res is None: _res = ResiliencyEngine()
    return _res
