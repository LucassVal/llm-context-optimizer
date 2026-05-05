"""---
@Module NC-HK-FR-002-simple-hook mcp _genealogy:   injected_at: '2026-04-16T00:24:02.15
---
"""


from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:02.153226'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-HK-FR-002-simple-hook.py
Hooks pr-fabricados plug-and-play para o HookRegistry.

Hooks disponveis:
  LoggingHook    log estruturado de toda tool_call
  TimingHook     mede latncia de toda tool_call
  RateLimitHook  bloqueia agente se exceder N calls/min
  AuditHook      escreve linha em audit YAML por chamada

Uso:
  from neocortex.core.hooks import HookRegistry, HOOK_BEFORE_TOOL_CALL, HOOK_AFTER_TOOL_CALL
  from neocortex.core.hooks.NC-HK-FR-002-simple-hook import LoggingHook, TimingHook

  registry = HookRegistry()
  lh = LoggingHook()
  registry.register(HOOK_BEFORE_TOOL_CALL, lh.on_before)
  registry.register(HOOK_AFTER_TOOL_CALL,  lh.on_after)
"""

import logging
import threading
import time
from collections import defaultdict, deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# LoggingHook  log estruturado de chamadas de tool
# ---------------------------------------------------------------------------

class LoggingHook:
    """Loga cada tool_call antes e depois da execucao."""

    def on_before(self, tool_name: str | dict | None = None, args: dict | None = None, **kwargs) -> None:
        if isinstance(tool_name, dict):
            tool_name = tool_name.get("tool_name", "unknown")
        logger.info("[HOOK] before_tool_call | tool=%s", tool_name)

    def on_after(self, tool_name: str | dict | None = None, result=None, elapsed_ms: float = 0.0, **kwargs) -> None:
        if isinstance(tool_name, dict):
            tool_name = tool_name.get("tool_name", "unknown")
        logger.info("[HOOK] after_tool_call  | tool=%s | elapsed=%.1fms", tool_name, elapsed_ms)

    def on_error(self, tool_name: str | dict | None = None, error=None, **kwargs) -> None:
        if isinstance(tool_name, dict):
            tool_name = tool_name.get("tool_name", "unknown")
        logger.error("[HOOK] on_error | tool=%s | error=%s", tool_name, error)


# ---------------------------------------------------------------------------
# TimingHook  mede latncia de cada tool_call
# ---------------------------------------------------------------------------

class TimingHook:
    """Armazena latencias por tool para analise de performance."""

    def __init__(self) -> None:
        self._start: dict[str, float] = {}
        self._latencies: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _extract_tool_name(self, context_or_tool) -> str:
        if isinstance(context_or_tool, dict):
            return context_or_tool.get("tool_name", "unknown")
        return str(context_or_tool) if context_or_tool else "unknown"

    def on_before(self, tool_name: str | dict | None = None, **kwargs) -> None:
        name = self._extract_tool_name(tool_name)
        with self._lock:
            self._start[name] = time.monotonic()

    def on_after(self, tool_name: str | dict | None = None, **kwargs) -> None:
        name = self._extract_tool_name(tool_name)
        with self._lock:
            start = self._start.pop(name, None)
            if start is not None:
                elapsed_ms = (time.monotonic() - start) * 1000
                self._latencies[name].append(elapsed_ms)
                logger.debug("[TIMING] %s %.1fms", name, elapsed_ms)

    def get_stats(self, tool_name: str) -> dict:
        """Retorna p50/p95/avg para a tool informada."""
        lats = sorted(self._latencies.get(tool_name, []))
        if not lats:
            return {"count": 0}
        count = len(lats)
        avg = sum(lats) / count
        p50 = lats[count // 2]
        p95 = lats[int(count * 0.95)]
        return {"count": count, "avg_ms": round(avg, 1), "p50_ms": round(p50, 1), "p95_ms": round(p95, 1)}


# ---------------------------------------------------------------------------
# RateLimitHook  bloqueia agente se exceder N calls/min
# ---------------------------------------------------------------------------

class RateLimitHook:
    """Levanta RuntimeError se a tool for chamada mais de max_calls vezes por minuto."""

    def __init__(self, max_calls: int = 60, window_sec: int = 60) -> None:
        self._max = max_calls
        self._window = window_sec
        self._history: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def on_before(self, tool_name: str, **kwargs: Any) -> None:
        now = time.monotonic()
        with self._lock:
            q = self._history[tool_name]
            # Remove timestamps fora da janela
            while q and now - q[0] > self._window:
                q.popleft()
            if len(q) >= self._max:
                raise RuntimeError(
                    f"[RATE_LIMIT] tool '{tool_name}' excedeu {self._max} calls/{self._window}s"
                )
            q.append(now)


# ---------------------------------------------------------------------------
# AuditHook  grava linha YAML em audit-log por chamada
# ---------------------------------------------------------------------------

class AuditHook:
    """Grava entrada de auditoria em arquivo YAML no diretrio de logs."""

    def __init__(self, log_dir: str | Path | None = None) -> None:
        if log_dir is None:
            try:
                from neocortex.core.config.NC_CFG_FR_002_config import (
                    get_config,  # type: ignore
                )
                cfg = get_config()
                log_dir = Path(cfg.base_path) / ".neocortex" / "logs" / "NC-LOG-FR-001-hud-audit"
            except Exception:
                log_dir = Path(".neocortex") / "logs" / "NC-LOG-FR-001-hud-audit"
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._file = self._log_dir / f"audit-hook-{datetime.now(UTC).strftime('%Y%m%d')}.yaml"

    def on_after(self, tool_name: str, result: Any = None, **kwargs: Any) -> None:
        ts = datetime.now(UTC).isoformat()
        entry = f"- timestamp: \"{ts}\"\n  tool: \"{tool_name}\"\n  status: ok\n"
        try:
            with open(self._file, "a", encoding="utf-8") as fh:
                fh.write(entry)
        except OSError as exc:
            logger.warning("[AUDIT_HOOK] Falha ao gravar log: %s", exc)

    def on_error(self, tool_name: str, error: Exception, **kwargs: Any) -> None:
        ts = datetime.now(UTC).isoformat()
        entry = f"- timestamp: \"{ts}\"\n  tool: \"{tool_name}\"\n  status: error\n  error: \"{error}\"\n"
        try:
            with open(self._file, "a", encoding="utf-8") as fh:
                fh.write(entry)
        except OSError as exc:
            logger.warning("[AUDIT_HOOK] Falha ao gravar log: %s", exc)


__all__ = ["AuditHook", "LoggingHook", "RateLimitHook", "TimingHook"]
