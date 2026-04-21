#!/usr/bin/env python3
"""
NC-SUPER-006 — neocortex_system
FÓRUM — Sistema e Infraestrutura

Funde: system (025), config (005), pulse (015), health (029),
       export (006), init (007).

Actions:
  config.get, config.set, config.list
  pulse.status, pulse.start, pulse.stop, pulse.schedule_custom
  health.agent, health.full, health.tools_count
  system.diagnostics, system.env_check
  export.snapshot, export.list
  init.workspace
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_system"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_system(
        action: str,
        key: str = "",
        value: str = "",
        task_name: str = "",
        schedule_interval: int = 300,
        lines: int = 50,
        output_path: str = "",
    ) -> Dict[str, Any]:
        """FÓRUM — Sistema, Config, Pulse, Health, Export, Init.
        Funde: system, config, pulse, health, export, init.
        Actions: config.get/set/list, pulse.status/start/stop/schedule_custom,
                 health.agent/full/tools_count, system.diagnostics/env_check,
                 export.snapshot/list, init.workspace
        """
        ts = _ts()
        root = _root()

        # ── CONFIG ────────────────────────────────────────────────────────────
        if action == "config.get":
            try:
                from neocortex.core import get_config
                cfg = get_config()
                if key:
                    val = getattr(cfg, key, None)
                    return {"success": True, "action": action, "key": key, "value": val, "timestamp": ts}
                return {"success": True, "action": action,
                        "config": {k: str(v) for k, v in vars(cfg).items()
                                   if not k.startswith("_")}, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "config.list":
            try:
                from neocortex.core import get_config
                cfg = get_config()
                keys = [k for k in vars(cfg) if not k.startswith("_")]
                return {"success": True, "action": action, "keys": keys,
                        "count": len(keys), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── PULSE ─────────────────────────────────────────────────────────────
        elif action == "pulse.status":
            try:
                from neocortex.mcp.server import pulse_scheduler_instance
                if pulse_scheduler_instance and pulse_scheduler_instance.is_running():
                    tasks = pulse_scheduler_instance.list_tasks()
                    return {"success": True, "action": action, "running": True,
                            "tasks": tasks, "count": len(tasks), "timestamp": ts}
                return {"success": True, "action": action, "running": False, "timestamp": ts}
            except Exception as e:
                return {"success": True, "action": action, "note": str(e), "timestamp": ts}

        elif action == "pulse.schedule_custom":
            if not task_name:
                return {"success": False, "error": "task_name obrigatório", "timestamp": ts}
            try:
                from neocortex.mcp.server import pulse_scheduler_instance
                if pulse_scheduler_instance:
                    pulse_scheduler_instance.schedule_task(task_name, schedule_interval)
                    return {"success": True, "action": action, "task": task_name,
                            "interval_sec": schedule_interval, "timestamp": ts}
                return {"success": False, "error": "PulseScheduler não inicializado", "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── HEALTH ────────────────────────────────────────────────────────────
        elif action == "health.agent":
            try:
                import requests
                services = {
                    "mcp_8765": {"port": 8765},
                    "mission_control_3000": {"port": 3000},
                    "picoclaw_18790": {"port": 18790},
                }
                for name, info in services.items():
                    try:
                        r = requests.get(f"http://localhost:{info['port']}/health", timeout=2)
                        services[name]["reachable"] = r.ok
                        services[name]["status"] = "up" if r.ok else "down"
                    except Exception:
                        services[name]["reachable"] = False
                        services[name]["status"] = "down"
                return {"success": True, "action": action, "services": services, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "health.tools_count":
            tools_dir = Path(__file__).parent
            tool_files = [f for f in tools_dir.glob("*.py") if f.name != "__init__.py"]
            return {"success": True, "action": action, "tool_files": len(tool_files),
                    "tool_names": [f.stem.replace("NC-SUPER-", "").split("-", 1)[-1]
                                   for f in tool_files], "timestamp": ts}

        elif action == "health.full":
            tools_dir = Path(__file__).parent
            tool_count = len([f for f in tools_dir.glob("NC-SUPER-*.py")])
            return {"success": True, "action": action,
                    "super_tools": tool_count, "architecture": "CF-v0.2",
                    "tiers": ["STF", "STJ", "TJ", "FORUM"],
                    "powers": ["legislativo", "executivo", "judiciario"], "timestamp": ts}

        elif action == "system.diagnostics":
            import platform
            import sys
            return {"success": True, "action": action,
                    "python_version": sys.version.split()[0],
                    "platform": platform.system(),
                    "project_root": str(root),
                    "tools_dir": str(Path(__file__).parent),
                    "timestamp": ts}

        elif action == "system.env_check":
            checks = {}
            try:
                import requests
                checks["requests"] = True
            except ImportError:
                checks["requests"] = False
            try:
                import yaml
                checks["yaml"] = True
            except ImportError:
                checks["yaml"] = False
            try:
                from neocortex.core import get_config
                get_config()
                checks["neocortex_config"] = True
            except Exception:
                checks["neocortex_config"] = False
            return {"success": True, "action": action, "env_checks": checks,
                    "all_ok": all(checks.values()), "timestamp": ts}

        # ── EXPORT ────────────────────────────────────────────────────────────
        elif action == "export.snapshot":
            try:
                from neocortex.core import get_export_service
                svc = get_export_service()
                result = svc.export()
                return {"success": True, "action": action, "snapshot": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "export.list":
            export_dir = root / "exports"
            if not export_dir.exists():
                return {"success": True, "action": action, "exports": [], "count": 0, "timestamp": ts}
            exports = [f.name for f in sorted(export_dir.glob("*.json"))]
            return {"success": True, "action": action, "exports": exports[-20:],
                    "count": len(exports), "timestamp": ts}

        # ── INIT ──────────────────────────────────────────────────────────────
        elif action == "init.workspace":
            try:
                from neocortex.core import get_init_service
                svc = get_init_service()
                result = svc.initialize()
                return {"success": True, "action": action, "result": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── CONFIG (extended from NC-TOOL-FR-025) ─────────────────────────────
        elif action == "config.reload":
            try:
                from neocortex.core import get_config
                cfg = get_config()
                if hasattr(cfg, "reload"):
                    cfg.reload()
                    return {"success": True, "action": action,
                            "message": "Configuracao recarregada.", "timestamp": ts}
                return {"success": False, "error": "ConfigProvider nao suporta reload", "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "config.diff":
            try:
                import yaml

                from neocortex.core import get_config
                cfg = get_config()
                base = getattr(cfg, "project_root", None)
                if base is None:
                    return {"success": False, "error": "project_root nao disponivel", "timestamp": ts}
                prod_path = Path(base) / "neocortex_config.yaml"
                dev_path  = Path(base) / "DIR-CFG-FR-001-config-main" / "neocortex_config_dev.yaml"
                if not dev_path.exists():
                    return {"success": False, "error": f"Config dev nao encontrada: {dev_path}", "timestamp": ts}
                prod = yaml.safe_load(prod_path.read_text("utf-8")) or {}
                dev  = yaml.safe_load(dev_path.read_text("utf-8"))  or {}
                diff = {k: {"prod": prod.get(k), "dev": dev.get(k)}
                        for k in set(prod) | set(dev) if prod.get(k) != dev.get(k)}
                return {"success": True, "action": action, "diff": diff,
                        "prod_file": str(prod_path), "dev_file": str(dev_path), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "config.set_model":
            if not key:
                return {"success": False, "error": "key (model name) obrigatorio", "timestamp": ts}
            try:
                from neocortex.core import get_config_service
                svc = get_config_service()
                result = svc.set_model(key) if hasattr(svc, "set_model") else {"success": False, "error": "set_model nao disponivel"}
                return {**result, "action": action, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "config.list_models":
            try:
                from neocortex.core import get_config_service
                svc = get_config_service()
                result = svc.list_available_models() if hasattr(svc, "list_available_models") else {"models": []}
                return {**result, "action": action, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "config.set_agent_backend":
            import json as _json
            if not key or not value:
                return {"success": False, "error": "key (role) e value (backend JSON) obrigatorios", "timestamp": ts}
            try:
                from neocortex.core import get_config
                cfg = get_config()
                try:
                    backend_config = _json.loads(value)
                except Exception:
                    backend_config = {"provider": value}
                cfg.set(f"llm.agent_backends.{key}", backend_config)
                return {"success": True, "action": action, "role": key,
                        "backend_config": backend_config, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── PULSE (extended) ──────────────────────────────────────────────────
        elif action == "pulse.force":
            if not task_name:
                return {"success": False, "error": "task_name obrigatorio", "timestamp": ts}
            try:
                from neocortex.mcp.server import pulse_scheduler_instance
                if pulse_scheduler_instance and hasattr(pulse_scheduler_instance, "force_task"):
                    result = pulse_scheduler_instance.force_task(task_name)
                    return {"success": True, "action": action, "task_name": task_name,
                            "result": result, "timestamp": ts}
                return {"success": False, "error": "PulseScheduler.force_task nao disponivel", "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        else:
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["config.get", "config.set", "config.list",
                                  "config.reload", "config.diff", "config.set_model",
                                  "config.list_models", "config.set_agent_backend",
                                  "pulse.status", "pulse.start", "pulse.stop",
                                  "pulse.schedule_custom", "pulse.force",
                                  "health.agent", "health.full", "health.tools_count",
                                  "system.diagnostics", "system.env_check",
                                  "export.snapshot", "export.list", "init.workspace"],
                    "timestamp": ts}
