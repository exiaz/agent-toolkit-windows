param([switch]$DryRun)
$ErrorActionPreference = 'Stop'
$python = Get-Command python -ErrorAction Stop
& $python.Source -c 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ required"'
if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.11+ first.' }
$installerArgs = @((Join-Path $PSScriptRoot 'install.py'))
if ($DryRun) { $installerArgs += '--dry-run' }
& $python.Source @installerArgs
if ($LASTEXITCODE -ne 0) { throw 'Installation failed; see the error above.' }
