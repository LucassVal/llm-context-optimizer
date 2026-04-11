#!/usr/bin/env python3
"""
Generate tools manifest JSON for NeoCortex MCP tools.
"""

import importlib
import inspect
import json
import re
from pathlib import Path
from typing import Dict, Any, List

# Path to tools directory
TOOLS_DIR = Path(__file__).parent / "neocortex" / "mcp" / "tools"

# List of all tool modules (exclude __init__.py)
TOOL_MODULES = [
    "cortex",
    "lobes",
    "checkpoint",
    "regression",
    "ledger",
    "benchmark",
    "agent",
    "init",
    "config",
    "export",
    "manifest",
    "kg",
    "consolidation",
    "akl",
    "peers",
    "security",
]


def extract_actions_from_docstring(docstring: str) -> List[Dict[str, str]]:
    """Extract actions from docstring lines like '- action: description'."""
    if not docstring:
        return []

    actions = []
    lines = docstring.split("\n")
    in_actions_section = False

    for line in lines:
        stripped = line.strip()
        # Look for "Actions:" or "Actions:" in any language
        if "Actions:" in stripped or "Ações:" in stripped or "actions:" in stripped:
            in_actions_section = True
            continue

        if in_actions_section:
            # End of section when we hit a blank line or new section
            if (
                not stripped
                or stripped.startswith("Parameters")
                or stripped.startswith("Returns")
            ):
                break

            # Match lines like "- action: description" or "- action: description"
            match = re.match(r"^[-*]\s+(\w+):\s*(.+)$", stripped)
            if match:
                action_name = match.group(1)
                action_desc = match.group(2)
                actions.append(
                    {"name": action_name, "description": action_desc.strip()}
                )
            else:
                # Try pattern without colon: "- action description"
                match2 = re.match(r"^[-*]\s+(\w+)\s+(.+)$", stripped)
                if match2:
                    action_name = match2.group(1)
                    action_desc = match2.group(2)
                    actions.append(
                        {"name": action_name, "description": action_desc.strip()}
                    )

    return actions


def extract_parameters_from_signature(func) -> List[Dict[str, str]]:
    """Extract parameters from function signature."""
    sig = inspect.signature(func)
    params = []

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        param_info = {
            "name": param_name,
            "type": str(param.annotation)
            if param.annotation != inspect.Parameter.empty
            else "Any",
            "default": str(param.default)
            if param.default != inspect.Parameter.empty
            else None,
            "required": param.default == inspect.Parameter.empty,
        }
        params.append(param_info)

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

        # We need to get the tool function inside register_tool
        # Since register_tool returns the tool function, we can call it with a mock mcp
        # to get the function. Let's create a mock mcp that captures the decorator.
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

        # Get description (first line of docstring)
        description = ""
        if docstring:
            lines = docstring.split("\n")
            for line in lines:
                if line.strip() and not line.strip().startswith("Actions:"):
                    description = line.strip()
                    break

        # Extract actions
        actions = extract_actions_from_docstring(docstring)

        # Extract parameters
        parameters = extract_parameters_from_signature(tool_func)

        return {
            "name": tool_name,
            "module": module_name,
            "description": description,
            "full_description": docstring,
            "actions": actions,
            "parameters": parameters,
            "action_count": len(actions),
        }

    except Exception as e:
        print(f"  ERROR processing {module_name}: {e}")
        return None


def main():
    print("Generating tools manifest...")

    all_tools = []

    for module_name in TOOL_MODULES:
        print(f"  Processing {module_name}...")
        tool_info = process_tool_module(module_name)
        if tool_info:
            all_tools.append(tool_info)
            print(
                f"    -> {tool_info['name']} with {tool_info['action_count']} actions"
            )
        else:
            print(f"    -> Failed to process")

    # Create manifest structure
    manifest = {
        "version": "4.2-cortex",
        "schema_version": "1.0.0",
        "generated_at": "2026-04-10T12:30:00Z",  # TODO: use actual timestamp
        "total_tools": len(all_tools),
        "total_actions": sum(tool.get("action_count", 0) for tool in all_tools),
        "tools": all_tools,
    }

    # Write to file
    output_path = TOOLS_DIR.parent / "tools_manifest.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nManifest generated: {output_path}")
    print(f"Total tools: {len(all_tools)}")
    print(f"Total actions: {manifest['total_actions']}")


if __name__ == "__main__":
    main()
