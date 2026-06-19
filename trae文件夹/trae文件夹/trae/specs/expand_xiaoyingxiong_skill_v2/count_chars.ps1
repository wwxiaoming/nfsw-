$file = Get-Item ".\pixiv_深度阅读笔记_02_勇者魔物奇幻.md"
$content = [System.IO.File]::ReadAllText($file.FullName)
Write-Host "Characters: $($content.Length)"
Write-Host "File size (bytes): $($file.Length)"
