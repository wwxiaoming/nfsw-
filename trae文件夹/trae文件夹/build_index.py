# -*- coding: utf-8 -*-
"""
build_index.py
基于 convert_lorebook_to_md.py 生成的 convert_record.json 重建索引：
- _索引/00_Tavo参考世界书总览.md
- _索引/lorebook_size_index.json
"""
import json
from pathlib import Path

WORK = Path(r'C:\Users\Administrator\Desktop\trae文件夹')
DST = WORK / 'extracted' / '帝王战队角色卡' / '帝王战队资料' / 'Tavo参考世界书'
INDEX_DIR = DST / '_索引'
INDEX_DIR.mkdir(parents=True, exist_ok=True)
RECORD = INDEX_DIR / 'convert_record.json'
INDEX_JSON = INDEX_DIR / 'lorebook_size_index.json'
OVERVIEW_MD = INDEX_DIR / '00_Tavo参考世界书总览.md'

# 写卡助手 文件夹（保留，不参与编号）
ASSIST_DIR_NAME = '写卡助手'


def main():
    if not RECORD.exists():
        print(f'错误：找不到 {RECORD}')
        return 1

    with open(RECORD, 'r', encoding='utf-8') as f:
        records = json.load(f)

    # 计算每个 .md 的当前大小（已落盘）
    for r in records:
        md_path = DST / f"{r['sequence']:02d}.{r['display_name']}.md"
        if not md_path.exists():
            print(f"警告：{md_path} 不存在")
            r['md_path'] = None
            r['md_size'] = 0
        else:
            r['md_path'] = str(md_path.relative_to(DST))
            r['md_size'] = md_path.stat().st_size

    # 索引 JSON
    with open(INDEX_JSON, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f'[OK] 索引 JSON 写入: {INDEX_JSON}  ({len(records)} 条)')

    # 写卡助手 文件夹文件数
    assist_dir = DST / ASSIST_DIR_NAME
    assist_count = sum(1 for p in assist_dir.rglob('*.json')) if assist_dir.exists() else 0

    # 总览 MD
    total_md_size = sum(r['md_size'] for r in records)
    total_entries = sum(r['entry_count'] for r in records)

    lines = []
    lines.append('# Tavo 参考世界书 · 总览（按文件大小降序）')
    lines.append('')
    lines.append('> 生成日期：2026-06-19  ')
    lines.append('> 扫描目录：`extracted/帝王战队角色卡/帝王战队资料/Tavo参考世界书/`  ')
    lines.append('> **格式**：AI 可读 Markdown（H1 序号 + H2 条目标题 + 完整 content 原文）  ')
    lines.append('> **排序**：按文件大小 **降序**，序号 1 = 最大文件；`01.XX.md`、`02.XX.md` ...')
    lines.append('> 索引 JSON：`_索引/lorebook_size_index.json`  ')
    lines.append('> 转换记录：`_索引/convert_record.json`')
    lines.append('')
    lines.append('## 摘要')
    lines.append('')
    lines.append(f'- **总文件数**：{len(records)} 个 `.md` 世界书 + {assist_count} 个 `写卡助手/` 工具')
    lines.append(f'- **总大小**：{total_md_size:,} bytes ≈ **{total_md_size/1024/1024:.2f} MB**')
    lines.append(f'- **总条目数**：{total_entries:,} 个')
    lines.append(f'- **格式**：已剔除 JSON 代码字段（`uid/key/constant/position/selectiveLogic` 等），仅保留 `name` + `content`')
    lines.append('')
    lines.append('## 1. 文件大小序列表')
    lines.append('')
    lines.append('| 序号 | 大小 | 文件名 | 条目数 | 原始来源 |')
    lines.append('|---:|---:|---|---:|---|')
    for r in records:
        size_str = f"{r['md_size']:,}" if r['md_size'] else '-'
        filename = f"`{r['md_path']}`" if r['md_path'] else '?'
        lines.append(f"| {r['sequence']:02d} | {size_str} | {filename} | {r['entry_count']} | `{r['source_filename']}` |")
    lines.append('')
    lines.append('## 2. 文件速览')
    lines.append('')
    for r in records:
        title = f"{r['sequence']:02d}. {r['display_name']}.md"
        lines.append(f'### {title}')
        lines.append('')
        md_path = r.get('md_path', '')
        lines.append(f"- **大小**：{r['md_size']:,} bytes")
        lines.append(f"- **条目数**：{r['entry_count']}")
        lines.append(f"- **原始来源**：`{r['source_filename']}`（{r['source_size']:,} bytes）")
        lines.append(f"- **路径**：[`Tavo参考世界书/{md_path}`](file:///C:/Users/Administrator/Desktop/trae文件夹/extracted/帝王战队角色卡/帝王战队资料/Tavo参考世界书/{md_path.replace(chr(92), '/')})")
        lines.append('')
    lines.append('## 3. 命名约定')
    lines.append('')
    lines.append('- **格式**：`{序号}.{显示名}.md`，序号为 2 位前导零（01, 02, ...）')
    lines.append('- **排序规则**：按转换前的 .json 字节大小**降序**排序')
    lines.append('- **显示名来源**：')
    lines.append('  1. chara_card_v3：取 `data.name` 字段')
    lines.append('  2. Tavo lorebook：取 `Tavo_` 与 `’s Lorebook` 之间的部分（即源角色卡名）')
    lines.append('  3. 独立世界书 / prompt preset / .txt：取文件名去扩展名')
    lines.append('- **清洗规则**：去除 `Tavo_` 前缀、版本号（v4.2 / v5.1 / v1.27）、`MVU` 标记、`《》` 括号、`Worldbooks` 装饰、重复空格')
    lines.append('')
    lines.append('## 4. 排除范围')
    lines.append('')
    lines.append(f'- `{ASSIST_DIR_NAME}/` 子目录（共 {assist_count} 个）— 非世界书，是辅助工具，跳过转换')
    lines.append('- `_索引/` 目录自身 — 索引输出，不参与编号')
    lines.append('')
    lines.append('## 5. 下一步')
    lines.append('')
    lines.append('基于每个 .md 世界书，对应写出"剧情文档"。可按本总览的序号（01, 02, 03, ...）逐个读取再撰写。')
    lines.append('')
    lines.append('> 推荐路径：剧情文档存放在 `_索引/剧情/` 子目录下，按相同序号前缀命名，例如：')
    lines.append('> - `_索引/剧情/01.命定之诗与黄昏之歌.md`')
    lines.append('> - `_索引/剧情/02.WSXH.md`')
    lines.append('> - ...')
    lines.append('')

    with open(OVERVIEW_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'[OK] 总览写入: {OVERVIEW_MD}')

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
