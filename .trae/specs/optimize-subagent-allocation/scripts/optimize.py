#!/usr/bin/env python3
"""Sub-agent 分配优化脚本：拆分超限本、装箱 sub-agent、生成新速查表。"""
import json
import os
import re
from pathlib import Path

WS = Path("/workspace/帝王战队621 1：00")
DOCS = WS / "documents"
PKTS = WS / "tmp" / "execution_packets.md"
OUT = DOCS / "sub-agent分配速查表.md"
OLD = DOCS / "v2-阶段4.1-sub-agent小说速查表_2026-06-20.md"

HARD_LIMIT = 500.0

BATCH_FILES = {
    "01_战队特摄": "pixiv_深度阅读笔记_01_战队特摄.md",
    "02_勇者魔物奇幻": "pixiv_深度阅读笔记_02_勇者魔物奇幻.md",
    "03_正太校园堕落": "pixiv_深度阅读笔记_03_正太校园堕落.md",
    "04+05_调教+异种": "pixiv_深度阅读笔记_04调教拍卖+05异种触手.md",
    "06+07_修真+外语": "pixiv_深度阅读笔记_06修真玄幻+07外语.md",
    "08+09_同人+女性向": "pixiv_深度阅读笔记_08同人+09女性向.md",
}

OVER_LIMIT_NOVELS = {
    "《豪想和你在一起》": "02_勇者魔物奇幻",
    "裆能战记系列": "01_战队特摄",
    "魔王的勇者们": "02_勇者魔物奇幻",
    "光环 无限": "08_同人",
    "勇装戦士 ブレイブレンジャー": "07_外语",
    "圣兽战士": "05_异种兽化触手",
    "奥鲁斯托的少年英雄小说（连载中）": "02_勇者魔物奇幻",
    "魔法世界": "06_修真玄幻其他",
    "乱七八糟的文都在这": "05_异种兽化触手",
    "正太胶囊公司": "03_正太校园堕落",
    "奴隶调教中心": "09_女性向",
    "关于被诅咒变成正太这件事": "03_正太校园堕落",
    "搾精生物から生き残れ！": "07_外语",
    "高弹紧身衣战士白曜": "01_战队特摄",
    "印第安部落之歌正传（更新中）": "02_勇者魔物奇幻",
    "天启者联盟": "02_勇者魔物奇幻",
}


def _char_min(novel):
    chapters = novel.get("chapters", 1)
    if chapters >= 75:
        return 80000
    if chapters >= 30:
        return 40000
    return 15000


def get_chapter_sizes(novel_dir_name):
    pixiv = WS / "pixiv小说"
    base = None
    for c in pixiv.iterdir():
        if c.is_dir() and (c / novel_dir_name).is_dir():
            base = c / novel_dir_name
            break
    if not base:
        return []
    items = []
    idx = 0
    for f in sorted(base.iterdir()):
        if not f.is_file() or not f.name.endswith(".txt"):
            continue
        if f.name.startswith("作品信息"):
            continue
        idx += 1
        items.append((idx, f.name, f.stat().st_size))
    return items


def greedy_split(chapters, limit=HARD_LIMIT):
    segs = []
    cur = []
    cur_kb = 0.0
    for idx, name, sz in chapters:
        kb = sz / 1024.0
        if cur and cur_kb + kb > limit:
            segs.append((cur[0][0], cur[-1][0], cur_kb))
            cur = []
            cur_kb = 0.0
        cur.append((idx, name, sz))
        cur_kb += kb
    if cur:
        segs.append((cur[0][0], cur[-1][0], cur_kb))
    return segs


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
            # title 可能带 " / X 章 / Y / Z" 后缀，去掉
            title = re.split(r"\s*/\s*\d+", title_raw)[0].strip()
            # 标题内可能含 "+" 表示多本聚合，取主标题（第一个"+"前）
            chapters = int(m.group(4))
            total_kb = float(m.group(5))
            max_kb = float(m.group(6))
            novel_type = m.group(7).strip()
            novels.append({
                "sa": sa, "batch": current_batch, "title": title,
                "chapters": chapters, "total_kb": total_kb,
                "max_kb": max_kb, "type": novel_type,
                "title_raw": title_raw,
            })
    return novels


def batch_to_file(batch):
    m = {
        "01_战队特摄": BATCH_FILES["01_战队特摄"],
        "02_勇者魔物奇幻": BATCH_FILES["02_勇者魔物奇幻"],
        "03_正太校园堕落": BATCH_FILES["03_正太校园堕落"],
        "04_调教拍卖系统流": BATCH_FILES["04+05_调教+异种"],
        "05_异种兽化触手": BATCH_FILES["04+05_调教+异种"],
        "06_修真玄幻其他": BATCH_FILES["06+07_修真+外语"],
        "07_外语": BATCH_FILES["06+07_修真+外语"],
        "08_同人": BATCH_FILES["08+09_同人+女性向"],
        "09_女性向": BATCH_FILES["08+09_同人+女性向"],
    }
    return m.get(batch, "")


def render_md(agents):
    lines = []
    lines.append("# Sub-agent 分配速查表（500KB 硬约束版）")
    lines.append("")
    lines.append("> **用途**：sub-agent 启动时**单文件速查**，仅做**分配指引**，不约束 AI 输出字数。  ")
    lines.append("> **核心硬约束**：每个 sub-agent 分配的源小说**总大小 ≤ 500KB**（实测单次 Read 上限）。  ")
    lines.append("> **来源**：")
    lines.append("> - `tmp/execution_packets.md`（77 部小说 + 章节 + 总大小清单）")
    lines.append("> - 各小说目录的实际章节文件字节数（贪心装箱）")
    lines.append("> - `v2-阶段4.1-4.3-逐本通读+笔记实时写入_2026-06-20.md`（规划层）")
    lines.append("> - 实测：500KB 稳定 / 600KB 截断（2026-06-20）")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. sub-agent 启动 3 步走")
    lines.append("1. **找到自己的 ID**（如 `SA-01-A`）→ 跳到对应小节")
    lines.append("2. **Read 源小说**（路径在本小节每条记录中）→ 单段 ≤500KB 直接读；超 500KB 的子段用 `offset`/`limit` 分段")
    lines.append("3. **Write 笔记对应段落**（段落编号 4.X / 5.X）→ 写入目标见各批量开头\"写入目标\"段")
    lines.append("")
    lines.append("> ⚠ 本表**仅做分配**，每本小说的**输出指引（灵活模板）**见规划文档 `v2-阶段4.1-4.3-...`。**无字符下限、无必含项硬指标**——AI 按作品实际自由发挥。")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 2. 批量总览")
    lines.append("")
    lines.append("| 批量 | 笔记文件 | sub-agent 数 | 分配单元数 |")
    lines.append("|---|---|---:|---:|")
    file_groups = {}
    for a in agents:
        file_groups.setdefault(a["file"], []).append(a)
    batch_idx_disp = 0
    total_units_all = 0
    for bf, ags in file_groups.items():
        batch_idx_disp += 1
        ags.sort(key=lambda a: (a["grp"], a["seq"][0] if a["seq"] else ""))
        bname = bf.replace("pixiv_深度阅读笔记_", "").replace(".md", "")
        units = sum(len(a['items']) for a in ags)
        total_units_all += units
        lines.append(f"| 批量 {batch_idx_disp} | `{bf}` | {len(ags)} | {units} |")
    total_agents = len(agents)
    lines.append(f"| **合计** | — | **{total_agents}** | **{total_units_all}** |")
    lines.append("")
    lines.append("**所有写入目标路径前缀**：`.trae/specs/expand_xiaoyingxiong_skill_v2/`")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 3. 写入位置速查")
    lines.append("")
    lines.append("| 笔记文件 | 4.X 段（高分 / 超限本独立） | 5.X 段（中分 / 聚合包） | 6.X 段（低分） |")
    lines.append("|---|---|---|---|")
    for f in BATCH_FILES.values():
        g4 = [a for a in agents if a["file"] == f and a["grp"] == "4"]
        g5 = [a for a in agents if a["file"] == f and a["grp"] == "5"]
        n4 = sum(len(a["items"]) for a in g4)
        n5 = sum(len(a["items"]) for a in g5)
        if n4 or n5:
            lines.append(f"| `{f}` | {n4} 子段 | {n5} 子段 | — |")
    lines.append("")
    lines.append("---")
    lines.append("")

    batch_idx = 0
    for f in BATCH_FILES.values():
        ags = [a for a in agents if a["file"] == f]
        if not ags:
            continue
        batch_idx += 1
        fname = f.replace("pixiv_深度阅读笔记_", "").replace(".md", "")
        lines.append(f"## {3 + batch_idx}. 批量 {batch_idx}：{fname}（{len(ags)} sub-agent）")
        lines.append("")
        n4 = sum(len(a["items"]) for a in ags if a["grp"] == "4")
        n5 = sum(len(a["items"]) for a in ags if a["grp"] == "5")
        lines.append("### 写入目标")
        lines.append(f"**`{f}`**")
        if n4:
            lines.append(f"- 4.X 段（高分 / 超限本独立，共 {n4} 部 / 子段）")
        if n5:
            lines.append(f"- 5.X 段（中分 / 聚合包，共 {n5} 部 / 子段）")
        lines.append("")

        ags.sort(key=lambda a: (a["grp"], a["seq"][0] if a["seq"] else ""))
        for a_idx, a in enumerate(ags):
            letter = chr(ord("A") + a_idx)
            has_seg = any(s["is_segment"] for s in a["items"])
            titles = sorted({s["title"] for s in a["items"]})
            title_summary = " + ".join(titles[:2])
            if len(titles) > 2:
                title_summary += f" + 等 {len(titles)} 部"
            seg_note = "（含超限本子段）" if has_seg else ""
            lines.append(f"### SA-{batch_idx:02d}-{letter}：《{title_summary}》{seg_note}")
            lines.append("")
            lines.append("| # | 作品 | 完整路径 | 章节 | KB | 实际读 X/Y | 写入 |")
            lines.append("|---:|---|---|---:|---:|---|---|")
            for i, (s, seq) in enumerate(zip(a["items"], a["seq"]), 1):
                sub = s["path_sub"]
                title = s["title"]
                if s["is_segment"]:
                    path = f"`工作区/pixiv小说/{sub}/{title}/`（子段 {s['seg_idx']}/{s['seg_cnt']}：第 {s['ch_start']}-{s['ch_end']} 章）"
                else:
                    path = f"`工作区/pixiv小说/{sub}/{title}/`"
                if s["is_segment"]:
                    ch_disp = f"{s['ch_start']}-{s['ch_end']}（共 {s['ch_end']-s['ch_start']+1}）"
                else:
                    ch_disp = str(s["chapters"])
                kb_disp = f"{s['kb']:.1f}"
                if s["is_segment"]:
                    actual = f"{s['ch_end']-s['ch_start']+1}/{s['ch_end']-s['ch_start']+1} (100%)"
                else:
                    actual = f"{s['chapters']}/{s['chapters']} (100%)"
                write = f"{seq}"
                seg_tag = f"（子段 {s['seg_idx']}/{s['seg_cnt']}）" if s["is_segment"] else ""
                lines.append(f"| {i} | {title}{seg_tag} | {path} | {ch_disp} | {kb_disp} | {actual} | {write} |")
            if a['total_kb'] > HARD_LIMIT:
                lines.append(f"- **本 sub-agent 总大小**：{a['total_kb']:.1f} KB（**单章硬读** ⚠，单章节文件 > 500KB 无法再拆分，sub-agent 需直接 Read 全文，注意上下文溢出风险）")
            else:
                lines.append(f"- **本 sub-agent 总大小**：{a['total_kb']:.1f} KB（硬约束 ≤ 500KB ✓）")
            if has_seg:
                lines.append("- **特别说明**：含超限本子段，已按章节大小预拆分，sub-agent 直接读子段路径")
            lines.append("")

        lines.append("---")
        lines.append("")

    lines.append("## X. 同名/相似名 易混淆提示（来自 _整理报告 §13）")
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

    lines.append("## X+1. 大文件读取提示（避免上下文溢出）")
    lines.append("")
    lines.append("对超长篇（>30 章）或大体积文件（实测 >300KB）使用 `Read` 工具的 `offset` + `limit` 分段读取：")
    lines.append("")
    lines.append("```python")
    lines.append("# 示例：分 3 段读《豪想和你在一起》76 章（约 450KB）")
    lines.append("Read(file_path=path, limit=2000, offset=0)   # 第 1 段")
    lines.append("Read(file_path=path, limit=2000, offset=2000) # 第 2 段")
    lines.append("Read(file_path=path, limit=2000, offset=4000) # 第 3 段")
    lines.append("```")
    lines.append("")
    lines.append("**本版硬约束**（替代原文档 §13 的 500KB 软上限）：")
    lines.append("- **每 sub-agent 总大小 ≤ 500KB**：本速查表已按此硬约束装箱")
    lines.append("- **单部 >500KB 的小说已预先拆段**：按章节大小贪心分给多个 sub-agent")
    lines.append("- **子段内 ≤ 500KB**：直接 Read 全文即可，无需再分段")
    lines.append("- **分段策略**（仅用于子段内仍有 > 500KB 章节文件）：")
    lines.append("  - 75+ 章：3-4 段（按 500KB/段拆分）")
    lines.append("  - 30-50 章：2-3 段")
    lines.append("  - 10-30 章：1-2 段")
    lines.append("  - <10 章：直接读全文")
    lines.append("  - **硬上限**：单次读取 ≤ 500KB，超过必须拆分")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## X+2. 完成回报格式")
    lines.append("")
    lines.append("每 sub-agent 完成后，**报告以下信息**给主代理：")
    lines.append("")
    lines.append("```markdown")
    lines.append("## SA-XX-X 完成报告")
    lines.append("- 处理小说：N 部（列出作品名 + 子段号）")
    lines.append("- 实际读取章节：X / Y 章（X% = X/Y 计算得出，目标 100%，但不强制）")
    lines.append("- 写入笔记：pixiv_深度阅读笔记_XX_XXX.md 段落 4.X / 5.X")
    lines.append("- 实际输出字符：~XXXXX（无硬性下限，AI 按内容自由发挥）")
    lines.append("- 分段信息：（如有；大文件需说明分段策略）")
    lines.append("- 异常情况：（如有；如实际读 < 100% 需说明原因）")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## X+3. 速查表 vs 源文档关系")
    lines.append("")
    lines.append("| 文档 | 角色 |")
    lines.append("|---|---|")
    lines.append("| 本速查表（sub-agent 分配速查表） | sub-agent **执行时**查（**仅做分配**） |")
    lines.append("| `工作区/pixiv小说/_整理报告.md` | **索引层**（按子类+权重分类） |")
    lines.append("| `工作区/documents/v2-阶段4.1-4.3-逐本通读+笔记实时写入_2026-06-20.md` | **规划层**（含每本小说灵活模板输出指引） |")
    lines.append("| `工作区/tmp/execution_packets.md` | **小说元数据**（77 部 + 章节 + 大小） |")
    lines.append("| `pixiv_深度阅读笔记_*.md`（6 份） | **写入目标** |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## X+4. 实测边界说明（2026-06-20）")
    lines.append("")
    lines.append("| 测试项 | 结果 | 结论 |")
    lines.append("|---|---|---|")
    lines.append("| 200KB 文件阅读 | ✅ 2709 行，100% 读完 | 稳定通过 |")
    lines.append("| 400KB 文件阅读 | ✅ 5119 行，100% 读完 | 稳定通过 |")
    lines.append("| 500KB 文件阅读 | ✅ 8680 行，100% 读完 | **稳定上限** |")
    lines.append("| 600KB 文件阅读 | ❌ 只读 513 行（5.6%） | 上下文截断 |")
    lines.append("| 800KB NIAH（0%/25%/50%/75%/100%） | ✅ 全部命中 | 分段后可用 |")
    lines.append("| 800KB 完整阅读 | ❌ 被子代理拒绝 | 不可行 |")
    lines.append("")
    lines.append("**本规划基于上述实测结果制定，500KB 为单次读取硬上限，所有大文件必须拆分后执行。**")
    lines.append("")
    lines.append("**2026-06-21 优化**：本速查表已在 sub-agent 层面强制 ≤500KB 硬约束，16 部超限本已按章节大小贪心拆段，无需 sub-agent 自行判断。**输出字数不限，由规划文档的灵活模板指引**。")
    lines.append("")

    return "\n".join(lines)


def main():
    novels = parse_packets()
    print(f"解析到 {len(novels)} 部小说")

    segments = []
    for n in novels:
        title = n["title"]
        if title in OVER_LIMIT_NOVELS:
            sub = OVER_LIMIT_NOVELS[title]
            chapters = get_chapter_sizes(title)
            if not chapters:
                avg = n["total_kb"] / max(n["chapters"], 1)
                chapters = [(i, f"chapter_{i}", int(avg * 1024)) for i in range(1, n["chapters"] + 1)]
            actual_total = sum(c[2] for c in chapters) / 1024.0
            if actual_total < n["total_kb"] * 0.95 and actual_total > 0:
                scale = n["total_kb"] / actual_total
                chapters = [(i, nm, int(sz * scale)) for i, nm, sz in chapters]
            # 单章节且单章 > 500KB：不拆分，硬读
            if len(chapters) <= 1:
                kb = chapters[0][2] / 1024.0 if chapters else n["total_kb"]
                splits = [(chapters[0][0] if chapters else 1, chapters[-1][0] if chapters else n["chapters"], kb)]
            else:
                splits = greedy_split(chapters, HARD_LIMIT)
            for i, (s, e, kb) in enumerate(splits, 1):
                segments.append({
                    "title": title, "seg_idx": i, "seg_cnt": len(splits),
                    "ch_start": s, "ch_end": e, "kb": kb,
                    "chapters": n["chapters"], "total_kb": n["total_kb"],
                    "type": n["type"], "batch": n["batch"],
                    "path_sub": sub, "is_segment": True, "sa": n["sa"],
                })
        else:
            segments.append({
                "title": title, "seg_idx": 0, "seg_cnt": 0,
                "ch_start": 1, "ch_end": n["chapters"], "kb": n["total_kb"],
                "chapters": n["chapters"], "total_kb": n["total_kb"],
                "type": n["type"], "batch": n["batch"],
                "path_sub": n["batch"], "is_segment": False, "sa": n["sa"],
            })

    groups = {}
    for s in segments:
        f = batch_to_file(s["path_sub"])
        grp = "4" if s["type"] == "超限本独立" else "5"
        groups.setdefault((f, grp), []).append(s)

    agents = []
    for f in BATCH_FILES.values():
        for grp in ["4", "5"]:
            segs = groups.get((f, grp), [])
            segs.sort(key=lambda s: -s["kb"])
            cur = []
            cur_kb = 0.0
            for s in segs:
                if cur and cur_kb + s["kb"] > HARD_LIMIT:
                    agents.append({"file": f, "grp": grp, "items": cur, "total_kb": cur_kb})
                    cur = []
                    cur_kb = 0.0
                cur.append(s)
                cur_kb += s["kb"]
            if cur:
                agents.append({"file": f, "grp": grp, "items": cur, "total_kb": cur_kb})

    for a in agents:
        a["items"].sort(key=lambda s: (s.get("sa", "999"), s["ch_start"]))
        a["seq"] = [f"{a['grp']}.{i+1}" for i in range(len(a["items"]))]

    md = render_md(agents)
    OUT.write_text(md, encoding="utf-8")
    print(f"已写入 {OUT}，sub-agent 总数: {len(agents)}")
    over = [a for a in agents if a["total_kb"] > HARD_LIMIT]
    print(f"超 500KB 的 sub-agent 数: {len(over)}")
    for a in over:
        print(f"  - {a['file']} {a['grp']}X: {a['total_kb']:.1f}KB, {len(a['items'])} 部")
    if OLD.exists():
        OLD.unlink()
        print(f"已删除旧文件 {OLD}")
    # 同时删除 v2-阶段4.1-sub-agent小说速查表_多本聚合版_2026-06-20.md
    old2 = DOCS / "v2-阶段4.1-sub-agent小说速查表_多本聚合版_2026-06-20.md"
    if old2.exists():
        # 保留旧文件，不删
        pass


if __name__ == "__main__":
    main()
