# Phase 1.6R：可用链与待修复池（政策 1.0）

本轮依据用户明确批准的方案执行：未能连接、无歧义转换或提供充分原始信息的材料，当前不可用；原文保留，等待补证或人工修复。NOT_USABLE 不等于事实为假，也不等于已经证明资料不存在。

## 与上一轮验收的关系

旧 Gate、报告和失败原始输出保持原样。新 Gate 在 `phase1/phase1_6r_gate_result.json`，修订标识为 `USER_APPROVED_ACTIVE_CHAIN_POLICY_1.0`。G06/G15/G16 的检查范围是当前启用的派生数据，而不是全部历史资料；G20 同时检查历史诊断仍存在与新派生链完整。不是通过放宽 Validator 的类型检查来消除错误。

旧运行时、Frozen、Registry、Golden 原文件均不修改。旧 Golden 测试里 GS004/005 的验收项已显式改为：先确认历史诊断，再验证用户批准的激活投影；没有 skip、xfail 或删除失败案例。既有 532 项测试继续全量运行。

## 可执行入口

在 macro-mind-engine 下执行：

```powershell
.venv/Scripts/python.exe -m macromind.compatibility.activation --input <原始文件> --output <新的.activation.json> --contract-root ../golden_sample_test/core_ontology/v0.3 --registry-root registries/v0_3
```

必须指定新输出文件，已有文件拒绝覆盖。退出码 0 表示存在引用闭合的可用对象；1 表示没有可用对象（如 GS001 摘要）；2 表示输入、输出或执行失败。0 不代表事实已证实或全部历史资料已导入。

结果同时包含原文、格式转换后的副本、旧适配器结果、转换记录、精确来源片段、可用数据包、依赖图、隔离轮次、待修复池和完整 Validator 报告。下游读取 `active_bundle`；不能把 `raw_document`、`prepared_document`、`adaptation.canonical_bundle` 或 `repair_pool` 当作已经启用的证据。归档时应保留整个 activation 文件，不能只保存裸 active_bundle 丢失来源修复记录。现有 LEGACY 审计入口保持历史行为；新规则需要明确启用。

## 转换与隔离规则

1. 对已知时间字段，仅当旧值是由四位数字年份组成的 start/end 字典且没有其他属性时，转成保留原字典内容的时间文本。具体 start/end 时间戳保持空，禁止补造日期、时区或精确时间。原值与新值均记录。
2. MechanismUsage.source_refs 和 IndicatorObservation.comparison_basis.baseline_source_ref 明确要求来源身份。当目标是 SourceSegment，且该片段显式所属 Source 存在时，可以投影到该 Source。片段本身仍作为强制依赖保留；片段或其版本失效时，使用者也失效，不能靠引用整份来源绕过缺口。
3. 完整 Validator 报错的对象、引用解析不确定的对象，以及原始证据依赖不可用的对象，整项进入待修复池。不通过清空错误引用来留用结论。
4. 重复检查至无新增隔离：被隔离对象的引用者也要隔离。若推理链失效，其记录的中间及最终结论也隔离，再传播给下游引用者。采取保守策略，不假设尚未明确核实的替代证据能支持该结论。
5. 不自动连接跨样本 prior，不用编号推断年代，不把摘要制造成完整历史对象。材料补充后必须重新计算闭合并验证，修改池中状态字符串不能重新启用。
6. 原有明确历史排除决定继续保留；待修复不表示可以擅自推翻该决定。

## 可用范围与不确定性

引用闭合是结构条件，不代表每条事实已核实、每个时间已明确或每种方法已验证。原 Validator 允许的 unknown、非引用类 INDETERMINATE 和 WARNING 继续显示，不转为 PASS、不补齐数值或作者归属。使用时必须遵循这些限制；不得因此声称可用于已验证的方法归纳或时间先后判断。

GS001 只有摘要，不启用任何对象。GS002/GS003 本轮仅保留背景性对象，不能当作完整的分析链正例。GS004/GS005 保留非空的 Claim、Argument、Scenario 等；这证明没有通过清空所有数据实现表面放行。Analyst Model、Skill、Production 仍 NOT_READY。

## 人工待修复池

`phase1/phase1_6r_manual_repair_pool.json` 是人工索引；完整原文在各样本 activation/repair_pool 文件中。每条有来源哈希、原始路径、原因、依赖、状态与恢复条件。修复时补充证据或提出有版本的明确转换规则，然后重新运行，保留旧结果作为历史。不删除原件，不静默写入 Accepted Golden。

## 验证与续接

`verify_phase1_6r.py` 保存各命令、stdout/stderr、JUnit、真实审计结果和 Gate。先查看 `phase1_6r_progress.json`、最新原始输出及命令退出码。该脚本的 --resume 支持复用已完成且哈希验证一致的样本激活输出；后续阶段中断时，应先检查已存在文件及日志，不能直接覆盖或盲目从头重跑。进度记录不是通过证明。
