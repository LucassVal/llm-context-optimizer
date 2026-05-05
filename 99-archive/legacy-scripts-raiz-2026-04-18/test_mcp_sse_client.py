#!/usr/bin/env python3
"""
Test MCP SSE client connection to NeoCortex server.
"""

import asyncio
import logging
from mcp.client import Client
from mcp.client.sse import sse_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_sse():
    url = "http://localhost:8765/sse"
    logger.info(f"Connecting to SSE server at {url}")
    try:
        async with sse_client(url) as (read, write):
            logger.info("SSE connection established")
            # Initialize MCP client
            client = Client(read, write)
            await client.initialize(
                protocol_version="2024-11-05",
                client_info={"name": "test-client", "version": "1.0"},
            )
            logger.info("Initialized")
            # List tools
            tools = await client.list_tools()
            logger.info(f"Tools: {len(tools)}")
            for tool in tools:
                logger.info(f"  - {tool.name}")
            # Close
            await client.finish()
            return True
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_sse())
    exit(0 if success else 1)
