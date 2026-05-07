# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
"""---
@Pact NC-CORE-FR-131-federative-pact mcp NC-CORE-FR-131-federative-pact.py — Pacto Federati
---
"""


import logging
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class FederativeLevel(Enum):
    UNIAO = "uniao"         # Kernel 0 — competências exclusivas
    ESTADO = "estado"       # Parent — competências concorrentes
    MUNICIPIO = "municipio" # Child — competências locais
    DISTRITO = "distrito"   # Sub-child — administrativo


class CompetenceType(Enum):
    EXCLUSIVE = "exclusive"       # Só este nível pode
    CONCURRENT = "concurrent"     # União + Estados podem
    LOCAL = "local"               # Só Município pode
    DELEGATED = "delegated"       # Delegado por nível superior


class FederativePact:
    """Pacto Federativo — define competências e territórios de cada ente."""

    # Competências por nível (CF/88)
    COMPETENCIES = {
        FederativeLevel.UNIAO: {
            CompetenceType.EXCLUSIVE: [
                "definir_constituicao",      # CF/88 Art. 21
                "gerir_chaves_mestras",      # CryptoHub master key
                "declarar_guerra",           # desligar todo o sistema
                "emitir_moeda",              # criar tokens/recursos
                "relacoes_exteriores",       # APIs externas, bridges
                "criar_estados",             # spawnar parents
            ],
            CompetenceType.CONCURRENT: [
                "proteger_dados",            # CryptoHub (com estados)
                "auditar_contas",            # WAL (com estados)
                "legislar_sobre_ia",         # regras de agentes
                "fiscalizar_agentes",        # compliance
            ],
        },
        FederativeLevel.ESTADO: {
            CompetenceType.CONCURRENT: [
                "criar_municipios",          # spawnar children
                "proteger_dados",            # CryptoHub derivado
                "auditar_contas",            # WAL regional
                "organizar_territorio",      # write zones estaduais
            ],
            CompetenceType.EXCLUSIVE: [
                "legislacao_estadual",       # regras específicas do domínio
                "policia_estadual",          # guardian local
                "transporte_intermunicipal", # comunicação child→child
            ],
        },
        FederativeLevel.MUNICIPIO: {
            CompetenceType.LOCAL: [
                "criar_distritos",           # spawnar sub-children
                "legislacao_local",          # regras do child
                "ordenamento_urbano",        # organização interna
                "coleta_lixo",               # auto-cleanup (TTL)
                "transporte_local",          # comunicação interna
            ],
            CompetenceType.DELEGATED: [
                "fiscalizacao_sanitaria",    # sandbox health check
                "educacao_infantil",         # treinamento de sub-agentes
            ],
        },
        FederativeLevel.DISTRITO: {
            CompetenceType.DELEGATED: [
                "execucao_administrativa",   # tarefas delegadas
                "manutencao_local",          # auto-manutenção
            ],
        },
    }

    # Limites territoriais (Write Zones por nível)
    TERRITORIES = {
        FederativeLevel.UNIAO: ["*"],  # Soberania total
        FederativeLevel.ESTADO: [
            "01_neocortex_framework/",
            "02_memory_lobes/",
            "DIR-DS-*/",
            ".neocortex/sandbox/",
        ],
        FederativeLevel.MUNICIPIO: [
            ".neocortex/sandbox/{instance_name}/",
            "05_examples/",
            "DIR-DS-001-tickets/",
        ],
        FederativeLevel.DISTRITO: [
            ".neocortex/sandbox/{instance_name}/",
        ],
    }

    def __init__(self, root: Path | None = None):
        import os as _os
        self.root = root or Path(_os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self._instance_level = FederativeLevel.UNIAO

    # ── Competências ───────────────────────────────────────────

    def get_competencies(self, level: FederativeLevel) -> dict[str, list[str]]:
        """Listar todas as competências de um nível federativo."""
        comps = {}
        for ctype, items in self.COMPETENCIES.get(level, {}).items():
            comps[ctype.value] = items
        return comps

    def can_do(self, action: str, level: FederativeLevel) -> tuple[bool, str]:
        """
        Verificar se um nível federativo tem competência para uma ação.
        CF/88 Art. 21-30: distribuição de competências.
        """
        competencies = self.get_competencies(level)
        for ctype, actions in competencies.items():
            if action in actions:
                return True, f"{ctype} — permitido pelo Art. 21-30"
            # Fuzzy match
            for a in actions:
                if a.replace("_", " ") in action.replace("_", " "):
                    return True, f"similar a '{a}' ({ctype})"
        return False, f"incompetência federativa: {level.value} não pode '{action}'"

    def is_valid_hierarchy(self, parent_level: FederativeLevel,
                           child_level: FederativeLevel) -> bool:
        """Validar se a hierarquia é legítima (pai pode criar filho)."""
        valid = {
            FederativeLevel.UNIAO: [FederativeLevel.ESTADO],
            FederativeLevel.ESTADO: [FederativeLevel.MUNICIPIO],
            FederativeLevel.MUNICIPIO: [FederativeLevel.DISTRITO],
            FederativeLevel.DISTRITO: [],
        }
        return child_level in valid.get(parent_level, [])

    # ── Territórios ────────────────────────────────────────────

    def get_territory(self, level: FederativeLevel,
                      instance_name: str = "") -> list[str]:
        """Retornar território (write zones) de um nível."""
        zones = self.TERRITORIES.get(level, [])
        if instance_name:
            zones = [z.replace("{instance_name}", instance_name) for z in zones]
        return zones

    def is_in_territory(self, path: str, level: FederativeLevel,
                        instance_name: str = "") -> bool:
        """Verificar se path está dentro do território do ente."""
        zones = self.get_territory(level, instance_name)
        return any(Path(path).is_relative_to(z.replace("/*", "")) if hasattr(Path, "is_relative_to") else
                   str(path).startswith(z.replace("/**", "").replace("/*", ""))
                   for z in zones if z not in ["*"])

    # ── Relações Inter-Federativas ─────────────────────────────

    def inter_federative_pact(self, level_a: FederativeLevel,
                               level_b: FederativeLevel) -> dict[str, Any]:
        """
        Definir relação entre dois entes federativos.
        Retorna protocolo de interação.
        """
        if level_a == level_b:
            return {"relation": "horizontal", "protocol": "peer_review",
                    "can_share_data": True, "can_override": False}

        levels = [FederativeLevel.UNIAO, FederativeLevel.ESTADO,
                  FederativeLevel.MUNICIPIO, FederativeLevel.DISTRITO]
        idx_a = levels.index(level_a)
        idx_b = levels.index(level_b)

        if idx_a < idx_b:  # A é superior a B
            return {
                "relation": "vertical_downstream",
                "superior": level_a.value,
                "inferior": level_b.value,
                "can_spawn": self.is_valid_hierarchy(level_a, level_b),
                "can_review": True,        # superior revisa inferior
                "can_override": True,       # superior pode sobrepor
                "can_share_keys": False,    # chaves NUNCA fluem downstream
                "pact": "CF/88 Art. 23 (competências comuns)",
            }
        else:  # B é superior a A
            return {
                "relation": "vertical_upstream",
                "inferior": level_a.value,
                "superior": level_b.value,
                "can_propose": True,        # inferior pode propor
                "can_appeal": True,         # inferior pode recorrer
                "must_report": True,        # inferior deve reportar
                "pact": "CF/88 Art. 34 (intervenção federal)",
            }

    # ── Receita (Budget Sharing) ───────────────────────────────

    def budget_share(self, level: FederativeLevel) -> dict[str, float]:
        """
        Distribuição de recursos (token budget) por nível federativo.
        Similar ao FPE/FPM brasileiro.
        """
        shares = {
            FederativeLevel.UNIAO: {"total_budget": 1.0, "share": 0.40,
                                     "explanation": "União retém 40% (defesa, exterior, moeda)"},
            FederativeLevel.ESTADO: {"total_budget": 0.6, "share": 0.35,
                                      "explanation": "Estados recebem 35% do restante"},
            FederativeLevel.MUNICIPIO: {"total_budget": 0.25, "share": 0.20,
                                         "explanation": "Municípios recebem 20%"},
            FederativeLevel.DISTRITO: {"total_budget": 0.05, "share": 0.05,
                                        "explanation": "Distritos recebem 5%"},
        }
        return shares.get(level, {"share": 0.0})


# Singleton
_pact_instance: FederativePact | None = None


def get_federative_pact() -> FederativePact:
    global _pact_instance
    if _pact_instance is None:
        _pact_instance = FederativePact()
    return _pact_instance
