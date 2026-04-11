#!/usr/bin/env python3
"""
Generate official NeoCortex Tool Manifest (NC-TLM-FR-001-tool-manifest.json).
"""

import json
import importlib
import inspect
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Paths
TOOLS_DIR = Path(__file__).parent / "neocortex" / "mcp" / "tools"
OUTPUT_PATH = (
    Path(__file__).parent
    / "DIR-CORE-FR-001-core-central"
    / "NC-TLM-FR-001-tool-manifest.json"
)
SCHEMA_PATH = (
    Path(__file__).parent
    / "DIR-CORE-FR-001-core-central"
    / "NC-TLM-FR-001-tool-manifest-schema.json"
)

# Tool categories mapping
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
        if "Actions:" in stripped or "Ações:" in stripped:
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


def process_tool_module(module_name: str) -> Dict[str, Any]:
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
            display_name = "Córtex Central"
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

        return {
            "name": tool_name,
            "display_name": display_name,
            "description": description,
            "category": category,
            "version": "1.0.0",
            "actions": actions,
            "access_control": access_control,
            "metadata": {"module": module_name, "action_count": len(actions)},
        }

    except Exception as e:
        print(f"  ERROR processing {module_name}: {e}")
        import traceback

        traceback.print_exc()
        return None


def main():
    print("Generating official NeoCortex Tool Manifest...")

    # Tool modules
    tool_modules = list(TOOL_CATEGORIES.keys())

    all_tools = []

    for module_name in tool_modules:
        print(f"  Processing {module_name}...")
        tool_info = process_tool_module(module_name)
        if tool_info:
            all_tools.append(tool_info)
            print(
                f"    -> {tool_info['display_name']} ({tool_info['category']}) with {len(tool_info['actions'])} actions"
            )
        else:
            print(f"    -> Failed to process")

    # Create manifest structure
    manifest = {
        "$schema": "neocortex-tool-manifest-v1.0",
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat() + "Z",
        "server_name": "neocortex",
        "tools": all_tools,
        "custom_tools": [],
        "categories": CATEGORY_DESCRIPTIONS,
    }

    # Write to file
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Tool Manifest generated: {OUTPUT_PATH}")
    print(f"[STATS] Statistics:")
    print(f"   Total tools: {len(all_tools)}")
    total_actions = sum(len(tool.get("actions", [])) for tool in all_tools)
    print(f"   Total actions: {total_actions}")
    print(f"   Categories: {len(set(tool['category'] for tool in all_tools))}")

    # Validate against schema (optional)
    try:
        import jsonschema

        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        jsonschema.validate(manifest, schema)
        print(f"[OK] Manifest validated against schema")
    except ImportError:
        print(f"[WARN] jsonschema not installed, skipping validation")
    except Exception as e:
        print(f"[WARN] Schema validation failed: {e}")


if __name__ == "__main__":
    main()
