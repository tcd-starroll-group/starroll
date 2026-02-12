# 替换为你的实际项目路径！！
$PROJECT_ROOT = "C:\Users\1\Desktop\First_semester\Advanced_software_enginering\starroll"
$env:PYTHONPATH = "$PROJECT_ROOT\gen\py\src;$PROJECT_ROOT"

Set-Location -Path $PROJECT_ROOT

Write-Host "======================================"
Write-Host "Loading."
Write-Host "======================================"


python -m fastapi dev "$PROJECT_ROOT\gen\py\src\openapi_server\main.py"


Write-Host "======================================"
Write-Host "Stop"
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")