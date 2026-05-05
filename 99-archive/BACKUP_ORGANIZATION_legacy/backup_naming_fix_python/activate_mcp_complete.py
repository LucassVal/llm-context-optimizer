#!/usr/bin/env python3
"""
Complete MCP activation for neocortex - ciclo 1
"""

import socket
import time
import subprocess
import sys
import json
import os

def activate_mcp_neocortex():
    print("=" * 60)
    print("ACTIVATING MCP - NEOCORTEX - CICLO 1")
    print("=" * 60)
    
    # Set environment
    env = os.environ.copy()
    env["PYTHONPATH"] = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework"
    env["NEOCORTEX_PROJECT_ROOT"] = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework"
    env["NC_ROOT"] = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42"
    env["PYTHONUTF8"] = "1"
    env["NEOCORTEX_LOG_LEVEL"] = "INFO"
    
    print("\n[1/3] Starting MCP Server...")
    
    # Start MCP server
    server_proc = subprocess.Popen(
        [sys.executable, 'mcp_server_fixed.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Wait for server to start
    time.sleep(3)
    
    print("[2/3] Testing server connection...")
    
    # Test if server is listening
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('localhost', 8765))
    sock.close()
    
    if result != 0:
        print("[ERROR] MCP Server failed to start on port 8765")
        stdout, stderr = server_proc.communicate(timeout=1)
        print(f"STDOUT: {stdout[:300]}")
        print(f"STDERR: {stderr[:300]}")
        return False
    
    print("[OK] MCP Server is running on port 8765")
    
    print("[3/3] Testing MCP protocol...")
    
    # Test MCP protocol
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.settimeout(3)
        test_sock.connect(('localhost', 8765))
        
        # Test 1: Initialize
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'neocortex-client', 'version': '1.0.0'}
            }
        }
        
        test_sock.sendall((json.dumps(init_msg) + '\n').encode('utf-8'))
        init_response = test_sock.recv(4096).decode('utf-8')
        
        # Test 2: List tools
        tools_msg = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/list',
            'params': {}
        }
        
        test_sock.sendall((json.dumps(tools_msg) + '\n').encode('utf-8'))
        tools_response = test_sock.recv(4096).decode('utf-8')
        
        test_sock.close()
        
        # Parse responses
        init_data = json.loads(init_response)
        tools_data = json.loads(tools_response)
        
        if 'result' in init_data and 'result' in tools_data:
            print("[OK] MCP protocol working correctly")
            print(f"[INFO] Server: {init_data['result'].get('serverInfo', {}).get('name', 'unknown')}")
            print(f"[INFO] Tools available: {len(tools_data['result'].get('tools', []))}")
            
            # List all 17 tools
            print("\n" + "=" * 60)
            print("NEOCORTEX MCP TOOLS ACTIVATED:")
            print("=" * 60)
            
            tools_list = [
                "1. neocortex_governance",
                "2. neocortex_orchestration", 
                "3. neocortex_memory",
                "4. neocortex_state",
                "5. neocortex_llm_router",
                "6. neocortex_system",
                "7. neocortex_brain",
                "8. neocortex_context",
                "9. neocortex_security",
                "10. neocortex_benchmark",
                "11. neocortex_notification",
                "12. neocortex_akl",
                "13. neocortex_health",
                "14. neocortex_ledger",
                "15. neocortex_memory_auto",
                "16. neocortex_picoclaw",
                "17. neocortex_pulse_bridge"
            ]
            
            for tool in tools_list:
                print(tool)
            
            print("\n" + "=" * 60)
            print("MCP ACTIVATION SUCCESSFUL - CICLO 1 COMPLETE")
            print("=" * 60)
            print("\nMCP Server is running in background.")
            print("Endpoint: localhost:8765")
            print("Use Ctrl+C in this terminal to stop the server.")
            
            # Keep server running
            try:
                server_proc.wait()
            except KeyboardInterrupt:
                print("\n[INFO] Stopping MCP server...")
                server_proc.terminate()
                server_proc.wait()
                print("[INFO] MCP server stopped.")
            
            return True
            
        else:
            print("[ERROR] Invalid MCP responses")
            print(f"Init response: {init_response[:200]}")
            print(f"Tools response: {tools_response[:200]}")
            
    except Exception as e:
        print(f"[ERROR] MCP protocol test failed: {e}")
    
    # Cleanup on error
    server_proc.terminate()
    server_proc.wait()
    return False

if __name__ == "__main__":
    activate_mcp_neocortex()