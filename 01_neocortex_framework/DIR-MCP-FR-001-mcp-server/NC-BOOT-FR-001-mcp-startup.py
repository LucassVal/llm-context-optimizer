#!/usr/bin/env python3
"""
NC-BOOT-FR-001 - MCP Services Startup Script
Inicia todos os serviços MCP com naming convention NC-
"""

import subprocess
import sys
import time
import threading
import os

def start_service(script_name, description):
    """Start a service in a separate thread"""
    print(f"Iniciando {description}...")
    
    def run_script():
        try:
            # Usar o Python do sistema
            python_exe = sys.executable
            process = subprocess.Popen(
                [python_exe, script_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            # Aguardar um pouco para ver se inicia
            time.sleep(2)
            
            # Verificar se ainda está rodando
            if process.poll() is None:
                print(f"  ✅ {description} iniciado")
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"  ❌ {description} falhou: {stderr[:100]}")
                return None
                
        except Exception as e:
            print(f"  ❌ Erro ao iniciar {description}: {e}")
            return None
    
    thread = threading.Thread(target=run_script)
    thread.daemon = True
    thread.start()
    return thread

def main():
    print("=" * 60)
    print("NC-BOOT-FR-001 - Inicialização Serviços MCP Neocortex")
    print("=" * 60)
    print()
    
    # Lista de serviços para iniciar (arquivos NC-)
    services = [
        {
            'script': 'NC-SVC-FR-100-mcp-server.py',
            'description': 'MCP Server (porta 8765)',
            'port': 8765
        },
        {
            'script': 'NC-SVC-FR-101-litellm-gateway.py',
            'description': 'LiteLLM Gateway (porta 4000)',
            'port': 4000
        }
    ]
    
    # Verificar se os arquivos existem
    for service in services:
        if not os.path.exists(service['script']):
            print(f"❌ Arquivo não encontrado: {service['script']}")
            return
    
    # Iniciar serviços
    threads = []
    for service in services:
        thread = start_service(service['script'], service['description'])
        if thread:
            threads.append(thread)
    
    # Aguardar todos iniciarem
    time.sleep(3)
    
    print()
    print("=" * 60)
    print("STATUS DOS SERVIÇOS:")
    print("=" * 60)
    
    # Verificar portas
    import socket
    for service in services:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', service['port']))
        sock.close()
        
        if result == 0:
            print(f"✅ {service['description']}: ONLINE")
        else:
            print(f"❌ {service['description']}: OFFLINE")
    
    print()
    print("=" * 60)
    print("SERVIÇOS INICIADOS COM SUCESSO!")
    print("=" * 60)
    print()
    print("Pressione Ctrl+C para parar os serviços...")
    
    # Manter o script rodando
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nParando serviços...")

if __name__ == "__main__":
    main()