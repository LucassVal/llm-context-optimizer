#!/usr/bin/env python3
"""
Teste simples do MCP server
"""

import sys
import os

# Adicionar caminho do framework
framework_path = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework"
sys.path.insert(0, framework_path)

os.environ["PYTHONPATH"] = framework_path
os.environ["NEOCORTEX_PROJECT_ROOT"] = framework_path
os.environ["NC_ROOT"] = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42"
os.environ["PYTHONUTF8"] = "1"

print("Testando MCP server...")

try:
    from neocortex.mcp.server import create_mcp_server
    
    print("Criando servidor MCP...")
    server = create_mcp_server(host="127.0.0.1", port=8765)
    
    print(f"Servidor criado: {server}")
    print(f"Tipo: {type(server)}")
    
    # Testar health check tool
    if hasattr(server, 'health_check'):
        print("Health check tool disponível")
        result = server.health_check()
        print(f"Health check result: {result}")
    else:
        print("Health check tool NÃO disponível")
        
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()