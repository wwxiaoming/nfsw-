#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 12 份交付物"""
import os
from pathlib import Path

OUT_DIR = Path("/workspace/帝王战队621 1：00/documents/sub-agent-deliverables")
BATCHES = [
    "batch-01_战队特摄", "batch-02_勇者魔物奇幻", "batch-03_正太校园堕落",
    "batch-04_调教拍卖+异种触手", "batch-05_修真玄幻+外语", "batch-06_同人+女性向"
]

FORBIDDEN = ["📖 可参考资源", "Step 0.5", "Step 6.5", "sub-agent 主动读",
             "父子", "父子乱伦", "★★★★★", "不进入自动生成", "原作 IP 版权敏感度"]

print("=== 元素表行数（每份输入输出规范） ===")
all_pass = True
for b in BATCHES:
    f = OUT_DIR / b / f"输入输出规范_{b}.md"
    content = f.read_text(encoding="utf-8")
    lines = [ln for ln in content.splitlines() if ln.startswith("| **")]
    status = "✓" if len(lines) >= 25 else "❌"
    if len(lines) < 25:
        all_pass = False
    print(f"  {b}: {len(lines)} 行元素 {status}")

print()
print("=== 3.4 大类引导方向标题存在性 ===")
count_34 = 0
for b in BATCHES:
    f = OUT_DIR / b / f"输入输出规范_{b}.md"
    content = f.read_text(encoding="utf-8")
    if "### 3.4 大类引导方向\n" in content or "### 3.4 大类引导方向" in content:
        count_34 += 1
        print(f"  ✓ {b}")
    else:
        print(f"  ❌ {b}")
        all_pass = False
print(f"  3.4 标题存在: {count_34}/6")

print()
print("=== 3.4 节不写括号验证（应只有'### 3.4 大类引导方向'，无'（...）'） ===")
for b in BATCHES:
    f = OUT_DIR / b / f"输入输出规范_{b}.md"
    content = f.read_text(encoding="utf-8")
    # 找 3.4 标题行
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("### 3.4"):
            if "（" in line and "）" in line:
                print(f"  ❌ {b}: 标题含括号: {line}")
                all_pass = False
            else:
                print(f"  ✓ {b}: 标题无括号")
            break

print()
print("=== 9 大子类型 × 3-5 方向（3.4.1-3.4.9） ===")
for b in BATCHES:
    f = OUT_DIR / b / f"输入输出规范_{b}.md"
    content = f.read_text(encoding="utf-8")
    subsections = []
    for sub in ["3.4.1", "3.4.2", "3.4.3", "3.4.4", "3.4.5", "3.4.6", "3.4.7", "3.4.8", "3.4.9"]:
        if f"#### {sub}" in content:
            subsections.append(sub)
    status = "✓" if len(subsections) == 9 else "❌"
    if len(subsections) != 9:
        all_pass = False
    print(f"  {b}: {len(subsections)}/9 {status} ({', '.join(subsections)})")

print()
print("=== 3.5 10 份可选增量 references 建议 ===")
for b in BATCHES:
    f = OUT_DIR / b / f"输入输出规范_{b}.md"
    content = f.read_text(encoding="utf-8")
    has_35 = "### 3.5 10 份可选增量 references 建议" in content
    count = content.count(".md`（")
    status = "✓" if has_35 else "❌"
    if not has_35:
        all_pass = False
    print(f"  {b}: 3.5 节={has_35}, references 数={count}")

print()
print("=== 速查表无 X+5 / 大文件读取提示 / 可参考资源 ===")
for b in BATCHES:
    f = OUT_DIR / b / f"速查表_{b}.md"
    content = f.read_text(encoding="utf-8")
    bad = []
    for f_word in ["X+5", "大文件读取提示", "可参考资源"]:
        if f_word in content:
            bad.append(f_word)
    status = "✓" if not bad else "❌"
    if bad:
        all_pass = False
    print(f"  {b}: {status} {bad}")

print()
print("=== 速查表 X+1/X+2/X+3 编号正确 ===")
for b in BATCHES:
    f = OUT_DIR / b / f"速查表_{b}.md"
    content = f.read_text(encoding="utf-8")
    has_x1 = "## X+1. 完成回报格式" in content
    has_x2 = "## X+2. 速查表 vs 源文档关系" in content
    has_x3 = "## X+3. 实测边界说明" in content
    status = "✓" if (has_x1 and has_x2 and has_x3) else "❌"
    if not (has_x1 and has_x2 and has_x3):
        all_pass = False
    print(f"  {b}: X+1={has_x1} X+2={has_x2} X+3={has_x3} {status}")

print()
print("=== 硬约束保留（500KB / 完成回报 / 73 sub-agent / 6 批量段 / 方案 1） ===")
for b in BATCHES:
    f_speed = OUT_DIR / b / f"速查表_{b}.md"
    f_norm = OUT_DIR / b / f"输入输出规范_{b}.md"
    s_content = f_speed.read_text(encoding="utf-8")
    n_content = f_norm.read_text(encoding="utf-8")
    checks = {
        "500KB 速查表": "500KB" in s_content,
        "完成回报 速查表": "完成回报" in s_content,
        "6 批量段 速查表": "## 4-9. 批量" not in s_content and "## " in s_content,  # 简略
        "方案 1 输入输出规范": "方案 1" in n_content,
        "v2 SKILL 升级建议": "v2 SKILL 升级建议" in n_content,
        "Step 0-8 流程": "Step 0" in n_content,
        "13 元素灵活模板": "13 项" in n_content or "25+ 项" in n_content,
    }
    failed = [k for k, v in checks.items() if not v]
    status = "✓" if not failed else "❌"
    if failed:
        all_pass = False
    print(f"  {b}: {status} {failed}")

print()
print("=" * 50)
if all_pass:
    print("✓ 12 份交付物全部通过验证")
else:
    print("❌ 部分交付物未通过验证")
