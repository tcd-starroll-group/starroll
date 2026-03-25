$PROJECT_ROOT = $PSScriptRoot
# 对应 makefile 中的 export PYTHONPATH="gen/py/src:."
$env:PYTHONPATH = "$PROJECT_ROOT\gen\py\src;$PROJECT_ROOT"

Set-Location -Path $PROJECT_ROOT

Write-Host "======================================"
Write-Host "Starting Backend Console Service..."
Write-Host "======================================"

# 对应 makefile 中的 uvicorn --reload --host 0.0.0.0 --port 8000 backend.console.app:app
# 推荐使用 python -m uvicorn 确保使用的是当前虚拟环境中的 uvicorn
python -m uvicorn backend.console.app:app --reload --host 0.0.0.0 --port 8000

Write-Host "======================================"
Write-Host "Service Stopped. Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")