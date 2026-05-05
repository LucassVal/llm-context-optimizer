#!/usr/bin/env python3
"""
Test WebSocket connection to MCP server.
"""

import asyncio
import websockets
import json
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mcp_websocket():
    uri = "ws://127.0.0.1:8765"
    try:
        logger.info(f"Connecting to {uri}...")
        async with websockets.connect(uri, open_timeout=5) as websocket:
            logger.info("Connected!")
            # Send a simple MCP initialization request
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "clientInfo": {"name": "test-client", "version": "1.0"},
                },
            }
            await websocket.send(json.dumps(init_msg))
            logger.info("Sent initialization request")
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            logger.info(f"Received: {response}")
            return True
    except asyncio.TimeoutError:
        logger.error("Timeout connecting or receiving response")
        return False
    except ConnectionRefusedError:
        logger.error("Connection refused - server not listening")
        return False
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp_websocket())
    sys.exit(0 if success else 1)
