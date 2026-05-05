"""---
NC-CORE-FR-171-due-diligence-strangler.py — P0: R59 + R68
Due Diligence: hash validation of new modules before loading
Strangler Fig: wire migration tracker into PulseScheduler
---
"""
import hashlib
import json
import os
import pathlib
from datetime import datetime
from typing import Dict


class DueDiligence:
    """R59 H: Valida integridade de novos modulos antes de carregar."""

    def __init__(self, root: pathlib.Path = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self._registry_file = self.root / ".neocortex" / "state" / "NC-STATE-DUE-DILIGENCE.json"
        self._registry_file.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self):
        if self._registry_file.exists():
            try:
                self._known_hashes = json.loads(self._registry_file.read_text("utf-8"))
            except:
                self._known_hashes = {}
        else:
            self._known_hashes = {}

    def _save(self):
        self._registry_file.write_text(json.dumps(self._known_hashes, indent=2), encoding="utf-8")

    def validate_module(self, filepath: str) -> Dict:
        """Valida integridade de modulo antes de carregar."""
        fp = self.root / filepath if not filepath.startswith(str(self.root)) else pathlib.Path(filepath)
        if not fp.exists():
            return {"approved": False, "reason": "FILE_NOT_FOUND", "rule": "R59"}

        content = fp.read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()[:16]
        rel = str(fp.relative_to(self.root))

        if rel in self._known_hashes:
            known = self._known_hashes[rel]
            if known["hash"] != file_hash:
                return {"approved": False, "reason": "HASH_MISMATCH: file modified without registry update",
                        "expected": known["hash"], "actual": file_hash, "rule": "R59"}
            return {"approved": True, "hash": file_hash, "verified": True, "rule": "R59"}

        # New file: register
        self._known_hashes[rel] = {"hash": file_hash, "registered_at": datetime.now().isoformat(),
                                     "size": len(content)}
        self._save()
        return {"approved": True, "hash": file_hash, "new_registration": True, "rule": "R59"}

    def scan_all(self) -> Dict:
        """Verifica todos os modulos registrados."""
        fw = self.root / "01_neocortex_framework" / "neocortex"
        verified, modified, new_files = 0, 0, 0
        for f in fw.rglob("NC-*.py"):
            if "__pycache__" in str(f):
                continue
            rel = str(f.relative_to(self.root))
            result = self.validate_module(rel)
            if result["approved"]:
                if result.get("new_registration"):
                    new_files += 1
                else:
                    verified += 1
            else:
                modified += 1
        return {"verified": verified, "modified": modified, "new": new_files,
                "total": verified + modified + new_files, "timestamp": datetime.now().isoformat()}


class StranglerFigWire:
    """R68 H+S: Wire migration tracker no PulseScheduler."""

    def __init__(self, root: pathlib.Path = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))

    def track_migration(self) -> Dict:
        """Track progresso de migracao para MCP."""
        tools_dir = self.root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"
        core_dir = self.root / "01_neocortex_framework" / "neocortex" / "core"

        mcp_tools = len(list(tools_dir.glob("NC-SUPER-*.py"))) if tools_dir.exists() else 0
        gw_wired = sum(1 for t in tools_dir.glob("NC-SUPER-*.py")
                      if "gateway_check" in t.read_text("utf-8", errors="ignore")) if tools_dir.exists() else 0

        nc_files = len(list(core_dir.glob("NC-CORE-FR-*.py"))) if core_dir.exists() else 0
        non_nc = len([f for f in core_dir.glob("*.py")
                     if not f.name.startswith("NC-") and f.name != "__init__.py"]) if core_dir.exists() else 0

        total = nc_files + non_nc
        migrated_pct = round(nc_files / max(total, 1) * 100, 1)

        tracker_file = self.root / ".neocortex" / "state" / "NC-STATE-STRANGLER-FIG.json"
        data = {
            "mcp_tools": mcp_tools,
            "mcp_gw_wired": gw_wired,
            "core_nc_files": nc_files,
            "core_non_nc": non_nc,
            "migration_pct": migrated_pct,
            "principle": "Substituir hardcoded -> MCP um a um sem downtime",
            "updated_at": datetime.now().isoformat(),
        }
        tracker_file.parent.mkdir(parents=True, exist_ok=True)
        tracker_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data


_dd = None
_sw = None


def get_due_diligence():
    global _dd
    if _dd is None: _dd = DueDiligence()
    return _dd


def get_strangler_wire():
    global _sw
    if _sw is None: _sw = StranglerFigWire()
    return _sw
