#!/usr/bin/env python3
"""
Proxy HTTP para MCP Socket
Converte requisições HTTP do painel para socket MCP
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import socket
import threading
import time

class MCPProxyHandler(BaseHTTPRequestHandler):
    def _send_mcp_request(self, method, params=None):
        """Enviar requisição para MCP server via socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(('localhost', 8765))
            
            request = {
                'jsonrpc': '2.0',
                'id': 1,
                'method': method,
                'params': params or {}
            }
            
            sock.sendall((json.dumps(request) + '\n').encode('utf-8'))
            response = sock.recv(4096).decode('utf-8')
            sock.close()
            
            return json.loads(response)
        except Exception as e:
            return {'error': {'code': -32000, 'message': f'MCP connection failed: {str(e)}'}}
    
    def do_GET(self):
        print(f"[PROXY] GET {self.path}")
        
        if self.path == '/mcps' or self.path == '/mcps/':
            # Endpoint do painel
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Testar conexão MCP
            init_response = self._send_mcp_request('initialize', {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'http-proxy', 'version': '1.0.0'}
            })
            
            if 'error' in init_response:
                status = 'error'
                message = init_response['error']['message']
            else:
                # Pegar lista de ferramentas
                tools_response = self._send_mcp_request('tools/list')
                
                if 'error' in tools_response:
                    status = 'partial'
                    message = 'Connected but tools list failed'
                    tools_count = 0
                else:
                    status = 'ok'
                    message = 'MCP server connected'
                    tools_count = len(tools_response.get('result', {}).get('tools', []))
            
            response = {
                'status': status,
                'message': message,
                'server': {
                    'name': 'neocortex-mcp-server',
                    'port': 8765,
                    'tools': tools_count if 'tools_count' in locals() else 0,
                    'protocol': 'json-rpc over tcp'
                },
                'proxy': {
                    'port': 8766,
                    'endpoint': '/mcps'
                }
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
            
        elif self.path == '/health':
            # Endpoint de health check
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {'status': 'ok', 'service': 'mcp-http-proxy'}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            method = data.get('method', '')
            params = data.get('params', {})
            
            print(f"[PROXY] POST {self.path} - Method: {method}")
            
            # Encaminhar para MCP server
            response = self._send_mcp_request(method, params)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {'error': {'code': -32700, 'message': f'Parse error: {str(e)}'}}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def log_message(self, format, *args):
        # Log personalizado
        print(f"[HTTP] {args[0]} - {args[1]}")

def start_proxy(port=8766):
    """Iniciar proxy HTTP"""
    server = HTTPServer(('localhost', port), MCPProxyHandler)
    print(f"Proxy HTTP MCP iniciado na porta {port}")
    print(f"Endpoints:")
    print(f"  GET  http://localhost:{port}/mcps    - Status do MCP server")
    print(f"  GET  http://localhost:{port}/health  - Health check")
    print(f"  POST http://localhost:{port}/        - Encaminhar para MCP")
    print(f"\nMCP Server: localhost:8765 (socket)")
    print(f"HTTP Proxy: localhost:{port} (http)")
    
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    
    return server

def main():
    print("=" * 60)
    print("PROXY HTTP PARA MCP SOCKET")
    print("=" * 60)
    print("\nEste proxy permite que o painel acesse o MCP server via HTTP.")
    print("Resolve o problema '/mcps failed' se o painel espera HTTP.")
    
    server = start_proxy()
    
    print("\nProxy rodando. Teste no navegador:")
    print(f"  http://localhost:8766/mcps")
    print("\nPressione Ctrl+C para parar...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nParando proxy...")
        server.shutdown()

if __name__ == "__main__":
    main()