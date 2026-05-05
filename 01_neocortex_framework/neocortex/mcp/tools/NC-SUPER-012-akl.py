#!/usr/bin/env python3
"""---
NC-SUPER-012 — neocortex_akl
---
"""

"""---
NC-SUPER-012 — neocortex_akl
---
"""

"""
NC-SUPER-012 — neocortex_akl
FÓRUM — AKL + Knowledge Graph + Consolidation

Funde: akl, kg (knowledge graph), consolidation.

Actions:
  akl.add, akl.search, akl.export
  kg.query, kg.enrich, kg.stats
  consolidate.session, consolidate.run
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_akl"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_akl(
        action: str,
        content: str = "",
        query: str = "",
        key: str = "",
        tag: str = "",
        session_id: str = "",
        summary: str = "",
        limit: int = 10,
    ) -> Dict[str, Any]:
        """FÓRUM — AKL, Knowledge Graph e Consolidation.
        Funde: akl + kg + consolidation.
        Actions: akl.add, akl.search, akl.export,
                 kg.query, kg.enrich, kg.stats,
                 consolidate.session, consolidate.run
        """
        ts = _ts()


        # UBL Gateway (Kernel 0)
        try:
            from neocortex.core.utils.gateway_bridge import gateway_check
            _ok, _report = gateway_check(action, root)
            if not _ok: return _report
        except Exception: pass
        # ── AKL ───────────────────────────────────────────────────────────────
        if action == "akl.add":
            if not content:
                return {"success": False, "error": "content obrigatório", "timestamp": ts}
            try:
                from neocortex.core import get_akl_service
                svc = get_akl_service()
                result = svc.add(content=content, key=key, tag=tag)
                return {"success": True, "action": action, "result": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "akl.search":
            if not query:
                return {"success": False, "error": "query obrigatório", "timestamp": ts}
            try:
                from neocortex.core import get_akl_service
                svc = get_akl_service()
                results = svc.search(query, limit=limit)
                return {"success": True, "action": action, "results": results,
                        "count": len(results), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "akl.export":
            try:
                from neocortex.core import get_akl_service, get_export_service
                akl = get_akl_service()
                data = akl.export()
                export_svc = get_export_service()
                result = export_svc.export_akl(data)
                return {"success": True, "action": action, "exported": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── KG ────────────────────────────────────────────────────────────────
        elif action == "kg.query":
            if not query:
                return {"success": False, "error": "query obrigatório", "timestamp": ts}
            try:
                from neocortex.core.knowledge_graph import get_kg_service
                kg = get_kg_service()
                result = kg.query(query, limit=limit)
                return {"success": True, "action": action, "result": result, "timestamp": ts}
            except Exception as e:
                return {"success": True, "action": action,
                        "note": f"KG indisponível: {e} — use memory.lobe.search", "timestamp": ts}

        elif action == "kg.enrich":
            if not content:
                return {"success": False, "error": "content obrigatório", "timestamp": ts}
            try:
                from neocortex.core.knowledge_graph import get_kg_service
                kg = get_kg_service()
                result = kg.enrich(content, tag=tag)
                return {"success": True, "action": action, "enriched": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "kg.stats":
            root = _root()
            kg_file = root / "genealogy_graph.json"
            if not kg_file.exists():
                return {"success": True, "action": action,
                        "note": "genealogy_graph.json não encontrado", "timestamp": ts}
            data = json.loads(kg_file.read_text(encoding="utf-8"))
            return {"success": True, "action": action,
                    "nodes": len(data) if isinstance(data, list) else
                             len(data.get("nodes", [])),
                    "kg_file": str(kg_file), "timestamp": ts}

        # ── CONSOLIDATION ─────────────────────────────────────────────────────
        elif action == "consolidate.session":
            try:
                from neocortex.core import get_consolidation_service
                svc = get_consolidation_service()
                sid = session_id or f"session_{ts.replace(':', '-')}"
                result = svc.summarize_session(session_id=sid,
                                               summary=summary or "Consolidação automática")
                return {"success": True, "action": action, "session_id": sid,
                        "result": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "consolidate.run":
            try:
                from neocortex.core import get_consolidation_service
                svc = get_consolidation_service()
                result = svc.run_full_consolidation()
                return {"success": True, "action": action, "result": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}


        elif action == "knowledge.get_documents":
            from pathlib import Path
            docs_dir = Path(__file__).parents[4] / "04_user_docs"
            if not docs_dir.exists():
                return {"success": True, "action": action, "documents": [], "timestamp": ts}
            docs = [{"name": f.name, "size_kb": round(f.stat().st_size/1024,1)}
                    for f in sorted(docs_dir.iterdir()) if f.is_file()]
            return {"success": True, "action": action, "documents": docs, "count": len(docs), "timestamp": ts}

        elif action == "knowledge.project_manifest":
            from pathlib import Path
            root = Path(__file__).parents[4]
            ssot = root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-NAM-FR-001-naming-convention.md"
            if ssot.exists():
                content_txt = ssot.read_text("utf-8", errors="replace")[:3000]
                return {"success": True, "action": action, "manifest": content_txt, "timestamp": ts}
            return {"success": False, "error": "NC-NAM-FR-001 nao encontrado", "timestamp": ts}

        elif action == "knowledge.get_boot_context":
            from pathlib import Path
            boot = Path(__file__).parents[4] / "DIR-BOOT-FR-001-bootup-main" / "NC-BOOT-FR-001-system-manifest.md"
            if boot.exists():
                return {"success": True, "action": action, "boot_context": boot.read_text("utf-8", errors="replace")[:4000], "timestamp": ts}
            return {"success": False, "error": "NC-BOOT-FR-001 nao encontrado", "timestamp": ts}

        elif action == "knowledge.update_index":
            try:
                from neocortex.core import get_lobe_service
                svc = get_lobe_service()
                result = svc.rebuild_index() if hasattr(svc, "rebuild_index") else {"note": "rebuild_index nao disponivel"}
                return {"success": True, "action": action, "result": result, "timestamp": ts}
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
                    "available": ["akl.add", "akl.search", "akl.export",
                                  "kg.query", "kg.enrich", "kg.stats",
                                  "consolidate.session", "consolidate.run"],
                    "timestamp": ts}
