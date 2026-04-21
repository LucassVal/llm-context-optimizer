from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.181489'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TOOL-FR-029-health
related_ssot:
  - NC-LOG-FR-001-hud-audit
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-TOOL-FR-029-health.py
FR-029  MCP Tool: neocortex_health

Observabilidade em tempo real do sistema NeoCortex.
Aes disponveis:
  server.status       uptime, tools carregadas, transport
  server.tools_count  N tools e N aes registradas
  agent.health        /health HTTP de sub-server especfico
  agent.health_all    health check de todos os sub-servers ativos
  agent.last_error    ltimo erro de cada agente
  metrics.live        mtricas em tempo real (tokens, latncia, erros)
  metrics.dashboard   snapshot completo para HUD
  log.tail            ltimas N linhas do log JSONL
  log.errors          apenas entradas de erro
  log.search          busca no log por pattern
  log.purge           apagar logs > N dias (TTL-002)
"""


import json
import logging
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_START_TIME = time.time()


def _config():
    try:
        from neocortex.config import get_config
        return get_config()
    except Exception:
        return None


def _get_log_dir() -> Path:
    cfg = _config()
    if cfg:
        try:
            base = Path(cfg.base_path)
            return base / "NC-LOG-FR-001-hud-audit"
        except Exception:
            pass
    return Path("NC-LOG-FR-001-hud-audit")


def _get_metrics_store():
    try:
        from neocortex.core import get_metrics_store
        return get_metrics_store()
    except Exception:
        return None


def _http_health(host: str, port: int, timeout: int = 3) -> Dict[str, Any]:
    """Faz GET /health em um sub-server e retorna o resultado."""
    url = f"http://{host}:{port}/health"
    try:
        req = urllib.request.urlopen(url, timeout=timeout)
        data = json.loads(req.read().decode())
        return {"reachable": True, "status": data.get("status", "ok"), "data": data}
    except urllib.error.URLError as e:
        return {"reachable": False, "error": str(e.reason)}
    except Exception as e:
        return {"reachable": False, "error": str(e)}


# Portas padro por role (definido em neocortex_config.yaml / INFRA-002)
DEFAULT_PORTS = {
    "courier": 8767,
    "engineer": 8768,
    "guardian": 8769,
}


def register_tool(mcp) -> None:
    """Registra neocortex_health no servidor MCP."""

    @mcp.tool(name="neocortex_health")
    def neocortex_health(
        action: str,
        agent_role: str = "",
        port: int = 0,
        lines: int = 50,
        pattern: str = "",
        days: int = 7,
    ) -> Dict[str, Any]:
        """Observabilidade em tempo real do sistema NeoCortex.

        Actions: server.status, server.tools_count, agent.health, agent.health_all,
                 metrics.live, log.tail, log.errors, log.search, log.purge
        """

        #  server.status
        if action == "server.status":
            uptime_s = int(time.time() - _START_TIME)
            h, rem = divmod(uptime_s, 3600)
            m, s = divmod(rem, 60)
            return {
                "success": True,
                "action": action,
                "uptime": f"{h:02d}:{m:02d}:{s:02d}",
                "uptime_seconds": uptime_s,
                "server": "neocortex-mcp",
                "timestamp": datetime.now().isoformat(),
                "status": "running",
            }

        #  server.tools_count
        elif action == "server.tools_count":
            tools_dir = Path(__file__).parent
            tool_files = list(tools_dir.glob("NC-TOOL-FR-*.py"))
            return {
                "success": True,
                "action": action,
                "tool_files": len(tool_files),
                "tool_names": [f.stem.split("-")[-1] for f in sorted(tool_files)],
            }

        #  agent.health
        elif action == "agent.health":
            if not agent_role and not port:
                return {"success": False, "error": "Fornea agent_role ou port."}
            _port = port or DEFAULT_PORTS.get(agent_role, 0)
            if not _port:
                return {"success": False, "error": f"Role '{agent_role}' desconhecido. Use: {list(DEFAULT_PORTS.keys())}"}
            result = _http_health("localhost", _port)
            return {"success": True, "action": action, "agent_role": agent_role or "custom", "port": _port, **result}

        #  agent.health_all
        elif action == "agent.health_all":
            results = {}
            for role, p in DEFAULT_PORTS.items():
                results[role] = _http_health("localhost", p)
            healthy = sum(1 for r in results.values() if r.get("reachable"))
            return {
                "success": True,
                "action": action,
                "healthy": healthy,
                "total": len(results),
                "agents": results,
            }

        #  metrics.live
        elif action == "metrics.live":
            import socket
            ms = _get_metrics_store()
            metrics_summary: Dict[str, Any] = {}
            if ms is not None:
                try:
                    metrics_summary = ms.get_summary() if hasattr(ms, "get_summary") else {}
                except Exception as e:
                    metrics_summary = {"error": str(e)}

            # T-07: verificar portas externas (Mission Control, PicoClaw, Pixel Agents)
            external_ports = {
                "mission_control_3000": 3000,
                "picoclaw_18790": 18790,
                "pixel_agents_8767": 8767,
            }
            external_services: Dict[str, Any] = {}
            for svc_name, svc_port in external_ports.items():
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(("localhost", svc_port))
                    sock.close()
                    external_services[svc_name] = {
                        "port": svc_port,
                        "reachable": result == 0,
                        "status": "up" if result == 0 else "down",
                    }
                except Exception as exc:
                    external_services[svc_name] = {"port": svc_port, "reachable": False, "error": str(exc)}

            return {
                "success": True,
                "action": action,
                "metrics": metrics_summary,
                "external_services": external_services,
                "timestamp": datetime.now().isoformat(),
            }


        #  log.tail
        elif action == "log.tail":
            log_dir = _get_log_dir()
            jsonl_files = sorted(log_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
            if not jsonl_files:
                return {"success": False, "error": f"Nenhum log JSONL encontrado em {log_dir}"}
            log_file = jsonl_files[0]
            try:
                all_lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
                tail = all_lines[-lines:]
                parsed = []
                for ln in tail:
                    try:
                        parsed.append(json.loads(ln))
                    except Exception:
                        parsed.append({"raw": ln})
                return {"success": True, "action": action, "file": log_file.name, "count": len(parsed), "lines": parsed}
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  log.errors
        elif action == "log.errors":
            log_dir = _get_log_dir()
            jsonl_files = sorted(log_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
            if not jsonl_files:
                return {"success": False, "error": "Nenhum log encontrado."}
            errors: List[Dict] = []
            for log_file in jsonl_files[:3]:  # ltimos 3 arquivos
                try:
                    for ln in log_file.read_text(encoding="utf-8", errors="replace").splitlines():
                        try:
                            entry = json.loads(ln)
                            if entry.get("levelname") in ("ERROR", "CRITICAL") or entry.get("level") in ("ERROR", "CRITICAL"):
                                errors.append(entry)
                        except Exception:
                            pass
                except Exception:
                    pass
            return {"success": True, "action": action, "error_count": len(errors), "errors": errors[-lines:]}

        #  log.search
        elif action == "log.search":
            if not pattern:
                return {"success": False, "error": "Fornea pattern para pesquisa."}
            log_dir = _get_log_dir()
            matches: List[Dict] = []
            for log_file in sorted(log_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)[:5]:
                try:
                    for ln in log_file.read_text(encoding="utf-8", errors="replace").splitlines():
                        if pattern.lower() in ln.lower():
                            try:
                                matches.append(json.loads(ln))
                            except Exception:
                                matches.append({"raw": ln})
                except Exception:
                    pass
            return {"success": True, "action": action, "pattern": pattern, "count": len(matches), "results": matches[:lines]}

        #  log.purge
        elif action == "log.purge":
            log_dir = _get_log_dir()
            cutoff = datetime.now() - timedelta(days=days)
            removed = []
            for log_file in log_dir.glob("*.jsonl"):
                try:
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if mtime < cutoff:
                        log_file.unlink()
                        removed.append(log_file.name)
                except Exception as e:
                    logger.warning(f"[health_tool] Erro ao purge {log_file}: {e}")
            return {
                "success": True,
                "action": action,
                "days_threshold": days,
                "removed_count": len(removed),
                "removed_files": removed,
            }

        #  ao desconhecida
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'.",
                "available": [
                    "server.status", "server.tools_count",
                    "agent.health", "agent.health_all",
                    "metrics.live",
                    "log.tail", "log.errors", "log.search", "log.purge",
                ],
            }
