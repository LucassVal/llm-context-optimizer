#!/usr/bin/env python3
"""
NeoCortex Pulse Tool

Ferramenta MCP para neocortex_pulse - controle do Pulse Scheduler.
"""

import json
from typing import Dict, Any

# O scheduler deve ser injetado ou acessado globalmente
_pulse_scheduler = None


def set_pulse_scheduler(scheduler):
    """Define a instância global do PulseScheduler."""
    global _pulse_scheduler
    _pulse_scheduler = scheduler


def register_tool(mcp):
    """
    Registra a ferramenta neocortex_pulse no servidor MCP.
    """

    @mcp.tool(name="neocortex_pulse")
    def tool_pulse(
        action: str,
        task_name: str = "",
    ) -> Dict[str, Any]:
        """
        Controle do Pulso Cognitivo.

        Actions:
        - status: Retorna o status atual do pulso
        - force: Força a execução de uma tarefa (pruning, consolidation, akl, backup, checkpoint)
        - start: Inicia o agendador
        - stop: Para o agendador
        """
        if not _pulse_scheduler:
            return {"success": False, "error": "PulseScheduler não inicializado."}

        if action == "status":
            return {"success": True, "status": _pulse_scheduler.get_status()}

        elif action == "force":
            if not task_name:
                return {
                    "success": False,
                    "error": "task_name é obrigatório para force.",
                }
            return _pulse_scheduler.force_task(task_name)

        elif action == "start":
            _pulse_scheduler.start()
            return {"success": True, "message": "PulseScheduler iniciado."}

        elif action == "stop":
            _pulse_scheduler.stop()
            return {"success": True, "message": "PulseScheduler parado."}

        else:
            return {"success": False, "error": f"Ação desconhecida: {action}"}

    return tool_pulse
