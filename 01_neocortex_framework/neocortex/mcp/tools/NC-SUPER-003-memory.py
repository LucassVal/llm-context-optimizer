#!/usr/bin/env python3
"""---
NC-SUPER-003 — neocortex_memory
CORTE TJ — Memória e Conhecimento

WHAT: Cortex state CRUD, lobe file system operations (list/get/search/
      activate/deactivate/populate), semantic knowledge search/store,
      manifest generation with query/filter, lexico neuroplasticity building,
      and automated semantic categorization of all memory lobes via Qwen 1.5b.
WHY: Unify 7 legacy tools (cortex, lobes, search, knowledge x2, memory,
     manifest) into one TJ-tier memory interface for structured context
     read/write, lobe file search, and auto-population from SSOT.
WHERE: Registered as 'neocortex_memory' — manages 02_memory_lobes directory,
       cortex state, manifest registries under TURBOQUANT_V42 project root.

Actions: cortex.get/update/reset/get_full/get_section/get_aliases/
  get_workflows/validate_alias,
  lobe.list/get/activate/search/list_active/list_all/get_content/
  deactivate/populate,
  knowledge.search, knowledge.store,
  manifest.generate/list/update/query/generate_all,
  search.advanced, lexico.build/search/stats, semantic.categorize
---
"""
import contextlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_memory"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


def _get_cortex_service():
    try:
        from neocortex.core import get_cortex_service
        return get_cortex_service()
    except Exception:
        return None


def _get_lobe_service():
    try:
        from neocortex.core import get_lobe_service
        return get_lobe_service()
    except Exception:
        return None


def _get_knowledge_service():
    try:
        from neocortex.core import get_knowledge_service
        return get_knowledge_service()
    except Exception:
        return None


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_memory(
        action: str,
        query: str = "",
        content: str = "",
        key: str = "",
        lobe_name: str = "",
        limit: int = 10,
        category: str = "",
        tag: str = "",
        section: str = "",
        alias: str = "",
        target: str = "",
        manifest_id: str = "",
        metadata: str = "",
        search_term: str | None = None,
        manifest_type: str | None = None,
        tags_filter: list[str] | None = None,
    ) -> dict[str, Any]:
        """CORTE TJ — Memória e Conhecimento.
        Funde: cortex, lobes, search, knowledge×2, memory, manifest.
        Actions: cortex.get, cortex.update, cortex.reset,
                 lobe.list, lobe.get, lobe.activate, lobe.search,
                 knowledge.search, knowledge.store,
                 manifest.generate, manifest.list, search.advanced
        """
        ts = _ts()
        root = _root()

        # ── UBL Gateway (Kernel 0) ──────────────────────────────────────────
        try:
            from neocortex.core.utils.gateway_bridge import gateway_check
            _ok, _report = gateway_check(action, root)
            if not _ok:
                return _report
        except Exception:
            pass

        # ── CORTEX ────────────────────────────────────────────────────────────
        if action == "cortex.get":
            svc = _get_cortex_service()
            if svc:
                try:
                    data = svc.get_full_context() if hasattr(svc, "get_full_context") else svc.read()
                    return {"success": True, "action": action, "cortex": data, "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            # Fallback: ler arquivo cortex diretamente
            try:
                from neocortex.core.file_utils import read_cortex
                return {"success": True, "action": action, "cortex": read_cortex(), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "cortex.update":
            if not content:
                return {"success": False, "error": "content obrigatório", "timestamp": ts}
            try:
                from neocortex.core.file_utils import write_cortex
                write_cortex(content)
                return {"success": True, "action": action, "updated": True, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "cortex.reset":
            try:
                from neocortex.core.file_utils import write_cortex
                write_cortex({})
                return {"success": True, "action": action, "reset": True, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── LOBES ─────────────────────────────────────────────────────────────
        elif action == "lobe.list":
            lobes_dir = root / "02_memory_lobes"
            if not lobes_dir.exists():
                lobes_dir = root / "01_neocortex_framework" / "lobes"
            if not lobes_dir.exists():
                return {"success": True, "action": action, "lobes": [], "count": 0, "timestamp": ts}
            lobes = [{"name": f.stem, "path": str(f.relative_to(root)), "size_bytes": f.stat().st_size}
                     for f in sorted(lobes_dir.rglob("*.mdc"))
                     if not any(p.startswith(".") for p in f.parts)]
            if category:
                lobes = [l for l in lobes if category.lower() in l["path"].lower()]
            return {"success": True, "action": action, "lobes": lobes[:limit],
                    "count": len(lobes), "timestamp": ts}

        elif action == "lobe.get":
            if not lobe_name:
                return {"success": False, "error": "lobe_name obrigatório", "timestamp": ts}
            lobes_dir = root / "02_memory_lobes"
            if not lobes_dir.exists():
                lobes_dir = root / "01_neocortex_framework" / "lobes"
            matches = list(lobes_dir.rglob(f"*{lobe_name}*.mdc"))
            if not matches:
                return {"success": False, "error": f"Lobe '{lobe_name}' não encontrado", "timestamp": ts}
            content_text = matches[0].read_text(encoding="utf-8", errors="replace")
            return {"success": True, "action": action, "lobe": matches[0].name,
                    "content": content_text[:4000], "full_path": str(matches[0]), "timestamp": ts}

        elif action == "lobe.search":
            if not query:
                return {"success": False, "error": "query obrigatório", "timestamp": ts}
            lobes_dir = root / "02_memory_lobes"
            if not lobes_dir.exists():
                lobes_dir = root / "01_neocortex_framework" / "lobes"
            results = []
            for lobe_file in lobes_dir.rglob("*.mdc"):
                try:
                    text = lobe_file.read_text(encoding="utf-8", errors="replace")
                    if query.lower() in text.lower():
                        idx = text.lower().find(query.lower())
                        snippet = text[max(0, idx-50):idx+150]
                        results.append({"lobe": lobe_file.name, "snippet": snippet})
                except Exception:
                    pass
            return {"success": True, "action": action, "query": query,
                    "results": results[:limit], "count": len(results), "timestamp": ts}

        elif action == "lobe.activate":
            svc = _get_lobe_service()
            if svc:
                try:
                    result = svc.activate(lobe_name)
                    return {"success": True, "action": action, "lobe": lobe_name, "result": result, "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "LobeService indisponível", "timestamp": ts}

        # ── KNOWLEDGE ─────────────────────────────────────────────────────────
        elif action == "knowledge.search":
            if not query:
                return {"success": False, "error": "query obrigatório", "timestamp": ts}
            svc = _get_knowledge_service()
            if svc:
                try:
                    results = svc.search(query, limit=limit)
                    return {"success": True, "action": action, "results": results,
                            "count": len(results), "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            # GAP-005: fallback to real SearchService
            try:
                from neocortex.core import get_search_service
                search_svc = get_search_service()
                if search_svc:
                    result = search_svc.search_knowledge(query, limit)
                    return {"success": True, "action": action,
                            "results": result.get("results", []),
                            "total_found": result.get("total_found", 0), "timestamp": ts}
            except Exception:
                pass
            return {"success": True, "action": action,
                    "note": "KnowledgeService indisponível — use lobe.search", "timestamp": ts}

        elif action == "knowledge.store":
            if not key or not content:
                return {"success": False, "error": "key e content obrigatórios", "timestamp": ts}
            svc = _get_knowledge_service()
            if svc:
                try:
                    result = svc.store(key=key, content=content, tag=tag)
                    return {"success": True, "action": action, "stored": key, "result": result, "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "KnowledgeService indisponível", "timestamp": ts}

        # ── SEARCH ────────────────────────────────────────────────────────────
        elif action == "search.advanced":
            if not query:
                return {"success": False, "error": "query obrigatório", "timestamp": ts}
            try:
                from neocortex.core import get_search_service
                svc = get_search_service()
                results = svc.search_advanced(query, limit=limit)
                return {"success": True, "action": action, "query": query,
                        "results": results.get("results", []),
                        "total_found": results.get("total_found", 0), "timestamp": ts}
            except Exception as e:
                # Fallback: SearchService indisponível
                return {"success": True, "action": action, "query": query,
                        "note": f"SearchService indisponível ({e}), use lobe.search", "timestamp": ts}

        # ── MANIFEST ──────────────────────────────────────────────────────────
        elif action == "manifest.generate":
            try:
                from neocortex.core import get_manifest_service
                svc = get_manifest_service()
                result = svc.generate()
                return {"success": True, "action": action, "manifest": result, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "manifest.list":
            root_path = _root()
            manifest_dir = root_path / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main"
            manifests = [f.name for f in manifest_dir.glob("*manifest*.yaml")] if manifest_dir.exists() else []
            return {"success": True, "action": action, "manifests": manifests,
                    "count": len(manifests), "timestamp": ts}


        # ── LOBE (extended from NC-TOOL-FR-021) ───────────────────────────────
        elif action == "lobe.list_active":
            svc = _get_lobe_service()
            if svc:
                try:
                    all_r    = svc.list_lobes() if hasattr(svc, "list_lobes") else {}
                    active_r = svc.get_active_lobes() if hasattr(svc, "get_active_lobes") else {}
                    return {"success": True, "action": action,
                            "all_lobes": all_r.get("lobes", []),
                            "active_lobes": active_r.get("active_lobes", []),
                            "total_lobes": all_r.get("total", 0),
                            "total_active": active_r.get("total_active", 0),
                            "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "LobeService indisponivel", "timestamp": ts}

        elif action == "lobe.list_all":
            svc = _get_lobe_service()
            if svc:
                try:
                    result = svc.list_lobes()
                    return {**result, "action": action, "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "LobeService indisponivel", "timestamp": ts}

        elif action == "lobe.get_content":
            if not lobe_name:
                return {"success": False, "error": "lobe_name obrigatorio", "timestamp": ts}
            svc = _get_lobe_service()
            if svc:
                try:
                    result = svc.get_lobe(lobe_name)
                    return {**result, "action": action, "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "LobeService indisponivel", "timestamp": ts}

        elif action == "lobe.deactivate":
            if not lobe_name:
                return {"success": False, "error": "lobe_name obrigatorio", "timestamp": ts}
            svc = _get_lobe_service()
            if svc and hasattr(svc, "deactivate_lobe"):
                try:
                    result = svc.deactivate_lobe(lobe_name)
                    return {**result, "action": action, "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "LobeService.deactivate_lobe indisponivel", "timestamp": ts}

        # ── CORTEX (extended from NC-TOOL-FR-021) ─────────────────────────────
        elif action == "cortex.get_full":
            svc = _get_cortex_service()
            if svc and hasattr(svc, "get_full_cortex"):
                try:
                    result = svc.get_full_cortex()
                    return {"success": True, "action": action,
                            "content": result.get("content"), "metadata": result.get("metadata"),
                            "aliases": result.get("aliases"), "workflows": result.get("workflows"),
                            "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "get_full_cortex nao disponivel, use cortex.get", "timestamp": ts}

        elif action == "cortex.get_section":
            if not section:
                return {"success": False, "error": "section obrigatorio", "timestamp": ts}
            svc = _get_cortex_service()
            if svc and hasattr(svc, "get_cortex_section"):
                try:
                    result = svc.get_cortex_section(section)
                    return {"success": result.get("found", False), "action": action,
                            "section": result.get("section"), "content": result.get("content"),
                            "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "get_cortex_section nao disponivel", "timestamp": ts}

        elif action == "cortex.get_aliases":
            svc = _get_cortex_service()
            if svc and hasattr(svc, "get_aliases"):
                try:
                    aliases = svc.get_aliases()
                    return {"success": True, "action": action,
                            "aliases": [{"symbol": k, "path": v} for k, v in aliases.items()],
                            "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "get_aliases nao disponivel", "timestamp": ts}

        elif action == "cortex.get_workflows":
            svc = _get_cortex_service()
            if svc and hasattr(svc, "get_workflows"):
                try:
                    wf = svc.get_workflows()
                    return {"success": True, "action": action, "workflows": wf, "count": len(wf), "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "get_workflows nao disponivel", "timestamp": ts}

        elif action == "cortex.validate_alias":
            if not alias:
                return {"success": False, "error": "alias obrigatorio", "timestamp": ts}
            svc = _get_cortex_service()
            if svc and hasattr(svc, "validate_alias"):
                try:
                    result = svc.validate_alias(alias)
                    return {"success": True, "action": action, "valid": result.get("valid"),
                            "exists": result.get("exists"), "value": result.get("value"), "timestamp": ts}
                except Exception as e:
                    return {"success": False, "error": str(e), "timestamp": ts}
            return {"success": False, "error": "validate_alias nao disponivel", "timestamp": ts}

        # ── MANIFEST (extended from NC-TOOL-FR-021) ────────────────────────────
        elif action == "manifest.update":
            import json as _json
            if not manifest_id:
                return {"success": False, "error": "manifest_id obrigatorio", "timestamp": ts}
            meta_dict = {}
            if metadata:
                try:
                    meta_dict = _json.loads(metadata)
                except Exception:
                    return {"success": False, "error": "metadata deve ser JSON valido", "timestamp": ts}
            try:
                from neocortex.core import get_manifest_service
                result = get_manifest_service().update_manifest(manifest_id, meta_dict)
                return {**result, "action": action, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "manifest.query":
            try:
                from neocortex.core import get_manifest_service
                result = get_manifest_service().query_manifests(
                    search_term=search_term, manifest_type=manifest_type,
                    tags=tags_filter, limit=limit)
                return {**result, "action": action, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "manifest.generate_all":
            try:
                from neocortex.core import get_manifest_service
                result = get_manifest_service().generate_all_manifests()
                return {**result, "action": action, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── LEXICO (LEXICO-001) — Neuroplasticidade ────────────────────────────
        elif action == "lexico.build":
            try:
                from neocortex.core.lexico_service import run_lexico_build
                max_defs = limit if limit else 30
                result = run_lexico_build(with_defs=True, max_defs=max_defs)
                return {"success": True, "action": action, **result}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "lexico.search":
            try:
                from neocortex.core.lexico_service import get_lexico_service
                if not query:
                    return {"success": False, "error": "query obrigatório", "timestamp": ts}
                hits = get_lexico_service().search(query)
                return {"success": True, "action": action, "query": query,
                        "results": hits, "count": len(hits), "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "lexico.stats":
            try:
                from neocortex.core.lexico_service import get_lexico_service
                stats = get_lexico_service().latest_stats()
                return {"success": True, "action": action, **stats}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        # ── LOBE POPULATE (G4 — @POPULATE NC-SCR-FR-001) ──────────────────────
        elif action == "lobe.populate":
            """G4 — Ciclo 4: Popular/sincronizar lobes via NC-SCR-FR-001-populate-lobes-ssot.py."""
            import subprocess
            import sys
            root = Path(__file__).parents[4]
            script = root / "01_neocortex_framework" / "scripts" / "NC-SCR-FR-001-populate-lobes-ssot.py"
            if not script.exists():
                return {"success": False, "action": action,
                        "error": f"Script ausente: {script.name}", "timestamp": ts}
            dry = False  # por segurança pode ser --dry-run controlado
            args = [sys.executable, str(script)]
            try:
                r = subprocess.run(args, capture_output=True, text=True, timeout=90,
                                   cwd=str(root / "01_neocortex_framework"))
                return {"success": r.returncode == 0, "action": action,
                        "stdout": r.stdout[-1200:], "stderr": r.stderr[-400:],
                        "returncode": r.returncode, "dry_run": dry, "timestamp": ts}
            except subprocess.TimeoutExpired:
                return {"success": False, "action": action, "error": "Timeout 90s", "timestamp": ts}
            except Exception as e:
                return {"success": False, "action": action, "error": str(e), "timestamp": ts}

        # ── SEMANTIC CATEGORIZE (P3 — NC-DS-148) ──────────────────────────────
        elif action == "semantic.categorize":
            """P3 — Categorização semântica de todos os lobes via Qwen 1.5b (NC-SCR-FR-114)."""
            import subprocess
            root = Path(__file__).parents[4]
            script = root / "01_neocortex_framework" / "scripts" / "NC-SCR-FR-114-auto-categorize-lobes.py"
            if not script.exists():
                return {"success": False, "action": action,
                        "error": f"Script ausente: {script.name}", "timestamp": ts}
            try:
                r = subprocess.run([sys.executable, str(script)],
                                   capture_output=True, text=True, timeout=300,
                                   cwd=str(root / "01_neocortex_framework"))
                # Tentar ler índice gerado
                index_path = root / "02_memory_lobes" / "NC-CAT-INDEX-001.json"
                index = None
                if index_path.exists():
                    with contextlib.suppress(Exception):
                        index = json.loads(index_path.read_text("utf-8"))
                return {"success": r.returncode == 0, "action": action,
                        "total_categorized": index.get("total", 0) if index else 0,
                        "distribution": index.get("distribution", {}) if index else {},
                        "stdout": r.stdout[-800:], "stderr": r.stderr[-300:],
                        "returncode": r.returncode, "timestamp": ts}
            except subprocess.TimeoutExpired:
                return {"success": False, "action": action, "error": "Timeout 300s", "timestamp": ts}
            except Exception as e:
                return {"success": False, "action": action, "error": str(e), "timestamp": ts}

        else:
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": [
                                  "cortex.get", "cortex.update", "cortex.reset",
                                  "cortex.get_full", "cortex.get_section", "cortex.get_aliases",
                                  "cortex.get_workflows", "cortex.validate_alias",
                                  "lobe.list", "lobe.get", "lobe.activate", "lobe.search",
                                  "lobe.list_active", "lobe.list_all", "lobe.get_content", "lobe.deactivate",
                                  "lobe.populate",
                                  "knowledge.search", "knowledge.store",
                                  "manifest.generate", "manifest.list",
                                  "manifest.update", "manifest.query", "manifest.generate_all",
                                  "search.advanced",
                                  "lexico.build", "lexico.search", "lexico.stats",
                                  "semantic.categorize"],
                    "timestamp": ts}


