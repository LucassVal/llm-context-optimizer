# NeoCortex MCP Server Startup Script
# Uso: .\start_neocortex_mcp.ps1
# Boot: NC-BOOT-FR-001 secao 3

$pythonCmd = "C:\Program Files\Python312\python.exe"
if (-not (Test-Path $pythonCmd)) { $pythonCmd = "python" }

$projectRoot = $PSScriptRoot
$env:PYTHONPATH = Join-Path $projectRoot "01_neocortex_framework"
Set-Location $projectRoot

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  NeoCortex MCP Server" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:8765/mcp" -ForegroundColor Gray
Write-Host "  CTRL+C para parar" -ForegroundColor Gray
Write-Host "=================================================" -ForegroundColor Cyan

& $pythonCmd -m neocortex.mcp.server --transport sse --host 127.0.0.1 --port 8765
