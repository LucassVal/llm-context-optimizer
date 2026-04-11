@echo off
echo ========================================
echo    NeoCortex MCP Server (Host Mode)
echo    Conecta Assistentes via WebSocket
echo ========================================
echo.

set PYTHON_PATH="C:\Program Files\Python312\python.exe"

REM Verificar se Python está disponível
%PYTHON_PATH% --version >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Python explicito nao encontrado. Tentando 'python' no PATH...
    set PYTHON_PATH=python
    %PYTHON_PATH% --version >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python não encontrado
        pause
        exit /b 1
    )
)

REM Navegar para diretório do projeto
cd /d "%~dp001_neocortex_framework"

REM Iniciar servidor em modo WebSocket
echo [INFO] Iniciando NeoCortex MCP Server...
echo [INFO] API DeepSeek (T-0) Disponivel
echo [INFO] Host: localhost:8765
echo.

%PYTHON_PATH% -m neocortex.mcp.server --transport websocket --host 127.0.0.1 --port 8765

pause