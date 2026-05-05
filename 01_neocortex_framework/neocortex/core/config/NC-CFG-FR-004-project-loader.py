"""---
@Module NC-CFG-FR-004-project-loader mcp _genealogy:   injected_at: '2026-04-16T00:23:58.23
---
"""


"""
NC-CFG-FR-004-project-loader.py
FR-004  ProjectConfigLoader: Hierarchical configuration loader with .nc/config.yaml support.

Loads configuration with precedence: .nc/config.yaml > ~/.config/neocortex/config.yaml > defaults.
Respects @LOCKED fields and crossplatform XDG/APPDATA paths.
"""

import logging
import os
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir
from ruamel.yaml import YAML

logger = logging.getLogger(__name__)


# Fields that cannot be overridden by local config (protected by @LOCKED)
LOCKED_FIELDS = {"server_port", "sub_server_port", "log_level", "database_path"}


class ProjectConfigLoader:
    """
    Hierarchical configuration loader for NeoCortex projects.

    Precedence (highest to lowest):
        1. .nc/config.yaml (in current directory or parent hierarchy)
        2. ~/.config/neocortex/config.yaml (or %APPDATA%/neocortex/config.yaml)
        3. Default values (provided as fallback)
    """

    def __init__(
        self,
        project_root: Path | None = None,
        defaults: dict[str, Any] | None = None,
    ):
        """
        Initialize loader with optional project root and defaults.

        Args:
            project_root: Root directory of the project (searches for .nc/config.yaml).
            defaults: Default configuration values (lowest precedence).
        """
        self.defaults = defaults or {}
        self._config: dict[str, Any] = {}
        self._project_path: Path | None = None
        self._global_path: Path | None = None
        self._yaml = YAML()
        self._yaml.preserve_quotes = True
        if project_root is not None:
            self.load(project_root)

    def load(self, project_root: Path | None = None) -> dict[str, Any]:
        """
        Load configuration merging all sources.

        Args:
            project_root: Project root directory to search for .nc/config.yaml.
                          If None, uses current working directory.

        Returns:
            Merged configuration dictionary.
        """
        if project_root is None:
            project_root = Path.cwd()
        elif isinstance(project_root, str):
            project_root = Path(project_root)

        # 1. Load global config (XDG/APPDATA)
        global_config = self._load_global_config()
        # 2. Load project config (if any)
        project_config = self._load_project_config(project_root)
        # 3. Merge with defaults
        merged = self._merge_all(global_config, project_config)
        self._config = merged
        return merged

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (dotnotation supported).

        Args:
            key: Configuration key, e.g., "server.host" or "log_level".
            default: Value to return if key not found.

        Returns:
            Configuration value or default.
        """
        if not self._config:
            self.reload()

        # Support dot notation for nested keys
        parts = key.split(".")
        value = self._config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        return value

    def get_global_path(self) -> Path:
        """
        Get path to global configuration file.

        Returns:
            Path to global config.yaml (XDG/APPDATA location).
        """
        if self._global_path is None:
            config_dir = os.environ.get("NEOCORTEX_CONFIG_DIR")
            if config_dir:
                self._global_path = Path(config_dir) / "config.yaml"
            else:
                # platformdirs handles Windows APPDATA and Linux/Mac XDG
                config_dir = user_config_dir("neocortex")
                self._global_path = Path(config_dir) / "config.yaml"
        return self._global_path

    def get_project_path(self) -> Path | None:
        """
        Get path to project .nc/config.yaml (if found).

        Returns:
            Path to project config.yaml, or None if not found.
        """
        return self._project_path

    def get_config_path(self) -> Path | None:
        """
        Retorna path do .nc/config.yaml ativo (None se no existir).
        """
        return self._project_path

    def reload(self) -> dict[str, Any]:
        """
        Reload configuration from disk (without changing project root).
        Returns merged configuration.
        """
        project_root = self._project_path.parent if self._project_path else None
        return self.load(project_root)

    def _load_global_config(self) -> dict[str, Any]:
        """Load global configuration from XDG/APPDATA location."""
        global_path = self.get_global_path()
        if not global_path.exists():
            logger.debug(f"Global config not found at {global_path}")
            return {}
        try:
            with open(global_path, encoding="utf-8") as f:
                config = self._yaml.load(f) or {}
            logger.debug(f"Loaded global config from {global_path}")
            return config
        except Exception as e:
            logger.warning(f"Failed to load global config {global_path}: {e}")
            return {}

    def _load_project_config(self, start_path: Path) -> dict[str, Any]:
        """
        Search up directory hierarchy for .nc/config.yaml and load it.

        Args:
            start_path: Directory to start searching.

        Returns:
            Project configuration dictionary (empty if not found).
        """
        config_file = self._find_nc_config(start_path)
        if config_file is None:
            self._project_path = None
            return {}

        self._project_path = config_file
        try:
            with open(config_file, encoding="utf-8") as f:
                config = self._yaml.load(f) or {}
            logger.debug(f"Loaded project config from {config_file}")
            return config
        except Exception as e:
            logger.warning(f"Failed to load project config {config_file}: {e}")
            return {}

    def _find_nc_config(self, start_path: Path) -> Path | None:
        """
        Walk up directory hierarchy to find .nc/config.yaml.

        Args:
            start_path: Starting directory.

        Returns:
            Path to .nc/config.yaml, or None if not found.
        """
        current = start_path.resolve()
        while current != current.parent:  # Stop at root
            nc_dir = current / ".nc"
            config_file = nc_dir / "config.yaml"
            if config_file.is_file():
                return config_file
            current = current.parent
        return None

    def _deep_merge(
        self, base: dict[str, Any], override: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge recursivo de dicionrios."""
        result = base.copy()
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _merge_all(
        self, global_config: dict[str, Any], project_config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Merge configurations with precedence and @LOCKED protection.

        Precedence: project > global > defaults.
        Locked fields from global/defaults cannot be overridden by project.

        Args:
            global_config: Configuration from global file.
            project_config: Configuration from project file.

        Returns:
            Merged configuration.
        """
        # Start with defaults
        merged = self.defaults.copy()
        # Deep merge global config (overriding defaults)
        merged = self._deep_merge(merged, global_config)
        # Deep merge project config, but remove locked fields
        project_filtered = {
            k: v for k, v in project_config.items() if k not in LOCKED_FIELDS
        }
        merged = self._deep_merge(merged, project_filtered)
        return merged


# Singleton instance
_loader: ProjectConfigLoader | None = None


def get_project_config_loader(
    project_root: Path | None = None,
) -> ProjectConfigLoader:
    """Singleton do ProjectConfigLoader."""
    global _loader
    if _loader is None:
        _loader = ProjectConfigLoader(project_root=project_root)
    elif project_root is not None:
        logger.warning("Project root ignored because loader already instantiated")
    return _loader


# Alias for backward compatibility
get_config_loader = get_project_config_loader
