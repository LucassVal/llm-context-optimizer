# NC-SCR-FR-110 — LiteLLM Windows Startup Script
# Registra litellm como tarefa no Windows Task Scheduler
# Execute como Administrador: .\NC-SCR-FR-110-litellm-startup.ps1

param(
    [switch]$Register,    # Registrar tarefa no Task Scheduler
    [switch]$Unregister,  # Remover tarefa
    [switch]$Start,       # Iniciar manualmente
    [switch]$Status       # Ver status
)

$TaskName    = "NeoCortex-LiteLLM-Gateway"
$ProjectRoot = "C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42"
$ConfigFile  = "$ProjectRoot\config.yaml"
$Port        = 4000
$LogFile     = "$ProjectRoot\DIR-DS-002-audit-logs\litellm-startup.log"

function Test-Gateway {
    try {
        $r = Invoke-RestMethod -Uri "http://localhost:$Port/health" `
             -Headers @{ "Authorization" = "Bearer sk-my-master-key-123" } `
             -TimeoutSec 3
        return $true
    } catch { return $false }
}

# ── Registrar no Task Scheduler ───────────────────────────────────────────────
if ($Register) {
    Write-Host "Registrando $TaskName no Task Scheduler..." -ForegroundColor Cyan

    # Encontra o python do litellm
    $LiteLLMPath = (Get-Command litellm -ErrorAction SilentlyContinue).Source
    if (-not $LiteLLMPath) {
        # Tenta via pip show
        $PipShow = pip show litellm 2>$null | Select-String "Location"
        if ($PipShow) {
            $SitePackages = ($PipShow -split ": ")[1].Trim()
            $LiteLLMPath = "$SitePackages\..\Scripts\litellm.exe"
        }
    }
    if (-not $LiteLLMPath) {
        Write-Host "ERRO: litellm não encontrado no PATH. Execute: pip install litellm" -ForegroundColor Red
        exit 1
    }

    $Action = New-ScheduledTaskAction `
        -Execute $LiteLLMPath `
        -Argument "--config `"$ConfigFile`" --port $Port" `
        -WorkingDirectory $ProjectRoot

    $Trigger = New-ScheduledTaskTrigger -AtLogOn

    $Settings = New-ScheduledTaskSettingsSet `
        -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 1) `
        -StartWhenAvailable

    $Principal = New-ScheduledTaskPrincipal `
        -UserId $env:USERNAME `
        -LogonType Interactive `
        -RunLevel Limited

    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description "NeoCortex LiteLLM Gateway — unified LLM proxy on :$Port" `
        -Force | Out-Null

    Write-Host "✅ Tarefa '$TaskName' registrada! Inicia automaticamente no próximo logon." -ForegroundColor Green
    Write-Host "   Para iniciar agora: .\NC-SCR-FR-110-litellm-startup.ps1 -Start" -ForegroundColor Yellow
    exit 0
}

# ── Remover do Task Scheduler ─────────────────────────────────────────────────
if ($Unregister) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "✅ Tarefa '$TaskName' removida." -ForegroundColor Green
    exit 0
}

# ── Iniciar manualmente ───────────────────────────────────────────────────────
if ($Start) {
    if (Test-Gateway) {
        Write-Host "✅ LiteLLM já está online em http://localhost:$Port" -ForegroundColor Green
        # Garantir qwen-1.5b carregado mesmo se LiteLLM já estava rodando
        try {
            Invoke-RestMethod "http://localhost:11434/api/generate" -Method Post `
                -Body '{"model":"qwen2.5-coder:1.5b-instruct","prompt":"ping","stream":false,"keep_alive":-1}' `
                -ContentType "application/json" -TimeoutSec 10 | Out-Null
            Write-Host "🔥 qwen2.5-coder:1.5b-instruct aquecido na VRAM (keep_alive=-1)" -ForegroundColor Green
        } catch { Write-Host "⚠ Warmup qwen-1.5b falhou: $_" -ForegroundColor Yellow }
        exit 0
    }
    Write-Host "Iniciando LiteLLM em background..." -ForegroundColor Cyan
    $proc = Start-Process litellm `
        -ArgumentList "--config `"$ConfigFile`" --port $Port" `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden `
        -PassThru
    Start-Sleep -Seconds 3
    if (Test-Gateway) {
        Write-Host "✅ LiteLLM online! PID=$($proc.Id) | http://localhost:$Port" -ForegroundColor Green
        "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Started PID=$($proc.Id)" | Add-Content $LogFile
    } else {
        Write-Host "⚠ LiteLLM iniciado mas não respondeu em 3s. Verifique o log." -ForegroundColor Yellow
    }

    # === Pré-aquecer qwen2.5-coder:1.5b-instruct na VRAM da RTX 3050 ===
    # keep_alive=-1 mantém o modelo carregado indefinidamente (enquanto Ollama estiver ativo)
    Write-Host "🔥 Pré-aquecendo qwen2.5-coder:1.5b-instruct na RTX 3050..." -ForegroundColor Cyan
    try {
        $warmup = Invoke-RestMethod "http://localhost:11434/api/generate" -Method Post `
            -Body '{"model":"qwen2.5-coder:1.5b-instruct","prompt":"ready","stream":false,"keep_alive":-1}' `
            -ContentType "application/json" -TimeoutSec 30
        Write-Host "🟢 qwen-1.5b sempre na VRAM (keep_alive=-1). Resposta imediata garantida." -ForegroundColor Green
        "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] qwen-1.5b warmed up, keep_alive=-1" | Add-Content $LogFile
    } catch {
        Write-Host "⚠ Warmup qwen-1.5b falhou (Ollama pode estar subindo). Tente novamente em 10s." -ForegroundColor Yellow
    }
    exit 0
}

# ── Status ────────────────────────────────────────────────────────────────────
if ($Status -or (-not $Register -and -not $Unregister -and -not $Start)) {
    $online = Test-Gateway
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host "=== NeoCortex LiteLLM Gateway ===" -ForegroundColor Cyan
    Write-Host "  Endpoint   : http://localhost:$Port"
    Write-Host "  Status     : $(if ($online) { '✅ ONLINE' } else { '❌ OFFLINE' })"
    Write-Host "  Scheduler  : $(if ($task) { '✅ Registrado (' + $task.State + ')' } else { '⚠ Não registrado' })"
    Write-Host "  Config     : $ConfigFile"
    Write-Host ""
    Write-Host "Comandos:" -ForegroundColor Yellow
    Write-Host "  -Register    Registrar no Task Scheduler (run as Admin)"
    Write-Host "  -Start       Iniciar manualmente"
    Write-Host "  -Unregister  Remover do Task Scheduler"
    exit 0
}
