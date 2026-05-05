#!/usr/bin/env python3
"""
Fixed MCP Server without Unicode characters
"""

import socket
import threading
import json
import time
import sys
import signal

print('NC-SVC-FR-100 - MCP Server Service (17 tools)')

# List of 17 tools
TOOLS = [
    'neocortex_governance', 'neocortex_orchestration', 'neocortex_memory',
    'neocortex_state', 'neocortex_llm_router', 'neocortex_system',
    'neocortex_brain', 'neocortex_context', 'neocortex_security',
    'neocortex_benchmark', 'neocortex_notification', 'neocortex_akl',
    'neocortex_health', 'neocortex_ledger', 'neocortex_memory_auto',
    'neocortex_picoclaw', 'neocortex_pulse_bridge'
]

class MCPService100:
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.running = True
        
        # Initialize tools
        self.tools = {}
        for tool in TOOLS:
            tool_name = tool.replace('neocortex_', '')
            self.tools[tool] = {
                'description': f'Neocortex {tool_name} tool',
                'inputSchema': {'type': 'object', 'properties': {}}
            }
    
    def process_mcp_request(self, request_data):
        """Process MCP protocol requests"""
        try:
            # Limpar dados e remover newlines extras
            request_data = request_data.strip()
            if not request_data:
                error_response = {
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {'code': -32700, 'message': 'Parse error: Empty request'}
                }
                return json.dumps(error_response) + '\n'
                
            request = json.loads(request_data)
            method = request.get('method', '')
            params = request.get('params', {})
            request_id = request.get('id', 1)
            
            # MCP Protocol Methods
            if method == 'initialize':
                response = {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'protocolVersion': '2024-11-05',
                        'capabilities': {},
                        'serverInfo': {
                            'name': 'neocortex-mcp-server',
                            'version': '1.0.0'
                        }
                    }
                }
                
            elif method == 'tools/list':
                tools_list = []
                for tool_name, tool_info in self.tools.items():
                    tools_list.append({
                        'name': tool_name,
                        'description': tool_info['description'],
                        'inputSchema': tool_info['inputSchema']
                    })
                
                response = {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'tools': tools_list
                    }
                }
                
            elif method == 'tools/call':
                tool_name = params.get('name', '')
                arguments = params.get('arguments', {})
                
                if tool_name in self.tools:
                    # Simulate tool execution
                    result = {
                        'content': [{
                            'type': 'text',
                            'text': f'Tool {tool_name} executed with arguments: {arguments}'
                        }]
                    }
                    
                    response = {
                        'jsonrpc': '2.0',
                        'id': request_id,
                        'result': result
                    }
                else:
                    response = {
                        'jsonrpc': '2.0',
                        'id': request_id,
                        'error': {
                            'code': -32601,
                            'message': f'Tool not found: {tool_name}'
                        }
                    }
                    
            else:
                response = {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'error': {
                        'code': -32601,
                        'message': f'Method not found: {method}'
                    }
                }
                
            return json.dumps(response) + '\n'
            
        except Exception as e:
            error_response = {
                'jsonrpc': '2.0',
                'id': request_id if 'request_id' in locals() else 1,
                'error': {
                    'code': -32603,
                    'message': f'Internal error: {str(e)}'
                }
            }
            return json.dumps(error_response) + '\n'
    
    def handle_client(self, conn, addr):
        """Handle client connection"""
        try:
            print(f'Client connected: {addr}')
            buffer = ''
            
            while self.running:
                try:
                    # Receive data
                    data = conn.recv(4096)
                    if not data:
                        break
                        
                    buffer += data.decode('utf-8')
                    
                    # Process complete lines (MCP uses newline-separated JSON)
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            response = self.process_mcp_request(line)
                            conn.sendall(response.encode('utf-8'))
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f'Client read error {addr}: {e}')
                    break
                    
        except Exception as e:
            print(f'Client error {addr}: {e}')
            
        finally:
            conn.close()
            print(f'Client disconnected: {addr}')
    
    def start(self):
        """Start the MCP server"""
        # Create socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            # Bind and listen
            server_socket.bind((self.host, self.port))
            server_socket.listen(20)
            server_socket.settimeout(1)  # Timeout for accepting connections
            
            print(f'[OK] MCP SERVICE 100% ACTIVE')
            print(f'[INFO] Endpoint: {self.host}:{self.port}')
            print(f'[INFO] Tools: {len(self.tools)}')
            print('[INFO] Waiting for MCP connections...')
            print('=' * 50)
            
            # Main server loop
            while self.running:
                try:
                    # Accept connection
                    conn, addr = server_socket.accept()
                    
                    # Set timeout for client socket
                    conn.settimeout(2)
                    
                    # Process in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    # Normal timeout, continue loop
                    continue
                    
                except KeyboardInterrupt:
                    print('\n[INFO] Interruption received...')
                    break
                    
                except Exception as e:
                    print(f'[WARN] Server accept error: {e}')
                    continue
        
        except Exception as e:
            print(f'[ERROR] Server fatal error: {e}')
        
        finally:
            # Cleanup
            server_socket.close()
            print('[INFO] MCP Server stopped')

def main():
    """Main entry point"""
    # Handle Ctrl+C
    def signal_handler(sig, frame):
        print('\n[INFO] Shutting down MCP server...')
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start server
    service = MCPService100()
    service.start()

if __name__ == "__main__":
    main()