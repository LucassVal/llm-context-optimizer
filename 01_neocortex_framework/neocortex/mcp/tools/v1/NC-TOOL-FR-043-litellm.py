"""---
title: NC-TOOL-FR-043-litellm
version: v1.0
created: 2026-04-18
tags: litellm, gateway, llm-routing, workers, budget
---"""
#!/usr/bin/env python3
"""
NC-TOOL-FR-043 — neocortex_litellm
MCP tool: gerencia o LiteLLM gateway :4000 (modelos, saude, budget, workers).
"""

import logging
import subprocess
import time
from pathlib import Path
from typing import Any, Dict

import requests

logger = logging.getLogger(__name__)

_LITELLM_BASE = "http://localhost:4000"
_LITELLM_KEY = "sk-my-master-key-123"
_OLLAMA_BASE = "http://localhost:11434"
_CONFIG_PATH = Path(__file__).parents[5] / "config.yaml"

_HEADERS = {
    "Authorization": f"Bearer {_LITELLM_KEY}",
    "Content-Type": "application/json",
}

# Mapa de complexidade -> modelo LiteLLM
_TIER_MODEL = {
    "OPERACIONAL": "qwen-1.5b",
    "TECNICO":     "deepseek-chat",
    "RACIOCINIO":  "deepseek-reasoner",
    "SOBERANO":    None,
}

# Processo LiteLLM gerenciado pelo MCP
_litellm_proc = None


def _get(path: str, timeout: int = 5) -> Dict:
    try:
        r = requests.get(f"{_LITELLM_BASE}{path}", headers=_HEADERS, timeout=timeout)
        return {"ok": r.status_code == 200, "status": r.status_code, "data": r.json() if r.content else {}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _post(path: str, body: dict, timeout: int = 60) -> Dict:
    try:
        r = requests.post(f"{_LITELLM_BASE}{path}", headers=_HEADERS, json=body, timeout=timeout)
        return {"ok": r.status_code in (200, 201), "status": r.status_code, "data": r.json() if r.content else {}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def register_tool(mcp):
    """Register neocortex_litellm tool on MCP server."""

    @mcp.tool(name="neocortex_litellm")
    def tool_litellm(
        action: str,
        model: str = "",
        prompt: str = "",
        system: str = "",
        complexity: str = "OPERACIONAL",
        n_workers: int = 1,
        max_tokens: int = 512,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """Gerencia LiteLLM gateway :4000 — modelos, saude, budget e worker pool.

        Actions: gateway.health, gateway.models, gateway.start, gateway.stop,
                 route.call, budget.status, workers.spawn
        Tiers: OPERACIONAL->qwen-1.5b | TECNICO->deepseek-chat | RACIOCINIO->deepseek-reasoner
        """
        global _litellm_proc

        # gateway.health
        if action == "gateway.health":
            result = _get("/health")
            models_result = _get("/v1/models")
            models = []
            if models_result.get("ok") and "data" in models_result:
                models = [m.get("id") for m in models_result["data"].get("data", [])]
            return {
                "success": True,
                "action": action,
                "gateway_online": result.get("ok", False),
                "endpoint": _LITELLM_BASE,
                "models_available": models,
                "error": result.get("error"),
            }

        # gateway.models
        if action == "gateway.models":
            result = _get("/v1/models")
            if not result.get("ok"):
                return {"success": False, "action": action, "error": result.get("error", "Gateway offline")}
            models = result["data"].get("data", [])
            return {
                "success": True,
                "action": action,
                "models": [{"id": m["id"]} for m in models],
                "count": len(models),
            }

        # gateway.start
        if action == "gateway.start":
            health = _get("/health")
            if health.get("ok"):
                return {"success": True, "action": action, "status": "already_running", "endpoint": _LITELLM_BASE}
            if not _CONFIG_PATH.exists():
                return {"success": False, "action": action, "error": f"config.yaml nao encontrado: {_CONFIG_PATH}"}
            try:
                _litellm_proc = subprocess.Popen(
                    ["litellm", "--config", str(_CONFIG_PATH), "--port", "4000"],
                    cwd=str(_CONFIG_PATH.parent),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(3)
                health2 = _get("/health")
                return {
                    "success": health2.get("ok", False),
                    "action": action,
                    "pid": _litellm_proc.pid,
                    "status": "started" if health2.get("ok") else "started_not_responding",
                    "endpoint": _LITELLM_BASE,
                }
            except FileNotFoundError:
                return {"success": False, "action": action, "error": "litellm nao encontrado no PATH. pip install litellm"}

        # gateway.stop
        if action == "gateway.stop":
            if _litellm_proc is not None and _litellm_proc.poll() is None:
                _litellm_proc.terminate()
                _litellm_proc = None
                return {"success": True, "action": action, "status": "stopped"}
            return {"success": True, "action": action, "status": "not_running_by_mcp"}

        # route.call
        if action == "route.call":
            target_model = model or _TIER_MODEL.get(complexity.upper(), "deepseek-chat")
            if not target_model:
                return {"success": False, "action": action, "error": "Tier SOBERANO nao delega — T0 executa diretamente"}
            if not prompt:
                return {"success": False, "action": action, "error": "prompt e obrigatorio para route.call"}
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            body = {"model": target_model, "messages": messages, "max_tokens": max_tokens}
            result = _post("/v1/chat/completions", body, timeout=timeout)
            if not result.get("ok"):
                return {"success": False, "action": action, "model": target_model, "error": result.get("error")}
            content = result["data"].get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = result["data"].get("usage", {})
            return {
                "success": True,
                "action": action,
                "model": target_model,
                "tier": complexity,
                "content": content,
                "tokens_used": usage.get("total_tokens", 0),
            }

        # budget.status
        if action == "budget.status":
            result = _get("/spend")
            if not result.get("ok"):
                return {"success": False, "action": action, "error": result.get("error", "Gateway offline")}
            return {"success": True, "action": action, "spend_data": result.get("data", {})}

        # workers.spawn
        if action == "workers.spawn":
            spawned = []
            for i in range(n_workers):
                try:
                    r = requests.post(
                        f"{_OLLAMA_BASE}/api/generate",
                        json={"model": "qwen2.5-coder:1.5b", "prompt": "ping", "stream": False},
                        timeout=30,
                    )
                    spawned.append({"worker": i + 1, "ok": r.status_code == 200})
                except Exception as e:
                    spawned.append({"worker": i + 1, "ok": False, "error": str(e)})
            return {
                "success": True,
                "action": action,
                "n_workers": n_workers,
                "results": spawned,
                "online": sum(1 for w in spawned if w["ok"]),
            }

        return {
            "success": False,
            "error": (
                f"Action desconhecida: {action}. "
                "Disponiveis: gateway.health, gateway.models, gateway.start, "
                "gateway.stop, route.call, budget.status, workers.spawn"
            ),
        }
