"""---
domain: "orchestration"
layer: "core"
type: "service"
tags: ["tool", "016", "subserver"]
hash: "auto-generated"
---"""
#!/usr/bin/env python3
"""
NeoCortex Subserver Tool  NC-TOOL-FR-016
ORCH-301: Real HTTP IPC for spawn (with role) + send_task.
ORCH-302: Sub-server exposes /task endpoint (in sub_server.py).
"""

import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict

# Global registry of active sub-servers
# Format: {port: {"process": Popen, "lobe_dir": str, "tools": List[str], "role": str}}
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
        role: str = "courier",
        task_data: str = None,
    ) -> Dict[str, Any]:
        """
        Orchestrate isolated sub-MCP servers for multi-agent execution.

        Actions:
        - spawn: Start a new sub-MCP server on specified port with lobe directory, tools and role
        - stop: Stop a running sub-server on specified port
        - list_active: List all currently active sub-servers
        - send_task: Send a task to a sub-server via HTTP POST to /task
        - health: Check if sub-server is alive
        """
        if action == "spawn":
            return _spawn_subserver(port, lobe_dir, tools, role)
        elif action == "stop":
            return _stop_subserver(port)
        elif action == "list_active":
            return _list_active()
        elif action == "send_task":
            return _send_task(port, task_data)
        elif action == "health":
            return _health_check(port)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}


#  ORCH-301a: spawn com --role
def _spawn_subserver(port: int, lobe_dir: str, tools: str, role: str = "courier") -> Dict[str, Any]:
    """Start a new sub-MCP server with role and HTTP task endpoint."""
    if port in _active_subservers:
        return {"success": False, "error": f"Port {port} already in use"}

    lobe_path = Path(lobe_dir)
    if not lobe_path.exists():
        return {"success": False, "error": f"Lobe directory not found: {lobe_dir}"}

    script_path = Path(__file__).parent.parent / "sub_server.py"
    if not script_path.exists():
        return {"success": False, "error": f"Sub-server script not found: {script_path}"}

    # ORCH-301b: passa --role e --http-port para ativar endpoint /task
    cmd = [
        "python", str(script_path),
        "--port", str(port),
        "--lobe-dir", lobe_dir,
        "--tools", tools,
        "--role", role,
        "--http-port", str(port),   # HTTP REST API na mesma porta numrica
    ]

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )
        time.sleep(2)  # aguarda sub-server inicializar

        if proc.poll() is not None:
            stdout, stderr = proc.communicate(timeout=1)
            return {"success": False, "error": f"Sub-server failed to start: {stderr}", "stdout": stdout}

        _active_subservers[port] = {
            "process": proc,
            "lobe_dir": lobe_dir,
            "tools": tools.split(",") if tools else [],
            "role": role,
            "http_port": port,
            "start_time": time.time(),
        }

        return {
            "success": True,
            "message": f"Sub-server '{role}' started on port {port}",
            "port": port,
            "role": role,
            "pid": proc.pid,
            "http_endpoint": f"http://127.0.0.1:{port}/task",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


#  ORCH-301a: _send_task via HTTP IPC (real)
def _send_task(port: int, task_data: str) -> Dict[str, Any]:
    """
    Send a task to a sub-server via HTTP POST to /task.
    ORCH-301: Real implementation replacing simulated stub.
    """
    if port not in _active_subservers:
        return {"success": False, "error": f"No sub-server running on port {port}"}

    server_info = _active_subservers[port]
    http_port = server_info.get("http_port", port)
    url = f"http://127.0.0.1:{http_port}/task"

    try:
        task_dict = json.loads(task_data) if task_data else {}
    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid JSON in task_data"}

    payload = json.dumps(task_dict).encode("utf-8")

    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            response_body = resp.read().decode("utf-8")
            result = json.loads(response_body)
            return {
                "success": True,
                "port": port,
                "role": server_info.get("role", "unknown"),
                "http_status": resp.status,
                "result": result,
            }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"HTTP connection failed to {url}: {e.reason}",
            "hint": "Ensure sub-server is running with --http-port and /task endpoint is active",
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
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

        return {
            "success": True,
            "message": f"Sub-server '{server_info.get('role','?')}' on port {port} stopped",
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
        servers.append({
            "port": port,
            "pid": proc.pid,
            "role": info.get("role", "unknown"),
            "lobe_dir": info["lobe_dir"],
            "tools": info["tools"],
            "running": proc.poll() is None,
            "http_endpoint": f"http://127.0.0.1:{info.get('http_port', port)}/task",
            "uptime_seconds": round(time.time() - info["start_time"], 1),
        })

    return {"success": True, "servers": servers, "total": len(servers)}


def _health_check(port: int) -> Dict[str, Any]:
    """Check if sub-server HTTP endpoint is alive."""
    if port not in _active_subservers:
        return {"success": False, "alive": False, "error": f"No sub-server on port {port}"}

    url = f"http://127.0.0.1:{port}/health"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return {"success": True, "alive": True, "port": port, "response": body}
    except Exception as e:
        # Check if process is still running even if HTTP not up yet
        info = _active_subservers.get(port, {})
        proc = info.get("process")
        running = proc.poll() is None if proc else False
        return {"success": True, "alive": running, "port": port, "http_ready": False, "note": str(e)}
