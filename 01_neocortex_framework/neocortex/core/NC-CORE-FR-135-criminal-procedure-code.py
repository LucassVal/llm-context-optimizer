"""---
@Code NC-CORE-FR-135-criminal-procedure-code mcp NC-CORE-FR-135-criminal-procedure-code.py — CPP Di
---
"""


import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CrimeSeverity(Enum):
    CONTRAVENTION = "contravencao"   # advertência
    MISDEMEANOR = "crime_medio"      # suspensão temporária
    FELONY = "crime_grave"           # quarentena
    CAPITAL = "crime_capital"        # bloqueio permanente


class PrisonStatus(Enum):
    FREE = "livre"
    WARNING = "advertido"
    SUSPENDED = "suspenso"
    QUARANTINED = "em_quarentena"
    BLOCKED = "bloqueado_permanentemente"
    PAROLED = "liberdade_condicional"


CRIMES = {
    "LOCK_VIOLATION": {
        "article": "Art. 1º Lei de Segurança Digital",
        "severity": CrimeSeverity.FELONY,
        "pena_base": "quarentena 24h",
        "description": "Violação de Atomic Lock",
    },
    "WRITE_ZONE_VIOLATION": {
        "article": "Art. 2º Lei de Segurança Digital",
        "severity": CrimeSeverity.MISDEMEANOR,
        "pena_base": "suspensão 6h",
        "description": "Escrita fora da zona permitida",
    },
    "NAMING_VIOLATION": {
        "article": "Art. 3º Lei de Segurança Digital",
        "severity": CrimeSeverity.CONTRAVENTION,
        "pena_base": "advertência",
        "description": "Violação de convenção NC-",
    },
    "STEP0_BYPASS": {
        "article": "Art. 4º Lei de Segurança Digital",
        "severity": CrimeSeverity.FELONY,
        "pena_base": "quarentena 48h",
        "description": "Bypass do STEP 0 (devido processo)",
    },
    "REPLICATION_ABUSE": {
        "article": "Art. 5º Lei de Segurança Digital",
        "severity": CrimeSeverity.CAPITAL,
        "pena_base": "bloqueio permanente",
        "description": "Abuso de replicação (R0 > 5/hora)",
    },
    "KEY_THEFT": {
        "article": "Art. 6º Lei de Segurança Digital",
        "severity": CrimeSeverity.CAPITAL,
        "pena_base": "bloqueio permanente + auditoria",
        "description": "Tentativa de acesso a chaves mestras",
    },
}


class CriminalProcedureCode:
    """CPP Digital — investigação, processo e execução penal."""

    def __init__(self, root: Path | None = None):
        import os as _os
        self.root = root or Path(_os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.investigations: dict[str, dict[str, Any]] = {}
        self.prison: dict[str, dict[str, Any]] = {}
        self._prison_file = self.root / ".neocortex" / "prison.json"
        self._load_prison()

    # ── INQUÉRITO POLICIAL (Guardian investiga) ────────────────

    def investigate(self, suspect: str, crime_type: str,
                    evidence: dict[str, Any],
                    investigator: str = "Guardian") -> dict[str, Any]:
        """Art. 4º CPP: Inquérito Policial — Guardian investiga."""
        if crime_type not in CRIMES:
            return {"success": False, "error": f"Tipo criminal '{crime_type}' não tipificado"}

        case_id = f"CPP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        crime = CRIMES[crime_type]
        self.investigations[case_id] = {
            "case_id": case_id,
            "suspect": suspect,
            "crime": crime_type,
            "severity": crime["severity"].value,
            "investigator": investigator,
            "evidence": [evidence],
            "status": "investigando",
            "opened_at": datetime.now().isoformat(),
        }
        return {"success": True, "case_id": case_id, "suspect": suspect,
                "crime": crime["description"], "severity": crime["severity"].value}

    # ── DENÚNCIA (MP — Compliance auditor) ────────────────────

    def indict(self, case_id: str, prosecutor: str = "MP") -> dict[str, Any]:
        """Art. 41 CPP: Denúncia — Ministério Público oferece denúncia."""
        if case_id not in self.investigations:
            return {"success": False, "error": "Inquérito não encontrado"}

        case = self.investigations[case_id]
        if case["status"] != "investigando":
            return {"success": False, "error": f"Status inválido: {case['status']}"}

        # Verificar se há provas suficientes
        evidence_count = len(case.get("evidence", []))
        if evidence_count < 1:
            return {"success": False, "error": "CPP Art. 41: provas insuficientes para denúncia"}

        case["status"] = "denunciado"
        case["prosecutor"] = prosecutor
        case["indicted_at"] = datetime.now().isoformat()
        return {"success": True, "case_id": case_id, "status": "denunciado",
                "next": "instrucao_processual"}

    # ── INSTRUÇÃO (Provas — WAL audit) ────────────────────────

    def gather_evidence(self, case_id: str, evidence: dict[str, Any]) -> dict[str, Any]:
        """Art. 155 CPP: Produção de provas."""
        if case_id not in self.investigations:
            return {"success": False, "error": "Caso não encontrado"}

        self.investigations[case_id].setdefault("evidence", []).append(evidence)
        return {"success": True, "case_id": case_id,
                "total_evidence": len(self.investigations[case_id]["evidence"])}

    # ── SENTENÇA (Juiz — Kernel 0) ────────────────────────────

    def sentence(self, case_id: str, judge: str = "Kernel0") -> dict[str, Any]:
        """Art. 381 CPP: Sentença — Kernel 0 julga."""
        if case_id not in self.investigations:
            return {"success": False, "error": "Caso não encontrado"}

        case = self.investigations[case_id]
        crime = CRIMES.get(case["crime"], {})
        severity = crime.get("severity", CrimeSeverity.CONTRAVENTION)

        # Determinar pena
        penalties = {
            CrimeSeverity.CONTRAVENTION: {"status": PrisonStatus.WARNING, "duration_hours": 0},
            CrimeSeverity.MISDEMEANOR: {"status": PrisonStatus.SUSPENDED, "duration_hours": 6},
            CrimeSeverity.FELONY: {"status": PrisonStatus.QUARANTINED, "duration_hours": 24},
            CrimeSeverity.CAPITAL: {"status": PrisonStatus.BLOCKED, "duration_hours": -1},
        }
        penalty = penalties.get(severity, penalties[CrimeSeverity.CONTRAVENTION])

        # Registrar no sistema prisional
        prisoner = {
            "case_id": case_id,
            "agent": case["suspect"],
            "crime": case["crime"],
            "status": penalty["status"].value,
            "sentence": penalty["duration_hours"],
            "started_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=penalty["duration_hours"])).isoformat()
            if penalty["duration_hours"] > 0 else None,
            "judge": judge,
        }
        self.prison[case["suspect"]] = prisoner
        self._save_prison()

        case["status"] = "sentenciado"
        case["sentence"] = penalty["status"].value
        return {"success": True, "case_id": case_id, "suspect": case["suspect"],
                "sentence": penalty["status"].value, "duration_hours": penalty["duration_hours"]}

    # ── EXECUÇÃO PENAL (Quarantine Manager) ───────────────────

    def check_prisoner(self, agent_id: str) -> tuple[bool, dict[str, Any]]:
        """Verificar se agente está preso/suspenso."""
        if agent_id not in self.prison:
            return True, {"status": PrisonStatus.FREE.value}

        prisoner = self.prison[agent_id]
        status = prisoner.get("status", PrisonStatus.FREE.value)

        # Verificar se pena expirou
        if prisoner.get("expires_at"):
            expires = datetime.fromisoformat(prisoner["expires_at"])
            if datetime.now() > expires:
                if status in [PrisonStatus.SUSPENDED.value, PrisonStatus.QUARANTINED.value]:
                    prisoner["status"] = PrisonStatus.FREE.value
                    self._save_prison()
                    return True, {"status": PrisonStatus.FREE.value,
                                  "note": "Pena cumprida — liberdade restaurada"}

        # Verificar liberdade condicional
        if status == PrisonStatus.PAROLED.value:
            return True, {"status": PrisonStatus.PAROLED.value,
                          "conditions": "Monitorado pelo Guardian"}

        # Bloqueado permanentemente
        if status == PrisonStatus.BLOCKED.value:
            return False, {"status": PrisonStatus.BLOCKED.value,
                           "reason": f"Crime: {prisoner.get('crime', 'desconhecido')}",
                           "appeal_to": "Kernel0"}

        # Suspenso ou em quarentena
        if status in [PrisonStatus.SUSPENDED.value, PrisonStatus.QUARANTINED.value]:
            return False, {"status": status, "expires_at": prisoner.get("expires_at"),
                           "reason": f"Crime: {prisoner.get('crime', 'desconhecido')}"}

        return True, {"status": prisoner.get("status", PrisonStatus.FREE.value)}

    def parole(self, agent_id: str, conditions: str = "",
               authorized_by: str = "Kernel0") -> dict[str, Any]:
        """Conceder liberdade condicional."""
        if agent_id not in self.prison:
            return {"success": False, "error": "Agente não está preso"}

        if authorized_by != "Kernel0":
            return {"success": False,
                    "error": "Apenas Kernel 0 pode conceder liberdade condicional"}

        self.prison[agent_id]["status"] = PrisonStatus.PAROLED.value
        self.prison[agent_id]["parole_conditions"] = conditions
        self._save_prison()
        return {"success": True, "agent": agent_id,
                "status": PrisonStatus.PAROLED.value, "conditions": conditions}

    def list_prisoners(self) -> list[dict[str, Any]]:
        """Listar todos os presos/suspensos."""
        return [
            {"agent": aid, "status": p.get("status"), "crime": p.get("crime"),
             "expires": p.get("expires_at")}
            for aid, p in self.prison.items()
            if p.get("status") != PrisonStatus.FREE.value
        ]

    # ── PERSISTÊNCIA ──────────────────────────────────────────

    def _load_prison(self) -> None:
        if self._prison_file.exists():
            try:
                self.prison = json.loads(self._prison_file.read_text(encoding="utf-8"))
            except Exception:
                self.prison = {}

    def _save_prison(self) -> None:
        self._prison_file.parent.mkdir(parents=True, exist_ok=True)
        self._prison_file.write_text(json.dumps(self.prison, indent=2, ensure_ascii=False),
                                     encoding="utf-8")


# Singleton
_cpp_instance: CriminalProcedureCode | None = None


def get_cpp() -> CriminalProcedureCode:
    global _cpp_instance
    if _cpp_instance is None:
        _cpp_instance = CriminalProcedureCode()
    return _cpp_instance
