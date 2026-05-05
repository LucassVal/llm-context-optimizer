from __future__ import annotations
"""---
domain: "orchestration"
layer: "core"
type: "service"
tags: ["tool", "030", "context"]
hash: "auto-generated"
---"""
"""
NC-TOOL-FR-030-context.py
FR-030  MCP Tool: neocortex_context

Economia de tokens e compresso de contexto.
Aes disponveis:
  context.budget_status  tokens usados vs limite da sesso
  context.window_used    % do context window estimado
  context.estimate       estima custo de uma ao antes de executar
  context.compress       gera sumrio comprimido da sesso atual
  context.smart_prune    remove entradas menos relevantes do ledger
  session.summarize      sumrio de fim de sesso para @BOOT
  session.handoff        empacota contexto para continuar em outra IA
  cache.stats            estatsticas do HotCache
"""


import json
import logging
import time
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Custo em USD por 1M tokens (DeepSeek pricing 2026-04)
DEEPSEEK_COST = {
    "deepseek-chat": {"input": 0.27, "output": 1.10, "cache_hit": 0.07},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19, "cache_hit": 0.14},
    "default": {"input": 0.50, "output": 1.50, "cache_hit": 0.12},
}

_SESSION_START = time.time()
_session_token_log: list = []  # acumulado na sesso


def _config():
    try:
        from neocortex.NC-CORE-FR-001-config import get_config

        return get_config()
    except Exception:
        return None


def _ledger():
    try:
        from neocortex.core import get_ledger_store

        return get_ledger_store()
    except Exception:
        return None


def _hot_cache():
    try:
        from neocortex.core import get_hot_cache

        return get_hot_cache()
    except Exception:
        return None


def _calc_usd(tokens: int, model: str, token_type: str = "input") -> float:
    rates = DEEPSEEK_COST.get(model, DEEPSEEK_COST["default"])
    rate = rates.get(token_type, rates["input"])
    return round((tokens / 1_000_000) * rate, 6)


def register_tool(mcp) -> None:
    """Registra neocortex_context no servidor MCP."""

    @mcp.tool(name="neocortex_context")
    def neocortex_context(
        action: str,
        model: str = "deepseek-chat",
        budget_daily_tokens: int = 500_000,
        action_description: str = "",
        estimated_tokens: int = 0,
        max_entries: int = 100,
    ) -> Dict[str, Any]:
        """
        Economia de tokens e gesto de contexto do NeoCortex.

        Aes disponveis:
          context.budget_status  tokens usados na sesso vs oramento dirio
          context.window_used    % estimado do context window consumido
          context.estimate       custo estimado em USD de uma ao
          context.compress       descrio comprimida do estado atual
          context.smart_prune    remove entradas antigas do ledger
          session.summarize      sumrio de sesso para @BOOT
          session.handoff        pacote compacto para nova IA continuar
          cache.stats            hit rate e tamanho do HotCache

        Args:
            action:               Ao desejada
            model:                Modelo LLM para estimativa de custo (deepseek-chat | deepseek-reasoner)
            budget_daily_tokens:  Oramento dirio em tokens (default: 500k)
            action_description:   Descrio da ao para context.estimate
            estimated_tokens:     Tokens estimados para context.estimate
            max_entries:          Mximo de entradas para context.smart_prune
        """

        #  context.budget_status 
        if action == "context.budget_status":
            ld = _ledger()
            tokens_used = 0
            if ld:
                try:
                    metrics = ld.get_metrics() if hasattr(ld, "get_metrics") else {}
                    tokens_used = metrics.get("total_tokens", 0)
                except Exception:
                    pass
            pct = (
                round((tokens_used / budget_daily_tokens) * 100, 1)
                if budget_daily_tokens > 0
                else 0
            )
            remaining = max(0, budget_daily_tokens - tokens_used)
            cost_used = _calc_usd(tokens_used, model, "input")
            return {
                "success": True,
                "action": action,
                "model": model,
                "tokens_used": tokens_used,
                "budget_daily": budget_daily_tokens,
                "remaining": remaining,
                "percent_used": pct,
                "estimated_cost_usd": cost_used,
                "status": " ATENO"
                if pct > 80
                else " Moderado"
                if pct > 50
                else " OK",
            }

        #  context.window_used 
        elif action == "context.window_used":
            # DeepSeek context window: 64K tokens
            WINDOW_SIZE = 64_000
            ld = _ledger()
            tokens_in_context = 0
            if ld:
                try:
                    metrics = ld.get_metrics() if hasattr(ld, "get_metrics") else {}
                    tokens_in_context = metrics.get(
                        "context_tokens", metrics.get("total_tokens", 0)
                    )
                except Exception:
                    pass
            pct = round((tokens_in_context / WINDOW_SIZE) * 100, 1)
            return {
                "success": True,
                "action": action,
                "window_size": WINDOW_SIZE,
                "tokens_in_context": tokens_in_context,
                "percent_used": pct,
                "tokens_remaining": max(0, WINDOW_SIZE - tokens_in_context),
                "recommend_compress": pct > 70,
            }

        #  context.estimate 
        elif action == "context.estimate":
            if not estimated_tokens and not action_description:
                return {
                    "success": False,
                    "error": "Fornea estimated_tokens ou action_description.",
                }
            # Heurstica: sem tokens explcitos, estima pelo tamanho da descrio
            if not estimated_tokens and action_description:
                estimated_tokens = len(action_description) // 4  # ~4 chars/token
            input_cost = _calc_usd(estimated_tokens, model, "input")
            output_cost = _calc_usd(estimated_tokens // 2, model, "output")
            cache_cost = _calc_usd(estimated_tokens, model, "cache_hit")
            return {
                "success": True,
                "action": action,
                "model": model,
                "estimated_tokens": estimated_tokens,
                "cost_if_cache_miss_usd": round(input_cost + output_cost, 6),
                "cost_if_cache_hit_usd": round(cache_cost + output_cost, 6),
                "savings_with_cache_usd": round(input_cost - cache_cost, 6),
                "recommendation": " Prossiga"
                if (input_cost + output_cost) < 0.01
                else " Custo moderado  considere comprimir contexto primeiro",
            }

        #  context.compress 
        elif action == "context.compress":
            uptime_s = int(time.time() - _SESSION_START)
            ld = _ledger()
            summary_data: Dict[str, Any] = {
                "session_uptime_s": uptime_s,
                "generated_at": datetime.now().isoformat(),
            }
            if ld:
                try:
                    summary_data["metrics"] = (
                        ld.get_metrics() if hasattr(ld, "get_metrics") else {}
                    )
                except Exception:
                    pass
            summary_text = (
                f"[NeoCortex Session Compress  {datetime.now().strftime('%Y-%m-%d %H:%M')}] "
                f"Uptime: {uptime_s}s | "
                f"Tokens: {summary_data.get('metrics', {}).get('total_tokens', 'N/A')} | "
                f"Load @BOOT para retomar contexto completo."
            )
            return {
                "success": True,
                "action": action,
                "compressed_summary": summary_text,
                "chars": len(summary_text),
                "estimated_tokens": len(summary_text) // 4,
                "data": summary_data,
            }

        #  context.smart_prune 
        elif action == "context.smart_prune":
            ld = _ledger()
            if ld is None:
                return {"success": False, "error": "LedgerStore indisponvel."}
            try:
                result = (
                    ld.prune_context(max_entries=max_entries)
                    if hasattr(ld, "prune_context")
                    else {"pruned": 0}
                )
                return {
                    "success": True,
                    "action": action,
                    "max_entries": max_entries,
                    **result,
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  session.summarize 
        elif action == "session.summarize":
            uptime_s = int(time.time() - _SESSION_START)
            ld = _ledger()
            metrics = {}
            if ld:
                try:
                    metrics = ld.get_metrics() if hasattr(ld, "get_metrics") else {}
                except Exception:
                    pass
            summary = {
                "generated_at": datetime.now().isoformat(),
                "session_uptime_seconds": uptime_s,
                "total_tokens": metrics.get("total_tokens", "N/A"),
                "estimated_cost_usd": _calc_usd(metrics.get("total_tokens", 0), model),
                "instruction": "Cole este sumrio no prximo @BOOT para continuidade de contexto.",
            }
            return {"success": True, "action": action, "summary": summary}

        #  session.handoff 
        elif action == "session.handoff":
            handoff = {
                "type": "neocortex_session_handoff",
                "timestamp": datetime.now().isoformat(),
                "project": "NeoCortex MCP Framework",
                "boot_instruction": "Carregue @BOOT (NC-BOOT-FR-001) e @SSOT (NC-NAM-FR-001) para retomar.",
                "active_tasks": "Consulte @ROADMAP (NC-TODO-FR-001) para tickets pendentes.",
                "phase": "Fase 3  Refatorao 2210 tools (FR-029/030 concludos, FR-021 prximo)",
                "model_config": {
                    "default": "deepseek-chat (T1)",
                    "reasoning": "deepseek-reasoner (T0)",
                    "workers": "qwen2.5-coder:1.5b (courier) / qwen2.5-coder:3b (engineer)",
                },
            }
            compact = json.dumps(handoff, ensure_ascii=False, separators=(",", ":"))
            return {
                "success": True,
                "action": action,
                "handoff_json": handoff,
                "compact_string": compact,
                "chars": len(compact),
                "estimated_tokens": len(compact) // 4,
            }

        #  cache.stats 
        elif action == "cache.stats":
            hc = _hot_cache()
            if hc is None:
                return {"success": False, "error": "HotCache indisponvel."}
            try:
                stats = hc.stats() if hasattr(hc, "stats") else {}
                volume = hc.volume() if hasattr(hc, "volume") else {}
                return {
                    "success": True,
                    "action": action,
                    "stats": stats,
                    "volume": volume,
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  ao desconhecida 
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'.",
                "available": [
                    "context.budget_status",
                    "context.window_used",
                    "context.estimate",
                    "context.compress",
                    "context.smart_prune",
                    "session.summarize",
                    "session.handoff",
                    "cache.stats",
                ],
            }
