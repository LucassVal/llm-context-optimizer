"""---
@Service NC-SVC-FR-002-health-service mcp _genealogy:   injected_at: '2026-04-16T00:23:58.59
---
"""



"""
NC-SVC-FR-002-health-service.py
FR-002  Health Service: Health status and monitoring wrapper for NeoCortex.

Provides health status information, MCP alive checks, and formatted health responses.
Can be imported by any module; does NOT modify @LOCKED files (server.py, sub_server.py).
"""

import http.client
import logging
import os
import socket
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Start time for uptime calculation
_START_TIME = time.time()


class HealthService:
    """Health monitoring service for NeoCortex."""

    VERSION = "1.0.0"

    @staticmethod
    def get_health_status() -> dict[str, Any]:
        """
        Get comprehensive health status of NeoCortex.

        Returns:
            Dictionary with uptime, pid, version, tools_count, and other metrics.
        """
        uptime_seconds = time.time() - _START_TIME
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Count tool files
        tools_count = 0
        try:
            tools_dir = Path(__file__).parent.parent.parent / "mcp" / "tools"
            if tools_dir.exists():
                tool_files = list(tools_dir.glob("NC-TOOL-FR-*.py"))
                tools_count = len(tool_files)
        except Exception as e:
            logger.warning(f"Failed to count tools: {e}")

        return {
            "uptime": f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}",
            "uptime_seconds": int(uptime_seconds),
            "pid": os.getpid(),
            "version": HealthService.VERSION,
            "tools_count": tools_count,
            "status": "healthy",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
        }

    @staticmethod
    def check_mcp_alive(port: int, host: str = "127.0.0.1", timeout: int = 2) -> bool:
        """
        Check if MCP server is alive on given port.

        Args:
            port: Port number to check
            host: Hostname (default localhost)
            timeout: Connection timeout in seconds

        Returns:
            True if server responds to TCP connection, False otherwise.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception as e:
            logger.debug(f"Connection check failed for {host}:{port}: {e}")
            return False

    @staticmethod
    def check_mcp_sse_alive(
        port: int, host: str = "127.0.0.1", timeout: int = 2
    ) -> bool:
        """
        Check if MCP SSE endpoint is alive and responding correctly.

        Args:
            port: Port number to check
            host: Hostname (default localhost)
            timeout: Connection timeout in seconds

        Returns:
            True if SSE endpoint returns 200 with correct content-type, False otherwise.
        """
        try:
            conn = http.client.HTTPConnection(host, port, timeout=timeout)
            conn.request("GET", "/sse")
            response = conn.getresponse()
            status_ok = response.status == 200
            content_type_ok = response.getheader("Content-Type", "").startswith(
                "text/event-stream"
            )
            conn.close()
            return status_ok and content_type_ok
        except Exception as e:
            logger.debug(f"SSE endpoint check failed for {host}:{port}: {e}")
            return False

    @staticmethod
    def format_health_response(
        status: str = "healthy",
        details: dict[str, Any] | None = None,
        include_timestamp: bool = True,
    ) -> dict[str, Any]:
        """
        Format health response as JSON-compatible dictionary.

        Args:
            status: Overall status ("healthy", "degraded", "unhealthy")
            details: Additional details dictionary
            include_timestamp: Whether to include timestamp

        Returns:
            Formatted health response dict.
        """
        response = {
            "status": status,
            "service": "neocortex",
            "version": HealthService.VERSION,
        }

        if include_timestamp:
            response["timestamp"] = time.strftime(
                "%Y-%m-%dT%H:%M:%S%z", time.localtime()
            )

        if details:
            response["details"] = details

        return response

    @staticmethod
    def get_system_info() -> dict[str, Any]:
        """
        Get basic system information.

        Returns:
            Dictionary with system info.
        """
        import platform

        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "current_user": os.getlogin() if hasattr(os, "getlogin") else "unknown",
        }


# Convenience functions
def get_health_status() -> dict[str, Any]:
    """Convenience function to get health status."""
    return HealthService.get_health_status()


def check_mcp_alive(port: int, host: str = "127.0.0.1", timeout: int = 2) -> bool:
    """Convenience function to check MCP server alive."""
    return HealthService.check_mcp_alive(port, host, timeout)


def check_mcp_sse_alive(port: int, host: str = "127.0.0.1", timeout: int = 2) -> bool:
    """Convenience function to check MCP SSE endpoint alive."""
    return HealthService.check_mcp_sse_alive(port, host, timeout)


def format_health_response(
    status: str = "healthy",
    details: dict[str, Any] | None = None,
    include_timestamp: bool = True,
) -> dict[str, Any]:
    """Convenience function to format health response."""
    return HealthService.format_health_response(status, details, include_timestamp)
