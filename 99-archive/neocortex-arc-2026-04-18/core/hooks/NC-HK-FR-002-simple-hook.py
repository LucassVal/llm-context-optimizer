import time
import statistics
from typing import Any, Dict, Optional, List
from datetime import datetime, date
from collections import defaultdict
import json
import os


class Hook:
    def before_tool_call(
        self, tool_name: str, args: Dict[str, Any], kwargs: Dict[str, Any]
    ) -> None:
        pass

    def after_tool_call(
        self, tool_name: str, result: Any, error: Optional[Exception]
    ) -> None:
        pass

    def on_error(self, error: Exception, context: Dict[str, Any]) -> None:
        pass

    def session_start(self, session_id: str, metadata: Dict[str, Any]) -> None:
        pass

    def session_end(self, session_id: str, metadata: Dict[str, Any]) -> None:
        pass

    def on_checkpoint(self, checkpoint_id: str, data: Dict[str, Any]) -> None:
        pass


class LoggingHook(Hook):
    def __init__(self, level: str = "INFO"):
        self.level = level

    def _log(self, message: str):
        timestamp = datetime.now().isoformat()
        print(f"[{self.level}][{timestamp}] {message}")

    def before_tool_call(
        self, tool_name: str, args: Dict[str, Any], kwargs: Dict[str, Any]
    ) -> None:
        self._log(f"Before tool call: {tool_name}, args={args}, kwargs={kwargs}")

    def after_tool_call(
        self, tool_name: str, result: Any, error: Optional[Exception]
    ) -> None:
        if error:
            self._log(f"After tool call: {tool_name}, error={error}")
        else:
            self._log(f"After tool call: {tool_name}, result={result}")

    def on_error(self, error: Exception, context: Dict[str, Any]) -> None:
        self._log(f"Error: {error}, context={context}")

    def session_start(self, session_id: str, metadata: Dict[str, Any]) -> None:
        self._log(f"Session start: {session_id}, metadata={metadata}")

    def session_end(self, session_id: str, metadata: Dict[str, Any]) -> None:
        self._log(f"Session end: {session_id}, metadata={metadata}")

    def on_checkpoint(self, checkpoint_id: str, data: Dict[str, Any]) -> None:
        self._log(f"Checkpoint: {checkpoint_id}, data={data}")


class TimingHook(Hook):
    def __init__(self, max_history: int = 1000):
        self._start_times = {}
        self._history = defaultdict(list)
        self.max_history = max_history

    def before_tool_call(
        self, tool_name: str, args: Dict[str, Any], kwargs: Dict[str, Any]
    ) -> None:
        self._start_times[tool_name] = time.time()

    def after_tool_call(
        self, tool_name: str, result: Any, error: Optional[Exception]
    ) -> None:
        start = self._start_times.get(tool_name)
        if start:
            elapsed = time.time() - start
            history = self._history[tool_name]
            history.append(elapsed)
            if len(history) > self.max_history:
                history.pop(0)

            if len(history) >= 5:
                sorted_times = sorted(history)
                p50 = sorted_times[int(len(sorted_times) * 0.5)]
                p95 = sorted_times[int(len(sorted_times) * 0.95)]
                p99 = sorted_times[int(len(sorted_times) * 0.99)]
                print(
                    f"[TIMING] {tool_name}: current={elapsed:.3f}s, "
                    f"p50={p50:.3f}s, p95={p95:.3f}s, p99={p99:.3f}s, "
                    f"n={len(history)}"
                )
            else:
                print(f"[TIMING] {tool_name}: {elapsed:.3f}s (n={len(history)})")
            del self._start_times[tool_name]

    def get_stats(self, tool_name: str) -> Dict[str, float]:
        history = self._history.get(tool_name, [])
        if not history:
            return {}
        sorted_times = sorted(history)
        return {
            "count": len(history),
            "mean": statistics.mean(history) if len(history) >= 1 else 0,
            "median": statistics.median(history) if len(history) >= 1 else 0,
            "p50": sorted_times[int(len(sorted_times) * 0.5)]
            if len(sorted_times) >= 1
            else 0,
            "p95": sorted_times[int(len(sorted_times) * 0.95)]
            if len(sorted_times) >= 1
            else 0,
            "p99": sorted_times[int(len(sorted_times) * 0.99)]
            if len(sorted_times) >= 1
            else 0,
            "min": min(history) if history else 0,
            "max": max(history) if history else 0,
        }


class RateLimitHook(Hook):
    def __init__(self, max_calls_per_minute: int = 60, window_seconds: int = 60):
        self.max_calls = max_calls_per_minute
        self.window = window_seconds
        self.calls = []

    def before_tool_call(
        self, tool_name: str, args: Dict[str, Any], kwargs: Dict[str, Any]
    ) -> None:
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.window]
        if len(self.calls) >= self.max_calls:
            raise Exception(
                f"Rate limit exceeded: {self.max_calls} calls per {self.window} seconds"
            )
        self.calls.append(now)

    def get_usage(self) -> Dict[str, Any]:
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.window]
        return {
            "calls_in_window": len(self.calls),
            "max_calls": self.max_calls,
            "window_seconds": self.window,
            "remaining": max(0, self.max_calls - len(self.calls)),
        }


class AuditHook(Hook):
    def __init__(self, audit_dir: str = "audit_logs"):
        self.audit_dir = audit_dir
        os.makedirs(audit_dir, exist_ok=True)
        self._yaml_available = self._check_yaml()

    def _check_yaml(self) -> bool:
        try:
            import yaml

            return True
        except ImportError:
            return False

    def _get_daily_file(self) -> str:
        today = date.today().isoformat()
        filename = f"audit_{today}.{'yaml' if self._yaml_available else 'json'}"
        return os.path.join(self.audit_dir, filename)

    def _write_entry(self, event: str, data: Dict[str, Any]):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data,
        }
        filename = self._get_daily_file()

        if self._yaml_available:
            import yaml

            with open(filename, "a", encoding="utf-8") as f:
                yaml.dump([entry], f, default_flow_style=False, allow_unicode=True)
                f.write("\n---\n")
        else:
            with open(filename, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def before_tool_call(
        self, tool_name: str, args: Dict[str, Any], kwargs: Dict[str, Any]
    ) -> None:
        self._write_entry(
            "before_tool_call",
            {
                "tool": tool_name,
                "args": args,
                "kwargs": kwargs,
            },
        )

    def after_tool_call(
        self, tool_name: str, result: Any, error: Optional[Exception]
    ) -> None:
        self._write_entry(
            "after_tool_call",
            {
                "tool": tool_name,
                "result": str(result)[:500],
                "error": str(error) if error else None,
                "success": error is None,
            },
        )

    def on_error(self, error: Exception, context: Dict[str, Any]) -> None:
        self._write_entry(
            "on_error",
            {
                "error": str(error),
                "error_type": error.__class__.__name__,
                "context": context,
            },
        )

    def session_start(self, session_id: str, metadata: Dict[str, Any]) -> None:
        self._write_entry(
            "session_start",
            {
                "session_id": session_id,
                "metadata": metadata,
            },
        )

    def session_end(self, session_id: str, metadata: Dict[str, Any]) -> None:
        self._write_entry(
            "session_end",
            {
                "session_id": session_id,
                "metadata": metadata,
            },
        )

    def on_checkpoint(self, checkpoint_id: str, data: Dict[str, Any]) -> None:
        self._write_entry(
            "on_checkpoint",
            {
                "checkpoint_id": checkpoint_id,
                "data": data,
            },
        )

    def list_audit_files(self) -> List[str]:
        files = []
        for f in os.listdir(self.audit_dir):
            if f.startswith("audit_") and (f.endswith(".yaml") or f.endswith(".json")):
                files.append(os.path.join(self.audit_dir, f))
        return sorted(files)
