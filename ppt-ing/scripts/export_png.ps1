# export_png.ps1 - 用真实 PowerPoint 渲染 PPTX 为逐页 PNG（PPT-ING QA 硬门槛）
#
# 为什么要绕这一圈：
#   1. PowerPoint COM 打不开含中文的路径（实测），必须先复制到纯英文临时目录
#   2. Open() 的 ReadOnly/Untitled/WithWindow 参数要传 msoTriState 整数 -1/0，
#      传 $true/$false 会报 "无法将值转换为 MsoTriState"
#
# 用法:
#   powershell -ExecutionPolicy Bypass -File export_png.ps1 -Pptx "D:\deck.pptx" -OutDir "D:\preview"
#   powershell -ExecutionPolicy Bypass -File export_png.ps1 -Pptx "D:\deck.pptx" -OutDir "D:\preview" -Width 2560 -Height 1440

param(
    [Parameter(Mandatory = $true)][string]$Pptx,
    [Parameter(Mandatory = $true)][string]$OutDir,
    [int]$Width = 1920,
    [int]$Height = 1080
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Pptx)) { throw "file not found: $Pptx" }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$tmp = Join-Path $env:TEMP ("pptqa_" + [guid]::NewGuid().ToString("N").Substring(0, 8))
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$work = Join-Path $tmp "deck.pptx"
Copy-Item $Pptx $work -Force

$app = $null
try {
    $app = New-Object -ComObject PowerPoint.Application
    $pres = $app.Presentations.Open($work, -1, 0, 0)   # ReadOnly=msoTrue, Untitled=msoFalse, WithWindow=msoFalse
    $n = $pres.Slides.Count
    for ($i = 1; $i -le $n; $i++) {
        $out = Join-Path $OutDir ("slide{0:d2}.png" -f $i)
        $pres.Slides.Item($i).Export($out, "PNG", $Width, $Height)
    }
    $pres.Close()
    Write-Output "exported $n slide(s) -> $OutDir"
}
finally {
    if ($app) {
        try { $app.Quit() } catch {}
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null
    }
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
