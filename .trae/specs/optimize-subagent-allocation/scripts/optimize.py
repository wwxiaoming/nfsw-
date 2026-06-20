#!/usr/bin/env python3
"""Sub-agent 分配速查表生成：每部小说 = 1 个 sub-agent，不拆段，无 KB 列。"""
import re
from pathlib import Path

WS = Path("/workspace/帝王战队621 1：00")
DOCS = WS / "documents"
PKTS = WS / "tmp" / "execution_packets.md"
OUT = DOCS / "sub-agent分配速查表.md"

# 6 份笔记文件 + 各自包含的子目录（顺序与渲染一致）
_BATCH_ORDER = [
    ("01", "01_战队特摄",        "pixiv_深度阅读笔记_01_战队特摄.md",                ["01_战队特摄"]),
    ("02", "02_勇者魔物奇幻",     "pixiv_深度阅读笔记_02_勇者魔物奇幻.md",            ["02_勇者魔物奇幻"]),
    ("03", "03_正太校园堕落",     "pixiv_深度阅读笔记_03_正太校园堕落.md",            ["03_正太校园堕落"]),
    ("04", "04调教拍卖+05异种触手","pixiv_深度阅读笔记_04调教拍卖+05异种触手.md",      ["04_调教拍卖系统流", "05_异种兽化触手"]),
    ("05", "06修真玄幻+07外语",   "pixiv_深度阅读笔记_06修真玄幻+07外语.md",          ["06_修真玄幻其他", "07_外语"]),
    ("06", "08同人+09女性向",     "pixiv_深度阅读笔记_08同人+09女性向.md",            ["08_同人", "09_女性向"]),
]

# 子目录 -> 批量号（用于解析小说路径批量归类）
_DIR_TO_BATCH = {}
for batch_num, _disp, _file, dirs in _BATCH_ORDER:
    for d in dirs:
        _DIR_TO_BATCH[d] = batch_num


def parse_packets():
    text = PKTS.read_text(encoding="utf-8")
    novels = []
    current_file = None
    current_dirs = []
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+?)\s+execution packets", line)
        if m:
            raw = m.group(1).strip()
            num_m = re.match(r"^(\d{2})_", raw)
            if num_m:
                num = num_m.group(1)
                for bnum, _d, fname, dirs in _BATCH_ORDER:
                    if dirs and any(d.startswith(num + "_") for d in dirs):
                        current_file = fname
                        current_dirs = dirs
                        break
            continue
        m = re.match(r"^\|\s*(SA-(\d+))\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*(.+?)\s*\|", line)
        if m and current_file:
            sa = m.group(2)
            title_raw = m.group(3).strip()
            title = re.split(r"\s*/\s*\d+", title_raw)[0].strip()
            chapters = int(m.group(4))
            total_kb = float(m.group(5))
            max_kb = float(m.group(6))
            novel_type = m.group(7).strip()
            sub_dir = current_dirs[0]
            novels.append({
                "sa": sa,
                "file": current_file,
                "sub_dir": sub_dir,
                "title": title,
                "chapters": chapters,
                "total_kb": total_kb,
                "max_kb": max_kb,
                "type": novel_type,
            })
    return novels


def render_md(novels):
    L = []
    L.append("# Sub-agent 分配速查表")
    L.append("")
    L.append("> **用途**：sub-agent 启动时**单文件速查**，仅做**分配指引**，不约束 AI 输出。  ")
    L.append("> **执行模式**：方案 1 — 批次内并行写草稿 → 主代理串行合并。详见 `sub-agent输入输出规范.md`。  ")
    L.append("> **来源**：`tmp/execution_packets.md`（小说元数据）。")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 1. sub-agent 启动 3 步走")
    L.append("1. **找到自己的 ID**（如 `SA-01-A`）→ 跳到对应小节")
    L.append("2. **Read 源小说**（路径在本小节每条记录中）")
    L.append("3. **Write 笔记对应段落**（段落编号 4.X / 5.X）→ 写入目标见各批量开头\"写入目标\"段")
    L.append("")
    L.append("> ⚠ 本表**仅做分配**，每本小说的**输出指引（灵活模板）**见 `sub-agent输入输出规范.md`。**纯分配，不约束输出**。")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 1.5 500KB 软上限 & 拆段指引")
    L.append("")
    L.append("> **软上限** = 经验值参考，**不强制**。实测单 sub-agent 上下文能稳定读远超 500KB，但**默认**仍按 500KB 切段，便于并行错峰。")
    L.append("")
    L.append("### 拆段判定（按本表 KB 列判断）")
    L.append("")
    L.append("| 情况 | 处理 |")
    L.append("|---|---|")
    L.append("| 总 KB ≤ 500 | **不拆**，单 sub-agent 直接 Read 全文 |")
    L.append("| 总 KB > 500 **且** 章节数 ≥ 3 | **建议拆 2-3 段**：按章节均分，确保每段 ≤ 500KB |")
    L.append("| 总 KB > 500 **但** 章节数 ≤ 2（单章硬读） | **不拆**，单 sub-agent 一次读完，写一条完整笔记 |")
    L.append("")
    L.append("### 拆段执行方法（建议方案 A）")
    L.append("1. **多 sub-agent 接力**：每段 = 1 个 sub-agent ID（SA-XX-A 读 1-N 章，SA-XX-A' 读 N+1-M 章…），各自写自己段号的草稿")
    L.append("2. **主代理合并**：所有段草稿写完后，主代理按 4.1 / 4.2 / 4.3 ... 顺序串行合并到正式笔记")
    L.append("3. **段号约定**：拆段后 4.X 段号连续（如 4.1=第 1 段，4.2=第 2 段，4.3=第 3 段），不要跳号")
    L.append("")
    L.append("### 注意事项")
    L.append("- **不强拆**：若 AI 评估后可一次读完（如上下文长 + 章节短），可跳过硬切段")
    L.append("- **单章硬读例外**：`SA-03-T 光环 无限` 这种 3 章/单章 > 500KB 的，不切段，直接整本读")
    L.append("- **拆段不拆 ID**：同一小说的多段共用一个 Sub-agent 编号族（SA-XX-A/A'/A''），便于合并时识别")
    L.append("")
    L.append("---")
    L.append("")

    # 按笔记文件分组
    by_file = {}
    for n in novels:
        by_file.setdefault(n["file"], []).append(n)

    # 批量总览
    L.append("## 2. 批量总览")
    L.append("")
    L.append("| 批量 | 笔记文件 | 小说数 |")
    L.append("|---|---|---:|")
    total = 0
    for i, (bnum, disp, fname, _dirs) in enumerate(_BATCH_ORDER, 1):
        items = by_file.get(fname, [])
        if not items:
            continue
        L.append(f"| 批量 {i} | `{fname}` | {len(items)} |")
        total += len(items)
    L.append(f"| **合计** | — | **{total}** |")
    L.append("")
    L.append("**所有写入目标路径前缀**：`.trae/specs/expand_xiaoyingxiong_skill_v2/`")
    L.append("")
    L.append("---")
    L.append("")

    # 写入位置速查
    L.append("## 3. 写入位置速查")
    L.append("")
    L.append("| 笔记文件 | 4.X 段（超限本独立） | 5.X 段（聚合包） |")
    L.append("|---|---|---|")
    for bnum, disp, fname, _dirs in _BATCH_ORDER:
        items = by_file.get(fname, [])
        if not items:
            continue
        n4 = sum(1 for x in items if x["type"] == "超限本独立")
        n5 = sum(1 for x in items if x["type"] == "聚合包")
        L.append(f"| `{fname}` | {n4} 部 | {n5} 部 |")
    L.append("")
    L.append("---")
    L.append("")

    # 每个批量的 sub-agent 列表（按 _BATCH_ORDER 顺序，连续 SA-XX-A/B/C 编号跨 4.X/5.X）
    section_num = 3
    for i, (bnum, disp, fname, _dirs) in enumerate(_BATCH_ORDER, 1):
        items = by_file.get(fname, [])
        if not items:
            continue
        section_num += 1
        items_sorted = sorted(items, key=lambda x: (0 if x["type"] == "超限本独立" else 1, x["sa"]))
        n_total = len(items_sorted)
        L.append(f"## {section_num}. 批量 {i}：{disp}（{n_total} 部 / sub-agent）")
        L.append("")
        L.append("### 写入目标")
        L.append(f"**`{fname}`**")
        L.append("")

        # 连续字母编号（4.X 和 5.X 拼起来 A、B、C...），段号 4.X / 5.X 也连续
        counters = {"4": 0, "5": 0}
        for idx, n in enumerate(items_sorted):
            n["letter"] = chr(ord("A") + idx)
            sec = "4" if n["type"] == "超限本独立" else "5"
            n["section_num"] = sec
            counters[sec] += 1
            n["sub_idx"] = counters[sec]

        # 渲染两个子表
        cur_section = None
        for n in items_sorted:
            sec = n["section_num"]
            if sec != cur_section:
                cur_section = sec
                cnt = counters[sec]
                label = "高分 4.X（超限本独立）" if sec == "4" else "中分 5.X（聚合包）"
                L.append(f"#### {label}（{cnt} 部）")
                L.append("")
                L.append("| Sub-agent | 作品 | 完整路径 | 章节 | 总KB | 最大KB | 写入 |")
                L.append("|---|---|---|---:|---:|---:|---|")
            path = f"`工作区/pixiv小说/{n['sub_dir']}/{n['title']}/`"
            L.append(f"| SA-{i:02d}-{n['letter']} | {n['title']} | {path} | {n['chapters']} | {n['total_kb']} | {n['max_kb']} | {n['section_num']}.{n['sub_idx']} |")
        L.append("")

        L.append("---")
        L.append("")

    # 易混淆提示
    L.append("## X. 同名/相似名 易混淆提示")
    L.append("")
    L.append("sub-agent 在 Read 源小说前**务必看清完整路径**，避免读错：")
    L.append("")
    L.append("| 易混点 | 区分方式 |")
    L.append("|---|---|")
    L.append("| `工作区/pixiv小说/03_正太校园堕落/万圣节，榨鸡鸡/` vs `工作区/pixiv小说/04_调教拍卖系统流/汪仔牛奶/` | 同内容，前者是镜像；统一按 03 路径读 |")
    L.append("| `工作区/pixiv小说/02_勇者魔物奇幻/当个少年英雄也不赖啊！系列/` vs `工作区/pixiv小说/02_勇者魔物奇幻/洗脑！运动队的少年英雄！系列/` | 同译者奥鲁斯托，**不同作品** |")
    L.append("| `工作区/pixiv小说/01_战队特摄/超级战士/` vs `工作区/pixiv小说/01_战队特摄/超级战队收集计划/` | **不同作品** |")
    L.append("| `工作区/pixiv小说/08_同人/血脉掠夺者/` vs `工作区/pixiv小说/08_同人/雨浩成神路/` | 都是斗罗同人，章号不同 |")
    L.append("| `工作区/pixiv小说/08_同人/妨碍拯救世界的勇者居然是魅魔！/` | 路径在 08，但**原 IP 设定接近 02 勇者** |")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## X+1. 完成回报格式")
    L.append("")
    L.append("每 sub-agent 完成后，**报告以下信息**给主代理：")
    L.append("")
    L.append("```markdown")
    L.append("## SA-XX-X 完成报告")
    L.append("- 处理小说：N 部（列出作品名）")
    L.append("- 实际读取章节：X / Y 章（X% = X/Y 计算得出，目标 100%，但不强制）")
    L.append("- 写入笔记：pixiv_深度阅读笔记_XX_XXX.md 段落 4.X / 5.X")
    L.append("- 实际输出字符：~XXXXX（无硬性下限，AI 按内容自由发挥）")
    L.append("- 异常情况：（如有；如实际读 < 100% 需说明原因）")
    L.append("```")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## X+2. 速查表 vs 源文档关系")
    L.append("")
    L.append("| 文档 | 角色 |")
    L.append("|---|---|")
    L.append("| 本速查表（sub-agent 分配速查表） | sub-agent **执行时**查（**仅做分配**） |")
    L.append("| `工作区/documents/sub-agent输入输出规范.md` | **规划层**（执行模式 + 灵活模板输出指引） |")
    L.append("| `工作区/tmp/execution_packets.md` | **小说元数据** |")
    L.append("| `pixiv_深度阅读笔记_*.md`（6 份） | **写入目标** |")
    L.append("")
    L.append("---")
    L.append("")

    L.append("*本表为 2026-06-21 简化版：每部小说默认 1 个 sub-agent，KB 列作软上限参考，单章/小本不强制拆段，AI 按内容自由发挥。*")
    L.append("")

    return "\n".join(L)


def main():
    novels = parse_packets()
    print(f"解析到 {len(novels)} 部小说")
    md = render_md(novels)
    OUT.write_text(md, encoding="utf-8")
    print(f"已写入 {OUT}")


if __name__ == "__main__":
    main()
