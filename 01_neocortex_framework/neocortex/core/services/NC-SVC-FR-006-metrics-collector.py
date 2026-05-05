"""---
@Module NC-SVC-FR-006-metrics-collector mcp _genealogy:   injected_at: '2026-04-16T00:23:58.74
---
"""


"""
NC-SVC-FR-006-metrics-collector.py
FR-006  MetricsCollector: Coleta de mtricas de execuo do NeoCortex.
"""

import importlib.util
import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Token usage record."""

    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class ToolMetric:
    """Mtrica de uma execuo de tool MCP."""

    tool_name: str
    action: str
    duration_ms: float
    success: bool
    tokens_used: int = 0
    error_msg: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """Coletora de mtricas de tools MCP, tokens, latncia e erros.

    Interface usada por NC-SVC-FR-009-session-buddy.py:
      - record_tool_call(tool_name, action, duration_ms, success, tokens, error)
      - get_session_metrics() -> Dict
      - get_tool_stats(tool_name) -> Dict
      - reset() -> None
    """

    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._lock = threading.Lock()
        self._session_token_usage: list[TokenUsage] = []
        self._tool_metrics: deque[ToolMetric] = deque(maxlen=1000)
        self._session_start_time = time.time()

        self._initialized = True

    @property
    def _event_bus(self):
        if not hasattr(self, "_event_bus_instance"):
            spec = importlib.util.spec_from_file_location(
                "event_bus", Path(__file__).parent / "NC-SVC-FR-005-event-bus.py"
            )
            if spec is None:
                raise ImportError("Failed to load event bus module")
            module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(module)
            self._event_bus_module = module
            self._event_bus_instance = module.get_event_bus()
        return self._event_bus_instance

    @property
    def _neocortex_event_class(self):
        _ = self._event_bus  # ensure module loaded
        return self._event_bus_module.NeoCortexEvent

    def record_token_usage(
        self, model: str, input_tokens: int, output_tokens: int, cost_usd: float
    ) -> None:
        """Record token usage for a model."""
        usage = TokenUsage(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            timestamp=time.time(),
        )
        with self._lock:
            self._session_token_usage.append(usage)

    def record_tool_call(self, *args, **kwargs) -> None:
        """Registra execuo de uma tool.

        Suporta duas assinaturas:
        1. (tool_name, duration_ms, success)  # compatibilidade com NC-DS-022 anterior
        2. (tool_name, action, duration_ms, success, tokens_used=0, error_msg=None)
        """
        # Parse arguments
        if len(args) == 3 and not kwargs:
            # Assinatura antiga: tool_name, duration_ms, success
            tool_name = args[0]
            action = ""
            duration_ms = args[1]
            success = args[2]
            tokens_used = 0
            error_msg = None
        else:
            # Assinatura nova com argumentos nomeados ou posicionais
            # Usar kwargs e preencher padres
            tool_name = kwargs.get("tool_name", args[0] if len(args) > 0 else None)
            action = kwargs.get("action", args[1] if len(args) > 1 else "")
            duration_ms = kwargs.get("duration_ms", args[2] if len(args) > 2 else 0.0)
            success = kwargs.get("success", args[3] if len(args) > 3 else True)
            tokens_used = kwargs.get("tokens_used", args[4] if len(args) > 4 else 0)
            error_msg = kwargs.get("error_msg", args[5] if len(args) > 5 else None)

        if tool_name is None:
            raise TypeError("missing required argument 'tool_name'")

        metric = ToolMetric(
            tool_name=tool_name,
            action=action,
            duration_ms=duration_ms,
            success=success,
            tokens_used=tokens_used,
            error_msg=error_msg,
            timestamp=datetime.now(),
        )
        with self._lock:
            self._tool_metrics.append(metric)

        if error_msg is not None:
            self._publish_error_event(metric)

    def _publish_error_event(self, metric: ToolMetric) -> None:
        """Publish error event to EventBus."""
        try:
            event = self._neocortex_event_class(
                event_type="TOOL_ERROR",
                payload={
                    "tool_name": metric.tool_name,
                    "action": metric.action,
                    "error_msg": metric.error_msg,
                    "timestamp": metric.timestamp.isoformat(),
                },
                timestamp=datetime.now(),
                source_tool="metrics_collector",
            )
            self._event_bus.publish(event)
        except Exception:
            logger.warning("Failed to publish error event", exc_info=True)

    def get_session_metrics(self) -> dict[str, Any]:
        """Retorna mtricas agregadas da sesso atual."""
        with self._lock:
            tool_metrics = list(self._tool_metrics)
            token_usages = list(self._session_token_usage)

        total_calls = len(tool_metrics)
        success_calls = sum(1 for m in tool_metrics if m.success)
        success_rate = success_calls / total_calls if total_calls > 0 else 0.0
        total_tokens = sum(m.tokens_used for m in tool_metrics)
        avg_duration = (
            sum(m.duration_ms for m in tool_metrics) / total_calls
            if total_calls > 0
            else 0.0
        )
        error_count = sum(1 for m in tool_metrics if m.error_msg is not None)
        tools_used = list({m.tool_name for m in tool_metrics})

        total_token_usage = sum(u.input_tokens + u.output_tokens for u in token_usages)
        total_cost = sum(u.cost_usd for u in token_usages)

        return {
            "total_calls": total_calls,
            "success_rate": success_rate,
            "total_tokens": total_tokens,
            "total_token_usage": total_token_usage,
            "total_cost_usd": total_cost,
            "avg_duration_ms": avg_duration,
            "error_count": error_count,
            "tools_used": tools_used,
            "session_duration_sec": time.time() - self._session_start_time,
        }

    def get_session_summary(self) -> dict[str, Any]:
        """
        Get summary of current session metrics.
        Compatible with NC-SVC-FR-009-session-buddy.py.
        """
        metrics = self.get_session_metrics()
        return {
            "total_tokens": metrics["total_token_usage"],
            "total_input_tokens": sum(
                u.input_tokens for u in self._session_token_usage
            ),
            "total_output_tokens": sum(
                u.output_tokens for u in self._session_token_usage
            ),
            "total_cost_usd": metrics["total_cost_usd"],
            "tool_calls": metrics["total_calls"],
            "avg_duration_ms": metrics["avg_duration_ms"],
            "session_duration_sec": metrics["session_duration_sec"],
            "timestamp": datetime.now().isoformat(),
        }

    def get_tool_stats(self, tool_name: str) -> dict[str, Any]:
        """Retorna estatsticas por tool."""
        with self._lock:
            tool_metrics = [m for m in self._tool_metrics if m.tool_name == tool_name]

        if not tool_metrics:
            return {
                "call_count": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "total_tokens": 0,
            }

        call_count = len(tool_metrics)
        success_count = sum(1 for m in tool_metrics if m.success)
        success_rate = success_count / call_count
        avg_duration = sum(m.duration_ms for m in tool_metrics) / call_count
        total_tokens = sum(m.tokens_used for m in tool_metrics)

        return {
            "call_count": call_count,
            "success_rate": success_rate,
            "avg_duration_ms": avg_duration,
            "total_tokens": total_tokens,
        }

    def get_recent_errors(self, limit: int = 10) -> list[ToolMetric]:
        """Retorna ltimos N erros registrados."""
        with self._lock:
            errors = [m for m in self._tool_metrics if m.error_msg is not None]
            return list(reversed(errors))[:limit]

    def reset(self) -> None:
        """Reseta mtricas da sesso."""
        with self._lock:
            self._session_token_usage.clear()
            self._tool_metrics.clear()
            self._session_start_time = time.time()

    def reset_session(self) -> None:
        """Reset current session metrics. Alias for reset()."""
        self.reset()

    # Compatibility methods (no disk persistence)
    def get_daily_report(self, target_date=None) -> dict[str, Any]:
        """Stub for daily report (no disk persistence)."""
        return {
            "date": datetime.now().date().isoformat()
            if target_date is None
            else target_date,
            "sessions": 0,
            "top_tools": [],
            "cost_breakdown": {},
            "total_tokens": 0,
            "total_cost_usd": 0.0,
        }

    def export_session(self, file_path=None):
        """Stub for export (no disk persistence)."""
        raise NotImplementedError("Disk persistence is disabled")


def get_metrics_collector() -> MetricsCollector:
    """Singleton do MetricsCollector."""
    return MetricsCollector()
