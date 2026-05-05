#!/usr/bin/env python3
import subprocess
import json
import time
import sys

def test_mcp_server():
    """Testa a conexão com o servidor MCP NeoCortex"""
    
    # Configuração do comando
    cmd = [
        "C:/Program Files/Python312/python.exe",
        "-m",
        "neocortex.mcp.server",
        "--transport",
        "stdio"
    ]
    
    # Variáveis de ambiente
    env = {
        **os.environ,
        "PYTHONPATH": "C:/Users/Lucas Valério/Desktop/TURBOQUANT_V42/01_neocortex_framework",
        "NEOCORTEX_PROJECT_ROOT": "C:/Users/Lucas Valério/Desktop/TURBOQUANT_V42/01_neocortex_framework",
        "NC_ROOT": "C:/Users/Lucas Valério/Desktop/TURBOQUANT_V42",
        "PYTHONUTF8": "1",
        "NEOCORTEX_LOG_LEVEL": "ERROR"
    }
    
    print("Iniciando servidor MCP NeoCortex...")
    
    try:
        # Inicia o processo
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1
        )
        
        # Mensagem de inicialização
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print(f"Enviando: {json.dumps(init_msg)}")
        proc.stdin.write(json.dumps(init_msg) + "\n")
        proc.stdin.flush()
        
        # Lê resposta
        time.sleep(0.5)
        response = proc.stdout.readline()
        print(f"Resposta: {response}")
        
        # Encerra
        proc.terminate()
        proc.wait(timeout=2)
        
        print("✅ Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    import os
    test_mcp_server()