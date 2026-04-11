#!/usr/bin/env python3
"""
Test script to list all MCP tools implemented in NeoCortex server.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the mcp object from the server script
exec(open("NC-MCP-FR-001-mcp-server.py", encoding="utf-8").read())

# List all tools
print("=== NeoCortex MCP Tools ===")
print(f"Total tools: {len(mcp.tools)}")
print()

for i, (tool_name, tool_func) in enumerate(mcp.tools.items(), 1):
    print(f"{i:2d}. {tool_name}")
    # Try to get docstring
    doc = tool_func.__doc__
    if doc:
        # Extract first line
        first_line = doc.strip().split("\n")[0]
        print(f"    {first_line}")
    print()

# Verify count
expected_tools = 16
actual_tools = len(mcp.tools)
if actual_tools == expected_tools:
    print(f" SUCCESS: All {expected_tools} tools implemented!")
else:
    print(f" WARNING: Expected {expected_tools} tools, found {actual_tools}")
