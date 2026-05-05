#!/usr/bin/env python3
"""
Simplified MCP activation script for neocortex - ciclo 1
"""

import subprocess
import sys
import os
import time

def activate_mcp_neocortex():
    print("=" * 60)
    print("ACTIVATING MCP - NEOCORTEX - CICLO 1")
    print("=" * 60)
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework"
    env["NEOCORTEX_PROJECT_ROOT"] = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework"
    env["NC_ROOT"] = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42"
    env["PYTHONUTF8"] = "1"
    env["NEOCORTEX_LOG_LEVEL"] = "INFO"
    
    # MCP server command
    mcp_server_path = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-100-mcp-server.py"
    
    print(f"\nStarting MCP Server from: {mcp_server_path}")
    
    try:
        # Start MCP server
        process = subprocess.Popen(
            [sys.executable, mcp_server_path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            bufsize=1
        )
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("[OK] MCP Server is running (port 8765)")
            
            # Test connection
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 8765))
            sock.close()
            
            if result == 0:
                print("[OK] MCP Server is listening on port 8765")
                print("\n" + "=" * 60)
                print("MCP ACTIVATION SUCCESSFUL - CICLO 1 COMPLETE")
                print("=" * 60)
                print("\nMCP Server with 17 neocortex tools is now active.")
                print("Tools available:")
                print("- neocortex_governance")
                print("- neocortex_orchestration") 
                print("- neocortex_memory")
                print("- neocortex_state")
                print("- neocortex_llm_router")
                print("- neocortex_system")
                print("- neocortex_brain")
                print("- neocortex_context")
                print("- neocortex_security")
                print("- neocortex_benchmark")
                print("- neocortex_notification")
                print("- neocortex_akl")
                print("- neocortex_health")
                print("- neocortex_ledger")
                print("- neocortex_memory_auto")
                print("- neocortex_picoclaw")
                print("- neocortex_pulse_bridge")
                
                # Keep the process running
                print("\nPress Ctrl+C to stop the MCP server...")
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\nStopping MCP server...")
                    process.terminate()
                    process.wait()
                    print("MCP server stopped.")
                    
            else:
                print("[ERROR] MCP Server not responding on port 8765")
                process.terminate()
                process.wait()
                
        else:
            stdout, stderr = process.communicate()
            print(f"[ERROR] MCP Server failed to start")
            print(f"STDOUT: {stdout[:200]}")
            print(f"STDERR: {stderr[:200]}")
            
    except Exception as e:
        print(f"[ERROR] Failed to activate MCP: {e}")

if __name__ == "__main__":
    activate_mcp_neocortex()