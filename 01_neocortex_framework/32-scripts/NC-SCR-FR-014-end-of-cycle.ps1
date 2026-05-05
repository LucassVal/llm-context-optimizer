# NC-SCR-FR-014-end-of-cycle.ps1
# Fim de Ciclo - Valida handoffs, lista R20, gera bloco STATUS
# Uso: .\01_neocortex_framework\scripts\NC-SCR-FR-014-end-of-cycle.ps1 [-AutoUpdate] [-ShowAll] [-UpdateCatalog] [-GenerateResume]
# Versao: 1.4 | 2026-04-14 - Formato de reaquecimento otimizado com instruções por ciclo

param(
    [switch]$AutoUpdate,
    [switch]$ShowAll,
    [switch]$UpdateCatalog,
    [switch]$GenerateResume
)

# ROOT = 2 niveis acima do script (scripts/ -> neocortex_fw/ -> TURBOQUANT_V42/)
$ROOT      = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$AUDIT_DIR = Join-Path $ROOT 'DIR-DS-002-audit-logs'
$TODAY     = Get-Date -Format 'yyyy-MM-dd'

Write-Host ''
Write-Host '======================================================' -ForegroundColor Cyan
Write-Host '  NC-SCR-FR-014 - FIM DE CICLO (R20)'                  -ForegroundColor Cyan
Write-Host '======================================================'  -ForegroundColor Cyan
Write-Host ('ROOT: ' + $ROOT) -ForegroundColor DarkGray
Write-Host ''

# ──────────────────────────────────────────────
# 1. HANDOFFS
# ──────────────────────────────────────────────
Write-Host '--- 1. HANDOFFS ---' -ForegroundColor Yellow

$yamls    = Get-ChildItem $AUDIT_DIR -Filter '*.yaml' -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending
$pending  = @()
$approved = @()
$rejected = @()

foreach ($y in $yamls) {
    $txt        = Get-Content $y.FullName -Raw -ErrorAction SilentlyContinue
    $ticketLine = ($txt | Select-String 'ticket_id:').Line
    $statusLine = ($txt | Select-String '^status:').Line
    $ticket = if ($ticketLine) { ($ticketLine -replace 'ticket_id:\s*','').Trim() } else { $y.BaseName }
    $status = if ($statusLine) { ($statusLine -replace 'status:\s*','').Trim()  }  else { 'UNKNOWN' }
    $obj = [pscustomobject]@{Ticket=$ticket; File=$y.Name; Time=$y.LastWriteTime.ToString('HH:mm')}
    switch ($status) {
        'PENDING_REVIEW' { $pending  += $obj }
        'APPROVED'       { $approved += $obj }
        'REJECTED'       { $rejected += $obj }
    }
}

if ($pending.Count -gt 0) {
    Write-Host ('PENDENTES (' + $pending.Count + '):') -ForegroundColor Yellow
    $pending | ForEach-Object { Write-Host ('  ' + $_.Time + '  ' + $_.Ticket + '  [' + $_.File + ']') }
} else {
    Write-Host 'Nenhum handoff pendente.' -ForegroundColor Green
}

if ($rejected.Count -gt 0) {
    Write-Host ('REJEITADOS (' + $rejected.Count + '):') -ForegroundColor Red
    $rejected | ForEach-Object { Write-Host ('  ' + $_.Time + '  ' + $_.Ticket) }
}

if ($ShowAll -and $approved.Count -gt 0) {
    Write-Host ('APROVADOS (' + $approved.Count + '):') -ForegroundColor Green
    $approved | Select-Object -First 10 | ForEach-Object { Write-Host ('  ' + $_.Time + '  ' + $_.Ticket) }
}

# ──────────────────────────────────────────────
# 2. ARQUIVOS ENTREGUES HOJE
# ──────────────────────────────────────────────
Write-Host ''
Write-Host ('--- 2. ARQUIVOS ENTREGUES HOJE (' + $TODAY + ') ---') -ForegroundColor Yellow

$zonas = @(
    '01_neocortex_framework\neocortex\core\services',
    '01_neocortex_framework\neocortex\core\hooks',
    '01_neocortex_framework\neocortex\core\config',
    '01_neocortex_framework\neocortex\core\review',
    '01_neocortex_framework\neocortex\core\workers',
    '01_neocortex_framework\neocortex\mcp\tools',
    '01_neocortex_framework\scripts'
)

$entregadosHoje = @()
foreach ($zona in $zonas) {
    $path = Join-Path $ROOT $zona
    if (Test-Path $path) {
        Get-ChildItem $path -Filter 'NC-*.py' |
            Where-Object { $_.LastWriteTime.Date -eq (Get-Date).Date } |
            ForEach-Object {
                $entregadosHoje += $_
                Write-Host ('  ' + $_.LastWriteTime.ToString('HH:mm') + '  ' + $_.Name + '  [' + $_.Length + 'b]')
            }
    }
}

if ($entregadosHoje.Count -eq 0) {
    Write-Host '  (nenhum arquivo .py novo hoje)' -ForegroundColor Gray
}

# ──────────────────────────────────────────────
# 3. CHECKLIST R20
# ──────────────────────────────────────────────
Write-Host ''
Write-Host '--- 3. CHECKLIST R20 ---' -ForegroundColor Yellow

$c1 = '[ ] @SSOT NC-NAM-FR-001 + changelog [' + $TODAY + ']'
$c2 = '[ ] %DONE no roadmap NC-TODO-DS-001 para tickets concluidos'
$c3 = '[ ] @POPULATE: python 01_neocortex_framework/scripts/NC-SCR-FR-001-populate-lobes-ssot.py'
$c4 = '[ ] @BOOT NC-BOOT-FR-001 atualizado'
$c5 = '[ ] NC-PROMPT-FR-001 STATUS atualizado (cole bloco abaixo)'
$c6 = '[ ] NC-LBE-FR-QUALITY-001 regression buffer atualizado'
$c7 = '[ ] Sem *.db / *.wal / __pycache__ para commitar'
$c8 = '[ ] Checkpoint criado'

@($c1,$c2,$c3,$c4,$c5,$c6,$c7,$c8) | ForEach-Object { Write-Host ('  ' + $_) }

# ──────────────────────────────────────────────
# 4. TICKETS PARA DONE
# ──────────────────────────────────────────────
Write-Host ''
Write-Host '--- 4. TICKETS PARA %DONE ---' -ForegroundColor Yellow

$ticketsDone = $approved |
    Where-Object { $_.Ticket -match 'NC-DS-' } |
    Select-Object -ExpandProperty Ticket -Unique

if ($ticketsDone.Count -gt 0) {
    $ticketsDone | ForEach-Object { Write-Host ('  %DONE -> ' + $_) -ForegroundColor Green }
} else {
    Write-Host '  Nenhum aprovado com ticket (verifique manualmente).' -ForegroundColor Gray
}

# ──────────────────────────────────────────────
# 5. CATÁLOGO DE ARTEFATOS
# ──────────────────────────────────────────────
Write-Host ''
Write-Host '--- 5. CATÁLOGO DE ARTEFATOS ---' -ForegroundColor Yellow

$CATALOG_JSON = Join-Path $ROOT 'DIR-DOC-FR-001-docs-main\artifact_catalog.json'
$CATALOG_MD = Join-Path $ROOT 'DIR-DOC-FR-001-docs-main\artifact_catalog.md'
$CATALOG_SCRIPT = Join-Path $ROOT '01_neocortex_framework\scripts\NC-SCR-FR-064-artifact-catalog.py'

$catalogExists = Test-Path $CATALOG_JSON -ErrorAction SilentlyContinue
$catalogAge = if ($catalogExists) { (Get-Date) - (Get-Item $CATALOG_JSON).LastWriteTime } else { $null }

if ($catalogExists) {
    if ($catalogAge.TotalHours -gt 24) {
        Write-Host '  Catálogo desatualizado (>24h).' -ForegroundColor Yellow
        $shouldUpdate = $true
    } else {
        Write-Host ('  Catálogo atualizado há ' + [math]::Round($catalogAge.TotalHours, 1) + 'h.') -ForegroundColor Green
        $shouldUpdate = $false
    }
} else {
    Write-Host '  Catálogo não encontrado.' -ForegroundColor Yellow
    $shouldUpdate = $true
}

# Atualizar catálogo se solicitado ou se necessário
if ($UpdateCatalog -or $shouldUpdate) {
    Write-Host '  [ATUALIZANDO] Executando NC-SCR-FR-064-artifact-catalog.py...' -ForegroundColor Cyan
    try {
        $pythonOutput = python $CATALOG_SCRIPT 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host '  [OK] Catálogo atualizado com sucesso.' -ForegroundColor Green
        } else {
            Write-Host ('  [ERRO] Falha ao atualizar catálogo: ' + $pythonOutput) -ForegroundColor Red
        }
    } catch {
        Write-Host ('  [ERRO] Exceção ao executar script: ' + $_.Exception.Message) -ForegroundColor Red
    }
}

# Ler estatísticas do catálogo se existir
if (Test-Path $CATALOG_JSON -ErrorAction SilentlyContinue) {
    try {
        $catalogData = Get-Content $CATALOG_JSON -Raw -ErrorAction Stop | ConvertFrom-Json
        $totalPy = $catalogData.metadata.total_py
        $totalYaml = $catalogData.metadata.total_yaml
        $generated = $catalogData.metadata.generated
        
        Write-Host ('  Estatísticas: ' + $totalPy + ' PY, ' + $totalYaml + ' YAML') -ForegroundColor Gray
        Write-Host ('  Gerado em: ' + $generated) -ForegroundColor Gray
    } catch {
        Write-Host '  [AVISO] Não foi possível ler estatísticas do catálogo.' -ForegroundColor Yellow
    }
}

# ──────────────────────────────────────────────
# 6. BOOTUP SYNC (Sincronização do Boot Manifest)
# ──────────────────────────────────────────────
Write-Host ''
Write-Host '--- 6. BOOTUP SYNC ---' -ForegroundColor Yellow

$BOOTUP_SCRIPT = Join-Path $ROOT '01_neocortex_framework\scripts\NC-SCR-FR-066-bootup-sync.py'
if (Test-Path $BOOTUP_SCRIPT -ErrorAction SilentlyContinue) {
    Write-Host '  [SINCRONIZANDO] Executando NC-SCR-FR-066-bootup-sync.py...' -ForegroundColor Cyan
    try {
        $bootupOutput = python $BOOTUP_SCRIPT 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host '  [OK] Boot manifest sincronizado com sucesso.' -ForegroundColor Green
        } else {
            Write-Host ('  [ERRO] Falha ao sincronizar boot manifest: ' + $bootupOutput) -ForegroundColor Red
        }
    } catch {
        Write-Host ('  [ERRO] Exceção ao executar script: ' + $_.Exception.Message) -ForegroundColor Red
    }
} else {
    Write-Host '  [AVISO] Script de sincronização bootup não encontrado.' -ForegroundColor Yellow
}

# ──────────────────────────────────────────────
# 7. BLOCO STATUS (AutoUpdate)
# ──────────────────────────────────────────────
if ($AutoUpdate) {
    Write-Host ''
    Write-Host '--- 6. BLOCO STATUS (cole no NC-PROMPT-FR-001) ---' -ForegroundColor Cyan

    $tSVC  = (Get-ChildItem (Join-Path $ROOT '01_neocortex_framework\neocortex\core\services') -Filter 'NC-SVC-*.py'  -ErrorAction SilentlyContinue).Count
    $tHK   = (Get-ChildItem (Join-Path $ROOT '01_neocortex_framework\neocortex\core\hooks')    -Filter 'NC-HK-*.py'   -ErrorAction SilentlyContinue).Count
    $tTOOL = (Get-ChildItem (Join-Path $ROOT '01_neocortex_framework\neocortex\mcp\tools')     -Filter 'NC-TOOL-*.py' -ErrorAction SilentlyContinue).Count
    $tUTL  = (Get-ChildItem (Join-Path $ROOT '01_neocortex_framework\neocortex\core\utils')    -Filter 'NC-UTL-*.py'  -ErrorAction SilentlyContinue).Count
    $now   = Get-Date -Format 'yyyy-MM-dd HH:mm'
    
    # Estatísticas do catálogo
    $catalogStats = ''
    $CATALOG_JSON = Join-Path $ROOT 'DIR-DOC-FR-001-docs-main\artifact_catalog.json'
    if (Test-Path $CATALOG_JSON -ErrorAction SilentlyContinue) {
        try {
            $catalogData = Get-Content $CATALOG_JSON -Raw -ErrorAction Stop | ConvertFrom-Json
            $totalPy = $catalogData.metadata.total_py
            $totalYaml = $catalogData.metadata.total_yaml
            $catalogStats = ' | CAT=' + $totalPy + 'PY/' + $totalYaml + 'YAML'
        } catch {
            $catalogStats = ' | CAT=ERRO'
        }
    } else {
        $catalogStats = ' | CAT=N/A'
    }

    Write-Host '--- COPIE ---'
    Write-Host ('Atualizado: ' + $now + ' | MCP: OFFLINE' + $catalogStats)
    Write-Host ('SVC=' + $tSVC + ' | TOOL=' + $tTOOL + ' | UTL=' + $tUTL + ' | HK=' + $tHK)
    Write-Host ('Pendentes: ' + $pending.Count + ' | Entregues hoje: ' + $entregadosHoje.Count)
    Write-Host '-------------'
}

# ──────────────────────────────────────────────
# 8. CONTEXTO DE RETOMADA (GenerateResume)
# ──────────────────────────────────────────────
if ($GenerateResume) {
    Write-Host ''
    Write-Host '--- 8. CONTEXTO DE RETOMADA (cole no início da próxima sessão) ---' -ForegroundColor Magenta
    
    # Coletar dados
    $now = Get-Date -Format 'yyyy-MM-dd HH:mm'
    $pendingCount = $pending.Count
    $todayFiles = $entregadosHoje.Count
    $ticketsDoneCount = $ticketsDone.Count
    
    # Estatísticas do catálogo
    $totalPy = 0
    $totalYaml = 0
    $catalogAgeHours = 0
    $CATALOG_JSON = Join-Path $ROOT 'DIR-DOC-FR-001-docs-main\artifact_catalog.json'
    if (Test-Path $CATALOG_JSON -ErrorAction SilentlyContinue) {
        try {
            $catalogData = Get-Content $CATALOG_JSON -Raw -ErrorAction Stop | ConvertFrom-Json
            $totalPy = $catalogData.metadata.total_py
            $totalYaml = $catalogData.metadata.total_yaml
            $catalogAge = (Get-Date) - (Get-Item $CATALOG_JSON).LastWriteTime
            $catalogAgeHours = [math]::Round($catalogAge.TotalHours, 1)
        } catch {
            $totalPy = 'ERRO'
            $totalYaml = 'ERRO'
        }
    }
    
    # Lista de handoffs pendentes (nomes de arquivo)
    $pendingList = @()
    foreach ($p in $pending) {
        $pendingList += $p.Ticket
    }
    $pendingListStr = if ($pendingList.Count -gt 0) { $pendingList -join ', ' } else { 'Nenhum' }
    
    Write-Host '--- COPIE ABAIXO ---'
    Write-Host '```markdown'
    Write-Host '[NC-PROMPT] [CICLO:1] [REAQUECIMENTO]'
    Write-Host 'Você está entrando em uma sessão de trabalho no projeto NeoCortex Framework. O contexto abaixo foi gerado automaticamente pelo script NC-SCR-FR-014-end-of-cycle.ps1 e contém as informações mínimas necessárias para continuidade.'
    Write-Host ''
    Write-Host "### CONTEXTO DE RETOMADA (Gerado em $(Get-Date -Format 'yyyy-MM-dd'))"
    Write-Host "**Status:** $pendingCount handoffs pendentes | $totalPy PY + $totalYaml YAML catalogados | Catálogo atualizado há ${catalogAgeHours}h"
    Write-Host '**Problemas Críticos Ativos:**'
    Write-Host '- Plano de renomeação (87 arquivos) aguardando validação de escopo/atualidade'
    Write-Host '- Testes VectorEngine com falhas (mock/API) – documentado em NC-DS-XXX'
    Write-Host '- Discrepância de escopo: plano atual (87) vs. auditoria (178)'
    Write-Host ''
    Write-Host '**Artefatos-Chave:**'
    Write-Host '| Arquivo | Função |'
    Write-Host '|---------|--------|'
    Write-Host '| `renaming_plan.yaml` | Plano atual com 87 arquivos |'
    Write-Host '| `artifact_catalog.json` | Mapa de dependências de todos scripts |'
    Write-Host '| `rename_impact_analysis.json` | Impacto previsto das renomeações |'
    Write-Host "| `DIR-DS-002-audit-logs/` | Handoffs pendentes: $pendingListStr |"
    Write-Host ''
    Write-Host '**Última Ação Concluída:** [Preencher com última ação realizada]'
    Write-Host ''
    Write-Host '### 🧭 INSTRUÇÕES PARA ESTA SESSÃO:'
    Write-Host 'O usuário informará qual **foco de trabalho** deseja para hoje. Com base nisso, você deverá:'
    Write-Host '1. **Ciclo 1 (Análise):** Consultar os artefatos-chave listados acima e fornecer um resumo executivo do estado atual.'
    Write-Host '2. **Ciclo 2 (Ação):** Propor e executar (se autorizado) os próximos passos lógicos, sempre documentando as ações em formato de handoff YAML ao final.'
    Write-Host '3. **Ciclo 3 (Fechamento):** Ao final da sessão, sugerir executar `NC-SCR-FR-014-end-of-cycle.ps1 -AutoUpdate` para gerar novo bloco de retomada.'
    Write-Host ''
    Write-Host '**Observação:** Mantenha respostas concisas e acionáveis, evitando explicações redundantes sobre o framework.'
    Write-Host ''
    Write-Host '[FIM DO BLOCO DE REAQUECIMENTO]'
    Write-Host '```'
    Write-Host '--- FIM DO BLOCO ---'
    Write-Host ''
}

# ──────────────────────────────────────────────
# RESUMO
# ──────────────────────────────────────────────
Write-Host ''
Write-Host '--- RESUMO ---' -ForegroundColor Cyan
$cPend = if ($pending.Count      -gt 0) { 'Yellow' } else { 'Green' }
$cDone = if ($ticketsDone.Count  -gt 0) { 'Yellow' } else { 'Green' }
Write-Host ('  Handoffs pendentes : ' + $pending.Count)      -ForegroundColor $cPend
Write-Host ('  Arquivos hoje      : ' + $entregadosHoje.Count)
Write-Host ('  Tickets p/ %DONE  : ' + $ticketsDone.Count)   -ForegroundColor $cDone

# Status do catálogo
$catalogStatus = 'N/A'
$CATALOG_JSON = Join-Path $ROOT 'DIR-DOC-FR-001-docs-main\artifact_catalog.json'
if (Test-Path $CATALOG_JSON -ErrorAction SilentlyContinue) {
    $catalogAge = (Get-Date) - (Get-Item $CATALOG_JSON).LastWriteTime
    if ($catalogAge.TotalHours -lt 24) {
        $catalogStatus = 'OK (' + [math]::Round($catalogAge.TotalHours, 1) + 'h)'
        $catalogColor = 'Green'
    } else {
        $catalogStatus = 'DESAT (' + [math]::Round($catalogAge.TotalHours, 1) + 'h)'
        $catalogColor = 'Yellow'
    }
} else {
    $catalogStatus = 'NÃO ENCONTRADO'
    $catalogColor = 'Red'
}
Write-Host ('  Catálogo artefatos : ' + $catalogStatus) -ForegroundColor $catalogColor
Write-Host ''
