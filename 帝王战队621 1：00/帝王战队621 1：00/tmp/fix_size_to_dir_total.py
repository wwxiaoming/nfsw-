#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v3 修复版：按"作品"列精确切分 + 名称归一化匹配。

修复点：
1. 从"作品"列（cell 索引 2）切分，按 + / 、 拆出每个作品名
2. 名称归一化：去 《》「」【】空格
3. 库存名也做归一化；用归一化名做等值匹配
4. 避免子串误匹配：长名优先，再短名
"""
import re
import unicodedata
from pathlib import Path

WS = Path(r"c:\Users\Administrator\Desktop\re\trae文件夹\工作区")
INV = WS / "tmp" / "novel_inventory.md"
SPEC1 = WS / "spec" / "v2-阶段4.1-4.3-逐本通读+笔记实时写入_2026-06-20.md"
SPEC2 = WS / "spec" / "v2-阶段4.1-sub-agent小说速查表_2026-06-20.md"


def norm(s: str) -> str:
    """归一化：去所有空格和书名号"""
    s = s.replace("《", "").replace("》", "")
    s = s.replace("「", "").replace("」", "")
    s = s.replace("【", "").replace("】", "")
    s = s.replace("（", "(").replace("）", ")")
    s = re.sub(r"\s+", "", s)
    return s.strip()


def parse_inventory(path: Path) -> dict:
    """返回 {归一化名: 原始名: 目录总大小KB}"""
    text = path.read_text(encoding="utf-8")
    mapping = {}  # norm_name -> (original_name, total_kb)
    pat = re.compile(
        r"\|\s*\d+\s*\|\s*([^|]+?)\s*\|\s*\d+\s*\|\s*[\d.]+\s*\|\s*([\d.]+)\s*\|"
    )
    for m in pat.finditer(text):
        orig = m.group(1).strip()
        n = norm(orig)
        mapping[n] = (orig, float(m.group(2)))
    return mapping


def split_works(cell: str) -> list:
    """从"作品"列切分出作品名列表。处理 + / 、 / 和 / 等分隔符。"""
    cell = cell.strip()
    # 按 + 或 、 切分
    parts = re.split(r"\s*[+、/／]\s*", cell)
    # 过滤掉 "..." 标记和空
    return [p for p in parts if p and not p.startswith(".")]


def lookup_works(cell: str, mapping: dict) -> list:
    """从"作品"cell 找到所有对应的 (原名, KB)

    严格等值匹配（归一化后）。spec 里写"少年骑士"这种缩名不匹配库存全名，
    会留原行不动，避免误匹到"少年骑士长的恶堕"等。
    """
    result = []
    parts = split_works(cell)
    for p in parts:
        n = norm(p)
        if n in mapping:
            result.append(mapping[n])
        # else: 缩名不匹配，跳过（保持原值）
    return result


def fmt_kb(val: float) -> str:
    if val == int(val):
        return f"{int(val)}KB"
    return f"{val:.1f}KB"


def fix_broken_line(line: str) -> str:
    """修复 "<写入编号> <KB>" 缺 | 的破坏行。"""
    return re.sub(r"(\d+\.\d+)\s+(\d+(?:\.\d+)?KB)", r"\1 | \2", line)


def process_row(line: str, mapping: dict) -> str:
    stripped = line.rstrip("\n")
    if "KB" not in stripped:
        return line
    stripped = fix_broken_line(stripped)
    if not stripped.lstrip().startswith("|"):
        return line

    cells = [c.strip() for c in stripped.strip("|").split("|")]
    if len(cells) < 3:
        return line

    # 找含 KB 的 cell
    kb_indices = [i for i, c in enumerate(cells) if re.search(r"[\d.~]+KB", c)]
    if not kb_indices:
        return line

    # 作品列 = 索引 1（第 2 列）
    works = lookup_works(cells[1], mapping)
    if not works:
        return line

    total = sum(w[1] for w in works)
    new_val = fmt_kb(total)

    for i in kb_indices:
        cells[i] = new_val

    body = " | ".join(cells)
    return "| " + body + " |\n" if line.endswith("\n") else "| " + body + " |"


def process_file(path: Path, mapping: dict) -> int:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    new_lines = [process_row(line, mapping) for line in lines]
    new_text = "".join(new_lines)
    path.write_text(new_text, encoding="utf-8")
    return sum(1 for a, b in zip(lines, new_lines) if a != b)


def main():
    mapping = parse_inventory(INV)
    print(f"[解析] {len(mapping)} 部作品\n")

    n1 = process_file(SPEC1, mapping)
    print(f"[详细版] {SPEC1.name}：修改 {n1} 行")
    n2 = process_file(SPEC2, mapping)
    print(f"[速查表] {SPEC2.name}：修改 {n2} 行")

    # 调试：输出可疑的 0KB / 0.0KB / 原值未变 的位置
    print("\n[核查] 详细版剩余 size < 1KB 的行：")
    for i, line in enumerate(SPEC1.read_text(encoding="utf-8").splitlines(), 1):
        if re.search(r"\|\s*0(?:\.0)?KB\s*\|", line):
            print(f"  L{i}: {line}")


if __name__ == "__main__":
    main()
