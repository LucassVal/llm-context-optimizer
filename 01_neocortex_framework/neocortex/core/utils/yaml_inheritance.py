#!/usr/bin/env python3
"""---
_genealogy:
  injected_at: '2026-04-14T22:00:00.000000'
  injected_by: manual
  version: '1.0'
topology: neocortex-other
level: 0
tags:
  - neocortex-other
  - level-0
  - python
  - yaml
  - inheritance
  - governance
---
YAML Inheritance Loader for NeoCortex Governance Templates.

Provides hierarchical inheritance resolution for YAML configuration files
using the `inherits_from` field. Supports deep merging of dictionaries
and smart merging of lists.
"""

import copy
from pathlib import Path
from typing import Any, Dict, List, Union

from . import load_yaml


def find_template_file(filename: str, base_dir: Path) -> Path:
    """
    Find a template file in search paths.

    Search order:
    1. Relative to base_dir
    2. In DIR-TMP-FR-001-templates-main directory relative to base_dir
    3. In DIR-TMP-FR-001-templates-main directory relative to parent directories
    4. In 01_neocortex_framework/DIR-TMP-FR-001-templates-main relative to project root

    Args:
        filename: Template filename
        base_dir: Base directory to start search

    Returns:
        Resolved Path

    Raises:
        FileNotFoundError: If template not found in any search path
    """
    # Try relative to base_dir
    candidate = base_dir / filename
    if candidate.exists():
        return candidate.resolve()

    # Try in templates directory relative to base_dir
    templates_dir = base_dir / "DIR-TMP-FR-001-templates-main"
    candidate = templates_dir / filename
    if candidate.exists():
        return candidate.resolve()

    # Try in templates directory relative to parent directories
    for up_level in range(1, 4):  # parent, grandparent, great-grandparent
        parent_dir = base_dir
        for _ in range(up_level):
            parent_dir = parent_dir.parent
        templates_dir = parent_dir / "DIR-TMP-FR-001-templates-main"
        candidate = templates_dir / filename
        if candidate.exists():
            return candidate.resolve()

    # Try in 01_neocortex_framework/DIR-TMP-FR-001-templates-main relative to project root
    # Project root is assumed to be 3 levels up from neocortex/core/utils
    project_root = (
        base_dir.parent.parent.parent
    )  # neocortex/core/utils -> neocortex -> .. -> project
    templates_dir = (
        project_root / "01_neocortex_framework" / "DIR-TMP-FR-001-templates-main"
    )
    candidate = templates_dir / filename
    if candidate.exists():
        return candidate.resolve()

    # Try in templates directory relative to project root
    templates_dir = project_root / "DIR-TMP-FR-001-templates-main"
    candidate = templates_dir / filename
    if candidate.exists():
        return candidate.resolve()

    # Try one more level up (in case base_dir is deeper)
    project_root2 = base_dir.parent.parent.parent.parent
    templates_dir = project_root2 / "DIR-TMP-FR-001-templates-main"
    candidate = templates_dir / filename
    if candidate.exists():
        return candidate.resolve()

    # Not found
    searched_dirs = [
        base_dir,
        base_dir / "DIR-TMP-FR-001-templates-main",
        project_root / "01_neocortex_framework" / "DIR-TMP-FR-001-templates-main",
        project_root / "DIR-TMP-FR-001-templates-main",
        project_root2 / "DIR-TMP-FR-001-templates-main",
    ]
    raise FileNotFoundError(
        f"Template file '{filename}' not found in search paths. "
        f"Looked in: {', '.join(str(d) for d in searched_dirs)}"
    )


def deep_merge(parent: Dict[str, Any], child: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge child dictionary into parent, with child values taking precedence.

    For lists, performs concatenation (child items appended to parent).
    For dictionaries, recursively merges.
    For other types, child overwrites parent.

    Args:
        parent: Parent dictionary
        child: Child dictionary

    Returns:
        Merged dictionary
    """
    result = copy.deepcopy(parent)

    for key, child_value in child.items():
        if key not in result:
            result[key] = child_value
            continue

        parent_value = result[key]

        # Handle list merging
        if isinstance(parent_value, list) and isinstance(child_value, list):
            # For tags and validation_rules, we want to append child items
            # but avoid duplicates based on certain criteria
            if key in ["tags", "validation_rules"]:
                # For tags, we need special handling because they can be strings or dicts
                merged_list = copy.deepcopy(parent_value)

                # For validation_rules, avoid duplicates by 'name' field
                if (
                    key == "validation_rules"
                    and parent_value
                    and isinstance(parent_value[0], dict)
                ):
                    existing_names = {
                        item.get("name") for item in parent_value if item.get("name")
                    }
                    for item in child_value:
                        if (
                            isinstance(item, dict)
                            and item.get("name") in existing_names
                        ):
                            # Replace existing rule with same name
                            for i, existing in enumerate(merged_list):
                                if isinstance(existing, dict) and existing.get(
                                    "name"
                                ) == item.get("name"):
                                    merged_list[i] = copy.deepcopy(item)
                                    break
                        else:
                            merged_list.append(copy.deepcopy(item))
                else:
                    # For tags, simple append (duplicates allowed)
                    merged_list.extend(copy.deepcopy(child_value))

                result[key] = merged_list
            else:
                # Default list behavior: concatenate
                result[key] = parent_value + child_value

        # Handle dictionary merging
        elif isinstance(parent_value, dict) and isinstance(child_value, dict):
            result[key] = deep_merge(parent_value, child_value)

        # Handle scalar values (child overwrites)
        else:
            result[key] = child_value

    return result


def resolve_inheritance(data: Dict[str, Any], base_dir: Path) -> Dict[str, Any]:
    """
    Resolve inheritance chain for a YAML dictionary.

    Args:
        data: Parsed YAML dictionary
        base_dir: Directory containing the YAML file (for resolving relative paths)

    Returns:
        Dictionary with all inherited values merged
    """
    if "inherits_from" not in data or data["inherits_from"] is None:
        return data

    parent_filename = data["inherits_from"]
    if not parent_filename:
        return data

    # Resolve parent file path using template search
    parent_path = find_template_file(parent_filename, base_dir)

    # Load parent and resolve its inheritance
    parent_data = load_yaml(str(parent_path))
    parent_data = resolve_inheritance(parent_data, parent_path.parent)

    # Merge child into parent (child values take precedence)
    merged = deep_merge(parent_data, data)

    # Preserve inherits_from from child (or remove if not needed)
    # Optionally, we could remove inherits_from after resolution
    # merged.pop('inherits_from', None)

    return merged


def load_yaml_with_inheritance(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load a YAML file and resolve its inheritance chain.

    Args:
        filepath: Path to YAML file

    Returns:
        Fully resolved dictionary with all inherited values
    """
    filepath = Path(filepath).resolve()
    if not filepath.exists():
        raise FileNotFoundError(f"YAML file not found: {filepath}")

    data = load_yaml(str(filepath))
    resolved = resolve_inheritance(data, filepath.parent)

    # Optionally remove inherits_from after resolution
    resolved.pop("inherits_from", None)

    return resolved


def validate_inheritance_chain(filepath: Union[str, Path]) -> List[str]:
    """
    Validate an inheritance chain and return list of resolved files.

    Args:
        filepath: Path to YAML file

    Returns:
        List of file paths in inheritance order (root to leaf)
    """
    filepath = Path(filepath).resolve()
    chain = [str(filepath)]

    data = load_yaml(str(filepath))
    base_dir = filepath.parent

    while "inherits_from" in data and data["inherits_from"] is not None:
        parent_filename = data["inherits_from"]
        parent_path = find_template_file(parent_filename, base_dir)

        chain.insert(0, str(parent_path))
        data = load_yaml(str(parent_path))
        base_dir = parent_path.parent

    return chain


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        try:
            resolved = load_yaml_with_inheritance(filepath)
            import yaml

            print(yaml.dump(resolved, default_flow_style=False, sort_keys=False))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print("Usage: python yaml_inheritance.py <yaml_file>")
