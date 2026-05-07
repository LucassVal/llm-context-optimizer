# @UBL @UBL @CFG-FR | LEXICO: #SYSTEM
"""
logging_config.py
Default logging configuration for NeoCortex.

Provides setup_default_logging() and convenience get_neocortex_logger().
"""

import logging
from pathlib import Path

from .services.NC_SVC_FR_001_logging_service import (
    NeoCortexLogger,
)
from .services.NC_SVC_FR_001_logging_service import (
    get_neocortex_logger as _get_logger,
)


def setup_default_logging() -> None:
    """
    Configure the root logger with JSON formatting.

    This sets up the root logger to output JSON structured logs to stdout
    and to a file in the default log directory.
    """
    from neocortex.config import get_config

    cfg = get_config()
    try:
        base_path = Path(cfg.project_root)
        log_dir = base_path / "NC-LOG-FR-001-hud-audit"
    except Exception:
        log_dir = Path("NC-LOG-FR-001-hud-audit")

    log_dir.mkdir(parents=True, exist_ok=True)
    root_log_file = log_dir / "neocortex_root.jsonl"

    # Configure root logger
    NeoCortexLogger.setup_json_logger("neocortex", logging.INFO, root_log_file)

    # Silence noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


# Re-export for convenience
get_neocortex_logger = _get_logger
