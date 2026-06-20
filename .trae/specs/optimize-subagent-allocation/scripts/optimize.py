#!/usr/bin/env python3
"""Sub-agent 分配速查表生成：每部小说 = 1 个 sub-agent，不拆段，无 KB 列。"""
import re
from pathlib import Path

WS = Path("/workspace/帝王战队621 1：00")
DOCS = WS / "documents"
PKTS = WS / "tmp" / "execution_packets.md"
OUT = DOCS / "sub-agent分配速查表.md"

BATCH_FILES = {
    "01_战队特摄": "pixiv_深度阅读笔记_01_战队特摄.md",
    "02_勇者魔物奇幻": "pixiv_深度阅读笔记_02_勇者魔物奇幻.md",
    "03_正太校园堕落": "pixiv_深度阅读笔记_03_正太校园堕落.md",
    "04_调教拍卖系统流": "pixiv_深度阅读笔记_04调教拍卖+05异种触手.md",
    "05_异种兽化触手": "pixiv_深度阅读笔记_04调教拍卖+05异种触手.md",
    "06_修真玄幻其他": "pixiv_深度阅读笔记_06修真玄幻+07外语.md",
    "07_外语": "pixiv_深度阅读笔记_06修真玄幻+07外语.md",
    "08_同人": "pixiv_深度阅读笔记_08同人+09女性向.md",
    "09_女性向": "pixiv_深度阅读笔记_08同人+09女性向.md",
}


def parse_packets():
    text = PKTS.read_text(encoding="utf-8")
    novels = []
    current_batch = None
    for line in text.splitlines():
        m = re.match(r"^#\s+(\S+)\s+execution packets", line)
        if m:
            current_batch = m.group(1).strip()
            continue
        m = re.match(r"^\|\s*(SA-(\d+))\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*(.+?)\s*\|", line)
        if m:
            sa_full = m.group(1)
            sa = m.group(2)
            title_raw = m.group(3).strip()
            title = re.split(r"\s*/\s*\d+", title_raw)[0].strip()
            chapters = int(m.group(4))
            total_kb = float(m.group(5))
            max_kb = float(m.group(6))
            novel_type = m.group(7).strip()
            novels.append({
                "sa": sa, "batch": current_batch, "title": title,
                "chapters": chapters, "total_kb": total_kb,
                "max_kb": max_kb, "type": novel_type,
            })
    return novels


def batch_to_file(batch):
    return BATCH_FILES.get(batch, "")


def render_md(novels):
    lines = []
    lines.append("# Sub-agent 分配速查表")
    lines.append("")
    lines.append("> **用途**：sub-agent 启动时**单文件速查**，仅做**分配指引**，不约束 AI 输出。  ")
    lines.append("> **执行模式**：方案 1 — 批次内并行写草稿 → 主代理串行合并。详见 `sub-agent输入输出规范.md`。  ")
    lines.append("> **来源**：`tmp/execution_packets.md`（小说元数据）。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. sub-agent 启动 3 步走")
    lines.append("1. **找到自己的 ID**（如 `SA-01-A`）→ 跳到对应小节")
    lines.append("2. **Read 源小说**（路径在本小节每条记录中）")
    lines.append("3. **Write 笔记对应段落**（段落编号 4.X / 5.X）→ 写入目标见各批量开头\"写入目标\"段")
    lines.append("")
    lines.append("> ⚠ 本表**仅做分配**，每本小说的**输出指引（灵活模板）**见 `sub-agent输入输出规范.md`。**纯分配，不约束输出**。")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 按笔记文件分组
    by_file = {}
    for n in novels:
        f = batch_to_file(n["batch"])
        by_file.setdefault(f, []).append(n)

    # 批量总览
    lines.append("## 2. 批量总览")
    lines.append("")
    lines.append("| 批量 | 笔记文件 | 小说数 |")
    lines.append("|---|---|---:|")
    batch_idx_disp = 0
    for f in BATCH_FILES.values():
        items = by_file.get(f, [])
        if not items:
            continue
        batch_idx_disp += 1
        bname = f.replace("pixiv_深度阅读笔记_", "").replace(".md", "")
        lines.append(f"| 批量 {batch_idx_disp} | `{f}` | {len(items)} |")
    lines.append(f"| **合计** | — | **{len(novels)}** |")
    lines.append("")
    lines.append("**所有写入目标路径前缀**：`.trae/specs/expand_xiaoyingxiong_skill_v2/`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 写入位置速查
    lines.append("## 3. 写入位置速查")
    lines.append("")
    lines.append("| 笔记文件 | 4.X 段（超限本独立） | 5.X 段（聚合包） |")
    lines.append("|---|---|---|")
    for f in BATCH_FILES.values():
        items = by_file.get(f, [])
        n4 = sum(1 for x in items if x["type"] == "超限本独立")
        n5 = sum(1 for x in items if x["type"] == "聚合包")
        if items:
            lines.append(f"| `{f}` | {n4} 部 | {n5} 部 |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 每个批量的 sub-agent 列表
    batch_idx = 0
    for f in BATCH_FILES.values():
        items = by_file.get(f, [])
        if not items:
            continue
        batch_idx += 1
        fname = f.replace("pixiv_深度阅读笔记_", "").replace(".md", "")
        lines.append(f"## {3 + batch_idx}. 批量 {batch_idx}：{fname}（{len(items)} sub-agent）")
        lines.append("")
        lines.append("### 写入目标")
        lines.append(f"**`{f}`**")
        lines.append("")

        # 按 type 分组：4=超限本独立，5=聚合包
        for grp, grp_name, grp_label in [("超限本独立", "4", "高分 4.X"), ("聚合包", "5", "中分 5.X")]:
            sub = [x for x in items if x["type"] == grp]
            if not sub:
                continue
            lines.append(f"#### {grp_label}（{grp}，{len(sub)} 部）")
            lines.append("")
            lines.append("| Sub-agent | 作品 | 完整路径 | 章节 | 写入 |")
            lines.append("|---|---|---|---:|---|")
            for i, n in enumerate(sub, 1):
                letter = chr(ord("A") + i - 1)
                # 路径用子目录
                sub_dir = n["batch"]
                path = f"`工作区/pixiv小说/{sub_dir}/{n['title']}/`"
                lines.append(f"| SA-{batch_idx:02d}-{letter} | {n['title']} | {path} | {n['chapters']} | {grp}.{i} |")
            lines.append("")

        lines.append("---")
        lines.append("")

    # 易混淆提示
    lines.append("## X. 同名/相似名 易混淆提示")
    lines.append("")
    lines.append("sub-agent 在 Read 源小说前**务必看清完整路径**，避免读错：")
    lines.append("")
    lines.append("| 易混点 | 区分方式 |")
    lines.append("|---|---|")
    lines.append("| `工作区/pixiv小说/03_正太校园堕落/万圣节，榨鸡鸡/` vs `工作区/pixiv小说/04_调教拍卖系统流/汪仔牛奶/` | 同内容，前者是镜像；统一按 03 路径读 |")
    lines.append("| `工作区/pixiv小说/02_勇者魔物奇幻/当个少年英雄也不赖啊！系列/` vs `工作区/pixiv小说/02_勇者魔物奇幻/洗脑！运动队的少年英雄！系列/` | 同译者奥鲁斯托，**不同作品** |")
    lines.append("| `工作区/pixiv小说/01_战队特摄/超级战士/` vs `工作区/pixiv小说/01_战队特摄/超级战队收集计划/` | **不同作品** |")
    lines.append("| `工作区/pixiv小说/08_同人/血脉掠夺者/` vs `工作区/pixiv小说/08_同人/雨浩成神路/` | 都是斗罗同人，章号不同 |")
    lines.append("| `工作区/pixiv小说/08_同人/妨碍拯救世界的勇者居然是魅魔！/` | 路径在 08，但**原 IP 设定接近 02 勇者** |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## X+1. 完成回报格式")
    lines.append("")
    lines.append("每 sub-agent 完成后，**报告以下信息**给主代理：")
    lines.append("")
    lines.append("```markdown")
    lines.append("## SA-XX-X 完成报告")
    lines.append("- 处理小说：N 部（列出作品名）")
    lines.append("- 实际读取章节：X / Y 章（X% = X/Y 计算得出，目标 100%，但不强制）")
    lines.append("- 写入笔记：pixiv_深度阅读笔记_XX_XXX.md 段落 4.X / 5.X")
    lines.append("- 实际输出字符：~XXXXX（无硬性下限，AI 按内容自由发挥）")
    lines.append("- 异常情况：（如有；如实际读 < 100% 需说明原因）")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## X+2. 速查表 vs 源文档关系")
    lines.append("")
    lines.append("| 文档 | 角色 |")
    lines.append("|---|---|")
    lines.append("| 本速查表（sub-agent 分配速查表） | sub-agent **执行时**查（**仅做分配**） |")
    lines.append("| `工作区/documents/sub-agent输入输出规范.md` | **规划层**（执行模式 + 灵活模板输出指引） |")
    lines.append("| `工作区/tmp/execution_packets.md` | **小说元数据** |")
    lines.append("| `pixiv_深度阅读笔记_*.md`（6 份） | **写入目标** |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("*本表为 2026-06-21 简化版：每部小说 = 1 个 sub-agent，不拆段，不锁大小，AI 按内容自由发挥。*")
    lines.append("")

    return "\n".join(lines)


def main():
    novels = parse_packets()
    print(f"解析到 {len(novels)} 部小说")
    md = render_md(novels)
    OUT.write_text(md, encoding="utf-8")
    print(f"已写入 {OUT}")


if __name__ == "__main__":
    main()
