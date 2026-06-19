chcp 65001 > $null
$dir = $args[0]
$subdirs = Get-ChildItem -Path $dir -Directory | Sort-Object Name
$total = 0
foreach ($sd in $subdirs) {
    $files = Get-ChildItem -Path $sd.FullName -Filter '*.txt' | Where-Object { $_.Name -ne '作品信息.txt' }
    $total += $files.Count
    Write-Host ('[' + $sd.Name + ']: ' + $files.Count + ' files')
}
Write-Host ('TOTAL: ' + $total)
