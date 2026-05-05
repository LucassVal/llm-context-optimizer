#!/usr/bin/env python3
"""
Simple SSE test for NeoCortex MCP server.
"""

import requests
import time

url = "http://localhost:8765/sse"
print(f"Connecting to SSE: {url}")

try:
    response = requests.get(url, stream=True, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}")

    # Read a few lines
    line_count = 0
    for line in response.iter_lines(decode_unicode=True):
        if line:
            print(f"Line {line_count}: {line}")
            line_count += 1
            if line_count >= 10:
                break
        time.sleep(0.1)

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
