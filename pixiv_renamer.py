#!/usr/bin/env python3
"""
pixiv_renamer.py — 按 作品信息.txt 标准化 pixiv_workspace/ 下章节文件名
策略:
  1. 优先按 文件 raw_title 与 作品信息 entry 标题 的规范化形式做精确/子串匹配
  2. 匹配不到时回退到 #N == 作品信息 顺序(降序 → 文件 #1 = 最早发布 = 作品信息最后一条)
  3. 仍匹配不到 → 原样保留
  4. 同名冲突 → 按 作品id 升序追加 (2)/(3)...
  5. Windows 非法字符清洗
用法: python3 pixiv_renamer.py [--dry-run]
"""
import argparse
import hashlib
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SRC_ROOT = Path("/workspace/pixiv_workspace")
DST_ROOT = Path("/workspace/pixiv_renamed")
REPORT_PATH = DST_ROOT / "rename_report.md"

# Windows 非法字符 + 控制字符
WIN_ILLEGAL_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

# 作品信息 块分隔：=== N. 标题 ===
BLOCK_HEADER_RE = re.compile(r'^===\s*(\d+)\s*[.、]?\s*(.+?)\s*===\s*$')

# #N 标题.txt
NUMBERED_RE = re.compile(r'^#(\d+)\s+(.+)\.txt$')

# 用于去除的标点（匹配时不计）
_PUNCT_RE = re.compile(
    r'[\s\u3000'                                  # 空白（含全角空格）
    r'《》「」『』“”"\'‘’'                          # 书名号/引号
    r'()()（）【】\[\]<>《》、'                        # 括号
    r'。.,，;:：!！?？—\-_~～·•…&＋+&'                # 标点
    r']'
)


def normalize_for_match(s: str) -> str:
    """去标点空白后的规范化串，用于模糊匹配"""
    s = unicodedata.normalize("NFKC", s)
    s = _PUNCT_RE.sub('', s)
    return s.lower()


def safe_filename(name: str) -> str:
    """清洗 Windows 非法字符；首尾 . 空白去掉"""
    name = WIN_ILLEGAL_RE.sub('', name)
    name = name.rstrip().lstrip()
    name = name.strip(' .')
    return name


def parse_work_info(text: str) -> List[dict]:
    """
    解析 作品信息.txt 文本
    返回按"顺序"升序的列表: [{order, title, work_id, created_at}, ...]
    顺序 1 = 最新一条（作品信息中按时间倒序排列）
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
                'raw_header_title': header_title,
            }
            continue
        if current is None:
            continue
        line_stripped = line.strip()
        if line_stripped.startswith('标题：') or line_stripped.startswith('标题:'):
            current['title'] = line_stripped.split('：', 1)[-1].split(':', 1)[-1].strip()
        elif line_stripped.startswith('作品id：') or line_stripped.startswith('作品id:') or line_stripped.startswith('作品ID：'):
            current['work_id'] = line_stripped.split('：', 1)[-1].split(':', 1)[-1].strip()
        elif line_stripped.startswith('创建时间：') or line_stripped.startswith('创建时间:'):
            current['created_at'] = line_stripped.split('：', 1)[-1].split(':', 1)[-1].strip()
    if current:
        entries.append(current)
    return entries


def find_work_info_files(root: Path) -> Dict[str, Path]:
    result = {}
    for p in root.rglob("作品信息.txt"):
        rel_dir = p.parent.relative_to(root)
        result[str(rel_dir)] = p
    return result


def build_work_info_index(root: Path) -> Tuple[Dict, List, Dict]:
    """
    返回:
      - work_index: {
          作品目录: {
            'entries': [按 order 升序],
            'by_order': {order: entry},
            'by_work_id': {work_id: entry},
            'normalized_titles': {norm_title: entry},  # 规范化后唯一
            'empty': bool,
            'used_work_ids': set,
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
            work_index[rel_dir] = {
                'entries': [],
                'by_order': {},
                'by_work_id': {},
                'normalized_titles': {},
                'empty': True,
                'used_work_ids': set(),
            }
            continue
        entries.sort(key=lambda e: e['order'])
        by_order = {e['order']: e for e in entries}
        by_work_id = {e['work_id']: e for e in entries if e.get('work_id')}
        normalized_titles = {}
        for e in entries:
            nt = normalize_for_match(e['title'])
            if nt and nt not in normalized_titles:
                normalized_titles[nt] = e
        work_index[rel_dir] = {
            'entries': entries,
            'by_order': by_order,
            'by_work_id': by_work_id,
            'normalized_titles': normalized_titles,
            'empty': False,
            'used_work_ids': set(),
        }

    for rel_dir in all_dirs:
        if rel_dir not in work_index and rel_dir != '.':
            empty_dirs.append(rel_dir)
            work_index[rel_dir] = {
                'entries': [],
                'by_order': {},
                'by_work_id': {},
                'normalized_titles': {},
                'empty': True,
                'used_work_ids': set(),
            }

    return work_index, empty_dirs, parse_errors


def fuzzy_match_title(raw_title: str, work_dir_info: dict) -> Optional[dict]:
    """在 work_dir_info 中按规范化标题找精确匹配或最长公共子串匹配"""
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


def match_file_to_entry(raw_title: str, file_n: Optional[int], work_dir_info: dict) -> Tuple[Optional[dict], str]:
    """
    核心匹配函数。返回 (entry, method)。
    优先级:
      1) raw_title 规范化精确匹配 → title_exact
      2) raw_title 规范化子串匹配 → title_substring
      3) file_n 序号对齐:
         - file_n == order#X → 假设 #1 = 最早发布 = order #max → order_match
         - 但因为方向不确定,这里提供两条候选,选唯一的那一边
      4) 无 → None
    """
    nt = normalize_for_match(raw_title)
    norm_titles = work_dir_info['normalized_titles']

    # 1) 精确
    if nt in norm_titles:
        return norm_titles[nt], 'title_exact'

    # 2) 子串
    substring_candidates = []
    for norm_t, entry in norm_titles.items():
        if nt in norm_t or norm_t in nt:
            substring_candidates.append((norm_t, entry))
    if len(substring_candidates) == 1:
        return substring_candidates[0][1], 'title_substring'
    if len(substring_candidates) > 1:
        # 多候选,选最长的（更具体）
        best = max(substring_candidates, key=lambda x: len(x[0]))
        return best[1], 'title_substring'

    # 3) 序号匹配 — 由于 作品信息 顺序=降序(最新先) 而 文件#N 顺序=故事顺序,
    #    它们的方向可能一致也可能相反。两种都试,看哪个能让所有文件都唯一命中。
    #    简化策略: file_n=1 → 作品信息 顺序=K(最后一条=最早发布)
    #    这对绝大多数情况成立;但有些作者(比如上面 深渊之役)会让 #1 = 最新发布
    #    = 作品信息 顺序=1。先按 "反向" 试,如冲突再用 "正向"。
    if file_n is not None and work_dir_info['by_order']:
        max_order = max(work_dir_info['by_order'].keys())
        if file_n <= max_order:
            # 反向映射候选
            reverse_candidate = work_dir_info['by_order'].get(max_order - file_n + 1)
            forward_candidate = work_dir_info['by_order'].get(file_n)
            # 我们已经走到这里说明 title 没匹配,优先用反向(最常见)
            if reverse_candidate and reverse_candidate['work_id'] not in work_dir_info['used_work_ids']:
                return reverse_candidate, 'order_reverse'
            if forward_candidate and forward_candidate['work_id'] not in work_dir_info['used_work_ids']:
                return forward_candidate, 'order_forward'

    return None, 'no_match'


def plan_renames(root: Path) -> Tuple[List[dict], dict]:
    work_index, empty_dirs, parse_errors = build_work_info_index(root)
    plan = []
    stats = {
        'total_files': 0,
        'info_files': 0,
        'numbered': 0,
        'title_exact': 0,
        'title_substring': 0,
        'order_reverse': 0,
        'order_forward': 0,
        'no_match_kept': 0,
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
        # 在该目录下累积已使用的新文件名（用于冲突检测）
        used_new_names_count: Dict[str, int] = defaultdict(int)

        for src in files:
            old_name = src.name
            rel_src = str(src.relative_to(root))

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
                    'title': None,
                })
                continue

            if src.stat().st_size == 0:
                stats['skipped_empty'] += 1
                plan.append({
                    'src': src,
                    'rel_src': rel_src,
                    'work_dir': rel_dir,
                    'old_name': old_name,
                    'new_name': old_name,
                    'action': 'skipped_empty',
                    'note': '0字节文件，原样保留',
                    'work_id': None,
                    'title': None,
                })
                stats['manual_review'].append({'rel': rel_src, 'reason': 'zip 中 0 字节文件'})
                continue

            # 检测是否 #N 文件
            m = NUMBERED_RE.match(old_name)
            file_n = int(m.group(1)) if m else None
            raw_title = m.group(2).strip() if m else (old_name[:-4] if old_name.endswith('.txt') else old_name)
            if m:
                stats['numbered'] += 1

            matched_entry = None
            match_method = None

            if info and not info['empty']:
                matched_entry, match_method = match_file_to_entry(raw_title, file_n, info)
                if matched_entry and matched_entry.get('work_id'):
                    info['used_work_ids'].add(matched_entry['work_id'])

            if matched_entry is None:
                # 无匹配 — 原样保留
                if file_n is not None:
                    stats['no_match_kept'] += 1
                    note = '无匹配，保留原 #N 文件名（去前缀尝试）'
                    new_name = raw_title + '.txt' if raw_title else old_name
                    action = 'no_match_kept'
                else:
                    stats['untouched'] += 1
                    note = '无 #N 前缀且 作品信息 无匹配'
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
                    'title': raw_title,
                })

                if info and info['empty']:
                    stats['manual_review'].append({
                        'rel': rel_dir + '/',
                        'reason': '作品信息缺失或为空',
                    })
                elif matched_entry is None and file_n is not None and info and not info['empty']:
                    stats['manual_review'].append({
                        'rel': rel_src,
                        'reason': f'#N 文件 {raw_title!r} 无法匹配 作品信息 中任何标题',
                    })
                continue

            # 命中 — 统计
            if match_method == 'title_exact':
                stats['title_exact'] += 1
            elif match_method == 'title_substring':
                stats['title_substring'] += 1
            elif match_method == 'order_reverse':
                stats['order_reverse'] += 1
                stats['manual_review'].append({
                    'rel': rel_src,
                    'reason': f'标题无匹配，按 #{file_n} 倒序对齐到 作品信息 第{(max(info["by_order"].keys()) - file_n + 1) if info["by_order"] else "?"} 条',
                })
            elif match_method == 'order_forward':
                stats['order_forward'] += 1
                stats['manual_review'].append({
                    'rel': rel_src,
                    'reason': f'标题无匹配，按 #{file_n} 顺序对齐到 作品信息 第{file_n} 条',
                })

            # 生成新文件名
            title = matched_entry['title'].strip()
            new_name = title + '.txt'

            base = new_name
            if new_name in used_new_names_count:
                used_new_names_count[new_name] += 1
                stem = base[:-4]
                new_name = f"{stem} ({used_new_names_count[new_name]}).txt"
                stats['conflicts_resolved'] += 1
                stats['manual_review'].append({
                    'rel': rel_src,
                    'reason': f'同目录命名冲突：{base!r} 已存在，自动追加 ({used_new_names_count[new_name]})',
                })
            else:
                used_new_names_count[base] = 1

            cleaned = safe_filename(new_name[:-4]) + '.txt' if new_name.endswith('.txt') else safe_filename(new_name)
            if cleaned != new_name:
                stats['manual_review'].append({
                    'rel': rel_src,
                    'reason': f'Windows 非法字符被清洗：{new_name!r} → {cleaned!r}',
                })
                new_name = cleaned
            if new_name == '.txt' or new_name == '':
                new_name = '__untitled__.txt'
                stats['manual_review'].append({
                    'rel': rel_src,
                    'reason': '清洗后文件名为空，使用 __untitled__ 占位',
                })

            plan.append({
                'src': src,
                'rel_src': rel_src,
                'work_dir': rel_dir,
                'old_name': old_name,
                'new_name': new_name,
                'action': 'renamed',
                'note': match_method,
                'work_id': matched_entry.get('work_id'),
                'title': title,
            })

    return plan, stats


def execute_plan(plan: List[dict], dry_run: bool = False) -> int:
    if not dry_run:
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


def write_report(plan: List[dict], stats: dict, dry_run: bool) -> None:
    lines = []
    lines.append('# Pixiv 章节文件重命名报告')
    lines.append('')
    if dry_run:
        lines.append('> **DRY-RUN 模式** — 下方计划未实际执行')
        lines.append('')
    lines.append('## 总览')
    lines.append('')
    lines.append(f'- 扫描 .txt 文件总数：**{stats["total_files"]}**')
    lines.append(f'- 作品信息.txt 数：**{stats["info_files"]}**')
    lines.append(f'- `#N` 编号章节文件：**{stats["numbered"]}**')
    lines.append(f'- 按标题规范化精确匹配重命名：**{stats["title_exact"]}**')
    lines.append(f'- 按标题规范化子串匹配重命名：**{stats["title_substring"]}**')
    lines.append(f'- 按序号倒序（#1=最早）回退重命名：**{stats["order_reverse"]}**')
    lines.append(f'- 按序号顺序（#1=最新）回退重命名：**{stats["order_forward"]}**')
    lines.append(f'- 无匹配，原 #N 文件保留（去前缀）：**{stats["no_match_kept"]}**')
    lines.append(f'- 无 `#N` 前缀且无匹配（untouched）：**{stats["untouched"]}**')
    lines.append(f'- 0 字节文件跳过：**{stats["skipped_empty"]}**')
    lines.append(f'- 命名冲突自动追加 `(2)/(3)`：**{stats["conflicts_resolved"]}**')
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
        lines.append('| 旧文件名 | 新文件名 | 匹配方式 | 作品 ID |')
        lines.append('| --- | --- | --- | --- |')
        for p in sorted(items, key=lambda x: x['old_name']):
            old = p['old_name'].replace('|', '\\|')
            new = p['new_name'].replace('|', '\\|')
            method = p.get('note', '') or p.get('action', '')
            wid = p.get('work_id') or '-'
            lines.append(f'| `{old}` | `{new}` | {method} | {wid} |')
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


def main():
    global SRC_ROOT, DST_ROOT, REPORT_PATH
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='只生成计划，不实际复制')
    ap.add_argument('--src', default=str(SRC_ROOT))
    ap.add_argument('--dst', default=str(DST_ROOT))
    args = ap.parse_args()

    SRC_ROOT = Path(args.src)
    DST_ROOT = Path(args.dst)
    REPORT_PATH = DST_ROOT / 'rename_report.md'

    print(f'[1/3] 解析 {SRC_ROOT} ...')
    plan, stats = plan_renames(SRC_ROOT)
    print(f'      共 {stats["total_files"]} 个文件, 其中 {stats["numbered"]} 个 #N 文件, {stats["info_files"]} 个 作品信息')
    print(f'[2/3] {"DRY-RUN 预览" if args.dry_run else "复制到 " + str(DST_ROOT)} ...')
    copied = execute_plan(plan, dry_run=args.dry_run)
    print(f'      已处理 {copied} 个文件')
    print(f'[3/3] 写入报告 {REPORT_PATH} ...')
    write_report(plan, stats, dry_run=args.dry_run)
    print('完成。')
    print()
    print('--- 总览 ---')
    for k, v in stats.items():
        if k == 'manual_review':
            print(f'  {k}: {len(v)} 条')
        else:
            print(f'  {k}: {v}')


if __name__ == '__main__':
    main()
