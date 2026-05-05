#!/usr/bin/env python3
"""---
NC-HK-FR-004-lexico-step0-hook.py
---
"""

"""---
NC-HK-FR-004-lexico-step0-hook.py
---
"""

"""
NC-HK-FR-004-lexico-step0-hook.py
LEXICO-004 — Hook STEP-0: lexico.search antes de qualquer edição de serviço.

Objetivo: intercept PreToolUse de tools que operam sobre serviços/tools NC-SVC/NC-TOOL
e rodar lexico.search automaticamente para alinhar nomenclatura antes de editar.

Regra: se tool_name indica escrita em NC-SVC, NC-TOOL, ou NC-HK → buscar no léxico.
Retorna resultado como warning (não bloqueia — apenas informa).

Integração: registrar via HookRegistry.register() ou NC-CFG-HK-001-hooks.yaml
"""

import importlib.util
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Tools/prefixos que acionam o hook (escrita em serviços core)
_SERVICE_TOOL_KEYWORDS = [
    "neocortex_system",    # config.set, init.workspace
    "neocortex_memory",    # knowledge.store, lobe.activate
    "neocortex_security",  # hook.register, lock.check
    "neocortex_orchestration",  # task.execute, agent.spawn
]

# Ações de escrita (não disparar em reads/queries)
_WRITE_ACTIONS = {
    "config.set", "init.workspace",
    "knowledge.store", "lobe.activate", "hook.register",
    "task.execute", "agent.spawn", "dispatch.create",
    "rule.create", "policy.update",
}

_lexico_svc_cache = None


def _get_lexico_service():
    """Carrega LexicoService via importlib (R09)."""
    global _lexico_svc_cache
    if _lexico_svc_cache is not None:
        return _lexico_svc_cache
    try:
        fw = Path(__file__).parents[3]  # neocortex_framework root
        lexico_path = fw / "core" / "lexico_service.py"
        spec = importlib.util.spec_from_file_location("lexico_service", lexico_path)
        if spec is None:
            raise ImportError(f"Não encontrado: {lexico_path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _lexico_svc_cache = mod.LexicoService()
        return _lexico_svc_cache
    except Exception as e:
        logger.debug(f"[LEXICO-STEP0] LexicoService não disponível: {e}")
        return None


def _should_trigger(tool_name: str, action: str = "") -> bool:
    """Verificar se o hook deve disparar para esta tool+action."""
    tool_match = any(kw in tool_name for kw in _SERVICE_TOOL_KEYWORDS)
    if not tool_match:
        return False
    # Se action disponível, filtrar por writes apenas
    if action:
        return action in _WRITE_ACTIONS
    return True


def _lexico_search(query: str, limit: int = 5) -> List[Dict]:
    """Busca termos relacionados no léxico."""
    svc = _get_lexico_service()
    if svc is None:
        return []
    try:
        results = svc.search(query, limit=limit)
        return results if isinstance(results, list) else []
    except Exception as e:
        logger.debug(f"[LEXICO-STEP0] search erro: {e}")
        return []


class LexicoStep0Hook:
    """
    Hook STEP-0: intercep PreToolUse de tools de serviço e consulta o léxico.

    Não bloqueia execução — emite warnings via logger e retorna sugestões
    para que o agente T0 possa verificar nomenclatura antes de editar.

    Uso via HookRegistry:
        hook = LexicoStep0Hook()
        registry.register("lexico_step0", HookEvent.PRE_TOOL_USE,
                          hook.on_pre_tool_use, timeout_seconds=3.0)
    """

    def __init__(self, auto_log: bool = True, min_confidence: float = 0.6):
        self.auto_log = auto_log
        self.min_confidence = min_confidence
        self._hit_count = 0
        self._miss_count = 0

    def on_pre_tool_use(
        self,
        tool_name: str = "",
        action: str = "",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Handler PreToolUse — busca léxico se for tool de serviço/escrita."""
        if not _should_trigger(tool_name, action):
            return {"lexico_step0": "skip", "reason": "not_a_service_write"}

        # Montar query a partir do contexto disponível
        query_parts = [tool_name, action]
        # kwargs pode conter key, content, task_name etc.
        for field in ("key", "task_name", "action_name", "hook_event"):
            val = kwargs.get(field, "")
            if val and isinstance(val, str):
                query_parts.append(val)
        query = " ".join(filter(None, query_parts))

        results = _lexico_search(query, limit=5)

        if not results:
            self._miss_count += 1
            result = {
                "lexico_step0": "no_match",
                "query": query,
                "suggestion": "Termo novo — verificar @SSOT antes de criar.",
            }
            if self.auto_log:
                logger.info(f"[LEXICO-STEP0] ⚠️  '{query}' — sem match no léxico. Verificar @SSOT.")
            return result

        # Filtrar por confiança mínima se campo disponível
        good = [r for r in results if r.get("score", 1.0) >= self.min_confidence]
        if not good:
            good = results[:3]

        self._hit_count += 1
        terms = [r.get("term") or r.get("key") or str(r) for r in good[:3]]

        result = {
            "lexico_step0": "ok",
            "query": query,
            "tool": tool_name,
            "action": action,
            "matches": len(results),
            "top_terms": terms,
            "regions": list({r.get("semantic_scope", "?") for r in good}),
        }

        if self.auto_log:
            logger.info(
                f"[LEXICO-STEP0] ✅ '{query}' → {len(results)} matches | "
                f"top: {terms[:2]} | regiões: {result['regions']}"
            )
        return result

    def stats(self) -> Dict[str, int]:
        """Retorna estatísticas de hits/misses do hook."""
        return {
            "hits": self._hit_count,
            "misses": self._miss_count,
            "total": self._hit_count + self._miss_count,
        }


# ── Função para registro direto via load_yaml ────────────────────────────────
_hook_instance: Optional[LexicoStep0Hook] = None


def get_hook() -> LexicoStep0Hook:
    """Singleton do LexicoStep0Hook."""
    global _hook_instance
    if _hook_instance is None:
        _hook_instance = LexicoStep0Hook()
    return _hook_instance


def hook_handler(**kwargs) -> Dict[str, Any]:
    """Entry point para load_yaml (HookRegistry espera uma função 'hook_handler')."""
    return get_hook().on_pre_tool_use(**kwargs)


__all__ = ["LexicoStep0Hook", "get_hook", "hook_handler"]
