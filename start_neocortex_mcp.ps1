# NeoCortex MCP Server Startup Script (PowerShell)
# Conecta Assistentes via WebSocket

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   NeoCortex MCP Server (Host Mode)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$pythonCmd = "C:\Program Files\Python312\python.exe"

try {
    & $pythonCmd --version 2>&1 | Out-Null
} catch {
    Write-Host "[AVISO] Python explicito nao encontrado. Tentando 'python'" -ForegroundColor Yellow
    $pythonCmd = "python"
    try {
        & $pythonCmd --version 2>&1 | Out-Null
    } catch {
        Write-Host "[ERRO] Python não encontrado no PATH" -ForegroundColor Red
        Read-Host "Pressione Enter para sair"
        exit 1
    }
}

$projectRoot = Join-Path $PSScriptRoot "01_neocortex_framework"
Set-Location $projectRoot

Write-Host "[INFO] Iniciando NeoCortex MCP Server..." -ForegroundColor Yellow
Write-Host "[INFO] Host: 127.0.0.1:8765" -ForegroundColor Gray
Write-Host "[INFO] T-0 Brain Assistente ativo (DeepSeek)" -ForegroundColor Gray
Write-Host ""

try {
    & $pythonCmd -m neocortex.mcp.server --transport websocket --host 127.0.0.1 --port 8765
} catch {
    Write-Host "[ERRO] Servidor WebSocket falhou: $_" -ForegroundColor Red
}