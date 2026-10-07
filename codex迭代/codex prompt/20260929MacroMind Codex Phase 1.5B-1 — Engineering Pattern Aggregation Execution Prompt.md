你正在执行：

MacroMind Codex Phase 1.5B-1
Engineering Pattern Aggregation


============================================================
0. 当前权威状态
============================================================

Core Ontology V0.3:
FROZEN

Phase 1.0–1.4:
ACCEPTED

Phase 1.5A:
ACCEPTED

Phase 1.5A Gate:
READY_FOR_PHASE_1_5B

Phase 1.5A latest accepted evidence:
phase1/phase1_5a_evidence/run_003

Phase 1.5A current real normalization:
9 explicit engineering inputs
26,220 AuditRecords

Phase 1.5B-1:
NOT_STARTED

Phase 1.5B-2:
NOT_STARTED

Phase 1.5C:
NOT_STARTED

Phase 1.6:
NOT_STARTED

Analyst Model:
NOT_READY

Analyst Skill:
NOT_READY

Production:
NOT_READY


============================================================
1. 本阶段唯一目标
============================================================

建立一个：

deterministic
read-only
reversible

的 Engineering Pattern Aggregation Layer。

输入：

Phase 1.5A NormalizedAuditBundle / AuditRecord[]

输出：

AuditPattern[]
+
Pattern ↔ Occurrence Index
+
Disposition Summary

目标是回答：

“几千/几万条工程Finding，
实际上由多少种重复出现的结构模式构成？”

本阶段只是：

工程问题压缩索引。

不是：

分析推理
风险判断
Ontology判断
自动修复。


============================================================
2. 核心原则
============================================================

必须保持：

AuditRecord occurrence 不删除

AuditRecord occurrence 不修改

Pattern 只是索引

Pattern 必须可以完整 drill-down 回全部 occurrence

Aggregation 必须确定性

不使用 LLM

不使用 embedding

不使用文本相似度

不解析 message 来判断相似性。


============================================================
3. Pattern ≠ Analytical Thread
============================================================

严格区分：

Engineering Pattern

和

Analytical Thread。

本阶段只做：

Engineering Pattern。

不得：

读取 ContinuityAnnotation 来构建Thread

创建 AnalyticalThread

创建 AnalyticalEpisode

做 SAME_ISSUE 自动判断

做 Evidence Delta

做 Judgment Delta

做 topic clustering。


============================================================
4. 不修改 Phase 1.5A
============================================================

Phase 1.5A 已 ACCEPTED。

不得修改已有：

src/macromind/audit/*.py

tests/audit/**

scripts/verify_phase1_5a.py

phase1/phase1_5a_*

docs/PHASE1_5A_AUDIT_CONTRACT.md

docs/ANALYTICAL_CONTINUITY_HOOK.md

优先通过新增独立subpackage实现。


============================================================
5. 推荐实现目录
============================================================

新增：

src/macromind/audit/patterns/
├── __init__.py
├── models.py
├── signature.py
└── aggregate.py

不要为了导出API修改：

src/macromind/audit/__init__.py

测试新增：

tests/audit_patterns/
├── __init__.py
├── helpers.py
├── test_signature.py
├── test_aggregation.py
├── test_disposition.py
├── test_determinism.py
├── test_conservation.py
└── test_real_phase1_5a.py

新增：

scripts/verify_phase1_5b1.py

docs/PHASE1_5B1_PATTERN_AGGREGATION.md


============================================================
6. 输入模型
============================================================

直接消费Phase 1.5A已有：

AuditRecord

NormalizedAuditBundle

不要重新定义：

AuditRecord

不要建立第二套Normalizer。

推荐API：

PatternAggregator.aggregate(
    bundle: NormalizedAuditBundle
) -> PatternAggregationResult


============================================================
7. Record Disposition
============================================================

Phase 1.5B-1首先必须把AuditRecord划为：

PATTERN_ELIGIBLE

TRACE_ONLY

SUMMARY_ONLY

OPAQUE_EXCLUDED


============================================================
8. PATTERN_ELIGIBLE
============================================================

第一版只有以下record_type进入Engineering Pattern：

VALIDATION_FINDING

ADAPTATION_LOSS

QUARANTINE

SCHEMA_GAP

REGISTRY_GAP


============================================================
9. TRACE_ONLY
============================================================

以下record不得进入问题Pattern：

MAPPING_EVENT

它是：

trace / provenance information

不是：

engineering issue。


============================================================
10. SUMMARY_ONLY
============================================================

以下record默认只进入统计：

TEST_RESULT

GATE_RESULT

IMMUTABILITY_EVENT

DEBT_STATUS

不得因为数量多而制造Pattern。


============================================================
11. OPAQUE_EXCLUDED
============================================================

第一版：

UNKNOWN_ENGINEERING_RECORD

不进入Engineering Pattern。

原因：

Phase 1.5A明确保留这些opaque payload，
但尚未赋予可信结构化语义。

本阶段不得：

解析raw payload
解析message
猜category

来聚合UNKNOWN记录。

只统计：

数量
来源artifact数量

并标记：

OPAQUE_EXCLUDED。


============================================================
12. 所有AuditRecord都必须有Disposition
============================================================

26,220条记录中的每一条：

必须且只能属于一种：

PATTERN_ELIGIBLE
TRACE_ONLY
SUMMARY_ONLY
OPAQUE_EXCLUDED

不得：

silent ignore。


============================================================
13. AuditPattern
============================================================

建立独立工程对象：

AuditPattern

它不是：

Frozen Ontology Object

Schema Object

Registry Object

AuditRecord。


============================================================
14. AuditPattern字段
============================================================

至少：

pattern_id

signature

record_type

component

category

rule_id

reason_code

structured_dimensions

source_path_shape

target_path_shape

occurrence_count

artifact_count

occurrence_record_ids

source_artifact_ids

severity_distribution

outcome_distribution

review_required_count

example_record_ids


============================================================
15. Pattern Signature禁止使用
============================================================

Pattern signature不得包含：

record_id

source_artifact_id

source_artifact_hash

source_pointer中的具体array index

message

description prose

review notes

filename

directory

wall clock

run id

random UUID。


============================================================
16. Pattern Signature核心字段
============================================================

PatternSignature至少由：

record_type

component

category

rule_id

reason_code

structured_dimensions

source_path_shape

target_path_shape

构成。

缺失字段：

保持null。

不得猜。


============================================================
17. Severity不进入Signature
============================================================

severity不得决定：

是否属于同一个Pattern。

同一种结构问题如果在不同occurrence中出现：

WARNING
ERROR
INDETERMINATE

仍允许属于同一个Pattern。

AuditPattern记录：

severity_distribution。


============================================================
18. Outcome不进入Signature
============================================================

同理：

source_outcome

不进入pattern identity。

保存：

outcome_distribution。

这样以后可以观察：

同一种结构Pattern
在不同上下文中产生了什么结果。


============================================================
19. structured_dimensions
============================================================

只允许从AuditRecord及其：

metadata.source_record

中读取明确存在的结构字段。

允许的第一版白名单：

source_family

source_object_type

target_object_type

object_type

field

field_name

source_field

target_field

如果字段不存在：

不要生成。


============================================================
20. structured_dimensions禁止推断
============================================================

禁止：

从message猜object_type

从目录名猜source_family

从rule_id文本拆出字段含义

从自然语言描述识别financial role。


============================================================
21. Path Shape
============================================================

AuditRecord可能有：

source_path
target_path

Pattern不能直接使用具体数组index，
否则每个occurrence可能都会变成独立Pattern。

实现：

normalize_path_shape(path)


============================================================
22. Path Shape允许的规范化
============================================================

仅允许：

将明确的纯数字数组索引：

/claims/0/source_refs/2

规范化为：

/claims/*/source_refs/*

不得：

删除字段名

猜ID

模糊字符串token

使用NLP

使用正则猜业务实体。


============================================================
23. Null Path
============================================================

source_path / target_path不存在：

path_shape = null

不要构造假的路径。


============================================================
24. Pattern ID
============================================================

pattern_id必须确定性生成：

pattern:
SHA256(
    canonical PatternSignature
)

禁止：

uuid4。


============================================================
25. Message Metamorphism
============================================================

两个AuditRecord：

所有结构化signature字段相同

只有message不同

必须：

得到同一pattern_id。


============================================================
26. Index Metamorphism
============================================================

例如：

/claims/0/detail
/claims/12/detail

其余signature相同：

必须：

得到同一pattern。


============================================================
27. Reason Code变化
============================================================

如果：

reason_code不同

即使message相似：

必须形成不同Pattern。


============================================================
28. Rule ID变化
============================================================

VALIDATION_FINDING：

rule_id不同

不得错误聚合。


============================================================
29. Record Type变化
============================================================

例如：

SCHEMA_GAP

和：

ADAPTATION_LOSS

即使其它字段相似：

不得属于同一个Pattern。


============================================================
30. Pattern Occurrence守恒
============================================================

设：

eligible_records =
所有PATTERN_ELIGIBLE AuditRecord。

必须满足：

sum(pattern.occurrence_count)
==
len(eligible_records)

并且：

每个eligible record_id
恰好出现在一个pattern中。


============================================================
31. 不允许重复归属
============================================================

同一个AuditRecord：

不能同时属于两个Pattern。

如果发生：

HARD ERROR。


============================================================
32. 不允许遗漏eligible
============================================================

PATTERN_ELIGIBLE record：

如果无法构建PatternSignature：

不得丢弃。

使用：

null dimensions

仍形成保守Pattern。

如果record本身结构损坏：

HARD ERROR

不要静默忽略。


============================================================
33. Pattern occurrence index
============================================================

生成双向Index：

pattern_id
→
occurrence_record_ids[]

和：

record_id
→
pattern_id

用于完整drill-down。


============================================================
34. occurrence refs完整保存
============================================================

不得只保存：

前10个examples。

必须保存：

全部 occurrence_record_ids。

example_record_ids仅用于快速查看。


============================================================
35. Examples deterministic
============================================================

example_record_ids：

按稳定排序取前：

最多5条。

不能随机sampling。


============================================================
36. Artifact统计
============================================================

artifact_count：

必须是该Pattern真实涉及的：

unique source_artifact_ids 数量。

source_artifact_ids稳定排序。


============================================================
37. Severity distribution
============================================================

例如：

{
  "ERROR": 3,
  "WARNING": 42,
  "null": 18
}

必须来自原AuditRecord。

不得重新评级。


============================================================
38. Outcome distribution
============================================================

同样保留原始：

source_outcome。

不得生成：

risk_level

importance

priority。


============================================================
39. Review Required
============================================================

review_required_count：

只统计原AuditRecord已有：

review_required == true

不得根据Pattern occurrence数量自动改成true。


============================================================
40. Pattern不是Debt
============================================================

严禁：

Pattern → Debt

自动转换。

例如：

347个Schema Gap occurrence
→ 10个Pattern

不能宣称：

10个Schema Debt。


============================================================
41. Pattern不是Schema提案
============================================================

不得：

自动生成schema patch

registry patch

ontology change

repair recommendation。


============================================================
42. Pattern Aggregation Result
============================================================

建立：

PatternAggregationResult

至少：

patterns

pattern_occurrence_index

record_dispositions

disposition_counts

eligible_occurrence_count

pattern_count

deterministic_hash


============================================================
43. record_dispositions
============================================================

必须可以查询：

record_id
→ disposition

所有输入AuditRecord都有一个明确Disposition。


============================================================
44. Deterministic ordering
============================================================

patterns：

按pattern_id稳定排序。

pattern occurrence IDs：

稳定排序。

distribution dictionary：

稳定key排序。

同样输入运行3次：

byte-stable semantic output。


============================================================
45. Semantic Hash
============================================================

PatternAggregationResult deterministic_hash：

不得包含：

wall clock

filename

absolute path

run directory

machine name

temporary execution id。


============================================================
46. 输入不能修改
============================================================

aggregation前后：

NormalizedAuditBundle semantic hash必须一致。

AuditRecord内容必须一致。


============================================================
47. 不生成新AuditRecord
============================================================

Pattern Aggregator不得：

新增AuditRecord

修改AuditRecord

删除AuditRecord。


============================================================
48. Phase 1.5B-1真实输入
============================================================

正式acceptance必须使用当前accepted：

phase1/phase1_5a_normalization_report.json

作为真实Aggregation输入。

不要重新运行Normalizer来制造一套不同输入。


============================================================
49. Current accepted baseline
============================================================

当前Phase 1.5A报告：

total AuditRecords = 26,220。

不要把26,220硬编码成算法成功条件。

应从实际：

NormalizedAuditBundle.record_counts

计算：

total

eligible

trace

summary

opaque

然后做守恒验证。


============================================================
50. 当前eligible计算方式
============================================================

eligible_expected应动态计算为：

VALIDATION_FINDING
+
ADAPTATION_LOSS
+
QUARANTINE
+
SCHEMA_GAP
+
REGISTRY_GAP

不要手填固定数字。


============================================================
51. 真实结果必须输出
============================================================

Acceptance结束后必须告诉我们：

total_records

eligible_records

trace_only_records

summary_only_records

opaque_excluded_records

pattern_count

largest_pattern_occurrence_count

patterns_by_record_type


============================================================
52. largest pattern只是描述
============================================================

可以记录：

largest_pattern_occurrence_count

但：

不要叫：

highest risk

worst pattern

most important pattern。


============================================================
53. 不做人工报告
============================================================

Phase 1.5B-1不生成：

AUDIT_REPORT.md

Human Report

Dashboard

Top Risks

Remediation Plan。


============================================================
54. 不做Continuity
============================================================

不得使用：

ContinuityAnnotation

relation_type

thread_ref

SAME_ISSUE_CANDIDATE

作为本阶段Pattern输入。


============================================================
55. 不修改Continuity Hook
============================================================

不得修改：

src/macromind/audit/continuity.py

ANALYTICAL_CONTINUITY_HOOK.md。


============================================================
56. No LLM / Network
============================================================

新增：

src/macromind/audit/patterns/**

不得依赖：

OpenAI

requests

httpx

socket

transformers

embedding libraries

NLP libraries。


============================================================
57. No fuzzy clustering
============================================================

禁止：

cosine similarity

Levenshtein clustering

semantic similarity

keyword similarity

fuzzy string grouping。

只允许：

deterministic structural signature。


============================================================
58. 测试：Disposition
============================================================

至少验证：

VALIDATION_FINDING → PATTERN_ELIGIBLE

ADAPTATION_LOSS → PATTERN_ELIGIBLE

QUARANTINE → PATTERN_ELIGIBLE

SCHEMA_GAP → PATTERN_ELIGIBLE

REGISTRY_GAP → PATTERN_ELIGIBLE

MAPPING_EVENT → TRACE_ONLY

TEST_RESULT → SUMMARY_ONLY

GATE_RESULT → SUMMARY_ONLY

IMMUTABILITY_EVENT → SUMMARY_ONLY

DEBT_STATUS → SUMMARY_ONLY

UNKNOWN_ENGINEERING_RECORD → OPAQUE_EXCLUDED


============================================================
59. 测试：Signature
============================================================

至少验证：

same structured fields + different message
→ same pattern

different reason_code
→ different pattern

different rule_id
→ different pattern

different record_type
→ different pattern

numeric array index change
→ same pattern

field name change
→ different pattern。


============================================================
60. 测试：Severity
============================================================

同Pattern：

一个WARNING

一个ERROR

必须：

same pattern_id

severity_distribution正确。


============================================================
61. 测试：Outcome
============================================================

同Pattern不同：

source_outcome

仍：

same pattern

outcome_distribution正确。


============================================================
62. 测试：Conservation
============================================================

必须验证：

eligible count守恒

每个eligible只属于一个Pattern

无eligible遗漏

无duplicate assignment。


============================================================
63. 测试：Trace排除
============================================================

10,000个MAPPING_EVENT：

不得产生问题Pattern。

但：

Disposition count必须记录10,000。


============================================================
64. 测试：Opaque排除
============================================================

10,000个UNKNOWN_ENGINEERING_RECORD：

不得解析payload制造Pattern。

必须：

OPAQUE_EXCLUDED = 10,000。


============================================================
65. 测试：Determinism
============================================================

同一bundle运行3次：

pattern IDs相同

pattern ordering相同

occurrence index相同

semantic hash相同。


============================================================
66. 测试：Input order
============================================================

如果仅改变：

AuditRecord输入array顺序

但AuditRecord集合完全相同：

Pattern semantic result必须一致。


============================================================
67. 测试：Filename invariance
============================================================

Phase 1.5A AuditRecord本身已不以filename作为身份。

Pattern层也不得重新引入filename dependence。


============================================================
68. Real Phase 1.5A Test
============================================================

使用真实：

phase1_5a_normalization_report.json

验证：

所有26,220条record有Disposition

eligible occurrence conservation

pattern IDs唯一

index双向一致

input hash不变。


============================================================
69. 不要求特定pattern数量
============================================================

不得事先硬编码：

“应该有47个pattern”

或其他数字。

真实pattern数量必须由实际数据决定。


============================================================
70. Pattern过多不是自动失败
============================================================

如果实际结果发现：

pattern数量仍然很多

不要为了数字漂亮：

放宽signature

解析message

做fuzzy clustering。

先如实输出。

后续由人工决定是否调整Pattern Contract。


============================================================
71. Pattern过少同样不自动成功
============================================================

如果只有很少Pattern：

检查是否：

错误删除结构维度

把不同reason/rule错误合并。

不要追求低Pattern数量。


============================================================
72. Machine Artifacts
============================================================

生成：

phase1/
  phase1_5b1_pattern_catalog.json
  phase1_5b1_pattern_occurrence_index.json
  phase1_5b1_disposition_summary.json

  phase1_5b1_test_report.json
  phase1_5b1_immutability_report.json
  phase1_5b1_gate_result.json
  phase1_5b1_manifest.json

  phase1_5b1_execution_progress.json
  phase1_5b1_execution_progress.jsonl


============================================================
73. pattern_catalog.json
============================================================

至少：

pattern_version

input_normalization_hash

pattern_count

eligible_occurrence_count

patterns


============================================================
74. pattern_occurrence_index.json
============================================================

至少：

by_pattern

by_record

并包含：

integrity checks。


============================================================
75. disposition_summary.json
============================================================

至少：

total_records

PATTERN_ELIGIBLE

TRACE_ONLY

SUMMARY_ONLY

OPAQUE_EXCLUDED

record_types_by_disposition

patterns_by_record_type

largest_pattern_occurrence_count


============================================================
76. 不生成1.5B-2 artifact
============================================================

不得生成：

continuity_index.json

thread_index.json

thread_membership_index.json

Evidence Delta

Judgment Delta。


============================================================
77. Acceptance Baseline
============================================================

执行开始前：

记录Phase 1.5A accepted implementation和artifacts hash。

由于当前工程可能没有Git：

不要依赖Git作为唯一变更依据。

使用：

SHA256 baseline。


============================================================
78. Protected Scope
============================================================

保护：

Frozen

Golden

Contract

Schema

Registry

Validator

Compatibility

Phase 1.5A accepted audit files

Phase 1.5A machine artifacts

Continuity hook。


============================================================
79. Allowed Changes
============================================================

默认只允许新增：

src/macromind/audit/patterns/**

tests/audit_patterns/**

scripts/verify_phase1_5b1.py

docs/PHASE1_5B1_PATTERN_AGGREGATION.md

phase1/phase1_5b1_*

不得修改现有Phase 1.5A源码。


============================================================
80. Hermes目录
============================================================

`.hermes/**`

属于外部operational workspace。

Codex不得修改。

如果执行期间Hermes或用户并行修改：

不要自动白名单整个目录。

停下来记录：

具体路径
hash
外部来源

等待用户确认。


============================================================
81. Existing Tests
============================================================

正式验收：

必须重新运行现有全部测试。

当前accepted baseline约为：

314 PASS

但不要把314当唯一条件。

要求：

existing collection unchanged

FAILED = 0
ERROR = 0
SKIPPED = 0


============================================================
82. New Tests
============================================================

Phase 1.5B-1新增测试：

必须全部：

PASS

FAILED = 0
ERROR = 0
SKIPPED = 0。


============================================================
83. Ruff / Format
============================================================

运行：

ruff check

ruff format --check

仅修复本阶段授权文件。

不得格式化protected历史文件来通过Gate。


============================================================
84. Verification Script
============================================================

建立：

scripts/verify_phase1_5b1.py

它是：

bounded engineering acceptance

不是：

Audit Runner

不是：

Pattern product CLI。


============================================================
85. Verification Script职责
============================================================

至少：

确认Phase 1.5A accepted

验证Phase 1.5A manifest/hash

运行全部tests

运行lint/format

读取accepted normalization report

运行真实Pattern Aggregation

检查disposition completeness

检查occurrence conservation

检查bidirectional index

检查determinism

检查input immutability

检查protected hashes

检查scope

生成Gate和Manifest。


============================================================
86. 不增加CLI
============================================================

本阶段不要修改：

src/macromind/cli/main.py

CLI统一留到：

Phase 1.5C Audit Runner。


============================================================
87. Phase 1.5B-1 Gate
============================================================

至少：

B101 Phase 1.5A remains accepted

B102 Existing tests all PASS

B103 New pattern tests all PASS

B104 Every AuditRecord has exactly one disposition

B105 Eligible record types exact

B106 Trace-only records excluded from issue patterns

B107 Summary-only records excluded from issue patterns

B108 Opaque records not semantically interpreted

B109 Pattern signature structural only

B110 Message metamorphism invariant

B111 Numeric path-index metamorphism invariant

B112 Different reason_code separates patterns

B113 Different rule_id separates patterns

B114 Different record_type separates patterns

B115 Severity does not split structural pattern

B116 Outcome does not split structural pattern

B117 Eligible occurrence count conserved

B118 Every eligible occurrence assigned exactly once

B119 Bidirectional occurrence index consistent

B120 Pattern IDs deterministic

B121 Pattern output deterministic

B122 Input order invariant

B123 NormalizedAuditBundle unchanged

B124 No new AuditRecords created

B125 No Pattern→Debt promotion

B126 No LLM/network/NLP/fuzzy clustering

B127 Phase 1.5A existing source unchanged

B128 Continuity Hook unchanged

B129 Frozen/Golden/Schema/Registry/Validator/Compatibility unchanged

B130 Phase 1.5B-2 NOT_STARTED

B131 Phase 1.5C NOT_STARTED

B132 Phase 1.6 NOT_STARTED

B133 Analyst Model/Skill NOT_READY


============================================================
88. 最终Gate状态
============================================================

只能输出：

READY_FOR_PHASE_1_5B_2

或：

NOT_READY_PATTERN_AGGREGATION_BLOCKER


============================================================
89. Manifest
============================================================

phase1_5b1_manifest.json至少：

phase = "1.5B-1"

pattern_version

audit_version

input_normalization_hash

total_records

eligible_records

trace_only_records

summary_only_records

opaque_excluded_records

pattern_count

patterns_by_record_type

largest_pattern_occurrence_count

tests

gate_status

generated_artifact_hashes

source_hashes

flags:

phase1_5b2 = NOT_STARTED
phase1_5c = NOT_STARTED
phase1_6 = NOT_STARTED
analyst_model = NOT_READY
analyst_skill = NOT_READY
production = NOT_READY


============================================================
90. Progress
============================================================

保留：

失败run

中断run

修复前run

不要覆盖历史证据。

最新progress只是：

resume aid

不是：

acceptance authority。


============================================================
91. 如果发现设计问题
============================================================

如果真实26,220条数据暴露：

当前signature无法稳定表达某类Pattern，

不要：

临时解析message

加LLM

做embedding

修改AuditRecord

修改Phase1.5A。

记录：

phase1_5b1_design_gap.json

并：

NOT_READY_PATTERN_AGGREGATION_BLOCKER

或在明确非阻塞情况下记录限制。


============================================================
92. 最终输出摘要
============================================================

完成后只输出：

MacroMind Codex Phase 1.5B-1 completed:
yes/no

Pattern version:
...

Input AuditRecords:
...

Pattern eligible:
...

Trace only:
...

Summary only:
...

Opaque excluded:
...

Engineering patterns:
...

Patterns by record type:
...

Largest pattern occurrence count:
...

Eligible occurrence conservation:
PASS/FAIL

Bidirectional index:
PASS/FAIL

Deterministic:
PASS/FAIL

Existing tests:
PASSED:
FAILED:
ERROR:
SKIPPED:

Phase 1.5B-1 tests:
PASSED:
FAILED:
ERROR:
SKIPPED:

Phase 1.5A source changed:
yes/no

Continuity Hook changed:
yes/no

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

Automatic Analytical Threads created:
必须为 0

Phase 1.5B-2 executed:
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
READY_FOR_PHASE_1_5B_2
or
NOT_READY_PATTERN_AGGREGATION_BLOCKER