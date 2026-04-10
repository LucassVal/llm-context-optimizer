#!/usr/bin/env python3
"""
NeoCortex CLI Tool

Command-line interface for the NeoCortex framework.
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="NeoCortex Framework CLI",
        epilog="For more information, see https://github.com/neocortex-framework/neocortex",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Server command
    server_parser = subparsers.add_parser("server", help="Start MCP server")
    server_parser.add_argument("--stdio", action="store_true", help="Use stdio mode")
    server_parser.add_argument(
        "--host", default="localhost", help="Host for socket mode"
    )
    server_parser.add_argument(
        "--port", type=int, default=8000, help="Port for socket mode"
    )

    # Info command
    info_parser = subparsers.add_parser("info", help="Show framework information")
    info_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Tools command
    tools_parser = subparsers.add_parser("tools", help="List available MCP tools")
    tools_parser.add_argument("--category", help="Filter by category")

    # Version command
    subparsers.add_parser("version", help="Show version information")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "server":
        from neocortex.mcp.server import create_mcp_server, FAST_MCP_AVAILABLE

        print(f"Starting NeoCortex MCP server...")

        # Create server
        server = create_mcp_server()

        if args.stdio:
            print("Running in stdio mode (for IDE integration)")
            if FAST_MCP_AVAILABLE:
                server.run(transport="stdio")
            else:
                server.run()
        else:
            print(f"Running in socket mode on {args.host}:{args.port}")
            # Note: Socket server implementation would go here
            print("Socket mode not yet implemented. Use --stdio for IDE integration.")
            return 1

    elif args.command == "info":
        from neocortex.core import get_cortex_service, get_ledger_service

        cortex_service = get_cortex_service()
        ledger_service = get_ledger_service()

        cortex_info = cortex_service.get_full_cortex()
        ledger_info = ledger_service.get_full_ledger()

        print("NeoCortex Framework Information")
        print("=" * 40)
        print(f"Version: {ledger_info.get('neocortex_version', 'N/A')}")
        print(f"System Type: {ledger_info.get('system_type', 'N/A')}")
        print(f"Architecture: {ledger_info.get('architecture', 'N/A')}")
        print(f"Cortex Size: {cortex_info['metadata']['size_chars']} chars")
        print(f"Lobes: {len(cortex_info.get('lobes', []))}")

        if args.verbose:
            print("\nSystem Constraints:")
            constraints = ledger_info.get("system_constraints", {})
            for key, value in constraints.items():
                print(f"  {key}: {value}")

    elif args.command == "tools":
        from neocortex.mcp.server import create_mcp_server
        import asyncio

        server = create_mcp_server()
        # FastMCP uses list_tools() method (async)
        if hasattr(server, "list_tools"):

            async def list_tools_async():
                return await server.list_tools()

            tools = asyncio.run(list_tools_async())
            print("Available MCP Tools:")
            print("=" * 40)
            if not tools:
                print("No tools found.")
                return 0
            for tool in tools:
                name = getattr(tool, "name", "Unknown")
                print(f"• {name}")
            return 0
        else:
            # Fallback for MockMCP
            tools = []
            if hasattr(server, "_tools") and isinstance(server._tools, dict):
                tools = list(server._tools.values())
            elif hasattr(server, "tools") and isinstance(server.tools, dict):
                tools = list(server.tools.values())
            elif hasattr(server, "_tools") and isinstance(server._tools, list):
                tools = server._tools
            elif hasattr(server, "tools") and isinstance(server.tools, list):
                tools = server.tools

            print("Available MCP Tools:")
            print("=" * 40)

            if not tools:
                print("No tools found.")
                return 0

            for tool in tools:
                name = getattr(tool, "name", "Unknown")
                print(f"• {name}")
            return 0

    elif args.command == "version":
        from neocortex.core import get_ledger_service

        ledger_service = get_ledger_service()
        ledger = ledger_service.get_full_ledger()

        version = ledger.get("neocortex_version", "4.2.0")
        print(f"NeoCortex Framework v{version}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Path: {Path(__file__).parent.parent.parent}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
