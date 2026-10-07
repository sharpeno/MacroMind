你现在要执行一次 **MacroMind GS005 → V0.3.1-MA.1 数据迁移**。

这不是重新抽取视频，也不是重新解释9527。

目标是：

> 在不改变原对象ID、不重写历史语料、不丢失原始字段和Provenance的前提下，根据MA.1补充审计，对现有GS005 JSON做确定性的Schema迁移与定点修正，并生成Validator结果和可审计Diff。

## 一、绝对禁止

不得：

1. 重新调用LLM生成Claims。
2. 重新生成对象ID。
3. 删除原始raw transcript。
4. 用模型知识修正历史Claim。
5. 把model_diagnostic转成9527历史Reasoning。
6. 自动把Review Queue对象判真或判假。
7. 自动决定C005是否进入Forecast Ledger。
8. 因字段未知而猜值。
9. 覆盖原GS005文件而不保留pre-migration版本。
10. 将Migration后的Schema合规错误解释成主播事实错误。

## 二、输入

读取：

- golden_sample_005.json
- golden_sample_005_ma1_supplement.md
- V0.3.1-MA.1 schema / registry / validation rules

首先复制：

golden_sample_005.json
→ golden_sample_005.pre_ma1.json

## 三、输出

生成：

- golden_sample_005.ma1_candidate.json
- migration/ma1/migration_log.jsonl
- migration/ma1/validation_before.json
- migration/ma1/validation_after.json
- migration/ma1/diff_summary.md
- migration/ma1/manual_review_queue.json

验证通过且人工确认前，不覆盖正式Golden。

## 四、执行10类迁移

### M01 Method Signal Migration

处理MS01–MS11。

增加/规范：

- domain
- transferability
- recurrence_status
- recurrence_match
- matched_prior_signal_refs
- matched_scope
- recurrence_evidence
- annotation_observer
- promotion_status

合法：

recurrence_status:

- first_observation
- repeated
- frequent
- candidate_pattern

recurrence_match:

- none
- exact
- partial
- analogous
- uncertain

禁止使用：

- limited_match
- first_observation_in_available_registry

如果原数据无法确定合法值：
使用最保守值，并记录Migration Log或Manual Review。

------

### M02 Method Recurrence Migration

规范MR01–MR13。

采用补充审计裁决：

- Candidate A = partial
- Candidate B = none
- Candidate C = partial
- Candidate D = partial

MR01和MR03降为uncertain。

未观察项正式使用none。

每个非none匹配必须保存：

- prior_ref
- current_signal_refs
- match_type
- matched_scope
- evidence_refs

不得把analogous当稳定规则复现。

------

### M03 Failure Signal Migration

处理MS07–MS09。

增加：

- observed_reasoner_id
- annotation_observer
- observed_action
- failure_assessment
- failure_type
- assessment_confidence
- promotion_status

建议：

MS07:
failure_type:

- unsupported_causal_jump
- scope_shift

MS08:
failure_type:

- unsupported_causal_jump

MS09:
failure_type:

- object_role_shift

这些是模型Assessment，不是9527自认错误。

------

### M04 Comparison Basis Migration

检查所有IndicatorObservation。

特别修复：

C025 / O01：

0.1属于ratio，不是delta。

delta_value = null

不要反推美元差额。

X10 / O13：

“降低到”还是“下降”未确定时：

delta_value = null

保留raw value。

所有Comparison Basis尽量保存：

- comparison_type
- baseline_value
- baseline_period
- baseline_source_ref
- delta_value
- delta_unit

未知使用null，不猜。

------

### M05 Semantic Role Migration

特别修：

X04 / I06 / O06：
盘前股价变化 → price

C066 / I05 / O05：
市值变化 → valuation

卫星数量：
优先volume，不自动capacity。

检查所有：

order
contract
backlog
revenue
capacity
asset
capex
operating_cost
cash_flow
profit
valuation
price
volume

禁止静默跨role。

------

### M06 Recognition Stage Migration

适用对象增加：

recognition_stage:

- planned
- contracted
- ordered
- committed
- delivered
- deployed
- utilized
- revenue_recognized
- cash_collected
- expensed
- depreciated
- impaired
- unknown

不知道即unknown。

不得为了字段完整强行推断。

“可复用20次”不得写成实际utilized 20次。

------

### M07 Veracity Migration

为Assessment增加独立：

verification_status:

- verified
- likely_true
- uncertain
- disputed
- likely_false
- false
- unverifiable

同时保留：

assessment_kind
detail
resolution_status

不得把：
forecast not evaluated

映射成：
unverifiable

不得把：
source supports statement

直接映射成：
verified reality

------

### M08 Argument Migration

处理AR01–AR17及DA01。

标准化：

- inference_modes
- expression_levels
- most_fragile_step
- inferential_distance
- creator_shortcuts

inferential_distance至少：

- edge_count
- longest_path_length
- model_bridge_count
- explicit_shortcut_count

DA01继续：

analysis_context = model_diagnostic

不得进入9527 Analyst Method evidence。

------

### M09 C005 Manual Forecast Review

不要自动修改C005。

创建：

manual_review_queue entry:

question:
“C005虽然低可结算，但是否存在真正的未来方向承诺，因此应同时进入Forecast Ledger？”

必须人工裁决。

Low resolvability本身不能成为排除Forecast的唯一原因。

------

### M10 Transcript / Metadata Migration

没有听音确认时：

不得把contextual normalization标成confirmed ASR error。

必要时增加：

normalization_status:
contextual_entity_normalization

asr_error_confirmed:
false

failure_origin:
unknown

最后再更新：

- README
- Summary
- Final Questions
- Validation metadata
- Prompt/version history

保留旧Prompt曾经截断的历史记录。

## 五、Validator

实现并运行：

R056–R063。

另增加：

V-MA101 MethodSignal合法枚举
V-MA102 非none recurrence必须有prior refs
V-MA103 partial/analogous/exact必须有matched_scope
V-MA104 failure必须有observed_reasoner_id
V-MA105 failure必须有annotation_observer
V-MA106 comparison对象完整
V-MA107 percent与percentage_points不混
V-MA108 recognition_stage字段完整
V-MA109跨semantic_role推理必须存在Argument Edge或Review
V-MA110 model_diagnostic不得进入AnalystMethodSignal证据

Validator输出：

- PASS
- FAIL
- WARNING

最终要求：

ERROR = 0

WARNING可以保留。

Unknown本身不是错误。

## 六、Diff

生成diff_summary.md。

按以下分类：

- added_fields
- changed_values
- normalized_enums
- manual_review_required
- untouched_objects

每一项必须列object_ref与migration rationale。

## 七、完成标准

完成后不得直接声明Core Ontology已Freeze。

只报告：

1. Migration是否完成。
2. Validator是否ERROR=0。
3. C005 manual review是否仍未处理。
4. 有多少Warning。
5. MA.1 compliance是否可以从partial_requires_revision升级。
6. 是否仍存在会误导机器使用的Schema错误。

如果Validator Error > 0：

保持：

golden_status:
extraction_complete_ma1_revision_required_review_pending_not_frozen

如果Error = 0但人工Review未完成：

使用：

golden_status:
ma1_migrated_validation_pass_manual_review_pending

只有人工验收后才能进入下一Freeze Readiness Audit。