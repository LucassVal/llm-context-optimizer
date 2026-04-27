@echo off
setlocal enabledelayedexpansion

title NeoCortex Stack Launcher
cls
echo ============================================================
echo    NEOCORTEX STACK LAUNCHER
echo    MCP Server + Mission Control
echo ============================================================
echo.

set ROOT=%~dp0
set FW=%ROOT%01_neocortex_framework
set MC_DIR=%ROOT%DIR-RES-CC-001-claude-leak-workzone\external-refs\mission-control
set PYTHON=C:\Program Files\Python312\python.exe

REM ─────────────────────────────────────────────
REM 1. VERIFICAR MCP SERVER (porta 8765)
REM ─────────────────────────────────────────────
echo [CHECK] MCP Server (porta 8765)...
netstat -ano | findstr ":8765 " | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 (
    echo [  OK ] MCP Server ja esta ATIVO na porta 8765. Pulando.
    set MCP_STARTED=0
) else (
    echo [ INFO] MCP Server DOWN — iniciando em background...
    start "NeoCortex MCP" /min cmd /c "cd /d "%FW%\DIR-MCP-FR-001-mcp-server" && set NEOCORTEX_PROJECT_ROOT=%FW% && set NEOCORTEX_LOG_LEVEL=INFO && "%PYTHON%" NC-HUB-FR-001-mcp-hub.py --transport sse > nul 2>&1"
    set MCP_STARTED=1
    echo [ INFO] MCP Server spawnado. Aguardando 3s...
    timeout /t 3 /nobreak >nul
)

REM ─────────────────────────────────────────────
REM 2. VERIFICAR MISSION CONTROL (porta 3000)
REM ─────────────────────────────────────────────
echo.
echo [CHECK] Mission Control (porta 3000)...
netstat -ano | findstr ":3000 " | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 (
    echo [  OK ] Mission Control ja esta ATIVO na porta 3000.
    set MC_STARTED=0
) else (
    echo [ INFO] Mission Control DOWN — iniciando pnpm dev...
    if exist "%MC_DIR%\package.json" (
        start "Mission Control" /min cmd /c "cd /d "%MC_DIR%" && pnpm dev"
        set MC_STARTED=1
        echo [ INFO] Mission Control spawnado na porta 3000.
    ) else (
        echo [ ERRO] Diretorio Mission Control nao encontrado:
        echo         %MC_DIR%
    )
)

REM ─────────────────────────────────────────────
REM 3. ABRIR BROWSER NO MISSION CONTROL
REM ─────────────────────────────────────────────
echo.
if !MC_STARTED!==1 (
    echo [ INFO] Aguardando Mission Control iniciar (8s)...
    timeout /t 8 /nobreak >nul
)
echo [ INFO] Abrindo Mission Control no browser...
start "" "http://localhost:3000"

REM ─────────────────────────────────────────────
REM 4. STATUS FINAL
REM ─────────────────────────────────────────────
echo.
echo ============================================================
echo    STATUS FINAL
echo ============================================================
netstat -ano | findstr ":8765 " | findstr "LISTENING" >nul && echo    MCP Server :8765  [ATIVO] || echo    MCP Server :8765  [VERIFICAR]
netstat -ano | findstr ":3000 " | findstr "LISTENING" >nul && echo    Mission Control :3000  [ATIVO] || echo    Mission Control :3000  [AGUARDANDO]
netstat -ano | findstr ":8766 " | findstr "LISTENING" >nul && echo    Health Wrapper :8766  [ATIVO] || echo    Health Wrapper :8766  [OFF]
echo.
echo    Antigravity MCP: stdio (auto-spawn pelo IDE)
echo ============================================================
echo.
pause
