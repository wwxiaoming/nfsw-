# Checklist: 将 2 份 sub-agent 文档按 6 批量拆分为交付物

## A. 文件夹创建检查
- [x] `documents/sub-agent-deliverables/` 已创建
- [x] `batch-01_战队特摄/` 已创建
- [x] `batch-02_勇者魔物奇幻/` 已创建
- [x] `batch-03_正太校园堕落/` 已创建
- [x] `batch-04_调教拍卖+异种触手/` 已创建
- [x] `batch-05_修真玄幻+外语/` 已创建
- [x] `batch-06_同人+女性向/` 已创建

## B. 12 份文档生成检查

### B.1 速查表 batch-01 至 batch-06
- [x] `速查表_batch-01_战队特摄.md` 生成（207 行）
  - [x] 含共享头部（500KB、拆段、易混淆、读取提示、完成回报、实测边界）
  - [x] **只**含"## 4. 批量 1：01_战队特摄（8 sub-agent）"段
  - [x] **不含**批量 2-6 段（grep 验证批量段总数=1）
  - [x] 可参考资源只列 xiaoyingxiong skill + `pixiv_深度阅读笔记_01_战队特摄.md`
- [x] `速查表_batch-02_勇者魔物奇幻.md` 生成（358 行）
  - [x] 含共享头部
  - [x] **只**含"## 5. 批量 2：02_勇者魔物奇幻（27 sub-agent）"段
  - [x] **不含**批量 1/3/4/5/6 段（grep 验证批量段总数=1）
  - [x] 可参考资源只列 xiaoyingxiong skill + `pixiv_深度阅读笔记_02_勇者魔物奇幻.md`
- [x] `速查表_batch-03_正太校园堕落.md` 生成（329 行）
  - [x] 含共享头部
  - [x] **只**含"## 6. 批量 3：03_正太校园堕落（24 sub-agent）"段
  - [x] **不含**批量 1/2/4/5/6 段（grep 验证批量段总数=1）
  - [x] 可参考资源只列 xiaoyingxiong skill + `pixiv_深度阅读笔记_03_正太校园堕落.md`
- [x] `速查表_batch-04_调教拍卖+异种触手.md` 生成（174 行）
  - [x] 含共享头部
  - [x] **只**含"## 7. 批量 4：04调教拍卖+05异种触手（4 sub-agent）"段
  - [x] **不含**批量 1/2/3/5/6 段（grep 验证批量段总数=1）
  - [x] 可参考资源只列 xiaoyingxiong skill + `pixiv_深度阅读笔记_04调教拍卖+05异种触手.md`
- [x] `速查表_batch-05_修真玄幻+外语.md` 生成（189 行）
  - [x] 含共享头部
  - [x] **只**含"## 8. 批量 5：06修真玄幻+07外语（6 sub-agent）"段
  - [x] **不含**批量 1/2/3/4/6 段（grep 验证批量段总数=1）
  - [x] 可参考资源只列 xiaoyingxiong skill + `pixiv_深度阅读笔记_06修真玄幻+07外语.md`
- [x] `速查表_batch-06_同人+女性向.md` 生成（187 行）
  - [x] 含共享头部
  - [x] **只**含"## 9. 批量 6：08同人+09女性向（4 sub-agent）"段
  - [x] **不含**批量 1/2/3/4/5 段（grep 验证批量段总数=1）
  - [x] 可参考资源只列 xiaoyingxiong skill + `pixiv_深度阅读笔记_08同人+09女性向.md`

### B.2 输入输出规范 batch-01 至 batch-06
- [x] `输入输出规范_batch-01_战队特摄.md` 生成（235 行）
  - [x] 完整保留 13 元素灵活模板
  - [x] 完整保留 Step 0-8 / V1/V2/V3 / Key Decisions / 风险 / 关系图
  - [x] 可参考资源只列 xiaoyingxiong skill + `pixiv_深度阅读笔记_01_战队特摄.md`
- [x] `输入输出规范_batch-02_勇者魔物奇幻.md` 生成（235 行）
  - [x] 完整保留 13 元素灵活模板
  - [x] 完整保留 Step 0-8 / V1/V2/V3 / Key Decisions / 风险 / 关系图
  - [x] 可参考资源只列 xiaoyingxiong skill + `pixiv_深度阅读笔记_02_勇者魔物奇幻.md`
- [x] `输入输出规范_batch-03_正太校园堕落.md` 生成（235 行）
  - [x] 完整保留 13 元素灵活模板
  - [x] 完整保留 Step 0-8 / V1/V2/V3 / Key Decisions / 风险 / 关系图
  - [x] 可参考资源只列 xiaoyingxiong skill + `pixiv_深度阅读笔记_03_正太校园堕落.md`
- [x] `输入输出规范_batch-04_调教拍卖+异种触手.md` 生成（235 行）
  - [x] 完整保留 13 元素灵活模板
  - [x] 完整保留 Step 0-8 / V1/V2/V3 / Key Decisions / 风险 / 关系图
  - [x] 可参考资源只列 xiaoyingxiong skill + `pixiv_深度阅读笔记_04调教拍卖+05异种触手.md`
- [x] `输入输出规范_batch-05_修真玄幻+外语.md` 生成（235 行）
  - [x] 完整保留 13 元素灵活模板
  - [x] 完整保留 Step 0-8 / V1/V2/V3 / Key Decisions / 风险 / 关系图
  - [x] 可参考资源只列 xiaoyingxiong skill + `pixiv_深度阅读笔记_06修真玄幻+07外语.md`
- [x] `输入输出规范_batch-06_同人+女性向.md` 生成（235 行）
  - [x] 完整保留 13 元素灵活模板
  - [x] 完整保留 Step 0-8 / V1/V2/V3 / Key Decisions / 风险 / 关系图
  - [x] 可参考资源只列 xiaoyingxiong skill + `pixiv_深度阅读笔记_08同人+09女性向.md`

## C. 内容一致性检查
- [x] 6 份速查表的"共享头部"措辞完全一致
- [x] 6 份输入输出规范的"主体内容"完全一致
- [x] 12 份文档与原 2 份文档措辞一致
- [x] 12 份文档中不出现"必含/必标/强制减分/严禁"硬指标（grep 验证）
- [x] 12 份文档中不出现新硬约束

## D. 用户硬约束检查
- [x] 只新增 12 份文档，不改原 2 份文档
- [x] 6 个文件夹已创建
- [x] 每文件夹 2 份文档
- [x] 速查表只含该批量 SA-XX-X（grep 验证批量段总数=1）
- [x] 输入输出规范完整保留 13 元素模板（grep 验证）
- [x] 可参考资源裁剪为该批量专属笔记
- [x] 措辞完全一致
- [x] 不引入新硬约束

## E. 交付物清单检查
- [x] `sub-agent-deliverables/batch-01_战队特摄/` 存在
- [x] `sub-agent-deliverables/batch-02_勇者魔物奇幻/` 存在
- [x] `sub-agent-deliverables/batch-03_正太校园堕落/` 存在
- [x] `sub-agent-deliverables/batch-04_调教拍卖+异种触手/` 存在
- [x] `sub-agent-deliverables/batch-05_修真玄幻+外语/` 存在
- [x] `sub-agent-deliverables/batch-06_同人+女性向/` 存在
- [x] 每文件夹 2 份文档（速查表 + 输入输出规范）
- [x] 总计 12 份文档（find 验证）
