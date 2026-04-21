from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-18T10:14:00.000000'
  injected_by: T0-Antigravity
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TOOL-FR-041-constitution
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
  - governance
  - constitution
---"""
"""
NC-TOOL-FR-041-constitution.py
FR-041  MCP Tool: neocortex_constitution

O GUARDIÃO DA CF — Auditor de Governança do NeoCortex.

Instâncias (equivalente ao judiciário BR):
  STF  constitution.pre_check   → constitucionalidade preventiva (atomic_locks, write_zones, CF)
  STJ  constitution.stj_check   → conformidade técnica (via handoff.validate)
  TJ   constitution.tj_check    → compliance domínio (NC-GOV-FR-003 rules)
  FÓR  constitution.forum_check → precedente/regressão local (regression buffer)

Outras ações:
  constitution.status     → estado atual: poderes ativos, fase, compliance score
  constitution.rights     → direitos e limitações por role (NC-GOV-FR-006)
  constitution.hierarchy  → hierarquia de leis vigentes
  constitution.audit_all  → auditoria completa (STF+STJ+TJ+Fórum em sequência)

IA LOCAL AUDITOR:
  constitution.local_ai_audit → despacha auditoria para agente local (Qwen via PicoClaw)
  — requer PicoClaw :18790 ativo e modelo local configurado
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_project_root() -> Path:
    try:
        from neocortex.core.config.NC_CFG_FR_002_config import get_config
        cfg = get_config()
        return Path(cfg.base_path).parent
    except Exception:
        return Path(__file__).parent.parent.parent.parent.parent


CONSTITUTIONAL_ROLES = {
    "T0": {"authority": "PLENA", "can_amend_cf": True, "can_veto": True},
    "T1": {"authority": "DELEGADA", "can_amend_cf": False, "can_veto": False},
    "T2": {"authority": "RESTRITA", "can_amend_cf": False, "can_veto": False},
    "T3": {"authority": "SOMENTE_LEITURA", "can_amend_cf": False, "can_veto": False},
}

CF_ARTICLES = [
    "Art.1 — NeoCortex é soberano, governado pela lei, indivisível.",
    "Art.2 — Poderes Legislativo, Executivo e Judiciário — independentes e harmônicos.",
    "Art.3 — Nenhum agente está acima da lei. T0 é o Guardião da CF.",
    "Art.4 — Todo ato gera handoff. Todo handoff tem instância de recurso.",
    "Art.5 — Poder constituinte é exclusivo do T0.",
    "Art.6 — Atomic locks são cláusulas pétreas. Intocáveis por qualquer poder.",
    "Art.7 — Lobes são memória institucional. Isolamento entre usuários é garantia fundamental.",
    "Art.8 — PicoClaw exerce autoridade executiva T1 após pré-aprovação T0.",
    "Art.9 — Tokens são recurso público. Gasto proporcional ao benefício.",
    "Art.10 — O sistema evolui mas jamais regride em governança.",
]


# ---------------------------------------------------------------------------
# STF — Controle de Constitucionalidade Preventivo
# ---------------------------------------------------------------------------

def _stf_pre_check(action: str, role: str, target_file: str) -> Dict[str, Any]:
    """Verifica se ação é constitucional ANTES de executar."""
    root = _get_project_root()
    violations = []
    warnings = []

    # Checar atomic_locks (Art. 6 — cláusula pétrea)
    locks_path = root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-SEC-FR-001-atomic-locks.yaml"
    if locks_path.exists() and target_file:
        content = locks_path.read_text(encoding="utf-8", errors="replace")
        target_name = Path(target_file).name
        if target_name in content:
            violations.append({
                "article": "Art.6",
                "severity": "UNCONSTITUTIONAL",
                "reason": f"'{target_name}' é cláusula pétrea (atomic_lock). Ação BLOQUEADA.",
            })

    # Checar role authority (Art. 5 — emenda CF só T0)
    role_upper = role.upper()
    if role_upper not in CONSTITUTIONAL_ROLES:
        warnings.append({"article": "Art.3", "reason": f"Role '{role}' não reconhecido pela CF."})
    elif role_upper != "T0" and action in ("amend_cf", "modify_governance_yaml", "delete"):
        violations.append({
            "article": "Art.5",
            "severity": "UNCONSTITUTIONAL",
            "reason": f"Role {role} não tem poder constituinte. Ação '{action}' requer T0.",
        })

    # Checar write_zones (Art. 3 — nenhum acima da lei)
    zones_path = root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-CFG-FR-002-rules-policy.yaml"
    if zones_path.exists() and target_file and role_upper in ("T2", "T3"):
        content = zones_path.read_text(encoding="utf-8", errors="replace")
        # Verificação básica: T3 nunca escreve
        if role_upper == "T3":
            violations.append({
                "article": "Art.2",
                "severity": "UNCONSTITUTIONAL",
                "reason": "T3 (observers) têm apenas leitura. Qualquer escrita é inconstitucional.",
            })

    is_allowed = len(violations) == 0
    verdict = "ALLOWED" if is_allowed else "BLOCKED_UNCONSTITUTIONAL"

    return {
        "success": True,
        "verdict": verdict,
        "is_constitutional": is_allowed,
        "role": role,
        "action": action,
        "target": target_file or "N/A",
        "violations": violations,
        "warnings": warnings,
        "authority": CONSTITUTIONAL_ROLES.get(role_upper, {}).get("authority", "UNKNOWN"),
    }


# ---------------------------------------------------------------------------
# STJ — Conformidade Técnica
# ---------------------------------------------------------------------------

def _stj_check(file_path: str) -> Dict[str, Any]:
    """STJ: valida código (py_compile + ruff + prints). Recurso possível via T0."""
    if not file_path:
        return {"success": False, "error": "file_path obrigatório"}
    p = Path(file_path)
    if not p.exists():
        return {"success": False, "error": f"Arquivo não encontrado: {file_path}"}
    if p.suffix != ".py":
        return {"success": True, "verdict": "STJ_NOT_APPLICABLE", "reason": "Apenas .py"}

    results = {}
    r1 = subprocess.run([sys.executable, "-m", "py_compile", str(p)], capture_output=True, text=True)
    results["compile_ok"] = r1.returncode == 0
    results["compile_error"] = r1.stderr.strip() or None

    r2 = subprocess.run([sys.executable, "-m", "ruff", "check", str(p)], capture_output=True, text=True)
    results["ruff_ok"] = r2.returncode == 0
    results["ruff_issues"] = r2.stdout.strip() or None

    text = p.read_text(encoding="utf-8", errors="replace")
    bad_prints = [ln.strip() for ln in text.splitlines()
                  if "print(" in ln and "file=sys.stderr" not in ln and not ln.strip().startswith("#")]
    results["no_stdout_print"] = len(bad_prints) == 0
    results["stdout_prints"] = bad_prints[:3]

    all_ok = results["compile_ok"] and results["ruff_ok"] and results["no_stdout_print"]
    return {
        "success": True,
        "verdict": "STJ_APPROVED" if all_ok else "STJ_REJECTED",
        "file": p.name,
        "appeal_possible": not all_ok,
        "appeal_to": "T0 (t0_review no handoff)",
        **results,
    }


# ---------------------------------------------------------------------------
# TJ — Compliance por Domínio
# ---------------------------------------------------------------------------

def _tj_check() -> Dict[str, Any]:
    """TJ: compliance das 20 regras NC-GOV-FR-003. Recurso ao STJ."""
    root = _get_project_root()
    script = root / "01_neocortex_framework" / "scripts" / "NC-SCR-FR-080-governance-auditor.py"
    if not script.exists():
        return {"success": False, "error": "NC-SCR-FR-080 não encontrado", "verdict": "TJ_UNAVAILABLE"}
    r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True,
                       cwd=str(root), timeout=60)
    output = r.stdout.strip()
    # Tentar extrair compliance %
    import re
    m = re.search(r"(\d+\.?\d*)%", output)
    score = float(m.group(1)) if m else None
    verdict = "TJ_APPROVED" if (score and score >= 80) else "TJ_PENDING"
    return {
        "success": True,
        "verdict": verdict,
        "compliance_score": score,
        "output_summary": output[:1000],
        "appeal_possible": True,
        "appeal_to": "STJ → STF",
        "threshold": "80%",
    }


# ---------------------------------------------------------------------------
# Fórum — Precedente Local
# ---------------------------------------------------------------------------

def _forum_check(error_description: str = "", action_taken: str = "") -> Dict[str, Any]:
    """Fórum: verifica regression buffer. Cabem recursos."""
    root = _get_project_root()
    # Usa neocortex_regression internamente via importlib
    try:
        pass  # type: ignore
    except Exception:
        pass

    # Fallback: leitura direta do ledger
    ledger_paths = list(root.rglob("regression_buffer.json"))
    if not ledger_paths:
        return {
            "success": True,
            "verdict": "FORUM_NO_PRECEDENT",
            "reason": "Nenhum buffer de regressão encontrado",
        }
    import json
    try:
        data = json.loads(ledger_paths[0].read_text(encoding="utf-8"))
        entries = data if isinstance(data, list) else data.get("entries", [])
        matches = [e for e in entries
                   if error_description.lower() in str(e).lower()] if error_description else []
        return {
            "success": True,
            "verdict": "FORUM_PRECEDENT_FOUND" if matches else "FORUM_NO_PRECEDENT",
            "precedents": matches[:3],
            "total_entries": len(entries),
            "appeal_possible": True,
            "appeal_to": "TJ",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Status + Rights + Hierarchy
# ---------------------------------------------------------------------------

def _constitution_status() -> Dict[str, Any]:
    root = _get_project_root()
    return {
        "success": True,
        "cf_version": "NC-CONST-FR-001-v0.2-20260418",
        "articles": len(CF_ARTICLES),
        "active_powers": {
            "legislativo": "neocortex_tickets + neocortex_governance (T0)",
            "executivo": "neocortex_orchestration + neocortex_picoclaw + neocortex_task",
            "judiciario": "neocortex_constitution (STF/STJ/TJ/Forum) + AuditHook",
        },
        "leis_complementares": ["NC-GOV-FR-002..005 (existente)", "NC-GOV-FR-006 (agent rights)", "NC-GOV-FR-008 (lobe taxonomy)"],
        "leis_pendentes": ["NC-GOV-FR-007 (picoclaw dispatch)", "NC-GOV-FR-009 (escalation)", "NC-GOV-FR-010 (constitution schema)"],
        "project_root": str(root),
    }


def _constitution_rights(role: str) -> Dict[str, Any]:
    role_u = role.upper()
    info = CONSTITUTIONAL_ROLES.get(role_u)
    if not info:
        return {"success": False, "error": f"Role '{role}' não reconhecido"}
    rights = {
        "T0": ["legislar", "julgar", "executar", "vetar", "emenda CF com ticket+handoff"],
        "T1": ["executar tickets com dispatch aprovado", "criar handoffs", "chamar T2", "ler qualquer arquivo"],
        "T2": ["editar no escopo do ticket", "rodar scripts do dispatch", "criar em write_zones restritas"],
        "T3": ["observar eventos", "notificar via hooks", "logar via AuditHook"],
    }
    restrictions = {
        "T0": ["atomic_locks sem quórum (Art.6)"],
        "T1": ["modificar CF", "tocar atomic_locks", "emitir %DONE sem T0", "criar tickets sem delegação"],
        "T2": ["criar/fechar tickets", "modificar gov YAMLs", "sair do escopo do dispatch"],
        "T3": ["qualquer escrita", "dispatchar agentes"],
    }
    return {
        "success": True,
        "role": role_u,
        "authority": info["authority"],
        "rights": rights.get(role_u, []),
        "restrictions": restrictions.get(role_u, []),
        "law_source": "NC-GOV-FR-006 + NC-CONST-FR-001",
    }


# ---------------------------------------------------------------------------
# IA Local Auditor (via PicoClaw)
# ---------------------------------------------------------------------------

def _local_ai_audit(scope: str = "full") -> Dict[str, Any]:
    """
    Despacha auditoria de governança para IA local (Qwen via PicoClaw :18790).
    Qwen atua como TJ autônomo — audita compliance sem gastar tokens de API.
    """
    try:
        import json as _json
        import urllib.request
        payload = _json.dumps({
            "task": (
                f"Você é o auditor de governança NeoCortex (equivalente ao TJ). "
                f"Escopo: {scope}. "
                "Verifique: (1) tickets sem handoff, (2) compliance NC-GOV-FR-003 rules, "
                "(3) atomic_locks íntegros, (4) naming convention NC- nos arquivos principais. "
                "Retorne: compliance_score, violations[], warnings[], recommendation."
            ),
            "context": "Constitution Layer NC-CONST-FR-001 v0.2",
            "agent_role": "T2",
            "authority": "TJ",
        }).encode()
        req = urllib.request.Request(
            "http://localhost:18790/message",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = _json.loads(resp.read())
        return {
            "success": True,
            "auditor": "Qwen-local via PicoClaw :18790",
            "scope": scope,
            "result": result,
            "law_source": "Art.8 CF — PicoClaw T1 authority",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"PicoClaw indisponível: {e}",
            "fallback": "Use constitution.tj_check para auditoria local sem IA",
            "tip": "Inicie PicoClaw: NC-SCR-PIC-001-picoclaw-watchdog.bat",
        }


# ---------------------------------------------------------------------------
# Register MCP tool
# ---------------------------------------------------------------------------

def register_tool(mcp) -> None:
    """Registra neocortex_constitution no servidor MCP."""

    @mcp.tool(name="neocortex_constitution")
    def neocortex_constitution(
        action: str,
        role: str = "T0",
        target_file: str = "",
        file_path: str = "",
        action_name: str = "",
        error_description: str = "",
        scope: str = "full",
    ) -> Dict[str, Any]:
        """O GUARDIÃO DA CF — Auditor de Governança do NeoCortex.

        Actions: constitution.pre_check (STF), constitution.stj_check (STJ),
                 constitution.tj_check (TJ), constitution.forum_check (Fórum),
                 constitution.audit_all, constitution.status, constitution.rights,
                 constitution.hierarchy, constitution.local_ai_audit
        """
        if action == "constitution.pre_check":
            return _stf_pre_check(action_name or action, role, target_file)

        elif action == "constitution.stj_check":
            return _stj_check(file_path or target_file)

        elif action == "constitution.tj_check":
            return _tj_check()

        elif action == "constitution.forum_check":
            return _forum_check(error_description)

        elif action == "constitution.audit_all":
            stf = _stf_pre_check(action_name or "audit", role, target_file)
            stj = _stj_check(file_path) if file_path else {"skipped": True, "reason": "file_path não fornecido"}
            tj = _tj_check()
            forum = _forum_check(error_description)
            all_ok = stf.get("is_constitutional", True) and tj.get("verdict", "").endswith("APPROVED")
            return {
                "success": True,
                "verdict": "CONSTITUCIONAL" if all_ok else "VIOLAÇÕES_DETECTADAS",
                "stf": stf,
                "stj": stj,
                "tj": tj,
                "forum": forum,
                "recommendation": "Sistema constitucional" if all_ok else "Ver violations nos órgãos acima",
            }

        elif action == "constitution.status":
            return _constitution_status()

        elif action == "constitution.rights":
            return _constitution_rights(role)

        elif action == "constitution.hierarchy":
            return {
                "success": True,
                "hierarchy": [
                    {"level": 1, "name": "CF — Constituição Federal", "file": "NC-WF-001-workspace-routine.md"},
                    {"level": 2, "name": "Leis Complementares", "files": ["NC-GOV-FR-002..010"]},
                    {"level": 3, "name": "Leis Ordinárias", "files": ["NC-NAM-FR-001", "NC-CFG-FR-002", "NC-CYC-FR-001"]},
                    {"level": 4, "name": "Decretos / Regulamentos", "files": ["Lobes .mdc por domínio"]},
                    {"level": 5, "name": "Jurisprudência", "files": ["regression_buffer.json", "handoffs REJECTED"]},
                ],
                "articles": CF_ARTICLES,
            }

        elif action == "constitution.local_ai_audit":
            return _local_ai_audit(scope=scope)

        else:
            return {
                "success": False,
                "error": f"Ação desconhecida: '{action}'",
                "available": [
                    "constitution.pre_check", "constitution.stj_check",
                    "constitution.tj_check", "constitution.forum_check",
                    "constitution.audit_all", "constitution.status",
                    "constitution.rights", "constitution.hierarchy",
                    "constitution.local_ai_audit",
                ],
            }
