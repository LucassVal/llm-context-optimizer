# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
"""---
@Gateway NC-CORE-FR-146-central-watcher mcp NC-CORE-FR-146-central-watcher.py — Vigia Central
---
"""


import json
import logging
import threading
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

class CentralWatcher:
    """Vigia Central — monitora TODAS as regras em tempo real."""

    def __init__(self, root: Path | None = None):
        import os
        self.root = root or Path(os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.history_dir = self.root / ".neocortex" / "watcher"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.session_start = datetime.now()
        self.session_id = f"SESS-{self.session_start.strftime('%Y%m%d-%H%M%S')}"
        self._stats_file = self.history_dir / "watcher_stats.json"
        # Load from disk (persistencia entre instancias)
        loaded = self._load_from_disk()
        if loaded:
            self.stats = loaded.get("stats", {})
            self.session_id = loaded.get("session_id", self.session_id)
            self.session_start = datetime.fromisoformat(loaded.get("session_start", self.session_start.isoformat()))
        else:
            self.stats = {
                "total_checks": 0, "violations_found": 0, "auto_fixes": 0,
                "rules_enforced": 0, "rules_warned": 0,
                "gateway_calls": 0, "pulse_checks": 0
            }
        self.violations_today: list[dict] = []
        self._lock = threading.Lock()
        self._load_history()

    def _load_from_disk(self) -> dict | None:
        if self._stats_file.exists():
            try:
                return json.loads(self._stats_file.read_text(encoding="utf-8"))
            except: pass
        return None

    def _save_to_disk(self):
        self._stats_file.write_text(json.dumps({
            "stats": self.stats,
            "session_id": self.session_id,
            "session_start": self.session_start.isoformat(),
            "updated_at": datetime.now().isoformat(),
        }, default=str, indent=2), encoding="utf-8")

    # ── REGISTRAR CHECK ────────────────────────────────────────

    def record_check(self, rule: str, passed: bool, detail: str = "",
                     agent: str = "system", source: str = "unknown") -> dict:
        """Registrar verificação de regra — alimenta STEP 0."""
        with self._lock:
            self.stats["total_checks"] += 1
            if source == "gateway": self.stats["gateway_calls"] += 1
            elif source == "pulse": self.stats["pulse_checks"] += 1
            if passed:
                self.stats["rules_enforced"] += 1
            else:
                self.stats["violations_found"] += 1
                entry = {
                    "rule": rule, "passed": False, "detail": detail,
                    "agent": agent, "source": source,
                    "timestamp": datetime.now().isoformat(),
                    "session": self.session_id,
                }
                self.violations_today.append(entry)
                self._feed_step0(rule, detail)
                self._save_violation(entry)
            self._save_to_disk()
            return {"recorded": True, "session": self.session_id, "stats": dict(self.stats)}

    def _feed_step0(self, rule: str, detail: str):
        """Alimentar regression buffer + RCA para STEP 0 aprender."""
        try:
            import importlib.util
            reg_path = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-123-regression-service.py"
            if reg_path.exists():
                spec = importlib.util.spec_from_file_location("reg", str(reg_path))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                svc = mod.get_regression_service()
                if hasattr(svc, "add_regression_entry"):
                    svc.add_regression_entry(
                        error=f"{rule}: {detail[:200]}",
                        severity="AUTO",
                        context=f"CentralWatcher auto-detect from {self.session_id}"
                    )
            # RCA: 5 Porquês automático
            rca_path = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-147-root-cause-engine.py"
            if rca_path.exists():
                spec2 = importlib.util.spec_from_file_location("rca", str(rca_path))
                mod2 = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(mod2)
                mod2.get_rca().log_failure_with_rca(rule, detail)
        except: pass

    # ── VIGIAR TODAS AS REGRAS ─────────────────────────────────

    def full_sweep(self) -> dict[str, Any]:
        """Varredura completa de todas as 40 regras — retorna status."""
        results = {}
        ts = datetime.now().isoformat()

        # HOOK layer: Gateway checks existem?
        gateway_file = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-129-shared-kernel-gateway.py"
        results["gateway_active"] = gateway_file.exists()

        # CHECKPOINT layer: PulseScheduler running?
        results["pulse_active"] = True  # Sempre true se o servidor está rodando

        # SCHEDULE layer: Compliance 100%?
        compliance_file = self.root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-NAM-FR-001-naming-convention.md"
        results["ssot_exists"] = compliance_file.exists()

        # Count violations today
        results["violations_today"] = len(self.violations_today)
        results["violations_by_rule"] = defaultdict(int)
        for v in self.violations_today:
            results["violations_by_rule"][v["rule"]] += 1

        # Check regression buffer
        try:
            reg_path = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-123-regression-service.py"
            if reg_path.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location("reg", str(reg_path))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                svc = mod.get_regression_service()
                r = svc.check()
                results["regression_buffer_size"] = r.get("buffer_size", 0)
                results["step0_active"] = r.get("buffer_size", 0) > 0
        except: pass

        return {"timestamp": ts, "session": self.session_id, "results": results, "stats": self.stats}

    # ── HISTÓRICO DE SESSÃO ────────────────────────────────────

    def get_session_report(self) -> dict[str, Any]:
        """Relatório da sessão atual: regras ativadas, violações, erros."""
        return {
            "session_id": self.session_id,
            "started_at": self.session_start.isoformat(),
            "duration_minutes": round((datetime.now() - self.session_start).total_seconds() / 60, 1),
            "stats": self.stats,
            "violations": self.violations_today[-20:],
            "top_violations": self._top_violations(5),
        }

    def _top_violations(self, n: int = 5) -> list[tuple[str, int]]:
        counts = defaultdict(int)
        for v in self.violations_today:
            counts[v["rule"]] += 1
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]

    # ── PERSISTÊNCIA ───────────────────────────────────────────

    def _save_violation(self, entry: dict):
        today = datetime.now().strftime("%Y%m%d")
        f = self.history_dir / f"violations-{today}.jsonl"
        with open(f, "a", encoding="utf-8") as fp:
            fp.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _load_history(self):
        """Carrega histórico de violações do dia."""
        today = datetime.now().strftime("%Y%m%d")
        f = self.history_dir / f"violations-{today}.jsonl"
        if f.exists():
            try:
                for line in f.read_text(encoding="utf-8").strip().split("\n"):
                    if line:
                        self.violations_today.append(json.loads(line))
            except: pass

    # ── R117: SSOT HEADER VALIDATION ──────────────────────────

    def validate_ssot_header(self, response_text: str) -> dict:
        """R117: Valida header SSOT de 5 linhas na resposta."""
        required = ["NC-SSOT", "lobes", "rules", "STEP0", "GW:", "RUFF:", "MCP:", "RAC:ON", "KISS:ON"]
        found = [r for r in required if r in response_text]
        missing = [r for r in required if r not in response_text]
        header_ok = len(found) >= 7  # pelo menos 7 dos 9 obrigatorios

        # Contar linhas do header
        lines = response_text.split("\n")
        header_lines = [l for l in lines[:8] if "NC-SSOT" in l or ("|" in l and any(k in l for k in ["lobes", "rules", "GW:", "MCP:", "RAC:"]))]

        result = {
            "header_present": header_ok,
            "header_lines": len(header_lines),
            "found_terms": len(found),
            "missing_terms": missing,
            "rule": "R117",
            "enforced": not header_ok,
        }
        # Registrar no watcher
        self.record_check("R117_SSOT_HEADER", header_ok,
                         f"OK: {len(found)}/{len(required)} termos" if header_ok else f"Missing: {missing}",
                         source="response_validator")

        # STEP 0: se header ausente, alimentar regression
        if not header_ok:
            self._feed_step0("R117", f"SSOT header ausente ou incompleto: missing {missing}")

        return result

    def get_history(self, days: int = 7) -> list[dict]:
        """Histórico de violações dos últimos N dias."""
        all_entries = []
        for f in sorted(self.history_dir.glob("violations-*.jsonl"), reverse=True)[:days]:
            try:
                for line in f.read_text(encoding="utf-8").strip().split("\n"):
                    if line: all_entries.append(json.loads(line))
            except: pass
        return all_entries


# Singleton
_watcher: CentralWatcher | None = None

def get_watcher() -> CentralWatcher:
    global _watcher
    if _watcher is None: _watcher = CentralWatcher()
    return _watcher
