#!/usr/bin/env python3
"""---
NC-SUPER-008 — neocortex_context
---
"""

"""---
NC-SUPER-008 — neocortex_context
---
"""

"""
NC-SUPER-008 — neocortex_context
CORTE TJ — Contexto e Compressão

Funde: context (017), report (013/010).

Actions:
  context.budget_status, context.compress, context.prune
  session.summarize, session.hot
  report.generate, report.list, report.compliance
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_context"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_context(
        action: str,
        content: str = "",
        summary: str = "",
        max_tokens: int = 4096,
        format: str = "markdown",
        output_path: str = "",
        session_id: str = "",
    ) -> dict[str, Any]:
        """CORTE TJ — Contexto e Compressão.
        Funde: context (017) + report (013+010).
        Actions: context.budget_status, context.compress, context.prune,
                 session.summarize, session.hot,
                 report.generate, report.list, report.compliance
        """
        ts = _ts()

        # UBL Gateway (Kernel 0)
        try:
            from neocortex.core.utils.gateway_bridge import gateway_check
            _ok, _report = gateway_check(action, root)
            if not _ok: return _report
        except Exception: pass
        root = _root()

        # ── CONTEXT ───────────────────────────────────────────────────────────
        if action == "context.budget_status":
            try:
                from neocortex.core import get_context_service
                svc = get_context_service()
                status = svc.get_budget_status()
                return {"success": True, "action": action, "budget": status, "timestamp": ts}
            except Exception as e:
                # Fallback: estimate from cortex size
                try:
                    from neocortex.core.file_utils import read_cortex
                    cortex = read_cortex()
                    size = len(json.dumps(cortex))
                    return {"success": True, "action": action,
                            "cortex_size_chars": size,
                            "estimated_tokens": size // 4,
                            "max_tokens": max_tokens,
                            "usage_pct": round((size // 4) / max_tokens * 100, 1),
                            "timestamp": ts}
                except Exception:
                    return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "context.compress":
            if not content:
                return {"success": False, "error": "content obrigatório", "timestamp": ts}

            # Fase 4.4.2: Excluir nós cuja temperatura esteja zerada / status: archived
            import re
            # Filter out chunks that contain "status: archived" or "temperature: 0"
            content_cleaned = re.sub(
                r"(?si)^---\nlobe:(.*?)(status:\s*archived|temperature:\s*0)(.*?)^---\n(.*?)\n\n",
                "", content
            )

            try:
                from neocortex.core import get_context_service
                svc = get_context_service()
                compressed = svc.compress(content_cleaned, max_tokens=max_tokens)
                return {"success": True, "action": action, "compressed": compressed,
                        "original_len": len(content), "cleaned_len": len(content_cleaned),
                        "compressed_len": len(compressed),
                        "ratio": round(len(compressed) / len(content) if len(content) else 1, 2),
                        "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "context.prune":
            try:
                from neocortex.core import get_context_service
                svc = get_context_service()
                result = svc.prune(max_tokens=max_tokens)
                return {"success": True, "action": action, "pruned": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── SESSION SUMMARIZE ─────────────────────────────────────────────────
        elif action == "session.summarize":
            try:
                svc_path = root / "01_neocortex_framework" / "neocortex" / "core" / "services"
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "session_memory_writer",
                    svc_path / "NC-SVC-FR-021-session-memory-writer.py"
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                sw = mod.SessionMemoryWriter()
                result = sw.session_end(summary=summary or "Sessão summarizada via neocortex_context")
                # Update hot-context.md
                hot_ctx = root / ".claude" / "projects"
                for proj in hot_ctx.glob("c--Users-*"):
                    hot = proj / "memory" / "hot-context.md"
                    if hot.exists():
                        old = hot.read_text(encoding="utf-8")
                        hot.write_text(f"---\nupdated: {ts}\n---\n\n{old}", encoding="utf-8")
                        break
                return {"success": True, "action": action, "session_end": result,
                        "summary": summary, "timestamp": ts}
            except Exception as e:
                return {"success": True, "action": action,
                        "note": f"SessionMemoryWriter fallback: {e}", "timestamp": ts}

        elif action == "session.hot":
            try:
                svc_path = root / "01_neocortex_framework" / "neocortex" / "core" / "services"
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "session_memory_writer",
                    svc_path / "NC-SVC-FR-021-session-memory-writer.py"
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                sw = mod.SessionMemoryWriter()
                hot = sw.get_hot_summary()
                return {"success": True, "action": action, "hot_summary": hot, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── REPORT ────────────────────────────────────────────────────────────
        elif action == "report.generate":
            try:
                from neocortex.core import get_report_service
                svc = get_report_service()
                report = svc.generate(format=format, session_id=session_id)
                if output_path:
                    Path(output_path).write_text(str(report), encoding="utf-8")
                return {"success": True, "action": action, "report": report,
                        "format": format, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "report.list":
            reports_dir = root / "reports"
            if not reports_dir.exists():
                return {"success": True, "action": action, "reports": [], "count": 0, "timestamp": ts}
            reports = [f.name for f in sorted(reports_dir.rglob("*.md")) if not f.name.startswith(".")]
            return {"success": True, "action": action, "reports": reports[-20:],
                    "count": len(reports), "timestamp": ts}

        elif action == "report.compliance":
            # Delega para governance.compliance.report
            try:
                import importlib
                gov_file = Path(__file__).parent / "NC-SUPER-001-governance.py"
                spec = importlib.util.spec_from_file_location("governance", gov_file)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                result = mod._compliance_report(root)
                return {"success": True, "action": action, "timestamp": ts, **result}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}


        elif action == "context.window_used":
            try:
                from neocortex.core import get_ledger_service
                svc = get_ledger_service()
                ledger = svc.read_ledger() if hasattr(svc, "read_ledger") else {}
                ctx = ledger.get("hot_context", {})
                entries = len(ctx) if isinstance(ctx, (list, dict)) else 0
                return {"success": True, "action": action, "entries": entries,
                        "hot_context_keys": list(ctx.keys()) if isinstance(ctx, dict) else entries,
                        "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "context.estimate":
            if not content:
                return {"success": False, "error": "content obrigatorio para estimativa", "timestamp": ts}
            tokens_est = len(content.split()) * 1.3
            return {"success": True, "action": action, "words": len(content.split()),
                    "tokens_estimated": int(tokens_est), "timestamp": ts}

        elif action == "context.smart_prune":
            try:
                from neocortex.core import get_ledger_service
                svc = get_ledger_service()
                if hasattr(svc, "prune_hot_context"):
                    result = svc.prune_hot_context()
                    return {"success": True, "action": action, "result": result, "timestamp": ts}
                return {"success": False, "error": "prune_hot_context nao disponivel", "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "session.handoff":
            try:
                from neocortex.core import get_ledger_service
                svc = get_ledger_service()
                ledger = svc.read_ledger() if hasattr(svc, "read_ledger") else {}
                handoff = {"session_id": ledger.get("session_id"),
                           "hot_context_entries": len(ledger.get("hot_context", {})),
                           "current_goal": ledger.get("current_goal"),
                           "timestamp": ts}
                return {"success": True, "action": action, "handoff": handoff, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "cache.stats":
            try:
                from neocortex.infra.hot_cache import get_hot_cache
                cache = get_hot_cache()
                stats = cache.stats() if hasattr(cache, "stats") else {"size": "unknown"}
                return {"success": True, "action": action, "stats": stats, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}
        # ORBITAL BRIDGE
        _orbital_result = None
        try:
            import importlib.util
            _spec = importlib.util.spec_from_file_location("orbital_bridge", str(root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-139-orbital-bridge.py"))
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            _orbital_result = _mod.orbital_dispatch(action, root)
        except Exception: pass
        if _orbital_result is not None: return _orbital_result


        else:
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["context.budget_status", "context.compress", "context.prune",
                                  "session.summarize", "session.hot",
                                  "report.generate", "report.list", "report.compliance"],
                    "timestamp": ts}
