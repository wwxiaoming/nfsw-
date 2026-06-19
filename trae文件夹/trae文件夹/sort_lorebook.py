# -*- coding: utf-8 -*-
"""
sort_lorebook.py
扫描 Tavo参考世界书 全部文件（.json + .txt），按大小降序编号，输出：
- _索引/lorebook_size_index.json：结构化索引
- _索引/00_Tavo参考世界书总览.md：总览文档
"""
import json
import os
from pathlib import Path

WORK = Path(r'C:\Users\Administrator\Desktop\trae文件夹')
DST = WORK / 'extracted' / '帝王战队角色卡' / '帝王战队资料' / 'Tavo参考世界书'
INDEX_DIR = DST / '_索引'
INDEX_DIR.mkdir(parents=True, exist_ok=True)
INDEX_JSON = INDEX_DIR / 'lorebook_size_index.json'
OVERVIEW_MD = INDEX_DIR / '00_Tavo参考世界书总览.md'

# 跳过 _索引 目录自身
SKIP_DIRS = {'_索引'}

# 复制的独立世界书（无 tavo_spec）
STANDALONE_FILES = {
    '青港市世界书.json',
    '黄油XP百科全书 (1).json',
    'BDSM道具 2025.2.2 (1).json',
}

# 本次新增的 Ex 文件（用于"新/旧"标识）
EX_PATTERN = '_Ex'


def summarize_entries(obj) -> dict:
    """从一个标准 Tavo lorebook 提取摘要"""
    entries = obj.get('entries', {})
    if isinstance(entries, dict):
        total = len(entries)
        enabled = sum(1 for e in entries.values()
                      if isinstance(e, dict) and not e.get('disable', False))
        constant_n = sum(1 for e in entries.values()
                         if isinstance(e, dict) and e.get('constant', False))
        selective_n = sum(1 for e in entries.values()
                          if isinstance(e, dict) and e.get('selective', False))
        regex_n = sum(1 for e in entries.values()
                      if isinstance(e, dict) and e.get('use_regex', False))
        sample = []
        for k, e in list(entries.items())[:5]:
            if not isinstance(e, dict):
                continue
            keys = e.get('key', [])
            if isinstance(keys, str):
                keys = [keys]
            comment = e.get('comment', '').strip()
            content_preview = (e.get('content', '') or '').strip().split('\n')[0][:60]
            label = comment or content_preview or f'(no label)'
            sample.append({
                'uid': k,
                'key': keys[:5] if keys else [],
                'label': label[:80],
            })
        return {
            'total': total,
            'enabled': enabled,
            'constant': constant_n,
            'selective': selective_n,
            'use_regex': regex_n,
            'sample': sample,
        }
    elif isinstance(entries, list):
        total = len(entries)
        enabled = sum(1 for e in entries
                      if isinstance(e, dict) and not e.get('disable', False))
        sample = []
        for e in entries[:5]:
            if not isinstance(e, dict):
                continue
            keys = e.get('key', [])
            if isinstance(keys, str):
                keys = [keys]
            comment = e.get('comment', '').strip()
            content_preview = (e.get('content', '') or '').strip().split('\n')[0][:60]
            label = comment or content_preview or f'(no label)'
            sample.append({
                'uid': e.get('uid', '?'),
                'key': keys[:5] if keys else [],
                'label': label[:80],
            })
        return {
            'total': total,
            'enabled': enabled,
            'constant': 0,
            'selective': 0,
            'use_regex': 0,
            'sample': sample,
        }
    return {'total': 0, 'enabled': 0, 'constant': 0, 'selective': 0, 'use_regex': 0, 'sample': []}


def process_json(path: Path) -> dict:
    """处理一个 .json 世界书文件"""
    size = path.stat().st_size
    try:
        with open(path, 'r', encoding='utf-8') as f:
            obj = json.load(f)
    except Exception as e:
        return {
            'file': path.name,
            'rel_path': str(path.relative_to(DST)),
            'size_bytes': size,
            'type': 'json',
            'parse': 'FAIL',
            'error': str(e),
        }

    # obj 可能是 dict 或 list
    if isinstance(obj, list):
        # 顶层是 list（罕见，兼容）
        return {
            'file': path.name,
            'rel_path': str(path.relative_to(DST)),
            'size_bytes': size,
            'type': 'json',
            'tavo_spec': 'N/A',
            'name': '(top-level list)',
            'is_standalone': path.name in STANDALONE_FILES,
            'is_new_extract': EX_PATTERN in path.name,
            'total': len(obj),
            'enabled': 0,
            'constant': 0,
            'selective': 0,
            'use_regex': 0,
            'sample': [],
        }

    tavo_spec = obj.get('tavo_spec', 'N/A') if isinstance(obj, dict) else 'N/A'
    name = obj.get('name', '') if isinstance(obj, dict) else ''
    if not isinstance(name, str):
        name = str(name)
    is_standalone = path.name in STANDALONE_FILES
    is_ex = EX_PATTERN in path.name

    summary = summarize_entries(obj) if isinstance(obj, dict) else {
        'total': 0, 'enabled': 0, 'constant': 0, 'selective': 0, 'use_regex': 0, 'sample': []
    }
    return {
        'file': path.name,
        'rel_path': str(path.relative_to(DST)),
        'size_bytes': size,
        'type': 'json',
        'tavo_spec': tavo_spec,
        'name': name,
        'is_standalone': is_standalone,
        'is_new_extract': is_ex,
        **summary,
    }


def process_txt(path: Path) -> dict:
    """处理一个 .txt 文件（精能大陆）"""
    size = path.stat().st_size
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return {
            'file': path.name,
            'rel_path': str(path.relative_to(DST)),
            'size_bytes': size,
            'type': 'txt',
            'parse': 'FAIL',
            'error': str(e),
        }
    lines = text.splitlines()
    preview = '\n'.join(lines[:10])
    return {
        'file': path.name,
        'rel_path': str(path.relative_to(DST)),
        'size_bytes': size,
        'type': 'txt',
        'parse': 'OK',
        'char_count': len(text),
        'line_count': len(lines),
        'preview': preview,
    }


def main():
    # 1) 扫描
    items = []
    for p in sorted(DST.rglob('*')):
        if not p.is_file():
            continue
        # 跳过 _索引 目录
        rel = p.relative_to(DST)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.suffix.lower() == '.json':
            items.append(process_json(p))
        elif p.suffix.lower() == '.txt':
            items.append(process_txt(p))
        # 其他类型忽略

    # 2) 按大小降序
    items.sort(key=lambda x: -x['size_bytes'])

    # 3) 编号
    for i, it in enumerate(items, start=1):
        it['index'] = i

    # 4) 输出索引 JSON
    with open(INDEX_JSON, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f'[OK] 索引写入: {INDEX_JSON}  (共 {len(items)} 条)')

    # 5) 渲染 Markdown 总览
    total_size = sum(it['size_bytes'] for it in items)
    total_size_mb = total_size / 1024 / 1024
    new_count = sum(1 for it in items if it.get('is_new_extract'))
    new_entries_total = sum(
        it.get('total', 0) for it in items if it.get('is_new_extract') and it.get('type') == 'json'
    )

    lines = []
    lines.append('# Tavo 参考世界书 · 总览（按文件大小降序）')
    lines.append('')
    lines.append('> 生成日期：2026-06-19  ')
    lines.append('> 扫描目录：`extracted/帝王战队角色卡/帝王战队资料/Tavo参考世界书/`  ')
    lines.append('> 排序规则：按文件字节大小 **降序**，序号 1 = 最大文件  ')
    lines.append('> 索引 JSON：`_索引/lorebook_size_index.json`')
    lines.append('')
    lines.append('## 摘要')
    lines.append('')
    lines.append(f'- **总文件数**：{len(items)} 个')
    lines.append(f'- **总大小**：{total_size:,} bytes ≈ **{total_size_mb:.2f} MB**')
    json_count = sum(1 for it in items if it.get('type') == 'json')
    txt_count = sum(1 for it in items if it.get('type') == 'txt')
    lines.append(f'- **类型分布**：.json × {json_count}，.txt × {txt_count}')
    lines.append(f'- **本次新增**：{new_count} 个文件（带 `_Ex<NN>` 编号），合计 {new_entries_total:,} 个世界书条目')
    lines.append('')
    lines.append('## 1. 文件大小序列表')
    lines.append('')
    lines.append('| 序号 | 大小 | 文件名 | 类型 | 条目数 | 启用 | cb.name / 备注 | 状态 |')
    lines.append('|---:|---:|---|---|---:|---:|---|---|---|')
    for it in items:
        if it.get('type') == 'json':
            t = '.json'
            n_total = it.get('total', 0)
            n_en = it.get('enabled', 0)
            cb = it.get('name', '') or 'N/A'
            cb_short = cb[:30] + ('…' if len(cb) > 30 else '')
        else:
            t = '.txt'
            n_total = it.get('line_count', '-')
            n_en = '-'
            cb_short = f"text, {it.get('char_count', 0)} 字"
        size_str = f"{it['size_bytes']:,}"
        if it.get('is_new_extract'):
            status = '🆕 新提取'
        elif it.get('is_standalone'):
            status = '📋 复制'
        elif '写卡助手' in it['rel_path']:
            status = '🛠 助手'
        elif it['file'].endswith('.txt'):
            status = '📄 文本'
        else:
            status = '—'
        rel = it['rel_path']
        lines.append(f"| {it['index']} | {size_str} | `{rel}` | {t} | {n_total} | {n_en} | {cb_short} | {status} |")

    lines.append('')
    lines.append('## 2. 文件条目速览')
    lines.append('')
    lines.append('> 每个文件 H2 标题；列出：总条目数、启用数、触发模式、抽样前 5 条 entry 关键词')
    lines.append('')
    for it in items:
        lines.append(f"### {it['index']:>2}. {it['file']}")
        lines.append('')
        rel = it['rel_path']
        lines.append(f"- **路径**：`{rel}`")
        lines.append(f"- **大小**：{it['size_bytes']:,} bytes")
        if it.get('type') == 'json':
            tavo_spec = it.get('tavo_spec', 'N/A')
            name = it.get('name', '') or 'N/A'
            lines.append(f"- **tavo_spec**：{tavo_spec}")
            lines.append(f"- **name**：{name}")
            lines.append(f"- **条目数**：{it.get('total', 0)} (启用 {it.get('enabled', 0)})")
            if it.get('is_standalone'):
                lines.append("- **类型**：📋 复制的独立世界书")
            elif it.get('is_new_extract'):
                lines.append("- **类型**：🆕 本次从 `完整角色卡` 提取")
            else:
                lines.append("- **类型**：原有文件")
            if it.get('constant', 0) or it.get('selective', 0) or it.get('use_regex', 0):
                lines.append(f"- **触发模式**：constant={it.get('constant', 0)}，selective={it.get('selective', 0)}，use_regex={it.get('use_regex', 0)}")
            sample = it.get('sample', [])
            if sample:
                lines.append("- **抽样条目（前 5）**：")
                for s in sample:
                    keys = s.get('key', [])
                    key_str = ' / '.join(keys) if keys else '(no key)'
                    lines.append(f"  - uid=`{s['uid']}` key=`{key_str}` — {s['label']}")
        else:
            lines.append(f"- **类型**：.txt 文本")
            lines.append(f"- **行数**：{it.get('line_count', 0)}")
            lines.append(f"- **字符数**：{it.get('char_count', 0)}")
            preview = it.get('preview', '')
            if preview:
                lines.append("- **前 10 行预览**：")
                lines.append('  ```')
                for ln in preview.splitlines()[:10]:
                    lines.append(f"  {ln}")
                lines.append('  ```')
        lines.append('')

    lines.append('## 3. 版本差异说明')
    lines.append('')
    lines.append('本次提取过程中识别到以下"同名不同版本"的世界书，均按计划保留：')
    lines.append('')
    lines.append('| 主题 | 已有版本（_索引前） | 本次新增 |')
    lines.append('|---|---|---|')
    # 文件名含单引号，用反引号包裹时需注意 markdown 渲染；这里用 raw 三引号写
    line1 = """| 勇者养成指南 / 四叶草编年史 | `Tavo_勇者指引指南 v1 四叶草编年史's Lorebook (四叶草编年史)_SATY.json`（v1） | `Tavo_勇者养成指南 v5 世界里侧 1's Lorebook (-- 四叶草编年史v3)_Ex02.json`（v5） |"""
    line2 = """| 英雄纪元 淫堕训练师 | `Tavo_英雄纪元 淫堕训练师v1.27 MVU_T4Ki.json`（MVU 整卡） | `Tavo_英雄纪元 淫堕训练师v1.27 MVU 2's Lorebook (淫乱小英雄v1.27-mvu)_Ex04.json`（MVU 2 仅世界书） |"""
    line3 = '| Tavo_<X> 角色卡 | 已存在 | Ex01-Ex20 共 20 个新增 |'
    line4 = '| 非 Tavo 角色卡（无声星环/男子高中/转盘抽奖调教模拟器） | 不存在 | Ex21-Ex23 共 3 个新增 |'
    line5 = '| 独立世界书（青港市/黄油XP/BDSM道具） | 原本独立 | 复制进 Tavo参考世界书（同名） |'
    lines.append(line1)
    lines.append(line2)
    lines.append(line3)
    lines.append(line4)
    lines.append(line5)
    lines.append('')
    lines.append('## 4. 下一步')
    lines.append('')
    lines.append('基于本总览中的每个原文件世界书，对应写出"剧情文档"。')
    lines.append('剧情文档将按本总览的序号（1, 2, 3, ...）对应生成，存放于 `_索引/剧情/` 目录下。')
    lines.append('')

    with open(OVERVIEW_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'[OK] 总览写入: {OVERVIEW_MD}')


if __name__ == '__main__':
    main()
