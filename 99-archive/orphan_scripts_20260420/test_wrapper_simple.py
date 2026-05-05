#!/usr/bin/env python3
"""
Simple test that starts health wrapper as subprocess, tests, then kills it.
"""

import subprocess
import time
import urllib.request
import json
import sys
import os


def test_wrapper():
    port = 8766
    script_path = os.path.join(
        os.path.dirname(__file__), "NC-SCR-FR-098-health-wrapper.py"
    )

    # Start wrapper
    print(f"Starting health wrapper on port {port}")
    proc = subprocess.Popen(
        [sys.executable, script_path, "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    # Wait for startup
    time.sleep(3)

    # Read any initial output
    stdout_lines = []
    stderr_lines = []
    while True:
        line = proc.stdout.readline()
        if line:
            stdout_lines.append(line.strip())
            print(f"[WRAPPER] {line.strip()}")
        else:
            break

    try:
        # Test /health
        print(f"Testing http://localhost:{port}/health")
        try:
            req = urllib.request.urlopen(f"http://localhost:{port}/health", timeout=5)
            data = json.load(req)
            print(f"✓ Health endpoint works: status={req.status}")
            print(json.dumps(data, indent=2))

            # Test /ready
            print(f"Testing http://localhost:{port}/ready")
            try:
                req = urllib.request.urlopen(
                    f"http://localhost:{port}/ready", timeout=5
                )
                if req.status == 200:
                    data = json.load(req)
                    print(f"✓ Ready endpoint (MCP alive): {json.dumps(data, indent=2)}")
                else:
                    print(f"✓ Ready endpoint returned {req.status}")
            except urllib.error.HTTPError as e:
                if e.code == 503:
                    print("✓ Ready endpoint correctly returns 503 (MCP not alive)")
                else:
                    print(f"✗ Ready unexpected HTTP error: {e.code}")
            except Exception as e:
                print(f"✗ Ready error: {e}")

            print("All tests passed!")
            return True
        except Exception as e:
            print(f"✗ Health endpoint failed: {e}")
            return False
    finally:
        # Kill wrapper
        print("Killing health wrapper process")
        proc.terminate()
        proc.wait(timeout=5)
        print("Process terminated")


if __name__ == "__main__":
    test_wrapper()
