from __future__ import annotations
"""---
domain: "orchestration"
layer: "core"
type: "service"
tags: ["tool", "024", "governance"]
hash: "auto-generated"
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
        from neocortex.NC-CORE-FR-001-config import get_config

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
        from neocortex.core.NC-CORE-FR-025-security-service import get_security_service

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
        """
        Governana  policy enforcement, audit trail e compliance.

        Args:
            action: ao desejada (policy.check, audit.replay, compliance.report,
                    lock.validate, rule.list, session.contracts, violation.log, ssot.diff)
            policy_name: nome da poltica (para policy.check)
            session_id: identificador da sesso (para audit.replay)
            lock_path: caminho do lock (para lock.validate)
            category: categoria de regras (para rule.list)
            violation_type: tipo de violao (para violation.log)
            violation_details: detalhes da violao (JSON string) (para violation.log)
            ssot_path: caminho do arquivo SSOT (para ssot.diff)
            expected_hash: hash esperado (para ssot.diff)
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

        #  compliance.report 
        elif action == "compliance.report":
            service = _get_policy_service()
            if service is None:
                return {
                    "success": False,
                    "error": "Servio de polticas indisponvel.",
                    "timestamp": timestamp,
                }
            try:
                result = service.compliance_report()
                return {
                    "success": True,
                    "action": action,
                    "report": result.get("report", {}),
                    "summary": result.get("summary", ""),
                    "timestamp": timestamp,
                }
            except Exception as e:
                logger.error(f"Erro em compliance.report: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": timestamp,
                }

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

        #  ao desconhecida 
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'.",
                "available": [
                    "policy.check",
                    "audit.replay",
                    "compliance.report",
                    "lock.validate",
                    "rule.list",
                    "session.contracts",
                    "violation.log",
                    "ssot.diff",
                ],
                "timestamp": timestamp,
            }
