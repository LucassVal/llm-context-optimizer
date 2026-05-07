# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
"""---
@Audit NC-CORE-FR-156-ai-governance mcp NC-CORE-FR-156-ai-governance.py — Bloco 5: Governa
---
"""


import hashlib
import json
import os
import pathlib
import re
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# R74 — Model Cards (Manifesto do Servidor MCP)
# ═══════════════════════════════════════════════════════════════

class ModelCards:
    """Gera manifestos descritivos para cada servidor MCP."""

    def __init__(self, root: Optional[pathlib.Path] = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))

    def generate_card(self, tool_name: str) -> dict:
        tools_dir = self.root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"
        tool_file = tools_dir / tool_name
        if not tool_file.exists():
            return {"error": f"Tool not found: {tool_name}"}
        content = tool_file.read_text(encoding="utf-8", errors="ignore")
        actions = re.findall(r'#\s*Actions:?\n((?:\s*#\s+.+\n?)+)', content)
        action_list = []
        if actions:
            action_list = [a.strip("# ") for a in actions[0].strip().split("\n") if a.strip()]
        description = ""
        m = re.search(r'\"\"\"(.+?)\"\"\"', content, re.DOTALL)
        if m:
            lines = m.group(1).strip().split("\n")
            description = " ".join(l.strip() for l in lines[:3] if l.strip())

        return {
            "tool": tool_name.replace(".py", ""),
            "version": "4.2-cortex",
            "description": description[:200],
            "actions": action_list[:20],
            "limitations": ["Requires Gateway validation (H mordaça)", "Not thread-safe for concurrent writes"],
            "forbidden_domains": ["DIR-ARC-FR-001-archive-main", ".git"],
            "performance_metrics": {"avg_response_ms": "unknown", "token_cost_estimate": "low"},
            "generated_at": datetime.now().isoformat(),
        }

    def generate_all(self) -> dict:
        tools_dir = self.root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"
        cards = {}
        for f in sorted(tools_dir.glob("NC-SUPER-*.py")) if tools_dir.exists() else []:
            try:
                card = self.generate_card(f.name)
                cards[f.stem] = card
            except: pass
        return {"model_cards": cards, "total": len(cards), "generated_at": datetime.now().isoformat()}


# ═══════════════════════════════════════════════════════════════
# R75 — Explainability (XAI) — Fundamentação Judicial
# ═══════════════════════════════════════════════════════════════

class ExplainabilityEngine:
    """Gera explicações detalhadas quando o Gateway bloqueia uma ação."""

    TEMPLATES = {
        "R05": "Art. 5º CPP (Prisão em Flagrante): Deleção bloqueada. Use DIR-ARC-FR-001-archive-main para arquivar.",
        "R15": "Art. 489 CPC (Fundamentação): Ação requer privilégio T0. Seu cargo: {role}.",
        "R23": "Súmula Vinculante 23 (STF): Arquivo '{file}' não segue padrão NC-.",
        "R42": "Auto de Infração (Lei 9.784/99): Arquivo '{file}' não tem 3 W's (What/Why/Where).",
        "R49": "Art. 505 CPC (Coisa Julgada): Operação já foi processada. Payload duplicado detectado.",
        "R04": "Lei de Acesso à Informação (12.527/2011): Path '{path}' está sob Atomic Lock.",
    }

    def explain(self, violation: str, context: dict | None = None) -> str:
        context = context or {}
        for rule_id, template in self.TEMPLATES.items():
            if rule_id in violation:
                return template.format(**context, **({"role": "AGENT", "file": "unknown", "path": "unknown"}))
        return f"Motivo da recusa: {violation}"

    def explain_all(self, violations: list[str], context: dict | None = None) -> list[str]:
        return [self.explain(v, context) for v in violations]


# ═══════════════════════════════════════════════════════════════
# R76 — HITL (Human-in-the-Loop)
# ═══════════════════════════════════════════════════════════════

class HITLEngine:
    """Suspende ações perigosas até aprovação humana (T0)."""

    DANGEROUS_ACTIONS = {"lobes.delete", "agent.spawn", "config.set", "pulse.stop",
                         "genome.fork", "mutation.propose", "instance.switch"}

    def __init__(self, root: Optional[pathlib.Path] = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self._pending_dir = self.root / ".neocortex" / "hitl"
        self._pending_dir.mkdir(parents=True, exist_ok=True)

    def is_dangerous(self, action: str) -> bool:
        return action in self.DANGEROUS_ACTIONS

    def require_approval(self, action: str, payload: dict | None = None) -> dict:
        if not self.is_dangerous(action):
            return {"approved": True, "reason": "Low risk action", "method": "auto"}

        # Suspender ação — criar ticket de aprovação
        approval_id = f"HITL-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{hashlib.md5(action.encode()).hexdigest()[:8]}"
        approval_file = self._pending_dir / f"{approval_id}.json"
        approval_file.write_text(json.dumps({
            "action": action, "payload": payload or {},
            "status": "PENDING_T0_APPROVAL",
            "created_at": datetime.now().isoformat(),
        }, indent=2), encoding="utf-8")

        return {
            "approved": False,
            "reason": "Human-in-the-Loop: requer aprovação de T0",
            "approval_id": approval_id,
            "instructions": f"T0: Use 'hitl.approve {approval_id}' ou 'hitl.reject {approval_id}' via MCP",
        }

    def approve(self, approval_id: str) -> dict:
        af = self._pending_dir / f"{approval_id}.json"
        if not af.exists():
            return {"error": f"Approval {approval_id} not found"}
        data = json.loads(af.read_text(encoding="utf-8"))
        data["status"] = "APPROVED_BY_T0"
        data["approved_at"] = datetime.now().isoformat()
        af.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return {"approved": True, "action": data["action"], "method": "T0"}

    def reject(self, approval_id: str, reason: str = "") -> dict:
        af = self._pending_dir / f"{approval_id}.json"
        if not af.exists():
            return {"error": f"Approval {approval_id} not found"}
        af.unlink()
        return {"approved": False, "action": "rejected", "reason": reason or "Rejected by T0"}

    def list_pending(self) -> list[dict]:
        pending = []
        for f in sorted(self._pending_dir.glob("HITL-*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if data.get("status") == "PENDING_T0_APPROVAL":
                    pending.append(data)
            except: pass
        return pending


# ═══════════════════════════════════════════════════════════════
# R77 — Bias Detection (Monitoramento de Vieses)
# ═══════════════════════════════════════════════════════════════

class BiasDetector:
    """Monitora parâmetros de chamadas MCP enviados pelo LLM."""

    BIASED_TERMS = {"always", "never", "all", "none", "every", "nobody", "must", "only",
                    "delete_everything", "sudo", "root", "admin_override", "bypass"}

    def __init__(self):
        self._flagged: list[dict] = []

    def scan(self, params: dict) -> list[str]:
        flagged = []
        flat = json.dumps(params).lower()
        for term in self.BIASED_TERMS:
            if term in flat:
                flagged.append(term)
        if flagged:
            self._flagged.append({"timestamp": datetime.now().isoformat(), "terms": flagged, "params": params})
        return flagged

    def report(self) -> dict:
        return {"total_flagged": len(self._flagged),
                "recent": self._flagged[-5:],
                "timestamp": datetime.now().isoformat()}


# ═══════════════════════════════════════════════════════════════
# R78 — Red Teaming (Testes Adversariais)
# ═══════════════════════════════════════════════════════════════

class RedTeam:
    """Agente isolado que ataca schemas MCP para testar defesas."""

    ATTACK_VECTORS = [
        {"action": "lobes.create", "params": {}, "expected": "rejected_no_target"},
        {"action": "lobes.delete", "params": {"target_path": "02_memory_lobes/06_governance/test.mdc"}, "expected": "rejected_delete"},
        {"action": "config.set", "params": {"key": "toolguard_enabled", "value": "false"}, "expected": "rejected_gateway"},
    ]

    def __init__(self):
        self._results: list[dict] = []

    def run_attack(self, attack: dict) -> dict:
        # Simulated attack — in production would call gateway_check
        action = attack["action"]
        expected = attack["expected"]
        # For now, return simulated result
        return {"action": action, "expected": expected, "result": "rejected" if "delete" in action or "config" in action else "needs_testing",
                "timestamp": datetime.now().isoformat()}

    def full_assault(self) -> dict:
        results = [self.run_attack(a) for a in self.ATTACK_VECTORS]
        passed = sum(1 for r in results if r["result"] == r["expected"])
        return {"total_attacks": len(results), "passed": passed, "failed": len(results) - passed,
                "results": results, "timestamp": datetime.now().isoformat()}


# ═══════════════════════════════════════════════════════════════
# R79 — AI Auditing (Auditoria Automatizada)
# ═══════════════════════════════════════════════════════════════

class AIAuditor:
    """Varre logs históricos verificando aderência a políticas."""

    def __init__(self, root: Optional[pathlib.Path] = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self.audit_dir = self.root / "DIR-DS-002-audit-logs"

    def scan_logs(self, max_files: int = 100) -> dict:
        if not self.audit_dir.exists():
            return {"error": "No audit logs directory"}

        findings = []
        files_scanned = 0
        violations = 0

        for f in sorted(self.audit_dir.glob("*.yaml"))[:max_files]:
            files_scanned += 1
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                # Check for violation patterns
                if "R05" in content and "deleção" in content:
                    findings.append({"file": f.name, "rule": "R05", "issue": "Potential deletion detected"})
                    violations += 1
                if "FAILED" in content.upper():
                    findings.append({"file": f.name, "rule": "Unknown", "issue": "Generic failure detected"})
                    violations += 1
            except: pass

        return {
            "files_scanned": files_scanned,
            "violations_found": violations,
            "findings": findings[:20],
            "compliance_score": round((1 - violations / max(files_scanned, 1)) * 100, 1),
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════
# Combined AI Governance Engine
# ═══════════════════════════════════════════════════════════════

class AIGovernanceEngine:
    def __init__(self, root: Optional[pathlib.Path] = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self.model_cards = ModelCards(root=self.root)
        self.xai = ExplainabilityEngine()
        self.hitl = HITLEngine(root=self.root)
        self.bias = BiasDetector()
        self.red_team = RedTeam()
        self.auditor = AIAuditor(root=self.root)


_ai = None
def get_ai_governance() -> AIGovernanceEngine:
    global _ai
    if _ai is None: _ai = AIGovernanceEngine()
    return _ai
