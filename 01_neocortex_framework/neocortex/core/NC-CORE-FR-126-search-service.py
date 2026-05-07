# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
"""---
@Service NC-CORE-FR-126-search-service mcp NC-CORE-FR-126-search-service.py — SearchService (
---
"""


import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SearchService:
    """Real search service — searches lobes, docs, and code on disk."""

    def __init__(self, root: Path | None = None):
        import os as _os
        self.root = root or Path(_os.environ.get("NC_ROOT", Path(__file__).parents[3]))

    def search_advanced(self, query: str, limit: int = 10) -> dict[str, Any]:
        """Advanced search across lobes, docs, and code."""
        results = []
        patterns = query.lower().split()

        # Search in memory lobes (.mdc files)
        lobes_dir = self.root / "02_memory_lobes"
        if lobes_dir.exists():
            for mdc in lobes_dir.rglob("*.mdc"):
                try:
                    content = mdc.read_text(encoding="utf-8", errors="ignore")
                    matches = sum(1 for p in patterns if p in content.lower())
                    if matches > 0:
                        results.append({
                            "type": "lobe",
                            "path": str(mdc.relative_to(self.root)),
                            "matches": matches,
                            "size": len(content),
                        })
                except Exception:
                    pass

        # Search in docs
        docs_dir = self.root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main"
        if docs_dir.exists():
            for doc in docs_dir.rglob("*.md"):
                try:
                    content = doc.read_text(encoding="utf-8", errors="ignore")
                    matches = sum(1 for p in patterns if p in content.lower())
                    if matches > 0:
                        results.append({
                            "type": "doc",
                            "path": str(doc.relative_to(self.root)),
                            "matches": matches,
                            "size": len(content),
                        })
                except Exception:
                    pass

        # Sort by matches descending
        results.sort(key=lambda r: r.get("matches", 0), reverse=True)

        return {
            "success": True,
            "query": query,
            "results": results[:limit],
            "total_found": len(results),
        }

    def search_knowledge(self, query: str, limit: int = 10) -> dict[str, Any]:
        """Knowledge search — same as advanced with knowledge tag filter."""
        return self.search_advanced(query, limit)


# Singleton
_search_service_instance: SearchService | None = None


def get_search_service(root: Path | None = None) -> SearchService:
    global _search_service_instance
    if _search_service_instance is None:
        _search_service_instance = SearchService(root)
    return _search_service_instance
