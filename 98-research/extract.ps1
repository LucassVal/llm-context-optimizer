$files = Get-Content all_files.txt
$classes = @{}
$functions = @{}
$featureFlags = @{}
$callbacks = @{}
$constants = @{}
$integrations = @{}
$numericValues = @{}
foreach ($file in $files) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        # Classes
        $matches = [regex]::Matches($content, 'class\s+(\w+)')
        foreach ($match in $matches) { $classes[$match.Groups[1].Value] = $true }
        # Functions
        $matches = [regex]::Matches($content, 'function\s+(\w+)')
        foreach ($match in $matches) { $functions[$match.Groups[1].Value] = $true }
        $matches = [regex]::Matches($content, 'export\s+(?:default\s+)?(?:async\s+)?function\s+(\w+)')
        foreach ($match in $matches) { $functions[$match.Groups[1].Value] = $true }
        $matches = [regex]::Matches($content, 'const\s+(\w+)\s*=\s*function')
        foreach ($match in $matches) { $functions[$match.Groups[1].Value] = $true }
        # Uppercase constants
        $matches = [regex]::Matches($content, '[A-Z_][A-Z0-9_]+')
        foreach ($match in $matches) { $constants[$match.Value] = $true }
        # Feature flags
        $matches = [regex]::Matches($content, "feature\('([^']+)'\)")
        foreach ($match in $matches) { $featureFlags[$match.Groups[1].Value] = $true }
        $matches = [regex]::Matches($content, 'checkGate|featureFlag|experiment', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
        foreach ($match in $matches) { $featureFlags[$match.Value] = $true }
        # Callbacks
        $matches = [regex]::Matches($content, 'on[A-Z]\w+')
        foreach ($match in $matches) { $callbacks[$match.Value] = $true }
        $matches = [regex]::Matches($content, 'emit[A-Z]\w+')
        foreach ($match in $matches) { $callbacks[$match.Value] = $true }
        $matches = [regex]::Matches($content, 'subscribe|register|addListener', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
        foreach ($match in $matches) { $callbacks[$match.Value] = $true }
        # State machine
        $matches = [regex]::Matches($content, 'STATE_[A-Z0-9_]+|STATUS_[A-Z0-9_]+')
        foreach ($match in $matches) { $constants[$match.Value] = $true }
        # Timeouts/TTLs
        $matches = [regex]::Matches($content, '\d+_?MS')
        foreach ($match in $matches) { $numericValues[$match.Value] = $true }
        $matches = [regex]::Matches($content, '\d+_?S')
        foreach ($match in $matches) { $numericValues[$match.Value] = $true }
        $matches = [regex]::Matches($content, 'timeout|ttl|interval', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
        foreach ($match in $matches) { $numericValues[$match.Value] = $true }
        # Integrations
        $matches = [regex]::Matches($content, 'Datadog|Growthbook|Sentry|OTel|OpenTelemetry', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
        foreach ($match in $matches) { $integrations[$match.Value] = $true }
    } else {
        Write-Host "File not found: $file"
    }
}
Write-Host "=== RESULTS ==="
Write-Host "Classes: $($classes.Count)"
Write-Host "Functions: $($functions.Count)"
Write-Host "Feature flags: $($featureFlags.Count)"
Write-Host "Callbacks: $($callbacks.Count)"
Write-Host "Constants: $($constants.Count)"
Write-Host "Integrations: $($integrations.Count)"
Write-Host "Numeric values: $($numericValues.Count)"
Write-Host "---"
Write-Host "Top 20 constants:"
$constants.Keys | Sort-Object | Select-Object -First 20 | ForEach-Object { Write-Host $_ }
