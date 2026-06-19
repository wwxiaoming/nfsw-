# -*- coding: utf-8 -*-
"""
verify_lorebook.py
验证 extract_lorebook.py 的输出：
- 26 个新文件存在
- 每个文件可解析为标准 Tavo lorebook
- entries 数量与源一致（对 chara_card 源）
"""
import json
from pathlib import Path

WORK = Path(r'C:\Users\Administrator\Desktop\trae文件夹')
SRC = WORK / 'extracted' / '帝王战队角色卡' / '帝王战队资料' / '完整角色卡'
DST = WORK / 'extracted' / '帝王战队角色卡' / '帝王战队资料' / 'Tavo参考世界书'

# 期望的新增文件 + 期望的源条目数（extract 验证用）
NEW_FILES = [
    # (新文件名, 源文件或None, 期望条目数 或 None)
    # Ex01-Ex20
    ("Tavo_魔王城堡迷宫模拟器's Lorebook (魔王城堡迷宫模拟器)_Ex01.json",
     'Tavo_魔王城堡迷宫模拟器_ZuTT.json', 181),
    ("Tavo_勇者养成指南 v5 世界里侧 1's Lorebook (-- 四叶草编年史v3)_Ex02.json",
     'Tavo_勇者养成指南 v5 世界里侧 1_ZuTE.json', 101),
    ("Tavo_还星余火's Lorebook (- 还星余火-)_Ex03.json",
     'Tavo_还星余火_ZuUz.json', 65),
    ("Tavo_英雄纪元 淫堕训练师v1.27 MVU 2's Lorebook (淫乱小英雄v1.27-mvu)_Ex04.json",
     'Tavo_英雄纪元 淫堕训练师v1.27 MVU 2_ZuZU.json', 38),
    ("Tavo_西幻魔法世界模拟器's Lorebook (西幻魔法调教模拟器)_Ex05.json",
     'Tavo_西幻魔法世界模拟器_ZuUU.json', 38),
    ("Tavo_龙王传说v2.7's Lorebook (龙王传说v2.7)_Ex06.json",
     'Tavo_龙王传说v2.7_ZuTm.json', 38),
    ("Tavo_造物主的游乐场's Lorebook (- 造物主指南)_Ex07.json",
     'Tavo_造物主的游乐场_ZuTM.json', 32),
    ("Tavo_迷宫之主's Lorebook (- 迷宫之主)_Ex08.json",
     'Tavo_迷宫之主_ZuXs.json', 25),
    ("Tavo_男寝怪谈's Lorebook (淫靡校园)_Ex09.json",
     'Tavo_男寝怪谈_ZuYQ.json', 23),
    ("Tavo_豚俘-猛男阳具复制系统's Lorebook (豚俘-猛男阳具复制系统)_Ex10.json",
     'Tavo_豚俘-猛男阳具复制系统_ZuUm.json', 22),
    ("Tavo_瓦罗特's Lorebook (熊)_Ex11.json",
     'Tavo_瓦罗特_ZuV0.json', 20),
    ("Tavo_黄权至上's Lorebook (- 黄权委员会)_Ex12.json",
     'Tavo_黄权至上_ZuXG.json', 16),
    ("Tavo_大华夏天朝东瀛自治区's Lorebook (隼_Worldbooks)_Ex13.json",
     'Tavo_大华夏天朝东瀛自治区_ZuV7.json', 14),
    ("Tavo_欢迎来到DND's Lorebook (DND)_Ex14.json",
     'Tavo_欢迎来到DND_ZuUF.json', 14),
    ("Tavo_投资性直播's Lorebook (主播主播,你是谁)_Ex15.json",
     'Tavo_投资性直播_ZuUt.json', 13),
    ("Tavo_寻道太虚(前端战斗)'s Lorebook (- 寻道太虚-Worldbooks -)_Ex16.json",
     'Tavo_寻道太虚(前端战斗)_ZuUL.json', 11),
    ("Tavo_炽热世界's Lorebook (炽热世界)_Ex17.json",
     'Tavo_炽热世界_ZuU9.json', 10),
    ("Tavo_精牛牧场's Lorebook (精牛牧场)_Ex18.json",
     'Tavo_精牛牧场_ZuZ2.json', 10),
    ("Tavo_竹马模拟器's Lorebook (崇明第一中学)_Ex19.json",
     'Tavo_竹马模拟器_ZuU0.json', 8),
    ("Tavo_综漫世界's Lorebook (综漫世界)_Ex20.json",
     'Tavo_综漫世界_ZuUf.json', 5),
    # Ex21-Ex23
    ("无声星环's Lorebook (WSXH)_Ex21.json", '无声星环.json', 607),
    ("男子高中's Lorebook (男子高中)_Ex22.json", '男子高中.json', 44),
    ("转盘抽奖调教模拟器's Lorebook (转轮抽奖调教模拟器)_Ex23.json", '转盘抽奖调教模拟器.json', 111),
    # 复制
    ('青港市世界书.json', '青港市世界书.json', None),
    ('黄油XP百科全书 (1).json', '黄油XP百科全书 (1).json', None),
    ('BDSM道具 2025.2.2 (1).json', 'BDSM道具 2025.2.2 (1).json', None),
]


def main():
    fail = 0
    ok = 0
    print('=== 验证 26 个新文件 ===')
    for out_name, src_name, expected_entries in NEW_FILES:
        out_path = DST / out_name
        if not out_path.exists():
            print(f'  [MISS]  {out_name}')
            fail += 1
            continue
        try:
            with open(out_path, 'r', encoding='utf-8') as f:
                obj = json.load(f)
        except Exception as e:
            print(f'  [PARSE_FAIL] {out_name} -> {e}')
            fail += 1
            continue
        # 验证是标准 Tavo lorebook（独立复制的世界书可能无 tavo_spec，标记为 KNOWN_STANDALONE）
        if out_name in ('青港市世界书.json', '黄油XP百科全书 (1).json', 'BDSM道具 2025.2.2 (1).json'):
            # 独立世界书原文件，无 tavo_spec 字段
            pass
        elif obj.get('tavo_spec') != 'lorebook':
            print(f'  [BAD_SPEC] {out_name} tavo_spec != lorebook')
            fail += 1
            continue
        if 'entries' not in obj:
            print(f'  [NO_ENTRIES] {out_name}')
            fail += 1
            continue
        # 验证条目数（entries 可能是 dict 或 list）
        entries = obj['entries']
        if isinstance(entries, dict):
            actual_n = len(entries)
            iter_entries = entries.values()
        elif isinstance(entries, list):
            actual_n = len(entries)
            iter_entries = entries
        else:
            print(f'  [BAD_ENTRIES_TYPE] {out_name} type={type(entries).__name__}')
            fail += 1
            continue
        if expected_entries is not None and actual_n != expected_entries:
            print(f'  [ENTRY_MISMATCH] {out_name} expected={expected_entries} actual={actual_n}')
            fail += 1
            continue
        # 至少一条 content 非空
        has_content = any(
            isinstance(e, dict) and e.get('content', '').strip()
            for e in iter_entries
        )
        if not has_content:
            print(f'  [EMPTY_CONTENT] {out_name}')
            fail += 1
            continue
        print(f'  [OK] {out_name}  entries={actual_n}')
        ok += 1

    print()
    print(f'  ok={ok}, fail={fail}, total={len(NEW_FILES)}')
    return fail == 0


if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
