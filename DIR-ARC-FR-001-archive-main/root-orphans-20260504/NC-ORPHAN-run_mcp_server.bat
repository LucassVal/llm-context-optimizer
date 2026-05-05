@echo off
chcp 65001 >nul 2>&1
title NeoCortex MCP Server :8765

set "PROJECT=%~dp0"
set "FW=%PROJECT%01_neocortex_framework"
set "MCP_PORT=8765"

set PYTHONPATH=%FW%
set NEOCORTEX_PROJECT_ROOT=%FW%
set NC_ROOT=%PROJECT%
set NO_PROXY=localhost,127.0.0.1
set PYTHONUTF8=1

cd /d "%PROJECT%"

echo ================================================================
echo   NeoCortex MCP Server
echo   http://127.0.0.1:%MCP_PORT%/mcp
echo   Nao feche esta janela.
echo ================================================================
echo.

python -m neocortex.mcp.server --transport sse --host 127.0.0.1 --port %MCP_PORT%
pause
