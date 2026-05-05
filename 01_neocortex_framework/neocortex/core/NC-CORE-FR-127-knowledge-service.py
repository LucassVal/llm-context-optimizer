"""---
@Service NC-CORE-FR-127-knowledge-service mcp NC-CORE-FR-127-knowledge-service.py — KnowledgeSer
---
"""


import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class KnowledgeService:
    """Real knowledge service — stores and retrieves knowledge entries on disk."""

    def __init__(self, root: Path | None = None):
        import os as _os
        self.root = root or Path(_os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.store_dir = self.root / ".neocortex" / "knowledge"
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def search(self, query: str, limit: int = 10) -> list:
        """Search knowledge entries. Falls back to SearchService."""
        results = []
        patterns = query.lower().split()

        try:
            from .NC_CORE_FR_126_search_service import get_search_service
            svc = get_search_service()
            r = svc.search_advanced(query, limit)
            return r.get("results", [])

        except Exception:
            pass

        # Direct file search
        if self.store_dir.exists():
            for f in self.store_dir.rglob("*.json"):
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    matches = sum(1 for p in patterns if p in content.lower())
                    if matches > 0:
                        import json
                        data = json.loads(content)
                        results.append({
                            "key": f.stem,
                            "content": str(data.get("content", ""))[:200],
                            "matches": matches,
                        })
                except Exception:
                    pass

        results.sort(key=lambda r: r.get("matches", 0), reverse=True)
        return results[:limit]

    def store(self, key: str, content: str, tag: str = "") -> dict[str, Any]:
        """Store a knowledge entry."""
        import json
        entry = {
            "key": key,
            "content": content,
            "tag": tag,
            "stored_at": __import__("datetime").datetime.now().isoformat(),
        }
        fname = self.store_dir / f"{key}.json"
        fname.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"success": True, "key": key, "file": str(fname)}


# Singleton
_knowledge_service_instance: KnowledgeService | None = None


def get_knowledge_service(root: Path | None = None) -> KnowledgeService:
    global _knowledge_service_instance
    if _knowledge_service_instance is None:
        _knowledge_service_instance = KnowledgeService(root)
    return _knowledge_service_instance
