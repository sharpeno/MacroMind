# Phase 1.6 — Golden Regression 与最终 Gate

本阶段依据 `MacroMind Codex Phase 1 Engineering Plan.md` 第十一至十四节执行。目标是验证工程基础能否安全承接 Batch Pilot，不是提炼 9527 方法、生成 Analyst Skill 或进入生产。

## 执行范围

新增 `tests/golden_regression/` 与 `scripts/verify_phase1_6.py`；不改 Frozen、Registry、既有运行时代码、原始 Golden、历史人工裁决或过去验收材料。既有 1531 个文件及原计划的哈希在 `phase1/phase1_6_input_hashes.json` 固定。此前 Phase 1.5C 的 524 个产物重新校验。旧测试身份清单为 532 项。

正式执行：在 `macro-mind-engine` 下运行 `.venv/Scripts/python.exe scripts/verify_phase1_6.py`。脚本依次保存基础检查、五份真实适配结果、partial_bundle 与 complete_bundle 验证报告、真实 CLI 审计、GS005 三次重复、全量 pytest/JUnit、lint、格式检查和 G01–G20。每条子进程命令保存 argv、cwd、退出码、stdout、stderr。历史失败不删除、不写成通过。

旧 Runner 包里的 `phase1_6_executed=false` 是 Phase 1.5C 独立组件的固定覆盖声明；外层 1.6 Gate 记录本次实际执行。不能为改变这个显示而改写已验收组件。

## 样本与语义覆盖

| 样本 | 真实语义检查 | 限制与补充 |
|---|---|---|
| GS001 | summary-only、来源冲突、预测与时间窗口表述保留，禁止重建不存在对象 | partial fixture；Expectation/Population、Claim 时间、modal strength 没有真实字段级全覆盖。已有 schema/forecast/provenance 测试及新增 synthetic 测试只能证明规则，不能补造真实证据 |
| GS002 | Event 不自动升格 StructuralProcess；增量/存量 population 原文和隔离项区分；AR01 推理链；候选 Heuristic 不升格 | 旧 candidate_only 无精确枚举映射时维持 unknown；隔离中的 Claim、Observation 不算完成迁移 |
| GS003 | 来源版本 capture/content 时间分离；滚动报道不是自动矛盾；基础设施 Event 子型；AR05 物理仓储与政治期限的限制保留 | 部分 Scenario/边限制只存在原始材料与 sidecar，不能声称已经成为可执行语义字段；通用 Scenario/Forecast 规则由独立测试覆盖 |
| GS004 | MS01 first_observation/uncertain；MS02 未来 prior 隔离；共享机制归属 unknown；OB20 不把 % 转 pp；模型推理不归给作者 | 原始“accepted”不是当前 Validator 通过的证明；局部错误和缺失引用阻塞 |
| GS005 | C005 仅 Scenario；显式不准入原因；M01–M04 技术/经济、回收/成本、订单/收入的原文与 model_diagnostic 归属；首次失败与 hotfix 历史均保留 | 语义保留与 synthetic ReviewState/SchemaValidity 测试并行；没有经济模型能力或完整引用闭合的承诺 |

不固定 WARNING 数量，不将历史 WARNING=80/69 当作验收标准。REAL 样本来自不可变原文件；命名为 `test_synthetic_*` 的构造测试只用于守卫规则，禁止统计为真实分析案例。

## Gate 判定

`CODEX-PHASE1-GATE-1` 逐项判定。`partial_bundle` 的零 ERROR 表示未发现局部硬错误，不表示“所有引用可解析”。完整模式用作缺口诊断：GS001 summary 不凭空要求迁移；GS002/003 可以保留保守 Adapter；但缺失引用仍必须在 G06 中显式记录，不能因为隔离或 partial 模式而消失。GS004/005 的 accepted 需按当前引擎重新证明，不复用历史通过结论。当前未定义可豁免的上下文闭合政策，因此 G16 不以 GS005 partial 零错误冒充完整通过。

语义契约修复、跨样本绑定、合法隔离例外，需要明确的变更方案及反例验证。优先建议保持 Frozen 和原始 Golden 不变，在版本化兼容规则/独立上下文中修复明确对应关系；不自动将 SourceSegment 替换为 Source，不编造缺失对象或研究者归属。

## Debt overlay（不覆盖历史 ledger）

- D02：保守 Adapter 已具备；真实对象仍大量隔离，不宣称全部迁移完成。
- D03：Scenario/Forecast 守卫存在；C005 决策锁定。真实输入不完整的限制仍保留。
- D04：时间守卫和样本编号反例存在；跨样本 prior 证据绑定仍未闭合。
- D07：Registry 可执行和负向验证沿用并重跑；引用契约问题不通过修改枚举掩盖。
- D11：Argument 图与归属验证沿用并重跑；真实边的未知归属仍未知。
- D16：比较基准、角色、阶段分离有测试；未补算 unknown 或把 3% 改为 3pp。
- D18：真实审计、回归与 Gate 证据已建设；只有 Gate 通过才能认为本阶段放行条件满足。
- D20：truth 与模型/作者边界守卫重跑；不代表现实命题已验证。
- D08、D12、D13、D14：仍留给 Batch Pilot 或 Pre-Skill，不在本阶段伪造正例或清零。

## 中断与续接

先读 `phase1/phase1_6_execution_progress.json`、最新 `run_*/invocation.json`、各 `.command.json`、JUnit 与 failure.txt；进度不是证明。复用已完成且哈希一致的只读报告，不重新创建基线。若调用进程尚在运行，先确认其输出；若已结束，按未完成阶段续接。新的正式全量验收使用新的 run 目录，保留旧失败与日志。最终报告见 `PHASE1_6_ACCEPTANCE_REPORT.md`（只有生成后才存在），机器结论见 `phase1_6_gate_result.json`。
