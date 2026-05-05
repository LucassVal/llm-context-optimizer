$terms = @("KAIROS", "tick", "SendUserFile", "PushNotification", "SubscribePR", "BRIDGE_MODE", "VOICE_MODE", "AFK", "ULTRAPLAN", "TELEPORT_LOCAL", "DRM", "license", "telemetry", "obfuscat")
$srcPath = "C:\Users\Lucas Valério\Desktop\CLAUDE_CODE_DISSECTION\free-code\src"
Set-Location $srcPath
$outputDir = "C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-RES-CC-001-claude-leak-workzone\analysis-session-b\temp"
foreach ($term in $terms) {
    $files = Get-ChildItem -Recurse -Include *.ts, *.tsx | Select-String -Pattern $term | Select-Object -Unique Path
    $count = $files.Count
    Write-Host "$term : $count files"
    $files | Out-File "$outputDir\\${term}_files.txt"
}