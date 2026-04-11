#!/usr/bin/env python3
"""
Configuration validation for NeoCortex infrastructure.

Provides comprehensive validation of configuration files, environment variables,
and runtime settings with detailed error reporting.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import yaml

logger = logging.getLogger(__name__)


class ValidationSeverity(str, Enum):
    """Validation severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Single validation result."""

    severity: ValidationSeverity
    message: str
    field: Optional[str] = None
    value: Optional[Any] = None
    suggestion: Optional[str] = None
    rule_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ConfigValidator:
    """
    Comprehensive configuration validator for NeoCortex.

    Validates configuration files, environment variables, and runtime settings
    against defined schemas and best practices.
    """

    # Default configuration schema
    DEFAULT_SCHEMA = {
        "type": "object",
        "properties": {
            "paths": {
                "type": "object",
                "properties": {
                    "core_central": {"type": "string"},
                    "archive": {"type": "string"},
                    "backup": {"type": "string"},
                    "templates": {"type": "string"},
                    "docs": {"type": "string"},
                    "source": {"type": "string"},
                    "mcp_server": {"type": "string"},
                    "profiles": {"type": "string"},
                },
                "additionalProperties": False,
            },
            "llm": {
                "type": "object",
                "properties": {
                    "provider": {
                        "type": "string",
                        "enum": ["ollama", "deepseek", "openai"],
                    },
                    "model": {"type": "string"},
                    "base_url": {"type": "string"},
                    "api_key": {"type": "string"},
                    "temperature": {"type": "number", "minimum": 0, "maximum": 2},
                    "max_tokens": {"type": "integer", "minimum": 1, "maximum": 100000},
                    "timeout": {"type": "integer", "minimum": 1},
                    "fallback_chain": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "provider": {"type": "string"},
                                "model": {"type": "string"},
                                "api_key": {"type": "string"},
                                "base_url": {"type": "string"},
                            },
                        },
                    },
                },
                "additionalProperties": True,
            },
            "infra": {
                "type": "object",
                "properties": {
                    "cache_size_gb": {"type": "number", "minimum": 0.1, "maximum": 100},
                    "search_backend": {
                        "type": "string",
                        "enum": ["sqlite_fts5", "xapian"],
                    },
                    "backup_retention_days": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 365,
                    },
                },
                "additionalProperties": True,
            },
        },
        "additionalProperties": True,
    }

    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize validator.

        Args:
            schema: Custom validation schema (uses default if None).
        """
        self.schema = schema or self.DEFAULT_SCHEMA
        self.rules = self._load_validation_rules()

    def _load_validation_rules(self) -> List[Dict[str, Any]]:
        """Load validation rules."""
        return [
            # Path validation rules
            {
                "id": "PATH_EXISTS",
                "description": "Path must exist",
                "fields": ["paths.*"],
                "validate": self._validate_path_exists,
            },
            {
                "id": "PATH_WRITABLE",
                "description": "Path must be writable",
                "fields": ["backup", "cache"],
                "validate": self._validate_path_writable,
            },
            # LLM validation rules
            {
                "id": "LLM_API_KEY",
                "description": "Cloud LLM requires API key",
                "fields": ["llm.provider", "llm.api_key"],
                "validate": self._validate_llm_api_key,
            },
            {
                "id": "LLM_BASE_URL",
                "description": "Local LLM requires base URL",
                "fields": ["llm.provider", "llm.base_url"],
                "validate": self._validate_llm_base_url,
            },
            # Security validation rules
            {
                "id": "NO_PLAIN_TEXT_SECRETS",
                "description": "Secrets should not be in plain text",
                "fields": ["**"],
                "validate": self._validate_no_plain_text_secrets,
            },
            # Performance validation rules
            {
                "id": "CACHE_SIZE",
                "description": "Cache size should be reasonable",
                "fields": ["infra.cache_size_gb"],
                "validate": self._validate_cache_size,
            },
        ]

    def validate_config_file(self, config_path: Path) -> List[ValidationResult]:
        """
        Validate configuration file.

        Args:
            config_path: Path to configuration file.

        Returns:
            List of validation results.
        """
        results = []

        # Check file exists
        if not config_path.exists():
            results.append(
                ValidationResult(
                    severity=ValidationSeverity.ERROR,
                    message=f"Configuration file not found: {config_path}",
                    rule_id="FILE_NOT_FOUND",
                )
            )
            return results

        # Load configuration
        try:
            if config_path.suffix == ".yaml" or config_path.suffix == ".yml":
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f) or {}
            elif config_path.suffix == ".json":
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            else:
                results.append(
                    ValidationResult(
                        severity=ValidationSeverity.ERROR,
                        message=f"Unsupported configuration file format: {config_path.suffix}",
                        rule_id="UNSUPPORTED_FORMAT",
                    )
                )
                return results
        except Exception as e:
            results.append(
                ValidationResult(
                    severity=ValidationSeverity.ERROR,
                    message=f"Failed to load configuration file: {e}",
                    rule_id="LOAD_ERROR",
                )
            )
            return results

        # Validate configuration content
        results.extend(self.validate_config(config))

        return results

    def validate_config(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate configuration dictionary.

        Args:
            config: Configuration dictionary.

        Returns:
            List of validation results.
        """
        results = []

        # Apply schema validation
        results.extend(self._validate_schema(config))

        # Apply custom rules
        for rule in self.rules:
            for field_pattern in rule["fields"]:
                matching_fields = self._find_matching_fields(config, field_pattern)
                for field_path, field_value in matching_fields:
                    rule_results = rule["validate"](field_path, field_value, config)
                    if rule_results:
                        for result in rule_results:
                            result.rule_id = rule["id"]
                        results.extend(rule_results)

        # Sort by severity
        severity_order = {
            ValidationSeverity.CRITICAL: 0,
            ValidationSeverity.ERROR: 1,
            ValidationSeverity.WARNING: 2,
            ValidationSeverity.INFO: 3,
        }
        results.sort(key=lambda r: severity_order.get(r.severity, 4))

        return results

    def validate_environment(self) -> List[ValidationResult]:
        """
        Validate environment variables.

        Returns:
            List of validation results.
        """
        results = []

        # Check required environment variables
        required_vars = [
            ("NEOCORTEX_PROJECT_ROOT", "Project root directory"),
        ]

        optional_vars = [
            ("DEEPSEEK_API_KEY", "DeepSeek API key"),
            ("OPENAI_API_KEY", "OpenAI API key"),
            ("NEOCORTEX_LOG_LEVEL", "Log level (DEBUG, INFO, WARNING, ERROR)"),
        ]

        for var_name, description in required_vars:
            if var_name not in os.environ:
                results.append(
                    ValidationResult(
                        severity=ValidationSeverity.ERROR,
                        message=f"Required environment variable not set: {var_name}",
                        field=var_name,
                        suggestion=f"Set {var_name} to {description}",
                        rule_id="ENV_REQUIRED",
                    )
                )

        for var_name, description in optional_vars:
            if var_name in os.environ:
                value = os.environ[var_name]

                # Validate specific variables
                if var_name == "NEOCORTEX_LOG_LEVEL":
                    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                    if value not in valid_levels:
                        results.append(
                            ValidationResult(
                                severity=ValidationSeverity.WARNING,
                                message=f"Invalid log level: {value}",
                                field=var_name,
                                value=value,
                                suggestion=f"Use one of: {', '.join(valid_levels)}",
                                rule_id="ENV_LOG_LEVEL",
                            )
                        )

        return results

    def _validate_schema(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Validate configuration against JSON schema."""
        results = []

        try:
            import jsonschema

            jsonschema.validate(config, self.schema)
        except ImportError:
            # jsonschema not available, skip schema validation
            results.append(
                ValidationResult(
                    severity=ValidationSeverity.WARNING,
                    message="jsonschema not available, skipping schema validation",
                    rule_id="SCHEMA_SKIP",
                )
            )
            return results
        except jsonschema.ValidationError as e:
            # Extract meaningful information from validation error
            path = ".".join(str(p) for p in e.path) if e.path else "root"

            results.append(
                ValidationResult(
                    severity=ValidationSeverity.ERROR,
                    message=f"Schema validation failed: {e.message}",
                    field=path,
                    value=e.instance if hasattr(e, "instance") else None,
                    suggestion=f"Expected: {e.schema.get('description', 'No suggestion')}",
                    rule_id="SCHEMA_VALIDATION",
                )
            )

        return results

    def _validate_path_exists(
        self, field_path: str, value: Any, config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate that path exists."""
        results = []

        if isinstance(value, str):
            path = Path(value)
            if not path.exists():
                results.append(
                    ValidationResult(
                        severity=ValidationSeverity.ERROR,
                        message=f"Path does not exist: {value}",
                        field=field_path,
                        value=value,
                        suggestion="Create the directory or check the path",
                        rule_id="PATH_EXISTS",
                    )
                )

        return results

    def _validate_path_writable(
        self, field_path: str, value: Any, config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate that path is writable."""
        results = []

        if isinstance(value, str):
            path = Path(value)

            # Create directory if it doesn't exist
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    results.append(
                        ValidationResult(
                            severity=ValidationSeverity.ERROR,
                            message=f"Cannot create directory: {value} - {e}",
                            field=field_path,
                            value=value,
                            suggestion="Check permissions or choose different location",
                            rule_id="PATH_WRITABLE",
                        )
                    )
                    return results

            # Test write permission
            test_file = path / ".write_test"
            try:
                test_file.touch(exist_ok=True)
                test_file.unlink(missing_ok=True)
            except Exception as e:
                results.append(
                    ValidationResult(
                        severity=ValidationSeverity.ERROR,
                        message=f"Directory not writable: {value} - {e}",
                        field=field_path,
                        value=value,
                        suggestion="Check directory permissions",
                        rule_id="PATH_WRITABLE",
                    )
                )

        return results

    def _validate_llm_api_key(
        self, field_path: str, value: Any, config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate LLM API key requirement."""
        results = []

        llm_config = config.get("llm", {})
        provider = llm_config.get("provider", "")
        api_key = llm_config.get("api_key", "")

        if provider in ["deepseek", "openai"] and not api_key:
            results.append(
                ValidationResult(
                    severity=ValidationSeverity.WARNING,
                    message=f"{provider.capitalize()} provider requires API key",
                    field="llm.api_key",
                    suggestion="Set api_key in configuration or use environment variable",
                    rule_id="LLM_API_KEY",
                )
            )

        return results

    def _validate_llm_base_url(
        self, field_path: str, value: Any, config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate LLM base URL requirement."""
        results = []

        llm_config = config.get("llm", {})
        provider = llm_config.get("provider", "")
        base_url = llm_config.get("base_url", "")

        if provider == "ollama" and not base_url:
            results.append(
                ValidationResult(
                    severity=ValidationSeverity.WARNING,
                    message="Ollama provider should have base_url",
                    field="llm.base_url",
                    suggestion="Set base_url to http://localhost:11434 or your Ollama server",
                    rule_id="LLM_BASE_URL",
                )
            )

        return results

    def _validate_no_plain_text_secrets(
        self, field_path: str, value: Any, config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate no plain text secrets in configuration."""
        results = []

        secret_patterns = [
            r"api[_-]?key",
            r"secret",
            r"password",
            r"token",
            r"auth",
            r"credential",
        ]

        if isinstance(value, str) and len(value) > 8:
            field_lower = field_path.lower()
            for pattern in secret_patterns:
                if re.search(pattern, field_lower):
                    # Check if value looks like a secret (long, random string)
                    if self._looks_like_secret(value):
                        results.append(
                            ValidationResult(
                                severity=ValidationSeverity.WARNING,
                                message=f"Potential secret found in plain text: {field_path}",
                                field=field_path,
                                suggestion="Use environment variables for secrets",
                                rule_id="NO_PLAIN_TEXT_SECRETS",
                            )
                        )
                    break

        return results

    def _validate_cache_size(
        self, field_path: str, value: Any, config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate cache size is reasonable."""
        results = []

        if isinstance(value, (int, float)):
            if value < 0.1:
                results.append(
                    ValidationResult(
                        severity=ValidationSeverity.WARNING,
                        message=f"Cache size very small: {value}GB",
                        field=field_path,
                        value=value,
                        suggestion="Increase cache size for better performance",
                        rule_id="CACHE_SIZE",
                    )
                )
            elif value > 10:
                results.append(
                    ValidationResult(
                        severity=ValidationSeverity.WARNING,
                        message=f"Cache size very large: {value}GB",
                        field=field_path,
                        value=value,
                        suggestion="Consider reducing cache size to save disk space",
                        rule_id="CACHE_SIZE",
                    )
                )

        return results

    def _find_matching_fields(
        self, config: Dict[str, Any], field_pattern: str
    ) -> List[Tuple[str, Any]]:
        """Find fields matching pattern in configuration."""
        matches = []

        if field_pattern == "**":
            # Match all fields
            self._collect_all_fields(config, "", matches)
        else:
            # Match specific pattern
            pattern_parts = field_pattern.split(".")
            self._find_fields_by_pattern(config, pattern_parts, "", matches)

        return matches

    def _collect_all_fields(
        self, config: Any, prefix: str, matches: List[Tuple[str, Any]]
    ):
        """Recursively collect all fields."""
        if isinstance(config, dict):
            for key, value in config.items():
                field_path = f"{prefix}.{key}" if prefix else key
                matches.append((field_path, value))
                self._collect_all_fields(value, field_path, matches)
        elif isinstance(config, list):
            for i, value in enumerate(config):
                field_path = f"{prefix}[{i}]"
                matches.append((field_path, value))
                self._collect_all_fields(value, field_path, matches)

    def _find_fields_by_pattern(
        self,
        config: Any,
        pattern_parts: List[str],
        prefix: str,
        matches: List[Tuple[str, Any]],
    ):
        """Find fields matching pattern."""
        if not pattern_parts:
            matches.append((prefix, config))
            return

        current_part = pattern_parts[0]
        remaining_parts = pattern_parts[1:]

        if current_part == "*":
            # Wildcard: match all keys at this level
            if isinstance(config, dict):
                for key, value in config.items():
                    field_path = f"{prefix}.{key}" if prefix else key
                    self._find_fields_by_pattern(
                        value, remaining_parts, field_path, matches
                    )
        else:
            # Specific key
            if isinstance(config, dict) and current_part in config:
                field_path = f"{prefix}.{current_part}" if prefix else current_part
                self._find_fields_by_pattern(
                    config[current_part], remaining_parts, field_path, matches
                )

    def _looks_like_secret(self, value: str) -> bool:
        """Check if string looks like a secret."""
        # Secrets are typically long, random strings
        if len(value) < 16:
            return False

        # Check for high entropy (simple heuristic)
        import string

        printable = set(string.printable)
        non_printable = sum(1 for c in value if c not in printable)

        # If more than 10% non-printable, likely binary/encoded
        if non_printable > len(value) * 0.1:
            return True

        # Check for common secret patterns
        secret_patterns = [
            r"^[A-Za-z0-9+/]{40,}={0,2}$",  # Base64 encoded
            r"^[A-Fa-f0-9]{64,}$",  # Hex encoded (SHA256, etc.)
            r"^[A-Za-z0-9\-_]{20,}$",  # JWT-like tokens
        ]

        for pattern in secret_patterns:
            if re.match(pattern, value):
                return True

        return False

    def format_results(self, results: List[ValidationResult]) -> str:
        """Format validation results for human reading."""
        if not results:
            return "✅ All validations passed"

        output = []

        by_severity = {
            ValidationSeverity.CRITICAL: [],
            ValidationSeverity.ERROR: [],
            ValidationSeverity.WARNING: [],
            ValidationSeverity.INFO: [],
        }

        for result in results:
            by_severity[result.severity].append(result)

        for severity in [
            ValidationSeverity.CRITICAL,
            ValidationSeverity.ERROR,
            ValidationSeverity.WARNING,
            ValidationSeverity.INFO,
        ]:
            severity_results = by_severity[severity]
            if not severity_results:
                continue

            output.append(f"\n{severity.upper()} ({len(severity_results)}):")
            for result in severity_results:
                line = f"  • {result.message}"
                if result.field:
                    line += f" [Field: {result.field}]"
                if result.suggestion:
                    line += f" → {result.suggestion}"
                if result.rule_id:
                    line += f" ({result.rule_id})"
                output.append(line)

        return "\n".join(output)


def validate_neocortex_config() -> Tuple[bool, str]:
    """
    Comprehensive NeoCortex configuration validation.

    Returns:
        Tuple of (is_valid, validation_report).
    """
    from ..config import get_config

    validator = ConfigValidator()
    config = get_config()

    results = []

    # Validate environment
    results.extend(validator.validate_environment())

    # Validate configuration
    config_dict = config.to_dict()
    results.extend(validator.validate_config(config_dict))

    # Check critical paths
    critical_paths = [
        ("core_central", config.core_central),
        ("ledger", config.ledger_path),
        ("cortex", config.cortex_path),
    ]

    for name, path in critical_paths:
        if not path.exists():
            results.append(
                ValidationResult(
                    severity=ValidationSeverity.ERROR,
                    message=f"Critical path does not exist: {name}",
                    field=f"paths.{name}",
                    value=str(path),
                    suggestion="Check NeoCortex installation or run initialization",
                    rule_id="CRITICAL_PATH",
                )
            )

    # Check if any errors
    has_errors = any(
        r.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
        for r in results
    )

    report = validator.format_results(results)
    return not has_errors, report


def create_config_validator(schema: Optional[Dict[str, Any]] = None) -> ConfigValidator:
    """
    Create a ConfigValidator instance.

    Args:
        schema: Custom validation schema.

    Returns:
        ConfigValidator instance.
    """
    return ConfigValidator(schema=schema)
