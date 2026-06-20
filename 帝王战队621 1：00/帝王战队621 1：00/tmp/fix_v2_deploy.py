from pathlib import Path

# 修复通读版部署文档
path = Path('工作区/documents/v2-阶段4.1-4.3-逐本通读+笔记实时写入_2026-06-20.md')
text = path.read_text(encoding='utf-8')

# 修复批次规划表格
old = '| 2 | 02 勇者魔物奇幻 | 8 | 23 | '
new = '| 2 | 02 勇者魔物奇幻 | 8 | 32 | '
text = text.replace(old, new)

old = '| **合计** | — | **36** | **101** | — | **≥675,000** |'
new = '| **合计** | — | **36** | **109** | — | **≥675,000** |'
text = text.replace(old, new)

# 修复写入位置速查表（02 勇者魔物奇幻的 5.X 段从 12 部改为 21 部）
old_summary = '| 笔记文件 | 4.X 段（9-10 分） | 5.X 段（5-8 分） | 6.X 段（1-4 分） |\n|---|---|---|---|\n| `pixiv_深度阅读笔记_01_战队特摄.md` | 4.1-4.4（4 部） | 5.1-5.4（4 部） | — |\n| `pixiv_深度阅读笔记_02_勇者魔物奇幻.md` | 4.1-4.11（11 部） | 5.1-5.12（12 部） | — |\n| `pixiv_深度阅读笔记_03_正太校园堕落.md` | 4.1-4.18（18 部） | 5.1-5.7（7 部） | — |\n| `pixiv_深度阅读笔记_04调教拍卖+05异种触手.md` | 4.1-4.14（14 部） | 5.1-5.6（6 部） | — |\n| `pixiv_深度阅读笔记_06修真玄幻+07外语.md` | 4.1-4.3（3 部） | 5.1-5.7（7 部） | — |\n| `pixiv_深度阅读笔记_08同人+09女性向.md` | 4.1-4.5（5 部） | 5.1-5.10（10 部） | — |'
new_summary = '| 笔记文件 | 4.X 段（9-10 分） | 5.X 段（5-8 分） | 6.X 段（1-4 分） |\n|---|---|---|---|\n| `pixiv_深度阅读笔记_01_战队特摄.md` | 4.1-4.4（4 部） | 5.1-5.4（4 部） | — |\n| `pixiv_深度阅读笔记_02_勇者魔物奇幻.md` | 4.1-4.11（11 部） | 5.1-5.12（21 部） | — |\n| `pixiv_深度阅读笔记_03_正太校园堕落.md` | 4.1-4.18（18 部） | 5.1-5.7（7 部） | — |\n| `pixiv_深度阅读笔记_04调教拍卖+05异种触手.md` | 4.1-4.14（14 部） | 5.1-5.6（6 部） | — |\n| `pixiv_深度阅读笔记_06修真玄幻+07外语.md` | 4.1-4.3（3 部） | 5.1-5.7（7 部） | — |\n| `pixiv_深度阅读笔记_08同人+09女性向.md` | 4.1-4.5（5 部） | 5.1-5.10（10 部） | — |'
text = text.replace(old_summary, new_summary)

# 修复 SA-02-D（裸之冒险团 + 神州九钥）
old_sa02d = '| SA-02-D | 裸之冒险团 + 白鸦 | 32 | 10 | 32/32 | 4.4 | ~200KB | 合包 |'
new_sa02d = '| SA-02-D | 裸之冒险团 + 神州九钥 | 41 | 10 | 41/41 | 4.4 | ~260KB | 合包 |'
text = text.replace(old_sa02d, new_sa02d)

# 修复 SA-02-E（少年骑士长的恶堕 + 白鸦）
old_sa02e = '| SA-02-E | 少年骑士长的恶堕 + 神州九钥 | 40 | 10 | 40/40 | 4.5 | ~230KB | 合包 |'
new_sa02e = '| SA-02-E | 少年骑士长的恶堕 + 白鸦 | 33 | 10 | 33/33 | 4.5 | ~200KB | 合包 |'
text = text.replace(old_sa02e, new_sa02e)

# 修复 SA-02-F 明细
old_sa02f = '| 2 | 神州九钥 | 工作区/pixiv小说/02_勇者魔物奇幻/神州九钥/ | 20 | 9 | 完整 | ≥6,000 字符 | 20/20 (100%) | 4.5 | ~140KB |'
new_sa02f = '| 2 | 白鸦 | 工作区/pixiv小说/02_勇者魔物奇幻/白鸦/ | 12 | 10 | 完整 | ≥6,000 字符 | 12/12 (100%) | 4.5 | ~80KB |'
text = text.replace(old_sa02f, new_sa02f)

# 修复 SA-02-F 的 5.X 明细（4.X 部分变为新的 5.X）
old_sa02f_rows = '| 3 | 淫堕英雄大陆 + 奥鲁斯托 + 星落之城 + 神兽之陨 | 22 | 9 | 22/22 | 4.6 | ~180KB | 合包 |\n| SA-02-G | 当个少年英雄 + ... 9部中低分 | 23 | 7-8 | 23/23 | 5.1-5.9 | ~220KB | 合包 |'
new_sa02f_rows = '| SA-02-F | 神州九钥 + 白鸦 + 失落骑士 + 奥鲁斯托 + 羽 | 57 | 7-8 | 57/57 | 5.1-5.8 | ~400KB | 合包 |\n| SA-02-G | 淫堕英雄大陆 + 奥鲁斯托的少年英雄小说 + 星落之城 + 神兽之陨 | 22 | 9 | 22/22 | 5.9-5.12 | ~180KB | 合包 |'
text = text.replace(old_sa02f_rows, new_sa02f_rows)

# 修复 SA-02-G 明细（9 部改为 13 部）
old_sa02g = '| SA-02-G | 当个少年英雄 + ... 9部中低分 | 23 | 7-8 | 23/23 | 5.1-5.9 | ~220KB | 合包 |'
new_sa02g = '| SA-02-G | 当个少年英雄 + ... 13部中低分 | 57 | 7-8 | 57/57 | 5.1-5.13 | ~400KB | 合包 |'
text = text.replace(old_sa02g, new_sa02g)

# 修复 SA-02-H（7 部改为 8 部）
old_sa02h = '| SA-02-H | 复仇正义 + 少年骑士 + 颠覆正义 | 4 | 5 | 4/4 | 5.10-5.12 | ~80KB | 合包 |'
new_sa02h = '| SA-02-H | 复仇正义 + 少年骑士 + 颠覆正义 | 4 | 5 | 4/4 | 5.14-5.17 | ~80KB | 合包 |'
text = text.replace(old_sa02h, new_sa02h)

# 修复写入目标
old_target = '### 写入目标\n**`pixiv_深度阅读笔记_02_勇者魔物奇幻.md`**\n- 4.1-4.11 段（9-10 分，共 11 部）\n- 5.1-5.12 段（5-8 分，共 12 部）'
new_target = '### 写入目标\n**`pixiv_深度阅读笔记_02_勇者魔物奇幻.md`**\n- 4.1-4.11 段（9-10 分，共 11 部）\n- 5.1-5.13 段（5-8 分，共 21 部）'
text = text.replace(old_target, new_target)

# 修复 Key Decisions（09 女性向）
old_d9 = '| D9 | NIAH 测试结论 | 800KB 文本中 0%/25%/50%/75%/100% 均命中，但完整阅读不可行 |'
new_d9 = '| D9 | NIAH 测试结论 | 800KB 文本中 0%/25%/50%/75%/100% 均命中，但完整阅读不可行 |\n| D10 | **实际读 X/Y 标注总量** | 应输出 **109** 条（而非旧版 101） |'
text = text.replace(old_d9, new_d9)

# 修复 Verification V2/V3
old_v2 = '# 应 = 101'
new_v2 = '# 应 = 109'
text = text.replace(old_v2, new_v2)

old_v3 = '| grep -E "^### [456]\.[0-9]+" pixiv_深度阅读笔记_*.md | wc -l\n# 应 = 101'
new_v3 = '| grep -E "^### [456]\.[0-9]+" pixiv_深度阅读笔记_*.md | wc -l\n# 应 = 109'
text = text.replace(old_v3, new_v3)

# 修复 Files to Execute
old_exec = '## 十一、Files to Execute\n\n| 文件 | 操作 | 说明 |\n|---|---|---|\n| `工作区/tmp/novel_inventory.md` | **读** | 109 部小说实测 size 清单 |\n| `工作区/tmp/assignment_summary.md` | **读** | 自动分桶结果（77 包） |\n| `工作区/tmp/execution_packets.md` | **读** | 6 批量执行包 |'
new_exec = '## 十二、Files to Execute\n\n| 文件 | 操作 | 说明 |\n|---|---|---|\n| `工作区/tmp/novel_inventory.md` | **读** | 109 部小说实测 size 清单 |\n| `工作区/tmp/novel_metrics.json` | **读** | 109 部小说 JSON 格式 size 数据 |'
text = text.replace(old_exec, new_exec)

# 修复十、Key Decisions 重复章节
old_key = '## 十、Key Decisions（基于实测修正）\n\n| # | 决策 | 说明 |\n|---|---|---|\n| D1'
new_key = '## 十、Key Decisions（基于实测修正 + novel_metrics 更新）\n\n| 数据项 | 数值 | 来源 |\n|---|---|---|\n| 小说总数 | **109 部** | novel_inventory.md / novel_metrics.json |\n| 章节总数 | **1131 章** | novel_inventory.md Summary |\n| 单部最大章节 | 《豪想和你在一起》**76 章** | novel_inventory.md |\n| 单部最大文件 | 《光环 无限》**683.5 KB** | novel_inventory.md |\n| 单部最大目录 | 《豪想和你在一起》**2620.2 KB** | novel_inventory.md |\n\n| # | 决策 | 说明 |\n|---|---|---|\n| D1'
text = text.replace(old_key, new_key)

# 修复十一节注释
old_k11 = '## 十一、Key Decisions（基于实测修正）\n\n| 风险'
new_k11 = '## 十一、Key Decisions（基于实测修正 + novel_metrics 更新）\n\n| 风险'
text = text.replace(old_k11, new_k11)

# 修复 Key Decisions 位置
old_k2 = '## 十、Key Decisions（基于实测修正）\n\n| 风险 | 数据支撑 | 缓解 |'
new_k2 = '## 十、Key Decisions（基于实测修正 + novel_metrics 更新）\n\n| 数据项 | 数值 | 来源 |\n|---|---|---|\n| 小说总数 | **109 部** | novel_inventory.md / novel_metrics.json |\n| 章节总数 | **1131 章** | novel_inventory.md Summary |\n| 单部最大章节 | 《豪想和你在一起》**76 章** | novel_inventory.md |\n| 单部最大文件 | 《光环 无限》**683.5 KB** | novel_inventory.md |\n| 单部最大目录 | 《豪想和你在一起》**2620.2 KB** | novel_inventory.md |\n\n| 风险 | 数据支撑 | 缓解 |'
text = text.replace(old_k2, new_k2)

path.write_text(text, encoding='utf-8')
print('通读版部署文档修复完成')
print(f'total chars: {len(text)}')
