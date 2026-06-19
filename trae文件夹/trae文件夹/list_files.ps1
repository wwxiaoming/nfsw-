chcp 65001
chcp 65001|out-null
$dir1 = 'c:\Users\Administrator\Desktop\trae文件夹\extracted\帝王战队角色卡\帝王战队资料\其他小英雄小说\pixiv小说\03_正太校园堕落\奇怪的堕淫app'
$dir2 = 'c:\Users\Administrator\Desktop\trae文件夹\extracted\帝王战队角色卡\帝王战队资料\其他小英雄小说\pixiv小说\03_正太校园堕落\少年赤脚行'
$dir3 = 'c:\Users\Administrator\Desktop\trae文件夹\extracted\帝王战队角色卡\帝王战队资料\其他小英雄小说\pixiv小说\03_正太校园堕落\少年顶点游戏'
$dir4 = 'c:\Users\Administrator\Desktop\trae文件夹\extracted\帝王战队角色卡\帝王战队资料\其他小英雄小说\pixiv小说\03_正太校园堕落\学生奇遇'
$dir5 = 'c:\Users\Administrator\Desktop\trae文件夹\extracted\帝王战队角色卡\帝王战队资料\其他小英雄小说\pixiv小说\03_正太校园堕落\属于我的少年'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'
Write-Host '=== 1 ==='
Get-ChildItem -LiteralPath $dir1 -Filter '*.txt' | Where-Object { $_.Name -ne '作品信息.txt' } | Select-Object -ExpandProperty Name | ForEach-Object { Write-Host $_ }
Write-Host '=== 2 ==='
Get-ChildItem -LiteralPath $dir2 -Filter '*.txt' | Where-Object { $_.Name -ne '作品信息.txt' } | Select-Object -ExpandProperty Name | ForEach-Object { Write-Host $_ }
Write-Host '=== 3 ==='
Get-ChildItem -LiteralPath $dir3 -Filter '*.txt' | Where-Object { $_.Name -ne '作品信息.txt' } | Select-Object -ExpandProperty Name | ForEach-Object { Write-Host $_ }
Write-Host '=== 4 ==='
Get-ChildItem -LiteralPath $dir4 -Filter '*.txt' | Where-Object { $_.Name -ne '作品信息.txt' } | Select-Object -ExpandProperty Name | ForEach-Object { Write-Host $_ }
Write-Host '=== 5 ==='
Get-ChildItem -LiteralPath $dir5 -Filter '*.txt' | Where-Object { $_.Name -ne '作品信息.txt' } | Select-Object -ExpandProperty Name | ForEach-Object { Write-Host $_ }
