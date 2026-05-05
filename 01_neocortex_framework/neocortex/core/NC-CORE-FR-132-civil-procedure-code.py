"""---
@Code NC-CORE-FR-132-civil-procedure-code mcp NC-CORE-FR-132-civil-procedure-code.py — CPC Digit
---
"""


import hashlib
import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ProceduralPhase(Enum):
    """Fases do processo civil digital."""
    PETITION = "peticao_inicial"
    ADMISSIBILITY = "admissibilidade"  # STEP 0
    CITATION = "citacao"               # notify parties
    CONTESTATION = "contestacao"       # regression check
    EVIDENCE = "provas"                # WAL audit
    FINAL_ARGUMENTS = "alegacoes_finais"  # ToolGuard
    SENTENCE = "sentenca"
    APPEAL = "recurso"
    RES_JUDICATA = "coisa_julgada"     # DNA immutable
    EXECUTION = "execucao"             # savepoint + rollback


class JudicialOrgan(Enum):
    """Órgãos do Poder Judiciário."""
    JUDGE_1ST = "juiz_1a_instancia"     # ToolGuard local
    COURT_2ND = "tribunal_2a_instancia" # Orbital
    STJ = "stj"                          # Parent
    STF = "stf"                          # Kernel 0
    PROSECUTOR = "ministerio_publico"    # Compliance auditor
    DEFENDER = "defensoria_publica"     # Error handler
    POLICE = "policia_judiciaria"       # Guardian


class CivilProcedureCode:
    """CPC Digital — devido processo legal para toda ação no NeoCortex."""

    def __init__(self, root: Path | None = None):
        import os as _os
        self.root = root or Path(_os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.case_registry: dict[str, dict[str, Any]] = {}
        self._warned_at = dict.fromkeys(["naming", "lock", "zone"], 0)

    # ── PROCESSO COMPLETO ──────────────────────────────────────

    def process_action(
        self,
        action: str,
        target_path: str = "",
        agent_id: str = "unknown",
        agent_role: str = "T0",
        urgency: str = "normal",
    ) -> tuple[bool, dict[str, Any]]:
        """
        CPC Art. 319 — Petição Inicial → Sentença.

        Fluxo completo do devido processo legal digital.
        """
        case_id = f"CPC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hashlib.md5(action.encode()).hexdigest()[:6]}"
        case = {
            "case_id": case_id,
            "action": action,
            "target": target_path,
            "agent": agent_id,
            "role": agent_role,
            "urgency": urgency,
            "started_at": datetime.now().isoformat(),
            "phases": [],
            "evidence": [],
            "violations": [],
            "status": "em_andamento",
        }

        # FASE 1: PETIÇÃO INICIAL (Art. 319 CPC)
        result = self._phase_petition(case, action, target_path, agent_id, agent_role)
        if not result["admitted"]:
            case["status"] = "indeferida"
            case["phases"].append({"phase": "peticao", "result": "indeferida",
                                    "reason": result["reason"]})
            self._archive_case(case)
            return False, case

        # FASE 2: ADMISSIBILIDADE — STEP 0 (Art. 321 CPC)
        result = self._phase_admissibility(case, action)
        if not result["passed"]:
            case["violations"].append(f"STEP-0: {result['reason']}")
            case["phases"].append({"phase": "admissibilidade", "result": "rejeitada"})
            if urgency != "emergency":
                case["status"] = "rejeitada_step0"
                self._archive_case(case)
                return False, case

        # FASE 3: CITAÇÃO (Art. 238 CPC) — notificar partes
        self._phase_citation(case, agent_id)

        # FASE 4: CONTESTAÇÃO (Art. 335 CPC) — regression check
        result = self._phase_contestation(case, action)
        case["evidence"].extend(result.get("evidence", []))

        # FASE 5: PROVAS (Art. 369 CPC) — WAL audit trail
        result = self._phase_evidence(case, target_path, agent_role)
        case["evidence"].extend(result.get("evidence", []))
        if not result["passed"]:
            case["violations"].extend(result.get("violations", []))

        # FASE 6: ALEGAÇÕES FINAIS (Art. 364 CPC) — ToolGuard
        result = self._phase_final_arguments(case, target_path, agent_role)
        case["evidence"].extend(result.get("evidence", []))

        # FASE 7: SENTENÇA (Art. 489 CPC)
        sentence = self._phase_sentence(case)

        # FASE 8: ARQUIVAMENTO + WAL
        self._archive_case(case)

        return sentence["allowed"], case

    # ── FASES ───────────────────────────────────────────────────

    def _phase_petition(self, case: dict, action: str, target: str,
                        agent_id: str, role: str) -> dict[str, Any]:
        """FASE 1: Petição Inicial — verifica requisitos formais."""
        case["phases"].append({"phase": "peticao", "timestamp": datetime.now().isoformat()})

        if not action:
            return {"admitted": False, "reason": "CPC Art. 319: ação não especificada"}
        if not agent_id:
            return {"admitted": False, "reason": "CPC Art. 319: parte não identificada"}

        # Verificar competência (qual órgão julga)
        court = self._determine_court(role)
        case["court"] = court.value

        return {"admitted": True, "court": court.value}

    def _phase_admissibility(self, case: dict, action: str) -> dict[str, Any]:
        """FASE 2: Admissibilidade — STEP 0 (regression check)."""
        case["phases"].append({"phase": "admissibilidade", "timestamp": datetime.now().isoformat()})

        try:
            from .NC_CORE_FR_123_regression_service import get_regression_service
            svc = get_regression_service()
            result = svc.check()
            recent = result.get("recent_errors", [])

            import difflib
            for err in recent:
                ratio = difflib.SequenceMatcher(None, action, err).ratio()
                if ratio > 0.5:
                    return {
                        "passed": False,
                        "reason": f"CPC Art. 321: ação {ratio:.0%} similar a erro passado",
                        "evidence": [{"type": "precedente", "match": err[:120], "ratio": ratio}],
                    }

            return {"passed": True, "buffer_size": result.get("buffer_size", 0)}
        except Exception as e:
            return {"passed": True, "note": f"STEP-0 indisponível: {e}"}

    def _phase_citation(self, case: dict, agent_id: str) -> None:
        """FASE 3: Citação — notificar partes (Art. 238 CPC)."""
        case["phases"].append({
            "phase": "citacao",
            "timestamp": datetime.now().isoformat(),
            "cited_party": agent_id,
            "method": "wal_notification",
        })

    def _phase_contestation(self, case: dict, action: str) -> dict[str, Any]:
        """FASE 4: Contestação — regression buffer + precedentes (Art. 335)."""
        case["phases"].append({"phase": "contestacao", "timestamp": datetime.now().isoformat()})

        evidence = []
        try:
            from .NC_CORE_FR_123_regression_service import get_regression_service
            svc = get_regression_service()
            entries = svc.list_all_entries()
            for entry in entries.get("entries", []):
                if any(w in entry.get("error", "") for w in action.split("_")):
                    evidence.append({
                        "type": "contestacao",
                        "entry": entry.get("error", "")[:200],
                        "severity": entry.get("severity", "unknown"),
                    })
        except Exception:
            pass

        return {"evidence": evidence[:3]}

    def _phase_evidence(self, case: dict, target: str,
                        role: str) -> dict[str, Any]:
        """FASE 5: Provas — WAL audit trail + Lock check (Art. 369)."""
        case["phases"].append({"phase": "provas", "timestamp": datetime.now().isoformat()})

        evidence = []
        violations = []

        # Prova 1: Atomic Lock check
        if target:
            try:
                from .NC_CORE_FR_014_lock_guard import get_lock_guard
                guard = get_lock_guard()
                allowed, reason = guard.check_write(target, role)
                evidence.append({
                    "type": "prova_lock",
                    "path": target,
                    "allowed": allowed,
                    "reason": reason,
                })
                if not allowed:
                    violations.append(f"LOCK: {reason}")
            except Exception:
                pass

        # Prova 2: Naming check
        if target:
            fname = Path(target).name
            if fname and not fname.startswith(".") and not fname.startswith("NC-"):
                violations.append(f"NAMING: {fname} não segue NC-")

        # Prova 3: Write Zone check
        if target and role != "T0":
            try:
                from .NC_CORE_FR_131_federative_pact import get_federative_pact
                pact = get_federative_pact()
                ok, msg = pact.can_do(f"escrever_em_{target.replace('/', '_')}",
                                      pact._instance_level)
                if not ok:
                    violations.append(f"WRITE-ZONE: {msg}")
            except Exception:
                pass

        # Prova 4: WAL audit — buscar ações similares no passado
        wal_dir = self.root / "DIR-DS-002-audit-logs"
        if wal_dir.exists():
            try:
                recent_wal = sorted(wal_dir.glob("NC-WAL-*.jsonl"),
                                   key=lambda p: p.stat().st_mtime, reverse=True)[:3]
                for wal in recent_wal:
                    evidence.append({"type": "prova_wal", "file": wal.name})
            except Exception:
                pass

        passed = len(violations) == 0
        return {"passed": passed, "evidence": evidence, "violations": violations}

    def _phase_final_arguments(self, case: dict, target: str,
                               role: str) -> dict[str, Any]:
        """FASE 6: Alegações Finais — ToolGuard pipeline (Art. 364)."""
        case["phases"].append({"phase": "alegacoes_finais", "timestamp": datetime.now().isoformat()})

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "tool_guard", str(Path(__file__).parent / "NC-CORE-FR-125-tool-guard.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            guard = mod.ToolGuard()

            evidence = []
            step0 = guard.step_zero(case["action"])
            evidence.append({"type": "step0", "result": step0})

            if target:
                write_ok = guard.validate_write(target, role)
                evidence.append({"type": "lockguard", "allowed": write_ok})

            naming = guard.check_naming(Path(target).name if target else "action")
            evidence.append({"type": "naming", "result": naming})

            signature = guard.sign_action(case["action"], role)
            evidence.append({"type": "crypto_sign", "signed": signature.get("signed")})

            return {"evidence": evidence}
        except Exception as e:
            return {"evidence": [{"type": "error", "detail": str(e)}]}

    def _phase_sentence(self, case: dict) -> dict[str, Any]:
        """FASE 7: Sentença — decisão final (Art. 489 CPC)."""
        case["phases"].append({"phase": "sentenca", "timestamp": datetime.now().isoformat()})

        violations = case.get("violations", [])
        evidence_count = len(case.get("evidence", []))

        if not violations:
            case["status"] = "deferida"
            return {
                "allowed": True,
                "sentence": "CPC Art. 487: AÇÃO DEFERIDA",
                "grounds": f"sem violações, {evidence_count} provas coletadas",
                "appealable": False,
            }
        elif len(violations) <= 2:
            case["status"] = "deferida_com_ressalvas"
            return {
                "allowed": True,
                "sentence": "CPC Art. 487: DEFERIDA COM RESSALVAS",
                "grounds": f"{len(violations)} violações não-bloqueantes",
                "violations": violations,
                "appealable": True,
            }
        else:
            case["status"] = "indeferida"
            return {
                "allowed": False,
                "sentence": "CPC Art. 487: AÇÃO INDEFERIDA",
                "grounds": f"{len(violations)} violações graves",
                "violations": violations,
                "appealable": True,
                "appeal_to": "orbital_parent",
            }

    # ── ÓRGÃOS DO JUDICIÁRIO ────────────────────────────────────

    def _determine_court(self, role: str) -> JudicialOrgan:
        """Determinar qual órgão do judiciário julga a ação."""
        courts = {
            "T0": JudicialOrgan.STF,
            "Guardian": JudicialOrgan.STJ,
            "T1": JudicialOrgan.COURT_2ND,
            "T2": JudicialOrgan.JUDGE_1ST,
            "T3": JudicialOrgan.JUDGE_1ST,
        }
        return courts.get(role, JudicialOrgan.JUDGE_1ST)

    def appeal(self, case_id: str, grounds: str) -> dict[str, Any]:
        """CPC Art. 994 — Interpor recurso."""
        # Buscar caso nos arquivos
        case = self._find_case(case_id)
        if not case:
            return {"success": False, "error": "CPC Art. 994: caso não encontrado"}

        # Recurso sobe para instância superior
        current_court = case.get("court", "juiz_1a_instancia")
        appeal_court = {
            "juiz_1a_instancia": "tribunal_2a_instancia",
            "tribunal_2a_instancia": "stj",
            "stj": "stf",
        }.get(current_court, "stf")

        return {
            "success": True,
            "case_id": case_id,
            "appeal_to": appeal_court,
            "grounds": grounds,
            "accepted": True,
            "note": "CPC Art. 1010: recurso interposto",
        }

    # ── ARQUIVAMENTO ───────────────────────────────────────────

    def _archive_case(self, case: dict) -> None:
        """Arquivar caso no WAL (coisa julgada)."""
        wal_dir = self.root / "DIR-DS-002-audit-logs"
        wal_dir.mkdir(parents=True, exist_ok=True)
        archive_file = wal_dir / f"NC-CPC-{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(archive_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(case, ensure_ascii=False) + "\n")

    def _find_case(self, case_id: str) -> dict | None:
        """Buscar caso arquivado."""
        wal_dir = self.root / "DIR-DS-002-audit-logs"
        if not wal_dir.exists():
            return None
        for f in sorted(wal_dir.glob("NC-CPC-*.jsonl"), reverse=True):
            for line in f.read_text(encoding="utf-8").strip().split("\n"):
                try:
                    c = json.loads(line)
                    if c.get("case_id") == case_id:
                        return c
                except Exception:
                    continue
        return None


# Singleton
_cpc_instance: CivilProcedureCode | None = None


def get_cpc() -> CivilProcedureCode:
    global _cpc_instance
    if _cpc_instance is None:
        _cpc_instance = CivilProcedureCode()
    return _cpc_instance
