$PROJECT_ROOT = $PSScriptRoot
$env:PYTHONPATH = $PROJECT_ROOT

Set-Location -Path $PROJECT_ROOT

Write-Host "======================================"
Write-Host "Loading Test"
Write-Host "======================================"


python -m pytest backend/console/tests

Write-Host "======================================"
Write-Host "Completed"
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")