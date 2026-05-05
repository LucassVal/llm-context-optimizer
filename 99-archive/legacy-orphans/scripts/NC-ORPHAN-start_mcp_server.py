#!/usr/bin/env python3
"""
Start NeoCortex MCP Server with SSE transport

This script starts the MCP server using FastMCP with SSE transport
instead of websocket, which is more stable for stdio-based clients.
"""

import sys
import os
from pathlib import Path

# Add the framework to the path
framework_dir = Path(__file__).parent / "01_neocortex_framework"
sys.path.insert(0, str(framework_dir))

try:
    # Import the main server module
    import neocortex.mcp.server as mcp_server
    
    print("Starting NeoCortex MCP Server v4.2-Cortex...")
    print("Transport: SSE (stdio)")
    print("Tools available: 15 super-tools")
    
    # Override sys.argv to pass the right arguments
    original_argv = sys.argv
    sys.argv = ["neocortex_mcp.py", "--transport", "sse", "--host", "127.0.0.1", "--port", "8765"]
    
    try:
        # Run the server with SSE transport
        mcp_server.main()
    finally:
        sys.argv = original_argv
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure FastMCP is installed: pip install mcp")
    sys.exit(1)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)