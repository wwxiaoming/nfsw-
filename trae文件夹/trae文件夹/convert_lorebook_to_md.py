# -*- coding: utf-8 -*-
"""
convert_lorebook_to_md.py
将 Tavo参考世界书/ 下所有世界书（跳过 写卡助手/）从 JSON/TXT 转为 AI 可读的 Markdown 格式，
按文件大小降序加 01-51 序号，原地替换原文件。
"""
import json
import os
import re
import shutil
import sys
from pathlib import Path

WORK = Path(r'C:\Users\Administrator\Desktop\trae文件夹')
DST = WORK / 'extracted' / '帝王战队角色卡' / '帝王战队资料' / 'Tavo参考世界书'
TMP_DIR = DST / '.tmp_convert'
SKIP_DIRS = {'_索引', '写卡助手'}

# 用于显示名清洗
VERSION_RE = re.compile(r'\s*v\d+(\.\d+)*\s*', re.IGNORECASE)
LEADING_NUM_RE = re.compile(r'^\d+')
MVU_RE = re.compile(r'\s*MVU\s*\d*\s*', re.IGNORECASE)
TRAILING_PUNCT_RE = re.compile(r'[\s_\-]+$')
LEADING_PUNCT_RE = re.compile(r'^[\s_\-]+')
MULTI_SPACE_RE = re.compile(r'\s+')


def clean_display_name(name: str) -> str:
    """清洗显示名：去 Tavo_ 前缀、Lorebook 后缀、版本号、装饰符号"""
    if not name:
        return ''
    s = name
    # 去 Tavo_ 前缀
    s = re.sub(r'^Tavo_', '', s)
    # 去 "'s Lorebook (xxx)_ZZZZ" 模式
    s = re.sub(r"'s\s+Lorebook\s*\(.*?\)\s*_[A-Za-z0-9]{3,4}$", '', s)
    # 去 " (1)" " (2)" 副本后缀
    s = re.sub(r'\s*\(\d+\)\s*$', '', s)
    # 去版本号 vN.N
    s = VERSION_RE.sub(' ', s)
    # 去 MVU 标记
    s = MVU_RE.sub(' ', s)
    # 去前后 《》 括号
    s = s.replace('《', '').replace('》', '')
    # 去 "_Worldbooks" / "- Worldbooks" / "Worldbooks"
    s = re.sub(r'_?Worldbooks', '', s, flags=re.IGNORECASE)
    # 去前后短横线/下划线/空格
    s = LEADING_PUNCT_RE.sub('', s)
    s = TRAILING_PUNCT_RE.sub('', s)
    # 去前缀数字（仅在名字起头有数字）
    m = LEADING_NUM_RE.match(s)
    if m and len(s) > len(m.group(0)):
        # 仅当数字后是中文字符才去除
        next_char = s[len(m.group(0))]
        if '\u4e00' <= next_char <= '\u9fff':
            s = s[len(m.group(0)):]
    # 合并多空格
    s = MULTI_SPACE_RE.sub(' ', s).strip()
    return s


def extract_display_name(json_obj, filename: str) -> str:
    """从 JSON 或文件名提取显示名"""
    if isinstance(json_obj, dict):
        if json_obj.get('spec') == 'chara_card_v3':
            data = json_obj.get('data', {})
            if isinstance(data, dict) and data.get('name'):
                return clean_display_name(data['name'])
        # Tavo lorebook
        name = json_obj.get('name', '')
        if name and not name.startswith('Tavo_'):
            return clean_display_name(name)
    # 文件名兜底
    base = filename.rsplit('.', 1)[0]
    return clean_display_name(base)


def parse_entries(json_obj) -> list:
    """返回有序的 entry 列表（dict 列表）"""
    if not isinstance(json_obj, dict):
        return []
    # chara_card_v3 提取 character_book
    if json_obj.get('spec') == 'chara_card_v3':
        cb = json_obj.get('data', {}).get('character_book')
        if isinstance(cb, dict):
            return parse_entries(cb)
        return []
    # 标准 Tavo lorebook
    if json_obj.get('tavo_spec') == 'lorebook' or 'entries' in json_obj:
        entries = json_obj.get('entries', {})
        if isinstance(entries, dict):
            items = list(entries.values())
        elif isinstance(entries, list):
            items = entries
        else:
            return []
        # 过滤非 dict
        items = [e for e in items if isinstance(e, dict)]

        def sort_key(e):
            return (
                int(e.get('display_index', 9999)) if isinstance(e.get('display_index'), (int, float)) else 9999,
                int(e.get('order', 9999)) if isinstance(e.get('order'), (int, float)) else 9999,
                str(e.get('uid', '')),
            )
        items.sort(key=sort_key)
        return items
    return []


def parse_prompt_preset(json_obj) -> tuple:
    """处理 咒术回战 prompt preset 格式
    返回 (display_name, list of (section_title, content))
    """
    if not isinstance(json_obj, list) or not json_obj:
        return None, []
    item0 = json_obj[0]
    if not isinstance(item0, dict) or 'promptGroup' not in item0:
        return None, []
    name = item0.get('name', '咒术回战')
    sections = []
    for pg in item0.get('promptGroup', []):
        if not isinstance(pg, dict):
            continue
        role = pg.get('role', 'UNKNOWN').upper()
        content = pg.get('content', '')
        sections.append((role, content))
    return name, sections


def render_md(sequence: int, display_name: str, items: list, source_filename: str, source_size: int) -> str:
    """生成 Markdown 内容"""
    lines = []
    title = f"{sequence:02d}. {display_name}" if display_name else f"{sequence:02d}. 未命名世界书"
    lines.append(f'# {title}')
    lines.append('')
    if items:
        enabled_count = sum(1 for e in items if not e.get('disable', False))
        lines.append(f'> 共 {len(items)} 个条目（启用 {enabled_count} 个），原始来源：`{source_filename}`，原始大小 {source_size:,} bytes')
    else:
        lines.append(f'> 原始来源：`{source_filename}`，原始大小 {source_size:,} bytes')
    lines.append('')

    for i, e in enumerate(items):
        # 标题：name 优先，其次 comment
        title = e.get('name', '') or e.get('comment', '') or f'(未命名条目 {i+1})'
        title = str(title).strip() or f'(未命名条目 {i+1})'
        content = e.get('content', '') or ''
        if not content.strip():
            content = '<空内容>'
        lines.append(f'## {title}')
        lines.append('')
        lines.append(content.rstrip())
        lines.append('')

    return '\n'.join(lines)


def render_prompt_md(sequence: int, display_name: str, sections: list, source_filename: str, source_size: int) -> str:
    """生成 prompt preset 类型的 Markdown"""
    lines = []
    title = f"{sequence:02d}. {display_name}" if display_name else f"{sequence:02d}. 咒术回战"
    lines.append(f'# {title}')
    lines.append('')
    lines.append(f'> prompt preset，共 {len(sections)} 段，原始来源：`{source_filename}`，原始大小 {source_size:,} bytes')
    lines.append('')
    for role, content in sections:
        lines.append(f'## {role}')
        lines.append('')
        lines.append(content.rstrip())
        lines.append('')
    return '\n'.join(lines)


def render_txt(sequence: int, display_name: str, text: str, source_filename: str, source_size: int) -> str:
    """生成纯文本包装的 Markdown"""
    lines = []
    title = f"{sequence:02d}. {display_name}" if display_name else f"{sequence:02d}. 未命名文本"
    lines.append(f'# {title}')
    lines.append('')
    lines.append(f'> 纯文本，原始来源：`{source_filename}`，原始大小 {source_size:,} bytes')
    lines.append('')
    lines.append(text.rstrip())
    return '\n'.join(lines)


def process_json_file(path: Path, sequence_n: int) -> tuple:
    """处理一个 .json 文件，返回 (display_name, md_content, entry_count) 或 raise"""
    with open(path, 'r', encoding='utf-8') as f:
        obj = json.load(f)

    display_name = extract_display_name(obj, path.name)
    source_size = path.stat().st_size

    # chara_card_v3
    if isinstance(obj, dict) and obj.get('spec') == 'chara_card_v3':
        items = parse_entries(obj)
        md = render_md(sequence_n, display_name, items, path.name, source_size)
        return display_name, md, len(items)

    # 标准 Tavo lorebook 或独立世界书
    if isinstance(obj, dict) and ('entries' in obj or obj.get('tavo_spec') == 'lorebook'):
        items = parse_entries(obj)
        md = render_md(sequence_n, display_name, items, path.name, source_size)
        return display_name, md, len(items)

    # 咒术回战 prompt preset
    if isinstance(obj, list):
        name, sections = parse_prompt_preset(obj)
        if sections:
            display_name = name or display_name
            md = render_prompt_md(sequence_n, display_name, sections, path.name, source_size)
            return display_name, md, len(sections)

    raise ValueError(f'未识别的 JSON 格式: {path.name}')


def process_txt_file(path: Path, sequence_n: int) -> tuple:
    """处理 .txt 文件"""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    display_name = clean_display_name(path.stem)
    source_size = path.stat().st_size
    md = render_txt(sequence_n, display_name, text, path.name, source_size)
    return display_name, md, 0


def main():
    print(f'DST = {DST}')
    print()

    if not DST.exists():
        print(f'错误：目录不存在 {DST}')
        return 1

    # 1) 扫描候选文件
    candidates = []
    for p in sorted(DST.rglob('*')):
        if not p.is_file():
            continue
        rel = p.relative_to(DST)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.suffix.lower() not in ('.json', '.txt'):
            continue
        candidates.append(p)

    print(f'候选文件数: {len(candidates)}')
    if not candidates:
        return 1

    # 2) 按大小降序
    candidates.sort(key=lambda p: -p.stat().st_size)

    # 3) 编号
    for i, p in enumerate(candidates, start=1):
        print(f'  {i:02d}. {p.stat().st_size:>10,} bytes  {p.name[:80]}')

    # 4) 临时输出
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    # 5) 解析 + 转换
    converted = []
    used_names = {}  # 显示名 -> 计数（用于消重）
    fail_count = 0

    for i, p in enumerate(candidates, start=1):
        rel = p.relative_to(DST)
        print(f'\n[{i:02d}/{len(candidates)}] 处理: {rel}')
        try:
            if p.suffix.lower() == '.json':
                display_name, md_content, entry_count = process_json_file(p, i)
            else:
                display_name, md_content, entry_count = process_txt_file(p, i)
        except Exception as e:
            print(f'  [FAIL] 解析失败: {e}')
            fail_count += 1
            break  # fail-fast

        # 消重
        base_name = display_name or f'未命名世界书_{i}'
        if base_name in used_names:
            used_names[base_name] += 1
            base_name = f'{base_name}-{used_names[base_name]}'
        else:
            used_names[base_name] = 1
        out_name = f'{i:02d}.{base_name}.md'
        out_path = TMP_DIR / out_name
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        converted.append({
            'sequence': i,
            'display_name': base_name,
            'md_path': out_path,
            'source_path': p,
            'source_size': p.stat().st_size,
            'entry_count': entry_count,
        })
        print(f'  -> {out_name}  ({entry_count} entries, {len(md_content):,} chars)')

    if fail_count:
        print(f'\n错误：{fail_count} 个文件失败，已停止。请修复后重跑。')
        # 不删除 tmp，用户可检查
        return 1

    # 6) 验证：序号连续 + 文件名唯一
    seqs = [c['sequence'] for c in converted]
    if seqs != list(range(1, len(converted) + 1)):
        print(f'\n错误：序号不连续 {seqs}')
        return 1
    out_names = [c['md_path'].name for c in converted]
    if len(out_names) != len(set(out_names)):
        print(f'\n错误：输出文件名重复')
        return 1
    print('\n验证通过：序号连续、文件名唯一')

    # 7) 原子替换：把 .tmp 的文件移到 DST，删除所有原 .json/.txt
    print('\n开始原子替换...')
    for c in converted:
        final = DST / c['md_path'].name
        shutil.move(str(c['md_path']), str(final))
    # 删除所有原 .json/.txt (排除 写卡助手/ 和 _索引/)
    deleted = 0
    for p in DST.rglob('*'):
        if not p.is_file():
            continue
        rel = p.relative_to(DST)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.suffix.lower() in ('.json', '.txt'):
            p.unlink()
            deleted += 1
    # 删除 .tmp_convert
    shutil.rmtree(TMP_DIR)
    print(f'  移动 {len(converted)} 个 .md 到 DST')
    print(f'  删除 {deleted} 个原 .json/.txt')
    print(f'  清理临时目录 .tmp_convert')

    # 8) 保存转换记录 JSON (供后续 _索引 重建)
    record_path = DST / '_索引' / 'convert_record.json'
    record_path.parent.mkdir(parents=True, exist_ok=True)
    with open(record_path, 'w', encoding='utf-8') as f:
        json.dump([{
            'sequence': c['sequence'],
            'display_name': c['display_name'],
            'source_filename': c['source_path'].name,
            'source_size': c['source_size'],
            'entry_count': c['entry_count'],
        } for c in converted], f, ensure_ascii=False, indent=2)
    print(f'  转换记录写入: {record_path}')

    print('\n=== 全部完成 ===')
    return 0


if __name__ == '__main__':
    sys.exit(main())
