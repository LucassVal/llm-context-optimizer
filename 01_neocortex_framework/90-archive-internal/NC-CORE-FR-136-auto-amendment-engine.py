"""---
NC-CORE-FR-136-auto-amendment-engine.py — Motor de Auto-Emenda Constitucional
STEP 0 + Governance: propõe alterações com base em erros recorrentes

Princípio:
  1. Regression Buffer detecta padrão rec
---
"""


import hashlib
import json
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# Mapeamento: tipo de erro → diploma a ser emendado
ERROR_TO_DIPLOMA = {
    "LOCK": "NC-SEC-FR-001-atomic-locks.yaml",
    "WRITE_ZONE": "NC-CORE-FR-131-federative-pact.py",
    "NAMING": "NC-LBE-FR-CONSTITUTION-001.mdc",
    "STEP0": "NC-CORE-FR-132-civil-procedure-code.py",
    "CRIME": "NC-CORE-FR-135-criminal-procedure-code.py",
    "REPLICATION": "NC-CORE-FR-130-genome-replicator.py",
    "GOVERNANCE": "NC-LBE-FR-CONSTITUTION-001.mdc",
    "COMPLIANCE": "NC-LBE-FR-CONSTITUTION-001.mdc",
}


class AutoAmendmentEngine:
    """Motor de auto-emenda — STEP 0 aprende e propõe mudanças."""

    def __init__(self, root: Optional[Path] = None):
        import os as _os
        self.root = root or Path(_os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.proposals_file = self.root / ".neocortex" / "amendments" / "proposals.json"
        self.proposals_file.parent.mkdir(parents=True, exist_ok=True)
        self.proposals: List[Dict[str, Any]] = self._load_proposals()

    # ── ANALYZE: detectar padrões recorrentes ──────────────────

    def analyze_regression_buffer(self) -> Dict[str, Any]:
        """
        Analisar buffer de regressão e detectar padrões que justificam emenda.
        STEP 0 → detect → propose → legislate.
        """
        try:
            from .NC_CORE_FR_123_regression_service import get_regression_service
            svc = get_regression_service()
            entries = svc.list_all_entries()
            all_errors = entries.get("entries", [])
        except Exception:
            return {"success": False, "error": "Regression buffer indisponível"}

        if not all_errors:
            return {"success": True, "patterns_found": 0, "note": "Buffer vazio"}

        # Categorizar erros
        categories = Counter()
        for entry in all_errors:
            error_text = entry.get("error", "")
            # Classificar por tipo
            if "LOCK" in error_text or "lock" in error_text:
                categories["LOCK"] += 1
            elif "ZONE" in error_text or "zone" in error_text or "write" in error_text:
                categories["WRITE_ZONE"] += 1
            elif "NAMING" in error_text or "naming" in error_text or "NC-" in error_text:
                categories["NAMING"] += 1
            elif "STEP" in error_text or "step" in error_text:
                categories["STEP0"] += 1
            elif "REPLIC" in error_text or "fork" in error_text:
                categories["REPLICATION"] += 1
            else:
                categories["GOVERNANCE"] += 1

        # Filtrar padrões recorrentes (>3 ocorrências)
        patterns = {k: v for k, v in categories.items() if v >= 3}

        return {
            "success": True,
            "total_errors": len(all_errors),
            "patterns_found": len(patterns),
            "patterns": dict(patterns),
            "diplomas_affected": [ERROR_TO_DIPLOMA.get(p, "unknown") for p in patterns],
        }

    # ── PROPOSE: gerar emenda para diploma específico ─────────

    def propose_amendment(
        self, error_category: str, description: str, proposed_change: str
    ) -> Dict[str, Any]:
        """
        Propor emenda a um diploma jurídico.
        A emenda é armazenada DENTRO do arquivo do diploma (seção de emendas).
        """
        if error_category not in ERROR_TO_DIPLOMA:
            return {"success": False, "error": f"Categoria '{error_category}' não mapeada a diploma"}

        diploma = ERROR_TO_DIPLOMA[error_category]
        amendment_id = f"EMD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hashlib.md5(description.encode()).hexdigest()[:6]}"

        proposal = {
            "amendment_id": amendment_id,
            "diploma": diploma,
            "category": error_category,
            "description": description,
            "proposed_change": proposed_change,
            "status": "proposto",  # proposto → plebiscito → congresso → ratificado
            "proposed_at": datetime.now().isoformat(),
            "votes": {"favor": 0, "contra": 0},
            "ratified": False,
        }

        # NÃO criar arquivo novo — armazenar no proposals.json (índice)
        # e ANEXAR ao diploma alvo como seção de emendas pendentes
        self._append_to_diploma(diploma, proposal)
        self.proposals.append(proposal)
        self._save_proposals()

        return {
            "success": True,
            "amendment_id": amendment_id,
            "diploma": diploma,
            "status": "proposto",
            "next_step": "plebiscito ou congresso para ratificação",
        }

    def _append_to_diploma(self, diploma_path: str, proposal: Dict[str, Any]) -> None:
        """Anexar proposta de emenda ao final do diploma alvo."""
        targets = [
            self.root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / diploma_path,
            self.root / "02_memory_lobes" / "01_framework" / diploma_path,
            self.root / "02_memory_lobes" / "06_governance" / diploma_path,
            self.root / "01_neocortex_framework" / "neocortex" / "core" / diploma_path,
        ]
        for target in targets:
            if target.exists():
                amendment_text = f"""
<!-- AMENDMENT PROPOSAL {proposal['amendment_id']} -->
<!-- Status: {proposal['status']} | Category: {proposal['category']} -->
<!-- {proposal['description']} -->
<!-- Proposed change: {proposal['proposed_change']} -->
"""
                with open(target, "a", encoding="utf-8") as f:
                    f.write(amendment_text)
                logger.info(f"[Amendment] Appended to {target.name}: {proposal['amendment_id']}")
                return

    # ── VOTE: plebiscito sobre emenda ──────────────────────────

    def vote_amendment(self, amendment_id: str, vote: str, voter: str = "T0") -> Dict[str, Any]:
        """Votar em proposta de emenda."""
        for p in self.proposals:
            if p["amendment_id"] == amendment_id:
                if vote == "favor":
                    p["votes"]["favor"] += 1
                else:
                    p["votes"]["contra"] += 1

                # Ratificação automática se favor > 3 e sem votos contra
                if p["votes"]["favor"] >= 3 and p["votes"]["contra"] == 0:
                    p["status"] = "ratificado"
                    p["ratified"] = True
                    p["ratified_at"] = datetime.now().isoformat()

                self._save_proposals()
                return {"success": True, "amendment_id": amendment_id,
                        "status": p["status"], "votes": p["votes"]}

        return {"success": False, "error": "Emenda não encontrada"}

    # ── LIST: emendas pendentes e ratificadas ──────────────────

    def list_amendments(self, status: str = "") -> List[Dict[str, Any]]:
        """Listar emendas."""
        if not status:
            return self.proposals
        return [p for p in self.proposals if p.get("status") == status]

    def get_diploma_amendments(self, diploma: str) -> List[Dict[str, Any]]:
        """Listar emendas de um diploma específico."""
        return [p for p in self.proposals if p.get("diploma") == diploma]

    # ── PERSISTÊNCIA ──────────────────────────────────────────

    def _load_proposals(self) -> List[Dict[str, Any]]:
        if self.proposals_file.exists():
            try:
                return json.loads(self.proposals_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return []

    def _save_proposals(self) -> None:
        self.proposals_file.write_text(
            json.dumps(self.proposals, indent=2, ensure_ascii=False), encoding="utf-8")


# Singleton
_amendment_engine: Optional[AutoAmendmentEngine] = None


def get_amendment_engine() -> AutoAmendmentEngine:
    global _amendment_engine
    if _amendment_engine is None:
        _amendment_engine = AutoAmendmentEngine()
    return _amendment_engine
