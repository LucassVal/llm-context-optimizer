#!/usr/bin/env python3
"""
Configuration provider for NeoCortex framework.

Centralized configuration management with environment variable support,
configuration file loading, and sensible defaults.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List


class Config:
    """
    Configuration provider for NeoCortex framework.

    Provides centralized access to framework paths, settings, and configuration
    with support for environment variable overrides and configuration files.
    """

    # Singleton instance
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Determine project root
        self._project_root = self._detect_project_root()

        # Load configuration
        self._config = self._load_configuration()

        # Initialize paths
        self._init_paths()

        self._initialized = True

    def _detect_project_root(self) -> Path:
        """
        Detect the project root directory.

        Returns:
            Path to project root
        """
        # Try to detect from environment variable
        env_root = os.environ.get("NEOCORTEX_PROJECT_ROOT")
        if env_root:
            return Path(env_root).resolve()

        # Default: assume config.py is in neocortex/ directory,
        # and project root is parent of neocortex/ directory
        config_file_path = Path(__file__).resolve()
        # config.py -> neocortex/ -> neocortex_framework/
        if config_file_path.parent.name == "neocortex":
            return config_file_path.parent.parent.resolve()

        # Fallback: current working directory
        return Path.cwd().resolve()

    def _load_configuration(self) -> Dict[str, Any]:
        """
        Load configuration from multiple sources with precedence:
        1. Environment variables
        2. Configuration file (neocortex_config.yaml or neocortex_config.json)
        3. Default values

        Returns:
            Configuration dictionary
        """
        config = {}

        # Load from YAML file if exists
        yaml_path = self._project_root / "neocortex_config.yaml"
        if yaml_path.exists():
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    yaml_config = yaml.safe_load(f) or {}
                    config.update(yaml_config)
            except Exception:
                pass

        # Load from JSON file if exists
        json_path = self._project_root / "neocortex_config.json"
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    json_config = json.load(f) or {}
                    config.update(json_config)
            except Exception:
                pass

        # Apply environment variable overrides
        self._apply_env_overrides(config)

        # Ensure LLM configuration section exists with defaults
        if "llm" not in config:
            config["llm"] = {}

        llm_config = config["llm"]

        # Default LLM configuration
        default_llm_config = {
            "provider": "ollama",
            "model": "llama2",
            "base_url": "http://localhost:11434",
            "api_key": "",
            "temperature": 0.7,
            "max_tokens": 4096,
            "timeout": 300,
            "fallback_chain": [
                {
                    "provider": "ollama",
                    "model": "llama2",
                    "base_url": "http://localhost:11434",
                },
                {"provider": "deepseek", "model": "deepseek-chat", "api_key": ""},
            ],
        }

        # Merge defaults with user config
        for key, default_value in default_llm_config.items():
            if key not in llm_config:
                llm_config[key] = default_value

        # Set environment variable API keys if not configured
        if not llm_config.get("api_key"):
            env_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get(
                "OPENAI_API_KEY"
            )
            if env_key:
                llm_config["api_key"] = env_key

        return config

    def _apply_env_overrides(self, config: Dict[str, Any]) -> None:
        """
        Apply environment variable overrides to configuration.

        Environment variables should be prefixed with NEOCORTEX_
        and use double underscore for nested keys.
        Example: NEOCORTEX_PATHS__CORTEX_PATH
        """
        for key, value in os.environ.items():
            if key.startswith("NEOCORTEX_"):
                # Remove prefix and split by double underscore
                config_key = key[10:]  # Remove "NEOCORTEX_"
                keys = [k.lower() for k in config_key.split("__")]

                # Navigate to nested position
                current = config
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]

                # Set value (convert string to appropriate type)
                final_key = keys[-1]
                current[final_key] = self._parse_env_value(value)

    def _parse_env_value(self, value: str) -> Union[str, int, float, bool, None]:
        """
        Parse environment variable string value to appropriate type.
        """
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif value.lower() == "null" or value.lower() == "none":
            return None

        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _init_paths(self) -> None:
        """
        Initialize all framework paths.
        """
        # Base paths from configuration or defaults
        paths_config = self._config.get("paths", {})

        # Core directories
        self.PATHS = {
            "project_root": self._project_root,
            "core_central": self._project_root
            / paths_config.get("core_central", "DIR-CORE-FR-001-core-central"),
            "archive": self._project_root
            / paths_config.get("archive", "DIR-ARC-FR-001-archive-main"),
            "backup": self._project_root
            / paths_config.get("backup", "DIR-BAK-FR-001-backup-main"),
            "templates": self._project_root
            / paths_config.get("templates", "DIR-TMP-FR-001-templates-main"),
            "docs": self._project_root
            / paths_config.get("docs", "DIR-DOC-FR-001-docs-main"),
            "source": self._project_root
            / paths_config.get("source", "DIR-SRC-FR-001-source-main"),
            "mcp_server": self._project_root
            / paths_config.get("mcp_server", "DIR-MCP-FR-001-mcp-server"),
            "profiles": self._project_root
            / paths_config.get("profiles", "DIR-PRF-FR-001-profiles-main"),
        }

        # Critical files
        self.FILES = {
            "cortex": self.PATHS["core_central"]
            / ".agents"
            / "rules"
            / "NC-CTX-FR-001-cortex-central.mdc",
            "ledger": self.PATHS["core_central"]
            / "NC-LED-FR-001-framework-ledger.json",
            "tool_manifest": self.PATHS["core_central"]
            / "NC-TLM-FR-001-tool-manifest.json",
            "tool_manifest_schema": self.PATHS["core_central"]
            / "NC-TLM-FR-001-tool-manifest-schema.json",
        }

        # Ensure critical directories exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """
        Ensure critical directories exist.
        """
        dirs_to_ensure = [
            self.PATHS["core_central"],
            self.PATHS["archive"],
            self.PATHS["backup"],
            self.PATHS["templates"],
            self.PATHS["docs"],
            self.PATHS["source"],
            self.PATHS["mcp_server"],
            self.PATHS["profiles"],
            self.PATHS["core_central"] / ".agents" / "rules",
        ]

        for directory in dirs_to_ensure:
            directory.mkdir(parents=True, exist_ok=True)

    # Property accessors
    @property
    def project_root(self) -> Path:
        """Get project root directory."""
        return self.PATHS["project_root"]

    @property
    def core_central(self) -> Path:
        """Get core central directory."""
        return self.PATHS["core_central"]

    @property
    def cortex_path(self) -> Path:
        """Get cortex file path."""
        return self.FILES["cortex"]

    @property
    def ledger_path(self) -> Path:
        """Get ledger file path."""
        return self.FILES["ledger"]

    @property
    def tool_manifest_path(self) -> Path:
        """Get tool manifest file path."""
        return self.FILES["tool_manifest"]

    @property
    def tool_manifest_schema_path(self) -> Path:
        """Get tool manifest schema file path."""
        return self.FILES["tool_manifest_schema"]

    @property
    def archive_path(self) -> Path:
        """Get archive directory."""
        return self.PATHS["archive"]

    @property
    def backup_path(self) -> Path:
        """Get backup directory."""
        return self.PATHS["backup"]

    @property
    def templates_path(self) -> Path:
        """Get templates directory."""
        return self.PATHS["templates"]

    @property
    def docs_path(self) -> Path:
        """Get docs directory."""
        return self.PATHS["docs"]

    @property
    def source_path(self) -> Path:
        """Get source directory."""
        return self.PATHS["source"]

    @property
    def mcp_server_path(self) -> Path:
        """Get MCP server directory."""
        return self.PATHS["mcp_server"]

    @property
    def profiles_path(self) -> Path:
        """Get profiles directory."""
        return self.PATHS["profiles"]

    # LLM configuration access
    @property
    def llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self._config.get("llm", {}).copy()

    @property
    def llm_provider(self) -> str:
        """Get configured LLM provider."""
        return self.llm_config.get("provider", "ollama")

    @property
    def llm_model(self) -> str:
        """Get configured LLM model."""
        return self.llm_config.get("model", "llama2")

    @property
    def llm_base_url(self) -> str:
        """Get configured LLM base URL."""
        return self.llm_config.get("base_url", "")

    @property
    def llm_api_key(self) -> str:
        """Get configured LLM API key."""
        return self.llm_config.get("api_key", "")

    @property
    def llm_temperature(self) -> float:
        """Get configured LLM temperature."""
        return float(self.llm_config.get("temperature", 0.7))

    @property
    def llm_max_tokens(self) -> int:
        """Get configured LLM max tokens."""
        return int(self.llm_config.get("max_tokens", 4096))

    @property
    def llm_fallback_chain(self) -> List[Dict[str, Any]]:
        """Get configured LLM fallback chain."""
        return self.llm_config.get("fallback_chain", [])

    # Cache configuration access
    @property
    def cache_config(self) -> Dict[str, Any]:
        """Get cache configuration."""
        return self._config.get("cache", {}).copy()

    @property
    def ledger_cache_size_gb(self) -> int:
        """Get ledger cache size in gigabytes."""
        return int(self.cache_config.get("ledger_size_gb", 1))

    @property
    def manifest_cache_size_gb(self) -> int:
        """Get manifest cache size in gigabytes."""
        return int(self.cache_config.get("manifest_size_gb", 1))

    @property
    def hot_cache_size_mb(self) -> int:
        """Get hot cache size in megabytes."""
        return int(self.cache_config.get("hot_cache_size_mb", 100))

    @property
    def hot_cache_default_ttl(self) -> int:
        """Get hot cache default TTL in seconds."""
        return int(self.cache_config.get("hot_cache_default_ttl", 300))

    @property
    def hot_cache_use_memory(self) -> bool:
        """Get whether to use memory cache."""
        return bool(self.cache_config.get("hot_cache_use_memory", True))

    # Scheduler configuration access
    @property
    def scheduler_config(self) -> Dict[str, Any]:
        """Get scheduler configuration."""
        return self._config.get("scheduler", {}).copy()

    @property
    def pruning_interval_minutes(self) -> int:
        """Get pruning interval in minutes."""
        return int(self.scheduler_config.get("pruning_interval_minutes", 15))

    @property
    def consolidation_interval_minutes(self) -> int:
        """Get consolidation interval in minutes."""
        return int(self.scheduler_config.get("consolidation_interval_minutes", 30))

    @property
    def akl_assessment_interval_hours(self) -> int:
        """Get AKL assessment interval in hours."""
        return int(self.scheduler_config.get("akl_assessment_interval_hours", 24))

    @property
    def backup_interval_hours(self) -> int:
        """Get backup interval in hours."""
        return int(self.scheduler_config.get("backup_interval_hours", 24))

    @property
    def backup_target_hour(self) -> int:
        """Get backup target hour (0-23)."""
        return int(self.scheduler_config.get("backup_target_hour", 3))

    @property
    def akl_assessment_target_hour(self) -> int:
        """Get AKL assessment target hour (0-23)."""
        return int(self.scheduler_config.get("akl_assessment_target_hour", 0))

    @property
    def checkpoint_interval_minutes(self) -> int:
        """Get checkpoint interval in minutes."""
        return int(self.scheduler_config.get("checkpoint_interval_minutes", 5))

    # Configuration access
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot notation.

        Args:
            key: Dot notation key (e.g., "paths.core_central")
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        current = self._config

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot notation.

        Args:
            key: Dot notation key
            value: Value to set
        """
        keys = key.split(".")
        current = self._config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def reload(self) -> None:
        """Reload configuration from files and environment."""
        self._config = self._load_configuration()
        self._init_paths()

    def validate(self) -> Dict[str, Any]:
        """
        Validate configuration for critical paths and required settings.

        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []

        # Validate critical paths exist
        for name, path in self.PATHS.items():
            if not path.exists():
                issues.append(f"Path '{name}' does not exist: {path}")

        # Validate LLM configuration
        llm_config = self.llm_config
        if not llm_config.get("provider"):
            warnings.append("LLM provider not configured, using default 'ollama'")

        # Validate fallback_chain is a list
        fallback_chain = llm_config.get("fallback_chain", [])
        if not isinstance(fallback_chain, list):
            issues.append("LLM fallback_chain must be a list")

        # Validate cache sizes are positive
        if self.ledger_cache_size_gb <= 0:
            warnings.append("Ledger cache size must be positive, using default 1GB")
        if self.manifest_cache_size_gb <= 0:
            warnings.append("Manifest cache size must be positive, using default 1GB")
        if self.hot_cache_size_mb <= 0:
            warnings.append("Hot cache size must be positive, using default 100MB")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "paths_validated": len(self.PATHS),
            "llm_provider": llm_config.get("provider", "not set"),
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Export configuration as dictionary.

        Returns:
            Configuration dictionary
        """
        return {
            "paths": {k: str(v) for k, v in self.PATHS.items()},
            "files": {k: str(v) for k, v in self.FILES.items()},
            "config": self._config.copy(),
        }

    def __str__(self) -> str:
        """String representation of configuration."""
        config_dict = self.to_dict()
        return json.dumps(config_dict, indent=2, ensure_ascii=False)


# Singleton instance
_config_instance = None


def get_config() -> Config:
    """
    Get the singleton configuration instance.

    Returns:
        Config instance
    """
    global _config_instance

    if _config_instance is None:
        _config_instance = Config()

    return _config_instance
