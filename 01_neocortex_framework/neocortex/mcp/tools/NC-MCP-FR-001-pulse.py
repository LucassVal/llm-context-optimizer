#!/usr/bin/env python3
"""---
NC-MCP-FR-001 — neocortex_pulse_bridge
Compatibilidade — use neocortex_system para ações de pulse

WHAT: Compatibility shim exposing a single 'status' action that returns
      pulse scheduler running state and task list. Auto-starts Guardian
      Daemon (NC-SCR-FR-115) upon scheduler registration via server.py.
WHY: Satisfy hard server.py import dependency (from .tools import pulse /
     pulse.set_pulse_scheduler()) without duplicating full pulse action set
     already in NC-SUPER-006-system. Exists for backward compatibility with
     locked server.py boot sequence.
WHERE: Registered as 'neocortex_pulse_bridge' — NOT intended for direct
       agent use. Agents should call neocortex_system for full pulse control.

Actions: status
---"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
root = Path(__file__).parents[4]

# Referência global ao scheduler (populada pelo server.py no boot)
_scheduler = None


def set_pulse_scheduler(scheduler) -> None:
    """Chamado pelo server.py após criar o PulseScheduler.
    Também inicia o Guardian Daemon (COG-001) automaticamente.
    """
    global _scheduler
    _scheduler = scheduler
    logger.info("[pulse bridge] PulseScheduler registrado com sucesso")

    # ── Auto-start Guardian Daemon ─────────────────────────────────────────────
    try:
        import importlib.util
        from pathlib import Path
        fw_dir = Path(__file__).parents[2]
        script = fw_dir / "scripts" / "NC-SCR-FR-115-guardian-daemon.py"
        if script.exists():
            spec = importlib.util.spec_from_file_location("guardian_daemon", script)
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            result = mod.start_guardian(interval=60)
            logger.info(f"[pulse bridge] 🚀 Guardian Daemon iniciado — session={result.get('session_id')} | interval=60s")
        else:
            logger.warning(f"[pulse bridge] Guardian script não encontrado: {script}")
    except Exception as e:
        logger.error(f"[pulse bridge] Guardian auto-start falhou (não crítico): {e}")
    # ── fim auto-start ─────────────────────────────────────────────────────────


def get_pulse_scheduler():
    return _scheduler


def register_tool(mcp) -> None:
    """
    Bridge register_tool — delega ao NC-SUPER-006-system para evitar duplicata.
    O FastMCP só registra o nome 'neocortex_pulse_bridge' aqui para não conflitar
    com neocortex_system que já expõe pulse.status e pulse.schedule_custom.
    """
    @mcp.tool(name="neocortex_pulse_bridge")
    def neocortex_pulse_bridge(action: str = "status") -> dict[str, Any]:
        """Bridge de compatibilidade — use neocortex_system para ações de pulse.
        Actions: status
        """
        ts = datetime.now().isoformat(timespec="seconds")
        try:
            from neocortex.core.utils.gateway_bridge import gateway_check
            _ok, _report = gateway_check(action, root)
            if not _ok: return _report
        except Exception: pass

        if _scheduler is None:
            return {"success": False, "error": "PulseScheduler não inicializado", "timestamp": ts}
        running = _scheduler.is_running() if hasattr(_scheduler, "is_running") else True
        tasks = _scheduler.list_tasks() if hasattr(_scheduler, "list_tasks") else []
        return {
            "success": True, "action": action,
            "running": running, "tasks": tasks,
            "note": "Use neocortex_system(action='pulse.status') para funcionalidade completa",
            "timestamp": ts,
        }
