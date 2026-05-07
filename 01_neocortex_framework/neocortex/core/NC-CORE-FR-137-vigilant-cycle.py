# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class VigilantCycle:
    """CICLO 0 — Vigilante. Roda após cada interação user↔AI."""

    def __init__(self, root: Path | None = None):
        import os as _os
        self.root = root or Path(_os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.turns: list[dict[str, Any]] = []
        self.detected_patterns: dict[str, int] = {}
        self.pending_proposals: list[dict[str, Any]] = []
        self._log_file = self.root / ".neocortex" / "vigilant" / "cycle0.jsonl"
        self._log_file.parent.mkdir(parents=True, exist_ok=True)

    # ── TURN RECORD: após cada interação ──────────────────────

    def record_turn(self, user_message: str, ai_action: str,
                    result: dict[str, Any]) -> dict[str, Any]:
        """
        Registrar turno e analisar.
        Chamado APÓS cada interação user↔AI.
        """
        ts = datetime.now().isoformat()
        turn = {
            "timestamp": ts,
            "user_message": user_message[:300],
            "ai_action": ai_action,
            "result_summary": str(result.get("success", "?"))[:100],
            "errors": result.get("violations", result.get("error", ""))[:200],
        }
        self.turns.append(turn)

        # Persistir
        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(turn, ensure_ascii=False) + "\n")

        # Analisar padrões
        analysis = self._analyze_turn(turn)

        return {
            "turn_recorded": True,
            "total_turns": len(self.turns),
            "patterns_detected": len(self.detected_patterns),
            "pending_proposals": len(self.pending_proposals),
            "analysis": analysis,
        }

    # ── ANALYZE: detectar padrões ──────────────────────────────

    def _analyze_turn(self, turn: dict[str, Any]) -> dict[str, Any]:
        """Analisar turno e detectar padrões de governança."""
        findings = []

        # 1. Detectar erros repetidos
        errors = turn.get("errors", "")
        if errors:
            errors_key = errors[:80]  # truncar para agrupar similares
            self.detected_patterns[errors_key] = self.detected_patterns.get(errors_key, 0) + 1

            if self.detected_patterns[errors_key] >= 3:
                findings.append({
                    "type": "recurring_error",
                    "pattern": errors_key,
                    "count": self.detected_patterns[errors_key],
                    "action": "analisar para proposta de emenda",
                })

        # 2. Detectar ações sem handoff
        action = turn.get("ai_action", "")
        if any(w in action.lower() for w in ["write", "create", "modify", "delete"]):
            has_handoff = "handoff" in str(turn.get("result_summary", "")).lower()
            if not has_handoff:
                findings.append({
                    "type": "missing_handoff",
                    "action": action,
                    "suggestion": "Criar handoff para ação de escrita",
                })

        # 3. Detectar padrões de naming
        if "naming" in str(errors).lower() or "NC-" in str(errors):
            findings.append({
                "type": "naming_violation",
                "suggestion": "Reforçar R01 no ToolGuard ou propor emenda ao CPC",
            })

        # 4. Propor auto-emenda se padrão recorrente
        proposals_generated = 0
        for pattern, count in self.detected_patterns.items():
            if count >= 3 and not any(p.get("pattern") == pattern for p in self.pending_proposals):
                proposal = self._generate_proposal(pattern, count)
                self.pending_proposals.append(proposal)
                proposals_generated += 1
                findings.append({
                    "type": "auto_amendment_proposed",
                    "pattern": pattern,
                    "count": count,
                    "proposal_id": proposal.get("id"),
                })

        return {"findings": findings, "proposals_generated": proposals_generated}

    # ── GENERATE PROPOSAL: criar emenda ────────────────────────

    def _generate_proposal(self, pattern: str, count: int) -> dict[str, Any]:
        """Gerar proposta de emenda baseada em padrão detectado."""
        proposal_id = f"VIG-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Classificar o tipo de erro para mapear ao diploma correto
        if "LOCK" in pattern.upper() or "lock" in pattern.lower():
            diploma = "NC-SEC-FR-001-atomic-locks.yaml"
            category = "LOCK"
        elif "NAMING" in pattern.upper() or "NC-" in pattern:
            diploma = "NC-LBE-FR-CONSTITUTION-001.mdc"
            category = "NAMING"
        elif "ZONE" in pattern.upper() or "write" in pattern.lower():
            diploma = "NC-CORE-FR-131-federative-pact.py"
            category = "WRITE_ZONE"
        else:
            diploma = "NC-LBE-FR-CONSTITUTION-001.mdc"
            category = "GOVERNANCE"

        return {
            "id": proposal_id,
            "pattern": pattern,
            "count": count,
            "diploma": diploma,
            "category": category,
            "status": "pending_t0_approval",
            "detected_at": datetime.now().isoformat(),
            "suggested_action": f"Propor emenda ao {diploma} para tratar padrão: {pattern[:100]}",
        }

    # ── APPROVE/REJECT: T0 decide ──────────────────────────────

    def approve_proposal(self, proposal_id: str) -> dict[str, Any]:
        """T0 aprova proposta e envia para auto-amendment engine."""
        for p in self.pending_proposals:
            if p["id"] == proposal_id:
                try:
                    from .NC_CORE_FR_136_auto_amendment_engine import (
                        get_amendment_engine,
                    )
                    engine = get_amendment_engine()
                    result = engine.propose_amendment(
                        error_category=p["category"],
                        description=f"CICLO 0 detectou padrão recorrente ({p['count']}x): {p['pattern']}",
                        proposed_change=p["suggested_action"],
                    )
                    if result.get("success"):
                        p["status"] = "forwarded_to_legislative"
                        return {"success": True, "proposal_id": proposal_id,
                                "amendment_id": result.get("amendment_id")}
                except Exception as e:
                    return {"success": False, "error": str(e)}

        return {"success": False, "error": "Proposta não encontrada"}

    def reject_proposal(self, proposal_id: str, reason: str = "") -> dict[str, Any]:
        """T0 rejeita proposta."""
        for p in self.pending_proposals:
            if p["id"] == proposal_id:
                p["status"] = "rejected_by_t0"
                p["rejection_reason"] = reason
                return {"success": True, "proposal_id": proposal_id, "status": "rejected"}
        return {"success": False, "error": "Proposta não encontrada"}

    # ── STATUS ─────────────────────────────────────────────────

    def get_status(self) -> dict[str, Any]:
        """Status do CICLO 0 + Drift Control (R37)."""
        drift = self._calculate_drift()
        return {
            "total_turns": len(self.turns),
            "detected_patterns": len(self.detected_patterns),
            "pending_proposals": len([p for p in self.pending_proposals
                                      if p.get("status") == "pending_t0_approval"]),
            "forwarded_proposals": len([p for p in self.pending_proposals
                                        if p.get("status") == "forwarded_to_legislative"]),
            "rejected_proposals": len([p for p in self.pending_proposals
                                       if p.get("status") == "rejected_by_t0"]),
            "top_patterns": sorted(self.detected_patterns.items(),
                                   key=lambda x: x[1], reverse=True)[:5],
            "drift": drift,
        }

    def _calculate_drift(self) -> dict[str, Any]:
        """R37: Calcular identity hysteresis ratio."""
        total = len(self.turns)
        if total < 10:
            return {"ratio": 0.0, "status": "insufficient_data", "threshold": 0.68}
        errors = sum(1 for t in self.turns if t.get("errors"))
        ratio = errors / total if total > 0 else 0
        return {
            "ratio": round(ratio, 4),
            "status": "STABLE" if ratio < 0.5 else ("WARNING" if ratio < 0.68 else "DRIFT_DETECTED"),
            "threshold": 0.68,
            "mutations_paused": ratio >= 0.68,
        }


# Singleton
_vigilant_cycle: VigilantCycle | None = None


def get_vigilant_cycle() -> VigilantCycle:
    global _vigilant_cycle
    if _vigilant_cycle is None:
        _vigilant_cycle = VigilantCycle()
    return _vigilant_cycle
