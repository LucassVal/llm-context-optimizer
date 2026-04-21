#!/usr/bin/env python3
"""
NC-TOOL-FR-044 — neocortex_memory_auto
Auto-memória de sessão: registra turnos, hot_summary, session_end, lobe.auto.
Actions: turn.record, session.hot, session.stats, session.end, lobe.auto, catalog.now
"""

import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

TOOL_NAME = "neocortex_memory_auto"
TOOL_DESCRIPTION = (
    "Auto-memória de sessão. "
    "Actions: turn.record, session.hot, session.stats, session.end, lobe.auto, catalog.now"
)


def _get_smw():
    try:
        import importlib
        mod = importlib.import_module(
            "neocortex.core.services.NC-SVC-FR-021-session-memory-writer",
        )
        return mod.get_session_memory()
    except Exception:
        # Fallback — importa direto pelo path
        import importlib.util
        import sys
        tools_dir = Path(__file__).parent
        svc_path = (
            tools_dir.parents[1]  # neocortex/
            / "core" / "services"
            / "NC-SVC-FR-021-session-memory-writer.py"
        )
        spec = importlib.util.spec_from_file_location("session_memory_writer", svc_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules["session_memory_writer"] = mod
            spec.loader.exec_module(mod)  # type: ignore
            return mod.get_session_memory()
        raise ImportError("NC-SVC-FR-021 não encontrado")


def _get_config():
    try:
        from neocortex.core import get_config
        return get_config()
    except Exception:
        return None


async def memory_auto_tool(action: str, **kwargs: Any) -> Dict:
    """NC-TOOL-FR-044 — neocortex_memory_auto dispatcher."""
    try:
        smw = _get_smw()
    except Exception as e:
        return {"success": False, "error": f"SessionMemoryWriter indisponível: {e}"}

    # ── turn.record ───────────────────────────────────────────────────────────
    if action == "turn.record":
        user_msg = kwargs.get("user_msg", "")
        ai_response = kwargs.get("ai_response", "")
        if not user_msg:
            return {"success": False, "error": "user_msg obrigatório"}
        entry = smw.turn_record(user_msg=user_msg, ai_response=ai_response)
        return {"success": True, "action": action, "entry": entry}

    # ── session.hot ───────────────────────────────────────────────────────────
    elif action == "session.hot":
        max_chars = int(kwargs.get("max_chars", 2000))
        return {
            "success": True,
            "action": action,
            "hot_summary_text": smw.get_hot_summary_text(max_chars=max_chars),
            "hot_entries": len(smw.get_hot_summary()),
        }

    # ── session.stats ─────────────────────────────────────────────────────────
    elif action == "session.stats":
        return {"success": True, "action": action, **smw.stats()}

    # ── session.end ───────────────────────────────────────────────────────────
    elif action == "session.end":
        output_dir = kwargs.get("output_dir")
        out_path = Path(output_dir) if output_dir else None
        handoff = smw.session_end(output_path=out_path)
        return {"success": True, "action": action, "handoff": handoff}

    # ── lobe.auto ─────────────────────────────────────────────────────────────
    elif action == "lobe.auto":
        """Cria lobe automaticamente se hot_summary tem ≥3 entradas com tag comum."""
        hot = smw.get_hot_summary()
        if len(hot) < 3:
            return {"success": False, "action": action, "reason": "< 3 turnos no hot buffer"}

        # Contar tags frequentes
        from collections import Counter
        all_tags = []
        for e in hot:
            all_tags.extend(e.get("topic_tags", []))
        freq = Counter(all_tags).most_common(3)
        if not freq or freq[0][1] < 3:
            return {
                "success": False, "action": action,
                "reason": "Nenhuma tag com frequência ≥3",
                "top_tags": freq,
            }

        top_topic = freq[0][0]
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        lobe_name = f"NC-LBE-AUTO-{top_topic.upper()}-{date_str}.mdc"
        lobe_dir = Path(__file__).parents[4] / "02_memory_lobes" / "06_auto"
        lobe_dir.mkdir(parents=True, exist_ok=True)
        lobe_path = lobe_dir / lobe_name

        if not lobe_path.exists():
            hot_text = smw.get_hot_summary_text()
            content = f"""---
title: {lobe_name}
created: {datetime.now().isoformat()}
created_by: neocortex_memory_auto (auto-cataloger)
topic: {top_topic}
tags: auto-generated, {top_topic}
status: draft
---

# Auto-Lobe: {top_topic.upper()}

> Gerado automaticamente a partir de {len(hot)} turnos de conversa.

## Hot Summary

{hot_text}
"""
            lobe_path.write_text(content, encoding="utf-8")
            logger.info("lobe.auto: criado %s", lobe_path)
            return {"success": True, "action": action, "lobe_created": lobe_name, "topic": top_topic}
        else:
            return {"success": True, "action": action, "lobe_exists": lobe_name, "topic": top_topic}

    # ── catalog.now ───────────────────────────────────────────────────────────
    elif action == "catalog.now":
        """Atualiza hot-context.md com hot_summary atual."""
        hot_text = smw.get_hot_summary_text()
        stats = smw.stats()
        memory_dir = Path(__file__).parents[5] / ".claude" / "projects" / \
            "c--Users-Lucas-Val-rio-Desktop-TURBOQUANT-V42" / "memory"
        hot_ctx_path = memory_dir / "hot-context.md"
        from datetime import datetime
        ts = datetime.now().isoformat()
        content = f"""---
updated: {ts}
turns: {stats['turns_recorded']}
---

## Hot Context — últimas {stats['hot_buffer_used']} interações

{hot_text if hot_text else '(sem turnos registrados nesta sessão)'}
"""
        try:
            hot_ctx_path.write_text(content, encoding="utf-8")
            return {"success": True, "action": action, "updated": str(hot_ctx_path)}
        except Exception as e:
            return {"success": False, "action": action, "error": str(e)}

    # ── unknown ───────────────────────────────────────────────────────────────
    else:
        available = ["turn.record", "session.hot", "session.stats", "session.end", "lobe.auto", "catalog.now"]
        return {"success": False, "error": f"action desconhecida: {action}", "available": available}


def register_tool(mcp) -> None:
    """Registra NC-TOOL-FR-044 no servidor MCP."""
    @mcp.tool(name=TOOL_NAME, description=TOOL_DESCRIPTION)
    async def _memory_auto(action: str, **kwargs: Any) -> Dict:
        return await memory_auto_tool(action, **kwargs)

    logger.info("Registered MCP tool: %s", TOOL_NAME)
