#!/usr/bin/env python3
"""Test MCP stdio communication with NeoCortex server."""

import json
import subprocess
import time
import os


def main():
    # Set environment variables
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework",
            "NEOCORTEX_PROJECT_ROOT": r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\.neocortex_stdio",
            "NEOCORTEX_LOG_LEVEL": "ERROR",
        }
    )

    # Start server
    cmd = [
        r"C:\Program Files\Python312\python.exe",
        "-m",
        "neocortex.mcp.server",
        "--transport",
        "stdio",
    ]
    print(f"Starting server: {' '.join(cmd)}")

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        bufsize=1,
    )

    # Give server time to initialize
    time.sleep(2)

    # Read any initial output
    import select

    # Set stdout non-blocking (Unix only) - not needed on Windows?
    # For Windows, we'll use threads or just read available data

    # Try to read stderr to see if there are errors
    import threading

    stderr_lines = []

    def read_stderr():
        while True:
            line = proc.stderr.readline()
            if line:
                stderr_lines.append(line)
                print(f"STDERR: {line.rstrip()}")
            else:
                break

    stderr_thread = threading.Thread(target=read_stderr)
    stderr_thread.daemon = True
    stderr_thread.start()

    # Send initialize request (MCP protocol)
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "test-client", "version": "1.0"},
            "capabilities": {},
        },
    }

    request_json = json.dumps(init_request)
    print(f"Sending: {request_json}")

    proc.stdin.write(request_json + "\n")
    proc.stdin.flush()

    # Wait for response
    time.sleep(1)

    # Try to read response
    response = None
    try:
        # Try to read a line from stdout
        import sys

        if sys.platform == "win32":
            # Windows non-blocking read

            # Use a loop to read available data
            import time

            start = time.time()
            output = []
            while time.time() - start < 2:
                # Check if there's data
                try:
                    line = proc.stdout.readline()
                    if line:
                        output.append(line)
                        print(f"Received: {line.rstrip()}")
                    else:
                        time.sleep(0.1)
                except:
                    break
            response = "".join(output)
        else:
            # Unix non-blocking
            import select

            if select.select([proc.stdout], [], [], 2)[0]:
                response = proc.stdout.readline()
                print(f"Received: {response}")
    except Exception as e:
        print(f"Error reading response: {e}")

    # Send exit notification
    exit_request = {"jsonrpc": "2.0", "method": "notifications/exit", "params": {}}

    proc.stdin.write(json.dumps(exit_request) + "\n")
    proc.stdin.flush()

    # Terminate
    proc.terminate()
    proc.wait(timeout=5)

    print(f"Server exited with code: {proc.returncode}")

    if response:
        print(f"Response: {response}")
    else:
        print("No response received")

    # Print stderr lines
    print("\nSTDERR lines:")
    for line in stderr_lines:
        print(f"  {line.rstrip()}")


if __name__ == "__main__":
    main()
