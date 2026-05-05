"""---
@Module NC-CORE-FR-134-legislative-process mcp NC-CORE-FR-134-legislative-process.py — Processo L
---
"""


import logging
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class LegislativeInstrument(Enum):
    """Instrumentos legislativos (CF/88 Art. 59)."""
    EMENDA_CONSTITUCIONAL = "emenda_constitucional"  # 3/5 + Kernel 0
    LEI_COMPLEMENTAR = "lei_complementar"            # maioria absoluta
    LEI_ORDINARIA = "lei_ordinaria"                   # maioria simples
    MEDIDA_PROVISORIA = "medida_provisoria"           # Kernel 0 emergency
    PLEBISCITO = "plebiscito"                         # consulta popular
    REFERENDO = "referendo"                           # ratificação


class VoteType(Enum):
    FAVOR = "favor"
    CONTRA = "contra"
    ABSTENCAO = "abstencao"


class LegislativeProcess:
    """Processo Legislativo Digital — CF/88 Art. 59-69."""

    def __init__(self, root: Path | None = None):
        import os as _os
        self.root = root or Path(_os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.bills: dict[str, dict[str, Any]] = {}
        self.votes: dict[str, dict[str, VoteType]] = {}
        self.constitution_amendments: list[dict[str, Any]] = []

    # ── PLEBISCITO (Art. 14 CF/88) ─────────────────────────────

    def propose_plebiscite(self, question: str, options: list[str],
                           proposer: str = "T0") -> dict[str, Any]:
        """Convocar plebiscito — consulta popular sobre feature."""
        bill_id = f"PLEB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.bills[bill_id] = {
            "type": LegislativeInstrument.PLEBISCITO.value,
            "question": question,
            "options": options,
            "proposer": proposer,
            "status": "voting",
            "created_at": datetime.now().isoformat(),
            "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
        }
        self.votes[bill_id] = {}
        return {
            "success": True,
            "bill_id": bill_id,
            "question": question,
            "options": options,
            "vote_until": self.bills[bill_id]["deadline"],
        }

    def vote_plebiscite(self, bill_id: str, option: str,
                        voter: str = "T0") -> dict[str, Any]:
        """Votar em plebiscito."""
        if bill_id not in self.bills:
            return {"success": False, "error": f"PLEBISCITO {bill_id} não encontrado"}

        bill = self.bills[bill_id]
        if bill["status"] != "voting":
            return {"success": False, "error": f"Votação encerrada: {bill['status']}"}

        if option not in bill["options"]:
            return {"success": False, "error": f"Opção '{option}' inválida"}

        self.votes[bill_id][voter] = option
        return {"success": True, "bill_id": bill_id, "voter": voter, "vote": option}

    def tally_plebiscite(self, bill_id: str) -> dict[str, Any]:
        """Apuracão de plebiscito."""
        if bill_id not in self.bills:
            return {"success": False, "error": "PLEBISCITO não encontrado"}

        votes = self.votes.get(bill_id, {})
        tally = dict.fromkeys(self.bills[bill_id]["options"], 0)
        for v in votes.values():
            if v in tally:
                tally[v] += 1

        winner = max(tally, key=tally.get) if tally else None
        self.bills[bill_id]["status"] = "concluido"
        self.bills[bill_id]["result"] = tally
        self.bills[bill_id]["winner"] = winner

        return {
            "bill_id": bill_id,
            "question": self.bills[bill_id]["question"],
            "tally": tally,
            "total_votes": sum(tally.values()),
            "winner": winner,
            "status": "concluido",
        }

    # ── CONGRESSO — Processo Legislativo (Art. 59-69) ──────────

    def propose_law(self, title: str, description: str,
                    law_type: LegislativeInstrument,
                    proposer: str = "T0") -> dict[str, Any]:
        """Propor projeto de lei."""
        bill_id = f"PL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        required_votes = {
            LegislativeInstrument.EMENDA_CONSTITUCIONAL: 0.60,  # 3/5
            LegislativeInstrument.LEI_COMPLEMENTAR: 0.50,       # maioria absoluta
            LegislativeInstrument.LEI_ORDINARIA: 0.33,          # maioria simples
        }

        self.bills[bill_id] = {
            "type": law_type.value,
            "title": title,
            "description": description,
            "proposer": proposer,
            "status": "camara",
            "required_approval": required_votes.get(law_type, 0.5),
            "created_at": datetime.now().isoformat(),
            "camara_votes": {},
            "senado_votes": {},
        }
        return {"success": True, "bill_id": bill_id, "law_type": law_type.value,
                "next": "camara_voting"}

    def vote_law(self, bill_id: str, vote: VoteType,
                 voter: str = "T0", house: str = "camara") -> dict[str, Any]:
        """Votar em projeto de lei (Câmara ou Senado)."""
        if bill_id not in self.bills:
            return {"success": False, "error": f"PL {bill_id} não encontrado"}

        house_key = f"{house}_votes"
        self.bills[bill_id][house_key][voter] = vote.value
        return {"success": True, "bill_id": bill_id, "voter": voter,
                "vote": vote.value, "house": house}

    def process_law(self, bill_id: str) -> dict[str, Any]:
        """Processar projeto de lei — tramitação completa."""
        bill = self.bills.get(bill_id)
        if not bill:
            return {"success": False, "error": "PL não encontrado"}

        # Câmara
        camara_votes = bill.get("camara_votes", {})
        camara_approval = self._calculate_approval(camara_votes)

        if camara_approval < bill["required_approval"]:
            bill["status"] = "rejeitado_camara"
            return {"success": False, "bill_id": bill_id,
                    "reason": f"Rejeitado na Câmara: {camara_approval:.0%} < {bill['required_approval']:.0%}"}

        # Senado (para EC e LC)
        if bill["type"] in ["emenda_constitucional", "lei_complementar"]:
            bill["status"] = "senado"
            senado_votes = bill.get("senado_votes", {})
            senado_approval = self._calculate_approval(senado_votes)

            if senado_approval < bill["required_approval"]:
                bill["status"] = "rejeitado_senado"
                return {"success": False, "bill_id": bill_id,
                        "reason": f"Rejeitado no Senado: {senado_approval:.0%} < {bill['required_approval']:.0%}"}

        # Aprovado
        bill["status"] = "aprovado"
        bill["approved_at"] = datetime.now().isoformat()

        # Emenda Constitucional requer ratificação do Kernel 0
        needs_kernel = bill["type"] == LegislativeInstrument.EMENDA_CONSTITUCIONAL.value

        return {
            "success": True,
            "bill_id": bill_id,
            "law_type": bill["type"],
            "title": bill["title"],
            "camara_approval": f"{camara_approval:.0%}",
            "status": "aprovado",
            "needs_kernel_ratification": needs_kernel,
        }

    # ── MEDIDA PROVISÓRIA (Art. 62 CF/88) ─────────────────────

    def emergency_decree(self, title: str, action: str,
                         kernel_authorization: bool = False) -> dict[str, Any]:
        """
        Medida Provisória — decreto de emergência do Kernel 0.
        Art. 62: Em caso de relevância e urgência, Kernel 0 pode editar MP.
        """
        if not kernel_authorization:
            return {"success": False,
                    "error": "CF/88 Art. 62: MP requer autorização do Kernel 0"}

        mp_id = f"MP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.bills[mp_id] = {
            "type": LegislativeInstrument.MEDIDA_PROVISORIA.value,
            "title": title,
            "action": action,
            "status": "em_vigor",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=60)).isoformat(),
            "needs_congress_approval": True,
        }
        return {
            "success": True,
            "mp_id": mp_id,
            "title": title,
            "status": "EM VIGOR (60 dias)",
            "note": "Art. 62 CF/88: Submetida ao Congresso para aprovação",
        }

    # ── HELPERS ─────────────────────────────────────────────────

    def _calculate_approval(self, votes: dict[str, str]) -> float:
        """Calcular taxa de aprovação."""
        if not votes:
            return 0.0
        favor = sum(1 for v in votes.values() if v == "favor")
        return favor / len(votes)

    def list_bills(self, status: str = "") -> list[dict[str, Any]]:
        """Listar projetos de lei."""
        bills = []
        for bid, bill in self.bills.items():
            if not status or bill.get("status") == status:
                bills.append({"bill_id": bid, "title": bill.get("title", ""),
                              "type": bill.get("type", ""), "status": bill.get("status", "")})
        return bills

    def get_constitution_amendments(self) -> list[dict[str, Any]]:
        """Listar emendas constitucionais aprovadas."""
        return self.constitution_amendments


# Singleton
_legislative_instance: LegislativeProcess | None = None


def get_legislative() -> LegislativeProcess:
    global _legislative_instance
    if _legislative_instance is None:
        _legislative_instance = LegislativeProcess()
    return _legislative_instance
