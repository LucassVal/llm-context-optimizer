"""---
@Guard NC-CORE-FR-168-semantic-audit mcp NC-CORE-FR-168-semantic-audit.py — Deep Semantic C
---
"""

import os
import pathlib
import re
from collections import defaultdict
from datetime import datetime


class SemanticAuditEngine:
    def __init__(self, root: pathlib.Path | None = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))

    def deep_audit(self) -> dict:
        core = self.root / "01_neocortex_framework" / "neocortex" / "core"
        tools = self.root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"

        all_files = {}
        nc_to_file = {}
        for d in [core, tools]:
            for f in sorted(d.glob("*.py")):
                if f.name.startswith("_"): continue
                rel = str(f.relative_to(self.root))
                content = f.read_text("utf-8", errors="ignore")
                all_files[rel] = {"content": content, "size": len(content.split("\n"))}
                nc_match = re.search(r'(NC-(?:CORE|SUPER|SVC|UTL|TOOL)-FR-\d+[\w-]*)', f.name)
                if nc_match:
                    nc_to_file[nc_match.group(1)] = rel

        # 1. REDUNDANCIES: files with same import set
        refs_by_file = {}
        for rel, data in all_files.items():
            refs = set(re.findall(r'NC-(?:CORE|SUPER|SVC|UTL|TOOL)-FR-\d+[\w-]*', data["content"]))
            refs.discard(nc_to_file.get(rel, ""))
            if refs:
                refs_by_file[rel] = frozenset(refs)
        red_groups = defaultdict(list)
        for rel, refs in refs_by_file.items():
            red_groups[refs].append(rel)
        redundancies = [{"imports": sorted(refs)[:5], "files": files, "count": len(files)}
                       for refs, files in red_groups.items() if len(files) > 1]

        # 2. ORPHANS: no refs in or out
        referenced_by = defaultdict(set)
        for rel, refs in refs_by_file.items():
            for ref_nc in refs:
                if ref_nc in nc_to_file:
                    referenced_by[nc_to_file[ref_nc]].add(rel)
        has_out = set(refs_by_file.keys())
        has_in = set(referenced_by.keys())
        orphans = sorted([rel for rel in all_files if rel not in has_out and rel not in has_in])

        # 3. FRAGMENTATION: files in same domain with similar names
        fragments = []
        name_groups = defaultdict(list)
        for rel in all_files:
            base = rel.split("/")[-1].split(".")[0].lower().replace("-", "_").replace("nc_core_fr_", "")
            # Extract core topic (remove NC- prefix and numbers)
            topic = re.sub(r'nc_\w+_fr_\d+_?', '', base)
            if topic:
                name_groups[topic].append(rel)
        for topic, files in name_groups.items():
            if len(files) > 1:
                fragments.append({"topic": topic, "files": files})

        # 4. MOST REFERENCED
        top_refs = sorted(referenced_by.items(), key=lambda x: -len(x[1]))[:5]

        return {
            "files_analyzed": len(all_files),
            "redundancies": len(redundancies),
            "redundancy_details": redundancies[:5],
            "orphans": len(orphans),
            "orphan_details": orphans[:15],
            "fragments": len(fragments),
            "fragment_details": fragments[:10],
            "most_referenced": [{"file": rel.split("/")[-1], "count": len(refs)} for rel, refs in top_refs],
            "recommendation": self._recommend(orphans, redundancies, fragments),
            "timestamp": datetime.now().isoformat(),
        }

    def _recommend(self, orphans, redundancies, fragments) -> str:
        recs = []
        if orphans:
            recs.append(f"{len(orphans)} orfaos: revisar para arquivar (R05) ou conectar")
        if redundancies:
            recs.append(f"{len(redundancies)} grupos redundantes: migrar para SemanticRouter (FR-166)")
        if fragments:
            recs.append(f"{len(fragments)} fragmentacoes: avaliar merge")
        return "; ".join(recs) if recs else "Sistema semanticamente integro"


_audit_engine = None
def get_semantic_audit():
    global _audit_engine
    if _audit_engine is None: _audit_engine = SemanticAuditEngine()
    return _audit_engine
