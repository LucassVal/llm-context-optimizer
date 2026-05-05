#!/usr/bin/env python3
"""
Daemon para manter MCP server vivo.
Workaround para bug atexit que fecha servidor.
"""

import sys
import os
import time
import signal
import threading

# Configurar environment
framework_path = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework"
sys.path.insert(0, framework_path)

os.environ.update({
    "PYTHONPATH": framework_path,
    "NEOCORTEX_PROJECT_ROOT": framework_path,
    "NC_ROOT": r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42",
    "PYTHONUTF8": "1"
})

print("=== NeoCortex MCP Daemon ===")
print("Host: 127.0.0.1:8765")
print("Transport: SSE")
print("")

# Flag para shutdown graceful
shutdown_flag = threading.Event()

def signal_handler(sig, frame):
    print(f"\nRecebido sinal {sig}, desligando...")
    shutdown_flag.set()

# Registrar handlers de sinal
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    from neocortex.mcp.server import create_mcp_server
    
    print("Criando servidor MCP...")
    server = create_mcp_server(host='127.0.0.1', port=8765)
    
    print("Servidor criado. Iniciando em thread separada...")
    
    # Thread para rodar servidor
    def run_server():
        try:
            print("Iniciando server.run(transport='sse')...")
            server.run(transport='sse')
            print("server.run() retornou (inesperado)")
        except Exception as e:
            print(f"Erro em server.run(): {e}")
            import traceback
            traceback.print_exc()
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("Servidor iniciado. Aguardando 3 segundos para inicialização...")
    time.sleep(3)
    
    # Testar se porta abriu
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1', 8765))
    sock.close()
    
    if result == 0:
        print("✅ SUCCESS: Porta 8765 aberta e escutando!")
        print("Servidor MCP está rodando.")
        print("Pressione Ctrl+C para parar.")
    else:
        print("❌ FAIL: Porta 8765 não abriu.")
        print("Código erro:", result)
    
    # Manter processo vivo até sinal de shutdown
    print("\nMantendo processo vivo...")
    while not shutdown_flag.is_set():
        time.sleep(1)
        
        # Verificar se thread ainda está viva
        if not server_thread.is_alive():
            print("Thread do servidor morreu. Reiniciando...")
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            time.sleep(2)
    
    print("\nDesligando daemon...")
    
except Exception as e:
    print(f"ERRO CRÍTICO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)