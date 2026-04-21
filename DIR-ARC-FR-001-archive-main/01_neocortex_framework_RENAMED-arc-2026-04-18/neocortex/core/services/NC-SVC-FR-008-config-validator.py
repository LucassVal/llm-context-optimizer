"""---
domain: "core"
layer: "core"
type: "file"
tags: ["svc", "008", "config", "validator"]
hash: "auto-generated"
---"""
"""
NC-SVC-FR-008-config-validator.py
FR-008  Config Validator: Validates neocortex_config.yaml for required fields, types, and path existence.

Provides validation methods for NeoCortex configuration files:
- validate_config(path) -> dict[errors, warnings, valid]
- is_valid(path) -> bool
- get_warnings(path) -> list
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


class ConfigValidator:
    """
    Validator for neocortex_config.yaml configuration files.

    Validates required fields, data types, and path existence according to
    NeoCortex framework specifications.
    """

    # Required top-level sections
    REQUIRED_SECTIONS = ["llm", "paths"]

    # LLM configuration schema
    LLM_REQUIRED_FIELDS = ["provider", "model"]
    LLM_FIELD_TYPES = {
        "provider": str,
        "model": str,
        "base_url": str,
        "api_key": str,
        "temperature": (int, float),
        "max_tokens": int,
        "timeout": int,
    }

    # Paths configuration - all paths are required
    PATHS_REQUIRED = [
        "core_central",
        "archive",
        "backup",
        "templates",
        "docs",
        "source",
        "mcp_server",
        "profiles",
    ]

    # Cache configuration field types (optional)
    CACHE_FIELD_TYPES = {
        "ledger_size_gb": (int, float),
        "manifest_size_gb": (int, float),
        "hot_cache_size_mb": (int, float),
        "hot_cache_default_ttl": int,
        "hot_cache_use_memory": bool,
    }

    # Search configuration field types (optional)
    SEARCH_FIELD_TYPES = {
        "engine": str,
        "max_results": int,
    }

    # Scheduler configuration field types (optional)
    SCHEDULER_FIELD_TYPES = {
        "pruning_interval_minutes": int,
        "consolidation_interval_minutes": int,
        "akl_assessment_interval_hours": int,
        "akl_assessment_target_hour": int,
        "backup_interval_hours": int,
        "backup_target_hour": int,
        "checkpoint_interval_minutes": int,
    }

    # Monitoring configuration field types (optional)
    MONITORING_FIELD_TYPES = {
        "enable_metrics": bool,
        "metrics_store": str,
        "health_check_interval_seconds": int,
    }

    def __init__(self):
        """Initialize the config validator."""
        self._errors: List[str] = []
        self._warnings: List[str] = []

    def _find_project_root(self, config_path: Path) -> Path:
        """
        Find project root directory containing the configuration file.

        Strategy:
        1. Start from config file directory
        2. Go up until we find a directory with neocortex_config.yaml or .git
        3. Fallback: use parent of config file directory
        """
        current = config_path.parent
        while current != current.parent:  # Stop at root
            # Check for project markers
            if (current / "neocortex_config.yaml").exists() or (
                current / ".git"
            ).exists():
                return current
            current = current.parent
        # If no markers found, assume config is at project root
        return config_path.parent

    def validate_config(
        self,
        config_path: Union[str, Path],
        project_root: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """
        Validate a neocortex_config.yaml file.

        Args:
            config_path: Path to configuration file

        Returns:
            Dictionary with:
                - valid: bool indicating if configuration is valid
                - errors: list of error messages
                - warnings: list of warning messages
                - config: loaded configuration (if valid YAML)
        """
        self._errors = []
        self._warnings = []

        path = Path(config_path)

        # Check file existence
        if not path.exists():
            self._errors.append(f"Configuration file does not exist: {path}")
            return self._build_result(None)

        # Load YAML
        config = self._load_yaml(path)
        if config is None:
            self._errors.append(f"Failed to parse YAML file: {path}")
            return self._build_result(None)

        # Validate required sections
        self._validate_required_sections(config)

        # Validate LLM configuration
        if "llm" in config:
            self._validate_llm_config(config["llm"])

        # Determine project root for path resolution
        if project_root is None:
            project_root = self._find_project_root(path)
        else:
            project_root = Path(project_root)

        # Validate paths configuration
        if "paths" in config:
            self._validate_paths_config(config["paths"], project_root)

        # Validate cache configuration (optional)
        if "cache" in config:
            self._validate_section_types(
                "cache", config["cache"], self.CACHE_FIELD_TYPES
            )

        # Validate search configuration (optional)
        if "search" in config:
            self._validate_section_types(
                "search", config["search"], self.SEARCH_FIELD_TYPES
            )

        # Validate scheduler configuration (optional)
        if "scheduler" in config:
            self._validate_section_types(
                "scheduler", config["scheduler"], self.SCHEDULER_FIELD_TYPES
            )

        # Validate monitoring configuration (optional)
        if "monitoring" in config:
            self._validate_section_types(
                "monitoring", config["monitoring"], self.MONITORING_FIELD_TYPES
            )

        # Validate fallback_chain structure if present
        if "llm" in config and "fallback_chain" in config["llm"]:
            self._validate_fallback_chain(config["llm"]["fallback_chain"])

        # Validate agent_backends structure if present
        if "llm" in config and "agent_backends" in config["llm"]:
            self._validate_agent_backends(config["llm"]["agent_backends"])

        return self._build_result(config)

    def is_valid(
        self,
        config_path: Union[str, Path],
        project_root: Optional[Union[str, Path]] = None,
    ) -> bool:
        """
        Check if a configuration file is valid.

        Args:
            config_path: Path to configuration file
            project_root: Optional project root directory for path resolution.
                         If not provided, will be auto-detected.

        Returns:
            True if configuration is valid (no errors), False otherwise
        """
        result = self.validate_config(config_path, project_root)
        return result["valid"]

    def get_warnings(
        self,
        config_path: Union[str, Path],
        project_root: Optional[Union[str, Path]] = None,
    ) -> List[str]:
        """
        Get warnings for a configuration file without failing on errors.

        Args:
            config_path: Path to configuration file
            project_root: Optional project root directory for path resolution.
                         If not provided, will be auto-detected.

        Returns:
            List of warning messages
        """
        self._errors = []
        self._warnings = []

        path = Path(config_path)
        if not path.exists():
            return [f"Configuration file does not exist: {path}"]

        config = self._load_yaml(path)
        if config is None:
            return [f"Failed to parse YAML file: {path}"]

        # Determine project root for path resolution
        if project_root is None:
            project_root = self._find_project_root(path)
        else:
            project_root = Path(project_root)

        # Collect warnings only (skip errors that would break validation)
        if "llm" in config:
            self._collect_llm_warnings(config["llm"])

        if "paths" in config:
            self._collect_path_warnings(config["paths"], project_root)

        # Type warnings for optional sections
        for section, field_types in [
            ("cache", self.CACHE_FIELD_TYPES),
            ("search", self.SEARCH_FIELD_TYPES),
            ("scheduler", self.SCHEDULER_FIELD_TYPES),
            ("monitoring", self.MONITORING_FIELD_TYPES),
        ]:
            if section in config:
                self._collect_type_warnings(section, config[section], field_types)

        return self._warnings

    def _load_yaml(self, path: Path) -> Optional[Dict[str, Any]]:
        """Load YAML file, return None on error."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except (yaml.YAMLError, IOError) as e:
            self._errors.append(f"YAML parsing error: {e}")
            return None

    def _validate_required_sections(self, config: Dict[str, Any]) -> None:
        """Validate that required sections are present."""
        for section in self.REQUIRED_SECTIONS:
            if section not in config:
                self._errors.append(f"Missing required section: '{section}'")

    def _validate_llm_config(self, llm_config: Dict[str, Any]) -> None:
        """Validate LLM configuration."""
        # Check required fields
        for field in self.LLM_REQUIRED_FIELDS:
            if field not in llm_config:
                self._errors.append(
                    f"LLM configuration missing required field: '{field}'"
                )

        # Check field types
        for field, expected_type in self.LLM_FIELD_TYPES.items():
            if field in llm_config:
                value = llm_config[field]
                if not isinstance(value, expected_type):
                    self._errors.append(
                        f"LLM field '{field}' has incorrect type: "
                        f"expected {expected_type.__name__ if hasattr(expected_type, '__name__') else ' or '.join(t.__name__ for t in expected_type)}, "
                        f"got {type(value).__name__}"
                    )

        # Special validation for temperature
        if "temperature" in llm_config:
            temp = llm_config["temperature"]
            if not (0.0 <= temp <= 1.0):
                self._warnings.append(
                    f"LLM temperature ({temp}) should be between 0.0 and 1.0"
                )

        # Special validation for max_tokens
        if "max_tokens" in llm_config:
            max_tokens = llm_config["max_tokens"]
            if max_tokens <= 0:
                self._errors.append(f"LLM max_tokens ({max_tokens}) must be positive")
            elif max_tokens > 100000:
                self._warnings.append(
                    f"LLM max_tokens ({max_tokens}) is unusually high"
                )

    def _validate_paths_config(
        self, paths_config: Dict[str, Any], base_dir: Path
    ) -> None:
        """Validate paths configuration."""
        # Check required paths
        for path_name in self.PATHS_REQUIRED:
            if path_name not in paths_config:
                self._errors.append(
                    f"Paths configuration missing required path: '{path_name}'"
                )
            else:
                path_value = paths_config[path_name]
                if not isinstance(path_value, str):
                    self._errors.append(
                        f"Path '{path_name}' must be a string, got {type(path_value).__name__}"
                    )
                else:
                    # Check if path exists relative to config file location
                    full_path = base_dir / path_value
                    if not full_path.exists():
                        self._warnings.append(
                            f"Path '{path_name}' does not exist: {full_path}"
                        )

    def _validate_section_types(
        self,
        section_name: str,
        section_config: Dict[str, Any],
        field_types: Dict[str, Any],
    ) -> None:
        """Validate field types in a configuration section."""
        for field, expected_type in field_types.items():
            if field in section_config:
                value = section_config[field]
                if not isinstance(value, expected_type):
                    # Handle tuple of multiple allowed types
                    if isinstance(expected_type, tuple):
                        type_names = " or ".join(t.__name__ for t in expected_type)
                        if not any(isinstance(value, t) for t in expected_type):
                            self._errors.append(
                                f"{section_name} field '{field}' has incorrect type: "
                                f"expected {type_names}, got {type(value).__name__}"
                            )
                    else:
                        self._errors.append(
                            f"{section_name} field '{field}' has incorrect type: "
                            f"expected {expected_type.__name__}, got {type(value).__name__}"
                        )

    def _validate_fallback_chain(self, fallback_chain: Any) -> None:
        """Validate LLM fallback_chain structure."""
        if not isinstance(fallback_chain, list):
            self._errors.append("LLM fallback_chain must be a list")
            return

        for i, entry in enumerate(fallback_chain):
            if not isinstance(entry, dict):
                self._errors.append(
                    f"LLM fallback_chain entry {i} must be a dictionary"
                )
                continue

            # Check required fields for fallback entry
            if "provider" not in entry:
                self._errors.append(
                    f"LLM fallback_chain entry {i} missing 'provider' field"
                )

            if "model" not in entry:
                self._warnings.append(
                    f"LLM fallback_chain entry {i} missing 'model' field"
                )

    def _validate_agent_backends(self, agent_backends: Any) -> None:
        """Validate LLM agent_backends structure."""
        if not isinstance(agent_backends, dict):
            self._errors.append("LLM agent_backends must be a dictionary")
            return

        # Check required agent types
        required_agents = ["default", "t0", "courier", "engineer"]
        for agent in required_agents:
            if agent not in agent_backends:
                self._warnings.append(
                    f"LLM agent_backends missing agent type: '{agent}'"
                )

        # Validate each agent backend
        for agent_name, backend_config in agent_backends.items():
            if not isinstance(backend_config, dict):
                self._errors.append(
                    f"LLM agent_backends['{agent_name}'] must be a dictionary"
                )
                continue

            if "provider" not in backend_config:
                self._errors.append(
                    f"LLM agent_backends['{agent_name}'] missing 'provider' field"
                )

            if "model" not in backend_config:
                self._warnings.append(
                    f"LLM agent_backends['{agent_name}'] missing 'model' field"
                )

    def _collect_llm_warnings(self, llm_config: Dict[str, Any]) -> None:
        """Collect warnings from LLM configuration without raising errors."""
        # Temperature range warning
        if "temperature" in llm_config:
            temp = llm_config["temperature"]
            if isinstance(temp, (int, float)) and not (0.0 <= temp <= 1.0):
                self._warnings.append(
                    f"LLM temperature ({temp}) should be between 0.0 and 1.0"
                )

        # Max tokens warning
        if "max_tokens" in llm_config:
            max_tokens = llm_config["max_tokens"]
            if isinstance(max_tokens, (int, float)) and max_tokens > 100000:
                self._warnings.append(
                    f"LLM max_tokens ({max_tokens}) is unusually high"
                )

    def _collect_path_warnings(
        self, paths_config: Dict[str, Any], base_dir: Path
    ) -> None:
        """Collect warnings from paths configuration."""
        for path_name, path_value in paths_config.items():
            if isinstance(path_value, str):
                full_path = base_dir / path_value
                if not full_path.exists():
                    self._warnings.append(
                        f"Path '{path_name}' does not exist: {full_path}"
                    )

    def _collect_type_warnings(
        self,
        section_name: str,
        section_config: Dict[str, Any],
        field_types: Dict[str, Any],
    ) -> None:
        """Collect type warnings without raising errors."""
        for field, expected_type in field_types.items():
            if field in section_config:
                value = section_config[field]
                # Check if value matches expected type(s)
                if isinstance(expected_type, tuple):
                    if not any(isinstance(value, t) for t in expected_type):
                        type_names = " or ".join(t.__name__ for t in expected_type)
                        self._warnings.append(
                            f"{section_name} field '{field}' has unexpected type: "
                            f"expected {type_names}, got {type(value).__name__}"
                        )
                elif not isinstance(value, expected_type):
                    self._warnings.append(
                        f"{section_name} field '{field}' has unexpected type: "
                        f"expected {expected_type.__name__}, got {type(value).__name__}"
                    )

    def _build_result(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build validation result dictionary."""
        return {
            "valid": len(self._errors) == 0,
            "errors": self._errors.copy(),
            "warnings": self._warnings.copy(),
            "config": config,
        }


# Convenience functions
def validate_config(
    config_path: Union[str, Path], project_root: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """
    Validate a neocortex_config.yaml file.

    Args:
        config_path: Path to configuration file
        project_root: Optional project root directory for path resolution.
                     If not provided, will be auto-detected.

    Returns:
        Dictionary with validation results
    """
    validator = ConfigValidator()
    return validator.validate_config(config_path, project_root)


def is_valid(
    config_path: Union[str, Path], project_root: Optional[Union[str, Path]] = None
) -> bool:
    """
    Check if a configuration file is valid.

    Args:
        config_path: Path to configuration file
        project_root: Optional project root directory for path resolution.
                     If not provided, will be auto-detected.

    Returns:
        True if configuration is valid (no errors), False otherwise
    """
    validator = ConfigValidator()
    return validator.is_valid(config_path, project_root)


def get_warnings(
    config_path: Union[str, Path], project_root: Optional[Union[str, Path]] = None
) -> List[str]:
    """
    Get warnings for a configuration file.

    Args:
        config_path: Path to configuration file
        project_root: Optional project root directory for path resolution.
                     If not provided, will be auto-detected.

    Returns:
        List of warning messages
    """
    validator = ConfigValidator()
    return validator.get_warnings(config_path, project_root)
