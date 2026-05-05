"""---
@Scheduler NC-CORE-FR-142-pulse-scheduler-orbital mcp NC-CORE-FR-142-pulse-scheduler-orbital.py — PulseS
---
"""


import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class OrbitalPulseScheduler:
    """PulseScheduler orbital — opera independente do servidor."""

    def __init__(self, root: Optional[Path] = None, interval: int = 300):
        import os
        self.root = root or Path(os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.interval = interval  # segundos entre pulsos (default: 5 min)
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self.stats = {"pulses": 0, "checkpoints": 0, "prunes": 0, "errors": 0}

    def start(self):
        """Iniciar scheduler em thread separada. NUNCA bloqueia o caller."""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="pulse-orbital")
        self._thread.start()
        logger.info(f"[PulseOrbital] Started (interval={self.interval}s)")

    def stop(self):
        """Parar scheduler. Thread-safe."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("[PulseOrbital] Stopped")

    def _run(self):
        while self.running:
            try:
                self._pulse()
            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"[PulseOrbital] Pulse error (non-fatal): {e}")
            time.sleep(self.interval)

    def _pulse(self):
        """Executar um pulso — cada operação é isolada, falha não cascateia."""
        self.stats["pulses"] += 1

        # 1. Auto-checkpoint (leve)
        try: self._auto_checkpoint()
        except Exception: pass

        # 2. Hot context pruning
        try: self._prune_context()
        except Exception: pass

        # 3. Registrar heartbeat no ledger
        try: self._heartbeat()
        except Exception: pass

        # 4. Compliance checkpoint (R02, R13, R20)
        try: self._compliance_check()
        except Exception: pass

        # 5. Naming audit (R01, R24)
        try: self._naming_audit()
        except Exception: pass

        # 6. SSOT drift check (R02)
        try: self._ssot_check()
        except Exception: pass

        # 7. Evolution check (R27-R35)
        try: self._evolution_check()
        except Exception: pass

        # 8. Mutation check (R36-R40)
        try: self._mutation_check()
        except Exception: pass

        # 9. AUTO-GOVERNANCE: compliance + KPI + handoff (R56-R58)
        try: self._auto_governance()
        except Exception: pass

    def _auto_checkpoint(self):
        """Checkpoint automático leve."""
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        cp_dir = self.root / ".neocortex" / "auto_checkpoints"
        cp_dir.mkdir(parents=True, exist_ok=True)
        entry = {"id": f"CP-AUTO-{ts}", "timestamp": datetime.now().isoformat(),
                 "pulse": self.stats["pulses"]}
        (cp_dir / f"{ts}.json").write_text(json.dumps(entry), encoding="utf-8")
        self.stats["checkpoints"] += 1

    def _prune_context(self):
        """Pruning do hot context."""
        hot_file = self.root / ".neocortex" / "hot_context" / "hot-context.md"
        if hot_file.exists() and hot_file.stat().st_size > 50_000:
            hot_file.unlink()
            self.stats["prunes"] += 1
            logger.info("[PulseOrbital] Hot context pruned")

    def _heartbeat(self):
        hb_file = self.root / ".neocortex" / "pulse_heartbeat.json"
        hb_file.write_text(json.dumps({"last_pulse": datetime.now().isoformat(),
                                        "stats": self.stats}), encoding="utf-8")

    def _compliance_check(self):
        """R02+R03+R20 checkpoint: verificar SSOT, tickets e compliance."""
        ssot = self.root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-NAM-FR-001-naming-convention.md"
        if ssot.exists():
            self.stats["ssot_ok"] = True
        # R03: Ticket reference check
        tickets = self.root / "DIR-DS-001-tickets"
        if tickets.exists():
            self.stats["tickets_count"] = len(list(tickets.glob("*.yaml")))
        # R20: Archive check
        archive = self.root / "DIR-ARC-FR-001-archive-main"
        if archive.exists():
            self.stats["archive_ok"] = True
        # ALERTAR se tickets ausentes (R03)
        if tickets.exists() and self.stats.get("tickets_count", 0) == 0:
            self._log_to_regression("R03: DIR-DS-001-tickets sem tickets YAML")
        # Registrar no WAL
        wal = self.root / "DIR-DS-002-audit-logs" / f"NC-WAL-PULSE-{datetime.now().strftime('%Y%m%d')}.jsonl"
        wal.parent.mkdir(parents=True, exist_ok=True)
        with open(wal, "a", encoding="utf-8") as f:
            f.write(json.dumps({"check": "compliance", "ts": datetime.now().isoformat()}, ensure_ascii=False) + "\n")

    def _naming_audit(self):
        """R01+R24: verificar + BLOQUEAR + aprender violações."""
        violations = []
        for f in self.root.glob("*"):
            if f.is_file() and not f.name.startswith('.') and not f.name.startswith('NC-'):
                violations.append(f.name)
        self.stats["non_nc_files"] = len(violations)
        # BLOQUEAR: renomear automaticamente para NC-
        for v in violations[:5]:  # max 5 por pulso
            try:
                src = self.root / v
                dst = self.root / f"NC-ORPHAN-{v}"
                src.rename(dst)
                # LOG no regression buffer (STEP 0 aprende)
                self._log_to_regression(f"R01: {v} renomeado para NC-ORPHAN-{v}")
                self.stats["auto_renamed"] = self.stats.get("auto_renamed", 0) + 1
            except: pass

    def _log_to_regression(self, error: str):
        """Alimentar regression buffer para STEP 0 aprender."""
        try:
            import importlib.util
            reg_path = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-123-regression-service.py"
            spec = importlib.util.spec_from_file_location("reg", str(reg_path))
            mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
            svc = mod.get_regression_service()
            if hasattr(svc, "add_regression_entry"):
                svc.add_regression_entry(error=error, severity="CHECKPOINT", context="PulseScheduler auto-detect")
            self.stats["regression_logs"] = self.stats.get("regression_logs", 0) + 1
        except: pass

    def _ssot_check(self):
        ssot = self.root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-NAM-FR-001-naming-convention.md"
        if ssot.exists():
            self.stats["ssot_size"] = ssot.stat().st_size

    def _evolution_check(self):
        """R27-R35: Verificar sandbox children status."""
        sandbox = self.root / ".neocortex" / "sandbox"
        if sandbox.exists():
            children = list(sandbox.glob("nc-child-*"))
            self.stats["children"] = len(children)
            # Verificar TTL expirado (R34)
            for child in children:
                rna = child / "RNA.json"
                if rna.exists():
                    try:
                        import json as _j
                        data = _j.loads(rna.read_text(encoding="utf-8"))
                        ttl = data.get("ttl_seconds", 0)
                        started = data.get("started_at", "")
                        if ttl > 0 and started:
                            from datetime import datetime as _dt
                            age = (_dt.now() - _dt.fromisoformat(started)).total_seconds()
                            if age > ttl:
                                import shutil
                                shutil.rmtree(str(child), ignore_errors=True)
                                self.stats["auto_cleaned"] = self.stats.get("auto_cleaned", 0) + 1
                    except: pass

    def _mutation_check(self):
        """R36-R40: Verificar propostas de mutação pendentes."""
        amend_file = self.root / ".neocortex" / "amendments" / "proposals.json"
        if amend_file.exists():
            try:
                import json as _j
                proposals = _j.loads(amend_file.read_text(encoding="utf-8"))
                self.stats["pending_mutations"] = len([p for p in proposals if p.get("status") == "proposto"])
            except: pass

    def _auto_governance(self):
        """R56-R58 + R112-R115: compliance + KPI + file scan + integrity checks."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("corp", str(self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-154-corporate-engines.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            corp = mod.get_corporate()
            gaps = corp.compliance.find_gaps()
            if gaps.get("gap_count", 0) > 0:
                corp.compliance.fix_gaps(auto_fit=True)
            kpis = corp.kpi.compute()
            self.stats["auto_gov_score"] = kpis.get("health_score", 0)
            self.stats["auto_gov_gaps"] = gaps.get("gap_count", 0)
            self._notify_watcher("auto_governance", gaps.get("gap_count", 0) == 0)

            # FILE WATCHER: ruff + mypy em arquivos modificados
            self._scan_recent_files()

            # INTEGRITY CHECKS (R112-R115): YAML + MDC + Secrets
            self._scan_integrity()

            # R77 Bias Detection (C): monitorar parâmetros para viés
            self._check_bias()

            # HANDOFF AUTOMÁTICO: registrar atividade do ciclo
            self._create_auto_handoff()

            # R119: Semantic Guardian — saude semantica
            self._check_semantic_health()

            # R52: Kaizen — auto-update log de micro-melhorias
            self._kaizen_log()

            # R83: ALCOA++ — verificar integridade do WAL
            self._alcoa_check()

            # AUTO-SUBMIT: pipeline automático se arquivos mudaram
            self._auto_submit()

            # R120: Semantic Boot — ULQ -> TAGS -> PREP
            self._semantic_boot()

            # R95: Self-Healing — auto-restart MCP if down
            self._self_healing()
        except Exception:
            self.stats["auto_gov_score"] = 0

    def _auto_submit(self):
        """CICLO 2 automático: roda submit se arquivos foram alterados."""
        try:
            # Check if scan_recent_files found changes
            ruff_errors = self.stats.get("file_scan_ruff", 0)
            files_scanned = self.stats.get("files_scanned", 0)
            if files_scanned > 0 and ruff_errors == 0:
                # Files changed and clean — auto-submit
                spec = importlib.util.spec_from_file_location("pipe", str(self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-148-submission-pipeline.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                pipe = mod.get_pipeline()
                result = pipe.submit(
                    files=[str(f) for f in (self.root / "01_neocortex_framework" / "neocortex" / "core").glob("NC-CORE-FR-*.py") if f.stat().st_mtime > __import__('time').time() - 3600],
                    description="Auto-submit: ciclo {}".format(self.stats.get("pulses", 0)),
                    agent="PulseScheduler"
                )
                self.stats["auto_submit"] = result.get("passed", False)
                self.stats["auto_submit_steps"] = len(result.get("steps", []))
                self._notify_watcher("auto_submit", result.get("passed", False))
            else:
                self.stats["auto_submit"] = "no_changes" if files_scanned == 0 else f"ruff_errors:{ruff_errors}"
        except Exception:
            self.stats["auto_submit"] = "error"

    def _kaizen_log(self):
        """R52 S: Auto-update Kaizen lobe com micro-melhorias do ciclo."""
        try:
            kaizen = self.root / "02_memory_lobes" / "06_governance" / "NC-LBE-FR-KAIZEN-001.mdc"
            if not kaizen.exists():
                return
            content = kaizen.read_text("utf-8", errors="ignore")
            today = datetime.now().strftime("%Y-%m-%d")
            entry = "| {} | PulseScheduler auto-cycle: {} checks, compliance={}, yaml={}%, mdc={}%, secrets={}\n".format(
                datetime.now().strftime("%H:%M"),
                self.stats.get("pulses", 0),
                self.stats.get("auto_gov_score", 0),
                self.stats.get("integrity_yaml_pct", 0),
                self.stats.get("integrity_mdc_pct", 0),
                self.stats.get("integrity_secrets_leaks", 0),
            )
            if today in content:
                # Append to today's section
                content = content.rstrip() + "\n" + entry
            else:
                content += f"\n## {today}\n\n| Hora | Item | Impacto |\n|------|------|----------|\n" + entry
            kaizen.write_text(content, "utf-8")
            self.stats["kaizen_updated"] = True
        except Exception:
            self.stats["kaizen_updated"] = False

    def _alcoa_check(self):
        """R83 C: ALCOA++ — verificar integridade do WAL (traceable, immutable)."""
        try:
            import sqlite3
            wal = self.root / "DIR-DS-003-wal" / "neocortex_wal.db"
            if not wal.exists():
                self.stats["alcoa"] = "no_wal"
                return
            conn = sqlite3.connect(str(wal))
            total = conn.execute("SELECT COUNT(*) FROM wal_log").fetchone()[0]
            # A: Attributable — all have session_id?
            null_sessions = conn.execute("SELECT COUNT(*) FROM wal_log WHERE session_id IS NULL").fetchone()[0]
            # L: Legible — all have operation?
            null_ops = conn.execute("SELECT COUNT(*) FROM wal_log WHERE operation IS NULL").fetchone()[0]
            # C: Contemporaneous — check timestamps
            oldest = "N/A"
            try:
                oldest = conn.execute("SELECT MIN(timestamp) FROM wal_log").fetchone()[0]
            except:
                pass
            conn.close()
            issues = []
            if null_sessions > 0: issues.append(f"A: {null_sessions} unattributed")
            if null_ops > 0: issues.append(f"L: {null_ops} illegible")
            if oldest and oldest != "N/A":
                self.stats["alcoa_oldest"] = str(oldest)[:19]
            self.stats["alcoa_issues"] = len(issues)
            self.stats["alcoa_total"] = total
            self._notify_watcher("ALCOA", len(issues) == 0)
        except Exception:
            self.stats["alcoa"] = "error"

    def _check_semantic_health(self):
        """R119 C: Semantic Guardian — verifica saude de lobes, catalog, memoria."""
        try:
            spec = importlib.util.spec_from_file_location("sg", str(self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-167-semantic-guardian.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            r = mod.get_guardian().full_health_check()
            self.stats["semantic_lobe_health"] = r["lobe_health"]["status"]
            self.stats["semantic_sync"] = r["catalog_sync"]["synced"]
            self.stats["semantic_sessions"] = r["memory_health"]["sessions"]
            self.stats["semantic_router"] = r["router_health"]["status"]
            self._notify_watcher("semantic_guardian", r["catalog_sync"]["synced"])
        except Exception:
            self.stats["semantic_lobe_health"] = "error"

    def _self_healing(self):
        """R95 C: Self-Healing — auto-restart MCP if down."""
        try:
            spec = importlib.util.spec_from_file_location("p1", str(self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-172-p1-engines.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            sh = mod.get_p1_engines()["selfheal"]
            health = sh.check_mcp_health()
            self.stats["mcp_health"] = health["status"]
            if health["status"] == "DOWN":
                result = sh.auto_heal()
                self.stats["self_healing_attempted"] = result.get("healed", False)
                self._notify_watcher("self_healing", result.get("healed", False))
        except Exception:
            self.stats["mcp_health"] = "error"

    def _create_auto_handoff(self):
        """Auto-handoff a cada ciclo: registra atividade da governança."""
        try:
            import json
            hf_dir = self.root / "DIR-DS-002-audit-logs"
            hf_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%dT%H%M%S")
            hf = hf_dir / f"NC-DS-AUTO-handoff-{ts}.yaml"
            summary = {
                "timestamp": datetime.now().isoformat(),
                "type": "auto_governance",
                "stats": dict(self.stats),
                "checks": {
                    "compliance_gaps": self.stats.get("auto_gov_gaps", 0),
                    "integrity_yaml": self.stats.get("integrity_yaml_pct", 0),
                    "integrity_mdc": self.stats.get("integrity_mdc_pct", 0),
                    "secrets_leaks": self.stats.get("integrity_secrets_leaks", 0),
                    "bias_flagged": self.stats.get("bias_flagged", 0),
                    "logger_issues": self.stats.get("logger_print_files", 0),
                    "wal_integrity": self.stats.get("wal_integrity_issues", 0),
                    "policy_health": self.stats.get("policy_health", 0),
                }
            }
            hf.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
            self.stats["handoffs"] = self.stats.get("handoffs", 0) + 1
        except Exception:
            pass

    def _check_wal_integrity(self):
        """R67 C: WAL Event Sourcing — verificar integridade do WAL."""
        try:
            import sqlite3
            wal = self.root / "DIR-DS-003-wal" / "neocortex_wal.db"
            if not wal.exists():
                self.stats["wal_integrity"] = "no_wal"
                return
            conn = sqlite3.connect(str(wal))
            total = conn.execute("SELECT COUNT(*) FROM wal_log").fetchone()[0]
            null_ops = conn.execute("SELECT COUNT(*) FROM wal_log WHERE operation IS NULL").fetchone()[0]
            sessions = conn.execute("SELECT COUNT(DISTINCT session_id) FROM wal_log").fetchone()[0]
            conn.close()
            issues = []
            if null_ops > 0:
                issues.append(f"{null_ops} entries without operation")
            if total > 0 and sessions == 0:
                issues.append("No session_id found")
            self.stats["wal_integrity_issues"] = len(issues)
            self.stats["wal_total"] = total
            self._notify_watcher("wal_integrity", len(issues) == 0)
        except Exception:
            self.stats["wal_integrity"] = "error"

    def _check_policy_health(self):
        """R17 C: PolicyLoader — verificar se YAML policies carregam."""
        try:
            locks_file = self.root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-SEC-FR-001-atomic-locks.yaml"
            blueprint = self.root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-ARC-FR-002-architecture-blueprint.yaml"
            import yaml as _y
            ok = 0
            for f in (locks_file, blueprint):
                if f.exists():
                    try:
                        _y.safe_load(f.read_text("utf-8"))
                        ok += 1
                    except: pass
            self.stats["policy_health"] = ok
            self._notify_watcher("policy_health", ok >= 2)
        except Exception:
            self.stats["policy_health"] = -1

    def _check_logger_usage(self):
        """R10 C: Logger — verificar se modulos usam logging.getLogger vs print."""
        try:
            core = self.root / "01_neocortex_framework" / "neocortex" / "core"
            tools = self.root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"
            print_files = []
            for d in (core, tools):
                if not d.exists(): continue
                for f in d.glob("NC-*.py"):
                    content = f.read_text("utf-8", errors="ignore")
                    has_print = bool(__import__("re").search(r'(?<!logging\.)\bprint\(', content))
                    has_logger = "getLogger" in content or "logger" in content.lower()
                    if has_print and not has_logger:
                        print_files.append(f.name[:40])
            self.stats["logger_print_files"] = len(print_files)
            self._notify_watcher("logger_usage", len(print_files) == 0)
        except Exception:
            self.stats["logger_print_files"] = -1

    def _check_bias(self):
        """R77 C: Bias Detection — monitoramento contínuo de vieses."""
        try:
            spec = importlib.util.spec_from_file_location("ai", str(self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-156-ai-governance.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            r = mod.get_ai_governance().bias.report()
            self.stats["bias_flagged"] = r.get("total_flagged", 0)
            self._notify_watcher("bias_detection", r.get("total_flagged", 99) == 0)
        except Exception:
            self.stats["bias_flagged"] = -1

    def _scan_integrity(self):
        """R112-R115: YAML validate + MDC header + Secret scan + Dead code."""
        try:
            spec = importlib.util.spec_from_file_location("si", str(self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-158-system-integrity.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            eng = mod.get_integrity()
            yaml = eng.yaml.validate_all()
            mdc = eng.mdc.validate_all()
            secrets = eng.secrets.scan()
            self.stats["integrity_yaml_pct"] = yaml.get("pct", 0)
            self.stats["integrity_mdc_pct"] = mdc.get("pct_healthy", 0)
            self.stats["integrity_secrets_leaks"] = secrets.get("leaks", 0)
            self.stats["integrity_yaml_invalid"] = yaml.get("invalid", 0)
            self.stats["integrity_mdc_invalid"] = mdc.get("invalid", 0)
            self._notify_watcher("integrity_yaml", yaml.get("invalid", 99) == 0)
            self._notify_watcher("integrity_mdc", mdc.get("invalid", 99) == 0)
            self._notify_watcher("integrity_secrets", secrets.get("leaks", 99) == 0)
        except Exception:
            self.stats["integrity_yaml_pct"] = -1

    def _scan_recent_files(self):
        """Auto-governance: ruff + mypy em arquivos modificados recentemente."""
        import subprocess
        import sys
        import time as _time
        now = _time.time()
        framework = self.root / "01_neocortex_framework" / "neocortex"
        recent_py = []
        for d in [framework / "core", framework / "mcp" / "tools"]:
            if not d.exists():
                continue
            for fp in d.glob("*.py"):
                if now - fp.stat().st_mtime < 3600 and "archive" not in str(fp).lower():
                    recent_py.append(str(fp))
        if recent_py:
            try:
                r = subprocess.run(
                    [sys.executable, "-m", "ruff", "check", *recent_py],
                    capture_output=True, text=True, timeout=30, cwd=str(self.root)
                )
                ruff_errs = len([l for l in r.stdout.splitlines() if l.strip()])
                self.stats["file_scan_ruff"] = ruff_errs
            except Exception:
                self.stats["file_scan_ruff"] = -1
            try:
                r = subprocess.run(
                    [sys.executable, "-m", "mypy", *recent_py, "--no-error-summary"],
                    capture_output=True, text=True, timeout=60, cwd=str(self.root)
                )
                type_errs = len([l for l in r.stdout.splitlines() if l.strip() and "error" in l.lower()])
                self.stats["file_scan_mypy"] = type_errs
            except Exception:
                self.stats["file_scan_mypy"] = -1
            self.stats["files_scanned"] = len(recent_py)
            if ruff_errs > 0 or type_errs > 0:
                self._notify_watcher("file_scan", False)
        else:
            self.stats["files_scanned"] = 0

    def _notify_watcher(self, check: str, passed: bool):
        """Vigia Central: registrar check no watcher."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("cw", str(self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-146-central-watcher.py"))
            mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
            mod.get_watcher().record_check(check, passed, "", "pulse", "pulse")
        except: pass

    def status(self) -> Dict[str, Any]:
        return {"running": self.running, "interval": self.interval, "stats": self.stats}


_pulse: Optional[OrbitalPulseScheduler] = None


def get_pulse_scheduler(interval: int = 300) -> OrbitalPulseScheduler:
    global _pulse
    if _pulse is None:
        _pulse = OrbitalPulseScheduler(interval=interval)
    return _pulse
