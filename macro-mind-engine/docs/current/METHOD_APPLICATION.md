# 五项规则与首次应用

2026-10-05。用户授权的“方法固定＋现有新材料应用”已完成。

- [规则文档](../../phase1/method_application/run_001/FRAMEWORK.md)
- [应用阅读页](../../phase1/method_application/run_001/TRACE.html)
- [验收边界与实际结果](../../phase1/method_application/run_001/REPORT.md)
- [续接清单](../../phase1/method_application/run_001/PROGRESS.md)

规则和案例分别封存；检查器可以运行，但不自动生成语义推理。新闻仅有单一媒体报道，事实、基础判断、条件分支分开。未阅读EP006字幕，尚未对照博主观点；后续对照须另存版本，不能改写原答案。

复核结构时，在工程目录执行 `.venv/Scripts/python.exe -X utf8 phase1/method_application/run_001/check_case.py` 会重新写入确定性的validation.json；真正只读的文件一致性复核应读取manifest后计算哈希。不要在封存目录重跑verify.py，它会重写验证日志。

最新研究候选：[v0.2规则与应用](../../phase1/method_application/run_002/REPORT.md)，v0.1保留为历史基线。


2026-10-05 巴以材料开发首组：[报告](../../phase1/conflict_study/run_001/REPORT.md)。30份登记归档、15/15划分，454/455首组对照完成；13份开发材料与15份留出检验尚未完成。v0.2未修改。


巴以开发组15期现已读完：[剩余13期报告](../../phase1/conflict_study/run_002/REPORT.md)。形成6项方法候选，v0.2未修改；15份留出检验尚未启动。


[v0.3六项规则人工审阅页](../../phase1/framework_review/v03_draft_001/REVIEW.html)已生成，规则忠实度与系统证据边界分开选择。仍为待审草案，未替换v0.2。

最新：[v0.3两项修订复审](../../phase1/framework_review/v03_draft_002/REVIEW.html)。已接收第一版6项意见，4项认可、C03/C04按意见改写待复审；六项扩展连续证据与整期字幕入口。[修订与验证报告](../../phase1/framework_review/v03_draft_002/REPORT.md)。v0.2未改，留出检验未启动。


v0.3复审已获用户在对话中明确认可，六项规则与本轮展示的上下文审阅完成。[封存报告](../../phase1/framework_review/v03_frozen_001/REPORT.md) · [固定研究候选](../../phase1/framework_review/v03_frozen_001/framework.json)。旧v0.2和应用不变；下一步为分阶段留出检验，尚未读取留出字幕。


第472期首例留出对照完成：[交互审阅页](../../phase1/holdout_evaluation/run_001/TRACE.html) · [报告](../../phase1/holdout_evaluation/run_001/REPORT.md)。先封存答案再读643条字幕；方法部分对齐但核心推理有遗漏，三项对照待人工审阅。检索接触较晚摘要，不称严格盲测。472已曝光，其余14份未读，v0.3和旧答案未改。


第472期审阅已接收：R01/R03认可，R02按“身份—事件—态度—角色约束—动机”补充，待确认。[修订记录](../../phase1/holdout_evaluation/run_001_review_001/REPORT.md)。原封存答案与v0.3未改，其余14份未读。


第472期R02修订已获对话确认。第473期完成先封存再读551条字幕的对照：[审阅页](../../phase1/holdout_evaluation/run_002/TRACE.html) · [报告](../../phase1/holdout_evaluation/run_002/REPORT.md)。身份记录落实，但行动信号、预期传导及示范链有遗漏，待三项人工核对。此次运用吸收上一例反馈，不作为固定策略准确率样本。其余13份未读。


第473期审阅已归档：R03认可，R01/R02按用户提供的完整文本落实修订。[最新修订记录](../../phase1/holdout_evaluation/run_002_review_001/REPORT.md)。原TRACE为历史版本，最新以该记录为准；原答案与v0.3未改，其余13份未读。


第474期第三例已完成先封存答案、再读684条字幕的对照：[审阅页](../../phase1/holdout_evaluation/run_003/TRACE.html) · [报告](../../phase1/holdout_evaluation/run_003/REPORT.md)。情景区分、策略性表态与内部责任链有遗漏，三项待核对。责任争议、技术/概率前提与预测未独立验证；剩余12份未读，冻结规则与原答案未改。


第474期三项对照归纳均已获人工认可，无修改意见。[审阅接收记录](../../phase1/holdout_evaluation/run_003_review_001/REPORT.md)。通过范围为对照归纳；原分析仍有关键遗漏，事实/预测未验收。下一例475尚未启动，剩余12份未读；原答案和v0.3未改。


第475期第四例完成：[审阅页](../../phase1/holdout_evaluation/run_004/TRACE.html) · [报告](../../phase1/holdout_evaluation/run_004/REPORT.md)。先封存三种候选解释及观察/更新条件，再读655条；政策排序、隐藏渠道与时间窗口仍有差异，待三项审阅。其余11份未读，v0.3和原答案保持冻结。


第475期审阅已归档：R01/R02认可并附实质补充，R03要求修订；三项用户文本均已落实。[最新修订记录](../../phase1/holdout_evaluation/run_004_review_001/REPORT.md)。重点是政策目标与既有高息作用、未知资金机制不补造、主要矛盾排序及作者明确倾向。原答案/v0.3未改，剩余11份未读。



2026-10-07：方向已调整为观点内容还原与观点生成过程复现。[最新忠实复现入口](FIDELITY_ALIGNMENT.md)含目标、12项四期诊断、7项操作候选、8条局部状态、4个分层示例与独立提示。v0.3及旧答案保留，剩余11份未读；下一步为已曝光案例的三组开发对照，尚未执行模型实验。
