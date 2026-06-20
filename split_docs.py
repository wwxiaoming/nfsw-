#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新生成 12 份 sub-agent 交付物（6 批量 × 2 文档）"""
import os
import re
from pathlib import Path

BASE = Path("/workspace/帝王战队621 1：00")
SRC_DIR = BASE / "documents"
OUT_DIR = BASE / "documents" / "sub-agent-deliverables"

# 6 批量定义：(目录名, 批量名中文, sub-agent数, 批量序号, 批量标题行, 源批量标题)
BATCHES = [
    ("batch-01_战队特摄", "战队特摄", "8 sub-agent", 1, "## 4. 批量 1：01_战队特摄（8 sub-agent）", "01_战队特摄"),
    ("batch-02_勇者魔物奇幻", "勇者魔物奇幻", "27 sub-agent", 2, "## 5. 批量 2：02_勇者魔物奇幻（27 sub-agent）", "02_勇者魔物奇幻"),
    ("batch-03_正太校园堕落", "正太校园堕落", "24 sub-agent", 3, "## 6. 批量 3：03_正太校园堕落（24 sub-agent）", "03_正太校园堕落"),
    ("batch-04_调教拍卖+异种触手", "调教拍卖+异种触手", "4 sub-agent", 4, "## 7. 批量 4：04调教拍卖+05异种触手（4 sub-agent）", "04调教拍卖+05异种触手"),
    ("batch-05_修真玄幻+外语", "修真玄幻+外语", "6 sub-agent", 5, "## 8. 批量 5：06修真玄幻+07外语（6 sub-agent）", "06修真玄幻+07外语"),
    ("batch-06_同人+女性向", "同人+女性向", "4 sub-agent", 6, "## 9. 批量 6：08同人+09女性向（4 sub-agent）", "08同人+09女性向"),
]

# 读取 2 份源文档
src_speed = (SRC_DIR / "sub-agent分配速查表.md").read_text(encoding="utf-8")
src_norm = (SRC_DIR / "sub-agent输入输出规范.md").read_text(encoding="utf-8")

# 速查表：找到各批量段的起止行
speed_lines = src_speed.splitlines(keepends=True)
# 找 6 批量标题位置
batch_positions = []
for i, line in enumerate(speed_lines):
    for batch in BATCHES:
        if line.startswith(batch[4] + "\n") or line.strip() == batch[4]:
            batch_positions.append((i, batch))
            break

assert len(batch_positions) == 6, f"找到 {len(batch_positions)} 个批量标题"

# 速查表共用部分（不含批量 X 段）：[0, batch_positions[0][0])
# 速查表尾部（含 X+1/X+2/X+3 段）：batch_positions[5][0] + 该批量内容长度, len]
# 取批量内容（每个批量到下一个批量前一行）
batch_contents = []
for idx, (pos, batch) in enumerate(batch_positions):
    if idx + 1 < len(batch_positions):
        next_pos = batch_positions[idx + 1][0]
    else:
        # 最后一个批量到 X+1 段前
        # 找 X+1 段位置
        for j in range(pos, len(speed_lines)):
            if speed_lines[j].startswith("## X+1."):
                next_pos = j
                break
    batch_contents.append("".join(speed_lines[pos:next_pos]))

# 速查表共用部分
speed_prefix = "".join(speed_lines[:batch_positions[0][0]])
speed_suffix = "".join(speed_lines[batch_positions[5][0] + len(batch_contents[5]):])  # 应该是空，因为 X+1 段已被排除

# 实际上 6 批量段在源文档中是连续的，X+1 段在最后。我们需要 X+1, X+2, X+3 段
# 找 X+1 段位置
x1_pos = None
for i, line in enumerate(speed_lines):
    if line.startswith("## X+1. "):
        x1_pos = i
        break

# 速查表尾部 = speed_lines[x1_pos:]
speed_tail = "".join(speed_lines[x1_pos:])

# 输入输出规范：所有 batch 共享主体（除了标题+头部 batch-specific）
# 主体 = 全文（不含最前的 batch-specific 6 行）
# 实际看，batch-specific 在第 1-6 行（L1-L6），主体从 L7 开始
norm_lines = src_norm.splitlines(keepends=True)
# 找第一个 # Sub-agent 输入输出规范（v5 软上限版）行（即主体标题行）
norm_body_start = None
for i, line in enumerate(norm_lines):
    if line.startswith("# Sub-agent 输入输出规范（v5"):
        norm_body_start = i
        break

# 主体 = norm_lines[norm_body_start:]
norm_body = "".join(norm_lines[norm_body_start:])

# 生成 12 份文件
for batch_dir, batch_name, sub_n, batch_no, batch_title, batch_id in BATCHES:
    out_dir = OUT_DIR / batch_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. 速查表：标题 + 头部 batch-specific + 共用部分 + 该批量内容 + 尾部
    speed_header = (
        f"# Sub-agent 分配速查表 - {batch_name}（{sub_n}）\n"
        f"\n"
        f"> 生成日期：2026-06-21\n"
        f"> 配套：`输入输出规范_{batch_dir}.md`（灵活模板）\n"
        f"> 批量范围：{batch_title}\n"
        f"\n"
    )
    # 共用部分需要移除原文档的"批量范围"行（已在 header 替换）
    # 找共用部分中的"## 1. sub-agent 启动 3 步走"等
    speed_out = speed_header + speed_prefix + batch_contents[batch_no - 1] + speed_tail

    speed_file = out_dir / f"速查表_{batch_dir}.md"
    speed_file.write_text(speed_out, encoding="utf-8")
    print(f"写入: {speed_file} ({len(speed_out.splitlines())} 行)")

    # 2. 输入输出规范：标题 + 头部 batch-specific + 主体
    norm_header = (
        f"# Sub-agent 输入输出规范 - {batch_name}（{sub_n}）\n"
        f"\n"
        f"> 生成日期：2026-06-21\n"
        f"> 配套：`速查表_{batch_dir}.md`（仅做分配）+ `tmp/execution_packets.md`（小说元数据）\n"
        f"> 批量范围：{batch_title}\n"
        f"\n"
    )
    norm_out = norm_header + norm_body

    norm_file = out_dir / f"输入输出规范_{batch_dir}.md"
    norm_file.write_text(norm_out, encoding="utf-8")
    print(f"写入: {norm_file} ({len(norm_out.splitlines())} 行)")

print("\n12 份交付物重新生成完毕")
