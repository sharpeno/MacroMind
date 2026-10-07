# Phase 1.6 正式验收报告

结论：**NOT_READY_ENGINEERING_BLOCKER**。回归与验收已执行；Phase 1 尚未放行，未开始 Batch Pilot。

## 验证结果

- 原有 532 项测试：全部通过，缺失/失败/错误/跳过均 0。
- 新增 35 项：34 通过、1 失败；合计 567 项，566 通过、1 失败、0 跳过。
- 唯一 pytest 失败：`test_accepted_golden_passes_current_validator[GS004]`。12 处 Source/SourceSegment 引用类型冲突，没有跳过或标成预期失败。
- 全量 lint、新增文件格式检查均退出 0。最终脚本单独 lint/格式检查也为 0。
- 1531 个基线文件无变动；Phase 1.5C 524 个产物哈希无差异；原计划哈希不变。
- 五份 REAL CLI 审计及 GS005 三次重复均完成，并通过审计包完整性校验。所有 CLI 返回 1（存在阻塞或不确定），不是无错误成功。
- GS005 三次 normalization/pattern/continuity/run 语义哈希相同，三份运行 manifest 哈希不同。真实连续性输入为空，不证明跨期观点分析已经完成。

## G01–G20

| Gate | 要求 | 结果 | 证据（相对 run_001） |
|---|---|---|---|
| G01 | Frozen Contract integrity | PASS | foundation.json; integrity_after.json |
| G02 | 14 Core executable models | PASS | foundation.json; test_report.json |
| G03 | Required Auxiliary models | PASS | foundation.json; test_report.json |
| G04 | Registry loads | PASS | foundation.json; test_report.json |
| G05 | Validator deterministic | PASS | test_report.json |
| G06 | All references resolvable | FAIL | reference_findings.json |
| G07 | Temporal validator active | PASS | test_report.json |
| G08 | Scenario/Forecast validator active | PASS | test_report.json |
| G09 | Truth propagation guard | PASS | test_report.json |
| G10 | Reasoner attribution validator | PASS | test_report.json |
| G11 | Legacy schema detection | PASS | sample_summary.json; test_report.json |
| G12 | GS001 conservative adapter | PASS | GS001.adaptation.json; test_report.json |
| G13 | GS002 adapter | PASS | GS002.adaptation.json; test_report.json |
| G14 | GS003 adapter | PASS | GS003.adaptation.json; test_report.json |
| G15 | GS004 accepted passes | FAIL | GS004.partial_bundle.validation.json |
| G16 | GS005 accepted passes | FAIL | GS005.complete_bundle.validation.json |
| G17 | Original Goldens byte unchanged | PASS | integrity_after.json |
| G18 | Audit bundle reproducible | PASS | reproducibility.json; replay_results.json |
| G19 | Unknown not auto-filled | PASS | test_report.json; *.adaptation.json |
| G20 | Golden regression suite PASS | FAIL | test_report.json; tests.xml |

16 项 PASS，4 项 FAIL：G06 引用未闭合；G15 GS004 当前验证失败；G16 GS005 未证明完整包通过；G20 Golden suite 因 GS004 失败。GS005 的 partial_bundle 零 ERROR 与 G16 完整验收失败并不矛盾。

## 五份真实样本

| 样本 | canonical 对象 | 隔离项 | partial ERROR | complete ERROR | 审计记录 | 工程 Pattern |
|---|---:|---:|---:|---:|---:|---:|
| GS001 | 0 | 0 | 0 | 0 | 38 | 38 |
| GS002 | 228 | 345 | 0 | 74 | 26898 | 253 |
| GS003 | 378 | 342 | 0 | 13 | 35333 | 264 |
| GS004 | 563 | 247 | 12 | 48 | 45043 | 398 |
| GS005 | 680 | 141 | 0 | 33 | 40867 | 358 |

GS001 是 partial summary：空对象包的零错误不等于真实对象全部验证通过。GS002/003 的 Adapter 可用不等于已经完整迁移。以上 Pattern 是工程问题聚合，不是 9527 的分析方法。

## 已完成与未完成

已完成：不可变基线与前置证据复核、真实 Golden 语义回归、双模式验证、五份 CLI 审计、重复稳定性、完整测试、逐项 Gate、阻塞定位、Debt/覆盖说明和原始输出保存。

未完成：12 处来源粒度冲突修复；156 个缺失引用位置的处置（129 处有精确隔离 ID 候选匹配，27 处无精确隔离 ID 匹配）；明确跨样本上下文与 partial fixture 的适用验收范围；修复后重新取得 G06/G15/G16/G20 通过。匹配数按引用位置计算，不是独立对象数。

## 下一步与决策

建议维持原验收标准，开展独立兼容修复批次：保留原件及历史裁决，在派生投影中保留精确片段证据，同时建立可证明的来源/跨样本引用绑定。对没有真实证据的字段继续保留 unknown。具体冲突与修复选项见 [阻塞报告](PHASE1_6_BLOCKERS.md)。本轮尚未修改引用契约或批准 partial-only 豁免。

这一步仍服务于原目标：让分析链能够追溯，防止 AI 补全被错当成博主观点。当前位置是“工程底座最终验收发现阻塞”，还没到 30–50 Episode 试运行、分析框架提炼、任意分析者切换或可视化产品。

## 证据与复现

- 执行入口：`scripts/verify_phase1_6.py`；cwd 为 macro-mind-engine。
- 正式证据：`phase1/phase1_6_evidence/run_001/`；每个 CLI/pytest/lint/format 均有 command.json、stdout、stderr，测试明细在 tests.xml/test_report.json。
- 双模式逐条报告：`GS00N.partial_bundle.validation.json` / `GS00N.complete_bundle.validation.json`。
- 逐条引用定位：`reference_findings.json` / `reference_diagnosis.json`。
- 本轮执行脚本快照：`verifier_executed_snapshot.py`；随后去掉了 G06 中不必要的“所有包必须非空”条件，因为原计划允许 GS001 summary-only。`gate_condition_review.json` 重新计算该条件，G06 仍 FAIL，总结论不变。
- 开发失败记录保留：development_001（5 项测试假设错误加 1 项真实失败）；development_002（重复序列化导致慢，已中止，最终测试缓存一次后完成）；verifier_001（导入路径错误）；没有以这些记录认定正式通过。
- 当前进度：`phase1/phase1_6_execution_progress.json`；下轮先读 Gate、阻塞报告与原始日志，不把进度当证明。
- 产物哈希目录：`phase1/phase1_6_manifest.json`，不自包含自身哈希。

## Debt

D02/D03/D04/D07/D11/D16/D18/D20 的工程能力与剩余限制见 [覆盖与 Debt 说明](PHASE1_6_GOLDEN_REGRESSION.md)。不覆盖历史 ledger、不声称全债务清零。D08/D12/D13/D14 保留到后续阶段。
