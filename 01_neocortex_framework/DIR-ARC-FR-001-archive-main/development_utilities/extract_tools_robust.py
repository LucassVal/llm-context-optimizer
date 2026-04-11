#!/usr/bin/env python3
"""
Robust extraction of MCP tools from monolithic server file.
"""

import re
from pathlib import Path

# Paths
MONOLITHIC_PATH = Path(
    r"neocortex_framework/DIR-MCP-FR-001-mcp-server/NC-MCP-FR-001-mcp-server.py"
)
TOOLS_DIR = Path(r"neocortex_framework/neocortex/mcp/tools")


def extract_tools_robust(content: str):
    """Extract all tool functions using regex."""
    # Pattern to match from @mcp.tool to next @mcp.tool or end of file
    # Use lookahead to find the next decorator or end
    pattern = r'(@mcp\.tool\(name="neocortex_\w+"\)\ndef tool_\w+\(.*?\) -> Dict\[str, Any\]:.*?)(?=\n@mcp\.tool|\Z)'

    # Use re.DOTALL to match across lines
    matches = re.finditer(pattern, content, re.DOTALL)

    tools = []
    for match in matches:
        tool_block = match.group(1).strip()
        # Extract tool name from decorator
        name_match = re.search(r'name="neocortex_(\w+)"', tool_block)
        if name_match:
            tool_name = name_match.group(1)
            tools.append((tool_name, tool_block))
        else:
            print(f"WARNING: Could not extract name from block")

    return tools


def generate_tool_module(tool_name: str, tool_block: str) -> str:
    """Generate complete Python module for a tool."""
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
    {tool_block}

    return tool_{tool_name}
'''
    return template


def main():
    print("Reading monolithic file...")
    content = MONOLITHIC_PATH.read_text(encoding="utf-8")

    print("Extracting tools with robust regex...")
    tools = extract_tools_robust(content)

    print(f"Found {len(tools)} tools")

    # Ensure tools directory exists
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)

    for tool_name, tool_block in tools:
        print(f"  Processing {tool_name}...")

        # Generate module content
        module_content = generate_tool_module(tool_name, tool_block)

        # Write to file
        output_path = TOOLS_DIR / f"{tool_name}.py"
        output_path.write_text(module_content, encoding="utf-8")
        print(f"    -> {output_path}")

    print("Done!")


if __name__ == "__main__":
    main()
