#!/usr/bin/env python3
"""
Diagnóstico do MCP server para resolver problema /mcps failed
"""

import socket
import json
import time

def test_mcp_connection():
    print("=" * 60)
    print("DIAGNÓSTICO MCP SERVER")
    print("=" * 60)
    
    # Teste 1: Conexão básica
    print("\n1. Testando conexão na porta 8765...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex(('localhost', 8765))
    sock.close()
    
    if result != 0:
        print("   [ERROR] FALHA: MCP Server nao esta rodando na porta 8765")
        print("   Solucao: Iniciar o MCP server")
        return False
    
    print("   [OK] Servidor aceitando conexoes")
    
    # Teste 2: Protocolo MCP
    print("\n2. Testando protocolo MCP...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('localhost', 8765))
        
        # Initialize request
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'diagnostic-client', 'version': '1.0.0'}
            }
        }
        
        sock.sendall((json.dumps(init_msg) + '\n').encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        
        print(f"   Resposta: {response[:150]}")
        
        # Parse response
        try:
            data = json.loads(response)
            if 'result' in data:
                server_name = data['result'].get('serverInfo', {}).get('name', 'unknown')
                print(f"   [OK] Protocolo MCP funcionando")
                print(f"   Server: {server_name}")
                
                # Teste 3: List tools
                print("\n3. Testando listagem de ferramentas...")
                tools_msg = {
                    'jsonrpc': '2.0',
                    'id': 2,
                    'method': 'tools/list',
                    'params': {}
                }
                
                sock.sendall((json.dumps(tools_msg) + '\n').encode('utf-8'))
                tools_response = sock.recv(4096).decode('utf-8')
                
                try:
                    tools_data = json.loads(tools_response)
                    if 'result' in tools_data:
                        tools = tools_data['result'].get('tools', [])
                        print(f"   [OK] {len(tools)} ferramentas disponiveis")
                        return True
                    else:
                        error = tools_data.get('error', {}).get('message', 'Unknown')
                        print(f"   [ERROR] FALHA: Erro ao listar ferramentas: {error}")
                        return False
                except:
                    print(f"   [ERROR] FALHA: Resposta invalida para tools/list")
                    return False
                
                else:
                    error_msg = data.get('error', {}).get('message', 'Unknown error')
                    print(f"   [ERROR] FALHA: Erro no initialize: {error_msg}")
                    return False
                    
        except json.JSONDecodeError:
            print(f"   [ERROR] FALHA: Resposta nao e JSON valido")
            return False
            
        sock.close()
        
    except Exception as e:
        print(f"   [ERROR] FALHA: Erro no teste: {e}")
        return False

def check_mcp_services():
    """Verificar outros serviços MCP relacionados"""
    print("\n" + "=" * 60)
    print("VERIFICANDO SERVIÇOS RELACIONADOS")
    print("=" * 60)
    
    services = [
        ('MCP Server', 8765),
        ('LiteLLM Gateway', 4000),
        ('Ollama', 11434),
        ('Picoclaw', 18790),
        ('Mission Control', 3000)
    ]
    
    all_ok = True
    for name, port in services:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        status = "[OK] ONLINE" if result == 0 else "[ERROR] OFFLINE"
        print(f"   {name} (porta {port}): {status}")
        
        if result != 0 and name == 'MCP Server':
            all_ok = False
    
    return all_ok

def main():
    """Função principal"""
    # Testar conexão MCP
    mcp_ok = test_mcp_connection()
    
    # Verificar outros serviços
    services_ok = check_mcp_services()
    
    print("\n" + "=" * 60)
    print("RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    
    if mcp_ok and services_ok:
        print("[OK] TODOS OS TESTES PASSARAM")
        print("\nPossiveis causas para /mcps failed:")
        print("1. Painel usando endpoint diferente")
        print("2. Autenticacao necessaria")
        print("3. Timeout muito curto no painel")
        print("4. Formato de resposta diferente do esperado")
    elif not mcp_ok:
        print("[ERROR] MCP SERVER COM PROBLEMAS")
        print("\nAcoes recomendadas:")
        print("1. Reiniciar o MCP server")
        print("2. Verificar logs do servidor")
        print("3. Testar com cliente MCP simples")
    else:
        print("[WARN] MCP OK MAS OUTROS SERVICOS OFFLINE")
        print("\nServicos offline podem afetar funcionalidades do painel")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()