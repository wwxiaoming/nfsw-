from pathlib import Path
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 读取 inventory 构建映射
inv = Path('工作区/tmp/novel_inventory.md').read_text(encoding='utf-8')
# 解析 inventory
parsed = {}
cat = None
for line in inv.split('\n'):
    line = line.strip()
    if line.startswith('## ') and not line.startswith('## Summary'):
        cat = line[3:].strip()
        parsed[cat] = {}
    elif line.startswith('|') and cat and '作品' not in line and '---' not in line:
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) >= 5:
            try:
                num, name, chapters = parts[0], parts[1], int(parts[2])
                max_kb = float(parts[3])
                total_kb = float(parts[4])
                path = parts[5] if len(parts) > 5 else ''
                parsed[cat][name] = {
                    'chapters': chapters,
                    'max_kb': max_kb,
                    'total_kb': total_kb,
                    'path': path
                }
            except Exception as e:
                pass

# flatten
all_novels = {}
for cat in parsed:
    all_novels.update(parsed[cat])

print(f'Loaded {len(all_novels)} novels from inventory')

# 速查表：逐行替换
sheet = Path('工作区/documents/v2-阶段4.1-sub-agent小说速查表_2026-06-20.md')
lines = sheet.read_text(encoding='utf-8').split('\n')

new_lines = []
replaced = 0
for line in lines:
    # 匹配作品行：| 序号 | 作品名 | ... | X/X (100%) | 4.X | ~XXXKB |
    if re.match(r'^\| \d+ \| .+ \| .+ \| \d+ \| .+ \| .+ \| .+ \| \d+/\d+ \(\d+%\) \| \d+\.\d+ \| ~\d+KB \|', line):
        # 提取作品名（第2列）
        parts = [p.strip() for p in line.split('|')[1:-1]]
        name = parts[1]
        if name in all_novels:
            info = all_novels[name]
            # 替换 ~xxxKB 为实际值
            new_line = line.rsplit('|', 1)[0] + f'| max {info["max_kb"]}KB / total {info["total_kb"]}KB |'
            new_lines.append(new_line)
            replaced += 1
            continue
    new_lines.append(line)

# 特殊处理：魔法世界Ⅱ 是 11 章，inventory 里就是 11，不要改成 39
# （这已经在之前被修复了，但如果还在就被换掉）
print(f'速查表替换 {replaced} 处作品行 file_size')
sheet.write_text('\n'.join(new_lines), encoding='utf-8')

# deployment 文档：需要先建立 SA -> 作品映射
# 先解析速查表
sheet_lines = '\n'.join(new_lines).split('\n')
sa_to_novels = {}
current_sa = None
for line in sheet_lines:
    m = re.match(r'^###\s+(SA-\d+[+\dA-Z-]+)[：:].*$', line)
    if m:
        current_sa = m.group(1)
        sa_to_novels[current_sa] = []
    if current_sa:
        m2 = re.match(r'^\| \d+ \| (.+?) \| `工作区/pixiv小说/', line)
        if m2:
            name = m2.group(1)
            sa_to_novels[current_sa].append(name)

print('SA 映射建立完成，样例：')
for sa in list(sa_to_novels.keys())[:5]:
    print(f'  {sa}: {sa_to_novels[sa]}')

# 处理 deployment 文档
deploy = Path('工作区/documents/v2-阶段4.1-4.3-逐本通读+笔记实时写入_2026-06-20.md')
lines = deploy.read_text(encoding='utf-8').split('\n')

# 先建立 deployment 中 SA 行列表，用速查表映射更新
new_lines = []
replaced = 0
current_sa = None
for line in lines:
    # 匹配部署文档中的 SA 行
    m = re.match(r'^\|\s*(SA-\d+[+\dA-Z-]*)\s*\|.*\| ~\d+KB \|', line)
    if m:
        sa_name = m.group(1)
        if sa_name in sa_to_novels:
            novels = sa_to_novels[sa_name]
            max_sum = sum(all_novels[n]['max_kb'] for n in novels if n in all_novels)
            total_sum = sum(all_novels[n]['total_kb'] for n in novels if n in all_novels)
            # 替换 size 列
            new_line = re.sub(r'\| ~\d+KB \|', f'| max {max_sum:.0f}KB / total {total_sum:.0f}KB |', line)
            new_lines.append(new_line)
            replaced += 1
            continue
    new_lines.append(line)

print(f'部署文档替换 {replaced} 处 SA size 行')
deploy.write_text('\n'.join(new_lines), encoding='utf-8')
print('完成')
