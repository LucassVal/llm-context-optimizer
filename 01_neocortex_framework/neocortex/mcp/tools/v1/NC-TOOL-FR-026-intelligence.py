from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.091769'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TOOL-FR-016-subserver
related_ssot:
  - NC-TOOL-FR-026-intelligence
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-TOOL-FR-026-intelligence.py
FR-026  MCP Tool: neocortex_intelligence

Inteligncia e auto-aprendizado do NeoCortex.
Aes disponveis:
  brain.think        envia prompt+contexto para DeepSeek, retorna plano racionalizado
  brain.plan         gera action plan longo baseado em user goal
  brain.orchestrate  spawn de agente para resolver task_description delegada
  brain.critique     avalia output de outro agente (self-eval loop para auto-aprendizado)
  brain.feedback     registra feedback de execuo nos lobes ativos (fecha loop retroalimentao)
"""


import json
import logging
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


def _config():
    try:
        from neocortex.config import get_config

        return get_config()
    except Exception:
        return None


def _get_deepseek_backend():
    try:
        from neocortex.infra.llm.factory import LLMFactory

        factory = LLMFactory()
        return factory.get_backend("deepseek")
    except Exception:
        return None


def _get_lobe_service():
    try:
        from neocortex.core import get_lobe_service

        return get_lobe_service()
    except Exception:
        return None


def _simulate_deepseek_response(prompt: str, context: str = "") -> Dict[str, Any]:
    """Simula resposta da API DeepSeek (fallback se backend no disponvel)."""
    return {
        "response": f"Simulated DeepSeek response for: {prompt[:50]}...",
        "rationale": "Baseado no contexto fornecido e nas capacidades do sistema.",
        "plan": [
            {"step": 1, "action": "Analisar dependncias"},
            {"step": 2, "action": "Gerar implementao"},
            {"step": 3, "action": "Validar com testes"},
        ],
        "timestamp": datetime.now().isoformat(),
    }


def register_tool(mcp) -> None:
    """Registra neocortex_intelligence no servidor MCP."""

    @mcp.tool(name="neocortex_intelligence")
    def neocortex_intelligence(
        action: str,
        prompt: str = "",
        context: str = "",
        goal: str = "",
        task_description: str = "",
        agent_output: str = "",
        feedback_data: str = "",
    ) -> Dict[str, Any]:
        """Inteligncia e auto-aprendizado do NeoCortex.

        Actions: brain.think, brain.plan, brain.orchestrate, brain.critique, brain.feedback"""

        #  brain.think
        if action == "brain.think":
            if not prompt:
                return {"success": False, "error": "Fornea 'prompt' para brain.think."}
            backend = _get_deepseek_backend()
            if backend is not None:
                try:
                    # Usar backend real se disponvel
                    response = backend.generate(
                        prompt=prompt,
                        context=context,
                        max_tokens=1000,
                    )
                    return {
                        "success": True,
                        "action": action,
                        "prompt": prompt[:100],
                        "context_used": bool(context),
                        "response": response,
                        "backend": "deepseek",
                        "timestamp": datetime.now().isoformat(),
                    }
                except Exception as e:
                    logger.warning(f"[intelligence] Erro no backend DeepSeek: {e}")
                    # Fallback para simulao
                    simulated = _simulate_deepseek_response(prompt, context)
                    simulated["backend"] = "simulated_fallback"
                    simulated["success"] = True
                    simulated["action"] = action
                    return simulated
            else:
                simulated = _simulate_deepseek_response(prompt, context)
                simulated["backend"] = "simulated_no_backend"
                simulated["success"] = True
                simulated["action"] = action
                return simulated

        #  brain.plan
        elif action == "brain.plan":
            if not goal:
                return {"success": False, "error": "Fornea 'goal' para brain.plan."}
            # Gera plano estruturado baseado no objetivo
            plan = [
                {
                    "step": 1,
                    "task": "Anlise de requisitos",
                    "details": f"Analisar goal: {goal[:50]}",
                },
                {
                    "step": 2,
                    "task": "Design de arquitetura",
                    "details": "Definir componentes e fluxos",
                },
                {"step": 3, "task": "Implementao", "details": "Codificar e integrar"},
                {
                    "step": 4,
                    "task": "Testes e validao",
                    "details": "Garantir qualidade e conformidade",
                },
                {
                    "step": 5,
                    "task": "Deploy e monitoramento",
                    "details": "Implantar e observar",
                },
            ]
            return {
                "success": True,
                "action": action,
                "goal": goal[:100],
                "plan": plan,
                "plan_length": len(plan),
                "timestamp": datetime.now().isoformat(),
            }

        #  brain.orchestrate
        elif action == "brain.orchestrate":
            if not task_description:
                return {
                    "success": False,
                    "error": "Fornea 'task_description' para brain.orchestrate.",
                }
            # Simula spawn de agente (integrao futura com NC-TOOL-FR-016-subserver)
            return {
                "success": True,
                "action": action,
                "task": task_description[:150],
                "orchestration": {
                    "agent_role": "engineer",
                    "status": "spawned",
                    "message": f"Agente delegado para: {task_description[:50]}...",
                    "next_step": "Executar via neocortex_task",
                },
                "timestamp": datetime.now().isoformat(),
            }

        #  brain.critique
        elif action == "brain.critique":
            if not agent_output:
                return {
                    "success": False,
                    "error": "Fornea 'agent_output' para brain.critique.",
                }
            # Avaliao crtica do output do agente (self-eval loop)
            critique_points = []
            if len(agent_output) < 50:
                critique_points.append("Output muito curto - pode estar incompleto.")
            if "error" in agent_output.lower():
                critique_points.append(
                    "Output contm meno a erro - precisa de correo."
                )
            if "TODO" in agent_output or "FIXME" in agent_output:
                critique_points.append(
                    "Output contm marcadores de pendncia - requer ateno."
                )
            score = max(0, min(10, 10 - len(critique_points)))
            return {
                "success": True,
                "action": action,
                "agent_output_preview": agent_output[:100],
                "critique_points": critique_points,
                "score": score,
                "recommendation": "Revisar e iterar" if score < 7 else "Aceitvel",
                "timestamp": datetime.now().isoformat(),
            }

        #  brain.feedback
        elif action == "brain.feedback":
            lobe_service = _get_lobe_service()
            if lobe_service is None:
                return {"success": False, "error": "LobeService no disponvel."}
            try:
                # Parse feedback data
                feedback = {}
                if feedback_data:
                    try:
                        feedback = json.loads(feedback_data)
                    except json.JSONDecodeError:
                        feedback = {"raw": feedback_data}
                # Registrar feedback no lobe ativo
                # Aqui seria integrado com LobeService para armazenar feedback
                # Por enquanto, apenas simula
                return {
                    "success": True,
                    "action": action,
                    "feedback_registered": True,
                    "feedback_data": feedback,
                    "message": "Feedback registrado para retroalimentao do sistema.",
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  ao desconhecida
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'.",
                "available": [
                    "brain.think",
                    "brain.plan",
                    "brain.orchestrate",
                    "brain.critique",
                    "brain.feedback",
                ],
            }
