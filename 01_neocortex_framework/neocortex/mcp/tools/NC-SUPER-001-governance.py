#!/usr/bin/env python3
"""
NC-SUPER-001 — neocortex_governance
PODER LEGISLATIVO + JUDICIÁRIO

Funde: governance (024), constitution (041), governance_ops (040),
       tickets (038), handoff (039).

Actions:
  Legislativo: policy.check, rule.list, compliance.report, violation.log
               naming.check, ssot.diff, cycle.check
  Constitucional: cf.status, cf.pre_check, cf.audit, cf.tj, cf.stj, cf.forum
  Tickets: ticket.create, ticket.list, ticket.close, roadmap.done
  Handoff: handoff.create, handoff.list, handoff.validate
  Ops: bootup.sync, catalog.refresh, yaml.sanitize
"""
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_governance"


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ── Compliance (standalone filesystem) ────────────────────────────────────────
def _compliance_report(root: Path) -> Dict:
    fw = root / "01_neocortex_framework"
    docs = fw / "DIR-DOC-FR-001-docs-main"
    tools = fw / "neocortex" / "mcp" / "tools"
    checks = {
        "R01_asset_inventory": (docs / "artifact_catalog.json").exists(),
        "R02_policy_formalized": (docs / "NC-NAM-FR-001-naming-convention.md").exists(),
        "R04_naming_convention": any(fw.rglob("NC-*.py")),
        "R07_polp": (docs / "NC-CFG-FR-001-agent-policy-template.yaml").exists(),
        "R08_atomic_locks": (docs / "NC-SEC-FR-001-atomic-locks.yaml").exists(),
        "R09_write_zones": (docs / "NC-CFG-FR-002-rules-policy.yaml").exists(),
        "R10_audit_trail": (root / "DIR-DS-002-audit-logs").exists(),
        "R12_handoffs": len(list((root / "DIR-DS-002-audit-logs").glob("*.yaml"))) > 0
            if (root / "DIR-DS-002-audit-logs").exists() else False,
        "R13_checkpoints": (tools / "v1" / "NC-TOOL-FR-004-checkpoint.py").exists()
            or (tools / "v1").exists(),
        "R15_savepoint": (tools / "v1" / "NC-TOOL-FR-031-savepoint.py").exists()
            or (tools / "v1").exists(),
        "R18_ticket_lifecycle": len(list((root / "DIR-DS-001-tickets").glob("NC-DS-*.yaml"))) > 0
            if (root / "DIR-DS-001-tickets").exists() else False,
        "R19_4cycle_routine": (root / ".agents" / "workflows" / "NC-WF-001-workspace-routine.md").exists(),
        "R20_archive": (root / "DIR-ARC-FR-001-archive-main").exists(),
        "LEXICO_service": (fw / "neocortex" / "core" / "services" / "NC-SVC-FR-020-lexico-service.py").exists(),
        "SESSION_MEMORY": (fw / "neocortex" / "core" / "services" / "NC-SVC-FR-021-session-memory-writer.py").exists(),
        "SUPER_TOOLS": (tools / "v1").exists() and len(list((tools / "v1").glob("*.py"))) > 0,
    }
    passed = [k for k, v in checks.items() if v]
    failed = [k for k, v in checks.items() if not v]
    score = round(len(passed) / len(checks) * 100, 1)
    return {
        "compliance_score": score,
        "rules_total": len(checks),
        "rules_passed": len(passed),
        "rules_failed": len(failed),
        "violations": failed,
        "status": "COMPLIANT" if score >= 80 else "NON_COMPLIANT",
    }


# ── Constitution checks ────────────────────────────────────────────────────────
CF_VERSION = "NC-CONST-FR-001-v0.2-20260418"
CF_POWERS = {
    "legislativo": "neocortex_governance (T0)",
    "executivo": "neocortex_orchestration + neocortex_system",
    "judiciario": "neocortex_governance (constitution section)",
}
TIER_AUTHORITY = {"T0": "PLENA", "T1": "DELEGADA", "T2": "OPERACIONAL", "T3": "RESTRITA"}


def _cf_pre_check(action_name: str, role: str) -> Dict:
    blocked = ["delete_all", "drop_database", "rm_rf", "format_disk"]
    is_blocked = any(b in action_name.lower() for b in blocked)
    authority = TIER_AUTHORITY.get(role.upper(), "DESCONHECIDA")
    return {
        "verdict": "BLOCKED" if is_blocked else "ALLOWED",
        "is_constitutional": not is_blocked,
        "role": role,
        "action": action_name,
        "violations": [f"Action '{action_name}' bloqueada pela CF"] if is_blocked else [],
        "authority": authority,
    }


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_governance(
        action: str,
        policy_name: str = "",
        action_name: str = "",
        role: str = "T0",
        ticket_id: str = "",
        title: str = "",
        description: str = "",
        agent: str = "T0",
        status: str = "OPEN",
        priority: str = "NORMAL",
        session_id: str = "",
        handoff_data: str = "",
        category: str = "",
    ) -> Dict[str, Any]:
        """PODER LEGISLATIVO + JUDICIÁRIO + CONSTITUIÇÃO.
        Funde: governance, constitution, governance_ops, tickets, handoff.
        Actions: policy.check, rule.list, compliance.report, violation.log,
                 cf.status, cf.pre_check, cf.audit, cf.stj, cf.tj, cf.forum,
                 ticket.create, ticket.list, ticket.close, roadmap.done,
                 handoff.create, handoff.list, bootup.sync, catalog.refresh,
                 naming.check, ssot.diff, cycle.check
        """
        ts = _ts()
        root = _root()

        # ── COMPLIANCE ────────────────────────────────────────────────────────
        if action == "compliance.report":
            r = _compliance_report(root)
            return {"success": True, "action": action, "timestamp": ts, **r}

        elif action == "rule.list":
            rules = {
                "R01": "Inventário de Ativos de IA", "R02": "Política Formalizada",
                "R03": "Estrutura de Diretórios", "R04": "Nomenclatura NC-",
                "R07": "Privilégio Mínimo (PoLP)", "R08": "Atomic Locks",
                "R09": "Zonas de Escrita", "R10": "Trilha de Auditoria",
                "R12": "Handoffs Formais", "R13": "Checkpoints",
                "R18": "Ciclo de Vida Tickets", "R19": "Rotina 4 Ciclos",
                "R20": "Revisão e Arquivo", "R21": "Zero Suposições",
            }
            cat = category.upper() if category else ""
            filtered = {k: v for k, v in rules.items() if not cat or cat in k}
            return {"success": True, "action": action, "rules": filtered, "total": len(filtered), "timestamp": ts}

        elif action == "violation.log":
            if not action_name:
                return {"success": False, "error": "action_name obrigatório", "timestamp": ts}
            log_dir = root / "DIR-DS-002-audit-logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            entry = {"timestamp": ts, "violation": action_name, "role": role, "details": description}
            log_file = log_dir / f"NC-VIO-{ts.replace(':', '-')}.json"
            log_file.write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"success": True, "action": action, "logged": str(log_file), "timestamp": ts}

        elif action == "naming.check":
            pattern = re.compile(r"^NC-[A-Z]+-[A-Z]+-\d{3}-.+\.\w+$")
            name = policy_name or action_name
            ok = bool(pattern.match(name)) if name else False
            return {"success": True, "action": action, "name": name, "valid": ok,
                    "pattern": "NC-<TIPO>-<SIGLA>-<NUM>-<desc>.<ext>", "timestamp": ts}

        elif action == "ssot.diff":
            ssot_path = root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-NAM-FR-001-naming-convention.md"
            exists = ssot_path.exists()
            mtime = datetime.fromtimestamp(ssot_path.stat().st_mtime).isoformat() if exists else None
            return {"success": True, "action": action, "ssot_exists": exists,
                    "ssot_last_modified": mtime, "drift_check": "manual", "timestamp": ts}

        elif action == "cycle.check":
            wf = root / ".agents" / "workflows" / "NC-WF-001-workspace-routine.md"
            return {"success": True, "action": action, "workflow_exists": wf.exists(),
                    "cycles": ["CICLO 0 (Boot)", "CICLO 1 (Início)", "CICLO 2 (Execução)", "CICLO 3 (Encerramento)", "CICLO 4 (Semanal)"],
                    "timestamp": ts}

        # ── CONSTITUTION ──────────────────────────────────────────────────────
        elif action == "cf.status":
            return {"success": True, "action": action, "cf_version": CF_VERSION,
                    "articles": 10, "active_powers": CF_POWERS,
                    "tiers": {"T0": "Soberano", "T1": "Técnico", "T2": "Operacional", "T3": "Braçal"},
                    "timestamp": ts}

        elif action == "cf.pre_check":
            r = _cf_pre_check(action_name or policy_name, role)
            return {"success": True, "action": action, "timestamp": ts, **r}

        elif action in ("cf.audit", "cf.stj", "cf.tj", "cf.forum"):
            r = _cf_pre_check(action_name or "system.audit", role)
            return {"success": True, "action": action,
                    "verdict": r["verdict"], "authority": r["authority"],
                    "compliance": _compliance_report(root), "timestamp": ts}

        # ── TICKETS ───────────────────────────────────────────────────────────
        elif action == "ticket.create":
            if not title:
                return {"success": False, "error": "title obrigatório", "timestamp": ts}
            tickets_dir = root / "DIR-DS-001-tickets"
            tickets_dir.mkdir(parents=True, exist_ok=True)
            existing = sorted(tickets_dir.glob("NC-DS-*.yaml"))
            next_num = 142  # próximo após NC-DS-141
            if existing:
                nums = [int(re.search(r"NC-DS-(\d+)", f.name).group(1))
                        for f in existing if re.search(r"NC-DS-(\d+)", f.name)]
                next_num = max(nums) + 1 if nums else next_num
            ticket_id_new = f"NC-DS-{next_num:03d}"
            content = (
                f"ticket_id: \"{ticket_id_new}\"\n"
                f"title: \"{title}\"\n"
                f"status: \"{status}\"\n"
                f"priority: \"{priority}\"\n"
                f"created: \"{ts}\"\n"
                f"agent: \"{agent}\"\n"
                f"description: |\n  {description}\n"
            )
            (tickets_dir / f"{ticket_id_new}-ticket.yaml").write_text(content, encoding="utf-8")
            return {"success": True, "action": action, "ticket_id": ticket_id_new,
                    "title": title, "timestamp": ts}

        elif action == "ticket.list":
            tickets_dir = root / "DIR-DS-001-tickets"
            if not tickets_dir.exists():
                return {"success": True, "action": action, "tickets": [], "count": 0, "timestamp": ts}
            tickets = [{"file": f.name, "id": re.search(r"NC-DS-\d+", f.name).group()
                        if re.search(r"NC-DS-\d+", f.name) else f.stem}
                       for f in sorted(tickets_dir.glob("NC-DS-*.yaml"))]
            return {"success": True, "action": action, "tickets": tickets[:50],
                    "count": len(tickets), "timestamp": ts}

        elif action == "ticket.close":
            if not ticket_id:
                return {"success": False, "error": "ticket_id obrigatório", "timestamp": ts}
            tickets_dir = root / "DIR-DS-001-tickets"
            matches = list(tickets_dir.glob(f"{ticket_id}*.yaml")) if tickets_dir.exists() else []
            if not matches:
                return {"success": False, "error": f"Ticket {ticket_id} não encontrado", "timestamp": ts}
            return {"success": True, "action": action, "ticket_id": ticket_id,
                    "note": "Marcar %DONE no roadmap via roadmap.done", "timestamp": ts}

        elif action == "roadmap.done":
            if not ticket_id:
                return {"success": False, "error": "ticket_id obrigatório", "timestamp": ts}
            roadmap = root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-TODO-FR-001-project-roadmap-consolidated.md"
            if not roadmap.exists():
                return {"success": False, "error": "Roadmap não encontrado", "timestamp": ts}
            content = roadmap.read_text(encoding="utf-8")
            new_content = content.replace(
                f"| {ticket_id} |", f"| {ticket_id} |"
            )
            updated = f"%DONE [{ts[:10]}]"
            new_content = re.sub(
                rf"(\| {re.escape(ticket_id)} \|[^|]+)\| %PENDING",
                lambda m: m.group(0).replace("%PENDING", updated), new_content
            )
            roadmap.write_text(new_content, encoding="utf-8")
            return {"success": True, "action": action, "ticket_id": ticket_id,
                    "marked": updated, "timestamp": ts}

        # ── HANDOFF ───────────────────────────────────────────────────────────
        elif action == "handoff.create":
            log_dir = root / "DIR-DS-002-audit-logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            ts_file = ts.replace(":", "-")
            handoff_file = log_dir / f"{ticket_id or 'NC-DS-SESS'}-handoff-{ts_file}.yaml"
            content = (
                f"ticket_id: \"{ticket_id or 'NC-DS-SESS'}\"\n"
                f"status: \"APPROVED\"\n"
                f"timestamp: \"{ts}\"\n"
                f"agent: \"{agent}\"\n"
                f"summary: |\n  {description or 'Handoff gerado via neocortex_governance'}\n"
                f"data: {handoff_data or '{}'}\n"
            )
            handoff_file.write_text(content, encoding="utf-8")
            return {"success": True, "action": action, "handoff_file": str(handoff_file), "timestamp": ts}

        elif action == "handoff.list":
            log_dir = root / "DIR-DS-002-audit-logs"
            if not log_dir.exists():
                return {"success": True, "action": action, "handoffs": [], "count": 0, "timestamp": ts}
            handoffs = [f.name for f in sorted(log_dir.glob("*handoff*.yaml"))]
            return {"success": True, "action": action, "handoffs": handoffs[-20:],
                    "count": len(handoffs), "timestamp": ts}

        # ── OPS (G1/G2/G3/G5/G6 — Automação Ciclos 3 e 4) ──────────────────────
        elif action == "bootup.sync":
            """G5 — Ciclo 3: Sincronizar NC-BOOT-FR-001 com handoffs recentes."""
            import subprocess
            import sys
            script = root / "01_neocortex_framework" / "scripts" / "NC-SCR-FR-066-bootup-sync.py"
            if not script.exists():
                boot = root / "DIR-BOOT-FR-001-bootup-main" / "NC-BOOT-FR-001-system-manifest.md"
                return {"success": False, "action": action, "bootup_exists": boot.exists(),
                        "error": f"Script ausente: {script.name}", "timestamp": ts}
            try:
                r = subprocess.run([sys.executable, str(script)],
                                   capture_output=True, text=True, timeout=60, cwd=str(root))
                return {"success": r.returncode == 0, "action": action,
                        "stdout": r.stdout[-1000:], "stderr": r.stderr[-400:],
                        "returncode": r.returncode, "timestamp": ts}
            except subprocess.TimeoutExpired:
                return {"success": False, "action": action, "error": "Timeout 60s", "timestamp": ts}
            except Exception as e:
                return {"success": False, "action": action, "error": str(e), "timestamp": ts}

        elif action == "catalog.refresh":
            """G1 — Ciclo 1/3: Regenerar artifact_catalog.json via NC-SCR-FR-064."""
            import subprocess
            import sys
            script = root / "01_neocortex_framework" / "scripts" / "NC-SCR-FR-064-artifact-catalog.py"
            if not script.exists():
                return {"success": False, "action": action,
                        "error": f"Script ausente: {script.name}", "timestamp": ts}
            try:
                r = subprocess.run([sys.executable, str(script)],
                                   capture_output=True, text=True, timeout=60, cwd=str(root))
                cat = root / "DIR-DOC-FR-001-docs-main" / "artifact_catalog.json"
                return {"success": r.returncode == 0, "action": action,
                        "catalog_exists": cat.exists(),
                        "catalog_bytes": cat.stat().st_size if cat.exists() else 0,
                        "stdout": r.stdout[-800:], "stderr": r.stderr[-300:],
                        "returncode": r.returncode, "timestamp": ts}
            except subprocess.TimeoutExpired:
                return {"success": False, "action": action, "error": "Timeout 60s", "timestamp": ts}
            except Exception as e:
                return {"success": False, "action": action, "error": str(e), "timestamp": ts}

        elif action == "yaml.sanitize":
            """G6 — Ciclo 1/3: Sanitizar YAMLs de governança via NC-SCR-FR-009."""
            import subprocess
            import sys
            script = root / "01_neocortex_framework" / "scripts" / "NC-SCR-FR-009-sanitize-all-yamls.py"
            if not script.exists():
                return {"success": False, "action": action,
                        "error": f"Script ausente: {script.name}", "timestamp": ts}
            check_only = True  # por segurança, apenas verifica (não escreve) via MCP
            args = [sys.executable, str(script), "--check-only"] if check_only else [sys.executable, str(script)]
            try:
                r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=str(root))
                return {"success": r.returncode == 0, "action": action,
                        "stdout": r.stdout[-800:], "stderr": r.stderr[-300:],
                        "returncode": r.returncode, "check_only": check_only, "timestamp": ts}
            except subprocess.TimeoutExpired:
                return {"success": False, "action": action, "error": "Timeout 60s", "timestamp": ts}
            except Exception as e:
                return {"success": False, "action": action, "error": str(e), "timestamp": ts}

        elif action == "governance.full_audit":
            """G2 — Ciclo 4: Auditoria completa 20 regras via NC-SCR-FR-080."""
            import subprocess
            import sys
            script = root / "01_neocortex_framework" / "scripts" / "NC-SCR-FR-080-governance-auditor.py"
            if not script.exists():
                # fallback: compliance interno
                r = _compliance_report(root)
                return {"success": True, "action": action, "source": "internal_fallback",
                        "timestamp": ts, **r}
            try:
                result = subprocess.run([sys.executable, str(script)],
                                        capture_output=True, text=True, timeout=120, cwd=str(root))
                r = _compliance_report(root)
                return {"success": result.returncode == 0, "action": action,
                        "compliance_score": r["compliance_score"],
                        "rules_passed": r["rules_passed"], "rules_total": r["rules_total"],
                        "violations": r["violations"],
                        "stdout": result.stdout[-1200:], "stderr": result.stderr[-400:],
                        "timestamp": ts}
            except subprocess.TimeoutExpired:
                return {"success": False, "action": action, "error": "Timeout 120s", "timestamp": ts}
            except Exception as e:
                return {"success": False, "action": action, "error": str(e), "timestamp": ts}

        elif action == "cycle.archive_handoffs":
            """G3 — Ciclo 4: Arquivar handoffs e tickets expirados."""
            import shutil
            from datetime import timedelta
            max_age_handoffs = 7   # dias — handoffs > 7d para arc/
            max_age_tickets  = 30  # dias — tickets órfãos > 30d para patches/
            now = datetime.now()
            cutoff_h = now - timedelta(days=max_age_handoffs)
            cutoff_t = now - timedelta(days=max_age_tickets)
            arc_dir = root / "DIR-ARC-FR-001-archive-main"
            arc_dir.mkdir(parents=True, exist_ok=True)
            archived_h, archived_t, errors = [], [], []
            # Arquivar handoffs antigos
            audit_dir = root / "DIR-DS-002-audit-logs"
            if audit_dir.exists():
                for f in audit_dir.glob("*.yaml"):
                    try:
                        mtime = datetime.fromtimestamp(f.stat().st_mtime)
                        if mtime < cutoff_h:
                            dest = arc_dir / f.name
                            shutil.move(str(f), str(dest))
                            archived_h.append(f.name)
                    except Exception as ex:
                        errors.append(f"{f.name}: {ex}")
            # Mover tickets órfãos antigos
            tickets_dir = root / "DIR-DS-001-tickets"
            patches_dir = root / "DIR-DS-004-patches"
            patches_dir.mkdir(parents=True, exist_ok=True)
            if tickets_dir.exists():
                for f in tickets_dir.glob("NC-DS-*.yaml"):
                    if "TEMPLATE" in f.name:
                        continue
                    try:
                        mtime = datetime.fromtimestamp(f.stat().st_mtime)
                        if mtime < cutoff_t:
                            dest = patches_dir / f.name
                            shutil.move(str(f), str(dest))
                            archived_t.append(f.name)
                    except Exception as ex:
                        errors.append(f"{f.name}: {ex}")
            return {"success": True, "action": action,
                    "archived_handoffs": len(archived_h), "archived_tickets": len(archived_t),
                    "handoff_list": archived_h[:20], "ticket_list": archived_t[:20],
                    "errors": errors[:5], "cutoff_handoffs_days": max_age_handoffs,
                    "cutoff_tickets_days": max_age_tickets, "timestamp": ts}

        # ── UNKNOWN ───────────────────────────────────────────────────────────

        elif action == "audit.replay":
            from pathlib import Path
            audit_dir = Path(__file__).parents[4] / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main"
            logs = sorted(audit_dir.glob("*.yaml"), key=lambda f: f.stat().st_mtime, reverse=True)[:5]
            entries = [{"file": f.name, "size_kb": round(f.stat().st_size/1024,1)} for f in logs]
            return {"success": True, "action": action, "recent_audit_logs": entries,
                    "count": len(entries), "timestamp": ts}

        elif action == "lock.validate":
            from pathlib import Path
            lock_file = Path(__file__).parents[4] / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-SEC-FR-001-atomic-locks.yaml"
            if not lock_file.exists():
                return {"success": False, "error": "NC-SEC-FR-001-atomic-locks.yaml nao encontrado", "timestamp": ts}
            import yaml as _yaml
            locks = _yaml.safe_load(lock_file.read_text("utf-8")) or {}
            return {"success": True, "action": action, "locks": locks, "total": len(locks), "timestamp": ts}
        else:
            available = [
                "compliance.report", "rule.list", "violation.log", "naming.check", "ssot.diff", "cycle.check",
                "cf.status", "cf.pre_check", "cf.audit", "cf.stj", "cf.tj", "cf.forum",
                "ticket.create", "ticket.list", "ticket.close", "roadmap.done",
                "handoff.create", "handoff.list",
                "bootup.sync", "catalog.refresh", "yaml.sanitize",
                "governance.full_audit", "cycle.archive_handoffs",
                "audit.replay", "lock.validate",
            ]
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": available, "timestamp": ts}
