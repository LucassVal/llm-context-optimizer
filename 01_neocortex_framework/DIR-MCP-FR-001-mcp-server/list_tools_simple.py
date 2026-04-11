#!/usr/bin/env python3
"""
List tools by forcing simulation mode.
"""

import sys
import os

# Force simulation mode by monkey-patching before import
sys.modules["mcp"] = None
sys.modules["mcp.server"] = None

# Now import the server module as a module
# We'll exec the entire file with FAST_MCP_AVAILABLE = False
with open("NC-MCP-FR-001-mcp-server.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace the FAST_MCP_AVAILABLE check
# Find the line "if FAST_MCP_AVAILABLE:" and comment it out
# Instead, we'll prepend a line setting FAST_MCP_AVAILABLE = False
code = "FAST_MCP_AVAILABLE = False\n" + code

# Execute in a namespace
namespace = {"__name__": "__list__", "__file__": "NC-MCP-FR-001-mcp-server.py"}
exec(code, namespace)

# Get mcp object
mcp = namespace["mcp"]

print("=== NeoCortex MCP Tools (Simulation Mode) ===")
print(f"Total tools: {len(mcp.tools)}")
print()

for i, tool_name in enumerate(sorted(mcp.tools.keys()), 1):
    print(f"{i:2d}. {tool_name}")

print()
if len(mcp.tools) == 16:
    print(" SUCCESS: All 16 tools implemented!")
else:
    print(f" WARNING: Expected 16 tools, found {len(mcp.tools)}")
