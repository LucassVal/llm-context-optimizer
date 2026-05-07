# @UBL @UBL @SVC-FR | LEXICO: #SYSTEM
"""
NC-SVC-FR-009-session-buddy.py
FR-009  SessionMate: Gamified session statistics with achievements.

Tracks session metrics, integrates with MetricsCollector (NC-SVC-FR-006),
persists stats to .nc/session_stats.json, and provides rich terminal display.
"""

import importlib
import json
import logging
import time
import types
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table

# Dynamic import for hyphenated module name
spec = importlib.util.spec_from_file_location(
    "metrics_collector", Path(__file__).parent / "NC-SVC-FR-006-metrics-collector.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
get_metrics_collector = module.get_metrics_collector


logger = logging.getLogger(__name__)


@dataclass
class Achievement:
    """Gamification achievement."""

    name: str
    description: str
    condition: Callable[["SessionStats"], bool] = field(repr=False)

    def is_unlocked(self, stats: "SessionStats") -> bool:
        """Check if achievement is unlocked given stats."""
        try:
            return self.condition(stats)
        except Exception as e:
            logger.warning(f"Achievement condition '{self.name}' raised {e}")
            return False


@dataclass
class SessionStats:
    """Session statistics."""

    session_id: str
    started_at: str  # ISO format
    ended_at: str | None = None
    tasks_done: int = 0
    tasks_approved: int = 0
    estimated_cost_usd: float = 0.0
    total_tokens: int = 0
    total_tool_calls: int = 0
    avg_duration_ms: float = 0.0
    achievements_unlocked: list[str] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)

    @property
    def approved_rate(self) -> float:
        """Approval rate (tasks approved / tasks done)."""
        if self.tasks_done == 0:
            return 0.0
        return self.tasks_approved / self.tasks_done

    @property
    def session_duration_sec(self) -> float:
        """Session duration in seconds."""
        if self.ended_at is None:
            return 0.0
        start = datetime.fromisoformat(self.started_at)
        end = datetime.fromisoformat(self.ended_at)
        return (end - start).total_seconds()


# Predefined achievements (5 badges)
ACHIEVEMENTS = [
    Achievement("first_task", "Primeira Task! ", lambda s: s.tasks_done >= 1),
    Achievement("speed_runner", "Speed Runner ", lambda s: s.avg_duration_ms < 300),
    Achievement(
        "budget_master", "Budget Master ", lambda s: s.estimated_cost_usd < 0.50
    ),
    Achievement("marathon", "Maratona ", lambda s: s.tasks_done >= 10),
    Achievement("quality_guard", "QA Guard ", lambda s: s.approved_rate >= 0.95),
]

# Badges/Conquistas from prompt
BADGES = {
    "first_session": {
        "name": " First Time",
        "condition": lambda s: s.tasks_done == 1,
    },
    "century": {"name": " Century", "condition": lambda s: s.total_tokens >= 100_000},
    "marathon": {
        "name": " Marathon",
        "condition": lambda s: s.session_duration_sec >= 3600,
    },
    "efficient": {
        "name": " Efficient",
        "condition": lambda s: getattr(s, "tokens_saved_ratio", 0) >= 0.5,
    },
    "streak_3": {
        "name": " Streak 3",
        "condition": lambda s: getattr(s, "consecutive_days", 0) >= 3,
    },
}


def find_nc_directory(start_path: Path | None = None) -> Path | None:
    """
    Walk up the directory hierarchy to find a `.nc` folder.

    Args:
        start_path: Starting directory (defaults to current working directory).

    Returns:
        Path to the `.nc` directory, or None if not found.
    """
    if start_path is None:
        start_path = Path.cwd()
    current = start_path.resolve()
    while current != current.parent:  # Stop at root
        nc_dir = current / ".nc"
        if nc_dir.is_dir():
            return nc_dir
        current = current.parent
    return None


class SessionMate:
    """Gamified session statistics service."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.session_id: str | None = None
        self.start_time: float | None = None
        self.stats: SessionStats | None = None
        self.nc_dir: Path | None = None
        self.metrics_collector = get_metrics_collector()
        self._console = Console()
        self._initialized = True

    def start_session(self) -> str:
        """
        Start a new session.

        Returns:
            Generated session ID.
        """
        if self.session_id is not None:
            logger.warning("Session already started, restarting")
            self.end_session()

        self.session_id = f"sess-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.start_time = time.time()
        self.nc_dir = find_nc_directory()
        if self.nc_dir is None:
            logger.warning(
                ".nc directory not found, session stats will not be persisted"
            )

        # Initialize stats
        self.stats = SessionStats(
            session_id=self.session_id,
            started_at=datetime.fromtimestamp(self.start_time).isoformat(),
        )
        logger.info(f"Session started: {self.session_id}")
        return self.session_id

    def end_session(self) -> SessionStats:
        """
        End the current session and persist stats.

        Returns:
            Final session statistics.
        """
        if self.session_id is None:
            raise RuntimeError("No active session to end")

        end_time = time.time()
        # Update stats with latest metrics
        self._refresh_stats()
        if self.stats is None:
            raise RuntimeError("Session stats not initialized")

        self.stats.ended_at = datetime.fromtimestamp(end_time).isoformat()
        # Persist to .nc/session_stats.json
        self._persist_stats()
        logger.info(
            f"Session ended: {self.session_id}, duration: {self.stats.session_duration_sec:.1f}s"
        )
        returned_stats = self.stats
        self.session_id = None
        self.start_time = None
        self.stats = None
        return returned_stats

    def record_task(self, ticket_id: str, status: str, duration_s: float) -> None:
        """
        Record a task completion.

        Args:
            ticket_id: Ticket identifier (e.g., "NC-DS-030")
            status: Task status (e.g., "completed", "approved", "failed")
            duration_s: Task duration in seconds.
        """
        if self.session_id is None:
            logger.warning("No active session, task not recorded")
            return

        if self.stats is None:
            raise RuntimeError("Session stats not initialized")

        self.stats.tasks_done += 1
        if status.lower() == "approved":
            self.stats.tasks_approved += 1

        self.stats.history.append(
            {
                "ticket_id": ticket_id,
                "status": status,
                "duration_s": duration_s,
                "timestamp": datetime.now().isoformat(),
            }
        )
        logger.debug(f"Recorded task {ticket_id} ({status})")

    def get_stats(self) -> SessionStats:
        """
        Get current session stats, updated with latest metrics.

        Returns:
            Current session statistics.
        """
        if self.session_id is None:
            raise RuntimeError("No active session")
        self._refresh_stats()
        if self.stats is None:
            raise RuntimeError("Session stats not initialized")
        return self.stats

    def check_achievements(self) -> list[Achievement]:
        """
        Check which achievements are unlocked based on current stats.

        Returns:
            List of unlocked achievements.
        """
        stats = self.get_stats()
        unlocked = []
        for ach in ACHIEVEMENTS:
            if ach.is_unlocked(stats) and ach.name not in stats.achievements_unlocked:
                unlocked.append(ach)
                stats.achievements_unlocked.append(ach.name)
                logger.info(f"Achievement unlocked: {ach.description}")
        if unlocked:
            self._persist_stats()
        return unlocked

    def display(self) -> None:
        """Display session statistics using rich."""
        stats = self.get_stats()
        console = self._console

        # Title
        console.print(
            f"\n[bold cyan]SessionMate[/bold cyan] [dim]{stats.session_id}[/dim]\n"
        )

        # Key metrics table
        table = Table(title="Session Statistics", show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Tasks Done", str(stats.tasks_done))
        table.add_row(
            "Tasks Approved",
            f"{stats.tasks_approved} ({stats.approved_rate * 100:.1f}%)",
        )
        table.add_row("Estimated Cost", f"${stats.estimated_cost_usd:.4f}")
        table.add_row("Total Tokens", f"{stats.total_tokens:,}")
        table.add_row("Tool Calls", str(stats.total_tool_calls))
        table.add_row("Avg Duration", f"{stats.avg_duration_ms:.1f} ms")
        if stats.ended_at:
            table.add_row("Session Duration", f"{stats.session_duration_sec:.1f} s")
        else:
            elapsed = time.time() - self.start_time if self.start_time else 0.0
            table.add_row("Elapsed Time", f"{elapsed:.1f} s")

        console.print(table)

        # Achievements
        unlocked = stats.achievements_unlocked
        if unlocked:
            console.print("\n[bold yellow] Achievements Unlocked[/bold yellow]")
            for name in unlocked:
                ach = next((a for a in ACHIEVEMENTS if a.name == name), None)
                if ach:
                    console.print(f"   {ach.description}")
        else:
            console.print("\n[dim]No achievements unlocked yet.[/dim]")

        # Progress bars (optional)
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            console=console,
            transient=True,
        ) as progress:
            task_progress = progress.add_task("Tasks", total=10)
            progress.update(task_progress, completed=min(stats.tasks_done, 10))
            cost_progress = progress.add_task("Cost (< $0.50)", total=0.5)
            progress.update(cost_progress, completed=min(stats.estimated_cost_usd, 0.5))

        console.print()

    def _refresh_stats(self) -> None:
        """Update stats with latest metrics from MetricsCollector."""
        if self.stats is None:
            return

        summary = self.metrics_collector.get_session_summary()
        self.stats.estimated_cost_usd = summary.get("total_cost_usd", 0.0)
        self.stats.total_tokens = summary.get("total_tokens", 0)
        self.stats.total_tool_calls = summary.get("tool_calls", 0)
        self.stats.avg_duration_ms = summary.get("avg_duration_ms", 0.0)

    def _persist_stats(self) -> None:
        """Persist session stats to .nc/session_stats.json."""
        if self.nc_dir is None or self.stats is None:
            return

        stats_file = self.nc_dir / "session_stats.json"
        try:
            if stats_file.exists():
                with open(stats_file, encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {
                    "sessions": [],
                    "achievements_unlocked": [],
                    "total_tasks_done": 0,
                    "total_cost_usd": 0.0,
                }

            # Append current session
            session_data = asdict(self.stats)
            # Remove condition field from achievements list (if any)
            session_data.pop("condition", None)
            data["sessions"].append(session_data)

            # Update aggregates
            data["total_tasks_done"] = (
                data.get("total_tasks_done", 0) + self.stats.tasks_done
            )
            data["total_cost_usd"] = (
                data.get("total_cost_usd", 0.0) + self.stats.estimated_cost_usd
            )
            # Merge achievements
            existing = set(data.get("achievements_unlocked", []))
            existing.update(self.stats.achievements_unlocked)
            data["achievements_unlocked"] = list(existing)

            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Session stats persisted to {stats_file}")
        except Exception as e:
            logger.error(f"Failed to persist session stats: {e}")

    def save_session(self, session_data: dict) -> None:
        """Persiste stats da sesso em .nc/session_stats.json (append)."""
        if self.nc_dir is None:
            return
        stats_file = self.nc_dir / "session_stats.json"
        try:
            if stats_file.exists():
                with open(stats_file, encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {
                    "sessions": [],
                    "achievements_unlocked": [],
                    "total_tasks_done": 0,
                    "total_cost_usd": 0.0,
                }
            data["sessions"].append(session_data)
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Session stats persisted to {stats_file}")
        except Exception as e:
            logger.error(f"Failed to persist session stats: {e}")

    def load_history(self, limit: int = 10) -> list[dict]:
        """Carrega ltimas N sesses do histrico."""
        if self.nc_dir is None:
            return []
        stats_file = self.nc_dir / "session_stats.json"
        if not stats_file.exists():
            return []
        try:
            with open(stats_file, encoding="utf-8") as f:
                data = json.load(f)
            sessions = data.get("sessions", [])
            return sessions[-limit:]
        except Exception as e:
            logger.error(f"Failed to load session history: {e}")
            return []

    def check_badges(self, stats: dict) -> list[str]:
        """Retorna lista de badges conquistados."""
        unlocked = []
        # Convert dict to SimpleNamespace for attribute access
        ns = types.SimpleNamespace(**stats)
        for badge_id, badge_info in BADGES.items():
            try:
                condition = badge_info["condition"]
                if condition(ns):
                    unlocked.append(badge_id)
            except Exception:
                continue
        return unlocked

    def display_summary(self, stats: dict) -> None:
        """Exibe tabela formatada com rich.Console."""
        # Usar self.display() que j usa rich
        self.display()


# Convenience function
def get_session_mate() -> SessionMate:
    """Get the singleton SessionMate instance."""
    return SessionMate()
