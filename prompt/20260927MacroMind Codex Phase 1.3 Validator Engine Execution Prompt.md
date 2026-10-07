你正在执行：

MacroMind Codex Phase 1.3 — Validator Engine

前置阶段已通过独立验收：

Core Ontology V0.3:
  FROZEN

Phase 1.0 Contract Loader:
  ACCEPTED

Phase 1.1 Executable Schema:
  ACCEPTED

Phase 1.2 Registry:
  ACCEPTED

Independent Evidence Gate:
  EVIDENCE_COMPLETE_READY_FOR_PHASE_1_3

当前版本：

ontology_version:
  0.3

schema_version:
  0.1.0

registry_version:
  0.1.0

production_import_ready:
  false

Analyst Skill:
  NOT_READY

MacroMind Core Skill:
  NOT_READY

============================================================
0. 本阶段唯一目标
============================================================

实现一个：

deterministic
auditable
runtime-agnostic
semantic Validator Engine

让MacroMind能够对：

Canonical Schema 0.1.0 objects

进行：

Schema
Reference
Provenance
Temporal
Semantic Boundary
Argument
Analyst/Governance

验证。

本阶段重点推进：

D03 Scenario / Forecast admission
D04 Temporal / recurrence chronology
D11 Argument validator
D20 truth propagation / attribution boundaries

并继续保守支持：

D16 comparison / role / stage

============================================================
1. 本阶段明确不做
============================================================

严禁实现：

Phase 1.4 Legacy Adapters

Phase 1.5 Audit Runner

Phase 1.6 Golden Regression Suite

Golden Migration

Batch Pilot

Analyst Mining

Analyst Model

Skill Compilation

MCP/API

Agent Runtime

Database backend

Production Import

不得把Phase 1.3扩展成：

“整个MacroMind Validator + Migration + Audit系统”。

本阶段只做：

Validator Engine。

============================================================
2. 权威输入
============================================================

必须读取实际workspace中的：

Frozen Contract：

CORE_ONTOLOGY_V0.3_FROZEN.md
core_objects.json
core_boundaries.json
core_principles.json
freeze_manifest.json
CHANGE_POLICY.md

Phase 1.0–1.2：

src/macromind/contract/**
src/macromind/schema/**
src/macromind/registry/**

registries/v0_3/**
schemas/v0_3/**

docs/SCHEMA_MAPPING.md
docs/REGISTRY_POLICY.md

phase1/debt_status_overlay.json

Freeze Debt：

freeze_debt_ledger.json

重点读取：

D03
D04
D11
D16
D20

============================================================
3. Frozen语义不可修改
============================================================

不得修改：

14 Core定义

15 Core Boundaries

16 Core Principles

Frozen Contract

GS001–GS005

不得为了Validator实现方便：

新增第15个Core Object

把Scenario改成Forecast subtype

把MechanismUsage改成Mechanism

把AnalystMethodSignal升级Core

改变Forecast定义

改变Heuristic生命周期

如果发现：

当前Schema真的不足以表达某条Frozen规则，

不得偷偷补字段。

记录：

phase1_3_schema_gap.json

并决定该规则：

INDETERMINATE
or
BLOCKED_BY_SCHEMA_GAP

不要自行修改Phase 1.1合同。

============================================================
4. Validator设计原则
============================================================

严格遵守：

Validator detects.

Validator does not repair.

Validator does not infer missing facts.

Validator does not migrate legacy data.

Validator does not rewrite objects.

Validator does not make truth judgments without evidence.

Unknown is valid data.

Indeterminate is not automatically Error.

ReviewState does not waive SchemaValidity.

Golden number is not chronology.

Model reconstruction is not analyst evidence.

============================================================
5. 新建模块
============================================================

建议：

src/macromind/validation/
├── __init__.py
├── engine.py
├── models.py
├── context.py
├── index.py
├── reference_contracts.py
├── catalog.py
└── rules/
    ├── __init__.py
    ├── schema.py
    ├── references.py
    ├── provenance.py
    ├── temporal.py
    ├── boundaries.py
    ├── forecast.py
    ├── argument.py
    ├── analyst.py
    └── governance.py

不要创建：

migration/
audit/
golden_regression/

这些属于后续Phase。

============================================================
6. ValidationInput不是Ontology对象
============================================================

允许创建内部runtime container：

ValidationInput

ValidationContext

ObjectIndex

它们：

不是Core Object

不是Auxiliary domain object

不得加入：

object_types.yaml

不得导出为：

MacroMind ontology JSON Schema

它们只是Validator runtime structures。

============================================================
7. ValidationContext
============================================================

至少支持：

ontology_version: "0.3"

schema_version: "0.1.0"

validation_mode:
  complete_bundle
  partial_bundle

knowledge_cutoff:
  datetime | None

current_content_time:
  datetime | None

time_overrides:
  dict[ref, datetime]

sample_label:
  optional opaque string

注意：

sample_label只用于日志。

严禁使用：

GS001
GS002
GS003

编号来推断时间顺序。

============================================================
8. 时间比较原则
============================================================

Validator只能比较：

明确结构化时间。

如果TimeReference有明确：

start
end

可比较。

不得：

从text字段自行自然语言解析日期。

例如：

"text": "去年秋天"

不得让Validator猜日期。

结果应为：

INDETERMINATE
review_required=true

时间解析属于：

Extraction / Normalization

不是Validator责任。

============================================================
9. Validation Outcome
============================================================

建立统一：

RuleOutcome

至少：

PASS

ERROR

WARNING

INDETERMINATE

NOT_APPLICABLE

不得静默skip。

每条已注册Rule在运行时必须：

执行
或
明确NOT_APPLICABLE

============================================================
10. ValidationIssue
============================================================

至少：

rule_id

rule_name

category

severity

outcome

object_ref

field_path

message

related_refs

evidence_refs

review_required

details

不得把自然语言错误信息作为唯一结构。

============================================================
11. ValidationReport
============================================================

至少：

validator_version

ontology_version

schema_version

mode

object_count

rule_count

executed_rule_count

outcome_counts

issues

errors

warnings

indeterminate

not_applicable

deterministic_hash

不得把：

WARNING
INDETERMINATE

算成ERROR。

============================================================
12. Severity规则
============================================================

ERROR：

明确违反已冻结合同
或
确定的引用/类型/时间不可能关系。

WARNING：

结构合法，
但存在需要注意的可疑或不完整状态。

INDETERMINATE：

当前已有字段无法证明对错。

UNKNOWN不能因为“无法判断”自动变ERROR。

============================================================
13. Rule ID必须稳定
============================================================

建立新通用命名：

V-SCHxxx
V-REFxxx
V-PROVxxx
V-TEMPxxx
V-BNDxxx
V-FCxxx
V-ARGxxx
V-ANxxx
V-GOVxxx

Rule ID一旦发布：

不得随意重编号。

============================================================
14. 不复制Golden专用Validator
============================================================

现有：

R056–R063

V-MA101–V-MA111

是历史Golden合同。

Phase 1.3要做：

通用规则。

生成：

docs/LEGACY_VALIDATOR_CROSSWALK.md

例如：

V-MA111
→ generic future-prior temporal rule

旧Rule可映射：

ported
covered_by_schema
deferred
sample_specific_not_ported

不得把：

GS004
GS005

特例写进通用Validator。

============================================================
15. Schema入口
============================================================

Validator只接受：

Canonical Schema 0.1.0

不得接受旧Golden结构然后自动适配。

raw dict进入时：

object_type
→ registered Pydantic Model
→ validation

如果：

legacy schema

返回：

unsupported_schema_version

不要Migration。

Phase 1.4才做Adapter。

============================================================
16. Object Index
============================================================

为Bundle建立：

id → object

并验证：

object ID唯一

object_type合法

schema_version=0.1.0

ontology_version=0.3

不得自动重命名冲突ID。

============================================================
17. Reference Resolution Mode
============================================================

支持：

complete_bundle

和：

partial_bundle

complete_bundle：

要求应当本地解析的reference存在。

缺失：

ERROR。

partial_bundle：

同一未解析reference：

WARNING或INDETERMINATE

不得误报为确定错误。

============================================================
18. Reference Contract
============================================================

集中定义：

field
→ allowed target types
→ resolution mode

不要在各Rule中散落magic target strings。

例如：

Source.version_refs
→ SourceVersion

Source.segment_refs
→ SourceSegment

Source.family_ref
→ SourceFamily

Claim.source_refs
→ Source

StructuralProcess.event_refs
→ Event

StructuralProcess.observation_refs
→ IndicatorObservation

StructuralProcess.policy_refs
→ Policy

Policy.actor_refs
→ Actor

Policy.event_refs
→ Event

Forecast.claim_ref
→ Claim

Assessment.information_set_ref
→ InformationSet

MechanismUsage.mechanism_ref
→ Mechanism

ClaimOccurrence.claim_ref
→ Claim

ClaimOccurrence.source_segment_ref
→ SourceSegment

ClaimOccurrence.source_version_ref
→ SourceVersion

ClaimOccurrence.origin_family_ref
→ SourceFamily

不得猜未知target类型。

============================================================
19. 基础Reference Rules
============================================================

至少：

V-REF001
duplicate object id
→ ERROR

V-REF002
unknown object type
→ ERROR

V-REF003
wrong target type
→ ERROR

V-REF004
dangling local ref in complete_bundle
→ ERROR

V-REF005
unresolved ref in partial_bundle
→ INDETERMINATE/WARNING

V-REF006
forbidden self-reference
→ ERROR where explicitly prohibited

============================================================
20. Provenance Rules
============================================================

至少实现：

Source ≠ Claim

Claim.source_refs必须引用Source

ClaimOccurrence负责：

specific occurrence
segment
version
origin family

SourceFamily不等于：

independent evidence

同源转载不得因多个Source自动增加独立支持数。

本阶段不要实现完整source independence scoring。

============================================================
21. Source / Claim / Reality
============================================================

不得存在任何Validator逻辑：

Source exists
→ Claim true

Claim quoted correctly
→ Reality true

Assessment verified
→ target Claim true

Validator只能检查：

结构
引用
归属
时间
规则一致性

不得做现实事实裁决。

============================================================
22. D20 — Assessment / Reality
============================================================

至少：

Assessment.target_ref必须可解析

information_set_ref必须指向InformationSet

observer与target分开

verification_status只描述Assessment

不得修改target object

不得产生：

target.truth = Assessment.verification_status

测试必须证明：

同一个Claim

无论Assessment：

verified
false
uncertain

Claim对象本身字节/内容不变。

============================================================
23. Actor / Geography
============================================================

Actor.location

不是：

Actor identity

roles

不是：

Actor identity

当前没有Geography Core Object。

不得：

创建Geography Object

不得：

通过location字符串自动merge Actor。

Identity仍由Phase 1.2 policy治理。

============================================================
24. D03 — Forecast Admission
============================================================

实现：

Forecast Admission Validator

但必须保守。

不得靠：

LLM
关键词
自然语言猜测

判断Forecast。

至少检查：

Forecast.claim_ref → Claim

claimant attribution存在或unknown

knowledge_cutoff存在或unknown

prediction_window存在或unknown

modal_strength存在或unknown

resolution_criteria存在或unknown

conditions

branch_selection

============================================================
25. Forecast Admission结果
============================================================

Validator可产生：

ADMISSION_STRUCTURALLY_SUPPORTED

ADMISSION_INDETERMINATE

ADMISSION_INVALID

但：

不得自动把对象改成Scenario或Forecast。

============================================================
26. Forecast明确错误
============================================================

例如：

claim_ref目标不是Claim

明确future window早于knowledge_cutoff

结构上自相矛盾的resolution timing

→ ERROR

============================================================
27. Conditional Forecast
============================================================

当前Schema没有完整表达：

“condition endorsement”

时，

不得猜。

如果：

conditions存在

branch_selection缺失/unknown

且现有结构无法证明：

主体承担该条件预测

结果：

INDETERMINATE
review_required=true

不得：

自动判Forecast合法

也不得：

自动改成Scenario。

============================================================
28. Scenario Gate
============================================================

Scenario：

始终保持Scenario类型。

不得：

Scenario
→ auto Forecast

Scenario有branch

不代表：

Forecast。

如果Scenario和Forecast引用同一Claim：

最多：

WARNING / REVIEW

除非存在明确结构冲突。

============================================================
29. Resolvability != Admission
============================================================

严格实现：

预测时间窗口不清

或：

resolution criteria不清

可以：

降低resolvability

但不得单独因此证明：

“不是Forecast”。

同样：

有resolution criteria

也不能单独证明：

“是Forecast”。

============================================================
30. Thesis / Forecast
============================================================

不要根据文本分类Thesis。

只做结构边界：

Thesis != Forecast

Forecast-only fields不得通过Schema混入Thesis。

已有Pydantic extra=forbid继续生效。

============================================================
31. D04 — Recurrence Chronology
============================================================

重点实现通用版：

future prior leakage validator。

规则必须依据：

实际content time
knowledge cutoff
available structured timestamps

绝不能依据：

Golden编号
ID字典序
文件名顺序。

============================================================
32. Recurrence prior规则
============================================================

AnalystMethodSignal：

matched_prior_signal_refs

如果引用的Signal：

明确晚于当前knowledge_cutoff
或
明确晚于current_content_time

→ ERROR

如果时间不可判断：

→ INDETERMINATE
review_required=true

不得猜。

============================================================
33. Golden Number反例测试
============================================================

必须测试：

signal id = GS002_x
time = 2026-09-21

current sample = GS004
time = 2026-08-05

尽管：

002 < 004

仍必须判：

future prior invalid。

再交换名称但保持日期：

结果必须完全相同。

============================================================
34. recurrence_match规则
============================================================

如果：

recurrence_match = none

则active：

matched_prior_signal_refs

原则上应为空。

若非空：

ERROR或明确规则冲突。

============================================================
35. uncertain recurrence
============================================================

如果：

recurrence_match = uncertain

且：

recurrence_status = first_observation

这是允许状态。

不得强制：

uncertain → repeated。

GS004曾出现的这种合法形态必须可以表达。

============================================================
36. repeated/frequent规则
============================================================

如果：

recurrence_status =
repeated
frequent
candidate_pattern

但没有任何：

eligible historical prior

则：

WARNING或INDETERMINATE + review

不要因数据不完整立刻ERROR，

除非已确定：

所有所谓prior都是未来证据。

============================================================
37. SourceVersion / Temporal
============================================================

只在时间可精确比较时检查：

published_at
captured_at
content_time

不要假设：

capture time
=
publication time

不要把：

video offset
=
asserted_at

不要从文本日期自动推断。

============================================================
38. Forecast Temporal
============================================================

当exact timestamps存在：

knowledge_cutoff
应早于或等于
prediction window start。

如果明确反转：

ERROR。

如果任何一侧unknown/null：

INDETERMINATE

不是ERROR。

============================================================
39. D11 — Argument Graph
============================================================

本阶段实现的是：

Argument structural-semantic validator

不是：

自动判断一个经济论证“是否正确”。

============================================================
40. Argument至少检查
============================================================

step IDs唯一

premise refs可解析

conclusion refs可解析

intermediate conclusion links合法

final conclusion link合法

graph cycle

orphan step

most_fragile_step指向有效step

per-edge reasoner attribution保留

analysis_context合法

expression_level合法

============================================================
41. Argument Cycle
============================================================

明确cycle：

A → B → A

→ ERROR

不要自动修图。

============================================================
42. fragile step
============================================================

如果：

most_fragile_step

引用不存在的step：

ERROR。

如果：

unknown

合法。

============================================================
43. Reasoner Attribution
============================================================

Argument overall reasoner

不得覆盖：

step.reasoner_id。

测试：

Argument reasoner=analyst

step reasoner=model

Validator必须保留差异。

不得自动继承。

============================================================
44. model reconstruction
============================================================

expression_level=model_reconstruction

不得被解释为：

creator explicit reasoning。

如果该对象被直接当作：

Analyst Method evidence
Repeated Analyst Pattern
Heuristic promotion evidence

Validator应：

WARNING/ERROR according to explicit use

并：

review_required=true。

不要删除对象。

============================================================
45. Method promotion边界
============================================================

Phase 1.3不得实现：

Skill promotion。

只允许Validator发现：

model reconstruction被错误当作analyst evidence

single signal被错误当作validated skill evidence

但不要生成Skill Rule。

============================================================
46. D11 role / stage / unit
============================================================

只验证当前Schema明确能表达的内容。

不得为了满足D11：

自行增加denominator字段

自行增加财务模型。

如果：

数据结构不足

输出：

INDETERMINATE

并记录：

remaining_debt。

============================================================
47. Comparison Basis
============================================================

不得自动计算：

delta_value

不得自动推导：

baseline_value

不得自动把：

3%

变成：

3 percentage points。

如果：

comparison_type=percentage_point_change

但delta_unit不明确：

WARNING / REVIEW

而不是自动修正。

============================================================
48. semantic_role
============================================================

继续保持：

order
revenue
cash_receipt
profit

彼此不同。

Validator不得建立：

order → revenue
revenue → cash receipt

自动等价。

============================================================
49. recognition_stage
============================================================

planned
contracted
ordered
committed
delivered
deployed
utilized
revenue_recognized
cash_collected

不得自动跳级。

但是：

当前没有明确transition evidence

不要凭枚举次序判业务错误。

enum顺序：

不等于因果流程。

============================================================
50. Event / StructuralProcess
============================================================

不允许：

single Event
→ auto StructuralProcess。

如果StructuralProcess：

event_refs=[]
observation_refs=[]
policy_refs=[]
evidence_refs=[]

→ WARNING/REVIEW

如果只有单Event且无跨期观测：

→ WARNING/REVIEW

不要设定：

“必须至少2个Event”

这种未经Frozen Contract授权的硬数字。

============================================================
51. Policy / Event
============================================================

验证：

Policy.event_refs
→ Event

Event.policy_refs
→ Policy

不要要求必须双向对称，

因为partial bundle可能只记录一边。

============================================================
52. Mechanism / MechanismUsage
============================================================

验证：

MechanismUsage.mechanism_ref
→ Mechanism

usage analyst

不得自动成为：

Mechanism author。

但如果两者ID偶然相同：

不得自动判错。

关键是：

Validator不执行复制/推断。

============================================================
53. Assessment / Claim
============================================================

Assessment targeting Claim

不允许：

Assessment verification status

传播为：

Claim truth field。

由于Claim Schema没有truth字段，

Validator必须保持这个边界。

============================================================
54. ReviewState ≠ SchemaValidity
============================================================

这一条必须成为hard governance rule：

ReviewQueueItem.status

不得改变：

Schema validation
Reference validation
Temporal error
Semantic boundary error

例如：

Review=open

绝不能豁免：

缺required canonical field
wrong target type
future prior leakage

Review=resolved

也不能自动使对象合法。

============================================================
55. No Review Exemptions
============================================================

Validator Engine中不得出现：

if review_open:
    skip_error()

不得出现：

if review_resolved:
    mark_valid()

Review只提供：

human workflow state。

============================================================
56. Validator deterministic
============================================================

同样输入：

objects
context
contract
registry

必须产生：

相同rule order
相同issues
相同report semantic hash

不得把：

timestamp
run_id

写入semantic result hash。

============================================================
57. Rule ordering
============================================================

固定顺序建议：

Schema

Reference

Provenance

Temporal

Boundary

Forecast

Argument

Analyst

Governance

结果排序：

rule_id
object_ref
field_path

确保determinism。

============================================================
58. 不使用LLM
============================================================

Phase 1.3 Validator Engine：

禁止：

LLM API
web search
embedding
vector retrieval
heuristic NLP keyword classification

Validator必须：

pure deterministic code。

============================================================
59. CLI
============================================================

现在允许新增：

macromind validate

例如：

macromind validate \
  --input canonical_bundle.json \
  --contract-root ... \
  --registry-root ... \
  --context validation_context.json \
  --mode complete_bundle

输出：

ValidationReport JSON。

============================================================
60. CLI退出码
============================================================

建议：

0:
no ERROR

1:
one or more ERROR

2:
CLI/input usage error

WARNING / INDETERMINATE：

不导致exit 1，

除非未来政策另行定义。

============================================================
61. Canonical Bundle
============================================================

本阶段可以定义内部文件格式：

{
  "objects": [...]
}

但：

它只是Validator transport envelope。

不得注册成：

Core Object

Auxiliary Object。

============================================================
62. Legacy Data
============================================================

如果输入：

schema_version != 0.1.0

Validator应：

明确拒绝或报告unsupported_schema_version。

不要适配。

不要迁移。

不要补字段。

============================================================
63. Rule Catalog
============================================================

生成：

phase1/validator_rule_catalog.json

每条：

rule_id
name
category
description
frozen_boundary_refs
principle_refs
debt_refs
severity_policy
implemented
limitations

============================================================
64. Legacy Validator Crosswalk
============================================================

生成：

docs/LEGACY_VALIDATOR_CROSSWALK.md

至少覆盖：

R056–R063
V-MA101–V-MA111

标注：

ported_to
covered_by_schema
deferred
sample_specific

特别：

V-MA111
必须映射到：

generic future-prior temporal validator。

============================================================
65. 不移植Sample Exemption
============================================================

任何历史：

C005 exemption
GS004-specific exemption
open-review exemption

不得移入通用Validator。

============================================================
66. Synthetic Tests
============================================================

Phase 1.3只使用：

synthetic canonical fixtures

和：

minimal failure-pattern fixtures

不要直接跑完整GS001–GS005。

完整Golden Regression属于：

Phase 1.6。

============================================================
67. 必测负例
============================================================

至少：

duplicate ID

dangling ref

wrong target type

Scenario treated as Forecast

conditional Forecast insufficient structured endorsement

future recurrence prior

Golden number chronology trap

Argument cycle

invalid fragile-step ref

model reconstruction used as analyst evidence

Assessment truth propagation attempt

Review status exemption attempt

3% → 3pp forbidden conversion

single Event → StructuralProcess overpromotion

MechanismUsage authorship leakage

============================================================
68. 必测Unknown
============================================================

必须证明：

unknown prediction_window

unknown baseline

unknown role/stage

unknown recurrence time

不会自动：

ERROR
猜值
补值。

应：

INDETERMINATE
或合法unknown。

============================================================
69. Metamorphic Tests
============================================================

至少：

改变Golden/sample label
但不改变time

→ chronology结果不变

改变Review状态
但不改变对象

→ schema/reference error结果不变

改变Assessment verification_status

→ target Claim内容不变

重复运行Validator

→ semantic report完全一致

============================================================
70. Existing tests必须继续PASS
============================================================

Phase 1.0–1.2：

84 tests

不得退化。

必须运行：

existing tests
+
Phase 1.3 tests

所有：

FAILED=0
ERROR=0
SKIPPED=0

============================================================
71. Frozen / Golden immutability
============================================================

Phase 1.3必须继续重新检查：

Frozen files

GS001–GS005

不得修改。

============================================================
72. Schema / Registry变更原则
============================================================

默认：

不修改Phase 1.1 Schema
不修改Phase 1.2 Registry vocabulary。

如果发现硬缺口：

生成：

phase1/phase1_3_schema_gap.json
或
phase1/phase1_3_registry_gap.json

不要在本任务自动扩Schema。

============================================================
73. Debt状态
============================================================

新建：

phase1/phase1_3_debt_overlay.json

不得修改历史：

freeze_debt_ledger.json

phase1/debt_status_overlay.json

============================================================
74. D03状态
============================================================

即使通用Forecast validator完成：

默认最多：

partially_addressed_phase1_3

因为：

GS003 legacy review
Golden Regression

尚未执行。

不得轻易标resolved。

============================================================
75. D04状态
============================================================

即使future-prior rule完成：

默认最多：

partially_addressed_phase1_3

因为legacy records/adapters和全Golden回归尚未执行。

============================================================
76. D11状态
============================================================

Argument graph规则完成后：

仍可能：

partially_addressed_phase1_3

如果：

denominator
role/stage transition
unit semantics

缺少结构字段。

不得为了“解决Debt”发明字段。

============================================================
77. D20状态
============================================================

完成truth/assessment/reference guards后：

默认：

partially_addressed_phase1_3

批量负例与全Golden回归仍留Phase 1.6 / Batch Pilot。

============================================================
78. Phase 1.3文档
============================================================

生成：

docs/
  PHASE1_3_VALIDATOR_ARCHITECTURE.md
  VALIDATOR_RULES.md
  LEGACY_VALIDATOR_CROSSWALK.md
  PHASE1_3_GATE.md

============================================================
79. Phase 1.3机器产物
============================================================

至少：

phase1/
  validator_rule_catalog.json
  phase1_3_manifest.json
  phase1_3_test_report.json
  phase1_3_gate_result.json
  phase1_3_debt_overlay.json
  phase1_3_immutability_report.json
  phase1_3_schema_gap.json
  phase1_3_registry_gap.json

gap文件即使无gap：

也生成：

{
  "gaps": []
}

============================================================
80. Validator Engine Tests
============================================================

建议：

tests/validation/
  test_engine.py
  test_references.py
  test_provenance.py
  test_temporal.py
  test_forecast.py
  test_argument.py
  test_analyst.py
  test_governance.py
  test_cli_validate.py

============================================================
81. Phase 1.3 Gate
============================================================

建立：

PHASE1_3_GATE

至少：

G01 Frozen Contract仍PASS

G02 Existing Phase1.0–1.2 tests全部PASS

G03 Validator Engine loads

G04 Rule catalog deterministic

G05 ID uniqueness rule works

G06 Reference resolver works

G07 complete/partial mode works

G08 Source/Claim provenance boundary works

G09 Scenario/Forecast conservative gate works

G10 future-prior chronology rule works

G11 Golden number does not affect chronology

G12 Argument graph validator works

G13 fragile-step validation works

G14 model reconstruction guard works

G15 Assessment truth non-propagation works

G16 ReviewState does not waive validation

G17 Unknown produces no guessed value

G18 StructuralProcess no auto-promotion

G19 Comparison no automatic delta/pp conversion

G20 Validator deterministic

G21 no Frozen file modified

G22 no Golden modified

G23 no Schema silently changed

G24 no Registry silently changed

G25 no Legacy Adapter implemented

G26 no Audit Runner implemented

G27 no Golden Regression implemented

G28 production_import_ready=false

G29 Skills remain NOT_READY

============================================================
82. Gate结果
============================================================

最终只能：

READY_FOR_PHASE_1_4

或：

NOT_READY_VALIDATOR_BLOCKER

不得：

直接启动Phase 1.4。

============================================================
83. 如果发现Schema Gap
============================================================

如果某Frozen规则：

确实无法由当前Schema判断，

不要假装实现。

记录：

rule_id
required_semantics
missing_structure
affected_debt
current_outcome:
  INDETERMINATE
recommended_future_action

如果该Gap使Validator核心目标无法成立：

Gate应FAIL。

============================================================
84. 如果测试失败
============================================================

不得：

删除测试
降低规则
加Golden exemption
加Review exemption

先修Validator。

若无法修：

Gate：

NOT_READY_VALIDATOR_BLOCKER。

============================================================
85. 最终状态
============================================================

若PASS：

Core Ontology V0.3:
  FROZEN

Phase 1.0:
  COMPLETE

Phase 1.1:
  COMPLETE

Phase 1.2:
  COMPLETE

Phase 1.3:
  COMPLETE

Phase 1.4:
  NOT_STARTED

Batch Pilot:
  NOT_STARTED

Analyst Model:
  NOT_READY

Analyst Skill:
  NOT_READY

MacroMind Core Skill:
  NOT_READY

Production:
  NOT_READY

============================================================
86. 最终执行摘要
============================================================

完成后只输出：

MacroMind Codex Phase 1.3 completed:
yes/no

Validator version:
...

Rules registered:
...

Rule outcomes supported:
PASS / ERROR / WARNING / INDETERMINATE / NOT_APPLICABLE

Reference validation:
PASS/FAIL

Temporal validation:
PASS/FAIL

Scenario/Forecast admission:
PASS/FAIL

Future-prior chronology:
PASS/FAIL

Argument graph:
PASS/FAIL

Truth non-propagation:
PASS/FAIL

ReviewState independence:
PASS/FAIL

Unknown handling:
PASS/FAIL

Existing Phase 1.0–1.2 tests:
PASSED:
FAILED:
ERROR:
SKIPPED:

Phase 1.3 tests:
PASSED:
FAILED:
ERROR:
SKIPPED:

Frozen artifacts modified:
yes/no

Golden files modified:
yes/no

Schema modified:
yes/no

Registry vocabulary modified:
yes/no

Schema gaps:
<number>

Registry gaps:
<number>

Debt overlay:
D03:
D04:
D11:
D20:

Phase 1.4 executed:
false

Production Import Ready:
false

Analyst Skill:
NOT_READY

Phase 1.3 Gate:
READY_FOR_PHASE_1_4
or
NOT_READY_VALIDATOR_BLOCKER

Recommended next step:
Phase 1.4 Legacy Compatibility