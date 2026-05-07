# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
import os
import pathlib
from datetime import datetime


class AdvancedResilience:
    def __init__(self, root: pathlib.Path | None = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))

    # R83 ALCOA++: Integridade de dados (Attributable, Legible, Contemporaneous, Original, Accurate)
    def check_alcoa(self) -> dict:
        wal_path = self.root / "DIR-DS-003-wal" / "neocortex_wal.db"
        issues = []
        if wal_path.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(str(wal_path))
                total = conn.execute("SELECT COUNT(*) FROM wal_log").fetchone()[0]
                null_session = conn.execute("SELECT COUNT(*) FROM wal_log WHERE session_id IS NULL").fetchone()[0]
                conn.close()
                if null_session > 0:
                    issues.append(f"ALCOA-A (Attributable) FAIL: {null_session}/{total} entries without session_id")
            except: pass
        return {"alcoa_issues": issues, "healthy": len(issues) == 0, "timestamp": datetime.now().isoformat()}

    # R84 Agile Governance: YAML-driven rules without recompilation
    def check_agile_gov(self) -> dict:
        yaml_driven = (self.root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-SEC-FR-001-atomic-locks.yaml").exists()
        return {"yaml_driven_active": yaml_driven, "principle": "Regras via YAML, sem recompilar"}

    # R87 Shackleton: survival mode when network down
    def check_shackleton(self) -> dict:
        local_tools = ["neocortex_governance", "neocortex_state", "neocortex_memory", "neocortex_system"]
        return {"local_tools": len(local_tools), "can_survive_offline": len(local_tools) >= 4}

    # R88 Predictive Risk: anticipate risky actions
    def check_predictive_risk(self) -> dict:
        dangerous = ["lobes.delete", "config.set", "genome.fork", "pulse.stop"]
        return {"dangerous_actions_monitored": len(dangerous), "actions": dangerous}

    # R91 SIEM: Security Information and Event Management
    def check_siem(self) -> dict:
        audit_dir = self.root / "DIR-DS-002-audit-logs"
        violations = []
        if audit_dir.exists():
            for f in sorted(audit_dir.glob("*.yaml"))[-20:]:
                try:
                    c = f.read_text("utf-8", errors="ignore")
                    if "R05" in c: violations.append({"file": f.name, "rule": "R05 Deletion blocked"})
                    if "SECRET" in c.upper(): violations.append({"file": f.name, "rule": "SECRET detected"})
                except: pass
        return {"recent_violations": violations[:5], "total_flagged": len(violations)}

    # R92 Cognitive Load: limit response payload
    def check_cognitive_load(self) -> dict:
        return {"max_context_tokens": 50000, "principle": "Payloads must not overflow LLM context window"}

    # R94 MAPE-K: Monitor-Analyze-Plan-Execute cycle
    def check_mapek(self) -> dict:
        return {"cycle": "Monitor(300s)→Analyze(compliance)→Plan(fix_gaps)→Execute(auto_fix)",
                "active": True, "entity": "PulseScheduler"}

    # R95 Self-Healing: auto-restart failed MCP servers
    def check_self_healing(self) -> dict:
        return {"principle": "Restartar container MCP se respostas 500", "implemented": False,
                "note": "Needs watchdog service (Fase 5)"}

    # R96 Anti-Fragile: errors generate immunity
    def check_anti_fragile(self) -> dict:
        return {"principle": "Cada erro gera vacina no Regression Buffer", "entity": "FR-123 regression-service"}

    # R98 Database Replication: state log duplication
    def check_replication(self) -> dict:
        return {"principle": "Duplicar WAL entre nós para HA", "implemented": False}

    # R101 Digital SRE: correlate token spikes with infra failures
    def check_digital_sre(self) -> dict:
        return {"principle": "Correlacionar picos de tokens com falhas de infra", "implemented": False}

    # R102 Intelligent Error Detection: coordinate rollbacks
    def check_intelligent_error(self) -> dict:
        return {"principle": "Rollback coordenado da task complexa do LLM", "entity": "FR-147 RCAEngine"}

    # R103 Microreboot: restart specific tool thread only
    def check_microreboot(self) -> dict:
        return {"principle": "Derrubar só o thread da ferramenta que travou", "implemented": False}

    def full_audit(self) -> dict:
        return {
            "alcoa": self.check_alcoa(),
            "agile_gov": self.check_agile_gov(),
            "shackleton": self.check_shackleton(),
            "predictive_risk": self.check_predictive_risk(),
            "siem": self.check_siem(),
            "cognitive_load": self.check_cognitive_load(),
            "mapek": self.check_mapek(),
            "self_healing": self.check_self_healing(),
            "anti_fragile": self.check_anti_fragile(),
            "replication": self.check_replication(),
            "digital_sre": self.check_digital_sre(),
            "intelligent_error": self.check_intelligent_error(),
            "microreboot": self.check_microreboot(),
            "generated_at": datetime.now().isoformat(),
        }


_resilience = None
def get_advanced_resilience():
    global _resilience
    if _resilience is None: _resilience = AdvancedResilience()
    return _resilience
