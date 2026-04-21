#!/usr/bin/env python3
"""Test MCP client connection to NeoCortex server."""

import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client import stdio


async def main():
    # Set environment variables
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework",
            "NEOCORTEX_PROJECT_ROOT": r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\.neocortex_stdio",
            "NEOCORTEX_LOG_LEVEL": "ERROR",
        }
    )

    # Server command
    server_params = StdioServerParameters(
        command=r"C:\Program Files\Python312\python.exe",
        args=["-m", "neocortex.mcp.server", "--transport", "stdio"],
        env=env,
    )

    print("Connecting to NeoCortex MCP server...")

    try:
        async with stdio.stdio_server(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize
                print("Initializing...")
                result = await session.initialize(
                    protocol_version="2024-11-05",
                    client_info={"name": "test-client", "version": "1.0"},
                    capabilities={},
                )
                print(f"Initialize result: {result}")

                # List tools
                print("Listing tools...")
                tools = await session.list_tools()
                print(f"Tools available: {len(tools.tools)}")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")

                # List resources
                print("Listing resources...")
                resources = await session.list_resources()
                print(f"Resources available: {len(resources.resources)}")
                for resource in resources.resources:
                    print(f"  - {resource.uri}: {resource.name}")

                print("Test completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
