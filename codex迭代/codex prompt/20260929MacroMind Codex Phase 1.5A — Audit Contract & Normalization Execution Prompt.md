你正在执行：

MacroMind Codex Phase 1.5A
Audit Contract & Normalization
with Human-Reviewed Analytical Continuity Hook


============================================================
0. 前置状态
============================================================

Core Ontology V0.3:
FROZEN

Phase 1.0:
ACCEPTED

Phase 1.1:
ACCEPTED

Phase 1.2:
ACCEPTED

Phase 1.3 Validator Engine:
ACCEPTED

Phase 1.4 Legacy Compatibility:
ACCEPTED

Phase 1.5A:
NOT_STARTED

Phase 1.5B:
NOT_STARTED

Phase 1.5C:
NOT_STARTED

Phase 1.6:
NOT_STARTED

Production:
NOT_READY

Analyst Model:
NOT_READY

Analyst Skill:
NOT_READY


============================================================
1. 本阶段唯一目标
============================================================

建立一个：

只读
确定性
可追溯
不做业务判断

的 Audit Normalization Layer。

把已有工程结果：

Validator findings
Compatibility losses
Quarantine
Mapping-related findings
Schema gaps
Registry gaps
Immutability results
Gate results
Test summaries
Debt statuses

转换成统一：

AuditRecord

同时建立一个非常薄的：

Human-Reviewed Analytical Continuity Hook

允许以后人工标记：

两个历史分析对象 / Episodes
可能属于同一长期分析论题。

本阶段不得自动创建Analytical Thread。


============================================================
2. Phase 1.5A 不做
============================================================

严禁：

Audit Pattern aggregation

Analytical Thread automatic discovery

topic clustering

embedding similarity

LLM topic classification

risk ranking

risk scoring

Audit Report

Dashboard

Audit Runner orchestration

cross-run diff

Golden Regression

Analyst Model

Method Signal mining

Heuristic mining

Skill compilation

automatic repair

automatic source mutation


============================================================
3. 依赖方向
============================================================

已有结果
    ↓
Audit Normalizer
    ↓
AuditRecord

不得：

Audit
↓
修改 Validator

不得：

Audit
↓
修改 Compatibility

不得：

Audit
↓
修改 Golden


============================================================
4. 推荐目录
============================================================

创建：

src/macromind/audit/
├── __init__.py
├── models.py
├── inputs.py
├── normalize.py
├── ids.py
├── provenance.py
└── continuity.py

tests/audit/
├── conftest.py
├── helpers.py
├── test_models.py
├── test_normalization.py
├── test_ids.py
├── test_provenance.py
├── test_continuity.py
├── test_determinism.py
└── test_immutability.py

docs/
├── PHASE1_5A_AUDIT_CONTRACT.md
└── ANALYTICAL_CONTINUITY_HOOK.md

scripts/
└── verify_phase1_5a.py


============================================================
5. AuditInputBundle
============================================================

建立：

AuditInputBundle

这是工程运行对象。

至少支持引用：

validation_reports

adaptation_results

immutability_reports

gate_results

test_reports

schema_gap_reports

registry_gap_reports

debt_overlays

manifests

不要自动扫描整个硬盘。

调用方必须明确提供Audit输入。


============================================================
6. AuditInputArtifact
============================================================

每个输入统一包装：

AuditInputArtifact

至少：

artifact_id

artifact_type

path_or_label

sha256

phase

component

format

content

source_metadata


============================================================
7. Audit输入必须Hash
============================================================

Normalizer运行前：

验证输入hash。

如调用方提供expected_sha256：

不一致：

HARD ERROR

不得继续normalize。


============================================================
8. AuditRecord
============================================================

建立统一：

AuditRecord

至少包含：

record_id

record_type

phase

component

category

severity

message

source_artifact_id

source_artifact_hash

source_pointer

object_ref

source_path

target_path

rule_id

reason_code

evidence_refs

review_required

metadata


============================================================
9. record_type
============================================================

至少支持：

VALIDATION_FINDING

ADAPTATION_LOSS

QUARANTINE

SCHEMA_GAP

REGISTRY_GAP

IMMUTABILITY_EVENT

GATE_RESULT

TEST_RESULT

DEBT_STATUS

MAPPING_EVENT

UNKNOWN_ENGINEERING_RECORD


============================================================
10. 不要统一成Issue
============================================================

明确保持：

Loss != Error

Quarantine != Error

Gap != Bug

Warning != Failure

Debt != Finding

不得把所有记录转换为：

issue


============================================================
11. Severity保真
============================================================

Audit Normalizer不得重新评价严重程度。

如果源数据：

ERROR
WARNING
INDETERMINATE
PASS
INFO
BLOCKING

必须保持其原始语义。

如不同来源severity体系不同：

保存：

source_severity

normalized_severity_class

但不得提升或降低风险。

normalized_severity_class只能用于兼容展示，
不能表示新的判断。


============================================================
12. Unknown保真
============================================================

Unknown / Indeterminate：

不得转换成：

False

PASS

ERROR

Guess

必须继续明确保存。


============================================================
13. Source Pointer
============================================================

每个AuditRecord必须能够追溯到：

source artifact
+
source pointer

例如：

phase1_4_gate_result.json
/gates/12

或：

adaptation result
/losses/423

source_pointer使用稳定JSON Pointer。


============================================================
14. Audit ID
============================================================

禁止uuid4作为语义身份。

record_id必须确定性生成。

推荐：

sha256(
  source_artifact_hash
  + source_pointer
  + record_type
)

同一输入重复normalize：

record_id必须一致。


============================================================
15. Input filename不属于语义
============================================================

如果：

文件内容相同
hash相同

仅改变：

文件名
目录

AuditRecord语义ID不得改变。


============================================================
16. Normalizer类型
============================================================

建议实现：

AuditNormalizer

API：

normalize_artifact(...)

normalize_bundle(...)

输出：

NormalizedAuditBundle


============================================================
17. NormalizedAuditBundle
============================================================

至少：

input_manifest

records

unsupported_inputs

normalization_warnings

record_counts

deterministic_hash


============================================================
18. Unsupported不能丢
============================================================

如果输入artifact类型暂不支持：

不得：

silently ignore

必须产生：

UNKNOWN_ENGINEERING_RECORD

或：

unsupported_inputs

并保留：

artifact hash
artifact type
reason


============================================================
19. 不做Pattern
============================================================

即使发现：

10,000条完全相同loss

1.5A仍然生成：

10,000条AuditRecord

不要聚合。

Aggregation属于：

Phase 1.5B。


============================================================
20. 不做Thread自动判断
============================================================

Phase 1.5A不得根据：

标题
关键词
文本相似度
embedding
LLM

判断两个分析：

属于同一个Analytical Thread。


============================================================
21. Analytical Continuity Hook
============================================================

建立一个独立工程对象：

ContinuityAnnotation

它不是Frozen Ontology对象。

也不是AuditRecord。

用于人工标记：

历史分析之间的连续性关系。


============================================================
22. ContinuityAnnotation字段
============================================================

至少：

annotation_id

subject_ref

related_ref

thread_ref

relation_type

review_status

reviewer

review_notes

evidence_refs

created_at

metadata


============================================================
23. thread_ref允许为空
============================================================

人工可以先标：

subject A
related B

relation_type:
SAME_ISSUE_CANDIDATE

但：

thread_ref = null

表示：

尚未创建正式Thread。


============================================================
24. relation_type
============================================================

初始只允许：

SAME_ISSUE_CANDIDATE

NEW_EVIDENCE

REPEAT_EVIDENCE

COUNTER_EVIDENCE

THESIS_REFINEMENT

FORECAST_UPDATE

METHOD_REUSE

UNCERTAIN_RELATION

注意：

这些只是人工关系标签。

不得由系统自动推断。


============================================================
25. review_status
============================================================

至少：

UNREVIEWED

CANDIDATE

CONFIRMED

REJECTED

默认：

UNREVIEWED

不能默认CONFIRMED。


============================================================
26. reviewer
============================================================

人工确认时：

reviewer必须明确。

不得默认：

9527

system

model

除非实际是对应observer。


============================================================
27. ContinuityAnnotation来源
============================================================

subject_ref / related_ref：

必须引用：

实际存在的artifact/object/episode reference。

如果暂时无法解析：

允许记录候选，

但必须：

resolution_status = UNRESOLVED

不得猜。


============================================================
28. annotation_id确定性
============================================================

annotation_id不得使用随机UUID。

基于：

subject_ref
related_ref
relation_type
reviewer

生成稳定ID。

但人工修改relation_type后：

应产生新的语义ID。


============================================================
29. Continuity不是Ontology
============================================================

不要修改：

Core Ontology

Schema 0.1.0

Registry 0.1.0

来加入：

AnalyticalThread

AnalyticalEpisode

ContinuityAnnotation

1.5A只作为工程辅助数据结构。


============================================================
30. 为什么保留Continuity Hook
============================================================

文档必须明确说明：

它用于未来研究：

同一分析问题
在多个时间点
随着Information Set变化
如何产生Judgment变化。

但：

1.5A不执行：

Evidence Delta

Judgment Delta

Thread construction

这些属于后续阶段。


============================================================
31. 输入支持优先级
============================================================

第一版至少支持真实：

Phase 1.3 Validator reports

Phase 1.4:
adaptation result
loss
quarantine
schema gap
registry gap
immutability
gate result
test report
debt overlay

不要为了数量支持不真实的格式。


============================================================
32. 不读取自然语言重新理解结果
============================================================

例如：

不要解析message文本来判断category。

优先使用：

rule_id
category
structured status
structured reason

自然语言message只作为：

preserved text。


============================================================
33. No LLM
============================================================

整个：

src/macromind/audit/**

不得依赖：

OpenAI
HTTP
network
embedding
transformer
NLP classifier


============================================================
34. Deterministic serialization
============================================================

机器输出：

UTF-8

stable ordering

sort keys where appropriate

normalized newline

deterministic hash不得包含：

wall clock

absolute path

machine name

temporary run id


============================================================
35. Operational created_at
============================================================

ContinuityAnnotation允许：

created_at

但：

created_at不能进入：

annotation semantic hash

AuditRecord deterministic id

NormalizedAuditBundle semantic hash。


============================================================
36. Immutability
============================================================

保护：

Frozen

Golden

Schema

Registry

Validator

Compatibility

Phase 1.0–1.4正式Artifacts

本阶段默认只允许修改：

src/macromind/audit/**

tests/audit/**

scripts/verify_phase1_5a.py

docs/PHASE1_5A_AUDIT_CONTRACT.md

docs/ANALYTICAL_CONTINUITY_HOOK.md

phase1/phase1_5a_*

如需要CLI：

本阶段暂时不要加。


============================================================
37. 为什么暂时不要CLI
============================================================

Phase 1.5A先稳定：

Contract

Normalization

Provenance

Continuity hook

CLI等到：

Phase 1.5C Audit Runner

再统一加入：

macromind audit run。


============================================================
38. 测试：Normalization
============================================================

至少测试：

Validator ERROR preserved

Validator WARNING preserved

INDETERMINATE preserved

Adaptation loss preserved

Quarantine preserved

Schema gap preserved

Registry gap preserved

Gate PASS preserved

Gate FAIL preserved

Debt status preserved

unsupported artifact not silently lost


============================================================
39. 测试：Provenance
============================================================

验证：

每个AuditRecord都有：

source artifact hash

source pointer

record id

source pointer能够重新定位原始记录。


============================================================
40. 测试：Determinism
============================================================

同一输入运行3次：

record ids一致

record ordering一致

bundle semantic hash一致

输出语义一致。


============================================================
41. Filename metamorphism
============================================================

相同内容：

a.json
banana.json

normalize结果：

semantic result相同。


============================================================
42. Source mutation测试
============================================================

normalize前后：

输入bytes hash完全相同。


============================================================
43. Continuity Hook测试
============================================================

测试：

candidate不会自动confirmed

thread_ref可以为空

人工confirmed必须有reviewer

unresolved refs不会被猜

relation_type改变会改变semantic annotation id

created_at变化不改变semantic annotation hash


============================================================
44. 禁止自动Thread测试
============================================================

提供两个标题/文本非常相似的分析对象。

系统：

不得自动产生：

ContinuityAnnotation

不得自动生成：

thread_ref。


============================================================
45. 真实Artifact测试
============================================================

至少使用：

1份真实Phase 1.3 Validator report

1份真实Phase 1.4 adaptation result

1份真实Phase 1.4 gap report

1份真实Phase 1.4 gate result

完成normalization smoke。


============================================================
46. Phase 1.5A机器产物
============================================================

生成：

phase1/
  phase1_5a_input_manifest.json
  phase1_5a_normalization_report.json
  phase1_5a_test_report.json
  phase1_5a_immutability_report.json
  phase1_5a_gate_result.json
  phase1_5a_manifest.json
  phase1_5a_execution_progress.json
  phase1_5a_execution_progress.jsonl


============================================================
47. 不生成Pattern机器产物
============================================================

不得生成：

patterns.json

thread_index.json

audit_summary.json

AUDIT_REPORT.md

这些属于后续Phase。


============================================================
48. Phase 1.5A Gate
============================================================

至少：

A01 Phase 1.4 final state still accepted

A02 Existing tests all PASS

A03 Supported artifacts normalize

A04 Unsupported input preserved/reported

A05 Source hashes verified

A06 Every AuditRecord traceable

A07 Deterministic record IDs

A08 Deterministic output

A09 Filename/path invariance

A10 Severity preserved

A11 Unknown/Indeterminate preserved

A12 Source inputs unchanged

A13 Frozen unchanged

A14 Golden unchanged

A15 Schema unchanged

A16 Registry unchanged

A17 Validator unchanged

A18 Compatibility unchanged

A19 Continuity annotation defaults unreviewed

A20 No automatic Thread creation

A21 No LLM/network/NLP

A22 Phase 1.5B NOT_STARTED

A23 Phase 1.5C NOT_STARTED

A24 Phase 1.6 NOT_STARTED

A25 Analyst Model/Skills NOT_READY


============================================================
49. 最终Gate状态
============================================================

只能：

READY_FOR_PHASE_1_5B

或：

NOT_READY_AUDIT_NORMALIZATION_BLOCKER


============================================================
50. 最终输出摘要
============================================================

最终只报告：

Phase 1.5A completed:
yes/no

Audit version:
...

Input artifacts normalized:
...

Audit records:
...

Unsupported artifacts:
...

Continuity annotations automatically created:
必须为 0

Existing tests:
PASSED / FAILED / ERROR / SKIPPED

Phase 1.5A tests:
PASSED / FAILED / ERROR / SKIPPED

Frozen changed:
yes/no

Golden changed:
yes/no

Schema changed:
yes/no

Registry changed:
yes/no

Validator changed:
yes/no

Compatibility changed:
yes/no

Phase 1.5B executed:
false

Phase 1.5C executed:
false

Phase 1.6 executed:
false

Analyst Model:
NOT_READY

Analyst Skill:
NOT_READY

Gate:
READY_FOR_PHASE_1_5B
or
NOT_READY_AUDIT_NORMALIZATION_BLOCKER