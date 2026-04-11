#!/usr/bin/env python3
"""
Test if MCP server can start without errors.
"""

import subprocess
import time
import sys
import os

print("Testing MCP server startup...")

# Run server with timeout
try:
    # Start process
    proc = subprocess.Popen(
        [sys.executable, "NC-MCP-FR-001-mcp-server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    # Wait a bit for initialization
    time.sleep(3)

    # Check if process is still running
    if proc.poll() is None:
        print("[OK] Server is running after 3 seconds")

        # Try to get any output
        try:
            stdout, stderr = proc.communicate(timeout=1)
            if stdout:
                print(f"Server stdout (first 500 chars): {stdout[:500]}")
            if stderr:
                print(f"Server stderr: {stderr[:500]}")
        except subprocess.TimeoutExpired:
            print("[OK] Server is responsive (no output yet)")

        # Kill process
        proc.terminate()
        try:
            proc.wait(timeout=2)
            print("[OK] Server terminated cleanly")
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            print("[OK] Server killed")
    else:
        # Process exited already
        stdout, stderr = proc.communicate()
        print(f"[FAIL] Server exited with code {proc.returncode}")
        if stdout:
            print(f"Stdout: {stdout[:1000]}")
        if stderr:
            print(f"Stderr: {stderr[:1000]}")

except Exception as e:
    print(f"[FAIL] Error starting server: {e}")
    import traceback

    traceback.print_exc()

print("\nTest complete.")
