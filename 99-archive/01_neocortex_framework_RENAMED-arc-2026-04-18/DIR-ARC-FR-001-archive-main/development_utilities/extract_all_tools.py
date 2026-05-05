#!/usr/bin/env python3
"""
Extract all MCP tools from monolithic server file to individual modules.
"""

import re
from pathlib import Path

# Paths
MONOLITHIC_PATH = Path(
    r"neocortex_framework/DIR-MCP-FR-001-mcp-server/NC-MCP-FR-001-mcp-server.py"
)
TOOLS_DIR = Path(r"neocortex_framework/neocortex/mcp/tools")


def extract_tools(content: str):
    """Extract all tool functions from monolithic file."""
    # Pattern to find tool decorators and their functions
    # We'll split by lines starting with @mcp.tool
    lines = content.split("\n")
    tools = []
    current_tool = None
    in_tool = False
    tool_lines = []
    indent_level = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Look for tool decorator
        if stripped.startswith("@mcp.tool"):
            if current_tool is not None:
                # Save previous tool
                tools.append({"name": current_tool, "lines": tool_lines})
            # Extract tool name from decorator
            match = re.search(r'name="neocortex_(\w+)"', stripped)
            if match:
                current_tool = match.group(1)
                tool_lines = [line]
                in_tool = True
            else:
                print(f"WARNING: Could not extract tool name from line: {stripped}")
                current_tool = None
                in_tool = False
        elif in_tool:
            tool_lines.append(line)
            # Check if we've reached the end of the function
            # Heuristic: if line is not empty and indentation level drops back to 0
            # (but we need to track indentation)
            if (
                stripped
                and not stripped.startswith(" ")
                and not stripped.startswith("\t")
                and not stripped.startswith("@")
            ):
                # Might be start of next function or top-level code
                # Check if this line looks like start of another tool or top-level code
                if stripped.startswith("def "):
                    # This is a new function definition, end current tool
                    # Remove the last line since it belongs to next function
                    tool_lines.pop()
                    tools.append({"name": current_tool, "lines": tool_lines})
                    # Start new tool
                    # Actually the decorator would have been caught earlier
                    # Reset state
                    current_tool = None
                    in_tool = False
                    tool_lines = []

    # Don't forget the last tool
    if current_tool is not None and tool_lines:
        tools.append({"name": current_tool, "lines": tool_lines})

    return tools


def generate_tool_module(tool_name: str, tool_lines: list) -> str:
    """Generate complete Python module for a tool."""
    # Join lines
    tool_content = "\n".join(tool_lines)

    # Extract function name (should be tool_{tool_name})
    func_name = f"tool_{tool_name}"

    # Template
    template = f'''#!/usr/bin/env python3
"""
NeoCortex {tool_name.capitalize()} Tool

Ferramenta MCP para neocortex_{tool_name}.
"""

from typing import Dict, Any
from ...core.file_utils import read_cortex, write_cortex, read_ledger, write_ledger, find_lobes, get_lobe_content


def register_tool(mcp):
    """
    Registra a ferramenta neocortex_{tool_name} no servidor MCP.
    """
{tool_content}

    return {func_name}
'''
    return template


def main():
    print("Reading monolithic file...")
    content = MONOLITHIC_PATH.read_text(encoding="utf-8")

    print("Extracting tools...")
    tools = extract_tools(content)

    print(f"Found {len(tools)} tools")

    # Ensure tools directory exists
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)

    for tool in tools:
        name = tool["name"]
        lines = tool["lines"]
        print(f"  Processing {name}...")

        # Generate module content
        module_content = generate_tool_module(name, lines)

        # Write to file
        output_path = TOOLS_DIR / f"{name}.py"
        output_path.write_text(module_content, encoding="utf-8")
        print(f"    -> {output_path}")

    print("Done!")


if __name__ == "__main__":
    main()
