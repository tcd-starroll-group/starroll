
$PROJECT_ROOT = "C:\Users\1\Desktop\First_semester\Advanced_software_enginering\starroll"


$env:PYTHONPATH = $PROJECT_ROOT

Set-Location -Path $PROJECT_ROOT

Write-Host "======================================"
Write-Host "Loading Test"
Write-Host "======================================"


python -m pytest backend/console/tests

# 测试完成后提示
Write-Host "======================================"
Write-Host "Completed"
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")