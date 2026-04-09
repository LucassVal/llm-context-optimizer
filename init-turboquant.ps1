param(
    [string]$ProjectName = "my_project"
)

Write-Host "Initializing TurboQuant v4.2 structure for: $ProjectName..." -ForegroundColor Cyan

# Define the list of required folders
$dirs = @(
    ".agents\rules\archive",
    ".agents\workflows",
    "memory_lobes",
    "archive",
    "backup"
)

# Create folders ignoring errors if they already exist
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
    Write-Host " [OK] Directory created: $d" -ForegroundColor Green
}

# Copy the initial Cortex if templates directory exists
if (Test-Path ".\templates\00-cortex-STARTER.mdc") {
    Copy-Item ".\templates\00-cortex-STARTER.mdc" ".\.agents\rules\00-cortex.mdc" -Force
    Write-Host " [OK] Template 00-cortex-STARTER.mdc copied to .agents\rules\00-cortex.mdc" -ForegroundColor Green
} else {
    Write-Warning "Warning: The folder templates\00-cortex-STARTER.mdc was not found. Please copy it manually."
}

# Try to copy JSON ledger if it exists in the template
if (Test-Path ".\templates\memory-ledger-TEMPLATE.json") {
    $jsonTarget = "memory_turboquant_$($ProjectName).json"
    if (-not (Test-Path $jsonTarget)) {
        Copy-Item ".\templates\memory-ledger-TEMPLATE.json" $jsonTarget -Force
        Write-Host " [OK] JSON Ledger template copied to $jsonTarget" -ForegroundColor Green
    }
}

Write-Host "`n🚀 TurboQuant v4.2 initialized successfully at '.\'!" -ForegroundColor Yellow
Write-Host "📝 Modify .\.agents\rules\00-cortex.mdc to define your project's specific rules." -ForegroundColor Gray
