# 目录地图与归档规则

## 工作区

| 位置 | 用途 | 整理策略 |
|---|---|---|
| START_HERE.md、MACROMIND_MASTER_STATE.md | 人的总入口和状态索引 | 导航到工程当前文档，不再复制多份进度 |
| 核心主旨.md | 核心目标 | 原位保留 |
| macro-mind-engine/ | 可执行工程 | 代码、测试、当前文档和证据分层 |
| batch_pilot_materials/ | 首五期原始素材与引用 | 保留原位；原文不覆盖 |
| golden_sample_test/ | 冻结本体、历史样本 | 保留被工程引用的原路径 |
| codex迭代/、prompt/、迭代/ | 计划、执行Prompt及历史设计 | 历史参考，不作为当前验收证明 |
| review-ui-qa/ | UI测试脚本与合成审核导出 | 不能作为用户真实审核意见 |

其他个人资料不属于本次工程整理范围。

## 工程内部

| 位置 | 职责 |
|---|---|
| README.md → docs/current/ | 唯一当前说明入口；STATUS/STRUCTURE/OPERATIONS分工 |
| src/、tests/ | 运行时代码和测试 |
| contracts/、registries/、schemas/ | 契约索引、权威词汇、生成结构 |
| scripts/operations/ | 新的只读运行导航工具 |
| scripts/其余既有脚本 | 编译、导出及各阶段验收入口，原路径兼容 |
| docs/既有阶段文档 | 当时的设计与验收说明，保持历史语义 |
| phase1/*_evidence/、phase1_acceptance_evidence/ | 各阶段原始证据与报告 |
| phase1/batch_pilot/run_*/ | 各版数据、diff、审计和封存清单；每个版本保留 |
| phase1/batch_pilot/human_reviews/ | 人工导出原件、接收记录和处理结果 |
| phase1/batch_pilot/review_*/ | 每轮审阅包，不能把旧页面当最新任务 |
| phase1/extraction_quality/ | 质量规则、自检试验和校准版本 |
| maintenance/<日期_主题>/ | 跨阶段维护的基线、命令、原始输出和报告 |

采用“统一入口、逻辑分层、原位归档”，没有把封存运行目录搬入archive：大量清单、审计引用和脚本依赖原路径，搬动会改变可复现条件。也不创建一份current数据副本或系统软链接，避免后续更新分叉。

## 以后如何放文件

1. 新素材放对应材料批次；审核导出按现有human_reviews接收流程归档，Downloads只是临时中转。
2. 新编译、审核、校准使用独立版本目录，保留输入清单、差异、命令、输出和封存哈希。
3. 完成相应验收后更新既有revision_latest/review_latest/extraction_quality latest指针，再运行project_status检查一致性。指针不一致时停止宣称“当前版本完整”。
4. 当前说明只放docs/current；历史报告不追改。跨阶段整理只写maintenance，不伪装成新的业务验收阶段。
5. 不删除质量编译试验或合成反馈：它们可能已被清单引用。缓存和虚拟环境不属于证据；本轮未清理它们。
