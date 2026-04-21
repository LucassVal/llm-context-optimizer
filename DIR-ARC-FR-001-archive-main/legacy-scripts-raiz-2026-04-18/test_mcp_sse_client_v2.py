#!/usr/bin/env python3
"""
Test MCP SSE client connection to NeoCortex server using mcp.client.sse.
"""

import asyncio
import logging
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_sse():
    url = "http://localhost:8765/sse"
    logger.info(f"Connecting to SSE server at {url}")
    try:
        async with sse_client(url) as (read, write):
            logger.info("SSE connection established")
            async with ClientSession(read, write) as session:
                # Initialize
                logger.info("Initializing session...")
                init_result = await session.initialize(
                    protocol_version="2024-11-05",
                    client_info={"name": "test-client", "version": "1.0"},
                    capabilities={},
                )
                logger.info(f"Initialized: {init_result}")

                # List tools
                logger.info("Listing tools...")
                tools_result = await session.list_tools()
                logger.info(f"Tools available: {len(tools_result.tools)}")
                for tool in tools_result.tools:
                    logger.info(f"  - {tool.name}: {tool.description}")

                # List resources
                logger.info("Listing resources...")
                resources_result = await session.list_resources()
                logger.info(f"Resources available: {len(resources_result.resources)}")
                for resource in resources_result.resources:
                    logger.info(f"  - {resource.uri}: {resource.name}")

                # Finish
                await session.finish()
                logger.info("Test completed successfully")
                return True
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_sse())
    exit(0 if success else 1)
