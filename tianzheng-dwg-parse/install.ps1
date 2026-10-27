# Tianzheng DWG Parse skill - one-line installer (Windows PowerShell)
# Usage:  irm https://raw.githubusercontent.com/hwdemtv/tianzheng-dwg-parse/main/install.ps1 | iex
$ErrorActionPreference = "Stop"

$owner = "hwdemtv"
$name  = "tianzheng-dwg-parse"
$dest  = Join-Path $env:USERPROFILE ".workbuddy\skills\$name"
$tmp   = Join-Path $env:TEMP "$name.zip"
$ext   = Join-Path $env:TEMP "$name-src"

Write-Host ">> Downloading $name ..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://github.com/$owner/$name/archive/refs/heads/main.zip" -OutFile $tmp -UseBasicParsing
if (Test-Path $ext) { Remove-Item $ext -Recurse -Force }
Expand-Archive -Path $tmp -DestinationPath $ext -Force
$src = Join-Path $ext "$name-main"

New-Item -ItemType Directory -Force -Path $dest | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $dest "references") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $dest "scripts") | Out-Null
Copy-Item (Join-Path $src "SKILL.md") $dest -Force
Copy-Item (Join-Path $src "references\*") (Join-Path $dest "references") -Force
Copy-Item (Join-Path $src "scripts\*") (Join-Path $dest "scripts") -Force

Remove-Item $tmp, $ext -Recurse -Force
Write-Host ">> Installed to $dest" -ForegroundColor Green
Write-Host ">> Restart WorkBuddy, then say: 用 tianzheng-dwg-parse 技能统计这张天正图纸的设备数量"
