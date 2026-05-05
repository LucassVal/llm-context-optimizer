#!/usr/bin/env python3
"""
Test HTTP endpoints of MCP server.
"""

import requests
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8765"
TIMEOUT = 3


def test_endpoint(path):
    url = f"{BASE_URL}{path}"
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        logger.info(f"GET {path} -> {resp.status_code} (len={len(resp.content)})")
        if resp.headers.get("content-type"):
            logger.info(f"  Content-Type: {resp.headers['content-type']}")
        if resp.status_code == 200 and len(resp.content) < 200:
            logger.info(f"  Content: {resp.text[:100]}")
        return True
    except requests.exceptions.ConnectionError:
        logger.error(f"GET {path} -> Connection refused")
        return False
    except Exception as e:
        logger.error(f"GET {path} -> Error: {e}")
        return False


def main():
    endpoints = [
        "/",
        "/health",
        "/sse",
        "/events",
        "/messages",
        "/api",
        "/api/health",
        "/api/sse",
        "/tools",
        "/list",
    ]
    success = True
    for ep in endpoints:
        if not test_endpoint(ep):
            success = False
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
