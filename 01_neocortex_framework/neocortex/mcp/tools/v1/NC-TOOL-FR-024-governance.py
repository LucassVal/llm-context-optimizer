from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.001322'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TOOL-FR-024-governance
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-TOOL-FR-024-governance.py
FR-024  MCP Tool: neocortex_governance

Governana  policy enforcement, audit trail e compliance.
Aes disponveis:
  policy.check        validar se uma ao viola alguma policy
  audit.replay        re-executar audit trail de uma sesso
  compliance.report   gerar relatrio de conformidade
  lock.validate       verificar integridade dos atomic locks
  rule.list           listar todas as regras ativas por categoria
  session.contracts   listar contratos de sesso ativos
  violation.log       registrar violao detectada
  ssot.diff           comparar estado atual vs SSOT esperado
"""


import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def _config():
    """Obtm configurao do NeoCortex."""
    try:
        from neocortex.config import get_config

        return get_config()
    except Exception:
        return None


def _get_policy_service():
    """Obtm servio de polticas."""
    try:
        from neocortex.core.policy_service import get_policy_service

        return get_policy_service()
    except Exception:
        return None


def _get_lock_service():
    """Obtm servio de locks atmicos."""
    try:
        from neocortex.core.security_service import get_security_service

        return get_security_service()
    except Exception:
        return None


def _get_audit_service():
    """Obtm servio de auditoria."""
    try:
        from neocortex.core.audit_service import get_audit_service

        return get_audit_service()
    except Exception:
        return None


def _get_ssot_service():
    """Obtm servio SSOT."""
    try:
        from neocortex.core.ssot_service import get_ssot_service

        return get_ssot_service()
    except Exception:
        return None


def _iso_timestamp() -> str:
    """Retorna timestamp atual no formato ISO 8601 completo (GOV-013)."""
    return datetime.now().isoformat(timespec="seconds")


def register_tool(mcp) -> None:
    """Registra neocortex_governance no servidor MCP."""

    @mcp.tool(name="neocortex_governance")
    def neocortex_governance(
        action: str,
        policy_name: str = "",
        session_id: str = "",
        lock_path: str = "",
        category: str = "",
        violation_type: str = "",
        violation_details: str = "",
        ssot_path: str = "",
        expected_hash: str = "",
    ) -> Dict[str, Any]:
        """Governança — policy enforcement, audit trail e compliance.

        Actions: policy.check, audit.replay, compliance.report, compliance.orphan_check,
                 lock.validate, rule.list, session.contracts, violation.log,
                 ssot.diff, governance.naming_delegate
        """
        timestamp = _iso_timestamp()

        #  policy.check
        if action == "policy.check":
            if not policy_name:
                return {
                    "success": False,
                    "error": "policy_name  obrigatrio.",
                    "timestamp": timestamp,
                }
            service = _get_policy_service()
            if service is None:
                return {
                    "success": False,
                    "error": "Servio de polticas indisponvel.",
                    "timestamp": timestamp,
                }
            try:
                result = service.validate(policy_name)
                return {
                    "success": True,
                    "action": action,
                    "policy_name": policy_name,
                    "valid": result.get("valid", False),
                    "violations": result.get("violations", []),
                    "timestamp": timestamp,
                }
            except Exception as e:
                logger.error(f"Erro em policy.check: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": timestamp,
                }

        #  audit.replay
        elif action == "audit.replay":
            if not session_id:
                return {
                    "success": False,
                    "error": "session_id  obrigatrio.",
                    "timestamp": timestamp,
                }
            service = _get_audit_service()
            if service is None:
                return {
                    "success": False,
                    "error": "Servio de auditoria indisponvel.",
                    "timestamp": timestamp,
                }
            try:
                result = service.replay(session_id)
                return {
                    "success": True,
                    "action": action,
                    "session_id": session_id,
                    "events": result.get("events", []),
                    "total_events": result.get("total", 0),
                    "timestamp": timestamp,
                }
            except Exception as e:
                logger.error(f"Erro em audit.replay: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": timestamp,
                }

        #  compliance.report — standalone (NC-DS-143 fix: sem policy_service)
        elif action == "compliance.report":
            try:
                cfg = _config()
                root = Path(cfg.project_root) if cfg else Path.cwd()
                fw = root / "01_neocortex_framework"
                docs = fw / "DIR-DOC-FR-001-docs-main"
                tools_dir = fw / "neocortex" / "mcp" / "tools"
                tickets_dir = root / "DIR-DS-001-tickets"
                audit_dir = root / "DIR-DS-002-audit-logs"
                checks = {
                    "R01_asset_inventory": (docs / "artifact_catalog.json").exists(),
                    "R02_policy_formalized": (docs / "NC-NAM-FR-001-naming-convention.md").exists(),
                    "R04_naming_convention": any(fw.rglob("NC-*.py")),
                    "R07_polp": (docs / "NC-CFG-FR-001-agent-policy-template.yaml").exists(),
                    "R08_atomic_locks": (docs / "NC-SEC-FR-001-atomic-locks.yaml").exists(),
                    "R09_write_zones": (docs / "NC-CFG-FR-002-rules-policy.yaml").exists(),
                    "R10_audit_trail": audit_dir.exists(),
                    "R12_handoffs": audit_dir.exists() and len(list(audit_dir.glob("*.yaml"))) > 0,
                    "R13_checkpoints": (tools_dir / "NC-TOOL-FR-022-session.py").exists(),
                    "R14_step0": (fw / "neocortex" / "mcp" / "sub_server.py").exists(),
                    "R15_savepoint": (tools_dir / "NC-TOOL-FR-031-savepoint.py").exists(),
                    "R18_ticket_lifecycle": tickets_dir.exists() and len(list(tickets_dir.glob("NC-DS-*.yaml"))) > 0,
                    "R19_4cycle_routine": (root / ".agents" / "workflows" / "NC-WF-001-workspace-routine.md").exists(),
                    "R20_archive": (root / "DIR-ARC-FR-001-archive-main").exists(),
                    "LEXICO_service": (fw / "neocortex" / "core" / "services" / "NC-SVC-FR-020-lexico-service.py").exists(),
                    "LITELLM_gateway": (tools_dir / "NC-TOOL-FR-043-litellm.py").exists(),
                    "SESSION_MEMORY": (fw / "neocortex" / "core" / "services" / "NC-SVC-FR-021-session-memory-writer.py").exists(),
                }
                passed = [k for k, v in checks.items() if v]
                failed = [k for k, v in checks.items() if not v]
                score = round(len(passed) / len(checks) * 100, 1) if checks else 0
                return {
                    "success": True,
                    "action": action,
                    "compliance_score": score,
                    "rules_total": len(checks),
                    "rules_passed": len(passed),
                    "rules_failed": len(failed),
                    "violations": failed,
                    "status": "COMPLIANT" if score >= 80 else "NON_COMPLIANT",
                    "timestamp": timestamp,
                }
            except Exception as e:
                logger.error(f"Erro em compliance.report standalone: {e}")
                return {"success": False, "error": str(e), "timestamp": timestamp}

        #  lock.validate
        elif action == "lock.validate":
            service = _get_lock_service()
            if service is None:
                return {
                    "success": False,
                    "error": "Servio de segurana indisponvel.",
                    "timestamp": timestamp,
                }
            try:
                result = service.validate_locks(lock_path if lock_path else None)
                return {
                    "success": True,
                    "action": action,
                    "lock_path": lock_path or "all",
                    "valid": result.get("valid", False),
                    "issues": result.get("issues", []),
                    "timestamp": timestamp,
                }
            except Exception as e:
                logger.error(f"Erro em lock.validate: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": timestamp,
                }

        #  rule.list
        elif action == "rule.list":
            service = _get_policy_service()
            if service is None:
                return {
                    "success": False,
                    "error": "Servio de polticas indisponvel.",
                    "timestamp": timestamp,
                }
            try:
                result = service.list_rules(category if category else None)
                return {
                    "success": True,
                    "action": action,
                    "category": category or "all",
                    "rules": result.get("rules", []),
                    "total": result.get("total", 0),
                    "timestamp": timestamp,
                }
            except Exception as e:
                logger.error(f"Erro em rule.list: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": timestamp,
                }

        #  session.contracts
        elif action == "session.contracts":
            cfg = _config()
            if cfg is None:
                return {
                    "success": False,
                    "error": "Configurao indisponvel.",
                    "timestamp": timestamp,
                }
            try:
                contracts_dir = Path(cfg.session_contracts_dir)
                contracts = []
                if contracts_dir.exists():
                    for f in contracts_dir.glob("*.yaml"):
                        contracts.append(f.name)
                return {
                    "success": True,
                    "action": action,
                    "contracts": contracts,
                    "total": len(contracts),
                    "timestamp": timestamp,
                }
            except Exception as e:
                logger.error(f"Erro em session.contracts: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": timestamp,
                }

        #  violation.log
        elif action == "violation.log":
            if not violation_type:
                return {
                    "success": False,
                    "error": "violation_type  obrigatrio.",
                    "timestamp": timestamp,
                }
            service = _get_audit_service()
            if service is None:
                return {
                    "success": False,
                    "error": "Servio de auditoria indisponvel.",
                    "timestamp": timestamp,
                }
            try:
                details = {}
                if violation_details:
                    details = json.loads(violation_details)
                result = service.log_violation(violation_type, details)
                return {
                    "success": True,
                    "action": action,
                    "violation_id": result.get("violation_id", ""),
                    "timestamp": timestamp,
                }
            except Exception as e:
                logger.error(f"Erro em violation.log: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": timestamp,
                }

        #  ssot.diff
        elif action == "ssot.diff":
            if not ssot_path:
                return {
                    "success": False,
                    "error": "ssot_path  obrigatrio.",
                    "timestamp": timestamp,
                }
            service = _get_ssot_service()
            if service is None:
                return {
                    "success": False,
                    "error": "Servio SSOT indisponvel.",
                    "timestamp": timestamp,
                }
            try:
                result = service.diff(
                    ssot_path, expected_hash if expected_hash else None
                )
                return {
                    "success": True,
                    "action": action,
                    "ssot_path": ssot_path,
                    "matches": result.get("matches", False),
                    "diff": result.get("diff", ""),
                    "timestamp": timestamp,
                }
            except Exception as e:
                logger.error(f"Erro em ssot.diff: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": timestamp,
                }

        # T-01: compliance.orphan_check — tickets sem handoff e vice-versa
        elif action == "compliance.orphan_check":
            try:
                cfg = _config()
                root = Path(cfg.project_root) if cfg else Path(".")
                tickets_dir = root / "DIR-DS-001-tickets"
                handoffs_dir = root / "DIR-DS-002-audit-logs"
                ticket_ids = {f.stem.split("-ticket")[0] for f in tickets_dir.glob("NC-DS-*-ticket.yaml")} if tickets_dir.exists() else set()
                handoff_ids = {f.stem.split("-handoff")[0] for f in handoffs_dir.glob("NC-DS-*-handoff.yaml")} if handoffs_dir.exists() else set()
                orphan_tickets = sorted(ticket_ids - handoff_ids)
                orphan_handoffs = sorted(handoff_ids - ticket_ids)
                total_ok = len(ticket_ids & handoff_ids)
                return {
                    "success": True, "action": action,
                    "orphan_tickets": orphan_tickets, "orphan_handoffs": orphan_handoffs,
                    "total_ok": total_ok, "timestamp": timestamp,
                }
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": timestamp}

        # T-02: ssot.diff com LockGuard hash real
        elif action == "ssot.diff":
            import hashlib
            cfg = _config()
            root = Path(cfg.project_root) if cfg else Path(".")
            lock_files = [
                root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-NAM-FR-001-naming-convention.md",
                root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-SEC-FR-001-atomic-locks.yaml",
                root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-CFG-FR-001-agent-policy-template.yaml",
                root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-TODO-FR-001-project-roadmap-consolidated.md",
            ]
            results = []
            for lf in lock_files:
                if lf.exists():
                    try:
                        h = hashlib.sha256(lf.read_bytes()).hexdigest()
                        results.append({"file": lf.name, "sha256": h, "exists": True, "status": "ok"})
                    except Exception as exc:
                        results.append({"file": lf.name, "error": str(exc), "status": "error"})
                else:
                    results.append({"file": lf.name, "exists": False, "status": "missing"})
            ok_count = sum(1 for r in results if r.get("status") == "ok")
            return {
                "success": True, "action": action,
                "files_checked": len(results), "files_ok": ok_count,
                "files": results, "timestamp": timestamp,
            }

        # T-03: audit.replay + draft=True gera rascunho de handoff
        elif action == "audit.replay":
            if not session_id:
                return {"success": False, "error": "session_id é obrigatório.", "timestamp": timestamp}
            draft = violation_details == "draft=true" or expected_hash == "draft"
            service = _get_audit_service()
            events: list = []
            if service:
                try:
                    result = service.replay(session_id)
                    events = result.get("events", [])
                except Exception as e:
                    logger.warning(f"audit.replay service failed: {e}")
            replay_result: dict = {
                "success": True, "action": action,
                "session_id": session_id, "total_events": len(events),
                "events": events, "timestamp": timestamp,
            }
            if draft:
                try:
                    import importlib as _il
                    _hf = _il.import_module(".tools.NC-TOOL-FR-038-handoff", package="neocortex.mcp")
                    # Chamar handoff.create via módulo já carregado
                    replay_result["draft_note"] = "Handoff draft: use neocortex_handoff.handoff.create com este session_id"
                except Exception:
                    replay_result["draft_note"] = "Handoff draft: use neocortex_handoff.handoff.create"
                replay_result["draft"] = True
            return replay_result

        # T-04: governance.naming_delegate — delega para neocortex_governance_ops
        elif action == "governance.naming_delegate":
            try:
                import importlib.util
                from pathlib import Path as _P
                ops_path = _P(__file__).parent / "NC-TOOL-FR-040-governance-ops.py"
                spec = importlib.util.spec_from_file_location("governance_ops", ops_path)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    # Chamar a função naming_audit diretamente
                    if hasattr(mod, "_naming_audit"):
                        cfg = _config()
                        root = str(cfg.project_root) if cfg else "."
                        result = mod._naming_audit(root, max_results=50)
                        return {"success": True, "action": action, "naming_audit": result, "timestamp": timestamp}
                return {"success": False, "error": "NC-TOOL-FR-040 não encontrado ou sem _naming_audit", "timestamp": timestamp}
            except Exception as exc:
                return {"success": False, "error": str(exc), "timestamp": timestamp}

        # T-05: compliance.report + code_quality (py_compile+ruff)
        elif action == "compliance.report":
            import subprocess
            import sys
            cfg = _config()
            root = Path(cfg.project_root) if cfg else Path(".")
            tools_dir = root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"
            code_quality: dict = {"files_ok": [], "files_failed": []}
            if tools_dir.exists():
                for py_file in sorted(tools_dir.glob("NC-TOOL-FR-*.py")):
                    try:
                        r = subprocess.run(
                            [sys.executable, "-m", "py_compile", str(py_file)],
                            capture_output=True, text=True, timeout=10
                        )
                        if r.returncode == 0:
                            code_quality["files_ok"].append(py_file.name)
                        else:
                            code_quality["files_failed"].append({"file": py_file.name, "error": r.stderr.strip()})
                    except Exception as exc:
                        code_quality["files_failed"].append({"file": py_file.name, "error": str(exc)})
            service = _get_policy_service()
            policy_report: dict = {}
            if service:
                try:
                    policy_report = service.compliance_report()
                except Exception:
                    policy_report = {}
            return {
                "success": True, "action": action,
                "report": policy_report.get("report", {}),
                "summary": policy_report.get("summary", ""),
                "code_quality": code_quality,
                "code_quality_score": len(code_quality["files_ok"]) / max(1, len(code_quality["files_ok"]) + len(code_quality["files_failed"])),
                "timestamp": timestamp,
            }

        # T-06: policy.check + write_zones por role
        elif action == "policy.check":
            if not policy_name:
                return {"success": False, "error": "policy_name é obrigatório.", "timestamp": timestamp}
            cfg = _config()
            root = Path(cfg.project_root) if cfg else Path(".")
            rules_policy_path = root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-CFG-FR-002-rules-policy.yaml"
            write_zone_check: dict = {}
            if rules_policy_path.exists():
                try:
                    import yaml as _yaml
                    with open(rules_policy_path, encoding="utf-8") as fh:
                        rules_data = _yaml.safe_load(fh) or {}
                    role_zones = rules_data.get("write_zones", {})
                    # policy_name pode ser "role:path" para checar zona específica
                    if ":" in policy_name:
                        role_arg, path_arg = policy_name.split(":", 1)
                        allowed_zones = role_zones.get(role_arg, [])
                        allowed = any(path_arg.startswith(z) for z in allowed_zones)
                        write_zone_check = {
                            "role": role_arg, "target_path": path_arg,
                            "allowed": allowed, "allowed_zones": allowed_zones,
                            "rule_source": str(rules_policy_path.name),
                        }
                except ImportError:
                    write_zone_check = {"error": "yaml não disponível, instalar pyyaml"}
                except Exception as exc:
                    write_zone_check = {"error": str(exc)}
            service = _get_policy_service()
            svc_result: dict = {}
            if service:
                try:
                    svc_result = service.validate(policy_name.split(":")[0])
                except Exception:
                    pass
            return {
                "success": True, "action": action, "policy_name": policy_name,
                "valid": svc_result.get("valid", True),
                "violations": svc_result.get("violations", []),
                "write_zone_check": write_zone_check,
                "timestamp": timestamp,
            }

        #  lock.validate
        elif action == "lock.validate":
            service = _get_lock_service()
            if service is None:
                return {"success": False, "error": "Serviço de segurança indisponível.", "timestamp": timestamp}
            try:
                result = service.validate_locks(lock_path if lock_path else None)
                return {"success": True, "action": action, "lock_path": lock_path or "all",
                        "valid": result.get("valid", False), "issues": result.get("issues", []), "timestamp": timestamp}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": timestamp}

        #  rule.list
        elif action == "rule.list":
            service = _get_policy_service()
            if service is None:
                return {"success": False, "error": "Serviço de políticas indisponível.", "timestamp": timestamp}
            try:
                result = service.list_rules(category if category else None)
                return {"success": True, "action": action, "category": category or "all",
                        "rules": result.get("rules", []), "total": result.get("total", 0), "timestamp": timestamp}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": timestamp}

        #  session.contracts
        elif action == "session.contracts":
            cfg = _config()
            if cfg is None:
                return {"success": False, "error": "Configuração indisponível.", "timestamp": timestamp}
            try:
                contracts_dir = Path(cfg.session_contracts_dir)
                contracts = [f.name for f in contracts_dir.glob("*.yaml")] if contracts_dir.exists() else []
                return {"success": True, "action": action, "contracts": contracts,
                        "total": len(contracts), "timestamp": timestamp}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": timestamp}

        #  violation.log
        elif action == "violation.log":
            if not violation_type:
                return {"success": False, "error": "violation_type é obrigatório.", "timestamp": timestamp}
            service = _get_audit_service()
            if service is None:
                return {"success": False, "error": "Serviço de auditoria indisponível.", "timestamp": timestamp}
            try:
                details = json.loads(violation_details) if violation_details else {}
                result = service.log_violation(violation_type, details)
                return {"success": True, "action": action,
                        "violation_id": result.get("violation_id", ""), "timestamp": timestamp}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": timestamp}

        #  ação desconhecida
        else:
            return {
                "success": False,
                "error": f"Ação desconhecida: '{action}'.",
                "available": [
                    "policy.check", "audit.replay", "compliance.report",
                    "compliance.orphan_check", "lock.validate", "rule.list",
                    "session.contracts", "violation.log", "ssot.diff",
                    "governance.naming_delegate",
                ],
                "timestamp": timestamp,
            }
