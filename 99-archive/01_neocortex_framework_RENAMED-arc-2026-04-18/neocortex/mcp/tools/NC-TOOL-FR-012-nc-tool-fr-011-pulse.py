"""---
domain: "orchestration"
layer: "core"
type: "service"
tags: ["tool", "011", "pulse"]
hash: "auto-generated"
---"""
#!/usr/bin/env python3
"""
NeoCortex Pulse Tool

Ferramenta MCP para neocortex_pulse - controle do Pulse Scheduler.
"""

from typing import Any, Dict

# O scheduler deve ser injetado ou acessado globalmente
_pulse_scheduler = None


def set_pulse_scheduler(scheduler):
    """Define a instncia global do PulseScheduler."""
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
        - force: Fora a execuo de uma tarefa (pruning, consolidation, akl, backup, checkpoint)
        - start: Inicia o agendador
        - stop: Para o agendador
        """
        if not _pulse_scheduler:
            return {"success": False, "error": "PulseScheduler no inicializado."}

        if action == "status":
            return {"success": True, "status": _pulse_scheduler.get_status()}

        elif action == "force":
            if not task_name:
                return {
                    "success": False,
                    "error": "task_name  obrigatrio para force.",
                }
            return _pulse_scheduler.force_task(task_name)

        elif action == "start":
            _pulse_scheduler.start()
            return {"success": True, "message": "PulseScheduler iniciado."}

        elif action == "stop":
            _pulse_scheduler.stop()
            return {"success": True, "message": "PulseScheduler parado."}

        else:
            return {"success": False, "error": f"Ao desconhecida: {action}"}

    return tool_pulse
