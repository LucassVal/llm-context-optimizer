@echo off
chcp 65001 > nul
echo ============================================================
echo NC-BOOT-FR-001 - Inicializacao Servicos MCP Neocortex
echo ============================================================
echo.

echo Iniciando MCP Server (porta 8765)...
start "MCP Server" python NC-SVC-FR-100-mcp-server.py
timeout /t 2 /nobreak > nul

echo Iniciando LiteLLM Gateway (porta 4000)...
start "LiteLLM Gateway" python NC-SVC-FR-101-litellm-gateway.py
timeout /t 2 /nobreak > nul

echo.
echo ============================================================
echo STATUS DOS SERVICOS:
echo ============================================================

:: Verificar portas
python -c "
import socket
import sys

services = [
    ('MCP Server', 8765),
    ('LiteLLM Gateway', 4000),
    ('Ollama', 11434),
    ('Picoclaw', 18790),
    ('Mission Control', 3000)
]

print('Verificando servicos...')
print()

for name, port in services:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    
    if result == 0:
        print(f'OK {name} (porta {port})')
    else:
        print(f'OFFLINE {name} (porta {port})')
"

echo.
echo ============================================================
echo SERVICOS INICIADOS!
echo ============================================================
echo.
echo Pressione qualquer tecla para sair...
pause > nul