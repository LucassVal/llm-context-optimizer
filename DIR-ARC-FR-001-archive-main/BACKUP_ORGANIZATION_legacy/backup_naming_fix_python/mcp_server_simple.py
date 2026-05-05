#!/usr/bin/env python3
"""
MCP Server simplificado para NeoCortex
"""

import socket
import threading
import json
import time
import sys
import signal
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleMCPServer:
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.running = True
        self.tools = self._discover_tools()
        
    def _discover_tools(self):
        """Descobre ferramentas disponíveis"""
        tools = {}
        
        # Ferramentas básicas do neocortex
        base_tools = [
            'neocortex_governance', 'neocortex_orchestration', 'neocortex_memory',
            'neocortex_state', 'neocortex_llm_router', 'neocortex_system',
            'neocortex_brain', 'neocortex_context', 'neocortex_security',
            'neocortex_benchmark', 'neocortex_notification', 'neocortex_akl',
            'neocortex_health', 'neocortex_ledger', 'neocortex_memory_auto',
            'neocortex_picoclaw', 'neocortex_pulse_bridge'
        ]
        
        for tool in base_tools:
            tool_name = tool.replace('neocortex_', '')
            tools[tool] = {
                'description': f'Neocortex {tool_name} tool',
                'inputSchema': {'type': 'object', 'properties': {}},
                'methods': ['execute', 'status', 'configure']
            }
            
        logger.info(f'Descobertas {len(tools)} ferramentas')
        return tools
    
    def process_request(self, request_data):
        """Processa requisições MCP"""
        try:
            # Limpar dados (pode ter newlines extras)
            request_data = request_data.strip()
            if not request_data:
                return json.dumps({
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {'code': -32700, 'message': 'Parse error: Empty request'}
                }) + '\n'
                
            request = json.loads(request_data)
            method = request.get('method', '')
            params = request.get('params', {})
            request_id = request.get('id', 1)
            
            logger.info(f'Processando método: {method}')
            
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
                    'result': {'tools': tools_list}
                }
                
            elif method == 'tools/call':
                tool_name = params.get('name', '')
                arguments = params.get('arguments', {})
                
                if tool_name in self.tools:
                    result = {
                        'content': [{
                            'type': 'text',
                            'text': f'Tool {tool_name} executed successfully with arguments: {arguments}'
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
            
        except json.JSONDecodeError as e:
            logger.error(f'JSON decode error: {e}')
            return json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'error': {
                    'code': -32700,
                    'message': f'Parse error: {str(e)}'
                }
            }) + '\n'
        except Exception as e:
            logger.error(f'Internal error: {e}')
            return json.dumps({
                'jsonrpc': '2.0',
                'id': request_id if 'request_id' in locals() else 1,
                'error': {
                    'code': -32603,
                    'message': f'Internal error: {str(e)}'
                }
            }) + '\n'
    
    def handle_client(self, conn, addr):
        """Lida com cliente conectado"""
        try:
            logger.info(f'Cliente conectado: {addr}')
            buffer = ''
            
            while self.running:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                        
                    buffer += data.decode('utf-8')
                    
                    # Processar linhas completas
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            response = self.process_request(line)
                            conn.sendall(response.encode('utf-8'))
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f'Erro no cliente {addr}: {e}')
                    break
                    
        except Exception as e:
            logger.error(f'Erro handling cliente {addr}: {e}')
        finally:
            conn.close()
            logger.info(f'Cliente desconectado: {addr}')
    
    def start(self):
        """Inicia o servidor"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(20)
            server_socket.settimeout(1)
            
            logger.info(f'MCP Server iniciado em {self.host}:{self.port}')
            logger.info(f'Ferramentas disponíveis: {len(self.tools)}')
            logger.info('Aguardando conexões...')
            
            while self.running:
                try:
                    conn, addr = server_socket.accept()
                    conn.settimeout(2)
                    
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except KeyboardInterrupt:
                    logger.info('Interrupção recebida...')
                    break
                except Exception as e:
                    logger.error(f'Erro accept: {e}')
                    continue
                    
        except Exception as e:
            logger.error(f'Erro fatal: {e}')
        finally:
            server_socket.close()
            logger.info('MCP Server parado')

def main():
    """Função principal"""
    def signal_handler(sig, frame):
        print('\nParando servidor...')
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    server = SimpleMCPServer()
    server.start()

if __name__ == '__main__':
    main()