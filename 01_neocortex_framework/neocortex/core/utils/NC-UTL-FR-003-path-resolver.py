"""---
@Module NC-UTL-FR-003-path-resolver mcp _genealogy:   injected_at: '2026-04-16T00:23:59.15
---
"""


"""
NC-UTL-FR-003-path-resolver.py
UTIL-003  PathResolver: resoluo de paths respeitando get_config()
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PathResolver:
    """Resolve caminhos de recursos NeoCortex usando get_config() como ncora."""

    def __init__(self):
        from neocortex.config import get_config

        self._cfg = get_config()

    def resolve_ticket_path(self, ticket_id: str) -> Path | None:
        """Busca ticket YAML em DIR-DS-001-tickets/NC-{ticket_id}-*.yaml"""
        # Padro: DIR-DS-001-tickets/NC-DS-NNN-*.yaml
        tickets_dir = self._cfg.project_root / "DIR-DS-001-tickets"
        if not tickets_dir.exists():
            return None

        # Ensure ticket_id starts with NC-? If not, add prefix NC-
        if not ticket_id.startswith("NC-"):
            ticket_id = f"NC-{ticket_id}"

        # Exact match with .yaml extension
        exact_path = tickets_dir / f"{ticket_id}.yaml"
        if exact_path.exists():
            return exact_path

        # Pattern match: NC-DS-NNN-*.yaml (where ticket_id already includes NC-)
        pattern = f"{ticket_id}-*.yaml"
        candidates = []
        for path in tickets_dir.glob(pattern):
            if path.is_file():
                candidates.append(path)

        if not candidates:
            return None

        # If multiple matches, return first alphabetically
        candidates.sort(key=lambda p: p.name)
        return candidates[0]

    def resolve_handoff_path(self, ticket_id: str) -> Path | None:
        """Busca handoff mais recente em DIR-DS-002-audit-logs/ para o ticket."""
        # Padro: NC-{ticket_id}-handoff-*.yaml  retorna o mais recente por mtime
        audit_logs_dir = self._cfg.project_root / "DIR-DS-002-audit-logs"
        if not audit_logs_dir.exists():
            return None

        # Ensure ticket_id starts with NC-? If not, add prefix NC-
        if not ticket_id.startswith("NC-"):
            ticket_id = f"NC-{ticket_id}"

        candidates = []
        pattern = f"{ticket_id}-handoff-*.yaml"
        for path in audit_logs_dir.glob(pattern):
            if path.is_file():
                candidates.append(path)

        if not candidates:
            return None

        # Sort by modification time, most recent first
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return candidates[0]

    def resolve_lobe_path(self, lobe_name: str) -> Path | None:
        """Busca .mdc em 01_neocortex_framework/lobes/ ou 02_memory_lobes/"""
        # Try 01_neocortex_framework/lobes/
        lobes_dir1 = self._cfg.project_root / "01_neocortex_framework" / "lobes"
        if lobes_dir1.exists():
            for ext in (".mdc", ".md", ".yaml", ".yml"):
                path = lobes_dir1 / f"{lobe_name}{ext}"
                if path.exists():
                    return path
                # glob for subdirectories
                for found in lobes_dir1.glob(f"**/{lobe_name}{ext}"):
                    if found.is_file():
                        return found

        # Try 02_memory_lobes/
        lobes_dir2 = self._cfg.project_root / "02_memory_lobes"
        if lobes_dir2.exists():
            for ext in (".mdc", ".md", ".yaml", ".yml"):
                path = lobes_dir2 / f"{lobe_name}{ext}"
                if path.exists():
                    return path
                for found in lobes_dir2.glob(f"**/{lobe_name}{ext}"):
                    if found.is_file():
                        return found

        return None

    def resolve_tool_path(self, tool_name: str) -> Path | None:
        """Busca tool em neocortex/mcp/tools/NC-TOOL-FR-*-{tool_name}.py"""
        tools_dir = (
            self._cfg.project_root
            / "01_neocortex_framework"
            / "neocortex"
            / "mcp"
            / "tools"
        )
        if not tools_dir.exists():
            return None

        # Remove .py extension if present
        if tool_name.endswith(".py"):
            tool_name = tool_name[:-3]

        # Pattern: NC-TOOL-FR-*-{tool_name}.py
        pattern = f"NC-TOOL-FR-*-{tool_name}.py"
        candidates = []
        for path in tools_dir.glob(pattern):
            if path.is_file():
                candidates.append(path)

        if not candidates:
            # Fallback: exact match
            exact_path = tools_dir / f"{tool_name}.py"
            if exact_path.exists():
                return exact_path
            return None

        # If multiple, return first alphabetically
        candidates.sort(key=lambda p: p.name)
        return candidates[0]

    def list_zone_files(self, write_zone: str) -> list[Path]:
        """Lista arquivos Python em uma write_zone (path relativo ao root)."""
        if not write_zone:
            return []

        zone_path = Path(write_zone)
        if not zone_path.is_absolute():
            zone_path = self._cfg.project_root / zone_path

        if not zone_path.exists():
            return []

        if zone_path.is_file():
            # If it's a single file, check if it's Python
            if zone_path.suffix == ".py":
                return [zone_path]
            return []

        # It's a directory, list all Python files recursively
        files = []
        for path in zone_path.rglob("*.py"):
            if path.is_file():
                files.append(path)

        return files

    def get_root(self) -> Path:
        """Retorna root do projeto via get_config()."""
        return self._cfg.project_root


# Singleton instance
_path_resolver_instance = None


def get_path_resolver() -> PathResolver:
    """Singleton do PathResolver."""
    global _path_resolver_instance
    if _path_resolver_instance is None:
        _path_resolver_instance = PathResolver()
    return _path_resolver_instance
