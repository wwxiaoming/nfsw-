# -*- coding: utf-8 -*-
"""
extract_lorebook.py (v2)
从 `完整角色卡` 中提取尚未在 `Tavo参考世界书` 中存在的世界书
- chara_card_v3 类型：提取 data.character_book 并转换为标准 Tavo lorebook 格式
  （list -> dict，字段重命名以匹配现有 Za5N/Za5z 等的格式）
- 顶层 entries 类型：直接复制
"""
import json
import os
import shutil
import sys
from pathlib import Path

# 路径
WORK = Path(r'C:\Users\Administrator\Desktop\trae文件夹')
SRC = WORK / 'extracted' / '帝王战队角色卡' / '帝王战队资料' / '完整角色卡'
DST = WORK / 'extracted' / '帝王战队角色卡' / '帝王战队资料' / 'Tavo参考世界书'

# 待提取的 Tavo 角色卡清单
TAVO_CARDS = [
    (1,  'Tavo_魔王城堡迷宫模拟器_ZuTT.json',                  '魔王城堡迷宫模拟器'),
    (2,  'Tavo_勇者养成指南 v5 世界里侧 1_ZuTE.json',           '勇者养成指南 v5 世界里侧 1'),
    (3,  'Tavo_还星余火_ZuUz.json',                            '还星余火'),
    (4,  'Tavo_英雄纪元 淫堕训练师v1.27 MVU 2_ZuZU.json',       '英雄纪元 淫堕训练师v1.27 MVU 2'),
    (5,  'Tavo_西幻魔法世界模拟器_ZuUU.json',                  '西幻魔法世界模拟器'),
    (6,  'Tavo_龙王传说v2.7_ZuTm.json',                        '龙王传说v2.7'),
    (7,  'Tavo_造物主的游乐场_ZuTM.json',                      '造物主的游乐场'),
    (8,  'Tavo_迷宫之主_ZuXs.json',                            '迷宫之主'),
    (9,  'Tavo_男寝怪谈_ZuYQ.json',                            '男寝怪谈'),
    (10, 'Tavo_豚俘-猛男阳具复制系统_ZuUm.json',                '豚俘-猛男阳具复制系统'),
    (11, 'Tavo_瓦罗特_ZuV0.json',                              '瓦罗特'),
    (12, 'Tavo_黄权至上_ZuXG.json',                            '黄权至上'),
    (13, 'Tavo_大华夏天朝东瀛自治区_ZuV7.json',                '大华夏天朝东瀛自治区'),
    (14, 'Tavo_欢迎来到DND_ZuUF.json',                         '欢迎来到DND'),
    (15, 'Tavo_投资性直播_ZuUt.json',                          '投资性直播'),
    (16, 'Tavo_寻道太虚(前端战斗)_ZuUL.json',                  '寻道太虚(前端战斗)'),
    (17, 'Tavo_炽热世界_ZuU9.json',                            '炽热世界'),
    (18, 'Tavo_精牛牧场_ZuZ2.json',                            '精牛牧场'),
    (19, 'Tavo_竹马模拟器_ZuU0.json',                          '竹马模拟器'),
    (20, 'Tavo_综漫世界_ZuUf.json',                            '综漫世界'),
]

# 待提取的非 Tavo 角色卡
OTHER_CARDS = [
    (21, '无声星环.json',                  'WSXH',                       '无声星环'),
    (22, '男子高中.json',                  '男子高中',                   '男子高中'),
    (23, '转盘抽奖调教模拟器.json',        '转轮抽奖调教模拟器',         '转盘抽奖调教模拟器'),
]

# 待复制的独立世界书
STANDALONE = [
    '青港市世界书.json',
    '黄油XP百科全书 (1).json',
    'BDSM道具 2025.2.2 (1).json',
]


def build_tavo_lorebook_name(card_name: str, cb_name: str, ex_nn: int) -> str:
    if not cb_name or cb_name == card_name:
        suffix = card_name
    else:
        suffix = cb_name
    return f"Tavo_{card_name}'s Lorebook ({suffix})_Ex{ex_nn:02d}.json"


def build_other_lorebook_name(card_name: str, cb_name: str, ex_nn: int) -> str:
    if not cb_name or cb_name == card_name:
        suffix = card_name
    else:
        suffix = cb_name
    return f"{card_name}'s Lorebook ({suffix})_Ex{ex_nn:02d}.json"


def convert_entry(src: dict) -> dict:
    """将 SillyTavern character_book entry（list 中的 item）转换为标准 Tavo lorebook entry 格式。
    字段映射：id→uid, enabled→disable(取反), keys→key, insertion_order→order,
              extensions 字典展平并重命名 key_case 为 camelCase。
    """
    if not isinstance(src, dict):
        return {}
    ext = src.get('extensions', {}) if isinstance(src.get('extensions', {}), dict) else {}

    def gv(key, default=None):
        """Get value from src first, then ext, then default."""
        if key in src and src[key] is not None:
            return src[key]
        if key in ext and ext[key] is not None:
            return ext[key]
        return default

    enabled = src.get('enabled', True)
    if enabled is None:
        enabled = True

    out = {
        'uid': src.get('id', 0),
        'disable': not bool(enabled),
        'use_regex': bool(src.get('use_regex', False)),
        'name': src.get('name', '') or src.get('comment', '') or '',
        'comment': src.get('comment', '') or src.get('name', '') or '',
        'content': src.get('content', '') or '',
        'constant': bool(src.get('constant', False)),
        'vectorized': bool(gv('vectorized', False)),
        'position': _to_int_pos(gv('position', 0), 0),
        'depth': int(gv('depth', 4) or 4),
        'role': int(gv('role', 0) or 0),
        'key': src.get('keys', []) or src.get('key', []) or [],
        'keysecondary': src.get('secondary_keys', []) or src.get('keysecondary', []) or [],
        'selective': bool(src.get('selective', True)),
        'selectiveLogic': int(gv('selectiveLogic', 0) or 0),
        'caseSensitive': bool(gv('case_sensitive', False)),
        'matchWholeWords': bool(gv('match_whole_words', False)),
        'scanDepth': _to_int(gv('scan_depth', 4), 4),
        'useGroupScoring': bool(gv('use_group_scoring', False)),
        'excludeRecursion': bool(gv('exclude_recursion', False)),
        'preventRecursion': bool(gv('prevent_recursion', False)),
        'delayUntilRecursion': bool(gv('delay_until_recursion', False)),
        'useProbability': bool(gv('useProbability', True)),
        'probability': int(gv('probability', 100) or 100),
        'sticky': int(gv('sticky', 0) or 0),
        'cooldown': int(gv('cooldown', 0) or 0),
        'delay': int(gv('delay', 0) or 0),
        'group': str(gv('group', '') or ''),
        'groupOverride': bool(gv('group_override', False)),
        'groupWeight': int(gv('group_weight', 100) or 100),
        'display_index': int(src.get('display_index', src.get('insertion_order', 0)) or 0),
        'order': int(src.get('insertion_order', 100) or 100),
    }
    return out


# position 字段可能是字符串（'before_char' / 'after_char' / 'at_depth' / 'system'）或整数
_POSITION_MAP = {
    'before': 0, 'before_char': 0,
    'after': 1, 'after_char': 1,
    'at_depth': 2,
    'system': 4, 'sys': 4,
    'author_note': 2, 'extension': 2,
}


def _to_int_pos(v, default):
    """Convert position to int, supporting string enum values."""
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        if v in _POSITION_MAP:
            return _POSITION_MAP[v]
        try:
            return int(v)
        except (ValueError, TypeError):
            return default
    return default


def _to_int(v, default):
    """Convert to int, returning default on failure."""
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        try:
            return int(v)
        except (ValueError, TypeError):
            return default
    return default


def convert_entries(entries) -> dict:
    """将 source character_book entries（list 或 dict）转换为 uid-keyed dict"""
    if isinstance(entries, list):
        result = {}
        for i, e in enumerate(entries):
            if not isinstance(e, dict):
                continue
            converted = convert_entry(e)
            uid = converted.get('uid')
            # 若 uid 重复或为 None，用 index 兜底
            if uid is None or str(uid) in result:
                uid = i
            result[str(uid)] = converted
        return result
    elif isinstance(entries, dict):
        # 已是 dict，仅做 entry 内部转换
        return {k: convert_entry(v) for k, v in entries.items() if isinstance(v, dict)}
    return {}


def extract_from_chara_card(src_path: Path, out_path: Path) -> tuple[bool, int, str]:
    with open(src_path, 'r', encoding='utf-8') as f:
        obj = json.load(f)
    if not isinstance(obj, dict) or obj.get('spec') != 'chara_card_v3':
        return False, 0, 'not chara_card_v3'
    cb = obj.get('data', {}).get('character_book')
    if not isinstance(cb, dict):
        return False, 0, 'no character_book'
    src_entries = cb.get('entries', {})
    cb_name = cb.get('name', '')

    converted_entries = convert_entries(src_entries)

    out_obj = {
        'tavo_spec': 'lorebook',
        'tavo_spec_version': 2,
        'name': cb_name,
        'entries': converted_entries,
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=2)
    return True, len(converted_entries), cb_name


def main():
    print(f'SRC = {SRC}')
    print(f'DST = {DST}')
    print()

    dst_existing = set()
    for p in DST.rglob('*.json'):
        if p.is_file():
            dst_existing.add(p.name)

    # 1) Tavo
    print('=== [1/3] 提取 Tavo 角色卡世界书 ===')
    extract_ok = extract_skip = extract_fail = 0
    for ex_nn, src_name, card_name in TAVO_CARDS:
        src_path = SRC / src_name
        if not src_path.exists():
            print(f'  [FAIL] 源文件不存在: {src_name}')
            extract_fail += 1
            continue
        try:
            with open(src_path, 'r', encoding='utf-8') as f:
                obj = json.load(f)
            cb = obj.get('data', {}).get('character_book', {})
            cb_name = cb.get('name', '') if isinstance(cb, dict) else ''
        except Exception as e:
            print(f'  [FAIL] 解析失败: {src_name} -> {e}')
            extract_fail += 1
            continue

        out_name = build_tavo_lorebook_name(card_name, cb_name, ex_nn)
        out_path = DST / out_name
        if out_path.name in dst_existing:
            print(f'  [SKIP] 已存在: {out_name}')
            extract_skip += 1
            continue
        try:
            ok, n, name = extract_from_chara_card(src_path, out_path)
            if ok:
                print(f'  [OK]   {out_name}  (entries={n}, cb.name={name})')
                extract_ok += 1
            else:
                print(f'  [FAIL] 提取失败: {src_name} -> {name}')
                extract_fail += 1
        except Exception as e:
            print(f'  [FAIL] 写入失败: {out_name} -> {e}')
            extract_fail += 1

    # 2) 非 Tavo
    print()
    print('=== [2/3] 提取非 Tavo 角色卡世界书 ===')
    other_ok = other_skip = other_fail = 0
    for ex_nn, src_name, cb_name, card_name in OTHER_CARDS:
        src_path = SRC / src_name
        if not src_path.exists():
            print(f'  [FAIL] 源文件不存在: {src_name}')
            other_fail += 1
            continue
        out_name = build_other_lorebook_name(card_name, cb_name, ex_nn)
        out_path = DST / out_name
        if out_path.name in dst_existing:
            print(f'  [SKIP] 已存在: {out_name}')
            other_skip += 1
            continue
        try:
            ok, n, name = extract_from_chara_card(src_path, out_path)
            if ok:
                print(f'  [OK]   {out_name}  (entries={n}, cb.name={name})')
                other_ok += 1
            else:
                print(f'  [FAIL] 提取失败: {src_name} -> {name}')
                other_fail += 1
        except Exception as e:
            print(f'  [FAIL] 写入失败: {out_name} -> {e}')
            other_fail += 1

    # 3) 复制
    print()
    print('=== [3/3] 复制独立世界书 ===')
    copy_ok = copy_skip = 0
    for fn in STANDALONE:
        src_path = SRC / fn
        dst_path = DST / fn
        if not src_path.exists():
            print(f'  [FAIL] 源文件不存在: {fn}')
            continue
        if dst_path.exists():
            print(f'  [SKIP] 目标已存在: {fn}')
            copy_skip += 1
            continue
        try:
            shutil.copy2(src_path, dst_path)
            print(f'  [OK]   {fn}')
            copy_ok += 1
        except Exception as e:
            print(f'  [FAIL] 复制失败: {fn} -> {e}')

    print()
    print('=== 总结 ===')
    print(f'  Tavo 提取:   ok={extract_ok}, skip={extract_skip}, fail={extract_fail}')
    print(f'  非Tavo 提取: ok={other_ok}, skip={other_skip}, fail={other_fail}')
    print(f'  独立世界书:  ok={copy_ok}, skip={copy_skip}')
    print(f'  本次新增总数: {extract_ok + other_ok + copy_ok}')


if __name__ == '__main__':
    main()
