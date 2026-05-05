# NC-SCR-FR-103-start-with-mc.ps1
# Wrapper para iniciar NeoCortex MCP Server e o hook de startup do Mission Control.
# NÃO modifica start_neocortex_mcp.ps1 (arquivo @LOCKS).
# Uso: .\NC-SCR-FR-103-start-with-mc.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   NeoCortex MCP Server + Mission Control" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Detecta Python (igual ao script original)
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

$projectRoot = Join-Path $PSScriptRoot ".."
Set-Location $projectRoot

Write-Host "[INFO] Iniciando NeoCortex MCP Server (background)..." -ForegroundColor Yellow
Write-Host "[INFO] Host: 127.0.0.1:8765" -ForegroundColor Gray
Write-Host ""

# 1. Inicia o servidor MCP em background com redirecionamento de logs
$serverLogOut = "mcp_server_out.log"
$serverLogErr = "mcp_server_err.log"
Write-Host "[INFO] Logs do servidor: stdout -> $serverLogOut, stderr -> $serverLogErr" -ForegroundColor Gray

$serverProcess = Start-Process -FilePath $pythonCmd `
    -ArgumentList "-m", "neocortex.mcp.server", "--transport", "websocket", "--host", "127.0.0.1", "--port", "8765" `
    -WorkingDirectory $projectRoot `
    -RedirectStandardOutput $serverLogOut `
    -RedirectStandardError $serverLogErr `
    -PassThru `
    -NoNewWindow

Write-Host "[INFO] Servidor MCP iniciado (PID: $($serverProcess.Id))" -ForegroundColor Gray

# 2. Aguarda alguns segundos para o servidor iniciar
Write-Host "[INFO] Aguardando inicializacao do servidor (5s)..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# 3. Inicia o hook de startup do Mission Control em outro job
Write-Host "[INFO] Iniciando Mission Control startup hook (background)..." -ForegroundColor Yellow
$hookJob = Start-Job -Name "MCHook" -ScriptBlock {
    $pythonCmd = $args[0]
    $projectRoot = $args[1]
    Set-Location $projectRoot
    & $pythonCmd "scripts/NC-SCR-FR-103-mc-startup-hook.py"
} -ArgumentList $pythonCmd, $projectRoot

Write-Host "[INFO] Hook iniciado como job (ID: $($hookJob.Id))" -ForegroundColor Gray
Write-Host ""
Write-Host "[INFO] Ambos processos rodando em background." -ForegroundColor Green
Write-Host "[INFO] Para monitorar servidor, veja logs: $serverLogOut, $serverLogErr" -ForegroundColor Gray
Write-Host "[INFO] Para monitorar jobs, use: Get-Job" -ForegroundColor Gray
Write-Host "[INFO] Para parar, use: Stop-Process -Id $($serverProcess.Id); Stop-Job -Id $($hookJob.Id); Remove-Job -Id $($hookJob.Id)" -ForegroundColor Gray
Write-Host ""

# 4. Monitora o servidor (processo principal) e, se ele terminar, para o hook também
try {
    $serverFinished = $false
    while (-not $serverFinished) {
        if ($serverProcess.HasExited) {
            Write-Host "[INFO] Servidor MCP terminou (código: $($serverProcess.ExitCode)). Parando hook..." -ForegroundColor Yellow
            Stop-Job -Id $hookJob.Id -ErrorAction SilentlyContinue
            Remove-Job -Id $hookJob.Id -ErrorAction SilentlyContinue
            $serverFinished = $true
        } else {
            # Verifica também se o hook job terminou (pode ser normal)
            $hookState = (Get-Job -Id $hookJob.Id -ErrorAction SilentlyContinue).State
            if ($hookState -eq "Completed" -or $hookState -eq "Failed") {
                Write-Host "[INFO] Hook terminou (estado: $hookState). Continuando monitoramento do servidor." -ForegroundColor Gray
            }
        }
        Start-Sleep -Seconds 2
    }
} finally {
    # Limpeza
    if (-not $serverProcess.HasExited) {
        Write-Host "[INFO] Parando servidor MCP..." -ForegroundColor Yellow
        Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Get-Job | Where-Object { $_.Name -match "MCHook" } | Remove-Job -Force -ErrorAction SilentlyContinue
    Write-Host "[INFO] Limpeza concluída. Fim." -ForegroundColor Gray
}