# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3



import io
import sys

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
_genealogy:
  injected_at: '2026-04-16T11:30:00.000000'
  injected_by: NC-SCR-FR-098-health-wrapper.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-098-health-wrapper
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-098-health-wrapper.py
FR-098 — Health wrapper: expõe endpoints /health e /ready via HTTP sem tocar server.py @LOCK.

Carrega NC-SVC-FR-002-health-service.py via importlib.util (R09).
Sobe um HTTPServer leve em thread separada na porta 8766 (não 8765 — evitar conflito).
GET /health → retorna JSON com status, uptime, timestamp ISO.
GET /ready → retorna 200 se MCP stdio está respondendo, 503 caso contrário.
Registra startup via NC-SVC-FR-016-wal-service.py (WAL log).

Uso:
  python NC-SCR-FR-098-health-wrapper.py --port 8766
"""

import argparse
import importlib.util
import json
import logging
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# ------------------------------------------------------------------
# Import HealthService via importlib.util (R09)
# ------------------------------------------------------------------


def load_health_service():
    """Load NC-SVC-FR-002-health-service.py via importlib."""
    base_path = Path(__file__).resolve().parent.parent
    health_path = (
        base_path
        / "neocortex"
        / "core"
        / "services"
        / "NC-SVC-FR-002-health-service.py"
    )
    if not health_path.exists():
        raise FileNotFoundError(f"Health service not found at {health_path}")
    spec = importlib.util.spec_from_file_location("health_service", health_path)
    if spec is None:
        raise ImportError(f"Failed to create spec for {health_path}")
    if spec.loader is None:
        raise ImportError(f"Spec loader is None for {health_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------------------
# Import WALService via importlib.util
# ------------------------------------------------------------------


def load_wal_service():
    """Load NC-SVC-FR-016-wal-service.py via importlib."""
    base_path = Path(__file__).resolve().parent.parent
    wal_path = (
        base_path / "neocortex" / "core" / "services" / "NC-SVC-FR-016-wal-service.py"
    )
    if not wal_path.exists():
        logger.warning(
            f"WAL service not found at {wal_path}, continuing without WAL logging"
        )
        return None
    spec = importlib.util.spec_from_file_location("wal_service", wal_path)
    if spec is None:
        logger.warning(
            f"Failed to create spec for {wal_path}, continuing without WAL logging"
        )
        return None
    if spec.loader is None:
        logger.warning(
            f"Spec loader is None for {wal_path}, continuing without WAL logging"
        )
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.WALService


# ------------------------------------------------------------------
# HTTP request handler
# ------------------------------------------------------------------


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for /health and /ready endpoints."""

    def __init__(self, health_module, wal_service, *args, **kwargs):
        self.health_module = health_module
        self.wal_service = wal_service
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == "/health":
            self.handle_health()
        elif self.path == "/ready":
            self.handle_ready()
        else:
            self.send_error(404, "Not Found")

    def handle_health(self):
        """Return health status JSON."""
        try:
            health_data = self.health_module.get_health_status()
            response = self.health_module.format_health_response(
                status="healthy", details=health_data, include_timestamp=True
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode("utf-8"))
        except Exception as e:
            logger.error(f"Error generating health response: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "Internal server error"}, indent=2).encode("utf-8")
            )

    def handle_ready(self):
        """Check MCP server alive on port 8765 (SSE endpoint)."""
        try:
            # First try SSE endpoint check (more accurate for MCP SSE mode)
            sse_alive = False
            socket_alive = False
            check_method = "unknown"

            # Check if check_mcp_sse_alive function exists
            if hasattr(self.health_module, "check_mcp_sse_alive"):
                sse_alive = self.health_module.check_mcp_sse_alive(
                    port=8765, host="127.0.0.1", timeout=2
                )
                check_method = "sse"
                alive = sse_alive
            else:
                # Fallback to socket check
                socket_alive = self.health_module.check_mcp_alive(
                    port=8765, host="127.0.0.1", timeout=2
                )
                check_method = "socket"
                alive = socket_alive

            if alive:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "status": "ready",
                            "mcp_alive": True,
                            "check_method": check_method,
                            "mcp_sse_alive": sse_alive
                            if check_method == "sse"
                            else None,
                            "mcp_socket_alive": socket_alive
                            if check_method == "socket"
                            else None,
                        },
                        indent=2,
                    ).encode("utf-8")
                )
            else:
                self.send_response(503)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "status": "not ready",
                            "mcp_alive": False,
                            "check_method": check_method,
                            "mcp_sse_alive": sse_alive
                            if check_method == "sse"
                            else None,
                            "mcp_socket_alive": socket_alive
                            if check_method == "socket"
                            else None,
                        },
                        indent=2,
                    ).encode("utf-8")
                )
        except Exception as e:
            logger.error(f"Error checking MCP alive: {e}")
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {"error": "MCP check failed", "details": str(e)}, indent=2
                ).encode("utf-8")
            )

    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")


# ------------------------------------------------------------------
# WAL logging helper
# ------------------------------------------------------------------


def log_wal_startup(wal_service, port):
    """Log health wrapper startup to WAL."""
    if wal_service is None:
        logger.warning("WAL service not available, skipping startup log")
        return
    try:
        session_id = f"health-wrapper-{int(time.time())}"
        wal_service.open_session(session_id, "health-wrapper", ticket_id="NC-DS-098")
        wal_service.log_operation(
            session_id=session_id,
            operation="HEALTH_WRAPPER_START",
            file_path=f"http://localhost:{port}/health",
            ticket_id="NC-DS-098",
            before_hash=None,
            after_hash=None,
        )
        wal_service.commit_session(session_id)
        logger.info(f"Logged health wrapper startup to WAL session {session_id}")
    except Exception as e:
        logger.error(f"Failed to log startup to WAL: {e}")


# ------------------------------------------------------------------
# Main server thread
# ------------------------------------------------------------------


def run_server(port, health_module, wal_service):
    """Start HTTP server in a separate thread."""

    def handler(*args, **kwargs):
        return HealthHandler(health_module, wal_service, *args, **kwargs)

    server = HTTPServer(("localhost", port), handler)
    logger.info(f"Health wrapper started on http://localhost:{port}")
    log_wal_startup(wal_service, port)
    server.serve_forever()


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Health wrapper for NeoCortex")
    parser.add_argument(
        "--port", type=int, default=8766, help="Port to listen on (default: 8766)"
    )
    args = parser.parse_args()

    try:
        health_module = load_health_service()
        logger.info("Health service loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load health service: {e}")
        sys.exit(1)

    wal_service = None
    try:
        WALService = load_wal_service()
        if WALService:
            wal_service = WALService()
            logger.info("WAL service loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to load WAL service: {e}")

    # Start server in daemon thread
    server_thread = threading.Thread(
        target=run_server, args=(args.port, health_module, wal_service), daemon=True
    )
    server_thread.start()
    logger.info("Health wrapper thread started. Use Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down health wrapper")
        sys.exit(0)


if __name__ == "__main__":
    main()
