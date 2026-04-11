#!/usr/bin/env python3
"""
List all tools from NeoCortex MCP server without starting the server.
"""

import sys
import os

# Prevent main from running
sys.modules["__main__"] = type(sys)("__main__")

# Read the server file and execute only the parts we need
server_code = open("NC-MCP-FR-001-mcp-server.py", encoding="utf-8").read()

# Split by lines and execute up to the tool definitions
lines = server_code.split("\n")
# We'll execute the whole file but replace the __main__ guard
# Instead, let's just find where mcp is defined
# Look for "if FAST_MCP_AVAILABLE:" and execute that block
# We'll create a local namespace
namespace = {}
# Define FAST_MCP_AVAILABLE as True to match actual environment
namespace["FAST_MCP_AVAILABLE"] = True
namespace["__name__"] = "__notmain__"
namespace["logging"] = __import__("logging")
namespace["sys"] = sys
namespace["os"] = os
namespace["Path"] = __import__("pathlib").Path
namespace["json"] = __import__("json")
namespace["asyncio"] = __import__("asyncio")
namespace["__file__"] = "NC-MCP-FR-001-mcp-server.py"

# Execute the initialization part (up to line 90)
init_code = "\n".join(lines[:90])
exec(init_code, namespace)

# Get mcp object
mcp = namespace["mcp"]

print("=== NeoCortex MCP Tools ===")
print(f"Total tools: {len(mcp.tools)}")
print()

tool_names = sorted(mcp.tools.keys())
for i, tool_name in enumerate(tool_names, 1):
    print(f"{i:2d}. {tool_name}")

print()
print(
    " All 16 tools are present!"
    if len(mcp.tools) == 16
    else f" Missing {16 - len(mcp.tools)} tools"
)
