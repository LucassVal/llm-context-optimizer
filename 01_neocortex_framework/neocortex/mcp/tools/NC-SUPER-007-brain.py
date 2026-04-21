#!/usr/bin/env python3
"""
NC-SUPER-007 — neocortex_brain
CORTE STF — Inteligência Soberana

Funde: brain (000), intelligence (027).

Actions:
  brain.think, brain.plan, brain.critique, brain.orchestrate
  intelligence.query, intelligence.synthesize
"""
import logging
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_brain"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_brain(
        action: str,
        prompt: str = "",
        context: str = "",
        goal: str = "",
        complexity: str = "RACIOCINIO",
        mode: str = "analytical",
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """CORTE STF — Inteligência Soberana.
        Funde: brain (000) + intelligence (027).
        Actions: brain.think, brain.plan, brain.critique, brain.orchestrate,
                 intelligence.query, intelligence.synthesize
        Nota: T0 executa localmente sem delegar a LLM tier inferior.
        """
        ts = _ts()

        if not prompt and not goal:
            return {"success": False, "error": "prompt ou goal obrigatório", "timestamp": ts}

        def _call_llm(system_msg: str, user_msg: str) -> str:
            try:
                import requests
                headers = {"Authorization": "Bearer sk-my-master-key-123", "Content-Type": "application/json"}
                body = {
                    "model": "deepseek-chat",
                    "messages": [{"role": "system", "content": system_msg},
                                  {"role": "user", "content": user_msg}],
                    "max_tokens": max_tokens,
                }
                r = requests.post("http://localhost:4000/v1/chat/completions",
                                  headers=headers, json=body, timeout=60)
                if r.ok:
                    return r.json()["choices"][0]["message"]["content"]
                return f"[LLM indisponível: {r.status_code}]"
            except Exception as e:
                return f"[LLM erro: {e}]"

        if action == "brain.think":
            system = ("Você é o núcleo de raciocínio do NeoCortex (STF). "
                      "Analise profundamente o que foi pedido e forneça insights estratégicos.")
            response = _call_llm(system, f"Contexto: {context}\n\nPergunta: {prompt}")
            return {"success": True, "action": action, "thinking": response,
                    "complexity": complexity, "timestamp": ts}

        elif action == "brain.plan":
            system = ("Você é o planejador estratégico do NeoCortex (STF). "
                      "Crie um plano de ação detalhado e priorizado.")
            user_msg = f"Goal: {goal or prompt}\nContext: {context}"
            response = _call_llm(system, user_msg)
            return {"success": True, "action": action, "plan": response,
                    "goal": goal or prompt, "timestamp": ts}

        elif action == "brain.critique":
            system = ("Você é o revisor crítico do NeoCortex (STF). "
                      "Identifique falhas, riscos e aponte melhorias. Seja direto.")
            response = _call_llm(system, f"Revisar: {prompt}\nContexto: {context}")
            return {"success": True, "action": action, "critique": response, "timestamp": ts}

        elif action == "brain.orchestrate":
            system = ("Você é o orquestrador do NeoCortex (STF). "
                      "Divida a tarefa em sub-tarefas delegáveis a agentes T1/T2/T3.")
            response = _call_llm(system, f"Tarefa: {goal or prompt}\nContexto: {context}")
            return {"success": True, "action": action, "orchestration": response,
                    "mode": mode, "timestamp": ts}

        elif action == "intelligence.query":
            system = "Você é o sistema de inteligência do NeoCortex. Responda com precisão técnica."
            response = _call_llm(system, prompt)
            return {"success": True, "action": action, "response": response, "timestamp": ts}

        elif action == "intelligence.synthesize":
            system = ("Você é o sintetizador de conhecimento do NeoCortex. "
                      "Combine as informações fornecidas em uma síntese coerente e acionável.")
            response = _call_llm(system, f"Sintetize: {prompt}\n\nContexto: {context}")
            return {"success": True, "action": action, "synthesis": response, "timestamp": ts}


        elif action == "brain.feedback":
            if not content:
                return {"success": False, "error": "content (feedback) obrigatorio", "timestamp": ts}
            try:
                from neocortex.core import get_ledger_service
                svc = get_ledger_service()
                ledger = svc.read_ledger() if hasattr(svc, "read_ledger") else {}
                fb_list = ledger.get("brain_feedback", [])
                fb_list.append({"ts": ts, "feedback": content})
                if hasattr(svc, "update_ledger"):
                    svc.update_ledger({"brain_feedback": fb_list[-50:]})
                return {"success": True, "action": action, "stored": True, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}
        else:
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["brain.think", "brain.plan", "brain.critique", "brain.orchestrate",
                                  "intelligence.query", "intelligence.synthesize"],
                    "timestamp": ts}
