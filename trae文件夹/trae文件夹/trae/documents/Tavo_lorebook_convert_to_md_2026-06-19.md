# Tavo 参考世界书 · 改格式为 AI 可读 + 加序号 计划

> 目标：将 `Tavo参考世界书` 下所有世界书从 JSON 转换为 AI 可读的 Markdown 格式（保留 H2 条目标题），同时按文件大小降序加序号重命名（`01.命定之诗与黄昏之歌.md`），便于按文件名排序后直接逐个读取来写剧情文档。

---

## Phase 0 · 当前状态分析（已确认）

### 0.1 Tavo参考世界书 当前 53 文件构成

| 类别 | 数量 | 处理方式 |
|---|---|---|
| 标准 Tavo lorebook (.json，`tavo_spec: "lorebook"` + `entries` dict) | 45 | **转换** |
| 写卡助手文件夹（2 个） | 2 | **跳过**（非世界书，是辅助工具） |
| Tavo_英雄纪元 淫堕训练师v1.27 MVU_T4Ki.json（chara_card_v3） | 1 | **提取 `data.character_book` 后转换** |
| 咒术回战_数据库剧情推进v4.8.json（prompt preset） | 1 | **转换**（保留 promptGroup 结构） |
| 独立世界书（青港市/黄油XP/BDSM道具） | 3 | **转换**（顶层 entries 已是 dict） |
| 精能大陆(小光).txt | 1 | **转 .md 包装**（已是文本） |

转换后预计生成 **51 个 .md 文件**（53 - 2 写卡助手）。

### 0.2 现状问题
- 当前文件是 JSON，AI 读取需要解析才能用
- 字段（`uid/key/constant/position/selectiveLogic` 等）对 AI 写剧情毫无帮助
- 文件名 `Tavo_<X>'s Lorebook (<X>)_<4字符ID>.json` 过长且无序号
- 用户已要求"删掉 JSON 代码字段"、"AI 可读性强"、"加序号"

### 0.3 目标输出形态
- **文件名**：`01.命定之诗与黄昏之歌.md`（按大小降序 + 简洁名称 + .md 后缀）
- **内容**：
  ```markdown
  # 01. 命定之诗与黄昏之歌

  ## 状态栏
  <content here>

  ## 变量初始化
  <content here>
  ...
  ```
- 不再有任何 JSON 元数据

---

## Phase 1 · 任务 A：转换所有世界书为 .md

### A.1 转换脚本
**文件**：`C:\Users\Administrator\Desktop\trae文件夹\convert_lorebook_to_md.py`

**输入目录**：`extracted/帝王战队角色卡/帝王战队资料/Tavo参考世界书/`
**输出目录**：`extracted/帝王战队角色卡\帝王战队资料\Tavo参考世界书\`（原地替换）
**索引输出**：`Tavo参考世界书\_索引\`（更新现有 00_Tavo参考世界书总览.md）

### A.2 处理逻辑（按文件类型）

| 输入类型 | 识别方式 | 提取方式 | 输出 |
|---|---|---|---|
| 标准 Tavo lorebook | `tavo_spec == "lorebook"` | 取 `entries`（dict），按 `display_index` 或 `order` 排序 | H2 标题 = `name`，内容 = `content` |
| 独立世界书（青港市等） | 顶层 `entries`（dict 或 list） | 取 entries，列表也按顺序 | H2 标题 = `name`/`comment`，内容 = `content` |
| chara_card_v3 | `spec == "chara_card_v3"` | 取 `data.character_book.entries`（list → 转换） | 同标准 Tavo lorebook |
| 咒术回战 prompt preset | 顶层是 list，且有 `promptGroup` 字段 | 取 `name` 作 H1 标题，`promptGroup` 数组按 role 顺序拼接 | H2 标题 = role（SYSTEM/USER/assistant），内容 = content |
| .txt 文本 | 文件后缀是 .txt | 整个文件内容 | 单一 H1 标题，正文 = 原文 |

### A.3 排序与编号

1. 扫描 `Tavo参考世界书/`（**跳过 `写卡助手/` 子目录**）
2. 每个 .json / .txt 文件取 `size_bytes`
3. **按 size 降序**排序
4. 编号 01, 02, 03, ... (2 位数前导零)
5. 第一个文件 = 当前最大者 `命定之诗与黄昏之歌`（1,519,090 bytes）
6. 跳过写卡助手后，序号 01-51

### A.4 文件名生成规则

从原文件提取"显示名"，加 `XX.` 前缀和 `.md` 后缀：

| 原文件名 | 提取显示名 | 输出 |
|---|---|---|
| `Tavo_命定之诗与黄昏之歌v4.2's Lorebook (命定之诗与黄昏之歌v4.2)_Za5z.json` | 命定之诗与黄昏之歌 | `01.命定之诗与黄昏之歌.md` |
| `Tavo_《道渊》v5.1's Lorebook (道友先上我断后)_Za5N.json` | 道渊 | `03.道渊.md` |
| `Tavo_夏恋·私奔v3.0's Lorebook (3夏恋·私奔)_SAVk.json` | 夏恋·私奔 | `06.夏恋·私奔.md` |
| `Tavo_英雄纪元 淫堕训练师v1.27 MVU_T4Ki.json` | 英雄纪元 | `12.英雄纪元.md` |
| `Tavo_乳胶系统's Lorebook (乳胶系统)_XeTc.json` | 乳胶系统 | `乳胶系统.md` |
| `无声星环's Lorebook (WSXH)_Ex21.json` | 无声星环 | `02.无声星环.md` |
| `精能大陆(小光).txt` | 精能大陆 | `精能大陆.md` |
| `青港市世界书.json` | 青港市世界书 | `青港市世界书.md` |
| `黄油XP百科全书 (1).json` | 黄油XP百科全书 | `黄油XP百科全书.md` |
| `BDSM道具 2025.2.2 (1).json` | BDSM道具 | `BDSM道具.md` |
| `咒术回战_数据库剧情推进v4.8.json` | 咒术回战 | `咒术回战.md` |
| `Tavo_勇者养成指南 v5 世界里侧 1's Lorebook (...)_Ex02.json` | 勇者养成指南v5 | `05.勇者养成指南v5.md` |

**显示名提取规则**（顺序尝试）：
1. 若是 chara_card_v3：取 `data.name` 字段
2. 否则若是标准 Tavo lorebook：取 Tavo_ 之后到 's Lorebook 之前的部分
3. 否则若是独立世界书/咒术回战：取文件名去掉扩展名

**显示名清洗**（按顺序应用）：
- 去 `Tavo_` 前缀
- 去 `'s Lorebook (...)_XXXX` 后缀
- 去 ` (1)` / ` (2)` 副本后缀
- 去版本号：`v\d+(\.\d+)*` → 空（如 `v4.2`, `v5.1`, `v1.27`, `v0.1`）
- 去 `MVU` / `MVU 2` 标记
- 去前后 `《》` 括号
- 去前缀数字（如 `3夏恋·私奔` 的 `3`）
- 去 `(_Worldbooks)` / `(-)` / `(- 寻道太虚-Worldbooks -)` 这种装饰
- 去结尾的 `_` / `-` / 空格
- 中间点 `·` 保留（用户示例 `命定之诗与黄昏之歌` 也没用·, 但 `夏恋·私奔` 用·更自然）
- 合并多空格

### A.5 Markdown 内容格式

```markdown
# 01. 命定之诗与黄昏之歌

> 共 N 个条目（启用 M 个），原始 JSON 大小 XXX,XXX bytes

## 状态栏
<content text here, 完整保留 HTML 标签、换行、特殊字符>

## 变量初始化
<content text here>

---

(每两个条目之间用空行分隔；不必显式加 `---` 分隔符，但空行足够清晰)
```

**关键不变量**：
- ❌ 删除所有 JSON 字段（`uid/key/keysecondary/constant/position/selectiveLogic/probability/...`）
- ✅ 保留 `content` 字段的**完整原始文本**（包括 HTML、Markdown、特殊字符）
- ✅ 保留 `name`/`comment` 作为 H2 标题（去重时优先 name）
- ✅ 禁用条目（`disable=true`）的判定逻辑：根据用户"AI 可读"目的，**默认全部保留**，在顶部注明"共 N 个，启用 M 个"
- ✅ entry 排序：优先按 `display_index`，其次 `order`，再次字典序 uid

### A.6 步骤详解

```
1. 脚本扫描 Tavo参考世界书/ （排除 写卡助手/）
2. 列出所有候选文件 (53 - 2 = 51 个)
3. 按文件大小降序排序
4. 为每个文件分配 01-51 序号
5. 计算"显示名"（按 A.4 规则）
6. 检测文件类型并解析（按 A.2）
7. 生成 Markdown 内容
8. **先写入临时文件**（如 Tavo参考世界书/.tmp/01.命定之诗与黄昏之歌.md）
9. 全部 51 个生成成功后，**原子替换**：
   - 把所有 .tmp 移出到 Tavo参考世界书/ 正式位置
   - 删除所有原 .json 和 精能大陆(小光).txt
   - 删除临时 .tmp 目录
10. 更新 _索引/00_Tavo参考世界书总览.md 和 lorebook_size_index.json
11. 删除旧的 extract_lorebook.py / verify_lorebook.py / sort_lorebook.py
```

### A.7 涉及文件清单

#### 新建
- `C:\Users\Administrator\Desktop\trae文件夹\convert_lorebook_to_md.py`（约 200 行）

#### 删除（脚本执行后）
- 51 个原 .json + 1 个 .txt（共 52 个原文件，51 个原 .json + 1 精能大陆 .txt）

#### 更新
- `Tavo参考世界书\_索引\00_Tavo参考世界书总览.md`
- `Tavo参考世界书\_索引\lorebook_size_index.json`

#### 保留（参考用，不动）
- `C:\Users\Administrator\Desktop\trae文件夹\extract_lorebook.py`
- `C:\Users\Administrator\Desktop\trae文件夹\verify_lorebook.py`
- `C:\Users\Administrator\Desktop\trae文件夹\sort_lorebook.py`
- `Tavo参考世界书\写卡助手\` 整个文件夹

---

## Phase 2 · 任务 B：更新 _索引/ 总览文档

### B.1 新内容
- 顶部摘要改为"已转为 Markdown 格式"
- 文件表改为 .md 后缀
- 每个文件块只显示：序号 / 文件名 / 路径 / 大小 / 条目数 / 启用数
- 删除所有 JSON 字段描述（key/constant/selective/use_regex 等已无意义）
- 每个文件块改为：`### XX. 文件名` + 简单一行介绍 + `（详见 01.命定之诗与黄昏之歌.md）`

### B.2 简化的文件速览块

```markdown
### 01. 命定之诗与黄昏之歌.md

- **大小**：1,519,090 bytes
- **条目数**：431 (启用 321)
- **原始**：Tavo_命定之诗与黄昏之歌v4.2's Lorebook (命定之诗与黄昏之歌v4.2)_Za5z.json
- **路径**：[Tavo参考世界书/01.命定之诗与黄昏之歌.md](file:///C:/.../01.命定之诗与黄昏之歌.md)
```

---

## Phase 3 · 验证步骤

### V1 · 转换完整性
- 51 个 .md 文件全部生成
- 总大小与原 .json 总和差异 < 5%（Markdown 略小，因为去掉了 JSON 结构）

### V2 · 命名唯一性
- `assert len(filenames) == 53` (51 .md + 2 in 写卡助手)
- 序号连续 01-51
- 无重复文件名

### V3 · 内容保留性
对每个 .md 文件：
- 顶部 H1 标题存在
- 至少 1 个 H2 标题（除单文件无 entries 的情况）
- 总 `content` 字符数 ≥ 原 `content` 字符数（去字段不删内容）

### V4 · 文件可读性
- 至少抽查 3 个 .md 文件（最大 / 中等 / 最小）
- 确认 H2 标题正确
- 确认 content 完整保留

### V5 · 索引更新
- `00_Tavo参考世界书总览.md` 反映新文件名
- `lorebook_size_index.json` 反映新数据

---

## 关键决策记录

| # | 决策 | 依据 |
|---|---|---|
| D1 | 文件后缀用 `.md` | 用户确认；Markdown 最 AI 友好 |
| D2 | 条目用 `## name` 标题 + 下面接 content | 用户确认；最方便定位 |
| D3 | 跳过 `写卡助手/` 文件夹 | 用户确认；非世界书，是辅助工具 |
| D4 | 提取 `Tavo_英雄纪元 淫堕训练师v1.27 MVU_T4Ki.json` 的 `data.character_book` | 用户确认；虽是 chara_card_v3 但内嵌世界书 |
| D5 | 保留咒术回战_数据库剧情推进v4.8.json | 用户未选跳过；虽然是 prompt preset 但与世界观相关 |
| D6 | 序号按文件大小降序 | 用户示例"01.命定之诗与黄昏之歌"对应 size 排序 #1；保持与现有总览一致 |
| D7 | 文件名清洗后加序号 + 名称 | 用户确认；不使用 Tavo_ 前缀和 4 字符 ID |
| D8 | 禁用条目默认全部保留，仅在顶部统计 | 用户说"AI 可读"，全量更稳妥 |
| D9 | 原地替换原 .json 为 .md | 用户说"改掉"= change/replace；不放子目录 |
| D10 | 总览文档同步更新 | 保持索引与实际文件一致 |

---

## 假设与边界

- **A1**：用户"AI 可读性强"指**结构化 Markdown** 而非纯文本（因为条目间有 `name` 标题作为锚点）
- **A2**：用户"按文件名排序"指 Windows 资源管理器按名称升序排序（与字典序一致）
- **A3**：用户示例 `01.命定之诗与黄昏之歌` 表明 strip 版本号（v4.2）
- **A4**：原 JSON 中的 `content` 字段是主要信息源；其他字段（key/constant 等）对 AI 写剧情没有价值，可安全删除
- **A5**：`精能大陆(小光).txt` 是用户手动创建的纯文本，无 entry 结构，整体作为单一 section 放入 .md
- **A6**：`写卡助手/` 子目录下的 2 个文件保留不动，**不**参与转换和编号（用户说"跳过"）
- **A7**：若同名 .md 已存在（如重跑脚本），新文件覆盖旧的
- **A8**：脚本对 51 个文件中的**任一**解析失败都应**阻断**整体（fail-fast），提示用户修复后重跑；不部分转换留下混合状态

---

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| 某个 .json 解析失败 | try/except 包裹单文件；失败立即停止并报错 |
| 文件名冲突（如多个源都清洗成"道渊"） | 重复名加后缀 `-2` / `-3`；脚本内断言 |
| 序号重排后大小顺序改变 | 排序后用 `assert order stable` 验证 |
| `content` 含 `##` 字符与 H2 标题冲突 | content 原样保留，Markdown 渲染可能把"##"识别为子标题——**不处理**，因为这是原内容 |
| 转换后某些 lorebook 体积过小（缺 content） | 在 .md 顶部注明 `<空内容>` |
| 用户对命名风格有其他偏好 | Phase 1 计划可调整；不执行前可改 |
| 原子替换失败留下半截状态 | 先全部写 .tmp，再一次性移动到正式位置并删除旧文件 |

---

## 实施时间线

1. **Step 1** — 写 `convert_lorebook_to_md.py`（约 200 行）
2. **Step 2** — 干跑（dry-run）：只扫描 + 报告计划产物，不实际写文件；让用户检查
3. **Step 3** — 实跑：先写 .tmp，再原子替换
4. **Step 4** — 重新生成 `_索引/00_Tavo参考世界书总览.md` 和 `lorebook_size_index.json`
5. **Step 5** — Read 工具抽查 3-5 个 .md 文件确认格式
6. **Step 6** — 报告输出

**不在本次范围**：剧情文档撰写（用户标记为"下一步"）。
