"""---
@Module NC-CORE-FR-022-save-point-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.88
---
"""


#!/usr/bin/env python3
"""
NC-SVC-FR-001-save-point-service.py
SAVE-002 / SAVE-003  STEP -1 Save Point & STEP +1 Rollback

Camada 3 do Edifcio NeoCortex:
  STEP -1   capture_save_point(action, context) ANTES de qualquer write op
  STEP +1   rollback_save_point(save_id)         aps falha/exceo

Comportamento:
  - Armazena snapshot em memria (TTL 10 min, mx 50 save points)
  - Thread-safe (RLock)
  - Zero dependncia de armazenamento externo (in-process)
  - Integra com LockGuard para bloquear writes em paths protegidos
  - Singleton global via get_save_point_service()
"""

import logging
import threading
import time
import uuid
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

#  Aes classificadas como WRITE (STEP -1 obrigatrio)
WRITE_ACTIONS: frozenset = frozenset({
    # Ledger
    "create", "update", "delete", "write", "upsert",
    # Lobes
    "lobe_write", "lobe_update", "populate",
    # Agents
    "spawn", "execute", "task_execute",
    # Filesystem
    "file_write", "file_create", "file_delete", "file_move",
    # Config
    "config_set", "config_update",
    # Security
    "lock_set", "policy_update",
})

#  TTL e limites
SAVE_POINT_TTL_SECONDS = 600   # 10 minutos
SAVE_POINT_MAX_SLOTS    = 50   # mx save points em memria


class SavePoint:
    """Representa um snapshot de estado antes de uma write operation."""

    __slots__ = (
        "action",
        "agent_role",
        "context",
        "created_at",
        "expires_at",
        "save_id",
        "status"
    )

    def __init__(self, action: str, agent_role: str, context: dict[str, Any]):
        self.save_id    = str(uuid.uuid4())[:12]
        self.action     = action
        self.agent_role = agent_role
        self.context    = context          # snapshot do estado relevante
        self.created_at = time.time()
        self.expires_at = self.created_at + SAVE_POINT_TTL_SECONDS
        self.status     = "active"         # active | rolled_back | committed | expired

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "save_id":    self.save_id,
            "action":     self.action,
            "agent_role": self.agent_role,
            "status":     self.status,
            "created_at": datetime.fromtimestamp(self.created_at).isoformat(),
            "expires_at": datetime.fromtimestamp(self.expires_at).isoformat(),
            "context_keys": list(self.context.keys()),
        }


class SavePointService:
    """
    STEP -1 Save Point + STEP +1 Rollback  Camada 3 do Edifcio NeoCortex.

    Uso:
        svc = get_save_point_service()

        # Antes de qualquer write:
        save_id, allowed = svc.capture(action="lobe_write", agent_role="courier",
                                       context={"path": str(path), "content_hash": h})
        if not allowed:
            raise PermissionError(f"Write bloqueada pelo LockGuard: {action}")

        try:
            do_write_operation()
            svc.commit(save_id)
        except Exception as e:
            result = svc.rollback(save_id)
            raise
    """

    def __init__(self):
        self._lock   = threading.RLock()
        self._store: dict[str, SavePoint] = {}
        self._stats  = {"captured": 0, "committed": 0, "rolled_back": 0, "expired": 0}

        # Tentar importar LockGuard (opcional  falha silenciosa)
        try:
            from .lock_guard import get_lock_guard
            self._lock_guard = get_lock_guard()
        except Exception:
            self._lock_guard = None

    #  STEP -1: Capturar Save Point
    def capture(
        self,
        action: str,
        agent_role: str = "unknown",
        context: dict[str, Any] | None = None,
    ) -> tuple[str, bool]:
        """
        STEP -1  Chamado ANTES de qualquer write op.

        Returns:
            (save_id, allowed): se allowed=False, a write DEVE ser bloqueada.
        """
        if context is None:
            context = {}

        # 1. Verificar se a ao  uma write op
        is_write = action in WRITE_ACTIONS or any(w in action for w in ("write", "create", "delete", "update", "spawn"))

        # 2. Verificar LockGuard (path-based)
        allowed = True
        lock_reason = "ok"
        if is_write and self._lock_guard is not None:
            path = context.get("path", "")
            if path:
                allowed, lock_reason = self._lock_guard.check_write(str(path), agent_role)

        if not allowed:
            logger.warning(
                f"[SavePoint]  STEP -1 BLOCKED | action={action} | role={agent_role} "
                f"| path={context.get('path','')} | reason={lock_reason}"
            )
            return ("BLOCKED", False)

        # 3. Limpeza de expirados antes de criar novo
        self._evict_expired()

        # 4. Criar save point
        with self._lock:
            if len(self._store) >= SAVE_POINT_MAX_SLOTS:
                # Remover o mais antigo
                oldest = min(self._store.values(), key=lambda s: s.created_at)
                del self._store[oldest.save_id]
                logger.warning(f"[SavePoint] Slot overflow  removido oldest: {oldest.save_id}")

            sp = SavePoint(action=action, agent_role=agent_role, context=context)
            self._store[sp.save_id] = sp
            self._stats["captured"] += 1

        logger.info(
            f"[SavePoint]  STEP -1 CAPTURED | id={sp.save_id} | action={action} "
            f"| role={agent_role} | context_keys={list(context.keys())}"
        )
        return (sp.save_id, True)

    #  STEP +1: Rollback
    def rollback(self, save_id: str) -> dict[str, Any]:
        """
        STEP +1  Reverter ao estado do save point aps falha.

        ATENO: Esta implementao registra o rollback e retorna o contexto
        capturado para que o chamador execute a reverso real.
        A reverso real depende do tipo de objeto (arquivo, ledger entry, etc).
        """
        with self._lock:
            sp = self._store.get(save_id)

        if sp is None:
            logger.error(f"[SavePoint]  STEP +1 ROLLBACK FAILED  save_id not found: {save_id}")
            return {"success": False, "reason": "save_point_not_found", "save_id": save_id}

        if sp.is_expired:
            logger.warning(f"[SavePoint]  STEP +1 ROLLBACK  save_id expired: {save_id}")
            return {"success": False, "reason": "save_point_expired", "save_id": save_id, "context": sp.context}

        with self._lock:
            sp.status = "rolled_back"
            self._stats["rolled_back"] += 1

        logger.warning(
            f"[SavePoint]  STEP +1 ROLLED BACK | id={save_id} | action={sp.action} "
            f"| role={sp.agent_role} | context={sp.context}"
        )
        return {
            "success":    True,
            "save_id":    save_id,
            "action":     sp.action,
            "agent_role": sp.agent_role,
            "context":    sp.context,
            "rolled_back_at": datetime.now().isoformat(),
        }

    def commit(self, save_id: str) -> bool:
        """Marcar save point como committed (operao concluda com sucesso)."""
        with self._lock:
            sp = self._store.get(save_id)
            if sp:
                sp.status = "committed"
                self._stats["committed"] += 1
                logger.debug(f"[SavePoint]  COMMITTED | id={save_id}")
                return True
        return False

    def discard(self, save_id: str) -> bool:
        """Descartar save point manualmente (sem rollback necessrio)."""
        with self._lock:
            removed = self._store.pop(save_id, None)
        if removed:
            logger.info(f"[SavePoint]  DISCARDED | id={save_id}")
        return removed is not None

    def list_active(self) -> list[dict[str, Any]]:
        """Listar todos os save points ativos (no expirados)."""
        self._evict_expired()
        with self._lock:
            return [sp.to_dict() for sp in self._store.values() if sp.status == "active"]

    def get_compliance_status(self) -> dict[str, Any]:
        """Retorna status para o HUD Compliance Heartbeat."""
        self._evict_expired()
        with self._lock:
            active = sum(1 for s in self._store.values() if s.status == "active")
        return {
            "service": "SavePointService",
            "active_save_points": active,
            "stats": dict(self._stats),
            "max_slots": SAVE_POINT_MAX_SLOTS,
            "ttl_seconds": SAVE_POINT_TTL_SECONDS,
            "lock_guard_connected": self._lock_guard is not None,
        }

    def _evict_expired(self):
        """Remover save points expirados."""
        with self._lock:
            expired = [sid for sid, sp in self._store.items() if sp.is_expired]
            for sid in expired:
                self._store[sid].status = "expired"
                del self._store[sid]
                self._stats["expired"] += 1
        if expired:
            logger.debug(f"[SavePoint] Evicted {len(expired)} expired save points.")


#  Singleton
_instance: SavePointService | None = None
_instance_lock = threading.Lock()


def get_save_point_service() -> SavePointService:
    """Retorna singleton do SavePointService (thread-safe)."""
    global _instance
    if _instance is None:
        with _instance_lock:
            if _instance is None:
                _instance = SavePointService()
                logger.info("[SavePoint] SavePointService inicializado (STEP -1/-1.5/+1 ativo).")
    return _instance


#  Decorator helper
def with_save_point(action: str, context_fn=None):
    """
    Decorator  envolve qualquer funo com STEP -1 + STEP +1 automaticamente.

    Uso:
        @with_save_point("lobe_write", context_fn=lambda args: {"path": args[0]})
        def minha_write_op(path, content):
            ...
    """
    import functools

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            svc = get_save_point_service()
            ctx = context_fn(args) if context_fn else {"args": str(args)[:200]}
            role = kwargs.get("agent_role", "unknown")

            save_id, allowed = svc.capture(action=action, agent_role=role, context=ctx)
            if not allowed:
                raise PermissionError(f"[STEP -1] Write bloqueada pelo LockGuard: action={action}")

            try:
                result = fn(*args, **kwargs)
                svc.commit(save_id)
                return result
            except Exception:
                svc.rollback(save_id)
                raise

        return wrapper
    return decorator
