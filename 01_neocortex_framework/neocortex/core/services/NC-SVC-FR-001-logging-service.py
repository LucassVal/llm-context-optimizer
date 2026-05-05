"""---
@Audit NC-SVC-FR-001-logging-service mcp _genealogy:   injected_at: '2026-04-16T00:23:58.56
---
"""


"""
NC-SVC-FR-001-logging-service.py
FR-001  Logging Service: Structured JSON logging wrapper for NeoCortex.

Provides centralized JSON logging with rotation, configurable log directory,
and structured event logging with context.

Restriction: server.py, sub_server.py, pulse_scheduler.py are @LOCKS.
This module is a wrapper that any module imports; locked files already use logger via __name__.
"""

import json
import logging
import logging.handlers
import time
from pathlib import Path
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formatter that outputs JSON structured logs."""

    def __init__(self):
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_entry = {
            "timestamp": time.strftime(
                "%Y-%m-%dT%H:%M:%S%z", time.localtime(record.created)
            ),
            "level": record.levelname,
            "module": record.name,
            "event": record.getMessage(),
            "context": getattr(record, "context", {}),
        }
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


class NeoCortexLogger:
    """Centralized logging service for NeoCortex."""

    _loggers = {}

    @classmethod
    def setup_json_logger(
        cls,
        name: str,
        level: int = logging.INFO,
        log_file: str | Path | None = None,
    ) -> logging.Logger:
        """
        Configure a logger with JSON formatting.

        Args:
            name: Logger name (usually __name__)
            level: Logging level (default INFO)
            log_file: Optional file path for logging. If None, logs only to stdout.

        Returns:
            Configured logger instance.
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Avoid adding handlers multiple times
        if logger.handlers:
            return logger

        # Create JSON formatter
        formatter = JSONFormatter()

        # Console handler (stdout)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler if log_file provided
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                log_path, maxBytes=10 * 1024 * 1024, backupCount=5
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create a logger with default configuration.

        Uses get_config() to determine log directory.
        """
        from neocortex.config import get_config

        cfg = get_config()
        # Determine log directory
        try:
            base_path = Path(cfg.project_root)
            log_dir = base_path / "NC-LOG-FR-001-hud-audit"
        except Exception:
            log_dir = Path("NC-LOG-FR-001-hud-audit")

        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{name.replace('.', '_')}.jsonl"

        return cls.setup_json_logger(name, logging.INFO, log_file)

    @classmethod
    def rotate_logs(
        cls, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5
    ) -> None:
        """
        Rotate log files for all registered file handlers.

        Args:
            max_bytes: Maximum size per log file before rotation
            backup_count: Number of backup files to keep
        """
        for _logger_name, logger in cls._loggers.items():
            for handler in logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    handler.maxBytes = max_bytes
                    handler.backupCount = backup_count

    @staticmethod
    def log_event(
        logger: logging.Logger,
        level: str,
        event: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """
        Log a structured event with context.

        Args:
            logger: Logger instance
            level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
            event: Event description
            context: Additional context dictionary
        """
        if context is None:
            context = {}

        # Create a log record with context attribute
        extra = {"context": context}
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(event, extra=extra)


# Convenience function
def get_neocortex_logger(name: str) -> logging.Logger:
    """Get a NeoCortex logger with default configuration."""
    return NeoCortexLogger.get_logger(name)
