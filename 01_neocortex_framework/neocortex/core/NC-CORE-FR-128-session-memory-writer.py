# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
"""---
NC-CORE-FR-128-session-memory-writer.py — SessionMemoryWriter (real, substitui stub)
---
"""


import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SessionMemoryWriter:
    """Real session memory writer — records turns and manages hot context."""

    def __init__(self, root: Path | None = None):
        import os as _os
        self.root = root or Path(_os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.hot_context_dir = self.root / ".neocortex" / "hot_context"
        self.hot_context_dir.mkdir(parents=True, exist_ok=True)
        self.session_log_dir = self.root / ".neocortex" / "sessions"
        self.session_log_dir.mkdir(parents=True, exist_ok=True)
        self.hot_context_file = self.hot_context_dir / "hot-context.md"
        self.max_hot_interactions = 5

    def record_turn(self, user_message: str, ai_response: str) -> dict[str, Any]:
        """Record a conversation turn."""
        ts = datetime.now().isoformat()
        entry = {
            "timestamp": ts,
            "user": user_message[:500],
            "ai": ai_response[:500],
        }

        # Append to session log
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.session_log_dir / f"session-{today}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Update hot context
        self._update_hot_context(entry)

        return {"success": True, "recorded": ts, "log_file": str(log_file)}

    def _update_hot_context(self, entry: dict[str, Any]) -> None:
        """Maintain hot context (last N interactions)."""
        current = []
        if self.hot_context_file.exists():
            current = self.hot_context_file.read_text(encoding="utf-8").split("\n---\n")

        current.append(f"[{entry['timestamp']}] User: {entry['user'][:100]}\nAI: {entry['ai'][:100]}")

        # Keep only last N
        if len(current) > self.max_hot_interactions:
            current = current[-self.max_hot_interactions:]

        self.hot_context_file.write_text("\n---\n".join(current), encoding="utf-8")

    def get_session_stats(self) -> dict[str, Any]:
        """Get session statistics."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.session_log_dir / f"session-{today}.jsonl"
        turns = 0
        if log_file.exists():
            turns = sum(1 for _ in open(log_file, encoding="utf-8"))
        return {
            "success": True,
            "date": today,
            "turns_today": turns,
            "hot_context_entries": self.max_hot_interactions,
        }

    def end_session(self) -> dict[str, Any]:
        """End current session — archive hot context."""
        if self.hot_context_file.exists():
            archive_dir = self.hot_context_dir / "archive"
            archive_dir.mkdir(exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_file = archive_dir / f"hot-context-{ts}.md"
            self.hot_context_file.rename(archive_file)
            return {"success": True, "archived": str(archive_file)}
        return {"success": True, "note": "No hot context to archive"}


# Singleton
_session_writer: SessionMemoryWriter | None = None


def get_session_memory_writer(root: Path | None = None) -> SessionMemoryWriter:
    global _session_writer
    if _session_writer is None:
        _session_writer = SessionMemoryWriter(root)
    return _session_writer
