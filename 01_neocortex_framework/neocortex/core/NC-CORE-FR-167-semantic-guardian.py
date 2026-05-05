"""---
@Guard NC-CORE-FR-167-semantic-guardian mcp NC-CORE-FR-167-semantic-guardian.py — R119: Semant
---
"""

import json
import os
import pathlib
from datetime import datetime
from typing import Dict


class SemanticGuardian:
    """Vigia da saude semantica — lobes, catalog, memory, routers."""

    def __init__(self, root: pathlib.Path = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self._last_check = None

    def full_health_check(self) -> Dict:
        self._last_check = datetime.now()
        return {
            "lobe_health": self.check_lobe_health(),
            "catalog_sync": self.check_catalog_sync(),
            "memory_health": self.check_memory_health(),
            "router_health": self.check_router_health(),
            "encoding_health": self.check_encoding_health(),
            "timestamp": self._last_check.isoformat(),
        }

    def check_lobe_health(self) -> Dict:
        """Verifica integridade dos lobes."""
        lobes_dir = self.root / "02_memory_lobes"
        lobes = list(lobes_dir.rglob("*.mdc"))
        issues = []
        empty_lobes = []
        no_header = []

        for l in lobes:
            size = l.stat().st_size
            content = ""
            if size == 0:
                empty_lobes.append(l.name)
                continue
            try:
                content = l.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                issues.append({"file": l.name, "error": str(e)})
                continue
            if not content.strip().startswith("---"):
                no_header.append(l.name)
            if "\ufffd" in content:
                issues.append({"file": l.name, "error": "CORRUPTED_ENCODING (U+FFFD)"})

        return {
            "total": len(lobes),
            "healthy": len(lobes) - len(empty_lobes) - len(issues),
            "empty": empty_lobes,
            "no_header": no_header[:10],
            "corrupted": issues,
            "domains": len({l.parent.relative_to(lobes_dir).as_posix() for l in lobes}),
            "status": "HEALTHY" if not empty_lobes and not issues else "NEEDS_ATTENTION",
        }

    def check_catalog_sync(self) -> Dict:
        """Verifica se catalogo = disco."""
        cat_file = self.root / "01_neocortex_framework" / ".neocortex" / "lexico" / "NC-LEXICO-LATEST.json"
        catalog_lobes = 0
        if cat_file.exists():
            catalog_lobes = json.loads(cat_file.read_text(encoding="utf-8")).get("total_lobes", 0)
        on_disk = len(list((self.root / "02_memory_lobes").rglob("*.mdc")))
        synced = catalog_lobes == on_disk
        return {
            "catalog": catalog_lobes,
            "disk": on_disk,
            "synced": synced,
            "drift": abs(catalog_lobes - on_disk),
            "status": "SYNCED" if synced else "DRIFT DETECTED",
        }

    def check_memory_health(self) -> Dict:
        """Verifica saude da memoria de sessoes."""
        mem_dir = self.root / ".neocortex" / "memory" / "sessions"
        sessions = list(mem_dir.glob("*.jsonl")) if mem_dir.exists() else []
        total_turns = 0
        stale_sessions = []
        now = datetime.now()
        for s in sessions:
            turns = len(s.read_text(encoding="utf-8", errors="ignore").splitlines())
            total_turns += turns
            age_days = (now - datetime.fromtimestamp(s.stat().st_mtime)).days
            if age_days > 7 and turns == 0:
                stale_sessions.append(s.name)

        watcher_stats = {}
        wf = self.root / ".neocortex" / "watcher" / "watcher_stats.json"
        if wf.exists():
            watcher_stats = json.loads(wf.read_text(encoding="utf-8")).get("stats", {})

        return {
            "sessions": len(sessions),
            "total_turns": total_turns,
            "stale_sessions": stale_sessions,
            "watcher_checks": watcher_stats.get("total_checks", 0),
            "status": "ACTIVE" if sessions else "NO_SESSIONS",
        }

    def check_router_health(self) -> Dict:
        """Verifica se domain routers estao funcionando."""
        router_file = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-166-domain-routers.py"
        if not router_file.exists():
            return {"available": False, "status": "NOT_DEPLOYED"}

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("dr", str(router_file))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            idx = mod.get_central_index()
            st = idx.status()
            return {
                "available": True,
                "domains": st["total_domains"],
                "items_indexed": st["total_indexed"],
                "status": "OPERATIONAL",
            }
        except Exception as e:
            return {"available": True, "error": str(e), "status": "ERROR"}

    def check_encoding_health(self) -> Dict:
        """Detecta corrupcao de encoding (acentos, UTF-8)."""
        fw = self.root / "01_neocortex_framework" / "neocortex"
        issues = []
        scanned = 0
        for f in fw.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            scanned += 1
            try:
                content = f.read_text(encoding="utf-8")
                if "\ufffd" in content:
                    issues.append(str(f.relative_to(self.root)))
            except UnicodeDecodeError:
                issues.append(str(f.relative_to(self.root)))
        return {
            "files_scanned": scanned,
            "encoding_issues": issues,
            "issue_count": len(issues),
            "status": "CLEAN" if not issues else f"{len(issues)} CORRUPTED",
        }


_guardian = None


def get_guardian():
    global _guardian
    if _guardian is None:
        _guardian = SemanticGuardian()
    return _guardian
