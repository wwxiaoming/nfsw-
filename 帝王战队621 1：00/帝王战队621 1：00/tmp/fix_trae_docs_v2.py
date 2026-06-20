from pathlib import Path
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 读取 inventory 建立 total_kb 映射
inv_text = Path('工作区/tmp/novel_inventory.md').read_text(encoding='utf-8')
parsed = {}
cat = None
for line in inv_text.split('\n'):
    line = line.strip()
    if line.startswith('## ') and not line.startswith('## Summary'):
        cat = line[3:].strip()
        parsed[cat] = {}
    elif line.startswith('|') and cat and '作品' not in line and '---' not in line:
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) >= 5:
            try:
                name, total_kb = parts[1], float(parts[4])
                parsed[cat][name] = total_kb
            except:
                pass

all_novels = {}
for cat in parsed:
    all_novels.update(parsed[cat])

print(f'Loaded {len(all_novels)} novels')

# 修正速查表：去掉 max，只用 total
sheet_path = Path('.trae/documents/v2-阶段4.1-sub-agent小说速查表_2026-06-20.md')
lines = sheet_path.read_text(encoding='utf-8').split('\n')
new_lines = []
replaced = 0
for line in lines:
    if re.match(r'^\| \d+ \| .+ \| `工作区/pixiv小说/', line):
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) >= 10:
            name = parts[1]
            if name in all_novels:
                total = all_novels[name]
                new_line = line.rsplit('|', 1)[0] + f'| {int(total)}KB |'
                new_lines.append(new_line)
                replaced += 1
                continue
    new_lines.append(line)

sheet_path.write_text('\n'.join(new_lines), encoding='utf-8')
print(f'速查表替换 {replaced} 处（仅保留 total）')

# 修正部署文档：去掉 max，只用 total
deploy_path = Path('.trae/documents/v2-阶段4.1-4.3-逐本通读+笔记实时写入_2026-06-20.md')
lines = deploy_path.read_text(encoding='utf-8').split('\n')

# 重新解析速查表建立 SA -> 作品映射
sheet_lines = '\n'.join(new_lines).split('\n')
sa_to_novels = {}
current_sa = None
for line in sheet_lines:
    m = re.match(r'^###\s+(SA-\d+[+\dA-Z-]*)[：:]\s*《?(.+?)》?$', line)
    if m:
        current_sa = m.group(1)
        sa_to_novels[current_sa] = []
    if current_sa:
        m2 = re.match(r'^\| \d+ \| (.+?) \| `工作区/pixiv小说/', line)
        if m2:
            name = m2.group(1)
            sa_to_novels[current_sa].append(name)

new_lines = []
replaced = 0
for line in lines:
    m = re.match(r'^\|\s*(SA-\d+[+\dA-Z-]*)\s*\|.*\|(.*?)\|', line)
    if m:
        sa_name = m.group(1)
        if sa_name in sa_to_novels:
            novels = sa_to_novels[sa_name]
            total = sum(all_novels[n] for n in novels if n in all_novels)
            # 替换 size 列（去掉 max/total，只保留数值）
            new_line = re.sub(r'\| ?max \d+KB / total \d+KB ?\|', f'| {int(total)}KB |', line)
            new_line = re.sub(r'\| total \d+KB \|', f'| {int(total)}KB |', new_line)
            if new_line != line:
                new_lines.append(new_line)
                replaced += 1
                continue
    new_lines.append(line)

deploy_path.write_text('\n'.join(new_lines), encoding='utf-8')
print(f'部署文档替换 {replaced} 处')
print('完成：已去掉 max，仅保留 total 目录总大小')
