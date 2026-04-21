#!/usr/bin/env python3
"""
pulse.py — Bridge module (obrigatório pelo server.py locked)

server.py linha 384 faz: from .tools import pulse
server.py linha 386 faz: pulse.set_pulse_scheduler(pulse_scheduler)

Este módulo bridge preserva essa interface sem duplicar a tool.
A lógica de pulse actions está em NC-SUPER-006-system.py.
"""
import logging
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)

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
    def neocortex_pulse_bridge(action: str = "status") -> Dict[str, Any]:
        """Bridge de compatibilidade — use neocortex_system para ações de pulse.
        Actions: status
        """
        ts = datetime.now().isoformat(timespec="seconds")
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
