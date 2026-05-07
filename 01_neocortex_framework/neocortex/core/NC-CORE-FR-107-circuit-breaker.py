# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
#!/usr/bin/env python3
"""---
NC-CORE-FR-107-circuit-breaker.py — SEC-403
Circuit Breaker para agentes locais (Qwen 1.5b/3b).

Protege contra loops degenerativos monitorando:
  - Número de chamadas por agente em janela de tempo
  - Chamadas repetidas com mesmo payload (loop detectado)
  - Tempo total de execução de uma tarefa

Estados: CLOSED (normal) → OPEN (bloqueado) → HALF_OPEN (testando)
---"""
from __future__ import annotations

import hashlib
import logging
import time
from collections import deque
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)


class CBState(Enum):
    CLOSED    = "CLOSED"     # Normal — aceita chamadas
    OPEN      = "OPEN"       # Bloqueado — rejeita chamadas
    HALF_OPEN = "HALF_OPEN"  # Testando — aceita 1 chamada trial


class CircuitBreakerError(Exception):
    """Raised quando o circuit breaker está OPEN."""
    pass


class CircuitBreaker:
    """
    Circuit Breaker para agentes locais.

    Usage:
        cb = CircuitBreaker(agent_id="courier", max_calls=10, window_sec=60)

        @cb.guard
        def my_llm_call(prompt):
            ...

        # ou diretamente:
        cb.record_call(payload_hash)
        if cb.is_open():
            raise CircuitBreakerError("Agente em loop")
    """

    def __init__(
        self,
        agent_id: str,
        max_calls: int = 20,           # Máx chamadas na janela
        window_sec: float = 60.0,      # Janela de tempo em segundos
        max_identical: int = 5,        # Máx chamadas idênticas (loop)
        cooldown_sec: float = 120.0,   # Tempo bloqueado após OPEN
        half_open_limit: int = 2,      # Chamadas permitidas em HALF_OPEN
    ):
        self.agent_id      = agent_id
        self.max_calls     = max_calls
        self.window_sec    = window_sec
        self.max_identical = max_identical
        self.cooldown_sec  = cooldown_sec
        self.half_open_limit = half_open_limit

        self._state        = CBState.CLOSED
        self._lock         = Lock()
        self._call_times:  deque = deque()    # timestamps das chamadas
        self._payload_counts: dict[str, int] = {}  # hash → count
        self._opened_at:   float | None = None
        self._half_open_trials = 0
        self._total_blocked = 0
        self._total_calls   = 0

    # ── Estado ────────────────────────────────────────────────────────────────

    @property
    def state(self) -> CBState:
        with self._lock:
            return self._get_state()

    def _get_state(self) -> CBState:
        if self._state == CBState.OPEN:
            if self._opened_at and (time.time() - self._opened_at) >= self.cooldown_sec:
                self._state = CBState.HALF_OPEN
                self._half_open_trials = 0
                logger.info(f"[CB:{self.agent_id}] HALF_OPEN — testando recuperação")
        return self._state

    def is_open(self) -> bool:
        return self._get_state() == CBState.OPEN

    def is_closed(self) -> bool:
        return self._get_state() == CBState.CLOSED

    # ── Registro de chamadas ───────────────────────────────────────────────────

    def record_call(self, payload: str = "") -> None:
        """Registra uma chamada e verifica limites."""
        with self._lock:
            state = self._get_state()

            if state == CBState.OPEN:
                self._total_blocked += 1
                raise CircuitBreakerError(
                    f"[CB:{self.agent_id}] OPEN — bloqueado até "
                    f"{datetime.fromtimestamp(self._opened_at + self.cooldown_sec).strftime('%H:%M:%S')}"
                )

            now = time.time()
            self._total_calls += 1

            # Limpar chamadas fora da janela
            while self._call_times and (now - self._call_times[0]) > self.window_sec:
                self._call_times.popleft()

            self._call_times.append(now)

            # Verificar payload repetido (loop detection)
            if payload:
                ph = hashlib.md5(payload.encode()).hexdigest()[:8]
                self._payload_counts[ph] = self._payload_counts.get(ph, 0) + 1
                if self._payload_counts[ph] >= self.max_identical:
                    logger.warning(f"[CB:{self.agent_id}] LOOP detectado — payload repetido {self._payload_counts[ph]}x")
                    self._trip(reason=f"loop detectado ({self._payload_counts[ph]}x mesmo payload)")
                    raise CircuitBreakerError(f"[CB:{self.agent_id}] Loop detectado — circuit aberto")

            # Verificar volume de chamadas
            if len(self._call_times) >= self.max_calls:
                logger.warning(f"[CB:{self.agent_id}] Limite de chamadas atingido ({self.max_calls}/{self.window_sec}s)")
                self._trip(reason=f"{self.max_calls} chamadas em {self.window_sec}s")
                raise CircuitBreakerError(f"[CB:{self.agent_id}] Rate limit — circuit aberto")

            # HALF_OPEN: contar trials
            if state == CBState.HALF_OPEN:
                self._half_open_trials += 1
                if self._half_open_trials >= self.half_open_limit:
                    self._state = CBState.CLOSED
                    self._payload_counts.clear()
                    logger.info(f"[CB:{self.agent_id}] CLOSED — recuperado com sucesso")

    def record_success(self) -> None:
        """Chamada bem-sucedida — contribui para fechar o breaker em HALF_OPEN."""
        with self._lock:
            if self._state == CBState.HALF_OPEN:
                self._half_open_trials += 1
                if self._half_open_trials >= self.half_open_limit:
                    self._state = CBState.CLOSED
                    self._payload_counts.clear()
                    logger.info(f"[CB:{self.agent_id}] CLOSED — OK após HALF_OPEN")

    def record_failure(self, reason: str = "") -> None:
        """Registrar falha — pode abrir o breaker em HALF_OPEN."""
        with self._lock:
            if self._state == CBState.HALF_OPEN:
                self._trip(reason=f"falha em HALF_OPEN: {reason}")

    def _trip(self, reason: str = "") -> None:
        self._state     = CBState.OPEN
        self._opened_at = time.time()
        logger.error(f"[CB:{self.agent_id}] OPEN — {reason}")

    def reset(self) -> None:
        """Reset manual (T0 only)."""
        with self._lock:
            self._state     = CBState.CLOSED
            self._opened_at = None
            self._call_times.clear()
            self._payload_counts.clear()
            self._half_open_trials = 0
            logger.info(f"[CB:{self.agent_id}] Reset manual")

    # ── Decorator ─────────────────────────────────────────────────────────────

    def guard(self, fn: Callable) -> Callable:
        """Decorator para proteger uma função."""
        def wrapper(*args, **kwargs):
            payload = str(args) + str(kwargs)
            self.record_call(payload)
            try:
                result = fn(*args, **kwargs)
                self.record_success()
                return result
            except CircuitBreakerError:
                raise
            except Exception as e:
                self.record_failure(str(e))
                raise
        wrapper.__name__ = fn.__name__
        return wrapper

    # ── Status ────────────────────────────────────────────────────────────────

    def status(self) -> dict[str, Any]:
        with self._lock:
            state = self._get_state()
            remaining_cooldown = 0.0
            if state == CBState.OPEN and self._opened_at:
                remaining_cooldown = max(0.0, self.cooldown_sec - (time.time() - self._opened_at))
            return {
                "agent_id":          self.agent_id,
                "state":             state.value,
                "calls_in_window":   len(self._call_times),
                "max_calls":         self.max_calls,
                "window_sec":        self.window_sec,
                "total_calls":       self._total_calls,
                "total_blocked":     self._total_blocked,
                "cooldown_remaining": round(remaining_cooldown, 1),
                "top_repeated_payloads": sorted(
                    self._payload_counts.items(), key=lambda x: x[1], reverse=True
                )[:3],
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }


# ── Registry global ───────────────────────────────────────────────────────────

_registry: dict[str, CircuitBreaker] = {}
_registry_lock = Lock()


def get_circuit_breaker(
    agent_id: str,
    max_calls: int = 20,
    window_sec: float = 60.0,
    max_identical: int = 5,
    cooldown_sec: float = 120.0,
) -> CircuitBreaker:
    """Retorna (ou cria) o CircuitBreaker para um agente."""
    with _registry_lock:
        if agent_id not in _registry:
            _registry[agent_id] = CircuitBreaker(
                agent_id=agent_id,
                max_calls=max_calls,
                window_sec=window_sec,
                max_identical=max_identical,
                cooldown_sec=cooldown_sec,
            )
        return _registry[agent_id]


def list_breakers() -> dict[str, dict[str, Any]]:
    """Retorna status de todos os circuit breakers ativos."""
    with _registry_lock:
        return {aid: cb.status() for aid, cb in _registry.items()}


def reset_breaker(agent_id: str) -> bool:
    """Reset manual de um breaker (T0 only)."""
    with _registry_lock:
        if agent_id in _registry:
            _registry[agent_id].reset()
            return True
        return False


# Pré-criar breakers para agentes locais conhecidos
def _init_default_breakers() -> None:
    defaults = [
        {"agent_id": "courier",     "max_calls": 15, "window_sec": 60, "max_identical": 4},
        {"agent_id": "engineer",    "max_calls": 20, "window_sec": 60, "max_identical": 5},
        {"agent_id": "guardian",    "max_calls": 30, "window_sec": 60, "max_identical": 8},
        {"agent_id": "litellm_t2",  "max_calls": 25, "window_sec": 60, "max_identical": 6},
        {"agent_id": "litellm_t3",  "max_calls": 10, "window_sec": 60, "max_identical": 3},
    ]
    for d in defaults:
        get_circuit_breaker(**d)
    logger.debug(f"CircuitBreaker: {len(defaults)} agentes pré-configurados")


_init_default_breakers()
