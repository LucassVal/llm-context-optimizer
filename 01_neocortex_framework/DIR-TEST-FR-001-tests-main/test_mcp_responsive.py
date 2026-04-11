#!/usr/bin/env python3
"""
Test MCP server responsiveness.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from neocortex.mcp.server import create_mcp_server, FAST_MCP_AVAILABLE


def test_server():
    print("Testing MCP server responsiveness...")
    print(f"FastMCP available: {FAST_MCP_AVAILABLE}")

    # Create server instance
    server = create_mcp_server()

    # List tools
    if FAST_MCP_AVAILABLE:
        # With FastMCP, tools are registered differently
        print("FastMCP server created")
        # We can't easily list tools without running the server
    else:
        # MockMCP
        print(f"MockMCP tools count: {len(server.tools)}")
        print("Available tools:")
        for tool_name in server.tools.keys():
            print(f"  - {tool_name}")

        # Test pulse tool
        if "neocortex_pulse" in server.tools:
            print("\nTesting neocortex_pulse tool...")
            try:
                result = server.tools["neocortex_pulse"](action="status")
                print(f"Pulse status: {result}")
            except Exception as e:
                print(f"Error calling pulse tool: {e}")
        else:
            print("neocortex_pulse tool not found")

    print("\nServer test completed.")


if __name__ == "__main__":
    test_server()
