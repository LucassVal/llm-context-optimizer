from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.045432'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TOOL-FR-011-pulse
related_ssot:
  - NC-TOOL-FR-005-config
  - NC-TOOL-FR-025-system
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-TOOL-FR-025-system.py
FR-025  MCP Tool: neocortex_system

Gerenciamento unificado de sistema, configurao e pulso do NeoCortex.
Absorve funcionalidades de NC-TOOL-FR-005-config.py e NC-TOOL-FR-011-pulse.py.
Aes disponveis:
  config.get              retorna config atual (neocortex_config.yaml) via get_config()
  config.reload           recarrega config sem reiniciar servidor
  config.diff             compara config atual vs config_dev (diferenas entre ambientes)
  config.set_model        define modelo LLM a ser usado
  config.list_models      lista modelos disponveis
  config.set_constraint   define restrio do sistema (key=constraint, value=novo_valor)
  config.list_constraints lista restries do sistema
  config.set_agent_backend  define backend LLM para uma role (key=role, value=backend_config JSON)
  system.diagnostics      coleta: verso Python, PYTHONPATH, memory usage, uptime servidor
  system.env_check        verifica variveis de ambiente obrigatrias (PYTHONUTF8, PYTHONPATH)
  pulse.status            retorna status do pulse_scheduler
  pulse.start             inicia o agendador do pulse
  pulse.stop              para o agendador do pulse
  pulse.schedule_custom   adiciona schedule customizado ao pulse
  pulse.force             fora execuo imediata de uma task do pulse (pruning, consolidation)
"""


import json
import logging
import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

_START_TIME = time.time()


def _config():
    try:
        from neocortex.config import get_config

        return get_config()
    except Exception:
        return None


def _get_config_service():
    try:
        from neocortex.core import get_config_service

        return get_config_service()
    except Exception:
        return None


def _get_pulse_scheduler():
    try:
        # type: ignore
        from neocortex.core import get_pulse_scheduler

        return get_pulse_scheduler()
    except Exception:
        return None


def _get_config_dev_path() -> Path:
    cfg = _config()
    if cfg:
        try:
            # Use project_root property; fallback to project_root attribute
            base = getattr(cfg, "project_root", getattr(cfg, "_project_root", None))
            if base is None:
                # If base is still None, try to get from PATHS
                if hasattr(cfg, "PATHS") and "project_root" in cfg.PATHS:
                    base = cfg.PATHS["project_root"]
                else:
                    return Path("neocortex_config_dev.yaml")
            base = Path(base)
            config_dir = base / "DIR-CFG-FR-001-config-main"
            dev_config = config_dir / "neocortex_config_dev.yaml"
            if dev_config.exists():
                return dev_config
        except Exception:
            pass
    return Path("neocortex_config_dev.yaml")


def register_tool(mcp) -> None:
    """Registra neocortex_system no servidor MCP."""

    @mcp.tool(name="neocortex_system")
    def neocortex_system(
        action: str,
        key: str = "",
        value: str = "",
        task_name: str = "",
        schedule_interval: int = 300,
    ) -> Dict[str, Any]:
        """Gerenciamento unificado de sistema, configurao e pulso do NeoCortex.

        Actions: config.get, config.reload, config.diff, config.set_model,
                 config.list_models, config.set_constraint, config.list_constraints,
                 config.set_agent_backend, system.diagnostics, system.env_check,
                 pulse.status, pulse.start, pulse.stop, pulse.schedule_custom, pulse.force"""

        #  config.get
        if action == "config.get":
            cfg = _config()
            if cfg is None:
                return {"success": False, "error": "ConfigProvider no disponvel."}
            try:
                config_dict = cfg.to_dict() if hasattr(cfg, "to_dict") else {}
                return {
                    "success": True,
                    "action": action,
                    "config": config_dict,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  config.reload
        elif action == "config.reload":
            cfg = _config()
            if cfg is None:
                return {"success": False, "error": "ConfigProvider no disponvel."}
            try:
                cfg.reload()
                return {
                    "success": True,
                    "action": action,
                    "message": "Configurao recarregada.",
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  config.diff
        elif action == "config.diff":
            import yaml

            cfg = _config()
            if cfg is None:
                return {"success": False, "error": "ConfigProvider no disponvel."}
            try:
                # Determine config file path
                config_path = None
                if hasattr(cfg, "config_path"):
                    config_path = Path(cfg.config_path)
                else:
                    # Try to locate neocortex_config.yaml in project root
                    base = getattr(
                        cfg, "project_root", getattr(cfg, "_project_root", None)
                    )
                    if (
                        base is None
                        and hasattr(cfg, "PATHS")
                        and "project_root" in cfg.PATHS
                    ):
                        base = cfg.PATHS["project_root"]
                    if base is not None:
                        config_path = Path(base) / "neocortex_config.yaml"
                    else:
                        config_path = Path("neocortex_config.yaml")
                # Ensure Path object
                config_path = Path(config_path)
                dev_config_path = _get_config_dev_path()
                if not dev_config_path.exists():
                    return {
                        "success": False,
                        "error": f"Config dev no encontrada: {dev_config_path}",
                    }
                with open(config_path, "r", encoding="utf-8") as f:
                    prod = yaml.safe_load(f) or {}
                with open(dev_config_path, "r", encoding="utf-8") as f:
                    dev = yaml.safe_load(f) or {}
                diff = {}
                all_keys = set(prod.keys()) | set(dev.keys())
                for k in all_keys:
                    if prod.get(k) != dev.get(k):
                        diff[k] = {"prod": prod.get(k), "dev": dev.get(k)}
                return {
                    "success": True,
                    "action": action,
                    "diff": diff,
                    "prod_file": str(config_path),
                    "dev_file": str(dev_config_path),
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  config.set_model
        elif action == "config.set_model":
            config_service = _get_config_service()
            if config_service is None:
                return {"success": False, "error": "ConfigService no disponvel."}
            if not key:
                return {"success": False, "error": "key (model name)  obrigatria."}
            try:
                result = config_service.set_model(key)
                return result
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  config.list_models
        elif action == "config.list_models":
            config_service = _get_config_service()
            if config_service is None:
                return {"success": False, "error": "ConfigService no disponvel."}
            try:
                result = config_service.list_available_models()
                return result
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  config.set_constraint
        elif action == "config.set_constraint":
            config_service = _get_config_service()
            if config_service is None:
                return {"success": False, "error": "ConfigService no disponvel."}
            if not key or not value:
                return {
                    "success": False,
                    "error": "key (constraint) e value so obrigatrios.",
                }
            try:
                # Tenta converter para int, depois float, mantm string se falhar
                try:
                    typed_value = int(value)
                except ValueError:
                    try:
                        typed_value = float(value)
                    except ValueError:
                        typed_value = value
                result = config_service.update_system_constraint(key, typed_value)
                return result
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  config.list_constraints
        elif action == "config.list_constraints":
            config_service = _get_config_service()
            if config_service is None:
                return {"success": False, "error": "ConfigService no disponvel."}
            try:
                result = config_service.get_constraint_summary()
                return result
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  config.set_agent_backend
        elif action == "config.set_agent_backend":
            if not key or not value:
                return {
                    "success": False,
                    "error": "key (role) e value (backend config JSON) so obrigatrios.",
                }
            cfg = _config()
            if cfg is None:
                return {"success": False, "error": "ConfigProvider no disponvel."}
            try:
                # Parse backend config from JSON string
                try:
                    backend_config = json.loads(value)
                except json.JSONDecodeError:
                    # If not JSON, treat as simple provider name
                    backend_config = {"provider": value}
                # Update configuration
                cfg.set(f"llm.agent_backends.{key}", backend_config)
                return {
                    "success": True,
                    "role": key,
                    "backend_config": backend_config,
                    "message": f"Backend configuration set for role '{key}'",
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  system.diagnostics
        elif action == "system.diagnostics":
            import psutil

            uptime_s = int(time.time() - _START_TIME)
            h, rem = divmod(uptime_s, 3600)
            m, s = divmod(rem, 60)
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "success": True,
                "action": action,
                "python_version": sys.version,
                "platform": platform.platform(),
                "pythonpath": sys.path,
                "uptime": f"{h:02d}:{m:02d}:{s:02d}",
                "uptime_seconds": uptime_s,
                "memory_rss_mb": memory_info.rss // 1024 // 1024,
                "memory_vms_mb": memory_info.vms // 1024 // 1024,
                "cpu_percent": process.cpu_percent(interval=0.1),
                "timestamp": datetime.now().isoformat(),
            }

        #  system.env_check
        elif action == "system.env_check":
            env_vars = {}
            env_vars["PYTHONUTF8"] = os.environ.get("PYTHONUTF8", "not set")
            env_vars["PYTHONPATH"] = os.environ.get("PYTHONPATH", "not set")
            env_vars["PYTHONIOENCODING"] = os.environ.get("PYTHONIOENCODING", "not set")
            issues = []
            if env_vars["PYTHONUTF8"] != "1":
                issues.append("PYTHONUTF8 should be '1' for UTF-8 support")
            if env_vars["PYTHONPATH"] == "not set":
                issues.append("PYTHONPATH not set (may affect module resolution)")
            return {
                "success": True,
                "action": action,
                "env_vars": env_vars,
                "issues": issues,
                "timestamp": datetime.now().isoformat(),
            }

        #  pulse.status
        elif action == "pulse.status":
            pulse = _get_pulse_scheduler()
            if pulse is None:
                return {"success": False, "error": "PulseScheduler no disponvel."}
            try:
                status = (
                    pulse.get_status()
                    if hasattr(pulse, "get_status")
                    else {"status": "unknown"}
                )
                return {
                    "success": True,
                    "action": action,
                    "status": status,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  pulse.start
        elif action == "pulse.start":
            pulse = _get_pulse_scheduler()
            if pulse is None:
                return {"success": False, "error": "PulseScheduler no disponvel."}
            try:
                pulse.start()
                return {
                    "success": True,
                    "action": action,
                    "message": "PulseScheduler iniciado.",
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  pulse.stop
        elif action == "pulse.stop":
            pulse = _get_pulse_scheduler()
            if pulse is None:
                return {"success": False, "error": "PulseScheduler no disponvel."}
            try:
                pulse.stop()
                return {
                    "success": True,
                    "action": action,
                    "message": "PulseScheduler parado.",
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  pulse.schedule_custom
        elif action == "pulse.schedule_custom":
            pulse = _get_pulse_scheduler()
            if pulse is None:
                return {"success": False, "error": "PulseScheduler no disponvel."}
            if not key:
                return {
                    "success": False,
                    "error": "Fornea 'key' com nome da task customizada.",
                }
            try:
                # Tenta adicionar schedule customizado
                # Assumindo que pulse tem mtodo add_custom_schedule
                if hasattr(pulse, "add_custom_schedule"):
                    pulse.add_custom_schedule(key, schedule_interval)
                    return {
                        "success": True,
                        "action": action,
                        "task_name": key,
                        "interval_seconds": schedule_interval,
                        "message": f"Schedule customizado '{key}' adicionado com intervalo {schedule_interval}s.",
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    return {
                        "success": False,
                        "error": "PulseScheduler no suporta schedules customizados.",
                    }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  pulse.force
        elif action == "pulse.force":
            pulse = _get_pulse_scheduler()
            if pulse is None:
                return {"success": False, "error": "PulseScheduler no disponvel."}
            if not task_name:
                return {
                    "success": False,
                    "error": "Fornea 'task_name' para forar execuo.",
                }
            try:
                if hasattr(pulse, "force_task"):
                    result = pulse.force_task(task_name)
                    return {
                        "success": True,
                        "action": action,
                        "task_name": task_name,
                        "result": result,
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    return {
                        "success": False,
                        "error": "PulseScheduler no suporta force_task.",
                    }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  ao desconhecida
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'.",
                "available": [
                    "config.get",
                    "config.reload",
                    "config.diff",
                    "config.set_model",
                    "config.list_models",
                    "config.set_constraint",
                    "config.list_constraints",
                    "config.set_agent_backend",
                    "system.diagnostics",
                    "system.env_check",
                    "pulse.status",
                    "pulse.start",
                    "pulse.stop",
                    "pulse.schedule_custom",
                    "pulse.force",
                ],
            }
