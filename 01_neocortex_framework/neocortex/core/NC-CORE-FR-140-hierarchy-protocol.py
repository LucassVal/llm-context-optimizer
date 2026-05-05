"""---
@Pact NC-CORE-FR-140-hierarchy-protocol mcp NC-CORE-FR-140-hierarchy-protocol.py — Protocolo d
---
"""


import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class CommunicationType(Enum):
    VERTICAL_DOWN = "vertical_down"     # Parent → Child
    VERTICAL_UP = "vertical_up"         # Child → Parent
    HORIZONTAL = "horizontal"           # Peer ↔ Peer (same level)
    DIAGONAL = "diagonal"               # Child → Other Parent


class HierarchyProtocol:
    """Protocolo de comunicação entre níveis hierárquicos."""

    def __init__(self, root: Optional[Path] = None):
        import os as _os
        self.root = root or Path(_os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.comm_log = self.root / ".neocortex" / "hierarchy" / "comm.jsonl"
        self.comm_log.parent.mkdir(parents=True, exist_ok=True)

    # ── VALIDATE: pode comunicar? ─────────────────────────────

    def can_communicate(self, source_level: str, target_level: str,
                        comm_type: CommunicationType,
                        same_parent: bool = True) -> Tuple[bool, str]:
        """
        Verificar se comunicação entre níveis é permitida.

        Regras:
        - Parent↔Parent: SEMPRE permitido (horizontal)
        - Parent→Child: SEMPRE permitido (downstream)
        - Child→Parent: SEMPRE permitido (upstream, feedback)
        - Child↔Child (same parent): permitido (horizontal intra-parent)
        - Child→OtherParent: SÓ com handoff autorizado (diagonal)
        - Child↔Child (different parents): BLOQUEADO (diagonal)
        """
        levels = ["uniao", "estado", "municipio", "distrito"]

        if source_level not in levels or target_level not in levels:
            return False, f"Nível inválido: {source_level}→{target_level}"

        src_idx = levels.index(source_level)
        tgt_idx = levels.index(target_level)

        # VERTICAL — sempre permitido
        if comm_type in (CommunicationType.VERTICAL_DOWN, CommunicationType.VERTICAL_UP):
            return True, "vertical: permitido"

        # HORIZONTAL — mesmo nível
        if comm_type == CommunicationType.HORIZONTAL:
            if src_idx == tgt_idx:
                return True, "horizontal: mesmo nível, permitido"
            return False, f"horizontal: níveis diferentes ({source_level}≠{target_level})"

        # DIAGONAL — requer autorização
        if comm_type == CommunicationType.DIAGONAL:
            if same_parent:
                return True, "diagonal: mesmo parent, permitido via handoff"
            return False, "diagonal: parents diferentes, requer autorização explícita"

        return False, f"tipo desconhecido: {comm_type}"

    # ── SEND: enviar mensagem ──────────────────────────────────

    def send(self, source_id: str, target_id: str, message: Dict[str, Any],
             source_level: str = "uniao", target_level: str = "municipio",
             comm_type: CommunicationType = CommunicationType.VERTICAL_DOWN,
             authorization: str = "") -> Dict[str, Any]:
        """
        Enviar mensagem entre níveis hierárquicos.
        Registra no WAL de comunicação.
        """
        allowed, reason = self.can_communicate(
            source_level, target_level, comm_type,
            same_parent=bool(authorization)
        )

        entry = {
            "msg_id": f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "source": source_id,
            "target": target_id,
            "source_level": source_level,
            "target_level": target_level,
            "type": comm_type.value,
            "allowed": allowed,
            "reason": reason,
            "message": message,
            "authorization": authorization[:50] if authorization else "",
            "timestamp": datetime.now().isoformat(),
        }

        # Registrar no WAL
        with open(self.comm_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        if not allowed:
            logger.warning(f"[Hierarchy] BLOCKED: {source_id}({source_level}) → {target_id}({target_level}): {reason}")
            return {"success": False, "blocked": True, "reason": reason, "entry": entry}

        logger.info(f"[Hierarchy] {source_id}→{target_id}: {comm_type.value}")
        return {"success": True, "sent": True, "entry": entry}

    # ── PARENT↔PARENT: WAL Sync ───────────────────────────────

    def parent_sync(self, parent_a: str, parent_b: str,
                    data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync entre dois parents (horizontal, mesmo nível)."""
        return self.send(parent_a, parent_b, data,
                        "estado", "estado", CommunicationType.HORIZONTAL)

    # ── CHILD↔CHILD: intra-parent ──────────────────────────────

    def child_communicate(self, child_a: str, child_b: str,
                          parent_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comunicação entre children do MESMO parent."""
        return self.send(child_a, child_b, data,
                        "municipio", "municipio", CommunicationType.HORIZONTAL,
                        authorization=parent_id)

    # ── DIAGONAL: Child → Other Parent ─────────────────────────

    def diagonal_request(self, child_id: str, target_parent: str,
                         own_parent: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Child solicita comunicação com parent de outro domínio."""
        # Requer autorização do próprio parent
        if not own_parent:
            return {"success": False, "blocked": True,
                    "reason": "diagonal requer autorização do parent de origem"}

        return self.send(child_id, target_parent, request,
                        "municipio", "estado", CommunicationType.DIAGONAL,
                        authorization=own_parent)

    # ── TERRITORY ENFORCEMENT ─────────────────────────────────

    def enforce_territory(self, level: str, path: str) -> Tuple[bool, str]:
        """
        Verificar se um path está dentro do território do nível.
        Usa as zonas definidas no Pacto Federativo.
        """
        try:
            from .NC_CORE_FR_131_federative_pact import FederativeLevel, FederativePact
            pact = FederativePact()
            level_enum = FederativeLevel(level)
            zones = pact.get_territory(level_enum)

            for zone in zones:
                if zone == "*":
                    return True, f"{level}: acesso total (*)"
                clean_zone = zone.replace("/**", "").replace("/*", "").replace("{instance_name}", "")
                if clean_zone and str(path).startswith(clean_zone):
                    return True, f"{level}: território '{zone}'"

            return False, f"{level}: path fora do território. Zonas: {zones}"
        except Exception as e:
            return True, f"territory check failed (fail-open): {e}"

    # ── QUERY: histórico de comunicação ────────────────────────

    def get_communication_log(self, source_id: str = "",
                              limit: int = 20) -> List[Dict[str, Any]]:
        """Consultar log de comunicação."""
        if not self.comm_log.exists():
            return []
        entries = []
        with open(self.comm_log, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if not source_id or source_id in (entry.get("source", ""), entry.get("target", "")):
                        entries.append(entry)
                except Exception:
                    continue
        return entries[-limit:]


# Singleton
_hierarchy_instance: Optional[HierarchyProtocol] = None


def get_hierarchy() -> HierarchyProtocol:
    global _hierarchy_instance
    if _hierarchy_instance is None:
        _hierarchy_instance = HierarchyProtocol()
    return _hierarchy_instance
