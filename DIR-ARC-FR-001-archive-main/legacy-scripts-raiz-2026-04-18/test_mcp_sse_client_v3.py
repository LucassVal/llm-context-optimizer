#!/usr/bin/env python3
"""
Test MCP SSE client connection to NeoCortex server using mcp.client.sse.
"""

import asyncio
import logging
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from mcp.types import Implementation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_sse():
    url = "http://localhost:8765/sse"
    logger.info(f"Connecting to SSE server at {url}")
    try:
        async with sse_client(url) as (read, write):
            logger.info("SSE connection established")
            # Create session with client info
            client_info = Implementation(name="test-client", version="1.0")
            async with ClientSession(read, write, client_info=client_info) as session:
                # Initialize (no parameters needed)
                logger.info("Initializing session...")
                init_result = await session.initialize()
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

                # Try to call a simple tool if available
                if tools_result.tools:
                    tool_name = tools_result.tools[0].name
                    logger.info(f"Testing tool call: {tool_name}")
                    try:
                        # Call tool with empty arguments
                        call_result = await session.call_tool(tool_name, {})
                        logger.info(f"Tool call result: {call_result}")
                    except Exception as e:
                        logger.error(f"Tool call failed: {e}")

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
