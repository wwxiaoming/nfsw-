$ErrorActionPreference = 'SilentlyContinue'
Set-Location 'C:\Users\Administrator\Desktop\trae文件夹'
$src = '.\extracted\帝王战队角色卡\帝王战队资料\完整角色卡'
$dst = '.\extracted\帝王战队角色卡\帝王战队资料\Tavo参考世界书'
$files = Get-ChildItem $src -Filter '*.json'
Write-Host ('Total: {0} json files' -f $files.Count)
Write-Host ''
$rows = @()
foreach ($f in $files) {
    $raw = Get-Content $f.FullName -Raw -Encoding UTF8
    try {
        $obj = $raw | ConvertFrom-Json
    } catch {
        $rows += [pscustomobject]@{File=$f.Name; Parse='FAIL'; LorebookPath=''; SizeKB=[math]::Round($f.Length/1KB,1)}
        continue
    }
    $lorebookPath = ''
    if ($obj.entries) { $lorebookPath = '$.entries' }
    elseif ($obj.data.entries) { $lorebookPath = '$.data.entries' }
    elseif ($obj.data.character_book) { $lorebookPath = '$.data.character_book' }
    elseif ($obj.lorebook) { $lorebookPath = '$.lorebook' }
    elseif ($obj.character_book) { $lorebookPath = '$.character_book' }
    $rows += [pscustomobject]@{
        File = $f.Name
        SizeKB = [math]::Round($f.Length/1KB,1)
        Parse = 'OK'
        CharCard = ($obj.spec -eq 'chara_card_v3')
        LorebookPath = $lorebookPath
    }
}
$rows | Format-Table -AutoSize -Wrap
