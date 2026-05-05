"""---
NC-CORE-FR-170-semantic-boot.py — Semantic Boot Sequence Engine
1. ULQ lookup -> 2. TAG index -> 3. PREP action
Auto-registry + Decay mechanism.
---
"""
import json
import os
import pathlib
import re
from collections import defaultdict
from datetime import datetime


class SemanticBootEngine:
    """Executa a sequencia de boot semantica: ULQ -> TAGS -> PREP."""

    def __init__(self, root: pathlib.Path | None = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self.lexico_dir = self.root / "01_neocortex_framework" / ".neocortex" / "lexico"
        self.lexico_dir.mkdir(parents=True, exist_ok=True)
        self._tag_index_cache = None
        self._ulq_cache = None

    # ── STEP 1: ULQ LOOKUP ────────────────────────────────────

    def ulq_lookup(self, term: str) -> dict | None:
        """Consulta ULQ para definicao de um termo."""
        ulq_file = self.root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-DOC-FR-001-ubiquitous-language-dictionary.md"
        if not ulq_file.exists():
            return None
        if not self._ulq_cache:
            self._ulq_cache = ulq_file.read_text("utf-8", errors="ignore")
        for line in self._ulq_cache.split("\n"):
            if term.lower() in line.lower() and "|" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3:
                    return {"term": term, "definition": parts[2] if len(parts) > 2 else parts[1], "source": "ULQ"}
        return None

    # ── STEP 2: TAG INDEX ─────────────────────────────────────

    def build_tag_index(self) -> dict:
        """Constroi indice de @Tags de todos os arquivos."""
        fw = self.root / "01_neocortex_framework" / "neocortex"
        tag_index = defaultdict(list)
        for d in [fw / "core", fw / "mcp" / "tools"]:
            if not d.exists():
                continue
            for f in sorted(d.glob("*.py")):
                if f.name.startswith("_"):
                    continue
                content = f.read_text("utf-8", errors="ignore")
                tags = re.findall(r'@(\w+)', content[:500])
                nc_id = re.search(r'(NC-(?:CORE|SUPER|SVC|UTL|TOOL)-FR-\d+[\w-]*)', f.name)
                entry = {
                    "file": f.name,
                    "path": str(f.relative_to(self.root)),
                    "nc_id": nc_id.group(1) if nc_id else None,
                    "tags": tags,
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                }
                for tag in tags:
                    tag_index[tag].append(entry)
                if not tags:
                    tag_index["@Untagged"].append(entry)

        # Save index
        index_file = self.lexico_dir / "NC-ULQ-TAG-INDEX.json"
        index_data = {"tags": dict(tag_index.items()), "total": sum(len(v) for v in tag_index.values()),
                       "generated_at": datetime.now().isoformat()}
        index_file.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")
        self._tag_index_cache = dict(tag_index)
        return {"total_tags": len(tag_index), "total_entries": sum(len(v) for v in tag_index.values()),
                "top_tags": sorted(tag_index.keys(), key=lambda k: len(tag_index[k]), reverse=True)[:10]}

    def tag_lookup(self, tag: str) -> list[dict]:
        """Encontra todos os arquivos com uma @tag."""
        if not self._tag_index_cache:
            self.build_tag_index()
        return self._tag_index_cache.get(tag, self._tag_index_cache.get("@" + tag, []))

    # ── STEP 3: PREP ──────────────────────────────────────────

    def prep(self, intent: str) -> dict:
        """Prepara acao baseada em intencao: 'KPI', 'audit', 'governance'."""
        # 1. ULQ lookup
        ulq_result = self.ulq_lookup(intent)
        # 2. Tag lookup
        tag_results = self.tag_lookup(intent)
        # 3. Return action plan
        return {
            "intent": intent,
            "ulq_definition": ulq_result,
            "matching_files": len(tag_results),
            "top_match": tag_results[0] if tag_results else None,
            "actions": self._suggest_actions(ulq_result, tag_results),
        }

    def _suggest_actions(self, ulq, tags):
        if not tags:
            return ["no_matching_files"]
        actions = []
        for t in tags:
            nc_id = t.get("nc_id", "")
            if "governance" in nc_id.lower():
                actions.append("MCP: neocortex_governance")
            elif "gateway" in nc_id.lower():
                actions.append("Gateway: validate_action()")
            elif "engine" in str(t.get("tags", [])):
                actions.append("Engine: importlib load")
        return actions or ["file_found"]

    # ── AUTO-REGISTRY ─────────────────────────────────────────

    def auto_register(self, filepath: str) -> dict:
        """Registra novo arquivo no indice de tags."""
        fp = self.root / filepath if not filepath.startswith(str(self.root)) else pathlib.Path(filepath)
        if not fp.exists():
            return {"error": "not_found"}
        content = fp.read_text("utf-8", errors="ignore")
        tags = re.findall(r'@(\w+)', content[:500])
        nc_id = re.search(r'(NC-(?:CORE|SUPER|SVC|UTL|TOOL)-FR-\d+[\w-]*)', fp.name)
        entry = {
            "file": fp.name,
            "path": filepath,
            "nc_id": nc_id.group(1) if nc_id else None,
            "tags": tags,
            "size": fp.stat().st_size,
            "registered_at": datetime.now().isoformat(),
        }
        # Update tag index
        for tag in tags:
            if tag not in self._tag_index_cache:
                self._tag_index_cache[tag] = []
            self._tag_index_cache[tag].append(entry)
        return {"registered": True, "tags": tags, "nc_id": entry["nc_id"]}

    # ── DECAY ─────────────────────────────────────────────────

    def decay_check(self, max_age_days: int = 7) -> dict:
        """Marca tags nao usadas como STALE."""
        decay_file = self.lexico_dir / "NC-DECAY-LOG.json"
        decay_log = json.loads(decay_file.read_text("utf-8")) if decay_file.exists() else {}
        now = datetime.now()
        stale = []
        for tag, entries in self._tag_index_cache.items():
            for e in entries:
                modified = datetime.fromisoformat(e["modified"])
                age = (now - modified).days
                if age > max_age_days and tag not in ("Module", "Engine", "Gateway", "Guard"):
                    stale.append({"tag": tag, "file": e["file"], "age_days": age})
        decay_log[now.strftime("%Y%m%d")] = {"stale_count": len(stale), "stale": stale}
        decay_file.write_text(json.dumps(decay_log, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"stale_tags": len(stale), "checked_at": now.isoformat(), "max_age_days": max_age_days}

    # ── FULL BOOT SEQUENCE ────────────────────────────────────

    def boot(self) -> dict:
        """Executa sequencia completa: ULQ -> TAGS -> PREP."""
        # 1. ULQ — carregar dicionario
        ulq_loaded = self.ulq_lookup("NeoCortex") is not None
        # 2. TAGS — construir indice
        tag_result = self.build_tag_index()
        # 3. PREP — exemplo de intent
        prep_result = self.prep("audit")
        return {
            "ulq_loaded": ulq_loaded,
            "tags_indexed": tag_result["total_entries"],
            "tags_count": tag_result["total_tags"],
            "prep_ready": prep_result["matching_files"] > 0,
            "timestamp": datetime.now().isoformat(),
        }


_boot_engine = None
def get_boot_engine():
    global _boot_engine
    if _boot_engine is None: _boot_engine = SemanticBootEngine()
    return _boot_engine
