# NC-SCR-FR-064-orchestration-agent-fixes.ps1
# Orquestração para execução dos 3 agentes (Engineer, Courier, Tester) na ordem correta.
# Uso: .\01_neocortex_framework\scripts\NC-SCR-FR-064-orchestration-agent-fixes.ps1 [-Sequential] [-LogDir <path>]
# Versão: 1.0 | 2026-04-14
# Autor: T0 (NeoCortex)

param(
    [switch]$Sequential,      # Executar sequencialmente (padrão) em vez de abrir janelas separadas
    [string]$LogDir = "",     # Diretório para logs (padrão: DIR-DOC-FR-001-docs-main)
    [switch]$DryRun           # Apenas validar pré-requisitos, não executar
)

# ROOT = 2 níveis acima do script
$ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$FRAMEWORK_DIR = Join-Path $ROOT "01_neocortex_framework"
$SCRIPTS_DIR = Join-Path $FRAMEWORK_DIR "scripts"
$DOCS_DIR = Join-Path $FRAMEWORK_DIR "DIR-DOC-FR-001-docs-main"

# Configurar diretório de logs
if ([string]::IsNullOrEmpty($LogDir)) {
    $LogDir = $DOCS_DIR
}

# Criar diretório de logs se não existir
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Timestamp para logs
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$LogFile = Join-Path $LogDir "orchestration_$Timestamp.log"

# Função para logging
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $logLine = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] $Message"
    Add-Content -Path $LogFile -Value $logLine
    if ($Level -eq "ERROR") {
        Write-Host $logLine -ForegroundColor Red
    } elseif ($Level -eq "WARNING") {
        Write-Host $logLine -ForegroundColor Yellow
    } else {
        Write-Host $logLine -ForegroundColor Green
    }
}

# Função para validação de pré-requisitos (STEP-0 simplificado)
function Test-Prerequisites {
    Write-Log "Validando pré-requisitos (STEP-0)..."
    
    $errors = @()
    
    # 1. Verificar Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            $errors += "Python não encontrado ou comando falhou"
        } else {
            Write-Log "Python OK: $pythonVersion"
        }
    } catch {
        $errors += "Erro ao verificar Python: $_"
    }
    
    # 2. Verificar scripts Python necessários
    $requiredScripts = @(
        "NC-SCR-FR-061-courier-discrepancy-fix.py",
        "NC-SCR-FR-062-engineer-encoding-fix.py", 
        "NC-SCR-FR-063-tester-vector-fix.py"
    )
    
    foreach ($script in $requiredScripts) {
        $scriptPath = Join-Path $SCRIPTS_DIR $script
        if (-not (Test-Path $scriptPath)) {
            $errors += "Script não encontrado: $script"
        } else {
            Write-Log "Script encontrado: $script"
        }
    }
    
    # 3. Verificar arquivos de entrada necessários
    $requiredInputs = @(
        "structural_audit_report.md",
        "renaming_plan.yaml"
    )
    
    foreach ($inputFile in $requiredInputs) {
        $inputPath = Join-Path $DOCS_DIR $inputFile
        if (-not (Test-Path $inputPath)) {
            $errors += "Arquivo de entrada não encontrado: $inputFile"
        } else {
            Write-Log "Arquivo de entrada encontrado: $inputFile"
        }
    }
    
    # 4. Verificar dependências Python básicas
    Write-Log "Verificando dependências Python..."
    $depsCheck = python -c "
import importlib, sys
deps = ['yaml', 'rich', 'logging', 're', 'json', 'pathlib']
missing = []
for d in deps:
    try:
        importlib.import_module(d)
        print(f'OK {d}')
    except ImportError:
        missing.append(d)
if missing:
    print(f'MISSING: {missing}')
    sys.exit(1)
" 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        $errors += "Dependências Python faltando: $depsCheck"
    } else {
        Write-Log "Dependências Python OK"
    }
    
    if ($errors.Count -gt 0) {
        Write-Log "Pré-requisitos falharam:" "ERROR"
        foreach ($err in $errors) {
            Write-Log "  - $err" "ERROR"
        }
        return $false
    }
    
    Write-Log "Todos os pré-requisitos validados com sucesso"
    return $true
}

# Função para executar script Python e capturar saída
function Invoke-PythonScript {
    param(
        [string]$ScriptName,
        [string]$Arguments = ""
    )
    
    $scriptPath = Join-Path $SCRIPTS_DIR $ScriptName
    $scriptLog = Join-Path $LogDir "$($ScriptName)_$Timestamp.log"
    
    Write-Log "Executando $ScriptName..."
    Write-Log "  Comando: python `"$scriptPath`" $Arguments"
    
    $startTime = Get-Date
    
    # Executar script Python
    $output = python $scriptPath 2>&1
    
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    # Salvar saída em arquivo de log
    $logContent = @"
=== EXECUÇÃO: $ScriptName ===
Início: $startTime
Fim: $endTime
Duração: $duration segundos

SAÍDA:
$output

=== FIM EXECUÇÃO ===

"@
    
    Add-Content -Path $scriptLog -Value $logContent
    
    # Analisar código de saída
    if ($LASTEXITCODE -eq 0) {
        Write-Log "$ScriptName concluído com sucesso (${duration}s)" "INFO"
        return @{
            Success = $true
            Output = $output
            LogFile = $scriptLog
            Duration = $duration
        }
    } else {
        Write-Log "$ScriptName falhou com código $LASTEXITCODE (${duration}s)" "ERROR"
        Write-Log "Saída: $output" "ERROR"
        return @{
            Success = $false
            Output = $output
            LogFile = $scriptLog
            Duration = $duration
            ExitCode = $LASTEXITCODE
        }
    }
}

# Função para gerar relatório final
function New-Report {
    param(
        [array]$Results
    )
    
    $reportFile = Join-Path $LogDir "orchestration_report_$Timestamp.md"
    
    $report = @"
# Relatório de Orquestração - Correções de Agentes
**Data:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Log principal:** $LogFile

## Resumo Executivo

| Agente | Script | Status | Duração (s) | Log |
|---|---|---|---|---|
"@
    
    $successCount = 0
    $failureCount = 0
    
    foreach ($result in $Results) {
        $status = if ($result.Success) { "✅ SUCESSO" } else { "❌ FALHA" }
        $duration = [math]::Round($result.Duration, 2)
        $logLink = Split-Path $result.LogFile -Leaf
        
        $report += "| $($result.Agent) | $($result.Script) | $status | $duration | [$logLink]($logLink) |`n"
        
        if ($result.Success) {
            $successCount++
        } else {
            $failureCount++
        }
    }
    
    $report += @"

## Estatísticas
- **Total de agentes:** $($Results.Count)
- **Sucessos:** $successCount
- **Falhas:** $failureCount
- **Taxa de sucesso:** $(if ($Results.Count -gt 0) { [math]::Round(($successCount / $Results.Count * 100), 1) } else { 0 })%

## Arquivos Gerados
"@
    
    # Listar arquivos gerados nos docs
    $generatedFiles = Get-ChildItem $DOCS_DIR -Filter "*discrepancy*" -File
    $generatedFiles += Get-ChildItem $DOCS_DIR -Filter "*renaming_plan_v2*" -File
    $generatedFiles += Get-ChildItem $DOCS_DIR -Filter "*dryrun*" -File
    $generatedFiles += Get-ChildItem $DOCS_DIR -Filter "*missing_dependencies*" -File
    $generatedFiles += Get-ChildItem $DOCS_DIR -Filter "*coverage_checklist*" -File
    
    if ($generatedFiles.Count -gt 0) {
        foreach ($file in $generatedFiles) {
            $relativePath = $file.FullName.Replace($ROOT, ".")
            $report += "- [$($file.Name)]($relativePath)`n"
        }
    } else {
        $report += "Nenhum arquivo novo detectado (pode ser que os arquivos já existiam).`n"
    }
    
    $report += @"

## Próximos Passos

1. **Revisar logs de execução** para cada agente
2. **Verificar arquivos gerados** listados acima
3. **Resolver conflitos** identificados no dry run (se houver)
4. **Executar testes** com `pytest tests/test_vector_engine.py -v --asyncio-mode=auto`
5. **Aprovar handoff** se todas as correções estiverem OK

## Notas

- Esta orquestração segue a ordem: Engineer → Courier → Tester
- Todos os logs estão disponíveis em: $LogDir
- Backup dos arquivos originais foi mantido pelos scripts individuais
- Em caso de falha, consulte o log específico do agente para detalhes

---

*Relatório gerado automaticamente por NC-SCR-FR-064-orchestration-agent-fixes.ps1*
"@
    
    Add-Content -Path $reportFile -Value $report
    Write-Log "Relatório gerado: $reportFile"
    
    return $reportFile
}

# --- MAIN EXECUTION ---
Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  NC-SCR-FR-064 - Orquestração de Correções de Agentes" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "ROOT: $ROOT" -ForegroundColor DarkGray
Write-Host "Log: $LogFile" -ForegroundColor DarkGray
Write-Host "Modo: $(if ($Sequential) { 'Sequencial' } else { 'Janelas separadas (não implementado)' })" -ForegroundColor DarkGray
Write-Host ""

# Iniciar logging
Write-Log "=== INÍCIO DA ORQUESTRAÇÃO ==="
Write-Log "Parâmetros: Sequential=$Sequential, LogDir='$LogDir', DryRun=$DryRun"

# Validação de pré-requisitos
if (-not (Test-Prerequisites)) {
    Write-Log "Orquestração abortada devido a falha nos pré-requisitos" "ERROR"
    exit 1
}

if ($DryRun) {
    Write-Log "DryRun ativado - apenas validação de pré-requisitos concluída" "INFO"
    exit 0
}

# Definir ordem de execução dos agentes
$agents = @(
    @{
        Name = "Engineer"
        Script = "NC-SCR-FR-062-engineer-encoding-fix.py"
        Arguments = ""
        Description = "Prepara ambiente (encoding UTF-8, dependências, dry run)"
    },
    @{
        Name = "Courier" 
        Script = "NC-SCR-FR-061-courier-discrepancy-fix.py"
        Arguments = ""
        Description = "Corrige discrepância de escopo e gera plano de renomeação completo"
    },
    @{
        Name = "Tester"
        Script = "NC-SCR-FR-063-tester-vector-fix.py"
        Arguments = ""
        Description = "Corrige incompatibilidade assíncrona e divergência de API nos testes"
    }
)

$results = @()

# Executar agentes na ordem definida
foreach ($agent in $agents) {
    Write-Log "`n--- INICIANDO AGENTE: $($agent.Name) ---"
    Write-Log "Descrição: $($agent.Description)"
    
    $result = Invoke-PythonScript -ScriptName $agent.Script -Arguments $agent.Arguments
    
    $resultObject = @{
        Agent = $agent.Name
        Script = $agent.Script
        Success = $result.Success
        Duration = $result.Duration
        LogFile = $result.LogFile
        ExitCode = if ($result.ExitCode) { $result.ExitCode } else { 0 }
    }
    
    $results += $resultObject
    
    # Se falhar, interromper a cadeia (dependências)
    if (-not $result.Success) {
        Write-Log "Agente $($agent.Name) falhou. Orquestração interrompida." "ERROR"
        break
    }
    
    Write-Log "--- AGENTE $($agent.Name) CONCLUÍDO ---`n"
}

# Gerar relatório final
$reportFile = New-Report -Results $results

# Resumo final
Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  ORQUESTRAÇÃO CONCLUÍDA" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

$successResults = $results | Where-Object { $_.Success }
$failedResults = $results | Where-Object { -not $_.Success }

Write-Host "Agentes executados: $($results.Count)" -ForegroundColor White
Write-Host "Sucessos: $($successResults.Count)" -ForegroundColor Green
Write-Host "Falhas: $($failedResults.Count)" -ForegroundColor $(if ($failedResults.Count -gt 0) { "Red" } else { "White" })

if ($failedResults.Count -eq 0) {
    Write-Host "`n✅ TODOS OS AGENTES CONCLUÍRAM COM SUCESSO!" -ForegroundColor Green
    Write-Host "Consulte o relatório em:" -ForegroundColor White
    Write-Host "  $reportFile" -ForegroundColor Yellow
} else {
    Write-Host "`n⚠️  ALGUNS AGENTES FALHARAM!" -ForegroundColor Yellow
    Write-Host "Verifique os logs para detalhes:" -ForegroundColor White
    foreach ($failed in $failedResults) {
        Write-Host "  - $($failed.Agent): $($failed.LogFile)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Log "=== FIM DA ORQUESTRAÇÃO ==="

# Código de saída: 0 se todos sucesso, 1 se alguma falha
if ($failedResults.Count -gt 0) {
    exit 1
} else {
    exit 0
}