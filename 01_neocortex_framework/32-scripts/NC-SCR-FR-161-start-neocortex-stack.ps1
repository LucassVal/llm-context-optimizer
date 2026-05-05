<#
.SYNOPSIS
  NC-SCR-FR-161 - Inicializa stack completa NeoCortex
  Sobe MCP Server (:8765) + DeepSeek Gateway (:4001) + LiteLLM (:4000)

.DESCRIPTION
  Script de produção que levanta todos os serviços do NeoCortex
  em janelas minimizadas. Pode ser chamado via atalho .bat na desktop
  ou via Mission Control.

.VERSION
  1.0 | 2026-04-26
#>

param(
  [switch]$NoMCP,
  [switch]$NoGateway,
  [switch]$NoLiteLLM,
  [switch]$Minimized = $true
)

$ROOT = "C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42"
$LOG_DIR = "$ROOT\01_neocortex_framework\.neocortex\logs"
$PYTHON = "python"

# Garantir diretório de logs
if (-not (Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null }

$windowStyle = if ($Minimized) { "Minimized" } else { "Normal" }

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  NeoCortex Stack Initialization" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# 1. MCP Server (:8765)
if (-not $NoMCP) {
  Write-Host "[1/3] Starting MCP Server (:8765)..." -ForegroundColor Yellow
  $mcpLog = "$LOG_DIR\mcp_server.log"
  Start-Process -WindowStyle $windowStyle -FilePath $PYTHON -ArgumentList @(
    "$ROOT\start_mcp_server.py"
  ) -RedirectStandardOutput $mcpLog -RedirectStandardError $mcpLog
  Write-Host "  → PID: (see taskmgr) | Log: $mcpLog" -ForegroundColor Gray
}

# 2. DeepSeek Gateway (:4001)
if (-not $NoGateway) {
  Write-Host "[2/3] Starting DeepSeek Gateway (:4001)..." -ForegroundColor Yellow
  $gwLog = "$LOG_DIR\deepseek_gateway.log"
  Start-Process -WindowStyle $windowStyle -FilePath $PYTHON -ArgumentList @(
    "$ROOT\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-102-deepseek-gateway.py"
  ) -RedirectStandardOutput $gwLog -RedirectStandardError $gwLog
  Write-Host "  → PID: (see taskmgr) | Log: $gwLog" -ForegroundColor Gray
}

# 3. LiteLLM Gateway (:4000)
if (-not $NoLiteLLM) {
  Write-Host "[3/3] Starting LiteLLM Gateway (:4000)..." -ForegroundColor Yellow
  $llmLog = "$LOG_DIR\litellm_gateway.log"
  Start-Process -WindowStyle $windowStyle -FilePath $PYTHON -ArgumentList @(
    "$ROOT\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\litellm_simple_gateway.py"
  ) -RedirectStandardOutput $llmLog -RedirectStandardError $llmLog
  Write-Host "  → PID: (see taskmgr) | Log: $llmLog" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✓ Stack inicializada. Aguarde 5-10s para serviços ficarem prontos." -ForegroundColor Green
Write-Host "  MCP Server:      http://localhost:8765" -ForegroundColor Cyan
Write-Host "  DeepSeek Gateway: http://localhost:4001" -ForegroundColor Cyan
Write-Host "  LiteLLM Gateway:  http://localhost:4000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para verificar: curl http://localhost:4001/health" -ForegroundColor Gray
