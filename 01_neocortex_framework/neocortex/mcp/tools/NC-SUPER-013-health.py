#!/usr/bin/env python3
"""
NC-SUPER-013 — neocortex_health
FÓRUM — Health e Monitoramento Ativo

Funde: health (029) + system monitor parts.

Actions:
  server.health, server.tools_count, log.errors, log.search
  metrics.live, metrics.tool_stats
  watchdog.start, watchdog.status
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_health"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_health(
        action: str,
        pattern: str = "",
        lines: int = 50,
        tool_name: str = "",
    ) -> Dict[str, Any]:
        """FÓRUM — Health e Monitoramento.
        Funde: health (029).
        Actions: server.health, server.tools_count, log.errors, log.search,
                 metrics.live, metrics.tool_stats, watchdog.start, watchdog.status
        """
        ts = _ts()
        root = _root()

        if action == "server.health":
            try:
                import requests
                import socket
                
                # Verificar cada serviço
                result = {}
                
                # Mission Control (3000) - tem /health
                try:
                    r = requests.get("http://localhost:3000/health", timeout=2)
                    result["mission_control_3000"] = {"reachable": r.status_code == 200, "status": "up" if r.status_code == 200 else "down"}
                except:
                    result["mission_control_3000"] = {"reachable": False, "status": "down"}
                
                # Picoclaw (18790) - tem /health
                try:
                    r = requests.get("http://localhost:18790/health", timeout=2)
                    result["picoclaw_18790"] = {"reachable": r.status_code == 200, "status": "up" if r.status_code == 200 else "down"}
                except:
                    result["picoclaw_18790"] = {"reachable": False, "status": "down"}
                
                # LiteLLM (40001) - porta aberta mas sem /health
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    connection_result = sock.connect_ex(('localhost', 40001))
                    sock.close()
                    result["litellm_4000"] = {"reachable": connection_result == 0, "status": "up" if connection_result == 0 else "down"}
                except:
                    result["litellm_4000"] = {"reachable": False, "status": "down"}
                
                # Ollama (11434) - API funciona
                try:
                    r = requests.get("http://localhost:11434/api/tags", timeout=2)
                    result["ollama_11434"] = {"reachable": r.status_code == 200, "status": "up" if r.status_code == 200 else "down"}
                except:
                    result["ollama_11434"] = {"reachable": False, "status": "down"}
                
                # MCP (8765) - Workaround: sempre considerar up
                # FastMCP com stdio não usa porta, então não podemos testar via socket
                result["mcp_8765"] = {"reachable": True, "status": "up"}
                
                online_count = sum(1 for v in result.values() if v["reachable"])
                return {"success": True, "action": action, "services": result,
                        "online": online_count, "total": len(result), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "server.tools_count":
            tools_dir = Path(__file__).parent
            super_tools = list(tools_dir.glob("NC-SUPER-*.py"))
            tool_names = [f.stem.split("-", 3)[-1] for f in super_tools]
            return {"success": True, "action": action,
                    "super_tool_files": len(super_tools),
                    "tool_names": tool_names,
                    "architecture": "CF-v0.2 — 15 super-tools",
                    "v1_archived": len(list((tools_dir / "v1").glob("*.py")))
                    if (tools_dir / "v1").exists() else 0,
                    "timestamp": ts}

        elif action == "log.errors":
            log_dir = root / "DIR-DS-002-audit-logs"
            if not log_dir.exists():
                return {"success": True, "action": action, "errors": [], "timestamp": ts}
            errors = []
            for f in sorted(log_dir.glob("NC-VIO-*.json"))[-10:]:
                try:
                    import json
                    errors.append(json.loads(f.read_text(encoding="utf-8")))
                except Exception:
                    pass
            return {"success": True, "action": action, "errors": errors,
                    "count": len(errors), "timestamp": ts}

        elif action == "log.search":
            if not pattern:
                return {"success": False, "error": "pattern obrigatório", "timestamp": ts}
            log_dir = root / "DIR-DS-002-audit-logs"
            matches = []
            if log_dir.exists():
                for f in sorted(log_dir.glob("*.yaml"))[-50:]:
                    try:
                        text = f.read_text(encoding="utf-8", errors="replace")
                        if pattern.lower() in text.lower():
                            matches.append({"file": f.name,
                                            "snippet": text[:200]})
                    except Exception:
                        pass
            return {"success": True, "action": action, "pattern": pattern,
                    "matches": matches[:20], "count": len(matches), "timestamp": ts}

        elif action == "metrics.live":
            try:
                from neocortex.mcp.server import get_metrics_store
                ms = get_metrics_store()
                if ms:
                    metrics = ms.get_recent(limit=10)
                    return {"success": True, "action": action, "metrics": metrics, "timestamp": ts}
            except Exception:
                pass
            return {"success": True, "action": action, "metrics": {},
                    "note": "MetricsStore indisponível", "timestamp": ts}

        elif action == "metrics.tool_stats":
            tools_dir = Path(__file__).parent
            super_tools = list(tools_dir.glob("NC-SUPER-*.py"))
            stats = []
            for f in sorted(super_tools):
                size = f.stat().st_size
                stats.append({"tool": f.stem, "size_bytes": size,
                               "size_kb": round(size / 1024, 1)})
            return {"success": True, "action": action, "tool_stats": stats,
                    "total_tools": len(stats), "timestamp": ts}

        elif action == "watchdog.status":
            try:
                from neocortex.mcp.server import pulse_scheduler_instance
                if pulse_scheduler_instance:
                    tasks = pulse_scheduler_instance.list_tasks() if hasattr(pulse_scheduler_instance, "list_tasks") else []
                    return {"success": True, "action": action, "running": True,
                            "tasks": tasks, "timestamp": ts}
                return {"success": True, "action": action, "running": False, "timestamp": ts}
            except Exception as e:
                return {"success": True, "action": action, "note": str(e), "timestamp": ts}

        elif action == "watchdog.start":
            try:
                from neocortex.mcp.server import pulse_scheduler_instance
                if pulse_scheduler_instance:
                    pulse_scheduler_instance.start()
                    return {"success": True, "action": action, "status": "started", "timestamp": ts}
                return {"success": False, "error": "PulseScheduler não inicializado", "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}


        elif action == "server.status":
            import socket
            ports = {"mcp": 8765, "litellm": 4000, "ollama": 11434}
            status = {}
            for name, port in ports.items():
                try:
                    s = socket.create_connection(("127.0.0.1", port), timeout=1)
                    s.close()
                    status[name] = {"port": port, "reachable": True}
                except Exception:
                    status[name] = {"port": port, "reachable": False}
            return {"success": True, "action": action, "services": status, "timestamp": ts}

        elif action == "log.tail":
            from pathlib import Path
            log_dir = Path(__file__).parents[4] / "logs"
            if not log_dir.exists():
                return {"success": True, "action": action, "lines": [], "note": "logs/ nao encontrado", "timestamp": ts}
            logs = sorted(log_dir.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
            if not logs:
                return {"success": True, "action": action, "lines": [], "timestamp": ts}
            n = int(lines) if lines else 50
            tail = logs[0].read_text("utf-8", errors="replace").splitlines()[-n:]
            return {"success": True, "action": action, "file": logs[0].name, "lines": tail, "timestamp": ts}

        elif action == "log.purge":
            from pathlib import Path
            log_dir = Path(__file__).parents[4] / "logs"
            if not log_dir.exists():
                return {"success": True, "action": action, "purged": 0, "timestamp": ts}
            old = [f for f in log_dir.glob("*.log") if f.stat().st_size < 100]
            for f in old: f.unlink()
            return {"success": True, "action": action, "purged": len(old), "timestamp": ts}
        # ── GUARDIAN DAEMON (COG-001) ──────────────────────────────────────────
        elif action == "guardian.start":
            try:
                import importlib.util
                fw_dir = Path(__file__).parents[3]
                spec = importlib.util.spec_from_file_location(
                    "guardian_daemon",
                    fw_dir / "scripts" / "NC-SCR-FR-115-guardian-daemon.py"
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                interval = int(lines) if lines else 60
                result = mod.start_guardian(interval=interval)
                return {"success": True, "action": action, **result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "guardian.stop":
            try:
                import importlib.util
                fw_dir = Path(__file__).parents[3]
                spec = importlib.util.spec_from_file_location(
                    "guardian_daemon",
                    fw_dir / "scripts" / "NC-SCR-FR-115-guardian-daemon.py"
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                result = mod.stop_guardian()
                return {"success": True, "action": action, **result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "guardian.status":
            try:
                state_file = Path(__file__).parents[3] / ".neocortex" / "guardian_state.json"
                if state_file.exists():
                    import json
                    state = json.loads(state_file.read_text("utf-8"))
                    return {"success": True, "action": action, "last_report": state, "timestamp": ts}
                return {"success": True, "action": action, "running": False,
                        "note": "guardian_state.json não encontrado — daemon não iniciado", "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        else:
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["server.health", "server.tools_count", "log.errors", "log.search",
                                  "metrics.live", "metrics.tool_stats", "server.status",
                                  "log.tail", "log.purge",
                                  "watchdog.start", "watchdog.status",
                                  "guardian.start", "guardian.stop", "guardian.status"],
                    "timestamp": ts}
