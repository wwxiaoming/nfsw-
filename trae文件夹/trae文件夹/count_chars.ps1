$path = "pixiv_深度阅读笔记_02_勇者魔物奇幻.md"
$fullPath = Join-Path (Get-Location) $path
$content = [System.IO.File]::ReadAllText($fullPath, [System.Text.Encoding]::UTF8)
Write-Host "Characters: $($content.Length)"
Write-Host "Lines: $($content.Split("`n").Count)"
Write-Host "File size (bytes): $((Get-Item $fullPath).Length)"
