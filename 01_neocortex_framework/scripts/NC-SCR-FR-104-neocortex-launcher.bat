@echo off
chcp 65001 >nul 2>&1
title NeoCortex MCP :8765 — Antigravity HTTP + OpenCode Stdio

rem Resolve paths via ~dp0 (filesystem canonical) — zero hardcoded absolute paths
rem Script location: 01_neocortex_framework\scripts\
rem   FW      = %~dp0..  (01_neocortex_framework)
rem   PROJECT = FW\..    (TURBOQUANT_V42)
for %%F in ("%~dp0..") do set "FW=%%~fF"
for %%P in ("%FW%\..") do set "PROJECT=%%~fP"

rem Porta e diretório de trabalho
set MCP_PORT=8765
cd /d "%FW%"

echo ================================================================
echo   NeoCortex MCP v5.0 — Startup
echo   HTTP Server :%MCP_PORT%/mcp (Antigravity)
echo   Stdio Server (OpenCode — auto via mcp.json)
echo ================================================================
echo.

if not exist "%FW%\" (
    echo [ERRO] Framework nao encontrado: %FW%
    pause
    exit /b 1
)

set PYTHONPATH=%FW%;%PROJECT%
set NEOCORTEX_PROJECT_ROOT=%FW%
set NC_ROOT=%PROJECT%
set NO_PROXY=localhost,127.0.0.1
set PYTHONUTF8=1

echo [OK] PYTHONPATH=%FW%
echo [OK] NC_ROOT=%PROJECT%
echo [OK] Porta=%MCP_PORT%
echo.

echo Iniciando NeoCortex MCP HTTP Server...
echo Pressione Ctrl+C para parar.
echo ================================================================

python -m neocortex.mcp.server --transport sse --host 127.0.0.1 --port %MCP_PORT% 2>&1

pause
