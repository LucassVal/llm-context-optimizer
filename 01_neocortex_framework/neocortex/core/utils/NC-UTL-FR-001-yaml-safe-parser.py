"""---
@Module NC-UTL-FR-001-yaml-safe-parser mcp _genealogy:   injected_at: '2026-04-16T00:23:59.08
---
"""


"""
NC-UTL-FR-001-yaml-safe-parser.py
FR-001  YAML safe parser with regex fallback.

Provides safe YAML loading/dumping with regex fallback for simple fields.
Automatically detects if yaml is available; uses regex as fallback.
"""

import json
import re
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _ensure_yaml():
    """Ensure yaml module is available; import with fallback warning."""
    try:
        import yaml

        return yaml
    except ImportError:
        warnings.warn(
            "PyYAML not installed. Using regex fallback for simple YAML parsing.",
            ImportWarning,
            stacklevel=3,
        )
        return None


def safe_load(path: Path) -> Dict[str, Any]:
    """
    Load YAML file safely with regex fallback.

    Args:
        path: Path to YAML file

    Returns:
        Parsed dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty or malformed
    """
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return {}

    yaml_module = _ensure_yaml()
    if yaml_module is not None:
        try:
            return yaml_module.safe_load(content) or {}
        except Exception as e:
            warnings.warn(
                f"YAML parsing failed ({e}), falling back to regex",
                RuntimeWarning,
                stacklevel=2,
            )

    # Regex fallback for simple key: value pairs
    result = {}
    # Match lines with key: value (ignoring comments and empty lines)
    pattern = r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*?)\s*(?:#.*)?$"
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(pattern, line)
        if match:
            key = match.group(1)
            value_str = match.group(2).strip()
            # Try to parse value (int, float, bool, string)
            if value_str.lower() in ("true", "false"):
                value = value_str.lower() == "true"
            elif value_str.isdigit():
                value = int(value_str)
            elif re.match(r"^-?\d+\.\d+$", value_str):
                value = float(value_str)
            elif value_str.startswith('"') and value_str.endswith('"'):
                value = value_str[1:-1]
            elif value_str.startswith("'") and value_str.endswith("'"):
                value = value_str[1:-1]
            else:
                value = value_str
            result[key] = value
    return result


def safe_dump(data: Dict[str, Any], path: Path) -> None:
    """
    Dump dictionary to YAML file safely.

    Args:
        data: Dictionary to dump
        path: Path to write YAML file

    Raises:
        IOError: If write fails
    """
    yaml_module = _ensure_yaml()
    if yaml_module is not None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                yaml_module.safe_dump(data, f, default_flow_style=False)
            return
        except Exception as e:
            warnings.warn(
                f"YAML dump failed ({e}), falling back to JSON",
                RuntimeWarning,
                stacklevel=2,
            )

    # JSON fallback
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_field(path: Path, field: str) -> Optional[str]:
    """
    Extract field from YAML file without full parsing.

    Args:
        path: Path to YAML file
        field: Field name to extract

    Returns:
        Field value as string, or None if not found
    """
    if not path.exists():
        return None

    content = path.read_text(encoding="utf-8")
    # Look for field: value pattern
    pattern = rf"^\s*{re.escape(field)}\s*:\s*(.*?)\s*(?:#.*)?$"
    for line in content.splitlines():
        match = re.match(pattern, line)
        if match:
            return match.group(1).strip()
    return None


def set_field(path: Path, field: str, value: str) -> None:
    """
    Update field in YAML file without full parsing.

    Args:
        path: Path to YAML file
        field: Field name to update
        value: New value

    Note:
        Creates file if it doesn't exist.
    """
    if not path.exists():
        path.write_text(f"{field}: {value}\n", encoding="utf-8")
        return

    lines = []
    updated = False
    content = path.read_text(encoding="utf-8")
    pattern = rf"^\s*{re.escape(field)}\s*:"

    for line in content.splitlines(keepends=True):
        if re.match(pattern, line):
            lines.append(f"{field}: {value}\n")
            updated = True
        else:
            lines.append(line)

    if not updated:
        lines.append(f"{field}: {value}\n")

    path.write_text("".join(lines), encoding="utf-8")


def validate_schema(
    data: Dict[str, Any], required_fields: List[str]
) -> Tuple[bool, List[str]]:
    """
    Validate dictionary against required fields.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, list_of_missing_fields)
    """
    missing = [field for field in required_fields if field not in data]
    return (len(missing) == 0, missing)


# Convenience function
def load_yaml(path: str) -> Dict[str, Any]:
    """Convenience wrapper for safe_load."""
    return safe_load(Path(path))
