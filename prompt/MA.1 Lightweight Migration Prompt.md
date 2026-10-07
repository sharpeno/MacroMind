你正在执行 MacroMind 项目的 Golden Sample #004（GS004）
V0.3.1-MA.1 Lightweight Migration。

这不是一次新的内容分析任务，不是重新抽取任务，不是重新解释视频，
也不是重新生成 Golden Sample。

你的任务是：

将现有 GS004 从其原始结构，确定性迁移到
MacroMind V0.3.1-MA.1 数据契约，
使其能够参与后续 Freeze Readiness Audit #001–#005。

============================================================
0. 核心任务定义
============================================================

任务名称：

GS004-MA1 Lightweight Migration

目标：

在不改变 GS004 历史语义、不重新生成核心对象、
不重新解释原视频的前提下：

1. 审计 GS004 与 V0.3.1-MA.1 的Schema差距；
2. 对确定性字段进行结构迁移；
3. 将无法确定的语义问题进入 Manual Review；
4. 运行 MA.1 Validator；
5. 输出 Migration Candidate、Diff、Validation、Review Queue；
6. 为后续 Human Finalization 做准备。

本任务的核心原则：

Old Golden
→ deterministic schema migration
→ candidate
→ diff
→ validator
→ manual review

而不是：

Old Golden
→ LLM重新分析
→ 新Golden

============================================================
1. 输入文件
============================================================

优先使用以下实际项目文件。

必须以本地真实文件为准，不得根据本Prompt伪造文件内容。

主要输入：

1.
golden_sample_004.json

如果项目中实际文件名不同，
先定位GS004正式JSON并记录真实路径。

2.
golden_sample_004_report.md

用于理解既有对象、limitations、Review Queue及迁移语义，
但不得使用Report重写原JSON已经存在的历史对象。

3.
V0.3.1-minor.md

作为 MA.1 Schema / Rule 依据。

4.
MacroMind V0.3.1-MA / MA.1相关规范文件

如果存在独立：
- schema
- registry
- validator rules
- ontology patch
则全部读取。

5.
Golden #001–#003 的 Method / Heuristic / Thesis Registry
仅用于 GS004 的历史先例比较。

6.
GS005 MA.1 accepted/finalized JSON

允许用途仅限：

- 参考MA.1字段结构
- 参考Migration工程模式
- 参考Validator格式
- 参考unknown/null处理方式

严禁将GS005作为GS004的历史 recurrence prior evidence。

GS005发生在GS004之后。

因此：

GS004 → GS005

可以在GS005中说“复现了GS004”。

但不得反过来在GS004中写：

GS005证明GS004已经repeated。

这属于 future-sample leakage。

如果某个输入文件缺失：

不得猜测其内容。

记录：

input_missing

并在最终报告中说明具体缺失内容和受到影响的迁移部分。

============================================================
2. 不可违反的迁移原则
============================================================

本次迁移必须遵守以下Hard Constraints。

------------------------------------------------------------
2.1 不重新抽取
------------------------------------------------------------

禁止：

- 重新观看/重新分析视频后生成新的Claim
- 重新从Transcript创建Claim
- 创建新的Argument来“改善”原分析
- 创建新的Thesis
- 创建新的Forecast
- 创建新的Scenario
- 创建新的MethodSignal

除非原对象实际上已经存在，
此次仅补MA.1字段。

------------------------------------------------------------
2.2 不重新生成ID
------------------------------------------------------------

所有现有对象ID必须保持。

包括但不限于：

Claim ID
Argument ID
MethodSignal ID
Mechanism ID
Forecast ID
Scenario ID
Assessment ID
Source ID
SourceSegment ID
Review ID

禁止为了统一Schema重新编号。

------------------------------------------------------------
2.3 不改变历史语义
------------------------------------------------------------

Schema migration ≠ semantic rewriting。

例如：

旧对象缺少：

semantic_role

允许：

semantic_role: unknown

不允许：

根据模型理解将其猜成revenue/profit/cost。

旧对象缺少：

recognition_stage

允许：

recognition_stage: unknown

不允许：

根据常识猜：

deployed
utilized
revenue_recognized

------------------------------------------------------------
2.4 Unknown > Guess
------------------------------------------------------------

当现有GS004材料不足以唯一决定新字段时：

使用：

unknown
null
[]
Manual Review

不得猜测。

------------------------------------------------------------
2.5 保留Legacy
------------------------------------------------------------

如果旧字段值需要归一化：

保留：

legacy_<field>

或Migration Log中保存完整旧值。

不得静默覆盖。

------------------------------------------------------------
2.6 Model Reasoning不得变成Analyst Method
------------------------------------------------------------

必须严格区分：

analyst_youhegaojian9527

和

model_gpt6

任何：

model_reconstruction
model_diagnostic
model_bridge
model critique

不得直接作为9527 AnalystMethodSignal的方法证据。

------------------------------------------------------------
2.7 不使用GS005反向增强GS004
------------------------------------------------------------

这是本次迁移特别重要的规则。

GS004中任何：

recurrence_match
matched_prior_signal_refs
recurrence_evidence

只能使用在GS004当时已经存在的：

GS001
GS002
GS003

或更早证据。

禁止：

GS005/...

作为prior。

后续全局 Analyst Method Mining 可以在整个时间序列上判断：

GS004与GS005相互印证。

但这不属于GS004历史对象内部的recurrence状态。

============================================================
3. Phase A — Pre-Migration Gap Audit
============================================================

首先不要修改GS004。

读取全部GS004对象后生成：

gs004_ma1_gap_report.json

至少统计：

{
  "golden_id": "GS004",

  "claims": {
    "total": ...,
    "missing_semantic_role": ...,
    "missing_recognition_stage": ...,
    "incomplete_comparison_basis": ...
  },

  "indicators": {
    "total": ...,
    "missing_semantic_role": ...,
    "missing_recognition_stage": ...
  },

  "observations": {
    "total": ...,
    "incomplete_comparison_basis": ...,
    "missing_baseline_source_ref": ...,
    "missing_recognition_stage": ...
  },

  "arguments": {
    "total": ...,
    "missing_inference_modes": ...,
    "missing_expression_levels": ...,
    "missing_inferential_distance": ...,
    "missing_creator_shortcuts": ...,
    "missing_most_fragile_step": ...
  },

  "method_signals": {
    "total": ...,
    "missing_domain": ...,
    "missing_transferability": ...,
    "invalid_recurrence_status": ...,
    "missing_recurrence_match": ...,
    "missing_matched_scope": ...
  },

  "failure_signals": {
    "total": ...,
    "missing_observed_reasoner_id": ...,
    "missing_annotation_observer": ...,
    "missing_observed_action": ...,
    "missing_failure_assessment": ...,
    "missing_failure_type": ...
  },

  "veracity_assessments": {
    "total": ...,
    "missing_verification_status": ...
  },

  "future_sample_leakage_found": ...
}

此阶段只审计。

不得修改任何源对象。

============================================================
4. Migration M01

  Claim / Indicator / Observation MA.1规范化
  ============================================================

检查所有适用：

Claim
Indicator
IndicatorObservation

统一补充或规范：

semantic_role

recognition_stage

comparison_basis

comparison_basis最低正式结构：

{
  "comparison_type": "...",
  "baseline_value": null,
  "baseline_period": null,
  "baseline_source_ref": null,
  "delta_value": null,
  "delta_unit": null
}

允许comparison_type：

none
yoy
qoq
mom
sequential
versus_consensus
versus_guidance
versus_baseline
versus_prior_period
percentage_point_change
absolute_delta
indexed_to
other
unknown

不得将百分比与百分点混淆。

如果旧对象没有comparison：

comparison_type = unknown 或 none

根据现有MA.1规则选择，
不得为了填字段制造不存在的比较。

============================================================
5. Migration M02

  Semantic Role规范化
  ============================================================

使用MA.1正式角色：

demand
order
contract
backlog
obligation
revenue
cash_receipt
capacity
utilization
asset
capex
depreciation
impairment
operating_expense
operating_cost
cash_flow
profit
margin
valuation
price
volume
inventory
other
unknown

如果旧GS004使用：

technology
financial_metric
market_metric
business_metric
等旧/专用角色，

不得直接删除原语义。

采用：

semantic_role: other

semantic_role_detail:
  <legacy meaning>

或按照当前MA.1正式mapping执行。

必须在migration log中记录：

old role
new role
mapping reason

严禁：

price → valuation

capacity → utilization

order → revenue

revenue → cash_receipt

capex → profit

等无Argument支持的角色跳跃。

============================================================
6. Migration M03

  Recognition Stage
  ============================================================

适用Claim / Indicator / Observation补：

recognition_stage

正式值：

planned
contracted
ordered
committed
delivered
deployed
utilized
revenue_recognized
cash_collected
expensed
depreciated
impaired
unknown

原则：

许可 ≠ deployed

设计能力 ≠ utilized

订单 ≠ delivered

合同 ≠ revenue_recognized

收入 ≠ cash_collected

CapEx ≠ expensed

没有明确证据时：

unknown

不得根据常识补具体阶段。

============================================================
7. Migration M04

  Argument正式结构补齐
  ============================================================

对GS004全部Argument逐一检查。

在不改变原Argument逻辑的前提下补：

inference_modes: []

expression_levels: []

inferential_distance:
  edge_count:
  longest_path_length:
  model_bridge_count:
  explicit_shortcut_count:

distance_counting_rule:

creator_shortcuts: []

most_fragile_step:

规则：

inference_modes必须由现有Argument step/relation归纳，
不得创造新机制。

expression_levels只能来自已有：

explicit
strongly_implied
model_reconstruction

若Argument包含不同层级，
保留数组。

inferential_distance按现有stored steps计算。

不得“补逻辑”使Argument更合理。

------------------------------------------------------------
7.1 most_fragile_step
------------------------------------------------------------

只有当旧Argument现有材料能够明确定位具体脆弱step时，
才能填：

[
  "ARxx/steps/n"
]

如果原limitations只是整体描述：

“证据不足”
“存在替代解释”
“因果尚未验证”

但无法唯一定位具体step：

most_fragile_step: null

并创建：

MA1-FRAGILE-ARxx

Manual Review。

不得为了让Validator通过而猜。

------------------------------------------------------------
7.2 Creator Shortcut
------------------------------------------------------------

creator_shortcuts只能标记：

原分析师实际存在的推理跳跃。

模型为了组织Argument而添加的bridge不得标为：

creator shortcut

必须保持reasoner attribution。

============================================================
8. Migration M05

  AnalystMethodSignal升级
  ============================================================

对GS004全部MethodSignal执行MA.1规范化。

每个Signal至少增加：

domain:

transferability:

recurrence_status:

recurrence_match:

matched_prior_signal_refs: []

matched_scope:

recurrence_evidence: []

保留：

legacy_recurrence_status
legacy_promotion_status

如果旧值例如：

limited_match
first_observation_in_available_registry
candidate_not_stable_skill

不能直接作为新enum。

新recurrence_status只描述出现频次：

first_observation
repeated
frequent

新recurrence_match描述与历史方法匹配精度：

none
exact
partial
analogous
uncertain

再次强调：

recurrence_status
≠
recurrence_match

------------------------------------------------------------
8.1 recurrence precision
------------------------------------------------------------

exact：

核心分析动作、条件、变量高度一致。

partial：

只复现旧方法的一部分。

analogous：

结构性分析操作相似，
但变量/机制/对象不同。

uncertain：

可能相关，但证据不足。

none：

没有可支持的历史匹配。

不得使用：

“关注底层逻辑”
“看成本”
“看趋势”

这种泛化语言证明recurrence。

必须有：

matched_scope

说明具体哪一步相似。

------------------------------------------------------------
8.2 Future Sample Leakage Rule
------------------------------------------------------------

GS004的：

matched_prior_signal_refs
recurrence_evidence

不得出现：

GS005

或者任何晚于GS004的Golden。

如果原文件已经存在这种引用：

不得静默保留。

移入：

Manual Review

并记录：

future_sample_leakage

但不得使用GS005内容重新判断GS004当时的recurrence_status。

============================================================
9. Migration M06

  Failure Signal规范化
  ============================================================

如果GS004包含failure类型MethodSignal，
或现有MethodSignal明确被标记为推理失败候选，

补：

observed_reasoner_id:

annotation_observer:

observed_action:

failure_assessment:

failure_type: []

assessment_confidence:

failure_type正式值：

dimensional_error
scope_shift
denominator_shift
temporal_mismatch
unsupported_causal_jump
motive_overreach
analogy_overreach
object_role_shift
closed_explanation
other

原则：

observed_action
=
分析师实际做了什么。

failure_assessment
=
模型/审查者认为哪里存在问题。

必须分开。

单个失败案例不能自动形成：

stable failure pattern

必须继续保持candidate/observation状态。

============================================================
10. Migration M07

    Veracity Assessment拆分
    ============================================================

检查GS004全部Assessment。

旧：

status

如果混合：

来源支持程度
现实真假
推理评价
预测结算状态

必须拆开。

至少新增：

verification_status

以及适用：

assessment_kind
detail
resolution_status

七值verification enum以MA.1正式规范为准。

不得将：

forecast not yet resolved

映射成：

false
unverifiable

Forecast尚未结算必须属于：

resolution_status

不是现实真假。

原旧status保留为：

legacy_status

或Migration Log。

============================================================
11. Migration M08

    Mechanism / MechanismUsage Attribution
    ============================================================

检查GS004 Mechanism。

如果已有：

Mechanism

但缺分析师使用层，

根据现有证据决定是否存在：

MechanismUsage

结构：

{
  "mechanism_ref": "...",
  "analyst_id": "...",
  "usage_context": "...",
  "expression_level": "...",
  "source_refs": [],
  "argument_refs": [],
  "first_observed_at": ...,
  "observed_count": ...,
  "domain_scope": ...,
  "confidence": ...
}

仅当现有GS004已经支持：

9527实际使用该机制

才可创建/补MechanismUsage。

如果只是：

model_gpt6总结了一个通用机制

不得伪造：

analyst_youhegaojian9527 used mechanism。

============================================================
12. Migration M09

    Reasoner Attribution Audit
    ============================================================

全量检查：

Claim
Argument
Mechanism
MechanismUsage
AnalystMethodSignal
Assessment

确保：

reasoner_id
analysis_context
annotation_observer

语义一致。

尤其：

analysis_context = model_diagnostic

的对象不得直接进入：

9527 Method evidence。

model_reconstruction不得被重新标记成：

explicit
strongly_implied

除非原GS004已有对应源证据。

============================================================
13. Migration M10

    Manual Review Queue
    ============================================================

无法确定的MA.1迁移问题进入：

ma1_manual_review_queue

推荐ID：

MA1-FRAGILE-ARxx

MA1-ROLE-ARxx

MA1-RECURRENCE-MSxx

MA1-FAILURE-MSxx

MA1-SEMANTIC-<object>

MA1-FUTURE-LEAK-<object>

每个Review必须有：

review_id
object_refs
category
question
status: open
decision: null
requires_human: true
blocks_verified_promotion: true/false

只有真正影响：

Skill promotion
verified knowledge
Freeze semantic boundary

的Review才：

blocks_verified_promotion: true

不要机械地让所有Warning都阻塞项目。

============================================================
14. Migration Metadata
============================================================

增加：

ma1_migration:

  schema_version: V0.3.1-MA.1

  migration_version:
    GS004-MA1-LW-1

  migration_type:
    lightweight

  source_golden:
    GS004

  semantic_objects_regenerated:
    false

  ids_regenerated:
    false

  re_extraction_performed:
    false

  model_reanalysis_performed:
    false

  future_sample_leakage_allowed:
    false

  human_acceptance:
    false

  frozen:
    false

  production_import_ready:
    false

加入：

source file SHA256
migration timestamp
migration prompt SHA256
validator version/hash

============================================================
15. Migration Log
============================================================

生成：

migration_log.jsonl

每个变化至少记录：

object_ref
json_path
change_type

change_type可包括：

added_field
normalized_enum
changed_value
legacy_preserved
manual_review_created

并记录：

old_value
new_value
migration_rule
reason

不得只生成最终JSON而没有变化日志。

============================================================
16. Diff Summary
============================================================

生成：

diff_summary.md

至少包含：

1. added_fields
2. changed_values
3. normalized_enums
4. legacy_fields_preserved
5. manual_review_required
6. future_sample_leakage_checks
7. untouched_objects
8. object_count_before_after

必须明确：

是否新增Claim
是否新增Argument
是否新增MethodSignal
是否重生成ID

预期均应为：

no

除非发现原数据损坏并进入Manual Review，
不得自动修复。

============================================================
17. Validator
============================================================

运行MA.1 Validator。

至少包括：

R056
Method recurrence specificity

R057
No vague recurrence

R058
Failure observer separation

R059
Single failure ≠ stable pattern

R060
Comparison basis completeness

R061
Percent / percentage-point integrity

R062
Semantic role integrity

R063
Cross semantic-role inference requires explicit Argument Edge / Review

以及：

V-MA101
legal MethodSignal enums / required fields

V-MA102
non-none recurrence requires prior refs

V-MA103
partial/analogous/exact require matched_scope

V-MA104
failure observed_reasoner_id

V-MA105
failure annotation_observer

V-MA106
comparison object completeness

V-MA107
percent/pp integrity

V-MA108
recognition_stage explicit

V-MA109
cross semantic-role transformation requires Argument Edge or Review

V-MA110
model_diagnostic forbidden from AnalystMethodSignal evidence

新增工程Validator：

V-MA111
No future-sample recurrence leakage

定义：

For GS004,
matched_prior_signal_refs / recurrence_evidence
must not use GS005 or any Golden later than GS004 as prior evidence.

同时检查：

ID uniqueness
reference integrity
reasoner attribution
object counts
legacy preservation

============================================================
18. Validator策略
============================================================

目标：

ERROR = 0

不要求：

WARNING = 0

Warning允许包括：

manual review
source uncertainty
registry incompleteness
semantic ambiguity

严禁为了清Warning：

猜most_fragile_step
猜semantic_role
猜recognition_stage
猜recurrence
修改原Claim语义

============================================================
19. Freeze相关检查
============================================================

Migration完成后，额外回答：

1.
GS004是否发现现有14 Core Objects无法表达的对象？

2.
是否存在必须新增第15个Core Object的问题？

3.
或者所有问题都能通过：

Auxiliary Object
Field
Registry
Validator
Review Queue

解决？

此判断只作为：

Freeze Readiness Input

不得擅自宣布：

Core Ontology FROZEN

============================================================
20. 输出文件
============================================================

最终至少生成：

golden_sample_004.pre_ma1.json

gs004_ma1_gap_report.json

golden_sample_004.ma1_candidate.json

migration_log.jsonl

diff_summary.md

validation_before_ma1.json
（如果旧结构可运行旧validator）

validation_after_ma1.json

manual_review_queue.json
（也可以同时嵌入candidate）

gs004_ma1_migration_report.md

============================================================
21. Candidate状态
============================================================

如果：

ERROR > 0

使用：

ma1_compliance:
  migration_requires_revision

golden_status:
  ma1_migration_validation_failed

如果：

ERROR = 0
但存在Human Review：

ma1_compliance:
  migrated_local_validation_pass_manual_review_pending

golden_status:
  ma1_migrated_validation_pass_manual_review_pending

human_acceptance:
  false

frozen:
  false

production_import_ready:
  false

不得因为ERROR=0直接标记：

human_accepted
frozen
production_ready

============================================================
22. 禁止事项
============================================================

严禁：

1. 重新抽取GS004视频。
2. 重新生成Claim。
3. 重新生成Argument。
4. 重新生成MethodSignal。
5. 重新编号对象。
6. 用GS005作为GS004的prior recurrence evidence。
7. 将model reconstruction变成9527历史方法。
8. 将unknown猜成具体语义。
9. 以删除对象方式解决Validator错误。
10. 修改Validator规则迎合数据。
11. 将Warning强制清零。
12. 宣布9527 Skill Ready。
13. 宣布MacroMind Core Skill Ready。
14. 宣布Core Ontology正式Freeze。
15. 使用后见信息修改GS004历史判断。

============================================================
23. 最终报告格式
============================================================

完成后只需要给出一份简明执行摘要：

GS004 MA.1 Lightweight Migration completed:
yes / no

Pre-migration objects:
Claims:
Arguments:
MethodSignals:
Assessments:
Indicators/Observations:

Objects regenerated:
yes/no

IDs changed:
yes/no

Future-sample leakage found:
yes/no

GS005 used as prior recurrence evidence:
must be no

Fields migrated:
...

Manual reviews created:
...

Validator:
ERROR:
WARNING:
PASS:

Core Ontology blocker discovered:
yes/no

Possible new Core Object required:
yes/no
如果yes，说明具体原因；
不得仅因缺字段提出新增Core Object。

Human finalization required:
yes/no

Current GS004 status:

frozen:
false

production_import_ready:
false

下一步只等待：
Human Review / Finalization
然后进入 Freeze Readiness Audit #001–#005。