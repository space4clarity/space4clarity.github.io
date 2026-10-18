param([string]$Time = '08:17')
$ErrorActionPreference = 'Stop'
$taskName = 'Space4Clarity Daily Reading'
$runner = Join-Path $PSScriptRoot 'run-daily.ps1'
$pythonPath = (Get-Command python -ErrorAction Stop).Source
$directories = @('node', 'git', 'codex') | ForEach-Object { Split-Path -Parent (Get-Command $_ -ErrorAction Stop).Source } | Select-Object -Unique
@{python = $pythonPath; commandDirectories = ($directories -join ';')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'local.json') -Encoding utf8
$action = New-ScheduledTaskAction -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument ('-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "' + $runner + '"') -WorkingDirectory (Split-Path -Parent $PSScriptRoot)
$daily = New-ScheduledTaskTrigger -Daily -At ([datetime]::Parse($Time))
$logon = New-ScheduledTaskTrigger -AtLogOn -User ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 45) -RestartCount 2 -RestartInterval (New-TimeSpan -Minutes 20)
$principal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$task = New-ScheduledTask -Action $action -Trigger @($daily, $logon) -Settings $settings -Principal $principal -Description 'Download a Gutenberg book, generate and verify one reading reflection, and publish it to Space4Clarity. Uses the existing Codex ChatGPT login. Runs once per Denver calendar day.'
Register-ScheduledTask -TaskName $taskName -InputObject $task -Force | Out-Null
Get-ScheduledTask -TaskName $taskName | Select-Object TaskName, State
Get-ScheduledTaskInfo -TaskName $taskName | Select-Object NextRunTime, LastRunTime, LastTaskResult
