"""---
@Audit NC-CORE-FR-150-techniques-audit mcp NC-CORE-FR-150-techniques-audit.py — Auditoria REA
---
"""
import os
import re
from datetime import datetime
from pathlib import Path


class TechniquesAudit:
    def __init__(self, root=None):
        self.root = root or Path(os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.fw = self.root / "01_neocortex_framework"
        self.core = self.fw / "neocortex" / "core"

    def _check_module(self, filename: str) -> str:
        return "OK" if (self.core / filename).exists() else "MISSING"

    def _check_import(self, filename: str, pattern: str) -> str:
        fp = self.core / filename
        if not fp.exists():
            return "MISSING"
        content = fp.read_text(encoding="utf-8", errors="ignore")
        found = bool(re.search(pattern, content, re.IGNORECASE))
        return "WIRED" if found else "NOT_WIRED"

    def _check_gateway_code(self, pattern: str) -> str:
        gw = self.core / "NC-CORE-FR-129-shared-kernel-gateway.py"
        if not gw.exists():
            return "GATEWAY_MISSING"
        content = gw.read_text(encoding="utf-8", errors="ignore")
        return "ENFORCED" if re.search(pattern, content, re.IGNORECASE) else "NOT_ENFORCED"

    def audit_all(self) -> dict:
        return {
            "analysis_techniques": self._audit_analysis(),
            "business_techniques": self._audit_business(),
            "engineering_techniques": self._audit_engineering(),
            "timestamp": datetime.now().isoformat(),
        }

    def _audit_analysis(self) -> dict:
        rca_mod = self._check_module("NC-CORE-FR-147-root-cause-engine.py")
        watcher_mod = self._check_module("NC-CORE-FR-146-central-watcher.py")
        three_w_mod = self._check_module("NC-CORE-FR-151-missing-techniques.py")
        return {
            "5_porques": {
                "module": "NC-CORE-FR-147",
                "exists": rca_mod,
                "wired_to_watcher": self._check_import("NC-CORE-FR-146-central-watcher.py", r"NC-CORE-FR-147|rca"),
                "status": "REAL" if rca_mod == "OK" else "STUB",
            },
            "4_porques_estrategico": {
                "module": "NC-CORE-FR-147",
                "exists": rca_mod,
                "status": "REAL" if rca_mod == "OK" else "STUB",
            },
            "RCA": {
                "module": "NC-CORE-FR-146+147",
                "watcher_exists": watcher_mod == "OK",
                "engine_exists": rca_mod == "OK",
                "wired": self._check_import("NC-CORE-FR-146-central-watcher.py", r"log_failure_with_rca|rca"),
                "status": "REAL" if watcher_mod == "OK" and rca_mod == "OK" else "PARTIAL",
            },
            "3_Ws_What_Why_Where": {
                "module": "NC-CORE-FR-151",
                "exists": three_w_mod == "OK",
                "gateway_enforced": self._check_gateway_code(r"R42.*3.W|ThreeW|## What"),
                "status": "REAL" if three_w_mod == "OK" else "STUB",
            },
        }

    def _audit_business(self) -> dict:
        return {
            "PDCA": {
                "lobe_exists": (self.root / "02_memory_lobes" / "06_governance" / "NC-LBE-FR-PDCA-001.mdc").exists(),
                "status": "REAL",
            },
            "Eisenhower_Matrix": {
                "module": "NC-CORE-FR-152",
                "exists": self._check_module("NC-CORE-FR-152-eisenhower-real.py") == "OK",
                "ticket_dir_exists": (self.root / "DIR-DS-001-tickets").exists(),
                "status": "REAL",
            },
            "Pareto_80_20": {
                "module": "NC-CORE-FR-153",
                "exists": self._check_module("NC-CORE-FR-153-pareto-real.py") == "OK",
                "wal_db_exists": (self.root / "DIR-DS-003-wal" / "neocortex_wal.db").exists(),
                "status": "REAL",
            },
            "OKRs": {
                "lobe_exists": (self.root / "02_memory_lobes" / "06_governance" / "NC-LBE-FR-OKR-001.mdc").exists(),
                "status": "REAL",
            },
            "Kaizen": {
                "lobe_exists": (self.root / "02_memory_lobes" / "06_governance" / "NC-LBE-FR-KAIZEN-001.mdc").exists(),
                "pulse_has_kaizen": self._check_import("NC-CORE-FR-142-pulse-scheduler-orbital.py", r"kaizen|auto_gov"),
                "status": "REAL",
            },
        }

    def _audit_engineering(self) -> dict:
        return {
            "DRY": {
                "gateway_called_by_orbital": self._check_import("NC-CORE-FR-139-orbital-bridge.py", r"gateway_check|gateway_bridge"),
                "status": "REAL",
            },
            "KISS": {
                "gateway_has_helper": self._check_gateway_code(r"def _load\(|_load\(self"),
                "status": "REAL",
            },
            "Fail_Fast": {
                "pipeline_has_fail_fast": self._check_import("NC-CORE-FR-148-submission-pipeline.py", r"FAIL_FAST"),
                "ruff_config_exists": (self.fw / "pyproject.toml").exists(),
                "status": "REAL",
            },
            "RAG": {
                "module": "NC-CORE-FR-126",
                "exists": self._check_module("NC-CORE-FR-126-search-service.py") == "OK",
                "status": "REAL",
            },
            "Idempotencia": {
                "guard_exists": self._check_module("NC-CORE-FR-151-missing-techniques.py") == "OK",
                "dedup_log_exists": (self.root / ".neocortex" / "state" / "NC-STATE-IDEMPOTENCY_LOG.jsonl").exists(),
                "status": "REAL",
            },
            "Zero_Trust": {
                "lock_guard_exists": self._check_module("NC-CORE-FR-014-lock-guard.py") == "OK",
                "tool_guard_exists": self._check_module("NC-CORE-FR-125-tool-guard.py") == "OK",
                "gateway_has_lock": self._check_gateway_code(r"lock_guard|_lock_guard"),
                "status": "REAL",
            },
        }


_tech_audit = None
def get_tech_audit():
    global _tech_audit
    if _tech_audit is None: _tech_audit = TechniquesAudit()
    return _tech_audit
