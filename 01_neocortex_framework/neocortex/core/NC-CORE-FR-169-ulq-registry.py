"""---
NC-CORE-FR-169-ulq-registry.py — ULQ Auto-Registry + Deep Cross-Reference
- File watcher: auto-registra novos arquivos no catalogo
- ULQ-aware cross-reference: usa tags @Engine @Tool etc para achar conexoes
- Detecta: orfaos, semi-orfaos, duplicatas, fragmentos, refs quebradas
---
"""
import hashlib
import json
import os
import pathlib
import re
from collections import defaultdict
from datetime import datetime


class ULQRegistry:
    """Auto-registro de novos arquivos + cross-reference ULQ-aware."""

    def __init__(self, root: pathlib.Path | None = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self._last_sync = None

    def auto_register(self) -> dict:
        """Detecta novos arquivos e registra no catalogo."""
        catalog_file = self.root / "01_neocortex_framework" / ".neocortex" / "lexico" / "NC-LEXICO-LATEST.json"
        if not catalog_file.exists():
            return {"error": "catalog not found"}

        catalog = json.loads(catalog_file.read_text(encoding="utf-8"))
        registered = set()
        for _dom, data in catalog.get("domains", {}).items():
            for lobe in data.get("lobes", []):
                registered.add(lobe["name"] if isinstance(lobe, dict) else lobe)

        # Scan for new files
        new_files = []
        for d in [
            self.root / "01_neocortex_framework" / "neocortex" / "core",
            self.root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools",
            self.root / "02_memory_lobes",
        ]:
            if not d.exists():
                continue
            for f in d.rglob("*"):
                if f.is_dir() or "__pycache__" in str(f):
                    continue
                if f.suffix in (".py", ".mdc", ".yaml"):
                    if f.name not in registered and not f.name.startswith("_"):
                        new_files.append({
                            "name": f.name,
                            "path": str(f.relative_to(self.root)),
                            "type": f.suffix,
                            "size": f.stat().st_size,
                        })

        return {
            "new_files": len(new_files),
            "details": new_files[:20],
            "total_registered": len(registered),
            "timestamp": datetime.now().isoformat(),
        }

    def cross_reference(self) -> dict:
        """ULQ-aware cross-reference: usa @tags + NC-IDs para mapear conexoes."""
        fw = self.root / "01_neocortex_framework" / "neocortex"

        # 1. Index all files with ULQ tags
        file_index = {}
        ulq_tags = {}
        for d in [fw / "core", fw / "mcp" / "tools"]:
            if not d.exists():
                continue
            for f in sorted(d.glob("*.py")):
                if f.name.startswith("_"):
                    continue
                rel = str(f.relative_to(self.root))
                content = f.read_text("utf-8", errors="ignore")
                # Extract @Tags from header
                tags = set(re.findall(r'@(\w+)', content[:500]))
                # Extract NC-IDs referenced
                refs = set(re.findall(r'NC-(?:CORE|SUPER|SVC|UTL|TOOL)-FR-\d+[\w-]*', content))
                # Extract self NC-ID
                self_id = re.search(r'(NC-(?:CORE|SUPER|SVC|UTL|TOOL)-FR-\d+[\w-]*)', f.name)
                self_nc = self_id.group(1) if self_id else None
                file_index[rel] = {"tags": tags, "refs": refs, "self_nc": self_nc, "hash": hashlib.md5(content.encode()).hexdigest()[:12]}
                for tag in tags:
                    if tag not in ulq_tags:
                        ulq_tags[tag] = []
                    ulq_tags[tag].append(rel)

        # 2. Find orphans (no incoming refs)
        all_refs = set()
        for rel, data in file_index.items():
            for ref in data["refs"]:
                all_refs.add(ref)
        orphans = []
        for rel, data in file_index.items():
            if data["self_nc"] and data["self_nc"] not in all_refs and len(data["refs"]) == 0:
                orphans.append(rel)

        # 3. Find duplicates (same functionality via @tags)
        dup_candidates = defaultdict(list)
        for rel, data in file_index.items():
            tag_key = frozenset(data["tags"])
            if tag_key:
                dup_candidates[tag_key].append(rel)
        duplicates = [(tags, files) for tags, files in dup_candidates.items() if len(files) > 1 and len(tags) >= 2]

        # 4. Find broken refs (reference non-existent NC-IDs)
        all_nc_ids = {data["self_nc"] for data in file_index.values() if data["self_nc"]}
        broken_refs = defaultdict(set)
        for rel, data in file_index.items():
            for ref in data["refs"]:
                if ref not in all_nc_ids:
                    broken_refs[rel].add(ref)
        broken = [(rel, sorted(refs)) for rel, refs in broken_refs.items() if refs]

        # 5. Find fragments (complementary @tags)
        tag_pairs = defaultdict(list)
        for tag, files in ulq_tags.items():
            if tag in ("Engine", "Service", "Tool", "Gateway"):
                for f in files:
                    tag_pairs[tag].append(f)
        fragments = [(tag, files) for tag, files in tag_pairs.items() if len(files) >= 3]

        return {
            "files_analyzed": len(file_index),
            "ulq_tags_found": len(ulq_tags),
            "tag_distribution": {tag: len(files) for tag, files in sorted(ulq_tags.items(), key=lambda x: -len(x[1]))[:10]},
            "orphans": len(orphans),
            "orphan_details": orphans[:15],
            "duplicates": len(duplicates),
            "duplicate_details": [{"tags": sorted(t), "files": f} for t, f in duplicates[:5]],
            "broken_refs": len(broken),
            "broken_details": [{"file": rel, "missing_refs": refs} for rel, refs in broken[:10]],
            "fragments": len(fragments),
            "fragment_details": [{"tag": t, "files": f[:8]} for t, f in fragments[:5]],
            "recommendation": self._summary(orphans, duplicates, broken, fragments),
            "timestamp": datetime.now().isoformat(),
        }

    def _summary(self, orphans, dupes, broken, frags):
        parts = []
        if orphans: parts.append(f"{len(orphans)} orfaos")
        if dupes: parts.append(f"{len(dupes)} duplicatas")
        if broken: parts.append(f"{len(broken)} refs quebradas")
        if frags: parts.append(f"{len(frags)} fragmentos")
        return "; ".join(parts) if parts else "Sistema integro"


_registry = None
def get_ulq_registry():
    global _registry
    if _registry is None: _registry = ULQRegistry()
    return _registry
