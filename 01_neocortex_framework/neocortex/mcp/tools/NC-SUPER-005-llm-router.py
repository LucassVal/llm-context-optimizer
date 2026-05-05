#!/usr/bin/env python3
"""---
NC-SUPER-005 — neocortex_llm_router
---
"""

"""---
NC-SUPER-005 — neocortex_llm_router
---
"""

"""
NC-SUPER-005 — neocortex_llm_router
CORTE STJ — Roteamento LLM

Funde: litellm (043), local-llm (042).

Actions:
  gateway.health, gateway.start, gateway.stop, gateway.models
  route.call  (routing tier → modelo)
  ollama.ask, ollama.list, ollama.pull
  budget.status
  workers.spawn, workers.status
"""
import logging
import subprocess
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_llm_router"

_LITELLM_BASE = "http://localhost:4000"
_LITELLM_KEY = "sk-my-master-key-123"
_OLLAMA_BASE = "http://localhost:11434"
_CONFIG_PATH = Path(__file__).parents[5] / "config.yaml"

_HEADERS = {"Authorization": f"Bearer {_LITELLM_KEY}", "Content-Type": "application/json"}

_TIER_MODEL = {
    "OPERACIONAL": "qwen-1.5b",
    "TECNICO": "deepseek-v4-flash",
    "RACIOCINIO": "deepseek-v4-pro",
    "SOBERANO": None,
}

_litellm_proc = None


def _get(path: str, timeout: int = 5) -> dict:
    try:
        import requests
        r = requests.get(f"{_LITELLM_BASE}{path}", headers=_HEADERS, timeout=timeout)
        return {"ok": r.status_code == 200, "status": r.status_code,
                "data": r.json() if r.content else {}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _post(path: str, body: dict, timeout: int = 60) -> dict:
    try:
        import requests
        r = requests.post(f"{_LITELLM_BASE}{path}", headers=_HEADERS, json=body, timeout=timeout)
        return {"ok": r.status_code in (200, 201), "status": r.status_code,
                "data": r.json() if r.content else {}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


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
        """CORTE STJ — Roteamento LLM.
        Funde: litellm (043) + local-llm (042).
        Actions: gateway.health, gateway.start, gateway.stop, gateway.models,
                 route.call, ollama.ask, ollama.list, ollama.pull,
                 budget.status, workers.spawn, workers.status
        Tiers: OPERACIONAL→qwen-1.5b | TECNICO→deepseek-v4-flash | RACIOCINIO→deepseek-v4-pro
        """
        global _litellm_proc

        if action == "gateway.health":
            result = _get("/health")
            models_result = _get("/v1/models")
            models = []
            if models_result.get("ok") and "data" in models_result:
                models = [m.get("id") for m in models_result["data"].get("data", [])]
            return {"success": True, "action": action, "gateway_online": result.get("ok", False),
                    "endpoint": _LITELLM_BASE, "models_available": models,
                    "error": result.get("error")}

        elif action == "gateway.models":
            result = _get("/v1/models")
            if not result.get("ok"):
                return {"success": False, "action": action, "error": result.get("error", "Gateway offline")}
            models = result["data"].get("data", [])
            return {"success": True, "action": action, "models": [{"id": m["id"]} for m in models],
                    "count": len(models)}

        elif action == "gateway.start":
            health = _get("/health")
            if health.get("ok"):
                return {"success": True, "action": action, "status": "already_running", "endpoint": _LITELLM_BASE}
            if not _CONFIG_PATH.exists():
                return {"success": False, "action": action, "error": f"config.yaml não encontrado: {_CONFIG_PATH}"}
            try:
                _litellm_proc = subprocess.Popen(
                    ["litellm", "--config", str(_CONFIG_PATH), "--port", "4000"],
                    cwd=str(_CONFIG_PATH.parent), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                time.sleep(3)
                health2 = _get("/health")
                return {"success": health2.get("ok", False), "action": action, "pid": _litellm_proc.pid,
                        "status": "started" if health2.get("ok") else "started_not_responding",
                        "endpoint": _LITELLM_BASE}
            except FileNotFoundError:
                return {"success": False, "action": action, "error": "litellm não encontrado. pip install litellm"}

        elif action == "gateway.stop":
            if _litellm_proc is not None and _litellm_proc.poll() is None:
                _litellm_proc.terminate()
                _litellm_proc = None
                return {"success": True, "action": action, "status": "stopped"}
            return {"success": True, "action": action, "status": "not_running_by_mcp"}

        elif action == "route.call":
            target_model = model or _TIER_MODEL.get(complexity.upper(), "deepseek-v4-flash")
            if not target_model:
                return {"success": False, "action": action, "error": "Tier SOBERANO não delega — T0 executa diretamente"}
            if not prompt:
                return {"success": False, "action": action, "error": "prompt obrigatório para route.call"}

            cache_prompt = f"{system}\n---\n{prompt}" if system else prompt
            try:
                import importlib.util as _iu
                _cache_path = Path(__file__).parent.parent.parent / "core" / "NC-CORE-FR-174-response-cache.py"
                _spec = _iu.spec_from_file_location("response_cache", str(_cache_path))
                _mod = _iu.module_from_spec(_spec)
                _spec.loader.exec_module(_mod)
                cache = _mod.get_response_cache()
                cached = cache.query(cache_prompt, tool_name="llm_router")
                if cached is not None:
                    cached["_cache_source"] = "semantic"
                    return cached
            except Exception:
                pass

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            body = {"model": target_model, "messages": messages, "max_tokens": max_tokens}
            result = _post("/v1/chat/completions", body, timeout=timeout)
            if not result.get("ok"):
                return {"success": False, "action": action, "model": target_model,
                        "error": result.get("error"), "http_status": result.get("status")}
            content_out = result["data"].get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = result["data"].get("usage", {})
            response = {"success": True, "action": action, "model": target_model, "tier": complexity,
                        "content": content_out, "tokens_used": usage.get("total_tokens", 0)}

            try:
                import importlib.util as _iu2
                _cache_path2 = Path(__file__).parent.parent.parent / "core" / "NC-CORE-FR-174-response-cache.py"
                _spec2 = _iu2.spec_from_file_location("response_cache_w", str(_cache_path2))
                _mod2 = _iu2.module_from_spec(_spec2)
                _spec2.loader.exec_module(_mod2)
                cache2 = _mod2.get_response_cache()
                cache2.store(cache_prompt, response, tool_name="llm_router")
            except Exception:
                pass

            return response

        elif action == "ollama.ask":
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

        elif action == "budget.status":
            result = _get("/spend")
            if not result.get("ok"):
                return {"success": False, "action": action, "error": result.get("error", "Gateway offline")}
            return {"success": True, "action": action, "spend_data": result.get("data", {})}

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
                    "available": ["gateway.health", "gateway.start", "gateway.stop", "gateway.models",
                                  "route.call", "ollama.ask", "ollama.list", "ollama.pull",
                                  "budget.status", "workers.spawn", "workers.status"]}
