#!/usr/bin/env python3
"""
NeoCortex Subserver Tool

MCP tool for neocortex_subserver - orchestration of isolated sub-MCP servers.
"""

import subprocess
import signal
import time
import json
from typing import Dict, Any, List
from pathlib import Path

# Global registry of active sub-servers
# Format: {port: {"process": Popen, "lobe_dir": str, "tools": List[str]}}
_active_subservers: Dict[int, Dict[str, Any]] = {}


def register_tool(mcp):
    """
    Register the neocortex_subserver tool with the MCP server.
    """

    @mcp.tool(name="neocortex_subserver")
    def tool_subserver(
        action: str,
        port: int = None,
        lobe_dir: str = None,
        tools: str = None,
        task_data: str = None,
    ) -> Dict[str, Any]:
        """
        Orchestrate isolated sub-MCP servers for multi-agent execution.

        Actions:
        - spawn: Start a new sub-MCP server on specified port with lobe directory and tools
        - stop: Stop a running sub-server on specified port
        - list_active: List all currently active sub-servers
        - send_task: Send a task to a sub-server (simulated - requires implementation)
        """
        if action == "spawn":
            return _spawn_subserver(port, lobe_dir, tools)
        elif action == "stop":
            return _stop_subserver(port)
        elif action == "list_active":
            return _list_active()
        elif action == "send_task":
            return _send_task(port, task_data)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}


def _spawn_subserver(port: int, lobe_dir: str, tools: str) -> Dict[str, Any]:
    """Start a new sub-MCP server."""
    if port in _active_subservers:
        return {"success": False, "error": f"Port {port} already in use"}

    # Validate lobe directory exists
    lobe_path = Path(lobe_dir)
    if not lobe_path.exists():
        return {"success": False, "error": f"Lobe directory not found: {lobe_dir}"}

    # Build command to start sub-server
    script_path = Path(__file__).parent.parent / "sub_server.py"
    if not script_path.exists():
        return {
            "success": False,
            "error": f"Sub-server script not found: {script_path}",
        }

    cmd = [
        "python",
        str(script_path),
        "--port",
        str(port),
        "--lobe-dir",
        lobe_dir,
        "--tools",
        tools,
    ]

    try:
        # Start subprocess
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )

        # Give it a moment to start
        time.sleep(1)

        # Check if process is still running
        if proc.poll() is not None:
            stdout, stderr = proc.communicate(timeout=1)
            return {
                "success": False,
                "error": f"Sub-server failed to start: {stderr}",
                "stdout": stdout,
            }

        # Register the sub-server
        _active_subservers[port] = {
            "process": proc,
            "lobe_dir": lobe_dir,
            "tools": tools.split(",") if tools else [],
            "start_time": time.time(),
        }

        return {
            "success": True,
            "message": f"Sub-server started on port {port}",
            "port": port,
            "pid": proc.pid,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def _stop_subserver(port: int) -> Dict[str, Any]:
    """Stop a running sub-server."""
    if port not in _active_subservers:
        return {"success": False, "error": f"No sub-server running on port {port}"}

    server_info = _active_subservers.pop(port)
    proc = server_info["process"]

    try:
        # Try graceful termination
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            # Force kill if doesn't terminate
            proc.kill()
            proc.wait()

        return {
            "success": True,
            "message": f"Sub-server on port {port} stopped",
            "port": port,
            "pid": proc.pid,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _list_active() -> Dict[str, Any]:
    """List all active sub-servers."""
    servers = []
    for port, info in _active_subservers.items():
        proc = info["process"]
        servers.append(
            {
                "port": port,
                "pid": proc.pid,
                "lobe_dir": info["lobe_dir"],
                "tools": info["tools"],
                "running": proc.poll() is None,
                "uptime_seconds": time.time() - info["start_time"],
            }
        )

    return {"success": True, "servers": servers, "total": len(servers)}


def _send_task(port: int, task_data: str) -> Dict[str, Any]:
    """Send a task to a sub-server (simulated - would require IPC)."""
    if port not in _active_subservers:
        return {"success": False, "error": f"No sub-server running on port {port}"}

    # For now, simulate task execution
    # In a real implementation, this would communicate via TCP/WebSocket
    try:
        task_dict = json.loads(task_data) if task_data else {}
        return {
            "success": True,
            "message": f"Task sent to sub-server on port {port}",
            "port": port,
            "task": task_dict.get("type", "unknown"),
            "simulated": True,
            "note": "Actual IPC not implemented - requires sub-server communication protocol",
        }
    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid JSON in task_data"}
