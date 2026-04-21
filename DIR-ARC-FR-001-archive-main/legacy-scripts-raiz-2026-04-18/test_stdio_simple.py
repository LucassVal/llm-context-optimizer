#!/usr/bin/env python3
import subprocess
import threading
import time
import os


def read_output(pipe, prefix):
    """Read lines from pipe and print with prefix."""
    try:
        for line in iter(pipe.readline, ""):
            if line:
                print(f"{prefix}: {line.rstrip()}")
    except Exception as e:
        print(f"{prefix} read error: {e}")


def main():
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework",
            "NEOCORTEX_PROJECT_ROOT": r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\.neocortex_stdio",
            "NEOCORTEX_LOG_LEVEL": "ERROR",
        }
    )

    cmd = [
        r"C:\Program Files\Python312\python.exe",
        "-m",
        "neocortex.mcp.server",
        "--transport",
        "stdio",
    ]

    print(f"Starting: {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        bufsize=1,
    )

    # Start reader threads
    stdout_thread = threading.Thread(target=read_output, args=(proc.stdout, "STDOUT"))
    stderr_thread = threading.Thread(target=read_output, args=(proc.stderr, "STDERR"))
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()

    # Wait a bit for server init
    time.sleep(3)

    # Send invalid JSON to see if server responds
    print("\nSending invalid JSON...")
    proc.stdin.write("invalid json\n")
    proc.stdin.flush()

    time.sleep(2)

    # Send empty line
    print("\nSending empty line...")
    proc.stdin.write("\n")
    proc.stdin.flush()

    time.sleep(2)

    # Send simple JSON-RPC request (initialize)
    import json

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "test", "version": "1.0"},
            "capabilities": {},
        },
    }
    print(f"\nSending: {json.dumps(request)}")
    proc.stdin.write(json.dumps(request) + "\n")
    proc.stdin.flush()

    # Wait for response
    time.sleep(3)

    # Check if process is still alive
    if proc.poll() is None:
        print("\nServer still running. Sending exit notification...")
        exit_msg = {"jsonrpc": "2.0", "method": "notifications/exit", "params": {}}
        proc.stdin.write(json.dumps(exit_msg) + "\n")
        proc.stdin.flush()
        time.sleep(1)
        proc.terminate()
    else:
        print(f"\nServer exited with code {proc.returncode}")

    proc.wait(timeout=5)
    print("Test completed.")


if __name__ == "__main__":
    main()
