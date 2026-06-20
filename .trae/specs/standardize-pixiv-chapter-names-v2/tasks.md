# Tasks (v2)

- [x] Task 1: 实现中文数字 → 阿拉伯数字转换（覆盖 0–999）
  - [ ] SubTask 1.1: 实现 `cn_num_to_int(s: str) -> Optional[int]`，支持 `一` 到 `一百零五` 等
  - [ ] SubTask 1.2: 单测：零、一、十、十三、二十三、一百、一百零五

- [x] Task 2: 解析 作品信息 标题模板
  - [ ] SubTask 2.1: 实现 `parse_title(title: str) -> (designation, number, subtitle)`
    - 匹配 `^第(数字)章(\s+(.+))?$` → `('章', int, subtitle)`
    - 匹配 `^序章(\s+(.+))?$` → `('序章', None, subtitle)`
    - 匹配 `^终章(\s+(.+))?$` → `('终章', None, subtitle)`
    - 匹配 `^第(数字)(季终章|季后记|季后日)(\s+(.+))?$` → 优先特殊
    - 匹配 `^第(数字)话(\s+(.+))?$` → `('话', int, subtitle)`
    - 匹配 `^番外(\s*(数字))?(\s+(.+))?$` → `('番外', int_or_None, subtitle)`
    - 匹配 `^幕间(\s+(.+))?$` → `('幕间', None, subtitle)`
    - 匹配 `^if线(\s+(.+))?$` → `('if线', None, subtitle)`
    - 其它 → `('章', None, original_title)`
  - [ ] SubTask 2.2: 单测：第一章 雄鹰末路、第十四章、序章 鬼影、终章 人间、第一季后记、第一季终章、番外、如果线 其一 三人行

- [x] Task 3: 作品内 rank 计算
  - [ ] SubTask 3.1: 对每个作品，把 作品信息 条目按 `创建时间` 升序排
  - [ ] SubTask 3.2: rank = 1-based 索引
  - [ ] SubTask 3.3: 无 `创建时间` 的条目 → 按 作品信息 顺序降序（即原顺序 1 = 最新 = rank 最大）

- [x] Task 4: 文件 → 作品信息 条目匹配（沿用 v1 的标题规范化精确/子串匹配）
  - [ ] SubTask 4.1: raw_title → normalize → 在 作品信息 normalized_titles 中查精确/子串匹配
  - [ ] SubTask 4.2: 匹配上 → 拿到 entry → 拿到 (rank, designation, number, subtitle)
  - [ ] SubTask 4.3: 匹配不上 → 保持原名，在报告中标 `untouched`

- [x] Task 5: 生成新文件名（按 v2 规则）
  - [ ] SubTask 5.1: `designation='章'` → `第 {rank} 章{subtitle ? ' ' + subtitle : ''}.txt`
  - [ ] SubTask 5.2: 特殊 designation（序章/终章/后记/番外/幕间/if线/话）→ `{rank:02d} {designation}{subtitle ? ' ' + subtitle : ''}.txt`
  - [ ] SubTask 5.3: subtitle 保留全部原标点
  - [ ] SubTask 5.4: Windows 非法字符清洗；空名兜底 `__untitled__`

- [x] Task 6: 复制到 `/workspace/pixiv_renamed/`（覆盖 v1 输出）
  - [ ] SubTask 6.1: 删除旧的 `/workspace/pixiv_renamed/`
  - [ ] SubTask 6.2: 按 v2 规则生成新目录
  - [ ] SubTask 6.3: 0 字节文件原样保留，文件名不变

- [x] Task 7: 生成 `rename_report.md`
  - [ ] SubTask 7.1: 顶部总览
  - [ ] SubTask 7.2: 各作品重命名表（旧→新）
  - [ ] SubTask 7.3: 人工核对清单

# Task Dependencies
- Task 1 独立
- Task 2 独立
- Task 3 依赖 Task 2（要解析标题才能写 designation/number）
- Task 4 依赖 Task 2 + Task 3
- Task 5 依赖 Task 4
- Task 6 依赖 Task 5
- Task 7 依赖 Task 6
