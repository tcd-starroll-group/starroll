$PROJECT_ROOT = $PSScriptRoot
$env:PYTHONPATH = "$PROJECT_ROOT\gen\py\src;$PROJECT_ROOT"

Set-Location -Path $PROJECT_ROOT

Write-Host "======================================"
Write-Host "Loading."
Write-Host "======================================"

& python -m fastapi dev "$PROJECT_ROOT\gen\py\src\openapi_server\main.py"

Write-Host "======================================"
Write-Host "Stop"
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")