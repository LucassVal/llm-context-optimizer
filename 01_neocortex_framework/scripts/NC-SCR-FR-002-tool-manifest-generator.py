#!/usr/bin/env python3

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.612561'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TLM-FR-001-tool-manifest-
---
"""

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.612561'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TLM-FR-001-tool-manifest-
---
"""

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.612561'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TLM-FR-001-tool-manifest-schema
related_ssot:
  - NC-TLM-FR-001-tool-manifest
  - NC-SCR-FR-002-tool-manifest-generator
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

import io
import sys

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
domain: "orchestration"
layer: "core"
type: "SCR"
topology:
  parent: "neocortex_framework"
  children: ["NC-TLM-FR-001-tool-manifest.json", "tools_manifest.json", "mcp_tools_inventory.json"]
  dependence: ["python", "json", "importlib", "inspect"]
  tier: 1
tags: ['tools', 'manifest', 'mcp', 'ssot', 'generator']
hash: "auto-generated"
---

NeoCortex Tool Manifest Generator Master (SSOT)

This script is the Single Source of Truth for generating the NeoCortex MCP tool manifest.
It replaces the following redundant scripts:
- generate_tools_manifest.py
- generate_official_tool_manifest.py
- extract_tools_final.py
- merge_tool_manifests.py

The generated manifest follows the NC-TLM-FR-001-tool-manifest-schema.json schema
and includes comprehensive metadata per NC-RULE-007 (Topological Tagging System).
"""

import importlib
import inspect
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# ============================================================================
# PATHS CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent.parent  # 01_neocortex_framework root

# Add project root to Python path for module imports
sys.path.insert(0, str(BASE_DIR))

# Input paths (existing files for reference/merge)
TOOLS_MANIFEST_PATH = BASE_DIR / "neocortex" / "mcp" / "tools_manifest.json"
SSOT_PATH = (
    BASE_DIR / "DIR-CORE-FR-001-core-central" / "NC-TLM-FR-001-tool-manifest.json"
)
INVENTORY_PATH = BASE_DIR / "DIR-DOC-FR-001-docs-main" / "mcp_tools_inventory.json"
SCHEMA_PATH = (
    BASE_DIR
    / "DIR-CORE-FR-001-core-central"
    / "NC-TLM-FR-001-tool-manifest-schema.json"
)

# Output path (SSOT - will overwrite)
OUTPUT_PATH = SSOT_PATH

# Tool categories mapping (from generate_official_tool_manifest.py)
TOOL_CATEGORIES = {
    "cortex": "core",
    "lobes": "core",
    "checkpoint": "core",
    "regression": "validation",
    "ledger": "core",
    "benchmark": "monitoring",
    "agent": "automation",
    "init": "setup",
    "config": "configuration",
    "export": "data",
    "manifest": "metadata",
    "kg": "knowledge",
    "consolidation": "learning",
    "akl": "knowledge",
    "peers": "collaboration",
    "security": "security",
}

# Category descriptions
CATEGORY_DESCRIPTIONS = {
    "core": "Core framework operations and state management",
    "validation": "Validation, regression testing, and error handling",
    "monitoring": "Performance monitoring and benchmarking",
    "automation": "Agent automation and task management",
    "setup": "Project initialization and bootstrapping",
    "configuration": "Configuration management and settings",
    "data": "Data import/export and serialization",
    "metadata": "Metadata management and indexing",
    "knowledge": "Knowledge graph and semantic operations",
    "learning": "Learning consolidation and experience capture",
    "collaboration": "Multi-user and peer-to-peer collaboration",
    "security": "Security, access control, and auditing",
}

# ============================================================================
# METADATA FOR NC-RULE-007 COMPLIANCE
# ============================================================================

MANIFEST_METADATA = {
    "_meta": {
        "domain": "orchestration",
        "layer": "core",
        "type": "manifest",
        "topology": {
            "parent": "neocortex_framework",
            "children": ["NC-SCR-FR-002-tool-manifest-generator.py"],
            "dependence": ["python", "json"],
            "codependence": ["neocortex.mcp.tools.*"],
            "tier": 1,
        },
        "tags": ["tools", "manifest", "mcp", "ssot"],
        "hash": "auto-generated",  # Will be replaced with actual hash if desired
        "generated_by": "NC-SCR-FR-002-tool-manifest-generator.py",
        "generated_at": None,  # Will be set at generation time
        "schema_version": "1.0.0",
        "compliance": ["NC-RULE-007", "NC-TLM-FR-001-tool-manifest-schema.json"],
    }
}

# ============================================================================
# TOOL EXTRACTION FUNCTIONS
# ============================================================================


def extract_actions_from_docstring(docstring: str) -> List[Dict[str, Any]]:
    """Extract actions from docstring with parameter info."""
    if not docstring:
        return []

    actions = []
    lines = docstring.split("\n")
    current_action = None
    collecting_params = False

    for line in lines:
        stripped = line.strip()

        # Look for "Actions:" section
        if "Actions:" in stripped or "Aes:" in stripped:
            continue

        # Match action lines: "- action: description" or "- action description"
        action_match = re.match(r"^[-*]\s+(\w+):\s*(.+)$", stripped)
        if not action_match:
            action_match = re.match(r"^[-*]\s+(\w+)\s+(.+)$", stripped)

        if action_match:
            # Save previous action if exists
            if current_action:
                actions.append(current_action)

            action_name = action_match.group(1)
            action_desc = action_match.group(2).strip()

            current_action = {
                "name": action_name,
                "description": action_desc,
                "parameters": {},
                "returns": {
                    "type": "object",
                    "description": "JSON object with 'success' boolean and result data",
                },
            }
            collecting_params = False
            continue

        # Look for parameter sections
        if "Parameters for" in stripped and current_action:
            collecting_params = True
            continue

        # Parse parameter lines if we're in a parameter section
        if (
            collecting_params
            and current_action
            and stripped
            and not stripped.startswith("-")
        ):
            # Try to parse parameter: description
            param_match = re.match(r"^-\s+(\w+):\s*(.+)$", stripped)
            if param_match:
                param_name = param_match.group(1)
                param_desc = param_match.group(2).strip()

                # Determine parameter type from description
                param_type = "string"
                if "boolean" in param_desc.lower() or "bool" in param_desc.lower():
                    param_type = "boolean"
                elif (
                    "number" in param_desc.lower()
                    or "int" in param_desc.lower()
                    or "float" in param_desc.lower()
                ):
                    param_type = "number"
                elif "json" in param_desc.lower() or "object" in param_desc.lower():
                    param_type = "object"
                elif "array" in param_desc.lower() or "list" in param_desc.lower():
                    param_type = "array"

                current_action["parameters"][param_name] = {
                    "type": param_type,
                    "description": param_desc,
                    "required": "obrigatorio" in param_desc.lower()
                    or "required" in param_desc.lower(),
                }

    # Add last action
    if current_action:
        actions.append(current_action)

    return actions


def extract_parameters_from_signature(func) -> Dict[str, Dict[str, Any]]:
    """Extract parameters from function signature."""
    sig = inspect.signature(func)
    params = {}

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        # Map Python types to JSON schema types
        py_type = param.annotation
        type_str = "string"

        if py_type == inspect.Parameter.empty:
            type_str = "any"
        elif hasattr(py_type, "__name__"):
            if py_type.__name__ == "str":
                type_str = "string"
            elif py_type.__name__ in ["int", "float"]:
                type_str = "number"
            elif py_type.__name__ == "bool":
                type_str = "boolean"
            elif py_type.__name__ in ["Dict", "dict"]:
                type_str = "object"
            elif py_type.__name__ in ["List", "list"]:
                type_str = "array"
            else:
                type_str = "any"

        param_info = {
            "type": type_str,
            "description": f"Parameter {param_name}",
            "required": param.default == inspect.Parameter.empty,
            "default": str(param.default)
            if param.default != inspect.Parameter.empty
            else None,
        }

        params[param_name] = param_info

    return params


def process_tool_module(module_name: str) -> Optional[Dict[str, Any]]:
    """Process a single tool module and extract metadata."""
    try:
        module = importlib.import_module(
            f".tools.{module_name}", package="neocortex.mcp"
        )

        # Get the register_tool function
        register_func = getattr(module, "register_tool", None)
        if not register_func:
            print(f"  WARNING: Module {module_name} has no register_tool function")
            return None

        # Mock MCP to capture tool function
        class MockMCP:
            def __init__(self):
                self.tool_func = None
                self.tool_name = None

            def tool(self, name=None):
                def decorator(func):
                    self.tool_func = func
                    self.tool_name = name or func.__name__
                    return func

                return decorator

        mock_mcp = MockMCP()

        # Call register_tool with mock mcp
        try:
            register_func(mock_mcp)
        except Exception as e:
            print(f"  WARNING: Error calling register_tool for {module_name}: {e}")
            return None

        if not mock_mcp.tool_func:
            print(f"  WARNING: No tool function registered for {module_name}")
            return None

        tool_func = mock_mcp.tool_func
        tool_name = mock_mcp.tool_name or f"neocortex_{module_name}"

        # Extract information
        docstring = inspect.getdoc(tool_func) or ""

        # Get description (first non-empty line of docstring)
        description = ""
        if docstring:
            lines = docstring.split("\n")
            for line in lines:
                if line.strip() and not line.strip().startswith("Actions:"):
                    description = line.strip()
                    break

        # Extract actions
        actions = extract_actions_from_docstring(docstring)

        # Extract parameters from signature
        sig_params = extract_parameters_from_signature(tool_func)

        # Merge signature parameters with docstring parameters
        for action in actions:
            # The main action parameter is always 'action' string
            # Other parameters come from function signature
            for param_name, param_info in sig_params.items():
                if param_name not in action["parameters"]:
                    action["parameters"][param_name] = param_info

        # Determine category
        category = TOOL_CATEGORIES.get(module_name, "core")

        # Create display name
        display_name = module_name.replace("_", " ").title()
        if module_name == "cortex":
            display_name = "Crtex Central"
        elif module_name == "lobes":
            display_name = "Lobos"
        elif module_name == "kg":
            display_name = "Knowledge Graph"
        elif module_name == "akl":
            display_name = "Adaptive Knowledge Lifecycle"

        # Determine access control
        access_control = {"default_read": "authenticated", "default_write": "admin"}

        if module_name == "security":
            access_control["default_read"] = "admin"
            access_control["default_write"] = "system"

        # Add module-level metadata
        tool_metadata = {
            "module": module_name,
            "action_count": len(actions),
            "extracted_at": datetime.now().isoformat() + "Z",
        }

        return {
            "name": tool_name,
            "display_name": display_name,
            "description": description,
            "full_description": docstring,
            "category": category,
            "version": "1.0.0",
            "actions": actions,
            "access_control": access_control,
            "metadata": tool_metadata,
        }

    except Exception as e:
        print(f"  ERROR processing {module_name}: {e}")
        import traceback

        traceback.print_exc()
        return None


def load_existing_data() -> Dict[str, Any]:
    """Load data from existing manifest files for reference."""
    existing_data = {"tools_manifest": None, "ssot": None, "inventory": None}

    try:
        if TOOLS_MANIFEST_PATH.exists():
            with open(TOOLS_MANIFEST_PATH, "r", encoding="utf-8") as f:
                existing_data["tools_manifest"] = json.load(f)
            print(
                f"[INFO] Loaded tools_manifest.json with {len(existing_data['tools_manifest'].get('tools', []))} tools"
            )
    except Exception as e:
        print(f"[WARN] Could not load tools_manifest.json: {e}")

    try:
        if SSOT_PATH.exists():
            with open(SSOT_PATH, "r", encoding="utf-8") as f:
                existing_data["ssot"] = json.load(f)
            print(
                f"[INFO] Loaded SSOT manifest with {len(existing_data['ssot'].get('tools', []))} tools"
            )
    except Exception as e:
        print(f"[WARN] Could not load SSOT manifest: {e}")

    try:
        if INVENTORY_PATH.exists():
            with open(INVENTORY_PATH, "r", encoding="utf-8") as f:
                existing_data["inventory"] = json.load(f)
            print(
                f"[INFO] Loaded inventory with {len(existing_data['inventory'].get('tools', []))} tools"
            )
    except Exception as e:
        print(f"[WARN] Could not load inventory: {e}")

    return existing_data


def merge_tool_data(
    generated_tool: Dict[str, Any], existing_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Merge generated tool data with existing data from other sources."""
    # For now, return the generated tool as-is
    # In a more advanced implementation, we could merge descriptions,
    # parameters, etc. from existing sources
    return generated_tool


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================


def generate_manifest():
    """Generate the complete tool manifest."""
    print("=" * 70)
    print("NeoCortex Tool Manifest Generator Master (SSOT)")
    print("=" * 70)

    # Load existing data for reference
    existing_data = load_existing_data()

    # Process all tool modules
    print("\n[1/3] Processing tool modules...")
    tool_modules = list(TOOL_CATEGORIES.keys())

    all_tools = []
    success_count = 0
    fail_count = 0

    for module_name in tool_modules:
        print(f"  Processing {module_name}...", end=" ")
        tool_info = process_tool_module(module_name)
        if tool_info:
            # Merge with existing data if available
            merged_tool = merge_tool_data(tool_info, existing_data)
            all_tools.append(merged_tool)
            success_count += 1
            print(f"[OK] ({len(tool_info['actions'])} actions)")
        else:
            fail_count += 1
            print("[FAIL] failed")

    print(f"\n  Result: {success_count} succeeded, {fail_count} failed")

    # Build manifest structure
    print("\n[2/3] Building manifest structure...")

    # Update metadata with generation info
    metadata = MANIFEST_METADATA.copy()
    metadata["_meta"]["generated_at"] = datetime.now().isoformat() + "Z"
    metadata["_meta"]["total_tools_generated"] = len(all_tools)
    metadata["_meta"]["total_actions"] = sum(
        len(t.get("actions", [])) for t in all_tools
    )

    manifest = {
        "$schema": "neocortex-tool-manifest-v1.0",
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat() + "Z",
        "server_name": "neocortex",
        "tools": all_tools,
        "custom_tools": [],
        "categories": CATEGORY_DESCRIPTIONS,
    }

    # Add metadata as top-level _meta key
    manifest["_meta"] = metadata["_meta"]

    # Validate against schema
    print("\n[3/3] Validating manifest...")
    try:
        import jsonschema

        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        jsonschema.validate(manifest, schema)
        print("  [OK] Manifest validated against schema")
    except ImportError:
        print("  [WARN] jsonschema not installed, skipping validation")
    except Exception as e:
        print(f"  [WARN] Schema validation failed: {e}")

    # Backup existing SSOT if it exists
    if SSOT_PATH.exists():
        backup_path = SSOT_PATH.with_suffix(".json.backup")
        import shutil

        shutil.copy2(SSOT_PATH, backup_path)
        print(f"  [OK] Existing SSOT backed up to {backup_path}")

    # Write manifest
    print(f"\n[4/3] Writing manifest to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print(f"Total tools: {len(all_tools)}")
    print(f"Total actions: {sum(len(t.get('actions', [])) for t in all_tools)}")
    print(f"Output file: {OUTPUT_PATH}")
    print(f"Metadata: {json.dumps(manifest['_meta'], indent=2)}")
    print("=" * 70)

    return manifest


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    generate_manifest()
