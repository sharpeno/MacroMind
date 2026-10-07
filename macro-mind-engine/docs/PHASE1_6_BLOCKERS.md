# Phase 1.6 阻塞与修复决策材料

这份报告只诊断，不修改历史文件、引用类型或人工决定。

## 1. GS004：12 处来源粒度冲突

当前字段只接受 Source，目标实际是 SourceSegment。片段不是整份来源；自动替换可能丢失证据定位。

| 对象 | 字段 | 当前目标 | 目标类型 | 片段显式所属 Source |
|---|---|---|---|---|
| MU01 | /source_refs/0 | SS-C026 | SourceSegment | S03 |
| MU01 | /source_refs/1 | SS-C027 | SourceSegment | S03 |
| MU02 | /source_refs/0 | SS-C065 | SourceSegment | S03 |
| MU02 | /source_refs/1 | SS-C066 | SourceSegment | S03 |
| MU02 | /source_refs/2 | SS-C073 | SourceSegment | S03 |
| MU03 | /source_refs/0 | SS-C062 | SourceSegment | S03 |
| MU03 | /source_refs/1 | SS-C077 | SourceSegment | S03 |
| MU03 | /source_refs/2 | SS-C078 | SourceSegment | S03 |
| OB11 | /comparison_basis/baseline_source_ref | SS-C017 | SourceSegment | S03 |
| OB12 | /comparison_basis/baseline_source_ref | SS-C017 | SourceSegment | S03 |
| OB23 | /comparison_basis/baseline_source_ref | SS-C045 | SourceSegment | S03 |
| OB24 | /comparison_basis/baseline_source_ref | SS-C045 | SourceSegment | S03 |

## 2. 引用未闭合

完整模式缺失引用位置数：GS002 74、GS003 13、GS004 36、GS005 33。GS004 另有上述 12 处类型冲突。总计 156 个缺失引用位置，不等于 156 个不同对象。

逐条诊断在 `phase1/phase1_6_evidence/run_001/reference_diagnosis.json`。精确匹配隔离项只是定位线索，不能视为该对象已合法进入 canonical bundle。没有匹配也不证明原始资料绝对不存在，可能是外部 prior、格式不兼容或缺失声明。

## 3. 建议的下一步：独立兼容修复批次

1. 保持 Frozen、原始 Golden 和历史人工裁决不变。建立版本化兼容投影和逐条映射记录。
2. 对 12 处冲突，先核对原始字段的真实含义。若字段只需要来源身份，可在派生投影中沿显式 source_ref 取 Source，同时保留原始 SourceSegment 证据链；若字段意图就是精确片段，则需要显式修改引用契约并增加正反例。不能混用两者。
3. 对隔离导致的缺失，逐对象查必填语义是否真实存在。只迁移可证明对象；其余保持隔离并明确验收覆盖范围。
4. 对跨样本 prior，建立明确命名空间、内容时间和来源哈希的上下文绑定；不得用样本编号、模糊文本或摘要伪造对象。
5. 如希望部分历史样本按 partial-only 放行，需要明确修改 G06/G15/G16 的适用范围。这是验收政策变更，不是修复程序；本轮未这样处理。

推荐采用以上兼容修复批次，再重跑受影响测试及 Gate。另一选择是明确批准 partial-only 验收范围，但会保留引用完整性限制。尚未执行任何一种语义/政策变更。

## 4. 与整体目标的关系

本轮没有转向投资预测或替你决定博主观点。它检查的是分析链能否追溯到正确资料、未知是否保留、AI 推理会不会冒充博主观点。引用未闭合会影响你要求的分析过程溯源，因此在 Batch Pilot 前暴露并修复是必要步骤。仍未进入分析框架提炼、任意分析者切换或可视化界面阶段。
