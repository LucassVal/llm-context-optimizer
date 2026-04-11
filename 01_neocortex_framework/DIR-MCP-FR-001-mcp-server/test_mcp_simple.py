#!/usr/bin/env python3
"""
Simple test for NeoCortex MCP server.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
    import neocortex_mcp

    print("[OK] Module imported successfully")

    # Check basic attributes
    print(f"FAST_MCP_AVAILABLE: {neocortex_mcp.FAST_MCP_AVAILABLE}")

    if hasattr(neocortex_mcp, "mcp"):
        print(f"[OK] MCP object created: {neocortex_mcp.mcp.name}")

        # Check tools
        if hasattr(neocortex_mcp.mcp, "tools"):
            tools = neocortex_mcp.mcp.tools
            print(f"[OK] Tools registered: {len(tools)}")
            print("Tools list:")
            for tool_name in sorted(tools.keys()):
                print(f"  - {tool_name}")
        else:
            print("[FAIL] No tools attribute")
    else:
        print("[FAIL] No mcp object")

    # Test file paths
    print(f"\nCORTEX_PATH exists: {os.path.exists(neocortex_mcp.CORTEX_PATH)}")
    print(f"LEDGER_PATH exists: {os.path.exists(neocortex_mcp.LEDGER_PATH)}")

    # Test direct tool call
    if hasattr(neocortex_mcp, "tool_cortex"):
        try:
            result = neocortex_mcp.tool_cortex("get_full")
            if result.get("success"):
                print("[OK] tool_cortex('get_full') works")
            else:
                print(f"[FAIL] tool_cortex returned error: {result.get('error')}")
        except Exception as e:
            print(f"[FAIL] tool_cortex exception: {e}")
    else:
        print("[FAIL] tool_cortex not found")

except Exception as e:
    print(f"[FAIL] Overall error: {e}")
    import traceback

    traceback.print_exc()
