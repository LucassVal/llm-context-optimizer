<#
.SYNOPSIS
  NC-SCR-FR-161 - Stack Watchdog Unificado
  Monitora MCP (:8765) + Gateway (:4001) + LiteLLM (:4000) + PicoClaw (:18790)
  Reinicia serviços que caírem. Projeta exit code para o Task Scheduler.

.DESCRIPTION
  Watchdog principal do NeoCortex. Roda a cada 5 min via Task Scheduler.
  Verifica cada serviço com health check HTTP e reinicia via Start-Process
  se detectar falha. Log estruturado em .neocortex/logs/stack-watchdog.log.

  Exit codes:
    0 = tudo ok (ou recuperado com sucesso)
    1 = falha em um ou mais serviços (não recuperou)

.VERSION
  1.0 | 2026-04-26
#>

param(
  [int]$IntervalSeconds = 300,
  [switch]$Loop
)

$ROOT = "C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42"
$LOG_DIR_PRIMARY = "$ROOT\01_neocortex_framework\.neocortex\logs"
$LOG_DIR_FALLBACK = "$env:TEMP\NeoCortex-Watchdog"
$LOG_FILE = "$LOG_DIR_FALLBACK\stack-watchdog.log"
$PYTHON = "python"
$MAX_LOG_KB = 1024

# Garantir diretório de logs (fallback pro TEMP se .neocortex/logs não for acessível)
$LOG_DIR = $LOG_DIR_PRIMARY
try {
  if (-not (Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Path $LOG_DIR -Force -ErrorAction Stop | Out-Null }
} catch {
  $LOG_DIR = $LOG_DIR_FALLBACK
  if (-not (Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null }
  $LOG_FILE = "$LOG_DIR\stack-watchdog.log"
}

# Rotação de log
function Rotate-Log {
  if (Test-Path $LOG_FILE) {
    $sz = (Get-Item $LOG_FILE).Length / 1KB
    if ($sz -gt $MAX_LOG_KB) {
      Copy-Item $LOG_FILE "$LOG_FILE.bak" -Force
      Remove-Item $LOG_FILE -Force
      Log "[ROTATE] Log rotated (was $([math]::Round($sz))KB)"
    }
  }
}

function Log {
  param([string]$Message)
  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  "$ts $Message" | Out-File -FilePath $LOG_FILE -Append -Encoding UTF8
}

function Test-Service {
  param(
    [string]$Name,
    [int]$Port,
    [string]$Endpoint = "/health",
    [int]$TimeoutSec = 5
  )
  $url = "http://127.0.0.1:$Port$Endpoint"
  try {
    $r = Invoke-WebRequest -Uri $url -TimeoutSec $TimeoutSec -UseBasicParsing -ErrorAction Stop
    if ($r.StatusCode -eq 200) {
      return $true
    }
    return $false
  } catch {
    return $false
  }
}

function Start-Service {
  param(
    [string]$Name,
    [string]$ScriptPath,
    [string]$Arguments = "",
    [string]$Desc
  )
  Log "[$Name] Attempting restart: $Desc..."

  # Matar processos residuais na porta (se aplicável)
  if ($Arguments -match "--port (\d+)") {
    $port = $Matches[1]
    $pids = netstat -ano | Select-String ":$port\s" | ForEach-Object {
      $_ -replace '.*\s+(\d+)$', '$1'
    } | Where-Object { $_ -ne '0' } | Select-Object -Unique
    foreach ($pid in $pids) {
      try { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } catch {}
    }
    Start-Sleep -Seconds 1
  }

  # Iniciar o serviço
  $logOutput = "$LOG_DIR\$(Split-Path $ScriptPath -Leaf).log"
  try {
    Start-Process -WindowStyle Minimized -FilePath $PYTHON -ArgumentList $Arguments -RedirectStandardOutput $logOutput -RedirectStandardError $logOutput
    Log "[$Name] Started (PID: see taskmgr)"
    return $true
  } catch {
    Log "[$Name] FAILED to start: $_"
    return $false
  }
}

# ─── Serviços monitorados ───
$services = @(
  @{
    Name = "MCP-Server"
    Port = 8765
    Endpoint = "/sse"  # MCP usa SSE, não /health
    Script = "$ROOT\start_mcp_server.py"
    Args = @("$ROOT\start_mcp_server.py")
    Desc = "FastMCP SSE server on :8765"
  }
  @{
    Name = "DeepSeek-Gateway"
    Port = 4001
    Endpoint = "/health"
    Script = "$ROOT\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-102-deepseek-gateway.py"
    Args = @("$ROOT\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-102-deepseek-gateway.py")
    Desc = "DeepSeek Reasoner proxy on :4001"
  }
  @{
    Name = "LiteLLM-Gateway"
    Port = 4000
    Endpoint = "/health"
    Script = "$ROOT\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\litellm_simple_gateway.py"
    Args = @("$ROOT\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\litellm_simple_gateway.py")
    Desc = "LiteLLM Ollama proxy on :4000"
  }
  @{
    Name = "PicoClaw"
    Port = 18790
    Endpoint = "/health"
    Script = ""  # picoclaw exe, não python
    Args = @()
    Desc = "PicoClaw agent gateway on :18790"
  }
)

# ─── Main loop ───
$globalExitCode = 0

do {
  Rotate-Log
  Log "=== Stack Watchdog run ==="

  foreach ($svc in $services) {
    $name = $svc.Name
    $alive = Test-Service -Name $name -Port $svc.Port -Endpoint $svc.Endpoint -TimeoutSec 4

    if ($alive) {
      Log "[$name] OK"
    } else {
      Log "[$name] OFFLINE"

      # Tenta restart (PicoClaw é exceção — não temos o binário)
      if ($name -eq "PicoClaw") {
        Log "[$name] No binary to restart. Manual intervention required."
        $globalExitCode = 1
      } elseif ($svc.Script -and (Test-Path $svc.Script)) {
        $ok = Start-Service -Name $name -ScriptPath $svc.Script -Arguments $svc.Args -Desc $svc.Desc
        if (-not $ok) { $globalExitCode = 1 }

        # Aguarda e revalida
        Start-Sleep -Seconds 3
        $recovered = Test-Service -Name $name -Port $svc.Port -Endpoint $svc.Endpoint -TimeoutSec 4
        if ($recovered) {
          Log "[$name] Recovered after restart"
        } else {
          Log "[$name] Still down after restart attempt"
          $globalExitCode = 1
        }
      } else {
        Log "[$name] Script not found: $($svc.Script)"
        $globalExitCode = 1
      }
    }
  }

  Log "=== Watchdog complete (exit: $globalExitCode) ==="

  if ($Loop) {
    Log "[SLEEP] ${IntervalSeconds}s until next check..."
    Start-Sleep -Seconds $IntervalSeconds
  }

} while ($Loop)

exit $globalExitCode
