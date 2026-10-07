# Phase 1.6R 修复验收报告

结论：**READY_FOR_BATCH_PILOT**，仅针对用户批准的当前可用投影。原始 Phase 1.6 的 NOT_READY 报告未改写。Batch Pilot 尚未开始，Analyst Model / Skill / Production 仍 NOT_READY。

## 本轮改变

- 新增独立启用的兼容规则 1.0：可确定的年份格式转换；来源身份与精确片段双重保留；缺失引用或错误对象隔离；依赖及推理结论逐轮传播；人工修复池。
- 未修改旧适配器、Validator、Registry、Frozen、原始 Golden 或历史人工裁决。旧测试的两个 accepted 验收分支明确转为新政策，同时保留 GS004 原始类型错误断言。
- 唯一已存在文件改动：tests/golden_regression/test_golden_semantic_regression.py；新增运行时、测试、验证脚本、报告及证据。

## 验证

- 584 项全部通过：既有 532 项，加 Golden/activation 52 项；无失败、错误、跳过，既有测试身份无缺失。
- 全量 lint 与新增文件格式检查通过。
- 五份真实样本转换与完整模式验证已保存。GS001 无可用对象，CLI 返回 1；其余返回 0，表示非空引用闭合数据，不表示事实已核实。
- GS005 三次激活语义哈希一致；GS002–005 的 CANONICAL 审计均完成，GS005 重复审计语义哈希一致。审计发现的不确定性仍保存，未改写为零问题。
- 基线 1843 个文件只出现上述授权测试修改；此前 1.5C 的 524 个产物哈希仍一致。

## 真实数量

| 样本 | 历史对象 | 当前可用 | 对象待修复/隔离 | 实际可用范围 |
|---|---:|---:|---:|---|
| GS001 | 0 | 0 | 0 | 只有摘要，另有 1 条摘要待修复记录 |
| GS002 | 573 | 194 | 379 | 来源、片段、主体、指标；无完整分析链 |
| GS003 | 720 | 26 | 694 | 仅 26 个主体对象；不可用作分析案例 |
| GS004 | 810 | 524 | 286 | 保留 131 Claim、17 Argument、20 Scenario 等 |
| GS005 | 821 | 658 | 163 | 保留 139 Claim、18 Argument、17 Scenario 等 |

合计历史对象 2924 个：1402 个进入引用闭合投影，1522 个对象隔离；另保留 GS001 摘要条目，人工修复池共 1523 条。数量守恒逐样本验证，没有丢失被隔离原文。

## 三个具体修复结果

1. **12 处 SourceSegment → Source 字段冲突**：依据显式父来源作投影，原片段及其哈希仍保留为必要依赖。相关对象还依赖缺失的 Mechanism / Indicator，因此最终全部留在待修复池；并未把这 12 次转换说成 12 个可用对象。
2. **GS005 C092 年份格式**：保留原有 2022、2026 年信息为不解析的时间文本，不补造日期和时区；C092 已恢复为可用 Claim，AR13 仍在可用推理链内。
3. **跨样本 prior 与不完整资料**：不猜测、不改写为空数组后继续使用；整项隔离并传播影响。GS001 不生成假对象，GS002/003 不冒充完整正例。

## 修订 Gate

| Gate | 当前结果 | 解释 |
|---|---|---|
| G01 | PASS | Frozen Contract integrity |
| G02 | PASS | 14 Core executable models |
| G03 | PASS | Required Auxiliary models |
| G04 | PASS | Registry loads |
| G05 | PASS | Validator deterministic |
| G06 | PASS | 按当前可用链验收，历史与隔离材料不在启用范围 |
| G07 | PASS | Temporal validator active |
| G08 | PASS | Scenario/Forecast validator active |
| G09 | PASS | Truth propagation guard |
| G10 | PASS | Reasoner attribution validator |
| G11 | PASS | Legacy schema detection |
| G12 | PASS | GS001 conservative adapter |
| G13 | PASS | GS002 adapter |
| G14 | PASS | GS003 adapter |
| G15 | PASS | 按当前可用链验收，历史与隔离材料不在启用范围 |
| G16 | PASS | 按当前可用链验收，历史与隔离材料不在启用范围 |
| G17 | PASS | Original Goldens byte unchanged |
| G18 | PASS | Audit bundle reproducible |
| G19 | PASS | Unknown not auto-filled |
| G20 | PASS | 完整回归和新政策反例通过 |

这是经过用户批准的验收范围修订，不是旧历史数据突然全部变得有效。GS004/005 的旧包仍有诊断问题；以新投影取代其直接进入分析的资格。

## 剩余限制与下一步

- active_bundle 是结构上可用，不是所有内容已经证实。GS002/004/005 分别仍有 131 / 412 / 565 条非引用 INDETERMINATE，完整原始报告保留；不能据此自动推断时间顺序、事实真伪或已验证方法。
- 1523 条池记录有稳定编号、来源哈希、原始路径、原因及恢复条件。人工补证或经审核的转换后再重算，不能直接改状态放行；历史明确排除项仍锁定。
- 下一阶段可开展受控 Batch Pilot，但选样必须有实际分析链及所需证据；GS001–003 当前不能作为完整分析能力的正例。不是立即部署或创建 Analyst Skill。

## 证据路径

- 运行入口：src/macromind/compatibility/activation.py；用法见 PHASE1_6R_ACTIVATION_POLICY.md。
- 本轮证据：phase1/phase1_6r_evidence/run_001/；命令、退出码、stdout/stderr、tests.xml、逐样本 activation、active_bundle、repair_pool、validation、真实审计包均保存。
- 机器 Gate：phase1/phase1_6r_gate_result.json；人工池索引：phase1/phase1_6r_manual_repair_pool.json。
- 历史基线：phase1/phase1_6r_input_hashes.json；产物哈希：phase1/phase1_6r_manifest.json。
- 首轮正式验证曾要求 GS002 也必须含推理对象，因其保守投影只剩背景对象而停止；按原计划允许 legacy partial fixture，改为要求 GS004/005 必须保留实际分析对象，再从完成的样本输出续接。初次脚本快照、失败日志和修改后的 invocation 均保留。此修正没有改变实际样本输出、过滤逻辑或旧 Validator。
