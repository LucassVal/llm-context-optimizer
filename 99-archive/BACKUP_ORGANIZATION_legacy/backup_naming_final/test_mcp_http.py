#!/usr/bin/env python3
"""
Testar se painel está tentando acessar MCP via HTTP
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import time

class MCPTestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"GET request: {self.path}")
        
        if self.path == '/mcps' or self.path == '/mcps/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'ok',
                'mcp_servers': [
                    {
                        'name': 'neocortex-mcp-server',
                        'port': 8765,
                        'status': 'running',
                        'tools': 17
                    }
                ]
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(f"POST request: {self.path}")
        print(f"Data: {post_data.decode('utf-8')[:200]}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {'status': 'received', 'path': self.path}
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def log_message(self, format, *args):
        # Silenciar logs padrão
        pass

def start_test_server(port=8766):
    """Iniciar servidor HTTP de teste"""
    server = HTTPServer(('localhost', port), MCPTestHandler)
    print(f"Servidor HTTP teste iniciado na porta {port}")
    print(f"Teste acessar: http://localhost:{port}/mcps")
    
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    
    return server

def main():
    print("Testando endpoints HTTP para MCP...")
    print("=" * 60)
    
    # Iniciar servidor de teste
    server = start_test_server(8766)
    
    print("\nEndpoints disponíveis:")
    print("1. Socket MCP: localhost:8765 (JSON-RPC over TCP)")
    print("2. HTTP Test: http://localhost:8766/mcps")
    print("\nO painel pode estar tentando acessar via HTTP em vez de socket.")
    print("\nPressione Ctrl+C para parar...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nParando servidor de teste...")
        server.shutdown()

if __name__ == "__main__":
    main()