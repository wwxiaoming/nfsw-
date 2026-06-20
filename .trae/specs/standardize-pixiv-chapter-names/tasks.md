# Tasks

- [x] Task 1: 解析所有 `作品信息.txt` 建立 `作品id → 标准标题` 反向映射
  - [x] SubTask 1.1: 扫描 `pixiv_workspace/` 下全部 `作品信息.txt`，跳过空文件与无内容文件，记录每个文件的 `(作品目录, 顺序, 标题, 作品id, 创建时间)`
  - [x] SubTask 1.2: 在内存中构造两个结构：
    - `by_work_dir[作品目录] = [(order, title, work_id, created_at), ...]`（按作品信息中"顺序"升序，即发布时间从旧到新）
    - `title_to_work_id[作品目录][title_normalized] = (work_id, created_at)` 用于错字/未编号文件的回退匹配
  - [x] SubTask 1.3: 记录所有"作品信息为空/缺失"的目录到一个清单（后续会原样复制）

- [x] Task 2: 解析每个作品目录下的章节文件名，建立 `#N → 作品id` 映射
  - [x] SubTask 2.1: 用正则 `^#(\d+)\s+(.+)\.txt$` 匹配 `(#N, raw_title, raw_filename)`
  - [x] SubTask 2.2: 把 `(#N, raw_title)` 对应到 `by_work_dir[dir]`，默认按"文件序号 = 作品信息顺序 1..K"对齐（即 `#1` 对应"作品信息中第 1 条 = 最新一条"）
  - [x] SubTask 2.3: 当对不上（序号跳号、重复、错位）时，按"raw_title 与作品信息标题相似度（去除标点空白后完全相等 / 子串包含）"尝试回退匹配
  - [x] SubTask 2.4: 把回退匹配结果标 `fuzzy_matched=True` 写入报告

- [x] Task 3: 处理无 `#N` 前缀的零散文件
  - [x] SubTask 3.1: 对每个目录下不匹配 `#N` 模式的 `.txt` 文件，跳过 `作品信息.txt` 本身
  - [x] SubTask 3.2: 尝试按"raw_title"在 `by_work_dir[dir]` 中查标准标题（精确匹配 → 模糊匹配）
  - [x] SubTask 3.3: 匹配失败 → 在报告中标 `untouched: <相对路径>`，新文件名 = 原文件名（去掉前后空白）
  - [x] SubTask 3.4: 跳过空文件 / 0 字节文件（zip 中 0 字节条目），在报告中标 `skipped_empty`

- [x] Task 4: 生成新文件名（处理冲突）
  - [x] SubTask 4.1: 命中映射 → `new_name = "<标准标题>.txt"`
  - [x] SubTask 4.2: 在同一目录下若 `new_name` 已存在，按作品id 创建时间升序追加 `(2)`, `(3)`, …
  - [x] SubTask 4.3: 标题去除首尾空白，但保留内部全部标点（含全角空格、书名号、破折号、冒号、引号、半角点等）
  - [x] SubTask 4.4: 新文件名再做"文件系统安全"清洗（去除 Windows 非法字符 `<>:"/\|?*` 与首尾的 `.` 与空白）；如清洗后变为空字符串，则用 `__untitled__` 占位并在报告中标 `unsafe_renamed`

- [x] Task 5: 复制到 `/workspace/pixiv_renamed/`（不动原目录）
  - [x] SubTask 5.1: 完整按 `pixiv_workspace` 的相对路径结构镜像到 `pixiv_renamed/`
  - [x] SubTask 5.2: 同时复制 `作品信息.txt`（原名不变）
  - [x] SubTask 5.3: 对每个新文件读源文件 → 写到目标 → 校验字节一致（md5 或字节长度）

- [x] Task 6: 生成 `rename_report.md`
  - [x] SubTask 6.1: 顶部总览：处理 N 个文件 / 成功重命名 M / 保持原样 K / 需人工核对 L / untouched U / skipped_empty E
  - [x] SubTask 6.2: 按作品目录分组列出 `旧文件名 → 新文件名` 表格
  - [x] SubTask 6.3: 单列"⚠️ 需人工核对"清单：
    - 序号错位 / 疑似错字
    - 作品信息缺失/为空
    - 序号跳号（`#1, #3` 缺 `#2`）
    - 命名冲突被自动加 `(2)` 的情况
    - 无 #N 前缀的零散文件
    - 文件名被 Windows 非法字符清洗的

# Task Dependencies
- Task 1 完成后才能开始 Task 2
- Task 2 与 Task 3 可以并行（一个处理 `#N` 文件，一个处理零散文件），但都依赖 Task 1
- Task 4 依赖 Task 2 + Task 3 的结果
- Task 5 依赖 Task 4
- Task 6 依赖 Task 5
