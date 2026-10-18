$ErrorActionPreference = 'Stop'
$repoDirectory = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoDirectory
$localSettings = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'local.json') -Raw | ConvertFrom-Json
# Task Scheduler's PATH can lag behind an interactive terminal's environment.
$env:PATH = $localSettings.commandDirectories + ';' + $env:PATH
$logDirectory = Join-Path $PSScriptRoot 'runs'
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
$logFile = Join-Path $logDirectory ('scheduled-' + (Get-Date -Format 'yyyy-MM-dd-HHmmss') + '.log')
Start-Transcript -LiteralPath $logFile -Force | Out-Null
try {
    & $localSettings.python (Join-Path $PSScriptRoot 'daily.py') --publish
    if ($LASTEXITCODE -ne 0) { throw "Daily Reading failed with exit code $LASTEXITCODE. See $logFile" }
}
finally {
    Stop-Transcript | Out-Null
}
