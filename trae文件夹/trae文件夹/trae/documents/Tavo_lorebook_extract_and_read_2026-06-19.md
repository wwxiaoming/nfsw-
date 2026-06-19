# Tavo 参考世界书 · 提取 + 编号阅读文档 计划

> 目标：先把 `完整角色卡` 里尚未在 `Tavo参考世界书` 中存在的世界书全部抽出来（标准 Tavo lorebook 格式），再把整理后的 `Tavo参考世界书` 按文件大小加序号、简单阅读，产出一份总览 Markdown 文档。**剧情文档的撰写留到下一步执行。**

---

## Phase 0 · 当前状态分析（已确认）

### 0.1 完整角色卡 目录（38 个 .json）
| 类别 | 数量 | 说明 |
|---|---|---|
| Tavo_* 角色卡（内嵌 `data.character_book`） | 33 | 需提取其世界书 |
| 非 Tavo 角色卡（内嵌 `data.character_book`） | 3 | 无声星环/男子高中/转盘抽奖调教模拟器，需提取 |
| 已是独立世界书（顶层 `entries`） | 3 | 青港市世界书/黄油XP百科全书/BDSM道具，需复制 |

**Tavo 角色卡的可提取世界书条目数（按从大到小）：**

| 序号 | 角色卡 | 条目数 | 现有 Tavo参考世界书 是否已覆盖 |
|---|---|---|---|
| 1 | 命定之诗与黄昏之歌v4.2 | 431 | ✓ 已存在 |
| 2 | 《道渊》v5.1 | 285 | ✓ 已存在 |
| 3 | 魔王城堡迷宫模拟器 | 181 | ✗ 待提取 |
| 4 | 异能英雄调教模拟器 | 171 | ✓ 已存在 |
| 5 | 勇者养成指南 v5 世界里侧 1 | 101 | ✗ 待提取（注：现有的是 v1） |
| 6 | 还星余火 | 65 | ✗ 待提取 |
| 7 | 小英雄 | 52 | ✓ 已存在 |
| 8 | 衡江高中 | 52 | ✓ 已存在 |
| 9 | 英雄纪元 淫堕训练师v1.27 MVU 2 | 38 | ✗ 待提取（注：现有的是 MVU 非 MVU 2） |
| 10 | 西幻魔法世界模拟器 | 38 | ✗ 待提取 |
| 11 | 龙王传说v2.7 | 38 | ✗ 待提取 |
| 12 | 造物主的游乐场 | 32 | ✗ 待提取 |
| 13 | 迷宫之主 | 25 | ✗ 待提取 |
| 14 | 男寝怪谈 | 23 | ✗ 待提取 |
| 15 | 豚俘-猛男阳具复制系统 | 22 | ✗ 待提取 |
| 16 | 瓦罗特 | 20 | ✗ 待提取 |
| 17 | 异血 | 19 | ✓ 已存在 |
| 18 | 正太坐忘道 | 19 | ✓ 已存在 |
| 19 | 乳胶系统 | 17 | ✓ 已存在 |
| 20 | 黄权至上 | 16 | ✗ 待提取 |
| 21 | 大华夏天朝东瀛自治区 | 14 | ✗ 待提取 |
| 22 | 欢迎来到DND | 14 | ✗ 待提取 |
| 23 | 隐秘直播间 | 8 | ✓ 已存在 |
| 24 | 《关于我穿越到异世界重生为魔王…》 | 13 | ✓ 已存在 |
| 25 | 投资性直播 | 13 | ✗ 待提取 |
| 26 | 寻道太虚(前端战斗) | 11 | ✗ 待提取 |
| 27 | 炽热世界 | 10 | ✗ 待提取 |
| 28 | 精牛牧场 | 10 | ✗ 待提取 |
| 29 | 竹马模拟器 | 8 | ✗ 待提取 |
| 30 | 穿梭不同世界只为和正太完成任务？ | 5 | ✓ 已存在 |
| 31 | 综漫世界 | 5 | ✗ 待提取 |
| 32 | 英雄命运 | 26 | ✓ 已存在 |
| 33 | 男色：中古战锤 - 异世降临沙盒 | 6 | ✓ 已存在 |

> 共 **20 个 Tavo 角色卡** 需要新增提取。**3 个非 Tavo 角色卡**也需要提取（无声星环 607 条 / 男子高中 44 条 / 转盘抽奖调教模拟器 111 条）。

### 0.2 Tavo参考世界书 目录（27 文件，共 5.46MB）
- 22 个 Tavo_<name>'s Lorebook...json（已存在 Tavo 角色卡对应世界书）
- 2 个 `写卡助手/写卡助手/*.json`（辅助工具）
- 1 个 `咒术回战_数据库剧情推进v4.8.json`（特殊）
- 1 个 `精能大陆(小光).txt`（特殊文本）
- 1 个 `Tavo_英雄纪元 淫堕训练师v1.27 MVU_T4Ki.json`（实为整张角色卡含世界书）

### 0.3 命名 / 格式约定
- 现有标准格式：`{"tavo_spec":"lorebook","tavo_spec_version":2,"name":"...","entries":{"<uid>":{...}}}`
- 单条 entry 必备字段：`uid / key / keysecondary / comment / content / constant / selective / position / order / disable / use_regex / probability / ...`
- 现有文件命名：`Tavo_<源角色卡名>'s Lorebook (<cb.name>)_<4字符ID>.json`
- 例：`Tavo_《道渊》v5.1's Lorebook (道友先上我断后)_Za5N.json`

---

## Phase 1 · 任务 A：从 `完整角色卡` 提取新世界书

### A.1 输出目录
`C:\Users\Administrator\Desktop\trae文件夹\extracted\帝王战队角色卡\帝王战队资料\Tavo参考世界书\`

### A.2 文件命名规则
- **Tavo 角色卡** → `Tavo_<源角色名>'s Lorebook (<cb.name>)_Ex<NN>.json`
  - `<NN>`：01~20，顺序按上表"待提取"列表
  - 例：`Tavo_魔王城堡迷宫模拟器's Lorebook (魔王城堡迷宫模拟器)_Ex01.json`
- **非 Tavo 角色卡** → `<源角色名>'s Lorebook (<cb.name>)_Ex<NN>.json`（无 Tavo_ 前缀）
  - 例：`无声星环's Lorebook (WSXH)_Ex21.json`
  - 男子高中 → Ex22，转盘抽奖调教模拟器 → Ex23
- **3 份独立世界书复制** → 保留原文件名
  - `青港市世界书.json` / `黄油XP百科全书 (1).json` / `BDSM道具 2025.2.2 (1).json`

### A.3 输出 JSON 格式（标准 Tavo lorebook）
```json
{
  "tavo_spec": "lorebook",
  "tavo_spec_version": 2,
  "name": "<cb.name 或 文件名>",
  "entries": {
    "<uid>": {
      "uid": <原值>,
      "key": ["...", "..."],
      "keysecondary": [...],
      "comment": "...",
      "content": "...",
      "constant": false,
      "selective": true,
      "selectiveLogic": 0,
      "use_regex": false,
      "position": 0,
      "order": 100,
      "disable": false,
      "probability": 100,
      "useProbability": true,
      "depth": 4,
      "group": "",
      "scanDepth": null,
      "caseSensitive": false,
      "matchWholeWords": false,
      "automationId": "",
      "role": 0,
      "sticky": 0,
      "cooldown": 0,
      "delay": 0,
      "vectorized": false,
      "excludeRecursion": false,
      "preventRecursion": false,
      "delayUntilRecursion": false,
      "addMemo": true,
      "displayIndex": <原值>
    }
  }
}
```
> 原 `data.character_book.entries` 全部字段按原样保留，仅把 `entries` 从 `data.character_book` 提升到顶层 + 补 `tavo_spec/tavo_spec_version/name`。

### A.4 执行步骤
1. 在工作目录 `C:\Users\Administrator\Desktop\trae文件夹\` 新建临时脚本 `extract_lorebook.py`
2. 脚本流程：
   - 加载 `完整角色卡` 下每个 .json
   - 若顶层是 `chara_card_v3` 且 `data.character_book` 存在 → 提取并按 A.2 命名落盘
   - 若顶层是 `entries`（独立世界书）→ 直接复制到 `Tavo参考世界书`
   - 输出控制台日志：每个文件"已提取"/"已跳过(已存在)"/"无 character_book"
3. 跑完后删除临时脚本（可选保留，作为可复现脚本）
4. 验证：列出 `Tavo参考世界书` 全部 .json，统计新增数 = 20(Tavo) + 3(非Tavo) + 3(复制) = **26 个新文件**

### A.5 涉及文件清单（23 个待提取 + 3 个待复制）

| # | 来源 | 操作 | 输出文件名 |
|---|---|---|---|
| 1 | Tavo_魔王城堡迷宫模拟器_ZuTT.json | extract | Tavo_魔王城堡迷宫模拟器's Lorebook (魔王城堡迷宫模拟器)_Ex01.json |
| 2 | Tavo_勇者养成指南 v5 世界里侧 1_ZuTE.json | extract | Tavo_勇者养成指南 v5 世界里侧 1's Lorebook (勇者养成指南 v5 世界里侧 1)_Ex02.json |
| 3 | Tavo_还星余火_ZuUz.json | extract | Tavo_还星余火's Lorebook (还星余火)_Ex03.json |
| 4 | Tavo_英雄纪元 淫堕训练师v1.27 MVU 2_ZuZU.json | extract | Tavo_英雄纪元 淫堕训练师v1.27 MVU 2's Lorebook (淫乱小英雄v1.27-mvu)_Ex04.json |
| 5 | Tavo_西幻魔法世界模拟器_ZuUU.json | extract | Tavo_西幻魔法世界模拟器's Lorebook (西幻魔法世界模拟器)_Ex05.json |
| 6 | Tavo_龙王传说v2.7_ZuTm.json | extract | Tavo_龙王传说v2.7's Lorebook (龙王传说v2.7)_Ex06.json |
| 7 | Tavo_造物主的游乐场_ZuTM.json | extract | Tavo_造物主的游乐场's Lorebook (造物主的游乐场)_Ex07.json |
| 8 | Tavo_迷宫之主_ZuXs.json | extract | Tavo_迷宫之主's Lorebook (迷宫之主)_Ex08.json |
| 9 | Tavo_男寝怪谈_ZuYQ.json | extract | Tavo_男寝怪谈's Lorebook (男寝怪谈)_Ex09.json |
| 10 | Tavo_豚俘-猛男阳具复制系统_ZuUm.json | extract | Tavo_豚俘-猛男阳具复制系统's Lorebook (豚俘-猛男阳具复制系统)_Ex10.json |
| 11 | Tavo_瓦罗特_ZuV0.json | extract | Tavo_瓦罗特's Lorebook (瓦罗特)_Ex11.json |
| 12 | Tavo_黄权至上_ZuXG.json | extract | Tavo_黄权至上's Lorebook (黄权至上)_Ex12.json |
| 13 | Tavo_大华夏天朝东瀛自治区_ZuV7.json | extract | Tavo_大华夏天朝东瀛自治区's Lorebook (大华夏天朝东瀛自治区)_Ex13.json |
| 14 | Tavo_欢迎来到DND_ZuUF.json | extract | Tavo_欢迎来到DND's Lorebook (欢迎来到DND)_Ex14.json |
| 15 | Tavo_投资性直播_ZuUt.json | extract | Tavo_投资性直播's Lorebook (投资性直播)_Ex15.json |
| 16 | Tavo_寻道太虚(前端战斗)_ZuUL.json | extract | Tavo_寻道太虚(前端战斗)'s Lorebook (寻道太虚(前端战斗))_Ex16.json |
| 17 | Tavo_炽热世界_ZuU9.json | extract | Tavo_炽热世界's Lorebook (炽热世界)_Ex17.json |
| 18 | Tavo_精牛牧场_ZuZ2.json | extract | Tavo_精牛牧场's Lorebook (精牛牧场)_Ex18.json |
| 19 | Tavo_竹马模拟器_ZuU0.json | extract | Tavo_竹马模拟器's Lorebook (竹马模拟器)_Ex19.json |
| 20 | Tavo_综漫世界_ZuUf.json | extract | Tavo_综漫世界's Lorebook (综漫世界)_Ex20.json |
| 21 | 无声星环.json | extract | 无声星环's Lorebook (WSXH)_Ex21.json |
| 22 | 男子高中.json | extract | 男子高中's Lorebook (男子高中)_Ex22.json |
| 23 | 转盘抽奖调教模拟器.json | extract | 转盘抽奖调教模拟器's Lorebook (转轮抽奖调教模拟器)_Ex23.json |
| 24 | 青港市世界书.json | copy | 青港市世界书.json |
| 25 | 黄油XP百科全书 (1).json | copy | 黄油XP百科全书 (1).json |
| 26 | BDSM道具 2025.2.2 (1).json | copy | BDSM道具 2025.2.2 (1).json |

---

## Phase 2 · 任务 B：按文件大小加序号 + 简单阅读 + 写总览文档

### B.1 排序与编号
- 范围：提取完成后 `Tavo参考世界书` 下所有 .json + 1 个 .txt
- 排序：按文件大小 **降序**
- 编号：1, 2, 3, ... （大→小）
- 写一个新脚本 `sort_lorebook.py`，输出 `lorebook_size_index.json`（含序号/路径/大小/类型/条目数/首条 key 预览）

### B.2 "简单阅读" 含义
针对每个 .json 世界书文件，提取以下摘要信息（**不复制正文内容**，仅结构化）：
- 文件序号 + 文件名
- 字节大小
- `tavo_spec` / `name`（如无则记 N/A）
- `entries` 总数
- 启用条目数（`disable=false`）
- 前 3~5 条 entry 的 `key` 与 `comment`（若空则用 `content` 前 60 字符）
- 触发逻辑（`constant / selective / use_regex`）统计

针对 1 个 .txt 文件（精能大陆），按文本字数 + 前 10 行概要。

### B.3 文档输出
- 路径：`C:\Users\Administrator\Desktop\trae文件夹\extracted\帝王战队角色卡\帝王战队资料\Tavo参考世界书\_索引\00_Tavo参考世界书总览.md`
- 文档结构：
  1. 顶部摘要：本次新增数、总文件数、总大小
  2. 文件大小序列表（Markdown 表格，列：序号/大小/文件名/类型/条目数/启用数）
  3. 按文件分别给出"条目速览"小节（每个文件 H2 标题）
  4. 末尾备注：版本差异说明（如 勇者养成指南 v1 vs v5、英雄纪元 MVU vs MVU 2）

### B.4 涉及文件
- 新建脚本：`C:\Users\Administrator\Desktop\trae文件夹\extract_lorebook.py`
- 新建脚本：`C:\Users\Administrator\Desktop\trae文件夹\sort_lorebook.py`
- 新建索引目录：`...\Tavo参考世界书\_索引\`
- 新建文档：`...\Tavo参考世界书\_索引\00_Tavo参考世界书总览.md`
- 临时索引 JSON：`...\Tavo参考世界书\_索引\lorebook_size_index.json`
- 输出 26 个新 .json 到 `...\Tavo参考世界书\`

---

## 关键决策记录

| # | 决策 | 依据 |
|---|---|---|
| D1 | 提取格式采用标准 Tavo lorebook（顶层 entries） | 用户确认；现有 Tavo参考世界书 大多数用此格式；导入 SillyTavern 更直接 |
| D2 | 3 份独立世界书复制进 Tavo参考世界书（保留原名） | 用户确认；保持目录"参考世界书"语义统一 |
| D3 | 3 份非 Tavo 角色卡的世界书也提取（无 Tavo_ 前缀） | 用户确认；让 Tavo参考世界书 成为完整世界书仓库 |
| D4 | 20 个版本号不同的角色卡（如 勇者养成指南 v5 vs 现有 v1）也提取为新文件 | 用户原话"已经有了的就不要提取"是对同名同版而言；v5 ≠ v1，理应保留 |
| D5 | 文件名用 `_Ex<NN>` 编号后缀以标识"提取来源" | 区分现有 `_Za5N/_XeTi` 体系；保留可追溯性 |
| D6 | 剧情文档撰写**不**在本次任务范围 | 用户明示"下一步" |

---

## 假设与边界

- **A1**：现有 Tavo参考世界书 中以 `Tavo_英雄纪元 淫堕训练师v1.27 MVU_T4Ki.json` 命名的文件是"整张角色卡含世界书"（chara_card_v3），按用户"已经有了的就不要提取"理解视为已存在。
- **A2**：所有 33 个 Tavo 角色卡的 `data.character_book` 都符合标准格式（`tavo_spec: "lorebook"`, `entries: {uid: {...}}`）。脚本需对异常情况打印警告并跳过，不中断整体流程。
- **A3**：3 份独立世界书复制前后内容不变，**不重命名**（避免用户已经依赖原文件名做引用）。
- **A4**：用户使用的"加序号"=按文件大小降序的 1, 2, 3… 整数序号。
- **A5**："简单阅读"指结构化摘要（条目数、key 列表、启用状态），**不**输出完整正文内容（避免文档膨胀）。
- **A6**：BDSM道具 / 青港市世界书 / 黄油XP百科全书 这 3 份在 `完整角色卡` 与 `Tavo参考世界书` 中**重复**时，以用户希望"复制进去"理解为单边动作：复制但**不删除**原文件。

---

## 验证步骤

### V1 · 提取阶段验证
```powershell
python extract_lorebook.py
# 期望：日志显示 23 个 extract 成功 + 3 个 copy 成功；无 FAIL
```
- 检查 `Tavo参考世界书` 文件总数 = 原 27 + 新 26 = **53 个**（含 _索引 目录前的 53 个）

### V2 · 命名唯一性验证
```python
# sort_lorebook.py 末尾断言
assert len(filenames) == len(set(filenames)), "文件名重复!"
```

### V3 · 内容完整性验证
对每个新提取文件：
- `entries` 数量 = 源 `data.character_book.entries` 数量（脚本内断言）
- 至少 1 个 entry 的 `content` 非空

### V4 · 文档输出验证
- `00_Tavo参考世界书总览.md` 存在且非空
- 表格行数 = Tavo参考世界书 内 .json 数量 + 1(.txt)
- 表格首行 = 最大文件（命定之诗 1.45MB 级别）
- 表格末行 = 最小文件

### V5 · 总览
- 输出"提取报告"+ "索引文档"两份产物
- 用户可在 `Tavo参考世界书\_索引\` 下查阅

---

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| 源 JSON 有 `escape` 字符或非标准字段 | 脚本用 `try/except` 包住每个文件，失败时打印错误并继续；不阻断整体流程 |
| 文件名含特殊字符导致复制失败 | 用 `shutil.copy2` 而非 `os.rename`；Windows 路径安全 |
| 提取后条目数与源不一致 | 脚本内逐文件断言 `len(extract_entries) == len(src_entries)`，失败时报警 |
| 索引文档过长 | 仅取每文件前 5 条 entry 作概要，全文不复制 |
| `Tavo_英雄纪元 淫堕训练师v1.27 MVU 2` 提取后与原 `MVU` 文件重名风险 | 用 `_Ex04` 后缀严格区分 |

---

## 实施时间线

1. **Step 1** — 写 `extract_lorebook.py`（约 60 行）→ 运行 → 验证
2. **Step 2** — 写 `sort_lorebook.py`（约 80 行）→ 运行 → 生成 `lorebook_size_index.json`
3. **Step 3** — 根据 index 渲染 `00_Tavo参考世界书总览.md`
4. **Step 4** — 用 `Read` 工具抽查 3~5 个新文件确认格式正确
5. **Step 5** — 报告输出

**不在本次范围**：剧情文档撰写（用户标记为"下一步"）。
