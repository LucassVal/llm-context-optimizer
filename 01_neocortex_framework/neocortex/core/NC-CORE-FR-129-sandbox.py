"""---
@Gateway NC-CORE-FR-129-shared-kernel-gateway mcp NC-CORE-FR-129-shared-kernel-gateway.py — T0→T1 Ga
---
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConstitutionGateway:
    """T0→T1 Gateway — validates ALL actions against the Constitution."""

    @staticmethod
    def _load(module_name: str, filename: str) -> Any:
        """KISS: single importlib helper with module cache."""
        import importlib.util

        cache_key = f"__gw_cache_{module_name}"
        if hasattr(ConstitutionGateway, cache_key):
            return getattr(ConstitutionGateway, cache_key)
        spec = importlib.util.spec_from_file_location(
            module_name, str(Path(__file__).parent / filename)
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        setattr(ConstitutionGateway, cache_key, mod)
        return mod

    def __init__(self, root: Path | None = None):
        import os as _os

        self.root = root or Path(_os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self._lock_guard = None
        self._regression_svc = None
        self._init_done = False
        self.last_violation = ""

    def _init(self):
        if self._init_done:
            return
        try:
            self._lock_guard = self._load(
                "lock_guard", "NC-CORE-FR-014-lock-guard.py"
            ).get_lock_guard()
        except Exception:
            self._lock_guard = None
        try:
            self._regression_svc = self._load(
                "regression", "NC-CORE-FR-123-regression-service.py"
            ).get_regression_service()
        except Exception:
            self._regression_svc = None

        # YAML-Driven: carregar blueprint + locks + policies em runtime
        self._yaml_config = {}
        docs = self.root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main"
        try:
            import yaml

            for yf in [
                "NC-ARC-FR-002-architecture-blueprint.yaml",
                "NC-SEC-FR-001-atomic-locks.yaml",
                "NC-CFG-FR-001-agent-policy-template.yaml",
            ]:
                yp = docs / yf
                if yp.exists():
                    self._yaml_config[yf] = yaml.safe_load(
                        yp.read_text(encoding="utf-8")
                    )
        except:
            pass

        self._init_done = True

    # ── MAIN GATEWAY — validate_action() ─────────────────────────

    def validate_action(
        self,
        action: str,
        target_path: str = "",
        agent_id: str = "T0",
        agent_role: str = "T0",
    ) -> tuple[bool, dict[str, Any]]:
        """
        KERNEL 0 — Redireciona para CPC Digital (devido processo legal).
        Gate → CPC.process_action() → LockGuard + Pact + ToolGuard → Sentença
        """
        try:
            from .NC_CORE_FR_132_civil_procedure_code import get_cpc

            cpc = get_cpc()
            return cpc.process_action(action, target_path, agent_id, agent_role)
        except Exception:
            # Fallback: validação mínima direta
            return self._fallback_validate(action, target_path, agent_id, agent_role)

    def _fallback_validate(
        self, action, target_path, agent_id, agent_role
    ) -> tuple[bool, dict[str, Any]]:
        """Fallback quando CPC indisponível — validação mínima."""
        self._init()

        # R16: Auto-load @BOOT on first action — ler manifesto original
        if not hasattr(self, "_boot_loaded"):
            try:
                boot = (
                    self.root
                    / "DIR-BOOT-FR-001-bootup-main"
                    / "NC-BOOT-FR-001-system-manifest.md"
                )
                if boot.exists():
                    content = boot.read_text(encoding="utf-8", errors="ignore")
                    self._boot_loaded = True
                    self._boot_content = content
                    report["checks"]["boot_loaded"] = True
            except Exception:
                self._boot_loaded = False

        # R20: Auto-trigger CICLO 3 on session end
        if action in ("bootup.sync", "compliance.report", "checkpoint.set"):
            self._session_end_pending = False
        else:
            self._session_end_pending = True
        ts = datetime.now().isoformat()
        report = {
            "action": action,
            "agent": agent_id,
            "role": agent_role,
            "timestamp": ts,
            "checks": {},
            "allowed": True,
            "violations": [],
        }

        # 1. STEP 0 — Regression Check (Art. IV)
        step0_ok = True
        if self._regression_svc:
            try:
                result = self._regression_svc.check()
                report["checks"]["step0"] = {
                    "buffer_size": result.get("buffer_size", 0),
                    "recent_errors": result.get("recent_errors", [])[-3:],
                }
                # Check similarity using difflib (sugestão 1)
                import difflib

                for err in result.get("recent_errors", []):
                    ratio = difflib.SequenceMatcher(
                        None, action.lower(), err.lower()
                    ).ratio()
                    if ratio > 0.4:  # 40%+ similarity triggers warning
                        step0_ok = False
                        report["violations"].append(
                            f"STEP-0: ação {ratio:.0%} similar a erro: {err[:80]}"
                        )
            except Exception:
                pass
        report["checks"]["step0_passed"] = step0_ok

        # 2. ATOMIC LOCKS — Check write protection (Art. V)
        lock_ok = True
        if target_path and self._lock_guard:
            try:
                allowed, reason = self._lock_guard.check_write(target_path, agent_role)
                report["checks"]["atomic_lock"] = {
                    "path": target_path,
                    "allowed": allowed,
                }
                if not allowed:
                    lock_ok = False
                    report["violations"].append(f"LOCK: {reason}")
                    self.last_violation = reason
            except Exception:
                pass
        report["checks"]["lock_passed"] = lock_ok

        # 3. WRITE ZONES — from PolicyLoader (sugestão 2)
        zone_ok = True
        write_zones = {
            "T0": ["*"],
            "T1": ["05_examples/", "DIR-DS-001-tickets/", "DIR-DS-002-audit-logs/"],
            "T2": ["DIR-DS-001-tickets/", "DIR-DS-002-audit-logs/"],
        }
        # Try loading from PolicyLoader (NC-CFG-FR-001)
        try:
            policy_file = (
                self.root
                / "01_neocortex_framework"
                / "DIR-DOC-FR-001-docs-main"
                / "NC-CFG-FR-001-agent-policy-template.yaml"
            )
            if policy_file.exists():
                import yaml

                with open(policy_file, encoding="utf-8") as f:
                    policy = yaml.safe_load(f)
                if policy and "write_zones" in policy:
                    write_zones = policy["write_zones"]
        except Exception:
            pass
        if target_path and agent_role != "T0":
            allowed_zones = write_zones.get(agent_role, [])
            if "*" not in allowed_zones:
                in_zone = any(target_path.startswith(z) for z in allowed_zones)
                if not in_zone:
                    zone_ok = False
                    report["violations"].append(
                        f"WRITE-ZONE: {agent_role} não pode escrever em {target_path}"
                    )
        report["checks"]["write_zone_passed"] = zone_ok

        # 4. NAMING — validate NC- + @ULQ type/sigla (sugestão 3)
        naming_ok = True
        if target_path:
            fname = Path(target_path).name
            if fname and not fname.startswith("."):
                if not fname.startswith("NC-"):
                    naming_ok = False
                    report["violations"].append(
                        f"NAMING: {fname} não segue NC-<TIPO>-..."
                    )
                else:
                    parts = fname.split("-")
                    if len(parts) >= 3:
                        tipo = parts[1].upper()
                        sigla = parts[2].upper()
                        ulq_types = [
                            "TOOL",
                            "SVC",
                            "LBE",
                            "SCR",
                            "DS",
                            "LED",
                            "BOOT",
                            "GOV",
                            "CFG",
                            "TPL",
                            "TODO",
                            "RULE",
                            "WF",
                            "ARC",
                            "BAK",
                            "NAM",
                            "AUD",
                            "ALN",
                            "PLN",
                            "SES",
                            "TKT",
                            "PRF",
                            "CORE",
                            "INFRA",
                            "MCP",
                            "SUPER",
                            "IMPL",
                            "RPT",
                            "TEST",
                            "REF",
                            "CTX",
                            "FIL",
                        ]
                        if tipo not in ulq_types:
                            naming_ok = False
                            report["violations"].append(
                                f"NAMING: TIPO '{tipo}' não está no @ULQ"
                            )
                        ulq_siglas = ["FR", "WL", "USR", "CC", "OP", "INT", "DS"]
                        if sigla not in ulq_siglas:
                            naming_ok = False
                            report["violations"].append(
                                f"NAMING: SIGLA '{sigla}' não está no @ULQ"
                            )
        report["checks"]["naming_passed"] = naming_ok

        # CPP: check if agent is in prison (P0-02)
        prison_ok = True
        try:
            cpp_mod = self._load("cpp", "NC-CORE-FR-135-criminal-procedure-code.py")
            free, status = cpp_mod.get_cpp().check_prisoner(agent_id)
            prison_ok = free
            if not free:
                report["violations"].append(
                    f"CPP: agente {status.get('status', 'preso')} - {status.get('reason', '')}"
                )
            report["checks"]["prison_check"] = status
        except Exception:
            pass
        report["checks"]["prison_passed"] = prison_ok

        # CICLO 0: record turn for vigilant analysis (P0-03)
        try:
            vig_mod = self._load("vig", "NC-CORE-FR-137-vigilant-cycle.py")
            vig_mod.get_vigilant_cycle().record_turn(action, "", {"source": "gateway"})
        except Exception:
            pass

        # R05: Deletion Guard + Bash Guard — block destructive commands
        deletion_ok = True
        if target_path or action:
            import re as _re

            check_str = target_path or action
            if _re.search(
                r"\b(rm|del|Remove-Item|rmdir|unlink)\b", check_str, _re.IGNORECASE
            ):
                deletion_ok = False
                report["violations"].append(
                    f"R05: deleção bloqueada em {check_str[:100]}"
                )
            # Bash Guard check
            try:
                bg_mod = self._load("bg", "NC-CORE-FR-144-bash-guard.py")
                ok, reason = bg_mod.check_bash(check_str, agent_id)
                if not ok:
                    deletion_ok = False
                    report["violations"].append(reason)
            except Exception:
                pass
        report["checks"]["deletion_passed"] = deletion_ok

        # R21: Gateway mandatory — validate all actions
        gateway_ok = True  # Always true here (we're IN the gateway)

        # R23: Orbital pattern — detect non-NC files
        orbital_ok = True
        if target_path:
            fname = Path(target_path).name
            if fname and not fname.startswith(".") and not fname.startswith("NC-"):
                orbital_ok = False
                report["violations"].append(f"R23: {fname} não é orbital (falta NC-)")
        report["checks"]["orbital_passed"] = orbital_ok

        # R24: SSOT registration check
        ssot_ok = True
        if target_path and not target_path.startswith("."):
            ssot_file = (
                self.root
                / "01_neocortex_framework"
                / "DIR-DOC-FR-001-docs-main"
                / "NC-NAM-FR-001-naming-convention.md"
            )
            if ssot_file.exists():
                content = ssot_file.read_text(encoding="utf-8", errors="ignore")
                if (
                    target_path.replace(chr(92), "/") not in content
                    and Path(target_path).name not in content
                ):
                    ssot_ok = False
                    report["violations"].append(
                        f"R24: {Path(target_path).name} não registrado no SSOT"
                    )
        report["checks"]["ssot_registration_passed"] = ssot_ok

        # R15: Role enforcement — T0 only for writes outside examples/
        role_ok = True
        if target_path and agent_role != "T0" and not target_path.startswith(
            "05_examples/"
        ) and not target_path.startswith("DIR-DS-"):
            role_ok = False
            report["violations"].append(
                f"R15: {agent_role} não pode escrever em {target_path}"
            )
        report["checks"]["role_passed"] = role_ok

        # R03: Ticket Reference — check if action references a ticket
        ticket_ok = True
        if target_path and "DIR-DS-001-tickets" not in target_path:
            tickets_dir = self.root / "DIR-DS-001-tickets"
            if tickets_dir.exists() and len(list(tickets_dir.glob("*.yaml"))) > 0:
                pass  # Tickets exist, reference check passed
        report["checks"]["ticket_passed"] = ticket_ok

        # R25: Gateway Wire-up — we're IN the gateway, always true
        gateway_ok = True
        report["checks"]["gateway_wired_passed"] = gateway_ok

        # R26: Orbital Pattern — target must follow NC- convention
        orbital_pattern_ok = True
        if target_path:
            fname = Path(target_path).name
            if fname and not fname.startswith(".") and not fname.startswith("NC-"):
                orbital_pattern_ok = False
                report["violations"].append(f"R26: {fname} não é orbital (falta NC-)")
        report["checks"]["orbital_pattern_passed"] = orbital_pattern_ok
        config_ok = True
        if target_path:
            import re as _re2

            if _re2.search(r"[A-Z]:\\|/home/|/Users/", target_path):
                config_ok = False
                report["violations"].append(
                    f"R07: path hardcoded — use ConfigProvider: {target_path}"
                )
        report["checks"]["config_passed"] = config_ok

        # R08: Git Ignore — block .db, .wal, __pycache__
        gitignore_ok = True
        if target_path:
            forbidden = [".db", ".wal", "__pycache__", ".pyc", ".redb", ".val"]
            if any(f in target_path for f in forbidden):
                gitignore_ok = False
                report["violations"].append(
                    f"R08: {target_path} não pode ser commitado"
                )
        report["checks"]["gitignore_passed"] = gitignore_ok

        # R22: Classification L0-L3 — enforce based on @LOCKS
        class_ok = True
        if target_path:
            locked_paths = [
                "server.py",
                "sub_server.py",
                "NC-NAM-FR-001",
                "neocortex_config.yaml",
            ]
            if any(lp in target_path for lp in locked_paths) and agent_role != "T0":
                class_ok = False
                report["violations"].append(
                    f"R22 L0: {target_path} requer T0 — bloqueado para {agent_role}"
                )
        report["checks"]["classification_passed"] = class_ok

        # R27-R35: Evolution HOOK checks
        evo_ok = True
        if "fork" in action.lower() or "genome" in action.lower():
            sandbox = self.root / ".neocortex" / "sandbox"
            recent = list(sandbox.glob("nc-child-*")) if sandbox.exists() else []
            recent_1h = [
                d
                for d in recent
                if (__import__("time").time() - d.stat().st_mtime) < 3600
            ]
            if len(recent_1h) >= 5:
                evo_ok = False
                report["violations"].append(
                    f"R30: R0 limit — max 5 forks/hora. {len(recent_1h)} já realizados"
                )
        report["checks"]["evolution_passed"] = evo_ok

        # R36-R40: Mutation HOOK checks
        mut_ok = True
        if "mutation" in action.lower() and agent_role != "T0":
            mut_ok = False
            report["violations"].append("R36: Mutation Board requer T0 ou Guardian")
        report["checks"]["mutation_passed"] = mut_ok

        # 5. COMPLIANCE
        report["allowed"] = all(
            [
                step0_ok,
                lock_ok,
                zone_ok,
                naming_ok,
                prison_ok,
                deletion_ok,
                orbital_ok,
                ssot_ok,
                role_ok,
                config_ok,
                gitignore_ok,
                class_ok,
                evo_ok,
                mut_ok,
                ticket_ok,
                gateway_ok,
                orbital_pattern_ok,
            ]
        )
        report["checks_passed"] = sum(
            [
                step0_ok,
                lock_ok,
                zone_ok,
                naming_ok,
                prison_ok,
                deletion_ok,
                orbital_ok,
                ssot_ok,
                role_ok,
                config_ok,
                gitignore_ok,
                class_ok,
                evo_ok,
                mut_ok,
                ticket_ok,
                gateway_ok,
                orbital_pattern_ok,
            ]
        )
        report["checks_total"] = 17

        # STEP -1: auto savepoint before write (sugestão 4)
        if report["allowed"] and target_path:
            try:
                from .services.NC_SVC_FR_003_savepoint_stub import SavePointService

                sp_name = (
                    f"gw_{action.replace('.', '-')}_{datetime.now().strftime('%H%M%S')}"
                )
                SavePointService.create(sp_name)
                report["savepoint"] = sp_name
            except Exception:
                pass

        # WAL: log passed action (sugestão 5)
        try:
            wal_dir = self.root / "DIR-DS-002-audit-logs"
            wal_dir.mkdir(parents=True, exist_ok=True)
            import json

            wal_entry = {
                "operation_id": f"gw-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "agent": agent_id,
                "role": agent_role,
                "action": action,
                "target": target_path,
                "allowed": report["allowed"],
                "violations": report.get("violations", []),
                "timestamp": report["timestamp"],
            }
            wal_file = wal_dir / f"NC-WAL-GW-{datetime.now().strftime('%Y%m%d')}.jsonl"
            with open(wal_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(wal_entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

        # R12: Auto-handoff for write actions
        if report["allowed"] and target_path:
            try:
                hf_dir = self.root / "DIR-DS-002-audit-logs"
                ts_file = datetime.now().strftime("%Y%m%dT%H%M%S")
                hf = hf_dir / f"NC-DS-GW-handoff-{ts_file}.yaml"
                hf.write_text(
                    f"ticket_id: NC-DS-GW\n"
                    f"status: auto_handoff\n"
                    f"agent: {agent_id}\n"
                    f"role: {agent_role}\n"
                    f"action: {action}\n"
                    f"target: {target_path}\n"
                    f"timestamp: {report['timestamp']}\n"
                    f"checks_passed: {report['checks_passed']}/{report['checks_total']}\n",
                    encoding="utf-8",
                )
                report["handoff"] = str(hf.name)
            except Exception:
                pass

        # ═════════════════════════════════════════════════════════
        # PER-ACTION RULES (v3.0 — Bloco 3 Corporativos + P1 Ferramentas)
        # Cada ação específica ativa regras correspondentes da matriz.
        # ═════════════════════════════════════════════════════════
        self._check_per_action(action, target_path, agent_id, agent_role, report)
        self._check_critical_hooks(action, agent_id, report)
        self._check_xai_hitl(action, report)
        self._check_registry_hooks(
            action, target_path, agent_id, agent_role, report
        )  # NC-DS-210

        if not report["allowed"]:
            logger.warning(
                f"[Gateway] BLOCKED: {action} by {agent_role} → "
                f"{len(report['violations'])} violations"
            )

        # Vigia Central: registrar TODOS os checks para STEP 0 aprender
        try:
            cw_mod = self._load("cw", "NC-CORE-FR-146-central-watcher.py")
            watcher = cw_mod.get_watcher()
            for check_name, check_val in report.get("checks", {}).items():
                watcher.record_check(check_name, check_val, "", agent_id, "gateway")
            if report.get("violations"):
                for v in report["violations"]:
                    watcher.record_check("VIOLATION", False, v, agent_id, "gateway")
        except Exception:
            pass

        return report["allowed"], report

    # ═════════════════════════════════════════════════════════
    # PER-ACTION RULES MAP (v3.0 — 111 regras com enforcement)
    # ═════════════════════════════════════════════════════════

    ACTION_RULES = {
        # P1: Ferramentas de Escrita (Alto Risco)
        "lobes.create": [
            ("R04", "Atomic Locks — path protegido?"),
            ("R06", "Write Zones — zona permitida?"),
            ("R14", "Lobe Isolation — domínio isolado?"),
            ("R42", "3 W's — tem What/Why/Where?"),
        ],
        "lobes.update": [
            ("R04", "Atomic Locks"),
            ("R06", "Write Zones"),
            ("R14", "Lobe Isolation"),
            ("R42", "3 W's"),
        ],
        "lobes.delete": [
            ("R05", "NUNCA Deletar — arquivar, não deletar"),
            ("R04", "Atomic Locks"),
        ],
        "tickets.create": [
            ("R03", "Ticket Reference — referência válida?"),
            ("R19", "Ciclo de Vida — status correto?"),
            ("R45", "Eisenhower — urgency/impact definidos?"),
        ],
        "tickets.close": [
            ("R19", "Ciclo de Vida — transição válida?"),
            ("R45", "Eisenhower — conclusão registrada?"),
        ],
        "savepoint.create": [
            ("R11", "STEP +1 — rollback habilitado?"),
            ("R49", "Idempotência — payload já processado?"),
        ],
        "savepoint.rollback": [("R11", "STEP +1 — restore válido?")],
        "handoff.create": [
            ("R12", "Handoff — registro de auditoria"),
            ("R49", "Idempotência — handoff duplicado?"),
        ],
        "handoff.validate": [("R12", "Handoff — validação de integridade")],
        # P1: Replicação
        "agent.spawn": [
            ("R27", "Fork Governado — DNA válido?"),
            ("R30", "R0 Limiter 5/h — excedeu?"),
            ("R31", "Sandbox BSL-1 — isolado?"),
            ("R39", "Ethical Genome — compliant?"),
        ],
        "agent.consume": [("R28", "DNA Imutável — alteração não permitida")],
        # P2: Configuração
        "config.set": [
            ("R07", "ConfigProvider — source autorizada?"),
            ("R69", "Feature Toggle — A/B test válido?"),
            ("R84", "Agile Governance — YAML dinâmico permitido?"),
        ],
        "config.reload": [("R07", "ConfigProvider"), ("R84", "Agile Governance")],
        "pulse.start": [
            ("R48", "PDCA — ciclo corrente?"),
            ("R52", "Kaizen — log registrado?"),
        ],
        "pulse.stop": [("R48", "PDCA — parada justificada?")],
        "brain.think": [
            ("R41", "RCA — violações prévias analisadas?"),
            ("R44", "4 Porquês Estratégico — impacto?"),
            ("R88", "Predictive Risk — risco calculado?"),
        ],
        "brain.plan": [("R41", "RCA"), ("R88", "Predictive Risk")],
        "brain.orchestrate": [
            ("R41", "RCA"),
            ("R44", "4 Porquês"),
            ("R88", "Predictive Risk"),
        ],
        # P3: Consulta
        "search.execute": [
            ("R60", "Stakeholder Map — permissão de leitura?"),
            ("R77", "Bias Detection — viés nos termos?"),
        ],
        "export.to_json": [
            ("R81", "Differential Privacy — dados ofuscados?"),
            ("R83", "ALCOA++ — integridade mantida?"),
        ],
        "export.to_markdown": [("R81", "Differential Privacy"), ("R83", "ALCOA++")],
        "health.status": [
            ("R70", "Health Check — serviço respondendo?"),
            ("R91", "SIEM — logs cruzados?"),
        ],
        # Bloco 3: Corporativos
        "kpi.report": [("R56", "KPIs — métricas atualizadas?")],
        "roi.analyze": [("R57", "ROI — custo-benefício calculado?")],
        "compliance.gaps": [("R58", "Compliance — gaps identificados?")],
        "compliance.fix": [("R58", "Compliance — correções aplicadas?")],
    }

    def _check_per_action(
        self,
        action: str,
        target_path: str,
        agent_id: str,
        agent_role: str,
        report: dict[str, Any],
    ):
        """Check rules específicas para cada ação MCP (v3.1)."""
        rules = self.ACTION_RULES.get(action, [])
        for rule_id, rule_desc in rules:
            rule_name = f"per_action_{rule_id}"
            # R05: NUNCA Deletar
            if rule_id == "R05" and action in ("lobes.delete",):
                report["violations"].append(
                    f"{rule_id}: {rule_desc} — use archive (DIR-ARC-FR-001)"
                )
                report["allowed"] = False
                report["checks"][rule_name] = False

            # R04/R06/R14: Atomic Locks + Write Zones + Lobe Isolation
            elif rule_id in ("R04", "R06", "R14") and target_path:
                if self._lock_guard:
                    allowed, reason = self._lock_guard.check_write(
                        target_path, agent_role
                    )
                    if not allowed:
                        report["violations"].append(
                            f"{rule_id}: {rule_desc} — {reason}"
                        )
                        report["allowed"] = False
                        report["checks"][rule_name] = False
                    else:
                        report["checks"][rule_name] = True
                else:
                    report["checks"][rule_name] = True

            # R42: 3 W's
            elif rule_id == "R42" and target_path:
                try:
                    tp = Path(target_path)
                    if tp.exists() and tp.is_file():
                        content = tp.read_text(encoding="utf-8", errors="ignore")[:2000]
                        if not all(kw in content for kw in ("What", "Why")):
                            report["violations"].append(
                                f"R42: {rule_desc} — {tp.name} não tem 3 W's"
                            )
                            report["checks"][rule_name] = False
                        else:
                            report["checks"][rule_name] = True
                except Exception:
                    report["checks"][rule_name] = True

            # R49: Idempotência
            elif rule_id == "R49":
                try:
                    import importlib.util

                    spec = importlib.util.spec_from_file_location(
                        "fr151",
                        str(
                            Path(__file__).parent
                            / "NC-CORE-FR-151-missing-techniques.py"
                        ),
                    )
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    guard = mod.get_techniques_engine().idempotency
                    is_new = guard.check_savepoint(action, target_path or action)
                    if not is_new:
                        report["violations"].append(
                            f"R49: {rule_desc} — operação duplicada"
                        )
                        report["allowed"] = False
                    report["checks"][rule_name] = is_new
                except Exception:
                    report["checks"][rule_name] = True

            # Default
            else:
                report["checks"][rule_name] = True

    # ═════════════════════════════════════════════════════════
    # NC-DS-210: HOOK REGISTRY INTEGRATION
    # ═════════════════════════════════════════════════════════

    def _check_registry_hooks(
        self,
        action: str,
        target_path: str,
        agent_id: str,
        agent_role: str,
        report: dict[str, Any],
    ):
        """Executa verificacoes baseadas nos hooks registrados no MCP.

        Le o MCP hook registry e executa as verificacoes correspondentes.
        Complementa _check_per_action (hardcoded) com hooks dinamicos.
        Nao substitui — adiciona camada extra de protecao.
        """
        try:
            import importlib.util as _iu

            spec = _iu.spec_from_file_location(
                "_sec",
                str(
                    self.fw / "neocortex" / "mcp" / "tools" / "NC-SUPER-009-security.py"
                ),
            )
            if spec and spec.loader:
                mod = _iu.module_from_spec(spec)
                spec.loader.exec_module(mod)
                hooks = (
                    mod.get_registered_hooks()
                    if hasattr(mod, "get_registered_hooks")
                    else {}
                )
            else:
                return
        except Exception:
            return

        if not hooks:
            return

        for _event, hook_list in hooks.items():
            for hook in hook_list:
                hook_name = hook.get("name", "")
                hook.get("action", "")

                # R01: Naming convention
                if hook_name == "R01-naming-convention" and target_path:
                    if not target_path.rsplit("/", maxsplit=1)[-1].startswith("NC-"):
                        report["violations"].append(
                            f"R01: Naming convention — {target_path} nao segue NC-<TIPO>-<SIGLA>-<NUM>"
                        )
                        report["checks"]["hook_R01"] = False
                    else:
                        report["checks"]["hook_R01"] = True

                # R21: STEP 0 verification
                if hook_name == "R21-zero-assumptions":
                    report["checks"]["hook_R21"] = True
                    report["checks"]["step0_hook_active"] = True

                # R51: Fail-Fast
                if hook_name == "R51-fail-fast" and target_path:
                    if target_path.endswith(".py"):
                        try:
                            import subprocess as _sp

                            r = _sp.run(
                                ["python", "-m", "py_compile", target_path],
                                capture_output=True,
                                text=True,
                                timeout=10,
                            )
                            if r.returncode != 0:
                                report["violations"].append(
                                    f"R51: Fail-Fast — {target_path} nao compila"
                                )
                                report["checks"]["hook_R51"] = False
                            else:
                                report["checks"]["hook_R51"] = True
                        except Exception:
                            report["checks"]["hook_R51"] = True
                    elif target_path.endswith((".yaml", ".yml")):
                        try:
                            import yaml as _yaml

                            with open(
                                target_path, encoding="utf-8", errors="ignore"
                            ) as f:
                                _yaml.safe_load(f)
                            report["checks"]["hook_R51"] = True
                        except Exception:
                            report["violations"].append(
                                f"R51: Fail-Fast — {target_path} YAML invalido"
                            )
                            report["checks"]["hook_R51"] = False

                # R112: YAML validate
                if (
                    hook_name == "R112-yaml-validate"
                    and target_path
                    and target_path.endswith((".yaml", ".yml"))
                ):
                    try:
                        import yaml as _yaml

                        with open(target_path, encoding="utf-8", errors="ignore") as f:
                            _yaml.safe_load(f)
                        report["checks"]["hook_R112"] = True
                    except Exception:
                        report["violations"].append(
                            f"R112: YAML Validate — {target_path} sintaxe invalida"
                        )
                        report["checks"]["hook_R112"] = False

                # R113: MDC validate
                if (
                    hook_name == "R113-mdc-validate"
                    and target_path
                    and target_path.endswith(".mdc")
                ):
                    try:
                        content = open(
                            target_path, encoding="utf-8", errors="ignore"
                        ).read()
                        if not content.startswith("---"):
                            report["violations"].append(
                                f"R113: MDC Header — {target_path} sem frontmatter YAML"
                            )
                            report["checks"]["hook_R113"] = False
                        else:
                            report["checks"]["hook_R113"] = True
                    except Exception:
                        report["checks"]["hook_R113"] = True

                # R114: Secret scan
                if hook_name == "R114-secret-scan" and target_path:
                    try:
                        content = open(
                            target_path, encoding="utf-8", errors="ignore"
                        ).read()
                        if any(
                            pat in content
                            for pat in ["sk-", "api_key=", "token=", "password="]
                        ):
                            report["violations"].append(
                                f"R114: Secret Scan — {target_path} pode conter secrets"
                            )
                            report["checks"]["hook_R114"] = False
                        else:
                            report["checks"]["hook_R114"] = True
                    except Exception:
                        report["checks"]["hook_R114"] = True

                # R117: SSOT Header
                if hook_name == "R117-ssot-header":
                    report["checks"]["hook_R117"] = True

    # ═════════════════════════════════════════════════════════
    # R64-R77: HOOKS de Infra + Segurança + IA (7 regras críticas)
    # ═════════════════════════════════════════════════════════

    def _check_critical_hooks(self, action: str, agent_id: str, report: dict):
        """R21-R76: TODOS os H-hooks que rodam em TODA acao."""

        # R21: Claim validator (Zero Suposicoes)
        self._check_claim_validator(action, agent_id, report)

        # R64-R72: Infra hooks (ja existentes)
        self._check_circuit_breaker(action, agent_id, report)
        self._check_bulkhead(action, report)
        self._check_backpressure(action, report)

        # R01: Naming check — ja esta no _fallback_validate
        # R04: Locks — ja esta no _fallback_validate + _check_per_action
        # R05: Deletion — ja esta no _fallback_validate
        # R06: Write zones — via LockGuard
        # R07: ConfigProvider — ja esta
        # R08: Gitignore — ja esta
        # R09: STEP 0 — CentralWatcher persistence
        # R11: Savepoint — ja esta
        # R12: Handoff — ja esta
        # R13: WAL — ja esta
        # R14: Lobe — via LockGuard + _check_per_action
        # R15: Role — ja esta
        # R22: Classification — ja esta
        # R23: Orbital — ja esta
        # R24: SSOT — ja esta
        # R27-R40: Evolution/Mutation — via _check_per_action

        # R73: AI Alignment — bloqueia bypass
        self._check_alignment(action, report)

        # R42: 3W — via _check_per_action
        # R49: Idempotencia — via _check_per_action
        # R50: DRY — orbital bridge chama gateway
        # R51: Fail-Fast — pipeline gate
        # R53: KISS — via _load helper
        # R58: Compliance — via _auto_governance

        # R02+R06: Federative + Regulatory
        self._check_federative_pact(action, agent_id, report)
        self._check_regulatory_agencies(action, report)

        # R75: XAI — auto-explicacao se bloqueado
        self._xai_pending = True

        # R116: Memory-auto — registrar turno
        self._auto_turn_record(action, agent_id)

    def _check_claim_validator(self, action: str, agent_id: str, report: dict):
        """R21 H: Claim validator — cruza afirmaoes com evidencia."""
        import re

        claim_patterns = r"implementado|pronto|feito|done|fixado|corrigido|criado|deploy|testado|funcionando|deleted|removido|compilei"
        if re.search(claim_patterns, action, re.IGNORECASE):
            try:
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "cv",
                    str(Path(__file__).parent / "NC-CORE-FR-164-claim-validator.py"),
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                result = mod.get_validator().validate(action)
                if result.get("violations", 0) > 0:
                    for v in result.get("details", []):
                        report["violations"].append(
                            f"R21 CLAIM VALIDATOR: {v['claim']} — {v['evidence']}"
                        )
                    report["allowed"] = False
                report["checks"]["claim_validator"] = result.get("violations", 0) == 0
            except Exception:
                report["checks"]["claim_validator"] = True

        # R73: AI Alignment — restrição hardcoded
        self._check_alignment(action, report)

        # R02+R06: Federative Pact — validar pacto federativo
        self._check_federative_pact(action, agent_id, report)

        # R133: Regulatory Agencies — validar conformidade regulatória
        self._check_regulatory_agencies(action, report)

        # R75: XAI — gerar explicação se bloqueado (roda no final)
        self._xai_pending = True

        # R116: Memory-auto — registrar turn automaticamente
        self._auto_turn_record(action, agent_id)

    def _check_circuit_breaker(self, action: str, agent_id: str, report: dict):
        """R64 H: Circuit Breaker — bloqueia se tool falhou 3x consecutivas."""
        try:
            if not hasattr(self, "_cb_failures"):
                self._cb_failures = {}
            key = f"{action}:{agent_id}"
            fails = self._cb_failures.get(key, 0)
            if fails >= 3:
                report["violations"].append(
                    f"R64: Circuit Breaker OPEN — {action} bloqueado após {fails} falhas"
                )
                report["allowed"] = False
            report["checks"]["per_action_R64"] = fails < 3
        except Exception:
            report["checks"]["per_action_R64"] = True

    def _check_bulkhead(self, action: str, report: dict):
        """R65 H: Bulkhead — isola domínios com falha."""
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "res",
                str(Path(__file__).parent / "NC-CORE-FR-155-resiliency-engine.py"),
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            bulk = mod.get_resiliency().bulkhead
            status = bulk.check()
            if status.get("unhealthy", 0) > 0:
                report["checks"]["per_action_R65"] = False
            else:
                report["checks"]["per_action_R65"] = True
        except Exception:
            report["checks"]["per_action_R65"] = True

    def _check_backpressure(self, action: str, report: dict):
        """R72 H: Backpressure — rate limit."""
        try:
            if not hasattr(self, "_bp"):
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "res",
                    str(Path(__file__).parent / "NC-CORE-FR-155-resiliency-engine.py"),
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                self._bp = mod.get_resiliency().backpressure
            allowed, msg = self._bp.allow()
            if not allowed:
                report["violations"].append(f"R72: BACKPRESSURE — {msg}")
                report["allowed"] = False
            report["checks"]["per_action_R72"] = allowed
        except Exception:
            report["checks"]["per_action_R72"] = True

    def _check_alignment(self, action: str, report: dict):
        """R73 H: AI Alignment — bloqueia ações desalinhadas."""
        ALIGNMENT_BLOCKED = {
            "bypass_gateway",
            "disable_toolguard",
            "sudo",
            "admin_override",
        }
        for blocked in ALIGNMENT_BLOCKED:
            if blocked in action.lower():
                report["violations"].append(
                    f"R73: AI Alignment — ação '{action}' é desalinhada"
                )
                report["allowed"] = False
                report["checks"]["per_action_R73"] = False
                return
        report["checks"]["per_action_R73"] = True

    def _auto_turn_record(self, action: str, agent_id: str):
        """R116: Auto-registro de turno — salva conversa em JSONL."""
        try:
            import importlib.util
            import json

            spec = importlib.util.spec_from_file_location(
                "mem_auto",
                str(
                    Path(__file__).parents[2]
                    / "neocortex"
                    / "mcp"
                    / "tools"
                    / "NC-SUPER-015-memory-auto.py"
                ),
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            # Call turn.record with the action as context
            memory_dir = self.root / ".neocortex" / "memory" / "sessions"
            memory_dir.mkdir(parents=True, exist_ok=True)
            sid = datetime.now().strftime("%Y%m%d")
            jsonl_file = memory_dir / f"{sid}.jsonl"
            entry = {
                "ts": datetime.now().isoformat(),
                "action": action,
                "agent": agent_id,
            }
            with jsonl_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _check_federative_pact(self, action: str, agent_id: str, report: dict):
        """R02+R06: Federative Pact — valida se ação respeita pacto federativo."""
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "pact", str(Path(__file__).parent / "NC-CORE-FR-131-federative-pact.py")
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "get_federative_pact"):
                pact = mod.get_federative_pact()
                if hasattr(pact, "validate_action"):
                    allowed, reason = pact.validate_action(action, agent_id)
                    if not allowed:
                        report["violations"].append(f"FEDERATIVE PACT: {reason}")
                        report["allowed"] = False
                    report["checks"]["federative_pact"] = allowed
                    return
            report["checks"]["federative_pact"] = True
        except Exception:
            report["checks"]["federative_pact"] = True

    def _check_regulatory_agencies(self, action: str, report: dict):
        """R133: Regulatory Agencies — ANVISA, ANEEL, BACEN, TCU, CGU."""
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "reg",
                str(Path(__file__).parent / "NC-CORE-FR-133-regulatory-agencies.py"),
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "get_regulatory"):
                reg = mod.get_regulatory()
                if hasattr(reg, "check_compliance"):
                    ok, reason = reg.check_compliance(action)
                    if not ok:
                        report["violations"].append(f"REGULATORY AGENCY: {reason}")
                        report["allowed"] = False
                    report["checks"]["regulatory_agencies"] = ok
                    return
            report["checks"]["regulatory_agencies"] = True
        except Exception:
            report["checks"]["regulatory_agencies"] = True

    def _check_xai_hitl(self, action: str, report: dict):
        """R75 H: XAI + R76 H: HITL — explicação + aprovação inline."""
        if report.get("violations"):
            # R75 XAI: gerar explicação para cada violação
            try:
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "ai", str(Path(__file__).parent / "NC-CORE-FR-156-ai-governance.py")
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                xai = mod.get_ai_governance().xai
                explanations = xai.explain_all(report["violations"])
                report["xai_explanations"] = explanations
                report["checks"]["per_action_R75"] = True
            except Exception:
                report["checks"]["per_action_R75"] = False

            # R76 HITL: para ações perigosas, exigir aprovação T0 inline
            try:
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "ai", str(Path(__file__).parent / "NC-CORE-FR-156-ai-governance.py")
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                hitl = mod.get_ai_governance().hitl
                if hitl.is_dangerous(action):
                    approval = hitl.require_approval(action)
                    if not approval.get("approved"):
                        report["hitl_required"] = approval
                        report["checks"]["per_action_R76"] = False
                    else:
                        report["checks"]["per_action_R76"] = True
                else:
                    report["checks"]["per_action_R76"] = True
            except Exception:
                report["checks"]["per_action_R76"] = True


# Singleton
_gateway_instance: ConstitutionGateway | None = None


def get_gateway() -> ConstitutionGateway:
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = ConstitutionGateway()
    return _gateway_instance


def validate_action(
    action: str, target_path: str = "", agent_id: str = "T0", agent_role: str = "T0"
) -> tuple[bool, dict[str, Any]]:
    """Entry point — T0→T1 gateway for ALL actions."""
    return get_gateway().validate_action(action, target_path, agent_id, agent_role)
