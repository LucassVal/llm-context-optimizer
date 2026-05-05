#!/usr/bin/env pwsh
# NC-DS-260 — R129 ITIL: Pre-commit hook — savepoint check
# Bloqueia commit se nenhum savepoint recente (<24h) existe em .neocortex/savepoints/
# Auto-cria savepoint se diretorio vazio. NAO bloqueia — warns.
# Instalado via: copy to .git/hooks/pre-commit

$ErrorActionPreference = "SilentlyContinue"
$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) { exit 0 }

$savepointDir = Join-Path $repoRoot ".neocortex\savepoints"
$recent = $false
$ts = Get-Date -Format "yyyy-MM-ddTHHmmss"
$savepointFile = Join-Path $savepointDir "ITIL-$ts.savepoint.json"

if (Test-Path $savepointDir) {
    $cutoff = (Get-Date).AddHours(-24)
    $files = Get-ChildItem $savepointDir -Filter "*.savepoint.json" -ErrorAction SilentlyContinue
    foreach ($f in $files) {
        if ($f.LastWriteTime -gt $cutoff) {
            $recent = $true
            break
        }
    }
} else {
    New-Item -ItemType Directory -Force -Path $savepointDir | Out-Null
}

if (-not $recent) {
    $staged = git diff --cached --name-only 2>$null
    $unstaged = git diff --name-only 2>$null
    $changes = @($staged, $unstaged) | Where-Object { $_ } | Measure-Object | Select-Object -ExpandProperty Count

    $savepointData = @{
        timestamp = (Get-Date -Format "o")
        action = "ITIL-pre-commit-guard"
        tracked_files = if ($staged) { @($staged) } else { @() }
        unstaged_files = if ($unstaged) { @($unstaged) } else { @() }
        git_branch = (git branch --show-current 2>$null)
        commit_message = (Get-Content "$repoRoot\.git\COMMIT_EDITMSG" -ErrorAction SilentlyContinue | Select-Object -First 1)
    } | ConvertTo-Json -Depth 2 -Compress

    [IO.File]::WriteAllText($savepointFile, $savepointData)

    Write-Host ""
    Write-Host "[NC-DS-260 ITIL] AUTO SAVEPOINT: $savepointFile" -ForegroundColor Yellow
    Write-Host "[NC-DS-260 ITIL] Mudancas detectadas: ~$changes arquivos. Savepoint criado." -ForegroundColor Yellow
    Write-Host "[NC-DS-260 ITIL] Rollback disponivel: neocortex_state action=savepoint.rollback" -ForegroundColor Yellow
    Write-Host ""
}

exit 0
