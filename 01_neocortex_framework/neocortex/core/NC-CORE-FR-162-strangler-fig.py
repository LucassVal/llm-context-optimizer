"""---
@Code NC-CORE-FR-162-strangler-fig mcp NC-CORE-FR-162-strangler-fig.py — R68 Strangler Fi
---
"""


import json
import os
import pathlib
from datetime import datetime


class StranglerFig:
    """Migration tracker: ferramentas hardcoded -> MCP."""

    def __init__(self, root: pathlib.Path | None = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self._tracker_file = self.root / ".neocortex" / "state" / "NC-STATE-STRANGLER-FIG.json"

    def scan(self) -> dict:
        tools_dir = self.root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"
        total_tools = len(list(tools_dir.glob("NC-SUPER-*.py"))) if tools_dir.exists() else 0
        gw_wired = sum(1 for t in tools_dir.glob("NC-SUPER-*.py") if "gateway_check" in t.read_text(encoding="utf-8", errors="ignore")) if tools_dir.exists() else 0

        # Legacy files with NC- prefix (migrated) vs without (not migrated)
        core_dir = self.root / "01_neocortex_framework" / "neocortex" / "core"
        nc_files = len(list(core_dir.glob("NC-CORE-FR-*.py"))) if core_dir.exists() else 0
        non_nc_files = len([f for f in core_dir.glob("*.py") if not f.name.startswith("NC-") and f.name != "__init__.py"]) if core_dir.exists() else 0

        migrated = nc_files
        remaining = non_nc_files
        total = migrated + remaining
        pct = round(migrated / max(total, 1) * 100, 1)

        result = {
            "mcp_tools_wired": f"{gw_wired}/{total_tools}",
            "core_files_migrated": f"{migrated}/{total} ({pct}%)",
            "legacy_remaining": remaining,
            "principle": "Substituir endpoints um a um sem downtime",
            "timestamp": datetime.now().isoformat(),
        }

        self._tracker_file.parent.mkdir(parents=True, exist_ok=True)
        self._tracker_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result


_strangler = None
def get_strangler():
    global _strangler
    if _strangler is None: _strangler = StranglerFig()
    return _strangler
