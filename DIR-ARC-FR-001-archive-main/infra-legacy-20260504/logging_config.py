"""---
@Module  mcp domain: "core" layer: "core" type: "file" tags: ["
---
"""


"""
logging_config.py  NeoCortex Logging Configuration
Centralizes logging setup for the entire NeoCortex framework.
Import this module at startup to configure structured logging.
"""
import logging
import logging.handlers
import sys
from pathlib import Path

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s  %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def configure_logging(
    level: str = "INFO",
    log_file: Path | None = None,
    max_bytes: int = 10_485_760,   # 10MB
    backup_count: int = 7,
    stderr_output: bool = True,
) -> None:
    """
    Configure framework-wide logging.

    Args:
        level:         Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file:      Optional path to rotating log file
        max_bytes:     Max size per log file before rotation
        backup_count:  Number of backup files to keep (TTL-002: 7 days default)
        stderr_output: If True, also write to stderr (MCP stdio-safe)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger   = logging.getLogger()
    root_logger.setLevel(numeric_level)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Stderr handler  MCP stdio protocol requires stdout clean
    if stderr_output:
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(formatter)
        root_logger.addHandler(stderr_handler)

    # Rotating file handler
    if log_file is not None:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger. Use module __name__ as convention.

    Usage:
        logger = get_logger(__name__)
        logger.info("MCP server started")
    """
    return logging.getLogger(name)


def suppress_noisy_loggers() -> None:
    """Suppress overly verbose third-party loggers."""
    for lib in ("websockets", "asyncio", "urllib3", "httpx"):
        logging.getLogger(lib).setLevel(logging.WARNING)


if __name__ == "__main__":
    configure_logging(level="DEBUG")
    logger = get_logger(__name__)
    logger.debug("logging_config self-test: DEBUG")
    logger.info("logging_config self-test: INFO")
    logger.warning("logging_config self-test: WARNING")
    print("logging_config.py: OK")
