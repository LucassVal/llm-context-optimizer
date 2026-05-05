#!/usr/bin/env python3
"""---
NC-SUPER-005 — neocortex_llm_router
CORTE STJ — Roteamento LLM (Ollama local only — LiteLLM removed 2026-05-04)
---
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_llm_router"

_OLLAMA_BASE = "http://localhost:11434"

_TIER_MODEL = {
    "OPERACIONAL": "qwen-1.5b",
    "TECNICO": "deepseek-v4-flash",
    "RACIOCINIO": "deepseek-v4-pro",
    "SOBERANO": None,
}


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_llm_router(
        action: str,
        model: str = "",
        prompt: str = "",
        system: str = "",
        complexity: str = "OPERACIONAL",
        max_tokens: int = 512,
        timeout: int = 60,
        n_workers: int = 1,
        ollama_model: str = "qwen2.5-coder:1.5b",
    ) -> dict[str, Any]:
        """CORTE STJ — Roteamento LLM (Ollama local only).
        Actions: ollama.ask, ollama.list, ollama.pull, workers.spawn, workers.status
        Tiers: OPERACIONAL→qwen-1.5b | TECNICO→deepseek-v4-flash | RACIOCINIO→deepseek-v4-pro
        """
        if action == "ollama.ask":
            if not prompt:
                return {"success": False, "action": action, "error": "prompt obrigatório"}
            try:
                import requests
                r = requests.post(f"{_OLLAMA_BASE}/api/generate",
                                  json={"model": ollama_model, "prompt": prompt, "stream": False},
                                  timeout=timeout)
                data = r.json() if r.ok else {}
                return {"success": r.ok, "action": action, "model": ollama_model,
                        "response": data.get("response", ""), "done": data.get("done", False)}
            except Exception as e:
                return {"success": False, "error": str(e)}

        elif action == "ollama.list":
            try:
                import requests
                r = requests.get(f"{_OLLAMA_BASE}/api/tags", timeout=5)
                models = r.json().get("models", []) if r.ok else []
                return {"success": True, "action": action, "models": [m.get("name") for m in models],
                        "count": len(models), "ollama_online": r.ok}
            except Exception as e:
                return {"success": False, "error": str(e), "ollama_online": False}

        elif action == "ollama.pull":
            if not ollama_model:
                return {"success": False, "error": "ollama_model obrigatório"}
            try:
                import requests
                r = requests.post(f"{_OLLAMA_BASE}/api/pull",
                                  json={"name": ollama_model, "stream": False}, timeout=300)
                return {"success": r.ok, "action": action, "model": ollama_model,
                        "status": r.json().get("status") if r.ok else r.text}
            except Exception as e:
                return {"success": False, "error": str(e)}

        elif action == "workers.spawn":
            spawned = []
            for i in range(min(n_workers, 10)):
                try:
                    import requests
                    r = requests.post(f"{_OLLAMA_BASE}/api/generate",
                                      json={"model": "qwen2.5-coder:1.5b", "prompt": "ping", "stream": False},
                                      timeout=30)
                    spawned.append({"worker": i + 1, "ok": r.status_code == 200})
                except Exception as e:
                    spawned.append({"worker": i + 1, "ok": False, "error": str(e)})
            return {"success": True, "action": action, "n_workers": n_workers, "results": spawned,
                    "online": sum(1 for w in spawned if w.get("ok"))}

        elif action == "workers.status":
            try:
                import requests
                r = requests.get(f"{_OLLAMA_BASE}/api/tags", timeout=5)
                models = r.json().get("models", []) if r.ok else []
                return {"success": True, "action": action, "ollama_online": r.ok,
                        "models": [m.get("name") for m in models]}
            except Exception as e:
                return {"success": False, "error": str(e)}

        else:
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["ollama.ask", "ollama.list", "ollama.pull",
                                  "workers.spawn", "workers.status"]}
