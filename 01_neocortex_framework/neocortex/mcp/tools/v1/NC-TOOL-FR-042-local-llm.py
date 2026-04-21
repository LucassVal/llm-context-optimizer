from __future__ import annotations

"""---
_genealogy:
  injected_at: '2026-04-18T10:35:00.000000'
  injected_by: T0-Antigravity
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TOOL-FR-042-local-llm
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
  - llm
  - ollama
---"""
"""
NC-TOOL-FR-042-local-llm.py
FR-042  MCP Tool: neocortex_local_llm

Bridge direta MCP ↔ Ollama + Router de Complexidade por Esfera.

Conexões disponíveis:
  ollama.list        lista modelos disponíveis (ollama list)
  ollama.ask         chama modelo local via HTTP POST localhost:11434
  ollama.status      verifica se Ollama está ativo + modelo carregado
  ollama.load        pré-carrega modelo na VRAM (keepalive)
  ollama.run_cmd     executa via subprocess (ollama run) com timeout
  llm.route          router automático por complexidade — escolhe o modelo certo
  llm.audit          auditoria de governança roteada pelo nível (Fórum/TJ/STJ/STF)

Roteamento por complexidade:
  OPERACIONAL  → Qwen 1.5b local (Fórum) — checks mecânicos, 24/7 iGPU
  TÉCNICO      → Qwen 3b local (TJ)       — análise de domínio, on-demand
  RACIOCÍNIO   → DeepSeek R1 via API      — constitucional, esporádico
  SOBERANO     → Antigravity/T0           — orquestra, nunca executa tarefas

Hook integration:
  PostToolUse → llm.audit automático após tools críticas de governança
"""

import json
import logging
import subprocess
import urllib.error
import urllib.request
from typing import Any, Dict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuração de modelos por complexidade
# ---------------------------------------------------------------------------

OLLAMA_BASE = "http://localhost:11434"

COMPLEXITY_MAP = {
    "OPERACIONAL": {
        "model": "qwen2.5-coder:1.5b-instruct",
        "backend": "ollama",
        "description": "Fórum — checks mecânicos 24/7 iGPU",
        "max_tokens": 512,
        "use_for": ["compile_check", "naming_audit", "orphan_check", "yaml_lint"],
    },
    "TECNICO": {
        "model": "qwen2.5-coder:3b-instruct",
        "backend": "ollama",
        "description": "TJ — análise de domínio on-demand",
        "max_tokens": 1024,
        "use_for": ["compliance_rules", "yaml_analysis", "lobe_review", "ticket_analysis"],
    },
    "RACIOCINIO": {
        "model": "deepseek-reasoner",
        "backend": "picoclaw",
        "description": "STJ/STF — raciocínio constitucional via API",
        "max_tokens": 4096,
        "use_for": ["constitutional_check", "multi_rule_conflict", "precedent_reasoning"],
        "endpoint": "http://localhost:18790/message",
    },
    "SOBERANO": {
        "model": "antigravity",
        "backend": "t0",
        "description": "T0 — orquestra, decide, veta. Nunca executa tarefas.",
        "max_tokens": 0,
        "use_for": ["veto", "emend_cf", "approve_handoff"],
    },
}

# Mapeamento de domínio → complexidade default
DOMAIN_COMPLEXITY = {
    "compile": "OPERACIONAL",
    "naming": "OPERACIONAL",
    "orphan": "OPERACIONAL",
    "yaml_lint": "OPERACIONAL",
    "compliance_rules": "TECNICO",
    "ticket_analysis": "TECNICO",
    "lobe_review": "TECNICO",
    "constitutional": "RACIOCINIO",
    "precedent": "RACIOCINIO",
    "multi_rule": "RACIOCINIO",
}


# ---------------------------------------------------------------------------
# Helpers — Ollama HTTP direto
# ---------------------------------------------------------------------------

def _ollama_is_up() -> bool:
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE}/api/tags")
        with urllib.request.urlopen(req, timeout=3):
            return True
    except Exception:
        return False


def _ollama_list() -> list:
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            return [m["name"] for m in data.get("models", [])]
    except Exception as e:
        return [f"ERROR: {e}"]


def _ollama_ask(model: str, prompt: str, system: str = "", max_tokens: int = 512) -> Dict[str, Any]:
    """POST direto à API do Ollama — sem PicoClaw, sem intermediário."""
    if not _ollama_is_up():
        return {"success": False, "error": "Ollama não está rodando em localhost:11434"}

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"num_predict": max_tokens},
    }).encode()

    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        content = result.get("message", {}).get("content", "")
        return {
            "success": True,
            "model": model,
            "response": content,
            "eval_count": result.get("eval_count", 0),
            "eval_duration_ms": round(result.get("eval_duration", 0) / 1e6, 1),
            "backend": "ollama_direct",
        }
    except Exception as e:
        return {"success": False, "error": str(e), "model": model}


def _ollama_load(model: str) -> Dict[str, Any]:
    """Pré-carrega modelo na VRAM via keep_alive longo."""
    payload = json.dumps({"model": model, "keep_alive": "24h"}).encode()
    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30):
            pass
        return {"success": True, "model": model, "status": "loaded_24h_keepalive"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _ollama_run_cmd(model: str, prompt: str, timeout: int = 30) -> Dict[str, Any]:
    """Fallback via command line — `ollama run model prompt`."""
    try:
        r = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, text=True, timeout=timeout
        )
        return {
            "success": r.returncode == 0,
            "response": r.stdout.strip(),
            "error": r.stderr.strip() or None,
            "backend": "ollama_cli",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Timeout após {timeout}s"}
    except FileNotFoundError:
        return {"success": False, "error": "ollama não encontrado no PATH"}


def _deepseek_api_ask(prompt: str, system: str = "") -> Dict[str, Any]:
    """
    Chama DeepSeek R1 diretamente via API REST.
    Fallback chain: DeepSeek API → PicoClaw proxy → Qwen 3b (degraded).
    PicoClaw é dispatcher de tasks, não gateway da API.
    """
    # Tentativa 1: DeepSeek API direta
    try:
        from neocortex.core.config.NC_CFG_FR_002_config import get_config
        cfg = get_config()
        api_key = getattr(cfg, "deepseek_api_key", "") or ""
    except Exception:
        api_key = ""

    if api_key:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = json.dumps({
            "model": "deepseek-reasoner",
            "messages": messages,
            "max_tokens": 4096,
        }).encode()
        try:
            req = urllib.request.Request(
                "https://api.deepseek.com/v1/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
            content = result["choices"][0]["message"]["content"]
            return {"success": True, "model": "deepseek-reasoner", "response": content,
                    "backend": "deepseek_api_direct", "fallback_used": None}
        except Exception as e:
            logger.warning(f"DeepSeek API falhou: {e} — tentando PicoClaw")

    # Tentativa 2: PicoClaw como proxy (quando funcionar)
    try:
        payload = json.dumps({"task": prompt, "context": system, "model": "deepseek-reasoner"}).encode()
        req = urllib.request.Request(
            "http://localhost:18790/message",
            data=payload, headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
        return {"success": True, "model": "deepseek-reasoner", "response": result,
                "backend": "picoclaw_proxy", "fallback_used": "picoclaw"}
    except Exception as e:
        logger.warning(f"PicoClaw indisponível: {e} — fallback para Qwen 3b (degraded)")

    # Fallback final: Qwen 3b local (raciocínio reduzido)
    result = _ollama_ask("qwen2.5-coder:3b-instruct", prompt, system=system, max_tokens=2048)
    result["backend"] = "ollama_3b_degraded"
    result["fallback_used"] = "qwen3b_local"
    result["warning"] = "DeepSeek API indisponível + PicoClaw offline. Raciocínio constitucional REDUZIDO."
    return result


# ---------------------------------------------------------------------------
# Router de Complexidade
# ---------------------------------------------------------------------------

def _llm_route(prompt: str, complexity: str = "OPERACIONAL", domain: str = "", system: str = "") -> Dict[str, Any]:
    """
    Router automático: escolhe modelo baseado na complexidade/domínio.
    Fórum (1.5b) → TJ (3b) → STJ/STF (R1 via PicoClaw)
    """
    # Resolver complexidade por domínio se não especificado
    if domain and not complexity:
        complexity = DOMAIN_COMPLEXITY.get(domain.lower(), "OPERACIONAL")

    cfg = COMPLEXITY_MAP.get(complexity.upper(), COMPLEXITY_MAP["OPERACIONAL"])

    if cfg["backend"] == "t0":
        return {"success": False, "info": "SOBERANO não executa tasks — T0 orquestra apenas"}

    if cfg["backend"] == "picoclaw":
        return _picoclaw_ask(prompt, system)

    # Ollama direto
    result = _ollama_ask(cfg["model"], prompt, system=system, max_tokens=cfg["max_tokens"])
    result["complexity"] = complexity
    result["tier"] = cfg["description"]
    return result


def _llm_audit(scope: str = "governance", level: str = "FORUM") -> Dict[str, Any]:
    """
    Auditoria de governança roteada pelo nível judicial.
    FORUM → 1.5b | TJ → 3b | STJ/STF → R1
    """
    level_to_complexity = {
        "FORUM": "OPERACIONAL",
        "TJ": "TECNICO",
        "STJ": "RACIOCINIO",
        "STF": "RACIOCINIO",
    }
    complexity = level_to_complexity.get(level.upper(), "OPERACIONAL")

    system = (
        "Você é o auditor de governança do NeoCortex. "
        f"Instância: {level}. Escopo: {scope}. "
        "Regras: NC-CONST-FR-001 + NC-GOV-FR-003 (20 regras). "
        "Retorne: compliance_score (0-100), violations[], warnings[], recommendation."
    )
    prompt = (
        f"Realize auditoria de escopo '{scope}'. "
        "Verifique: atomic_locks íntegros, tickets sem handoff, naming NC-, compliance geral."
    )
    result = _llm_route(prompt, complexity=complexity, system=system)
    result["audit_level"] = level
    result["scope"] = scope
    return result


# ---------------------------------------------------------------------------
# Register MCP tool
# ---------------------------------------------------------------------------

def register_tool(mcp) -> None:
    """Registra neocortex_local_llm no servidor MCP."""

    @mcp.tool(name="neocortex_local_llm")
    def neocortex_local_llm(
        action: str,
        model: str = "qwen2.5-coder:1.5b-instruct",
        prompt: str = "",
        system: str = "",
        complexity: str = "OPERACIONAL",
        domain: str = "",
        max_tokens: int = 512,
        timeout: int = 30,
        scope: str = "governance",
        level: str = "FORUM",
    ) -> Dict[str, Any]:
        """Bridge direta MCP ↔ Ollama + Router de Complexidade por Esfera.

        Actions: ollama.list, ollama.ask, ollama.status, ollama.load, ollama.run_cmd,
                 llm.route, llm.audit, llm.complexity_map
        Routing: OPERACIONAL→1.5b(Fórum) | TECNICO→3b(TJ) | RACIOCINIO→R1(STJ/STF) | SOBERANO→T0
        """
        if action == "ollama.list":
            models = _ollama_list()
            return {"success": True, "models": models, "count": len(models), "up": _ollama_is_up()}

        elif action == "ollama.status":
            up = _ollama_is_up()
            models = _ollama_list() if up else []
            return {
                "success": up,
                "ollama_up": up,
                "endpoint": OLLAMA_BASE,
                "models_loaded": models,
                "keepalive_env": "OLLAMA_KEEP_ALIVE=-1 (configure no sistema)",
                "recommended_24_7": "qwen2.5-coder:1.5b-instruct",
            }

        elif action == "ollama.ask":
            if not prompt:
                return {"success": False, "error": "prompt obrigatório"}
            return _ollama_ask(model, prompt, system=system, max_tokens=max_tokens)

        elif action == "ollama.load":
            return _ollama_load(model)

        elif action == "ollama.run_cmd":
            if not prompt:
                return {"success": False, "error": "prompt obrigatório"}
            return _ollama_run_cmd(model, prompt, timeout=timeout)

        elif action == "llm.route":
            if not prompt:
                return {"success": False, "error": "prompt obrigatório"}
            return _llm_route(prompt, complexity=complexity, domain=domain, system=system)

        elif action == "llm.audit":
            return _llm_audit(scope=scope, level=level)

        elif action == "llm.complexity_map":
            return {"success": True, "map": COMPLEXITY_MAP, "domain_map": DOMAIN_COMPLEXITY}

        else:
            return {
                "success": False,
                "error": f"Ação desconhecida: '{action}'",
                "available": [
                    "ollama.list", "ollama.ask", "ollama.status",
                    "ollama.load", "ollama.run_cmd",
                    "llm.route", "llm.audit", "llm.complexity_map",
                ],
            }
