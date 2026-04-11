#!/usr/bin/env python3
"""
Simple test for MCP tools.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# Monkey-patch to prevent mcp.run() from actually running
import mcp.server

original_run = mcp.server.FastMCP.run


def mock_run(self, transport="stdio"):
    print(f"[MOCK] FastMCP.run() called with transport={transport}")
    # Don't actually run


mcp.server.FastMCP.run = mock_run

# Now import the module
try:
    import NC_MCP_FR_001_mcp_server as mcp_module

    print(" Module imported successfully")

    # Check mcp object
    if hasattr(mcp_module, "mcp"):
        mcp_obj = mcp_module.mcp
        print(f" MCP object: {mcp_obj.name}")

        # Check if tools are callable
        print("\nTesting tool functions:")

        # Test tool_cortex
        if hasattr(mcp_module, "tool_cortex"):
            try:
                result = mcp_module.tool_cortex("get_full")
                if result.get("success"):
                    print(" tool_cortex('get_full'): SUCCESS")
                else:
                    print(f" tool_cortex('get_full'): {result.get('error')}")
            except Exception as e:
                print(f" tool_cortex('get_full'): {e}")
        else:
            print(" tool_cortex not found")

        # Test other tools
        test_functions = [
            ("tool_manifest", "generate"),
            ("tool_kg", "add_entity"),
            ("tool_consolidation", "summarize_session"),
            ("tool_akl", "assess_importance"),
        ]

        for func_name, action in test_functions:
            if hasattr(mcp_module, func_name):
                print(f" {func_name} found")
            else:
                print(f" {func_name} not found")

    else:
        print(" No mcp object in module")

except Exception as e:
    print(f" Import error: {e}")
    import traceback

    traceback.print_exc()

# Restore original
mcp.server.FastMCP.run = original_run

print("\n=== Direct function test ===")
# Try to import functions directly from the file
import ast

with open("NC-MCP-FR-001-mcp-server.py", "r", encoding="utf-8") as f:
    content = f.read()

# Count tool decorators
tool_count = content.count("@mcp.tool")
print(f"Tool decorators found in source: {tool_count}")

# List them
import re

tool_matches = re.findall(r'@mcp\.tool\(name="([^"]+)"\)', content)
print(f"Tool names found: {len(tool_matches)}")
for tool in tool_matches:
    print(f"  - {tool}")
