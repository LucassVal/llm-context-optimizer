# @UBL @UBL @SUPER-015 | LEXICO: #MCP
#!/usr/bin/env python3
"""---
NC-SUPER-015 — neocortex_memory_auto
FÓRUM — Auto-Memória e Catalogação Semântica

WHAT: Automatic turn recording to JSONL session files, hot context summary
      retrieval, session statistics from .neocortex/memory/sessions, session
      finalization with summary, auto-lobe creation with NC-compliant naming,
      thermal decay of lobe temperatures (archiving at zero), and catalog
      snapshotting to catalog.jsonl with hot-context update.
WHY: Fire-and-forget memory persistence after every conversation turn —
     implement thermal context decay so stale lobes cool and archive
     naturally, enabling programmatic memory lobe creation without manual
     file manipulation.
WHERE: Registered as 'neocortex_memory_auto' — called after every user-AI
       interaction turn, by session closure hooks, and by memory maintenance
       daemons performing decay and cataloging cycles.

Actions: turn.record, session.hot, session.stats,
  session.end, lobe.auto, lobe.decay, catalog.now
---
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from ..errors import mcp_response
logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_memory_auto"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


def _get_writer():
    root = _root()
    # Correct path: NC-CORE-FR-128 in core/ directory (not services/)
    writer_file = root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-128-session-memory-writer.py"
    if not writer_file.exists():
        # Fallback: old path
        writer_file = root / "01_neocortex_framework" / "neocortex" / "core" / "services" / "NC-SVC-FR-021-session-memory-writer.py"
    if not writer_file.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location("session_memory_writer", str(writer_file))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.SessionMemoryWriter()
    except Exception as e:
        logger.warning(f"SessionMemoryWriter indisponivel: {e}")
        return None


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    @mcp_response
    def neocortex_memory_auto(
        action: str,
        user_message: str = "",
        ai_response: str = "",
        session_id: str = "",
        summary: str = "",
        lobe_name: str = "",
        lobe_content: str = "",
        lobe_category: str = "04_cc_patterns",
        decay_amount: int = 10,
        n_turns: int = 10,
    ) -> dict[str, Any]:
        """FÓRUM — Auto-Memória e Catalogação Semântica.
        Gatilho: após cada turn (user → ai), registe automaticamente.
        Actions: turn.record, session.hot, session.stats,
                 session.end, lobe.auto, lobe.decay, catalog.now
        """
        ts = _ts()
        root = _root()

        # ── GATEWAY VALIDATION ──────────────────────────────
        try:
            from neocortex.core.utils.gateway_bridge import gateway_check
            _ok, _report = gateway_check(action, root)
            if not _ok:
                return _report
        except Exception:
            pass

        # ── TURN.RECORD ───────────────────────────────────────────────────────
        if action == "turn.record":
            if not user_message:
                return {"success": False, "error": "user_message obrigatório", "timestamp": ts}
            # Fallback directo: sempre grava JSONL local (mais confiável)
            memory_dir = root / ".neocortex" / "memory" / "sessions"
            memory_dir.mkdir(parents=True, exist_ok=True)
            sid = session_id or datetime.now().strftime("%Y%m%d")
            jsonl_file = memory_dir / f"{sid}.jsonl"
            entry = {"ts": ts, "user": user_message, "ai": ai_response[:500] if ai_response else ""}
            with jsonl_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return {"success": True, "action": action, "file": str(jsonl_file),
                    "turns": sum(1 for _ in jsonl_file.open(encoding="utf-8")), "timestamp": ts}

        # ── SESSION.HOT ───────────────────────────────────────────────────────
        elif action == "session.hot":
            writer = _get_writer()
            if writer:
                hot = writer.get_hot_summary()
                return {"success": True, "action": action, "hot_summary": hot, "timestamp": ts}
            hot_file = root / ".claude" / "projects"
            for proj in hot_file.glob("c--Users-*"):
                hf = proj / "memory" / "hot-context.md"
                if hf.exists():
                    return {"success": True, "action": action,
                            "hot_summary": hf.read_text(encoding="utf-8")[:2000], "timestamp": ts}
            return {"success": True, "action": action, "hot_summary": None,
                    "note": "hot-context.md não encontrado", "timestamp": ts}

        # ── SESSION.STATS ─────────────────────────────────────────────────────
        elif action == "session.stats":
            memory_dir = root / ".neocortex" / "memory" / "sessions"
            if not memory_dir.exists():
                return {"success": True, "action": action,
                        "stats": {"sessions": 0, "total_turns": 0}, "timestamp": ts}
            sessions = list(memory_dir.glob("*.jsonl"))
            total_turns = 0
            for s in sessions:
                with contextlib.suppress(Exception):
                    total_turns += sum(1 for _ in s.open(encoding="utf-8"))
            return {"success": True, "action": action,
                    "stats": {"sessions": len(sessions), "total_turns": total_turns},
                    "timestamp": ts}

        # ── SESSION.END ───────────────────────────────────────────────────────
        elif action == "session.end":
            writer = _get_writer()
            if writer:
                result = writer.session_end(summary=summary or "Sessão encerrada via memory_auto")
                return {"success": True, "action": action, "session_end": result, "timestamp": ts}
            return {"success": True, "action": action,
                    "note": "SessionMemoryWriter indisponível — state preservado em jsonl", "timestamp": ts}

        # ── LOBE.AUTO ─────────────────────────────────────────────────────────
        elif action == "lobe.auto":
            if not lobe_name or not lobe_content:
                return {"success": False, "error": "lobe_name e lobe_content obrigatórios", "timestamp": ts}
            lobes_dir = root / "02_memory_lobes" / lobe_category
            lobes_dir.mkdir(parents=True, exist_ok=True)
            # Gerar nome NC- compliant
            clean_name = lobe_name.upper().replace(" ", "-")
            num = len(list(lobes_dir.glob("*.mdc"))) + 1
            lobe_category.rsplit("_", maxsplit=1)[-1].upper()[:3]
            nc_name = f"NC-LBE-DS-{num:03d}-{clean_name[:30]}.mdc"
            lobe_file = lobes_dir / nc_name
            header = (
                f"---\n"
                f"lobe: {lobe_name}\n"
                f"category: {lobe_category}\n"
                f"created: {ts}\n"
                f"source: auto (neocortex_memory_auto)\n"
                f"---\n\n"
            )
            lobe_file.write_text(header + lobe_content, encoding="utf-8")
            return {"success": True, "action": action, "lobe_file": str(lobe_file),
                    "lobe_name": nc_name, "category": lobe_category, "timestamp": ts}

        # ── LOBE.DECAY (Thermal Context Decay) ────────────────────────────────
        elif action == "lobe.decay":
            lobes_dir = root / "02_memory_lobes"
            if not lobes_dir.exists():
                return {"success": True, "action": action, "decayed": 0, "timestamp": ts}

            import re
            decayed_count = 0
            archived_count = 0

            for mdc in lobes_dir.rglob("*.mdc"):
                content = mdc.read_text(encoding="utf-8")

                # Só decair se a temperatura não estiver já hardcoded como zero ou não existir
                # Assumindo temperatura default de 100
                temp_match = re.search(r"^temperature:\s*(\d+)$", content, re.MULTILINE)
                current_temp = int(temp_match.group(1)) if temp_match else 100

                if current_temp > 0:
                    new_temp = max(0, current_temp - decay_amount)

                    if temp_match:
                        content = re.sub(r"^temperature:\s*\d+$", f"temperature: {new_temp}", content, flags=re.MULTILINE)
                    else:
                        content = re.sub(r"^(---[\s\S]*?)(\n---)", f"\\1\ntemperature: {new_temp}\\2", content, count=1)
                    if new_temp == 0:
                        content = re.sub(r"^(---[\s\S]*?)(\n---)", "\\1\nstatus: archived\\2", content, count=1)
                        archived_count += 1
                    mdc.write_text(content, encoding="utf-8")
                    decayed_count += 1
            return {"success": True, "action": action, "lobes_decayed": decayed_count,
                    "lobes_frozen": archived_count, "amount": decay_amount, "timestamp": ts}

        elif action == "catalog.now":
            memory_dir = root / "memory" / "sessions"
            sessions = list(memory_dir.glob("*.jsonl")) if memory_dir.exists() else []
            catalog_entry = {
                "timestamp": ts,
                "sessions_found": len(sessions),
                "action": "catalog.now",
                "status": "cataloged",
                "lobes_dir": str(root / "02_memory_lobes"),
            }
            catalog_file = root / "memory" / "catalog.jsonl"
            catalog_file.parent.mkdir(parents=True, exist_ok=True)
            with catalog_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(catalog_entry, ensure_ascii=False) + "\n")
            hot_ctx = root / ".claude" / "projects"
            for proj in hot_ctx.glob("c--Users-*"):
                hf = proj / "memory" / "hot-context.md"
                if hf.exists():
                    old = hf.read_text(encoding="utf-8")
                    hf.write_text(
                        f"---\nupdated: {ts}\ncatalog_sessions: {len(sessions)}\n---\n\n{old[:1500]}",
                        encoding="utf-8"
                    )
                    break
            return {"success": True, "action": action, "catalog_entry": catalog_entry,
                    "catalog_file": str(catalog_file), "timestamp": ts}
        # ── ORBITAL BRIDGE: delegar ações ──────────────────────────────────
        _orbital_result = None
        try:
            import importlib.util
            _spec = importlib.util.spec_from_file_location("orbital_bridge", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-139-orbital-bridge.py"))
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            _orbital_result = _mod.orbital_dispatch(action, root)
        except Exception:
            pass
        if _orbital_result is not None:
            return _orbital_result


        else:
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["turn.record", "session.hot", "session.stats",
                                  "session.end", "lobe.auto", "lobe.decay", "catalog.now"],
                    "timestamp": ts}
