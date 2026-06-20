#!/usr/bin/env python3
"""
pixiv_renamer.py v2 — 按 作品信息 标准化章节文件名

v2 规则:
  - 新章节号 = 作品内 rank (按 作品信息 创建时间从早到晚排)
  - 新文件名:
      designation=章    → "第 N 章 副标题.txt" / "第 N 章.txt"
      designation=其他  → "NN designation 副标题.txt" (NN 零填充 2 位)
  - 中文数字 → 阿拉伯数字
  - 输出到 /workspace/pixiv_renamed/
"""
import argparse
import hashlib
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SRC_ROOT = Path("/workspace/pixiv_workspace")
DST_ROOT = Path("/workspace/pixiv_renamed")
REPORT_PATH = DST_ROOT / "rename_report.md"

WIN_ILLEGAL_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
BLOCK_HEADER_RE = re.compile(r'^===\s*(\d+)\s*[.、]?\s*(.+?)\s*===\s*$')
NUMBERED_RE = re.compile(r'^#(\d+)\s+(.+)\.txt$')

# 规范化标点（去重 + 去空白）
_PUNCT_RE = re.compile(
    r'[\s\u3000'
    r'《》「」『』“”"\'‘’'
    r'()()（）【】\[\]<>《》、'
    r'。.,，;:：!！?？—\-_~～·•…&＋+&'
    r']'
)

# ────────────────────────────────────────────────────────
# 中文数字 → int
# ────────────────────────────────────────────────────────
_CN_DIGIT = {'零': 0, '〇': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4,
             '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
_CN_UNIT = {'十': 10, '百': 100, '千': 1000}


def cn_num_to_int(s: str) -> Optional[int]:
    """
    把中文数字串转成 int。范围 0..9999。
    支持: 一/二/.../九, 十/百/千, 零, 二十三, 一百零五, 一千零一 等。
    返回 None 表示无法解析。
    """
    if not s:
        return None
    # 纯阿拉伯数字直接返回
    if s.isdigit():
        return int(s)

    # 去掉所有空白
    s = s.strip()
    if not s:
        return None

    # 全部字符必须都在合法集里
    valid_chars = set(_CN_DIGIT) | set(_CN_UNIT)
    for ch in s:
        if ch not in valid_chars:
            return None

    # 解析
    total = 0
    current = 0
    for ch in s:
        if ch in _CN_DIGIT:
            current = _CN_DIGIT[ch]
        elif ch in _CN_UNIT:
            unit = _CN_UNIT[ch]
            if current == 0:
                current = 1  # "十" 表示 10, 不是 0
            total += current * unit
            current = 0
    total += current
    return total


# ────────────────────────────────────────────────────────
# 标题模板解析
# ────────────────────────────────────────────────────────
# 优先级从高到低:
_PATTERNS = [
    # 第X季后记 / 第X季终章 / 第X季后日
    (re.compile(r'^第([零〇一二三四五六七八九十百千两\d]+)(季后记|季终章|季后日)(\s+(.+))?$'),
     'season_special'),
    # 第X话 副标题 (日语体)
    (re.compile(r'^第([零〇一二三四五六七八九十百千两\d]+)话(\s+(.+))?$'), 'hua'),
    # 第X章 副标题
    (re.compile(r'^第([零〇一二三四五六七八九十百千两\d]+)章(\s+(.+))?$'), 'zhang'),
    # 序章 副标题
    (re.compile(r'^序章(\s+(.+))?$'), 'xu'),
    # 终章 副标题
    (re.compile(r'^终章(\s+(.+))?$'), 'zhong'),
    # 番外 副标题 (无数字)
    (re.compile(r'^番外(\s+(.+))?$'), 'fanwai'),
    # 番外N 副标题 (有数字)
    (re.compile(r'^番外\s*([零〇一二三四五六七八九十百千两\d]+)(\s+(.+))?$'), 'fanwai_num'),
    # 幕间 副标题
    (re.compile(r'^幕间(\s+(.+))?$'), 'muxu'),
    # if线 副标题
    (re.compile(r'^if线(\s+(.+))?$'), 'ifxian'),
]


def parse_title(title: str) -> Tuple[str, Optional[int], str]:
    """
    解析 作品信息 标题。
    返回 (designation, number, subtitle)
    designation: '章' / '话' / '序章' / '终章' / '后记' / '番外' / '幕间' / 'if线'
    number: int or None
    subtitle: str
    """
    title = (title or '').strip()
    if not title:
        return '章', None, ''

    for pat, kind in _PATTERNS:
        m = pat.match(title)
        if not m:
            continue
        if kind == 'season_special':
            num = cn_num_to_int(m.group(1))
            special = m.group(2)  # 后记 / 终章 / 后日
            # 去掉 "季" 前缀, 保留 "后记" / "终章" / "后日"
            if special.startswith('季'):
                special = special[1:]
            subtitle = m.group(4).strip() if m.group(4) else ''
            designation = special  # 后记 / 终章 / 后日
            return designation, num, subtitle
        if kind == 'hua':
            num = cn_num_to_int(m.group(1))
            subtitle = m.group(3).strip() if m.group(3) else ''
            return '话', num, subtitle
        if kind == 'zhang':
            num = cn_num_to_int(m.group(1))
            subtitle = m.group(3).strip() if m.group(3) else ''
            return '章', num, subtitle
        if kind == 'xu':
            subtitle = m.group(2).strip() if m.group(2) else ''
            return '序章', None, subtitle
        if kind == 'zhong':
            subtitle = m.group(2).strip() if m.group(2) else ''
            return '终章', None, subtitle
        if kind == 'fanwai':
            subtitle = m.group(2).strip() if m.group(2) else ''
            return '番外', None, subtitle
        if kind == 'fanwai_num':
            num = cn_num_to_int(m.group(1))
            subtitle = m.group(3).strip() if m.group(3) else ''
            return '番外', num, subtitle
        if kind == 'muxu':
            subtitle = m.group(2).strip() if m.group(2) else ''
            return '幕间', None, subtitle
        if kind == 'ifxian':
            subtitle = m.group(2).strip() if m.group(2) else ''
            return 'if线', None, subtitle

    # 无法识别
    return '章', None, title


# ────────────────────────────────────────────────────────
# 工具函数
# ────────────────────────────────────────────────────────
def normalize_for_match(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = _PUNCT_RE.sub('', s)
    return s.lower()


def safe_filename(name: str) -> str:
    name = WIN_ILLEGAL_RE.sub('', name)
    name = name.rstrip().lstrip()
    name = name.strip(' .')
    return name


def parse_work_info(text: str) -> List[dict]:
    """
    解析 作品信息.txt 文本, 返回按 作品信息 顺序 升序的条目列表.
    每条: {order, title, work_id, created_at, raw_title, parsed: {designation, number, subtitle}, rank}
    """
    entries = []
    current = None
    for line in text.splitlines():
        m = BLOCK_HEADER_RE.match(line)
        if m:
            if current:
                entries.append(current)
            order = int(m.group(1))
            header_title = m.group(2).strip()
            current = {
                'order': order,
                'title': header_title,
                'work_id': None,
                'created_at': '',
                'raw_title': header_title,
            }
            continue
        if current is None:
            continue
        s = line.strip()
        if s.startswith('标题：') or s.startswith('标题:'):
            current['title'] = s.split('：', 1)[-1].split(':', 1)[-1].strip()
        elif s.startswith('作品id：') or s.startswith('作品id:') or s.startswith('作品ID：'):
            current['work_id'] = s.split('：', 1)[-1].split(':', 1)[-1].strip()
        elif s.startswith('创建时间：') or s.startswith('创建时间:'):
            current['created_at'] = s.split('：', 1)[-1].split(':', 1)[-1].strip()
    if current:
        entries.append(current)

    # 解析每条的 designation/number/subtitle
    for e in entries:
        des, num, sub = parse_title(e['title'])
        e['parsed'] = {'designation': des, 'number': num, 'subtitle': sub}

    return entries


def parse_created_at(s: str) -> Optional[datetime]:
    """解析 ISO 8601 时间字符串"""
    if not s:
        return None
    try:
        # 去掉时区后缀简化处理
        s = s.replace('Z', '+00:00')
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def find_work_info_files(root: Path) -> Dict[str, Path]:
    result = {}
    for p in root.rglob("作品信息.txt"):
        rel_dir = p.parent.relative_to(root)
        result[str(rel_dir)] = p
    return result


# ────────────────────────────────────────────────────────
# 构建索引 + 作品内 rank
# ────────────────────────────────────────────────────────
def build_work_info_index(root: Path) -> Tuple[Dict, List, Dict]:
    """
    返回:
      - work_index: {
          作品目录: {
            'entries': [按 order 升序],
            'by_order': {order: entry},
            'by_work_id': {work_id: entry},
            'normalized_titles': {norm_title: entry},
            'empty': bool,
            'used_work_ids': set,
            'ranked': [entry按 created_at 升序],
          }
        }
      - empty_dirs: 作品信息为空/缺失的目录列表
      - parse_errors: {dir: error_message}
    """
    work_index = {}
    empty_dirs = []
    parse_errors = {}

    info_files = find_work_info_files(root)
    all_dirs = {str(p.parent.relative_to(root)) for p in root.rglob("*.txt") if p.is_file()}

    for rel_dir, info_path in info_files.items():
        try:
            text = info_path.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            parse_errors[rel_dir] = f"read failed: {e}"
            continue
        entries = parse_work_info(text)
        if not entries:
            empty_dirs.append(rel_dir)
            work_index[rel_dir] = _empty_work_info()
            continue
        entries.sort(key=lambda e: e['order'])
        by_order = {e['order']: e for e in entries}
        by_work_id = {e['work_id']: e for e in entries if e.get('work_id')}
        normalized_titles = {}
        for e in entries:
            nt = normalize_for_match(e['title'])
            if nt and nt not in normalized_titles:
                normalized_titles[nt] = e

        # 计算 rank: 按 created_at 升序; 无 created_at 的条目放最后, 按 order 降序
        with_time = []
        without_time = []
        for e in entries:
            dt = parse_created_at(e['created_at'])
            if dt:
                with_time.append((dt, e))
            else:
                without_time.append(e)
        with_time.sort(key=lambda x: x[0])
        # 无时间: 排在最后, 顺序按 order 降序 (order=1 最新, 应在最后)
        without_time.sort(key=lambda e: -e['order'])

        ranked = [e for _, e in with_time] + without_time
        for i, e in enumerate(ranked, start=1):
            e['rank'] = i

        work_index[rel_dir] = {
            'entries': entries,
            'by_order': by_order,
            'by_work_id': by_work_id,
            'normalized_titles': normalized_titles,
            'empty': False,
            'used_work_ids': set(),
            'ranked': ranked,
        }

    for rel_dir in all_dirs:
        if rel_dir not in work_index and rel_dir != '.':
            empty_dirs.append(rel_dir)
            work_index[rel_dir] = _empty_work_info()

    return work_index, empty_dirs, parse_errors


def _empty_work_info():
    return {
        'entries': [],
        'by_order': {},
        'by_work_id': {},
        'normalized_titles': {},
        'empty': True,
        'used_work_ids': set(),
        'ranked': [],
    }


def match_file_to_entry(raw_title: str, work_dir_info: dict) -> Optional[dict]:
    """模糊匹配 作品信息 条目"""
    nt = normalize_for_match(raw_title)
    if not nt:
        return None
    if nt in work_dir_info['normalized_titles']:
        return work_dir_info['normalized_titles'][nt]
    # 子串匹配
    best_entry = None
    best_overlap = 0
    for norm_t, entry in work_dir_info['normalized_titles'].items():
        if nt in norm_t or norm_t in nt:
            overlap = min(len(nt), len(norm_t))
            if overlap > best_overlap:
                best_overlap = overlap
                best_entry = entry
    return best_entry


# ────────────────────────────────────────────────────────
# 生成新文件名
# ────────────────────────────────────────────────────────
def make_new_name(entry: dict) -> str:
    """
    根据 entry (含 parsed.designation, parsed.number, parsed.subtitle, rank)
    生成新文件名 (不含 .txt).
    """
    p = entry['parsed']
    rank = entry.get('rank', 0)
    des = p['designation']
    sub = p['subtitle']

    if des == '章':
        # 第 N 章 [副标题]
        if sub:
            return f"第 {rank} 章 {sub}"
        return f"第 {rank} 章"
    else:
        # NN designation [副标题]
        prefix = f"{rank:02d} {des}"
        if sub:
            return f"{prefix} {sub}"
        return prefix


# ────────────────────────────────────────────────────────
# 计划
# ────────────────────────────────────────────────────────
def plan_renames(root: Path) -> Tuple[List[dict], dict]:
    work_index, empty_dirs, parse_errors = build_work_info_index(root)
    plan = []
    stats = {
        'total_files': 0,
        'info_files': 0,
        'numbered': 0,
        'renamed': 0,
        'no_info_kept': 0,
        'untouched': 0,
        'skipped_empty': 0,
        'conflicts_resolved': 0,
        'manual_review': [],
    }

    all_txt = sorted([p for p in root.rglob("*.txt") if p.is_file()])
    stats['total_files'] = len(all_txt)

    by_dir = defaultdict(list)
    for p in all_txt:
        rel_dir = str(p.parent.relative_to(root))
        by_dir[rel_dir].append(p)

    for rel_dir in sorted(by_dir.keys()):
        info = work_index.get(rel_dir)
        files = by_dir[rel_dir]
        used_new_names: Dict[str, int] = defaultdict(int)

        for src in files:
            old_name = src.name
            rel_src = str(src.relative_to(root))

            # 1. 作品信息.txt 原样
            if old_name == '作品信息.txt':
                stats['info_files'] += 1
                plan.append({
                    'src': src,
                    'rel_src': rel_src,
                    'work_dir': rel_dir,
                    'old_name': old_name,
                    'new_name': '作品信息.txt',
                    'action': 'info_copied',
                    'note': '',
                    'work_id': None,
                })
                continue

            # 2. 0 字节文件: 原样保留 (不重命名, 避免覆盖)
            if src.stat().st_size == 0:
                stats['skipped_empty'] += 1
                plan.append({
                    'src': src,
                    'rel_src': rel_src,
                    'work_dir': rel_dir,
                    'old_name': old_name,
                    'new_name': old_name,
                    'action': 'skipped_empty',
                    'note': '0 字节文件, 原样保留',
                    'work_id': None,
                })
                stats['manual_review'].append({
                    'rel': rel_src, 'reason': '0 字节文件 (zip 中原已为空)'
                })
                continue

            # 3. 解析 #N
            m = NUMBERED_RE.match(old_name)
            file_n = int(m.group(1)) if m else None
            raw_title = m.group(2).strip() if m else (old_name[:-4] if old_name.endswith('.txt') else old_name)
            if m:
                stats['numbered'] += 1

            matched_entry = None
            if info and not info['empty']:
                matched_entry = match_file_to_entry(raw_title, info)
                if matched_entry and matched_entry.get('work_id'):
                    info['used_work_ids'].add(matched_entry['work_id'])

            if matched_entry is None:
                # 匹配失败
                if file_n is not None:
                    stats['no_info_kept'] += 1
                    note = '作品信息 缺失/为空 或 无匹配, 保留原标题去 #N 前缀'
                    new_name = raw_title + '.txt' if raw_title else old_name
                    action = 'no_info_kept'
                else:
                    stats['untouched'] += 1
                    note = '无 #N 前缀且 作品信息 无匹配, 原样保留'
                    new_name = old_name
                    action = 'untouched'

                plan.append({
                    'src': src,
                    'rel_src': rel_src,
                    'work_dir': rel_dir,
                    'old_name': old_name,
                    'new_name': new_name,
                    'action': action,
                    'note': note,
                    'work_id': None,
                })

                if info and info['empty']:
                    stats['manual_review'].append({
                        'rel': rel_dir + '/', 'reason': '作品信息 缺失或为空'
                    })
                elif file_n is not None and info and not info['empty']:
                    stats['manual_review'].append({
                        'rel': rel_src,
                        'reason': f'#N 文件 {raw_title!r} 无法匹配 作品信息 中任何标题'
                    })
                continue

            # 4. 生成新名
            new_name = make_new_name(matched_entry) + '.txt'
            base = new_name
            if new_name in used_new_names:
                used_new_names[new_name] += 1
                stem = base[:-4]
                new_name = f"{stem} ({used_new_names[new_name]}).txt"
                stats['conflicts_resolved'] += 1
                stats['manual_review'].append({
                    'rel': rel_src,
                    'reason': f'同目录命名冲突: {base!r} 已存在, 追加 ({used_new_names[new_name]})'
                })
            else:
                used_new_names[base] = 1

            cleaned = safe_filename(new_name[:-4]) + '.txt' if new_name.endswith('.txt') else safe_filename(new_name)
            if cleaned != new_name:
                stats['manual_review'].append({
                    'rel': rel_src,
                    'reason': f'Windows 非法字符被清洗: {new_name!r} → {cleaned!r}'
                })
                new_name = cleaned
            if new_name == '.txt' or not new_name.strip('.txt'):
                new_name = '__untitled__.txt'
                stats['manual_review'].append({
                    'rel': rel_src, 'reason': '清洗后文件名为空, 使用 __untitled__'
                })

            stats['renamed'] += 1
            plan.append({
                'src': src,
                'rel_src': rel_src,
                'work_dir': rel_dir,
                'old_name': old_name,
                'new_name': new_name,
                'action': 'renamed',
                'note': f"rank={matched_entry['rank']}, des={matched_entry['parsed']['designation']}, num={matched_entry['parsed']['number']}",
                'work_id': matched_entry.get('work_id'),
            })

    return plan, stats


# ────────────────────────────────────────────────────────
# 执行
# ────────────────────────────────────────────────────────
def execute_plan(plan: List[dict], dry_run: bool = False) -> int:
    if not dry_run:
        if DST_ROOT.exists():
            shutil_rmtree(DST_ROOT)
        DST_ROOT.mkdir(parents=True, exist_ok=True)
    copied = 0
    for p in plan:
        src: Path = p['src']
        rel_src: str = p['rel_src']
        new_name: str = p['new_name']
        dst = DST_ROOT / Path(rel_src).parent / new_name
        if dry_run:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        dst.write_bytes(data)
        if hashlib.md5(data).hexdigest() != hashlib.md5(dst.read_bytes()).hexdigest():
            raise RuntimeError(f"hash mismatch for {dst}")
        copied += 1
    return copied


def shutil_rmtree(path):
    import shutil
    shutil.rmtree(path)


def write_report(plan: List[dict], stats: dict, dry_run: bool) -> None:
    lines = []
    lines.append('# Pixiv 章节文件重命名报告 (v2)')
    lines.append('')
    if dry_run:
        lines.append('> **DRY-RUN 模式** — 下方计划未实际执行')
        lines.append('')
    lines.append('## 总览')
    lines.append('')
    lines.append(f'- 扫描 .txt 文件总数：**{stats["total_files"]}**')
    lines.append(f'- 作品信息.txt 数：**{stats["info_files"]}**')
    lines.append(f'- `#N` 编号章节文件：**{stats["numbered"]}**')
    lines.append(f'- 重命名成功：**{stats["renamed"]}**')
    lines.append(f'- 作品信息 缺失/为空, 保留原标题：**{stats["no_info_kept"]}**')
    lines.append(f'- 无 `#N` 前缀且无匹配 (untouched)：**{stats["untouched"]}**')
    lines.append(f'- 0 字节文件原样保留：**{stats["skipped_empty"]}**')
    lines.append(f'- 命名冲突自动加 `(2)/(3)`：**{stats["conflicts_resolved"]}**')
    lines.append('')
    lines.append('> 新章节号 = 作品内 rank（按 作品信息 创建时间从早到晚排，rank 1 = 最早发布）')
    lines.append('')

    by_dir = defaultdict(list)
    for p in plan:
        by_dir[p['work_dir']].append(p)

    lines.append('## 各作品重命名表')
    lines.append('')
    for rel_dir in sorted(by_dir.keys()):
        items = by_dir[rel_dir]
        lines.append(f'### `{rel_dir}`')
        lines.append('')
        lines.append('| 旧文件名 | 新文件名 | 匹配 | 作品 ID |')
        lines.append('| --- | --- | --- | --- |')
        for p in sorted(items, key=lambda x: x['old_name']):
            old = p['old_name'].replace('|', '\\|')
            new = p['new_name'].replace('|', '\\|')
            note = p.get('note', '') or p.get('action', '')
            wid = p.get('work_id') or '-'
            lines.append(f'| `{old}` | `{new}` | {note} | {wid} |')
        lines.append('')

    lines.append('## ⚠️ 需人工核对清单')
    lines.append('')
    if not stats['manual_review']:
        lines.append('_无_')
        lines.append('')
    else:
        seen = set()
        for r in stats['manual_review']:
            key = (r.get('rel', ''), r.get('reason', ''))
            if key in seen:
                continue
            seen.add(key)
            lines.append(f'- `{r.get("rel", "?")}` — {r.get("reason", "")}')
        lines.append('')

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text('\n'.join(lines), encoding='utf-8')


# ────────────────────────────────────────────────────────
# main
# ────────────────────────────────────────────────────────
def main():
    global SRC_ROOT, DST_ROOT, REPORT_PATH
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--src', default=str(SRC_ROOT))
    ap.add_argument('--dst', default=str(DST_ROOT))
    args = ap.parse_args()

    SRC_ROOT = Path(args.src)
    DST_ROOT = Path(args.dst)
    REPORT_PATH = DST_ROOT / 'rename_report.md'

    print(f'[1/3] 解析 {SRC_ROOT} ...')
    plan, stats = plan_renames(SRC_ROOT)
    print(f'      共 {stats["total_files"]} 个文件')
    print(f'[2/3] {"DRY-RUN" if args.dry_run else "执行到 " + str(DST_ROOT)} ...')
    copied = execute_plan(plan, dry_run=args.dry_run)
    print(f'      已处理 {copied} 个文件')
    print(f'[3/3] 写入报告 {REPORT_PATH} ...')
    write_report(plan, stats, dry_run=args.dry_run)
    print('完成。')
    print()
    for k, v in stats.items():
        if k == 'manual_review':
            print(f'  {k}: {len(v)} 条')
        else:
            print(f'  {k}: {v}')


# ────────────────────────────────────────────────────────
# 内置自测
# ────────────────────────────────────────────────────────
def _self_test():
    """单测 cn_num_to_int + parse_title"""
    tests_passed = 0
    tests_failed = 0

    def check(label, got, expected):
        nonlocal tests_passed, tests_failed
        if got == expected:
            tests_passed += 1
        else:
            tests_failed += 1
            print(f'  FAIL: {label}: got {got!r}, expected {expected!r}')

    # cn_num_to_int
    check('cn 0', cn_num_to_int('零'), 0)
    check('cn 1', cn_num_to_int('一'), 1)
    check('cn 10', cn_num_to_int('十'), 10)
    check('cn 13', cn_num_to_int('十三'), 13)
    check('cn 23', cn_num_to_int('二十三'), 23)
    check('cn 100', cn_num_to_int('一百'), 100)
    check('cn 105', cn_num_to_int('一百零五'), 105)
    check('cn 99', cn_num_to_int('九十九'), 99)
    check('digit 5', cn_num_to_int('5'), 5)

    # parse_title
    check('parse 第一章 雄鹰末路', parse_title('第一章 雄鹰末路'), ('章', 1, '雄鹰末路'))
    check('parse 第十四章', parse_title('第十四章'), ('章', 14, ''))
    check('parse 序章 鬼影', parse_title('序章 鬼影'), ('序章', None, '鬼影'))
    check('parse 终章 人间', parse_title('终章 人间'), ('终章', None, '人间'))
    check('parse 第一季后记', parse_title('第一季后记'), ('后记', 1, ''))
    check('parse 第一季终章', parse_title('第一季终章'), ('终章', 1, ''))
    check('parse 番外 番外二', parse_title('番外 番外二'), ('番外', None, '番外二'))
    check('parse 幕间', parse_title('幕间'), ('幕间', None, ''))
    check('parse if线 其一 三人行', parse_title('if线 其一 三人行'), ('if线', None, '其一 三人行'))
    check('parse 第七话', parse_title('第七话 青春的烦恼'), ('话', 7, '青春的烦恼'))
    check('parse 序章', parse_title('序章'), ('序章', None, ''))

    print(f'\n[单测] 通过 {tests_passed}, 失败 {tests_failed}')
    if tests_failed:
        sys.exit(1)


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        _self_test()
    else:
        main()
