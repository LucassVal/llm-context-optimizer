#!/usr/bin/env python3
"""---
NC-SUPER-006 — neocortex_system
FÓRUM — Sistema, Config, Pulse, Health, Export, Init

WHAT: Configuration management (get/set/list/reload/diff/model/agent_backend),
      pulse scheduler control (status/start/stop/schedule/force via
      NC-CORE-FR-142), health probes for MCP/Ollama/Mission-Control services,
      system diagnostics and env checks, export snapshots, workspace
      initialization, and regulatory agency inspections.
WHY: Fuse 6 infrastructure tools (system, config, pulse, health, export,
     init) into one Forum-tier entry point for centralized runtime config,
     scheduled task management, and health monitoring.
WHERE: Registered as 'neocortex_system' — accessed by T0 governance routines,
       boot sequences, and health dashboards managing runtime config and
       monitoring service availability across the framework.

Actions: config.get/set/list/reload/diff/set_model/list_models/
  set_agent_backend,
  pulse.status/start/stop/schedule_custom/force,
  health.agent/full/tools_count,
  system.diagnostics/env_check,
  export.snapshot/list, init.workspace,
  regulatory.health/audit
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from ..errors import mcp_response
logger = logging.getLogger(__name__)
from ..errors import mcp_error, mcp_success
TOOL_NAME = "neocortex_system"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    @mcp_response
    def neocortex_system(
        action: str,
        key: str = "",
        value: str = "",
        task_name: str = "",
        schedule_interval: int = 300,
        lines: int = 50,
        output_path: str = "",
    ) -> dict[str, Any]:
        """FÓRUM — Sistema, Config, Pulse, Health, Export, Init.
        Funde: system, config, pulse, health, export, init.
        Actions: config.get/set/list, pulse.status/start/stop/schedule_custom,
                 health.agent/full/tools_count, system.diagnostics/env_check,
                 export.snapshot/list, init.workspace
        """
        ts = _ts()
        # ── GATEWAY VALIDATION ──────────────────────────────
        try:
            from neocortex.core.utils.gateway_bridge import gateway_check
            _ok, _report = gateway_check(action, root)
            if not _ok:
                return _report
        except Exception:
            pass

        root = _root()

        # ── TOOLGUARD: STEP 0 + LockGuard (G1+G2) ────────────────────────────
        _guard = None
        try:
            import importlib.util
            _spec = importlib.util.spec_from_file_location("tool_guard", str(root / "neocortex" / "core" / "NC-CORE-FR-125-tool-guard.py"))
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            _guard = _mod.ToolGuard()
            _step0 = _guard.step_zero(action)
            if not _step0.get("ok"):
                return {"success": True, "action": action,
                        "step0_warning": _step0.get("warning", "STEP-0 alert"),
                        "matched_error": _step0.get("matched_error", ""), "timestamp": ts}
        except Exception:
            pass

        # ── CONFIG ────────────────────────────────────────────────────────────
        if action == "config.get":
            try:
                from neocortex.core import get_config
                cfg = get_config()
                if key:
                    val = getattr(cfg, key, None)
                    return mcp_success({"action": action, "key": key, "value": val, "timestamp": ts})
                return mcp_success({"action": action,
                        "config": {k: str(v) for k, v in vars(cfg).items()
                                   if not k.startswith("_")}, "timestamp": ts})
            except Exception as e:
                return mcp_error(str(e), context=f"action: {action}")

        elif action == "config.list":
            try:
                from neocortex.core import get_config
                cfg = get_config()
                keys = [k for k in vars(cfg) if not k.startswith("_")]
                return mcp_success({"action": action, "keys": keys,
                        "count": len(keys), "timestamp": ts})
            except Exception as e:
                return mcp_error(str(e), context=f"action: {action}")

        elif action == "config.set":
            if not key:
                return mcp_error("key obrigatório")
            # G1 LockGuard: validate write to config
            if _guard:
                _ok = _guard.validate_write("DIR-CFG-FR-001-config-main/")
                if not _ok:
                    return mcp_error(_guard.last_error or "LockGuard block")
                # G3 STEP -1: auto savepoint
                _guard.savepoint_before_write("config.set")
            try:
                from neocortex.core import get_config_service
                svc = get_config_service()
                result = svc.set(key, value)
                return mcp_success({"action": action, "key": key, "value": value,
                        "result": result, "timestamp": ts})
            except Exception as e:
                return mcp_error(str(e))

        # ── PULSE ─────────────────────────────────────────────────────────────
        elif action == "pulse.status":
            try:
                import importlib.util as _iu
                _s = _iu.spec_from_file_location("po", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-142-pulse-scheduler-orbital.py"))
                _m = _iu.module_from_spec(_s); _s.loader.exec_module(_m)
                pulse_scheduler_instance = _m.get_pulse_scheduler()  # R26 orbital
                if pulse_scheduler_instance and hasattr(pulse_scheduler_instance, "is_running") and pulse_scheduler_instance.is_running():
                    tasks = pulse_scheduler_instance.list_tasks()
                    return mcp_success({"action": action, "running": True,
                            "tasks": tasks, "count": len(tasks), "timestamp": ts})
                return mcp_success({"action": action, "running": False, "timestamp": ts})
            except Exception as e:
                return {"success": True, "action": action, "note": str(e), "timestamp": ts}

        elif action == "pulse.start":
            try:
                import importlib.util as _iu
                _s = _iu.spec_from_file_location("po", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-142-pulse-scheduler-orbital.py"))
                _m = _iu.module_from_spec(_s); _s.loader.exec_module(_m)
                pulse_scheduler_instance = _m.get_pulse_scheduler()  # R26 orbital
                if pulse_scheduler_instance:
                    pulse_scheduler_instance.start()
                    return mcp_success({"action": action, "running": True,
                            "message": "PulseScheduler iniciado.", "timestamp": ts})
                return mcp_error("PulseScheduler não inicializado")
            except Exception as e:
                return mcp_error(str(e))

        elif action == "pulse.stop":
            try:
                import importlib.util as _iu
                _s = _iu.spec_from_file_location("po", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-142-pulse-scheduler-orbital.py"))
                _m = _iu.module_from_spec(_s); _s.loader.exec_module(_m)
                pulse_scheduler_instance = _m.get_pulse_scheduler()  # R26 orbital
                if pulse_scheduler_instance:
                    pulse_scheduler_instance.stop()
                    return mcp_success({"action": action, "running": False,
                            "message": "PulseScheduler parado.", "timestamp": ts})
                return mcp_error("PulseScheduler não inicializado")
            except Exception as e:
                return mcp_error(str(e))

        elif action == "pulse.schedule_custom":
            if not task_name:
                return {"success": False, "error": "task_name obrigatório", "timestamp": ts}
            try:
                import importlib.util as _iu
                _s = _iu.spec_from_file_location("po", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-142-pulse-scheduler-orbital.py"))
                _m = _iu.module_from_spec(_s); _s.loader.exec_module(_m)
                pulse_scheduler_instance = _m.get_pulse_scheduler()  # R26 orbital
                if pulse_scheduler_instance:
                    pulse_scheduler_instance.schedule_task(task_name, schedule_interval)
                    return mcp_success({"action": action, "task": task_name,
                            "interval_sec": schedule_interval, "timestamp": ts})
                return mcp_error("PulseScheduler não inicializado")
            except Exception as e:
                return mcp_error(str(e))

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
                return mcp_success({"action": action, "services": services, "timestamp": ts})
            except Exception as e:
                return mcp_error(str(e))

        elif action == "health.tools_count":
            tools_dir = Path(__file__).parent
            tool_files = [f for f in tools_dir.glob("*.py") if f.name != "__init__.py"]
            return {"success": True, "action": action, "tool_files": len(tool_files),
                    "tool_names": [f.stem.replace("NC-SUPER-", "").split("-", 1)[-1]
                                   for f in tool_files], "timestamp": ts}

        elif action == "health.full":
            tools_dir = Path(__file__).parent
            tool_count = len(list(tools_dir.glob("NC-SUPER-*.py")))
            return mcp_success({"action": action,
                    "super_tools": tool_count, "architecture": "CF-v0.2",
                    "tiers": ["STF", "STJ", "TJ", "FORUM"],
                    "powers": ["legislativo", "executivo", "judiciario"], "timestamp": ts})

        elif action == "system.diagnostics":
            import platform
            import sys
            return mcp_success({"action": action,
                    "python_version": sys.version.split()[0],
                    "platform": platform.system(),
                    "project_root": str(root),
                    "tools_dir": str(Path(__file__).parent),
                    "timestamp": ts})

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
            return mcp_success({"action": action, "env_checks": checks,
                    "all_ok": all(checks.values()), "timestamp": ts})

        # ── EXPORT ────────────────────────────────────────────────────────────
        elif action == "export.snapshot":
            try:
                from neocortex.core import get_export_service
                svc = get_export_service()
                result = svc.export()
                return mcp_success({"action": action, "snapshot": result, "timestamp": ts})
            except Exception as e:
                return mcp_error(str(e))

        elif action == "export.list":
            export_dir = root / "exports"
            if not export_dir.exists():
                return mcp_success({"action": action, "exports": [], "count": 0, "timestamp": ts})
            exports = [f.name for f in sorted(export_dir.glob("*.json"))]
            return mcp_success({"action": action, "exports": exports[-20:],
                    "count": len(exports), "timestamp": ts})

        # ── INIT ──────────────────────────────────────────────────────────────
        elif action == "init.workspace":
            try:
                from neocortex.core import get_init_service
                svc = get_init_service()
                result = svc.initialize()
                return mcp_success({"action": action, "result": result, "timestamp": ts})
            except Exception as e:
                return mcp_error(str(e))

        # ── CONFIG (extended from NC-TOOL-FR-025) ─────────────────────────────
        elif action == "config.reload":
            try:
                from neocortex.core import get_config
                cfg = get_config()
                if hasattr(cfg, "reload"):
                    cfg.reload()
                    return mcp_success({"action": action,
                            "message": "Configuracao recarregada.", "timestamp": ts})
                return mcp_error("ConfigProvider nao suporta reload")
            except Exception as e:
                return mcp_error(str(e))

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
                return mcp_success({"action": action, "diff": diff,
                        "prod_file": str(prod_path), "dev_file": str(dev_path), "timestamp": ts})
            except Exception as e:
                return mcp_error(str(e))

            try:
                from neocortex.core import get_config_service
                svc = get_config_service()
                result = svc.set_model(key) if hasattr(svc, "set_model") else {"success": False, "error": "set_model nao disponivel"}
                if result.get("success"):
                    return mcp_success({**result, "action": action, "timestamp": ts})
                return mcp_error(result.get("error", "set_model failed"))
            except Exception as e:
                return mcp_error(str(e))

        elif action == "config.list_models":
            try:
                from neocortex.core import get_config_service
                svc = get_config_service()
                result = svc.list_available_models() if hasattr(svc, "list_available_models") else {"models": []}
                return mcp_success({**result, "action": action, "timestamp": ts})
            except Exception as e:
                return mcp_error(str(e))

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
                return mcp_success({"action": action, "role": key,
                        "backend_config": backend_config, "timestamp": ts})
            except Exception as e:
                return mcp_error(str(e))

        # ── PULSE (extended) ──────────────────────────────────────────────────
        elif action == "pulse.force":
            if not task_name:
                return {"success": False, "error": "task_name obrigatorio", "timestamp": ts}
            try:
                import importlib.util as _iu
                _s = _iu.spec_from_file_location("po", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-142-pulse-scheduler-orbital.py"))
                _m = _iu.module_from_spec(_s); _s.loader.exec_module(_m)
                pulse_scheduler_instance = _m.get_pulse_scheduler()  # R26 orbital
                if pulse_scheduler_instance and hasattr(pulse_scheduler_instance, "force_task"):
                    result = pulse_scheduler_instance.force_task(task_name)
                    return mcp_success({"action": action, "task_name": task_name,
                            "result": result, "timestamp": ts})
                return mcp_error("PulseScheduler.force_task nao disponivel")
            except Exception as e:
                return mcp_error(str(e))

        # ── Regulatory Agencies ─────────────────────────────────────────────
        elif action == "regulatory.health":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("reg", str(root / "neocortex" / "core" / "NC-CORE-FR-133-regulatory-agencies.py"))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                r = mod.get_regulatory().anv.inspect(root)
                return mcp_success({"action": action, "result": r, "timestamp": ts})
            except Exception as e: return mcp_error(str(e))

        elif action == "regulatory.audit":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("reg", str(root / "neocortex" / "core" / "NC-CORE-FR-133-regulatory-agencies.py"))
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
                r = mod.get_regulatory().full_audit(root)
                return mcp_success({"action": action, "result": r, "timestamp": ts})
            except Exception as e: return mcp_error(str(e))
        # ── ORBITAL BRIDGE: delegar ações ──────────────────────────────────
        _orbital_result = None
        try:
            import importlib.util
            _spec = importlib.util.spec_from_file_location("orbital_bridge", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-139-orbital-bridge.py"))
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            _orbital_result = _mod.orbital_dispatch(action, root)
        except Exception:
            pass
        if _orbital_result is not None:
            return _orbital_result


        else:
            return mcp_error(f"action desconhecida: {action}",
                    suggestion=f"Ações disponíveis: config.get, config.set, pulse.status, etc.")
