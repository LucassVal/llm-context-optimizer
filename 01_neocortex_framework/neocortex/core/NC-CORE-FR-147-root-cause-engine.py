# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
"""---
@Engine NC-CORE-FR-147-root-cause-engine mcp NC-CORE-FR-147-root-cause-engine.py — Motor de 5 P
---
"""


import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

class RootCauseEngine:
    """Motor de 5 Porquês + 4 Porquês Estratégicos."""

    def __init__(self, root: Path | None = None):
        import os
        self.root = root or Path(os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.rca_dir = self.root / ".neocortex" / "rca"
        self.rca_dir.mkdir(parents=True, exist_ok=True)
        self.analyses: list[dict] = self._load()

    # ── 5 PORQUÊS (RCA) ────────────────────────────────────────

    def analyze_failure(self, problem: str, whys: list[str]) -> dict[str, Any]:
        """
        Analisar falha usando 5 Porquês.

        Args:
            problem: Descrição do problema
            whys: Lista de 4-5 respostas consecutivas aos "por quês"
        """
        rca_id = f"RCA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        analysis = {
            "id": rca_id,
            "type": "5whys",
            "problem": problem,
            "whys": [],
            "root_cause": whys[-1] if whys else "",
            "corrective_action": "",
            "created_at": datetime.now().isoformat(),
            "status": "analyzed",
        }
        for i, why in enumerate(whys):
            analysis["whys"].append({f"why_{i+1}": f"Por que? {why}"})

        # Determinar ação corretiva baseada na causa raiz
        root = whys[-1].lower() if whys else ""
        if "não há" in root or "não existe" in root:
            analysis["corrective_action"] = f"Criar: {root}"
        elif "processo" in root:
            analysis["corrective_action"] = f"Automatizar processo: {root}"
        elif "manual" in root:
            analysis["corrective_action"] = "Automatizar: substituir manual por automático"
        else:
            analysis["corrective_action"] = f"Corrigir causa raiz: {root}"

        self.analyses.append(analysis)
        self._save()
        return analysis

    def auto_analyze(self, rule: str, detail: str) -> dict[str, Any]:
        """Auto RCA — gerar 5 Porquês a partir de violação detectada."""
        problem = f"Violação {rule}: {detail[:100]}"

        # Template de 5 Porquês baseado na regra violada
        templates = {
            "R05": [
                f"O arquivo foi deletado sem arquivamento ({detail[:50]})",
                "O agente usou Remove-Item/del sem validação",
                "O BashGuard não interceptou o comando",
                "O Gateway não estava wireado no bash tool",
                "Não há hook de validação no nível do sistema operacional",
            ],
            "R01": [
                f"Arquivo não segue NC- naming ({detail[:50]})",
                "O agente criou arquivo sem prefixo NC-",
                "O ToolGuard não bloqueou a criação",
                "O STEP 0 não foi executado antes da ação",
                "O naming check era WARNING, não ENFORCED",
            ],
            "R09": [
                f"STEP 0 não bloqueou ação ({detail[:50]})",
                "O regression check retornou WARNING",
                "O agente ignorou o aviso",
                "O STEP 0 não tem poder de bloqueio",
                "O enforcement era documental, não real",
            ],
        }

        whys = templates.get(rule, [
            f"Violação detectada: {detail[:80]}",
            "O sistema não impediu a ação",
            "A regra não tem enforcement automático",
            "O Gateway não cobre este tipo de ação",
            "Falta hook de validação universal",
        ])

        return self.analyze_failure(problem, whys)

    # ── 4 PORQUÊS ESTRATÉGICOS ─────────────────────────────────

    def strategic_alignment(self, context: str = "") -> dict[str, Any]:
        """4 Porquês do Planejamento Estratégico — alinhamento contínuo."""
        return {
            "why_1_mission": "Garantir governança automatizada para todo agente de IA",
            "why_2_alignment": f"Eliminar stubs, wire-up enforcement, criar 4 mordaças ({context})",
            "why_3_improvement": "Falhas de hoje provam que documentação sem enforcement = ilusão",
            "why_4_performance": "STEP 0 era WARNING. Gateway não era universal. CHECKPOINT só observava.",
            "analyzed_at": datetime.now().isoformat(),
        }

    # ── REGISTRO + CONSULTA ────────────────────────────────────

    def log_failure_with_rca(self, rule: str, detail: str) -> dict[str, Any]:
        """Log integrado: registra violação + gera RCA automática."""
        rca = self.auto_analyze(rule, detail)
        # Persistir no WAL
        wal = self.root / "DIR-DS-002-audit-logs" / f"NC-WAL-RCA-{datetime.now().strftime('%Y%m%d')}.jsonl"
        wal.parent.mkdir(parents=True, exist_ok=True)
        with open(wal, "a", encoding="utf-8") as f:
            f.write(json.dumps({"violation": {"rule": rule, "detail": detail}, "rca": rca}, ensure_ascii=False) + "\n")
        return {"logged": True, "rca_id": rca["id"], "root_cause": rca["root_cause"]}

    def get_analyses(self, limit: int = 10) -> list[dict]:
        return self.analyses[-limit:]

    def _load(self) -> list[dict]:
        f = self.rca_dir / "analyses.json"
        if f.exists():
            try: return json.loads(f.read_text(encoding="utf-8"))
            except: pass
        return []

    def _save(self):
        (self.rca_dir / "analyses.json").write_text(json.dumps(self.analyses, indent=2, ensure_ascii=False), encoding="utf-8")

_rca: RootCauseEngine | None = None
def get_rca() -> RootCauseEngine:
    global _rca
    if _rca is None: _rca = RootCauseEngine()
    return _rca
