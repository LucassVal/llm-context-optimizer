#!/usr/bin/env python3
"""---
@Module  mcp Wrapper that suppresses internal error notificatio
---
"""

"""---
@Module  mcp Wrapper that suppresses internal error notificatio
---
"""

"""Wrapper that suppresses internal error notifications from reaching stdout."""
import sys
import os
import json

# Redirect stderr to suppress noisy startup logs
sys.stderr = open(os.devnull, 'w')

# Set minimal environment
os.environ.setdefault("PYTHONPATH", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("NEOCORTEX_LOG_LEVEL", "ERROR")
os.environ.setdefault("PYTHONUTF8", "1")

# Now import and run the real server
from neocortex.mcp.server import create_mcp_server

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "websocket", "sse"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    mcp = create_mcp_server(host=args.host, port=args.port)
    transport = "sse" if args.transport in ["websocket", "sse"] else "stdio"
    mcp.run(transport=transport)
