"""---
@Module NC-SVC-FR-014-dry-run-preview mcp _genealogy:   injected_at: '2026-04-16T00:23:59.00
---
"""


#!/usr/bin/env python3
"""
NC-SVC-FR-014-dry-run-preview.py
SAVE-005  Dry-Run Preview Middleware

Calcula diff antes de write operations, exibe prvia e bloqueia se risco ALTO.
Integra com LockGuard para verificar paths protegidos (@LOCKS).
"""

import difflib
import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DryRunResult:
    """Resultado da anlise de dry-run."""

    risk: str  # 'low', 'medium', 'high'
    diff_lines: int
    affected_files: list[str]
    preview: str


class DryRunPreviewService:
    """
    Middleware de Dry-Run Preview (SAVE-005).

    Uso:
        svc = get_dry_run_preview_service()
        result = svc.preview(action="file_write", target_path="/foo/bar.py",
                             content="new content", agent_role="courier")
        if svc.should_block(result):
            raise PermissionError(f"Risco ALTO detectado: {result.risk}")
    """

    def __init__(self):
        self._lock = threading.RLock()
        # Tentar importar LockGuard (opcional  falha silenciosa)
        try:
            from neocortex.core import get_lock_guard

            self._lock_guard = get_lock_guard()
        except Exception:
            logger.warning(
                "[DryRunPreview] LockGuard indisponvel  verificaes de locks desabilitadas."
            )
            self._lock_guard = None

    def preview(
        self,
        action: str,
        target_path: str,
        content: str,
        agent_role: str = "unknown",
    ) -> DryRunResult:
        """
        Calcula diff entre contedo atual e novo.

        Args:
            action: Ao que causar a modificao (ex: 'file_write', 'lobe_update')
            target_path: Caminho absoluto ou relativo ao arquivo alvo
            content: Contedo novo (string)
            agent_role: Papel do agente (para verificaes de lock)

        Returns:
            DryRunResult com risk, diff_lines, affected_files, preview.
        """
        # 1. Normalizar path
        target = Path(target_path).resolve()
        affected_files = [str(target)]

        # 2. Ler contedo atual (se existir)
        old_lines = []
        if target.exists():
            try:
                with open(target, encoding="utf-8") as f:
                    old_lines = f.read().splitlines(keepends=True)
            except Exception as e:
                logger.warning(f"[DryRunPreview] No foi possvel ler {target}: {e}")
                old_lines = []

        # 3. Calcular diff
        new_lines = content.splitlines(keepends=True)
        diff = list(
            difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=str(target) + " (atual)",
                tofile=str(target) + " (novo)",
                lineterm="\n",
            )
        )
        diff_lines = len(diff)
        preview_text = "".join(diff) if diff else " (sem alteraes)"

        # 4. Avaliar risco
        risk = self._evaluate_risk(str(target), diff_lines, agent_role)

        return DryRunResult(
            risk=risk,
            diff_lines=diff_lines,
            affected_files=affected_files,
            preview=preview_text[:2000],  # Limitar tamanho
        )

    def _evaluate_risk(self, target_path: str, diff_lines: int, agent_role: str) -> str:
        """
        Determina nvel de risco: low, medium, high.

        Critrios (conforme SAVE-005):
          - high se afeta @LOCKS (LockGuard bloqueia)
          - high se diff_lines > 500 (mudana massiva)
          - medium se diff_lines > 100
          - low caso contrrio
        """
        # Verificar locks
        if self._lock_guard is not None:
            allowed, _reason = self._lock_guard.check_write(target_path, agent_role)
            if not allowed:
                logger.info(
                    f"[DryRunPreview] Path bloqueado por LockGuard: {target_path}  risco HIGH"
                )
                return "high"

        # Verificar tamanho do diff
        if diff_lines > 500:
            logger.info(
                f"[DryRunPreview] Diff massivo ({diff_lines} linhas)  risco HIGH"
            )
            return "high"
        if diff_lines > 100:
            logger.info(
                f"[DryRunPreview] Diff grande ({diff_lines} linhas)  risco MEDIUM"
            )
            return "medium"

        return "low"

    def should_block(self, result: DryRunResult) -> bool:
        """
        Decide se a operao deve ser bloqueada.

        Bloqueia se:
          - risk == 'high' (afeta @LOCKS ou diff massivo)
          - diff_lines > 500 (redundante, mas mantido)
          - Sem fallback disponvel (ainda no implementado)
        """
        if result.risk == "high":
            logger.warning("[DryRunPreview]  Bloqueio recomendado: risco HIGH")
            return True
        # Podemos adicionar mais lgicas futuramente
        return False

    def get_compliance_status(self) -> dict[str, Any]:
        """Retorna status para o HUD Compliance Heartbeat."""
        return {
            "service": "DryRunPreviewService",
            "lock_guard_connected": self._lock_guard is not None,
        }


#  Singleton
_instance: DryRunPreviewService | None = None
_instance_lock = threading.Lock()


def get_dry_run_preview_service() -> DryRunPreviewService:
    """Retorna singleton do DryRunPreviewService (thread-safe)."""
    global _instance
    if _instance is None:
        with _instance_lock:
            if _instance is None:
                _instance = DryRunPreviewService()
                logger.info(
                    "[DryRunPreview] DryRunPreviewService inicializado (SAVE005 ativo)."
                )
    return _instance
