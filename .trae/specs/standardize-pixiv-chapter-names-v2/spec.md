# Pixiv 章节文件名标准化 v2 Spec

## Why
v1 实现的输出被用户否决：
- 把"第一章 雄鹰末路"中的"一"留作了中文，**用户要求"纯数字"用阿拉伯数字**（第 1 章）
- 章节排序依赖 作品信息 顺序=最新到最旧，**用户要求"按发布时间从早到晚"**
- 章节名仍不统一

需要重写为用户期望的格式：`第 N 章 标题.txt`，N 为阿拉伯数字，章节顺序按发布从早到晚。

## What Changes
- 重写 `/workspace/pixiv_renamer.py`：
  - **解析 作品信息 标题**，识别 `第X章 副标题` / `第X章` / `序章 副标题` / `序章` / `终章 副标题` / `终章` / `番外 N 副标题` / `番外` / `幕间` / `if线` 等多种模板
  - **中文数字 → 阿拉伯数字**：`一→1, 二→2, …, 十→10, 十一→11, …, 九十九→99, 一百→100` 等
  - **章节序号 = 作品发布时间从早到晚的排名**（最早 = 第 1 章，最新 = 第 N 章）
  - **新文件名 = `第 N 章 副标题.txt`**；若标题只有 `第X章` 无副标题，则文件名 = `第 N 章.txt`；若是 `序章`/`终章`/`番外` 等非数字标题，保留原样但加序号前缀（如 `01 序章.txt`）
- 重新跑全量处理，覆盖 `pixiv_renamed/`
- 重新生成 `rename_report.md`

## Impact
- Affected specs: 覆盖 `standardize-pixiv-chapter-names` 的实现
- Affected code: `/workspace/pixiv_renamer.py`（重写）
- 输出: `/workspace/pixiv_renamed/`（重新生成）、`/workspace/pixiv_renamed/rename_report.md`
- 原 `/workspace/pixiv_workspace/` 仍只读

## ADDED Requirements

### Requirement: 中文数字 → 阿拉伯数字
系统 SHALL 把 `一二三四五六七八九十百千零` 组成的中文数字字符串转换为阿拉伯 int。范围 0–999。例：`一→1, 十→10, 十一→11, 二十三→23, 一百→100, 一百零五→105`。

#### Scenario: 单位数
- **WHEN** 输入 `一`
- **THEN** 返回 `1`

#### Scenario: 十位
- **WHEN** 输入 `十`
- **THEN** 返回 `10`

#### Scenario: 十几
- **WHEN** 输入 `十三`
- **THEN** 返回 `13`

#### Scenario: 二十几
- **WHEN** 输入 `二十三`
- **THEN** 返回 `23`

#### Scenario: 几百
- **WHEN** 输入 `一百零五`
- **THEN** 返回 `105`

### Requirement: 解析 作品信息 标题模板
系统 SHALL 从 作品信息 标题字符串解析出 `(designation, number, subtitle)`：
- `第X章 副标题` → designation=`章`, number=parse(X), subtitle=`副标题`
- `第X章` → designation=`章`, number=parse(X), subtitle=``
- `序章 副标题` → designation=`序章`, number=None, subtitle=`副标题`
- `序章` → designation=`序章`, number=None, subtitle=``
- `终章 副标题` → designation=`终章`, number=None, subtitle=`副标题`
- `终章` → designation=`终章`, number=None, subtitle=``
- `第X话 副标题` → designation=`话`, number=parse(X), subtitle=`副标题`（日语体）
- `第X季终章 副标题` / `第X季后记 副标题` → designation=`终章`/`后记`, number=parse(X), subtitle=… 整段保留
- `番外N 副标题` / `番外 副标题` / `番外` → designation=`番外`, number=parse(N) 或 None, subtitle=…
- `幕间` / `幕间 副标题` → designation=`幕间`, subtitle=…
- `if线 副标题` → designation=`if线`, subtitle=…
- 其他无法识别的 → designation=`章`, number=None, subtitle=完整原标题

#### Scenario: 简单第一章
- **WHEN** 标题 = `第一章 雄鹰末路`
- **THEN** designation=`章`, number=1, subtitle=`雄鹰末路`

#### Scenario: 第十四章无副标题
- **WHEN** 标题 = `第十四章`
- **THEN** designation=`章`, number=14, subtitle=``

#### Scenario: 序章
- **WHEN** 标题 = `序章 鬼影`
- **THEN** designation=`序章`, number=None, subtitle=`鬼影`

#### Scenario: 第一季后记
- **WHEN** 标题 = `第一季后记`
- **THEN** designation=`后记`, number=1, subtitle=``

### Requirement: 按发布时间从早到晚排名 → 新章节号
对每个作品的 作品信息 条目按 `创建时间` 升序排序（最早 = rank 1），得到 `(作品内 rank, designation, number, subtitle)`。

#### Scenario: 正常排序
- **WHEN** 作品有 4 个条目，创建时间分别为 2025-04, 2025-08, 2026-01, 2026-04
- **THEN** 2025-04 那条 rank=1, 2025-08 rank=2, 2026-01 rank=3, 2026-04 rank=4

#### Scenario: 作品信息 中 标题 出现 `第X章` 与 作品内 rank 不一致
- **WHEN** rank=1 的条目标题含 `第三章`, rank=2 含 `第一章`
- **THEN** 新文件名不采用标题里的 `第X章` 数字，而是按 rank 重新编号（详见下一条 Requirement）

### Requirement: 生成新文件名
**新章节号 = 作品内 rank**（按发布时间从早到晚）。

新文件名规则：
- 若 designation=`章` 且 number 非空：
  - 新章节号 = rank（不用原 number）
  - 文件名 = `第 {rank} 章{subtitle ? ' ' + subtitle : ''}.txt`
- 若 designation=`章` 但 number 为空（无法解析数字）：
  - 文件名 = `第 {rank} 章{如有 subtitle 则 ' '+subtitle}.txt`
- 若 designation=`序章`/`终章`/`后记`/`番外`/`幕间`/`if线` 等特殊称谓：
  - 文件名 = `{rank:02d} {designation}{subtitle ? ' '+subtitle : ''}.txt`
  - 特殊情况下（如 `第一季后记`），designation 优先取特殊词（`后记`）而非 `第…章`
- 副标题中的全角空格、书名号、破折号、冒号、引号等全部保留
- 文件名做 Windows 非法字符清洗（去 `<>:"/\|?*` 与首尾 `.` 空白）

#### Scenario: 正常奥鲁斯托第 1 章
- **WHEN** 作品信息有 4 条；rank=1 条目标题=`第一章 雄鹰末路`, 创建时间=2025-04-02（最早）
- **THEN** 新文件名 = `第 1 章 雄鹰末路.txt`

#### Scenario: 标题与 rank 不一致（如 rank=1 但标题含"第三章"）
- **WHEN** 作品信息 rank=1 条目标题=`第三章 浪潮`, 创建时间最早
- **THEN** 新文件名 = `第 1 章 浪潮.txt`（按 rank 重新编号，不用原"第三章"）

#### Scenario: 序章
- **WHEN** 作品信息 rank=1 条目标题=`序章 鬼影`
- **THEN** 新文件名 = `01 序章 鬼影.txt`

#### Scenario: 第一季后记（特殊）
- **WHEN** 作品信息 rank=16 条目标题=`第一季后记`（rank=16 是最晚发布）
- **THEN** 新文件名 = `16 第一季后记.txt`（designation=`后记`, number=1；rank=16；用特殊称谓保留）

#### Scenario: 都市传说天象旅店 第 14 章无副标题
- **WHEN** 作品信息 rank=14 条目标题=`第十四章`, subtitle=``
- **THEN** 新文件名 = `第 14 章.txt`

#### Scenario: 序章+第一章 合并
- **WHEN** 作品信息 rank=1 条目标题=`序章+第一章`
- **THEN** 新文件名 = `01 序章+第一章.txt`

### Requirement: 仍按 作品信息 对齐文件 → 章节
沿用 v1 的"raw_title 规范化精确/子串匹配"逻辑，把每个文件匹配到 作品信息 的某一条 entry，从而获得 (作品内 rank, designation, number, subtitle)。

#### Scenario: 错字文件
- **WHEN** 文件 `#2 第二张 无声地渗透.txt` 与 作品信息 `第二张 无声地渗透`（同 typo）匹配
- **THEN** 使用该 entry 的 rank 和解析后的 designation/number

#### Scenario: 副标题差异（作品信息 标点更规范）
- **WHEN** 文件 `#1 第一章 总偷瓶子的虎哥.txt` 与 作品信息 `第一章   总偷瓶子的虎哥.txt`（中间多空格）通过规范化匹配
- **THEN** 使用 作品信息 的 rank 和 subtitle

### Requirement: 无 #N 前缀文件 / 作品信息缺失文件
- 无 #N 前缀：尝试用 raw_title 匹配 作品信息，匹配上 → 用 作品信息 rank 生成新名；匹配不上 → 保留原文件名，在报告中标 `untouched`
- 作品信息 缺失或为空：保留原 #N 文件名（去掉 #N 前缀）作为新名，在报告中标 `no_info_kept`
- 0 字节文件：原样复制到新目录，文件名原样保留（不重命名，避免覆盖）

### Requirement: 文件名排序正确
由于采用"作品内 rank 重新编号"且 rank 是按发布时间从早到晚（rank 1 = 最早），新目录按文件名排序时，章节按阅读顺序排列。
- `第 1 章 xxx.txt` < `第 2 章 yyy.txt` < `第 10 章 zzz.txt`（按字典序也正确）
- `01 序章.txt` < `02 序章.txt` < ...（用零填充 2 位）
- `16 终章 xxx.txt`（按发布最晚）

## MODIFIED Requirements
- 覆盖 v1 spec 的 "ADDED Requirement: 生成标准化新文件名"（旧的"用 作品信息 标题直接做文件名"作废）
- 覆盖 v1 spec 的 "ADDED Requirement: 按 #N 文件名前缀建立文件名→作品id 映射"（旧的"按顺序默认对齐"作废，新规则按 作品信息 标题模糊匹配 + 作品内 rank 编号）

## REMOVED Requirements
- 旧的"`#1` = 作品信息第 1 条（最新发布）"假设 — 移除
- 旧的"保留 作品信息 标题中的中文数字'第一章'" — 移除
