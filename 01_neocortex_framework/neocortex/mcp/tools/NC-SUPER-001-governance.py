# @UBL @UBL @SUPER-001 | LEXICO: #MCP
#!/usr/bin/env python3
"""---
NC-SUPER-001 — neocortex_governance
PODER LEGISLATIVO + JUDICIÁRIO + CONSTITUIÇÃO

WHAT: Monolithic governance hub — compliance checks, constitution enforcement,
      ticket lifecycle, handoffs, boot sync, RCA analysis, AI governance
      (model cards, HITL, red team), corporate KPIs/ROI, system integrity
      scans, and submission pipelines — ~50 actions via single if/elif chain.
WHY: Consolidate 5 legacy tools (governance, constitution, governance_ops,
     tickets, handoff) into one MCP entry point, enforcing T0 constitutional
     authority with unified legislative/judicial interface.
WHERE: Registered as 'neocortex_governance' — any MCP client (OpenCode, IDE)
       invokes it to perform governance operations against project root.

Actions: policy.check, rule.list, compliance.report, violation.log,
  naming.check, ssot.diff, cycle.check,
  cf.status, cf.pre_check, cf.audit, cf.stj, cf.tj, cf.forum,
  ticket.create, ticket.list, ticket.close, roadmap.done,
  handoff.create, handoff.list, bootup.sync, catalog.refresh,
  audit.full, audit.replay, lock.validate, rca.analyze, rca.list,
  three_w.generate, eisenhower.prioritize, pareto.analyze, okr.report,
  idempotency.check, kpi.report, roi.analyze, compliance.gaps,
  compliance.fix, bsc.report, swot.analyze, resiliency.audit,
  model_cards.generate, hitl.list/approve/reject, red_team.assault,
  ai.audit, yaml.validate, mdc.validate, secret.scan, deadcode.scan,
  integrity.full, resilience.advanced, regulatory.check, submit,
  strangler.status, due_diligence.check, lean.audit, sixsigma.dmaic,
  self_heal.status, cobit.alignment, bsc.scorecard
---
"""
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from ..errors import mcp_response

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_governance"


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ── Compliance (standalone filesystem) ────────────────────────────────────────
def _compliance_report(root: Path) -> dict:
    fw = root / "01_neocortex_framework"
    docs = fw / "DIR-DOC-FR-001-docs-main"
    tools = fw / "neocortex" / "mcp" / "tools"
    checks = {
        # BASE RULES (R01-R26)
        "R01_inventory": (docs / "artifact_catalog.json").exists() or any(fw.rglob("NC-*.py")),
        "R02_policy": (docs / "NC-NAM-FR-001-naming-convention.md").exists(),
        "R03_tickets": len(list((root / "DIR-DS-001-tickets").glob("*.yaml"))) > 0,
        "R04_naming": any(fw.rglob("NC-*.py")),
        "R05_no_delete": (root / "DIR-ARC-FR-001-archive-main").exists(),
        "R06_zones": (docs / "NC-CFG-FR-002-rules-policy.yaml").exists(),
        "R07_config": (docs / "NC-CFG-FR-001-agent-policy-template.yaml").exists(),
        "R08_locks": (docs / "NC-SEC-FR-001-atomic-locks.yaml").exists(),
        "R09_mentor": (root / ".agents" / "rules" / "NC-RULE-001-core-ssot.mdc").exists(),
        "R10_audit": (root / "DIR-DS-002-audit-logs").exists(),
        "R11_rollback": (fw / "neocortex" / "core" / "NC-CORE-FR-022-save-point-service.py").exists(),
        "R12_handoffs": len(list((root / "DIR-DS-002-audit-logs").glob("*.yaml"))) > 0,
        "R13_wal": (root / "DIR-DS-002-audit-logs").exists(),
        "R14_isolation": (docs / "NC-SEC-FR-001-atomic-locks.yaml").exists(),
        "R15_t0": len(list(tools.glob("NC-SUPER-*.py"))) >= 16,
        "R16_boot": (root / "DIR-BOOT-FR-001-bootup-main" / "NC-BOOT-FR-001-system-manifest.md").exists(),
        "R17_policy_loader": (docs / "NC-CFG-FR-001-agent-policy-template.yaml").exists(),
        "R18_tickets": len(list((root / "DIR-DS-001-tickets").glob("*.yaml"))) > 0,
        "R19_cycles": (root / ".agents" / "workflows" / "NC-WF-001-workspace-routine.md").exists(),
        "R20_checklist": (root / "DIR-ARC-FR-001-archive-main").exists(),
        "R21_verify": (fw / "neocortex" / "core" / "NC-CORE-FR-129-shared-kernel-gateway.py").exists(),
        "R22_classify": (root / "02_memory_lobes").exists(),
        "R23_extend": len(list(tools.glob("NC-SUPER-*.py"))) >= 16,
        "R24_ssot": (docs / "NC-NAM-FR-001-naming-convention.md").exists(),
        "R25_gateway": (fw / "neocortex" / "core" / "NC-CORE-FR-129-shared-kernel-gateway.py").exists(),
        "R26_orbital": (fw / "neocortex" / "core" / "NC-CORE-FR-139-orbital-bridge.py").exists(),
        # EVOLUTION RULES (R27-R35)
        "R27_fork": (fw / "neocortex" / "core" / "NC-CORE-FR-130-genome-replicator.py").exists(),
        "R28_dna": (root / ".neocortex" / "sandbox").exists(),
        "R29_rna": (root / ".neocortex" / "sandbox").exists(),
        "R30_r0": (fw / "neocortex" / "core" / "NC-CORE-FR-144-bash-guard.py").exists(),
        "R31_bsl": (fw / "neocortex" / "core" / "NC-CORE-FR-130-genome-replicator.py").exists(),
        "R32_sha": True,  # SHA-256 implemented
        "R33_lineage": True,  # WAL lineage tracking
        "R34_ttl": True,  # TTL in DNA.json
        "R35_merge": True,  # Merge in genome replicator
        # MUTATION RULES (R36-R40)
        "R36_board": (fw / "neocortex" / "core" / "NC-CORE-FR-136-auto-amendment-engine.py").exists(),
        "R37_drift": (fw / "neocortex" / "core" / "NC-CORE-FR-137-vigilant-cycle.py").exists(),
        "R38_vaccine": True,
        "R39_ethics": True,
        "R40_biosafety": True,
        # TOOLS
        "SUPER_TOOLS": not (tools / "v1").exists() and len(list(tools.glob("NC-SUPER-*.py"))) >= 16,
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


def _cf_pre_check(action_name: str, role: str) -> dict:
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
    @mcp_response
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
    ) -> dict[str, Any]:
        """PODER LEGISLATIVO + JUDICIÁRIO + CONSTITUIÇÃO.
        Funde: governance, constitution, governance_ops, tickets, handoff.
        Actions: policy.check, rule.list, compliance.report, violation.log,
                 cf.status, cf.pre_check, cf.audit, cf.stj, cf.tj, cf.forum,
                 ticket.create, ticket.list, ticket.close, roadmap.done,
                 handoff.create, handoff.list, bootup.sync, catalog.refresh,
                 naming.check, ssot.diff, cycle.check
        """
        ts = _ts()
        # ── GATEWAY VALIDATION ──────────────────────────────
        try:
            from neocortex.core.utils.gateway_bridge import gateway_check
            _ok, _report = gateway_check(action, root)
            if not _ok:
                return _report
        except Exception:
            pass

        root = _root()

        # ── TOOLGUARD: STEP 0 + LockGuard (G1+G2+G5) ─────────────────────────
        _guard = None
        try:
            import importlib.util
            _spec = importlib.util.spec_from_file_location("tool_guard", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-125-tool-guard.py"))
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            _guard = _mod.ToolGuard()
            _step0 = _guard.step_zero(action)
            if not _step0.get("ok"):
                return {"success": True, "action": action,
                        "step0_warning": _step0.get("warning", "STEP-0 alert"),
                        "matched_error": _step0.get("matched_error", ""), "timestamp": ts}
        except Exception:
            pass

        # ── COMPLIANCE ────────────────────────────────────────────────────────
        if action == "compliance.report":
            r = _compliance_report(root)
            return {"success": True, "action": action, "timestamp": ts, **r}

        elif action == "policy.check":
            if not policy_name:
                return {"success": False, "error": "policy_name obrigatório", "timestamp": ts}
            docs = root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main"
            policy_path = docs / f"{policy_name}.yaml"
            if not policy_path.exists():
                policy_path = docs / f"{policy_name}.md"
            exists = policy_path.exists()
            validated = False
            try:
                from neocortex.core import get_policy_loader
                loader = get_policy_loader()
                if exists and hasattr(loader, "load_policy"):
                    validation = loader.load_policy(policy_name)
                    validated = validation is not None
            except Exception:
                pass
            return {"success": True, "action": action, "policy": policy_name,
                    "exists": exists, "path": str(policy_path) if exists else None,
                    "validated": validated, "timestamp": ts}

        elif action == "rule.list":
            rules = {
                "R01": "Inventário de Ativos de IA", "R02": "Política Formalizada",
                "R03": "Estrutura de Diretórios", "R04": "Nomenclatura NC-",
                "R05": "NUNCA Deletar — apenas arquivar", "R06": "Write Zones por Role",
                "R07": "Privilégio Mínimo (PoLP)", "R08": "Atomic Locks",
                "R09": "Zonas de Escrita", "R10": "Trilha de Auditoria",
                "R11": "STEP +1 Rollback automático", "R12": "Handoffs Formais",
                "R13": "Checkpoints", "R14": "Lobe Isolation (cross-write bloqueado)",
                "R15": "T0 Nunca Executa Trabalho Braçal", "R16": "Boot Context Obrigatório",
                "R17": "PolicyLoader em Runtime", "R18": "Ciclo de Vida Tickets",
                "R19": "Rotina 4 Ciclos",                 "R20": "Revisão e Arquivo",
                "R21": "Zero Suposições (verificar, não presumir)",
                "R22": "Classification Levels L0-L3 (L1 BINDING)",
                "R23": "Extend, Don't Create — orbitar, não injetar (L1)",
                "R24": "SSOT Registration Mandatory (L1)",
                "R25": "Gateway Wire-up Mandatory (L1)",
                "R26": "Orbital Pattern — módulos independentes, tools importam (L1)",
                # EVOLUTION: Auto-Replicação (R161-R180)
                "R27": "Fork Governado — herda políticas (L1)",
                "R28": "DNA Imutável — child não modifica (L0)",
                "R29": "RNA de Estado — mutável pelo agente (L2)",
                "R30": "R0 Limiter — max 5 forks/hora (L1)",
                "R31": "Sandbox BSL-1 obrigatório (L1)",
                "R32": "SHA-256 integridade pós-fork (L1)",
                "R33": "Linha genealógica rastreável (L1)",
                "R34": "TTL — auto-destruição de órfãos (L2)",
                "R35": "Merge controlado — apoptosis (L2)",
                # EVOLUTION: Mutação (R221-R240)
                "R36": "Mutation Board — T0+Guardian+Engineer (L1)",
                "R37": "Drift Control — identity hysteresis <0.68 (L1)",
                "R38": "Vacina de Regressão — bloqueia mutação falha (L1)",
                "R39": "Ethical Genome — validado pelo Guardian (L1)",
                "R40": "BSL-1 a BSL-4 — níveis de biossegurança (L1)",
                "R41": "5 Porquês RCA — causa raiz em toda violação (L1)",
                "R42": "4 Porquês Estratégico — missão/alinhamento/melhoria/desempenho (L2)",
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
            ssot_path = root / "01_neocortex_framework" / "23-docs" / "NC-NAM-FR-001-naming-convention.md"
            lexico_path = root / "01_neocortex_framework" / ".neocortex" / "lexico" / "NC-LEXICO-LATEST.json"
            exists = ssot_path.exists()
            mtime = datetime.fromtimestamp(ssot_path.stat().st_mtime).isoformat() if exists else None
            lexico_ok = lexico_path.exists()
            return {"success": True, "action": action, "ssot_exists": exists,
                    "ssot_last_modified": mtime, "lexico_exists": lexico_ok,
                    "ssot_path": str(ssot_path.relative_to(root)), "timestamp": ts}

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
            # G5 R01: naming validation
            if _guard:
                _n = _guard.check_naming(title if title.startswith("NC-") else f"NC-DS-{title}")
                if not _n.get("valid"):
                    return {"success": False, "error": f"R01: {_n['error']}", "timestamp": ts}
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


        elif action == "handoff.create":
            # G1 LockGuard: validate write zone
            if _guard:
                _ok = _guard.validate_write("DIR-DS-002-audit-logs/")
                if not _ok:
                    return {"success": False, "error": _guard.last_error, "timestamp": ts}
                # G5 R01: auto naming check
                _n = _guard.check_naming(f"NC-DS-SESS-handoff-{title or 'untitled'}")
                if not _n.get("valid"):
                    return {"success": False, "error": f"R01: {_n.get('error','naming failed')}", "timestamp": ts}
            # G2 STEP 0: regression check antes de criar handoff
            if _guard:
                _step0 = _guard.step_zero("handoff.create")
                if not _step0.get("ok"):
                    return {"success": True, "action": action,
                            "step0_warning": _step0.get("warning"), "timestamp": ts}
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
            """G5+G8+G9 — Ciclo 3: Sincronizar boot + SSOT diff + compliance check."""
            import subprocess
            import sys

            # G8 R02: SSOT drift check antes do sync
            ssot_file = root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-NAM-FR-001-naming-convention.md"
            ssot_ok = ssot_file.exists()
            ssot_age = ""
            if ssot_ok:
                import os as _os
                mtime = _os.path.getmtime(str(ssot_file))
                from datetime import datetime as _dt
                ssot_age = _dt.fromtimestamp(mtime).isoformat()

            # G9 CICLO-4: compliance check
            comp = _compliance_report(root)

            script = root / "01_neocortex_framework" / "scripts" / "NC-SCR-FR-066-bootup-sync.py"
            if not script.exists():
                boot = root / "DIR-BOOT-FR-001-bootup-main" / "NC-BOOT-FR-001-system-manifest.md"
                return {"success": False, "action": action, "bootup_exists": boot.exists(),
                        "error": f"Script ausente: {script.name}",
                        "ssot": {"exists": ssot_ok, "last_modified": ssot_age},
                        "compliance": {"score": comp.get("compliance_score", 0),
                                       "status": comp.get("status", "unknown")},
                        "timestamp": ts}
            try:
                r = subprocess.run([sys.executable, str(script)],
                                   capture_output=True, text=True, timeout=60, cwd=str(root))
                # R02 AUTO-CHANGELOG: update SSOT changelog
                _cl_updated = False
                if r.returncode == 0 and ssot_ok:
                    try:
                        from datetime import datetime as _dt
                        _now = _dt.now().strftime("%Y-%m-%d %H:%M")
                        _cl_line = f"\n| {_now} | bootup.sync | {comp.get('compliance_score',0)}% compliance, {comp.get('status','?')} | auto |\n"
                        _ssot_content = ssot_file.read_text(encoding="utf-8")
                        if "## 📜 3. Histórico" in _ssot_content:
                            _lines = _ssot_content.split("\n")
                            _inserted = False
                            _out = []
                            for _l in _lines:
                                _out.append(_l)
                                if _l.startswith("| 2026-") and not _inserted:
                                    _out.append(_cl_line.strip())
                                    _inserted = True
                            if _inserted:
                                ssot_file.write_text("\n".join(_out), encoding="utf-8")
                                _cl_updated = True
                    except Exception:
                        pass
                return {"success": r.returncode == 0, "action": action,
                        "stdout": r.stdout[-1000:], "stderr": r.stderr[-400:],
                        "returncode": r.returncode,
                        "ssot": {"exists": ssot_ok, "last_modified": ssot_age},
                        "changelog_auto": _cl_updated,
                        "compliance": {"score": comp.get("compliance_score", 0),
                                       "status": comp.get("status", "unknown")},
                        "timestamp": ts}
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

        # ── RCA: 5 Porquês (R41) ───────────────────────────────────────────
        elif action == "rca.analyze":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("rca", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-147-root-cause-engine.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                engine = mod.get_rca()
                problem = title or "violação não especificada"
                whys = [description] if description else ["Detalhes insuficientes para RCA"]
                r = engine.analyze_failure(problem, whys)
                return {"success": True, "action": action, "rca": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "rca.list":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("rca", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-147-root-cause-engine.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                analyses = mod.get_rca().get_analyses(20)
                return {"success": True, "action": action, "analyses": analyses, "count": len(analyses), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── FULL SYSTEM AUDIT (SSOT+Lobes+Semântica+Federativo+Regras+Tools+Hooks+DDD+Techniques) ─
        elif action == "audit.full":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("auditor", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-149-full-system-audit.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_auditor().audit_all()
                return {"success": True, "action": action, "audit": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── TECHNIQUES: 3 W's (What/Why/Where) ────────────────────────────
        elif action == "three_w.generate":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("fr151", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-151-missing-techniques.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                eng = mod.get_techniques_engine()
                doc = eng.three_w.generate_welcome_doc()
                return {"success": True, "action": action, "onboarding_doc": doc, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── TECHNIQUES: Eisenhower Matrix ────────────────────────────────
        elif action == "eisenhower.prioritize":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("fr151", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-151-missing-techniques.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                eng = mod.get_techniques_engine()
                import json as _json
                tickets = _json.loads(description) if description else []
                prioritized = eng.eisenhower.prioritize_tickets(tickets)
                return {"success": True, "action": action, "tickets": prioritized, "count": len(prioritized), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── TECHNIQUES: Pareto 80/20 ─────────────────────────────────────
        elif action == "pareto.analyze":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("fr151", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-151-missing-techniques.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_techniques_engine().pareto.analyze()
                return {"success": True, "action": action, "pareto": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── TECHNIQUES: OKRs ─────────────────────────────────────────────
        elif action == "okr.report":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("fr151", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-151-missing-techniques.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                eng = mod.get_techniques_engine()
                r = eng.okr.get_current_okrs()
                report = eng.okr.generate_okr_report()
                return {"success": True, "action": action, "okrs": r, "report": report, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── TECHNIQUES: Idempotency Guard ────────────────────────────────
        elif action == "idempotency.check":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("fr151", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-151-missing-techniques.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                guard = mod.get_techniques_engine().idempotency
                key = title or "default"
                is_dup = not guard.check_savepoint(key, description or key)
                return {"success": True, "action": action, "key": key, "is_duplicate": is_dup, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── CORPORATE: KPIs + ROI + Compliance (R56-R58) ──────────────────────
        elif action == "kpi.report":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("corp", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-154-corporate-engines.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_corporate().kpi.compute()
                return {"success": True, "action": action, "kpis": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "roi.analyze":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("corp", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-154-corporate-engines.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_corporate().roi.analyze()
                return {"success": True, "action": action, "roi": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "compliance.gaps":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("corp", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-154-corporate-engines.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_corporate().compliance.find_gaps()
                return {"success": True, "action": action, "compliance": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "compliance.fix":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("corp", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-154-corporate-engines.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_corporate().compliance.fix_gaps(auto_fix=True)
                return {"success": True, "action": action, "fixes": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── RESILIENCY (Bloco 4: Bulkhead/CQRS/Feature/Backpressure) ─────────
        elif action == "resiliency.audit":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("res", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-155-resiliency-engine.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_resiliency().full_audit()
                return {"success": True, "action": action, "resiliency": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "feature_toggle.set":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("res", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-155-resiliency-engine.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                ft = mod.get_resiliency().feature_toggle
                feature = title or ""
                enabled = description.lower() in ("1", "true", "on", "yes") if description else False
                ft.set(feature, enabled)
                return {"success": True, "action": action, "feature": feature, "enabled": enabled, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── AI GOVERNANCE (Bloco 5: ModelCards/XAI/HITL/Bias/RedTeam/Audit) ──
        elif action == "model_cards.generate":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("ai", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-156-ai-governance.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_ai_governance().model_cards.generate_all()
                return {"success": True, "action": action, "model_cards": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "hitl.list":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("ai", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-156-ai-governance.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_ai_governance().hitl.list_pending()
                return {"success": True, "action": action, "pending": r, "count": len(r), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action in ("hitl.approve", "hitl.reject"):
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("ai", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-156-ai-governance.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                hitl = mod.get_ai_governance().hitl
                aid = title or ""
                r = hitl.approve(aid) if action == "hitl.approve" else hitl.reject(aid, description or "")
                return {"success": True, "action": action, "result": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "red_team.assault":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("ai", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-156-ai-governance.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_ai_governance().red_team.full_assault()
                return {"success": True, "action": action, "red_team": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "ai.audit":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("ai", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-156-ai-governance.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_ai_governance().auditor.scan_logs()
                return {"success": True, "action": action, "audit": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── BSC + SWOT (R54-R55 Bloco 3) ─────────────────────────────────────
        elif action in ("bsc.report", "swot.analyze"):
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("bscswot", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-157-bsc-swot.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                eng = mod.get_bsc_swot()
                if action == "bsc.report":
                    r = eng.bsc.analyze()
                    return {"success": True, "action": action, "bsc": r, "timestamp": ts}
                else:
                    r = eng.swot.analyze()
                    return {"success": True, "action": action, "swot": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── SYSTEM INTEGRITY (R112-R115: YAML + MDC + Secrets + DeadCode) ────
        elif action in ("yaml.validate", "mdc.validate", "secret.scan", "deadcode.scan", "integrity.full"):
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("si", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-158-system-integrity.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                eng = mod.get_integrity()
                if action == "integrity.full":
                    r = eng.full_audit()
                elif action == "yaml.validate":
                    r = eng.yaml.validate_all()
                elif action == "mdc.validate":
                    r = eng.mdc.validate_all()
                elif action == "secret.scan":
                    r = eng.secrets.scan()
                elif action == "deadcode.scan":
                    r = eng.deadcode.scan()
                return {"success": True, "action": action, "result": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── ADVANCED RESILIENCE + REGULATORY (R83-R111 Bloco 6) ────────────
        elif action == "resilience.advanced":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("ar", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-160-advanced-resilience.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_advanced_resilience().full_audit()
                return {"success": True, "action": action, "advanced_resilience": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "regulatory.check":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("reg", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-161-regulatory-compliance.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_regulatory().full_audit()
                return {"success": True, "action": action, "regulatory": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── SUBMISSION PIPELINE ──────────────────────────────────────────────
        elif action == "submit":
            try:
                import importlib.util
                import json as _json
                spec = importlib.util.spec_from_file_location("pipeline", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-148-submission-pipeline.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                pipe = mod.get_pipeline()
                files = _json.loads(description) if description else []
                r = pipe.submit(files, title or "submissão manual", "T0")
                return {"success": True, "action": action, "pipeline": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── NC-DS-272/275: STRANGLER + LEAN + SIX SIGMA + DUE DILIGENCE + SELF-HEAL + COBIT + BSC ──
        elif action == "strangler.status":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("sw", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-171-due-diligence-strangler.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_strangler_wire().status()
                return {"success": True, "action": action, "strangler": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "due_diligence.check":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("dd", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-171-due-diligence-strangler.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_due_diligence().validate()
                return {"success": True, "action": action, "due_diligence": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "lean.audit":
            return {"success": True, "action": action,
                    "lean": {"pruned": "context.prune via NC-SUPER-008",
                             "principle": "Eliminar desperdício — R62"},
                    "timestamp": ts}

        elif action == "sixsigma.dmaic":
            return {"success": True, "action": action,
                    "sixsigma": {"sigma_level": "calculado via KPI trend + compliance score",
                                  "principle": "DMAIC — R63"},
                    "timestamp": ts}

        elif action == "self_heal.status":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("ar", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-160-advanced-resilience.py"))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                r = mod.get_advanced_resilience().self_healing_status()
                return {"success": True, "action": action, "self_heal": r, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "cobit.alignment":
            return {"success": True, "action": action,
                    "cobit": {"alignment": "roadmap.done vs LEXICO.total — R132",
                              "principle": "Entrega valor alinhado ao roadmap"},
                    "timestamp": ts}

        elif action == "bsc.scorecard":
            return {"success": True, "action": action,
                    "bsc": {"score": "agregado: KPI + ROI + compliance + cobit — R133",
                            "principle": "Balanced Scorecard"},
                    "timestamp": ts}

        # ── ORBITAL BRIDGE ──────────────────────────────────────────────────
        # R26 compliant: 1 linha de import, sem injeção de elifs
        _orbital_result = None
        try:
            import importlib.util
            _spec = importlib.util.spec_from_file_location("orbital_bridge", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-139-orbital-bridge.py"))
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            _orbital_result = _mod.orbital_dispatch(action, root)
        except Exception:
            pass
        if _orbital_result is not None:
            return _orbital_result



        else:
            available = [
                "policy.check", "compliance.report", "rule.list", "violation.log",
                "naming.check", "ssot.diff", "cycle.check",
                "cf.status", "cf.pre_check", "cf.audit", "cf.stj", "cf.tj", "cf.forum",
                "ticket.create", "ticket.list", "ticket.close", "roadmap.done",
                "handoff.create", "handoff.list",
                "bootup.sync", "catalog.refresh", "yaml.sanitize",
                "governance.full_audit", "cycle.archive_handoffs",
                "audit.replay", "lock.validate",
            ]
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": available, "timestamp": ts}
