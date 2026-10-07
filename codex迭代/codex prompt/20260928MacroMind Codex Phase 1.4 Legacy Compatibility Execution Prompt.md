你正在执行：

MacroMind Codex Phase 1.4 — Legacy Compatibility

前置阶段状态：

Core Ontology V0.3:
  FROZEN

Phase 1.0 Contract Loader:
  COMPLETE / ACCEPTED

Phase 1.1 Executable Schema:
  COMPLETE / ACCEPTED

Phase 1.2 Registry:
  COMPLETE / ACCEPTED

Phase 1.3 Validator Engine:
  COMPLETE / ACCEPTED

Validator version:
  0.1.0

Ontology version:
  0.3

Schema version:
  0.1.0

Registry version:
  0.1.0

Phase 1.3 Rules:
  37

Phase 1.3 Final Tests:
  Existing: 84 PASS
  Phase1.3: 123 PASS
  Total: 207 PASS
  FAILED: 0
  ERROR: 0
  SKIPPED: 0

Phase 1.4:
  NOT_STARTED

Production Import Ready:
  false

Analyst Model:
  NOT_READY

Analyst Skill:
  NOT_READY

MacroMind Core Skill:
  NOT_READY


============================================================
0. 本阶段唯一目标
============================================================

建立：

MacroMind Legacy Compatibility Layer

使历史MacroMind数据能够：

Legacy Historical Artifact
        ↓
Format / Shape Detection
        ↓
Legacy Adapter
        ↓
Canonical Runtime View
        ↓
Phase 1.3 Validator Engine

核心目标：

让旧数据在：

不修改原始文件
不重新抽取语义
不引入后见之明
不猜缺失字段
不修改Frozen Ontology
不修改Schema
不修改Registry Vocabulary

的前提下，

安全进入当前：

Canonical Schema 0.1.0

运行时世界。

Phase 1.4的成功标准不是：

“所有旧字段100%转换成功”

而是：

“所有转换都可解释、可追踪、可重复；
无法安全转换的内容明确标为unknown、partial、quarantine或unsupported。”


============================================================
1. 本阶段严格不做
============================================================

严禁实现：

Phase 1.5 Audit Runner

Phase 1.6 Golden Regression

Batch Pilot

Analyst Mining

Analyst Model

Skill Compilation

9527 Skill

MacroMind Core Skill

Production Import

Database migration

MCP

Agent Runtime

LLM extraction

LLM re-analysis

LLM semantic reconstruction

Golden re-adjudication

Frozen Ontology change

Schema redesign

Registry vocabulary redesign

不要因为Phase 1.4遇到Legacy问题，
顺手修改Phase 1.1 / 1.2 / 1.3。


============================================================
2. 权威输入
============================================================

必须读取实际workspace。

工程：

macro-mind-engine/

冻结合同：

golden_sample_test/core_ontology/v0.3/

Phase 1.3：

src/macromind/validation/**
src/macromind/schema/**
src/macromind/registry/**
src/macromind/contract/**

registries/v0_3/**
schemas/v0_3/**

历史Golden资产：

GS001
GS002
GS003
GS004
GS005

以及：

MA / MA.1 accepted artifacts
migration artifacts
finalization artifacts
human adjudication artifacts

只读取实际存在文件。

不要根据Prompt猜文件名。

先inventory，
再决定Legacy Families。


============================================================
3. 原始历史数据绝对不可修改
============================================================

所有Legacy / Golden文件：

READ ONLY

禁止：

overwrite
normalize in place
rewrite
reformat
rename original
delete original
fix original
add fields to original

Adapter只能生成：

new runtime artifacts。

如果任何命令试图：

input == output

必须：

HARD ERROR


============================================================
4. Adaptation不是Migration-in-place
============================================================

Phase 1.4中的compatibility/adaptation：

只生成：

Canonical Runtime View

不修改原对象。

所以优先使用模块名：

src/macromind/compatibility/

而不是：

migration/

如果已有migration目录且未用于当前系统：

不要因为命名方便直接复用，
避免与历史Golden migration混淆。


============================================================
5. 推荐目录
============================================================

创建：

src/macromind/compatibility/
├── __init__.py
├── detector.py
├── engine.py
├── models.py
├── registry.py
├── ids.py
├── mapping.py
├── loss.py
├── quarantine.py
└── adapters/
    ├── __init__.py
    ├── summary_only.py
    ├── legacy_pre_ma.py
    ├── v0_3_legacy.py
    └── ma1.py

tests/compatibility/
├── conftest.py
├── helpers.py
├── test_detector.py
├── test_registry.py
├── test_adapters.py
├── test_mapping.py
├── test_loss.py
├── test_quarantine.py
├── test_determinism.py
├── test_validator_integration.py
└── test_cli_compatibility.py

docs/
├── PHASE1_4_COMPATIBILITY_ARCHITECTURE.md
├── LEGACY_COMPATIBILITY_MATRIX.md
├── ADAPTER_POLICY.md
└── PHASE1_4_GATE.md

phase1/
├── phase1_4_legacy_inventory.json
├── phase1_4_adapter_catalog.json
├── phase1_4_manifest.json
├── phase1_4_test_report.json
├── phase1_4_gate_result.json
├── phase1_4_debt_overlay.json
├── phase1_4_immutability_report.json
├── phase1_4_schema_gap.json
├── phase1_4_registry_gap.json
└── phase1_4_execution_progress.json


============================================================
6. Phase 1.3必须保持不变
============================================================

Phase 1.4不得修改：

src/macromind/validation/**

除了：

如果为了公开compatibility integration API，
确有import-level glue需要，

默认也不要修改。

优先：

Compatibility Layer调用Validator，
而不是Validator调用Compatibility。

依赖方向：

Legacy Data
   ↓
Compatibility
   ↓
Canonical View
   ↓
Validator

不能：

Validator
   ↓
Legacy Adapter


============================================================
7. 第一阶段：Legacy Inventory
============================================================

先不要写Adapter。

第一步扫描实际历史资产。

生成：

phase1/phase1_4_legacy_inventory.json

至少记录：

artifact_path

sha256

bytes

top_level_type

top_level_keys

explicit_version_fields

object_sections

object_count

field_signatures

known_schema_markers

known_ma_markers

known_ma1_markers

known_summary_only_markers

candidate_family

detection_basis

adaptation_candidate

notes


============================================================
8. Inventory不得读取语义结论
============================================================

Inventory只能分析：

JSON/YAML/文件结构
字段
类型
version metadata
section names

不得：

重新判断Claim内容

重新分类Scenario/Forecast

重新判断Argument有效性

重新抽取MethodSignal

重新构造Mechanism

Inventory是：

shape inventory

不是：

semantic analysis。


============================================================
9. Legacy Family设计
============================================================

Legacy Family必须按：

结构 / schema shape

而不是：

Golden编号

设计。

初始候选Family可包括：

SUMMARY_ONLY_LEGACY

LEGACY_PRE_MA

V0_3_LEGACY

MA1_COMPAT

UNKNOWN_LEGACY

但：

最终Family名称必须根据实际Inventory调整。

禁止：

GS001_FAMILY
GS002_FAMILY
GS003_FAMILY

这种按Sample编号定义Adapter。


============================================================
10. Golden编号不是格式
============================================================

明确禁止：

if filename contains "004":
    family = MA1

if path contains "GS003":
    family = legacy

Detector不得使用：

文件名
目录名
Golden编号

作为格式判定依据。

文件名只允许：

logging metadata。


============================================================
11. Detector API
============================================================

实现：

detect_legacy_format(document) -> DetectionResult

DetectionResult至少：

family

status

evidence

matched_signatures

conflicting_signatures

explicit_version

shape_hash

Detection status：

EXACT
STRONG
AMBIGUOUS
UNKNOWN

禁止：

float confidence probability

例如：

0.83

不要生成假概率。


============================================================
12. Detector语义
============================================================

EXACT：

存在明确version/schema marker，
唯一对应已知family。

STRONG：

无明确version，
但字段/shape组合唯一对应family。

AMBIGUOUS：

多个family signature同时匹配。

UNKNOWN：

没有已知family可以安全识别。

AMBIGUOUS和UNKNOWN：

不得自动选择Adapter。


============================================================
13. Detector必须Deterministic
============================================================

同一document：

重复检测

family
status
evidence
shape_hash

必须完全一致。

改变：

filename
directory
sample_label

不得改变检测结果。


============================================================
14. Adapter Registry
============================================================

实现：

CompatibilityAdapterRegistry

AdapterSpec至少：

adapter_id

adapter_version

source_family

target_ontology_version

target_schema_version

supported_status

loss_profile

implementation_module

禁止：

if filename == ...

Adapter选择只能依据：

DetectionResult.family

+
target schema version。


============================================================
15. Adapter版本
============================================================

定义：

COMPATIBILITY_ADAPTER_VERSION = "0.1.0"

区分：

Ontology Version = 0.3

Schema Version = 0.1.0

Validator Version = 0.1.0

Compatibility Adapter Version = 0.1.0

未来：

Adapter 0.1.1

不意味着：

Schema变化
Ontology变化


============================================================
16. AdaptationResult
============================================================

建立统一：

AdaptationResult

至少：

source_sha256

source_family

detection_status

adapter_id

adapter_version

target_ontology_version

target_schema_version

status

canonical_bundle

quarantined_items

mapping_ledger

losses

unknowns

warnings

unsupported_fields

source_object_count

canonical_object_count

quarantined_object_count

deterministic_hash


============================================================
17. Adaptation Status
============================================================

只使用：

LOSSLESS

LOSSY_BUT_SAFE

PARTIAL

UNSUPPORTED

定义：

LOSSLESS
=
所有语义字段可直接无损表达。

LOSSY_BUT_SAFE
=
存在无法直接保留的非关键结构，
但没有语义猜测。

PARTIAL
=
部分对象可进入Canonical，
部分无法安全表达。

UNSUPPORTED
=
无法安全生成Canonical View。


============================================================
18. Adapter允许的Operation Taxonomy
============================================================

只允许：

COPY

RENAME

WRAP

FLATTEN

EXPAND_STRUCTURAL

ENUM_MAP

REF_MAP

DEFAULT_UNKNOWN

DROP_NONSEMANTIC

PRESERVE_RAW

QUARANTINE

UNSUPPORTED

禁止：

INFER

GUESS

REASON

RECLASSIFY_SEMANTICALLY

HINDSIGHT_ENRICH

LLM_RECONSTRUCT


============================================================
19. Mapping Ledger
============================================================

每一个Canonical字段的来源必须可解释。

MappingEntry至少：

source_path

target_path

operation

source_value_hash

target_value_hash

semantic_change

reason

evidence

semantic_change：

对于Phase 1.4正常Adapter：

必须默认：

false

如果某操作需要semantic_change=true：

默认认为：

Adapter不允许执行。

进入：

quarantine
或
unsupported。


============================================================
20. Default Unknown
============================================================

旧格式缺少Canonical字段时：

如果Canonical Schema允许unknown：

使用：

unknown

并记录：

operation = DEFAULT_UNKNOWN

reason =
legacy_field_absent
or
legacy_semantics_unavailable

不得：

根据上下文推断。


============================================================
21. Missing vs Unknown vs Null
============================================================

继续遵守Phase 1.1定义：

unknown
=
知道字段语义存在，
但当前历史证据无法判断。

None/null
=
未记录 / 不适用 / schema定义允许空。

missing
=
字段未提供。

Adapter不得把这三类混成一类。


============================================================
22. Required字段无法安全生成
============================================================

如果Canonical required字段：

没有legacy来源

且：

不允许unknown/null

不得发明。

该对象进入：

quarantine

AdaptationResult：

PARTIAL
或
UNSUPPORTED。


============================================================
23. Quarantine
============================================================

建立：

CompatibilityQuarantineItem

至少：

source_path

source_object_type

raw_payload_hash

reason_code

message

missing_semantics

candidate_target_type

suggested_future_action

不得删除raw payload。

如不想直接嵌入raw payload：

保存：

raw_payload_ref
+
raw_payload_hash

必须可回查。


============================================================
24. Canonical ID策略
============================================================

旧对象已有：

稳定唯一ID

优先保留。

如果：

旧ID跨类型冲突

不要自动覆盖。

采用：

deterministic namespace transform

并记录mapping。

没有ID：

生成deterministic ID。

建议：

sha256(
  source_sha256
  + source_path
  + object_type
)

禁止：

uuid4

用于Canonical object identity。


============================================================
25. Canonical ID必须稳定
============================================================

同一Legacy artifact重复adapt：

Canonical object IDs必须完全一致。

换：

filename
folder
sample label

不能改变ID。

source_sha256相同：

应产生相同Canonical ID。


============================================================
26. 引用映射
============================================================

Legacy refs：

先建立：

legacy_id → canonical_id

完整mapping。

再处理：

reference fields。

禁止：

遇到未知ref就猜目标。

如果：

ref无法解析

记录：

unknown / quarantine / warning

具体依据Canonical字段requiredness决定。


============================================================
27. Source Provenance
============================================================

Adapter生成的Canonical对象：

不得伪造新的Source事实。

Legacy provenance存在：

COPY / REF_MAP。

不存在：

unknown / empty according to schema semantics。

不得：

用文件本身自动当作Claim来源，
除非原Legacy格式确实如此定义。


============================================================
28. No Hindsight
============================================================

严禁：

利用后期Golden

利用后期MA.1字段

利用后期人工裁决

来补旧Sample当时不存在的信息，

除非：

该人工裁决明确属于同一个Legacy artifact的正式accepted migration history，

且该信息本来就是该artifact的权威后续修正。

即使如此：

必须保留：

source history
adjudication provenance
mapping origin

不得把它伪装成原始字段。


============================================================
29. Historical Human Decision Preservation
============================================================

对于：

GS004 accepted
GS005 accepted

Adapter必须保留已接受的人类裁决。

不得：

re-adjudicate

不得：

重新把Scenario判成Forecast

不得：

改变comparison unknown

不得：

重写reasoner attribution

不得：

重写future-prior decision


============================================================
30. GS005关键保护
============================================================

必须建立一个compatibility test：

C005

在Accepted legacy输入中：

仍然保持：

Scenario only

不得：

Adapter输出Forecast

除非原Accepted artifact本身就是Forecast。

测试必须依赖：

actual accepted field/shape

而不是硬编码：

if id == "C005"

行为规则必须通用。


============================================================
31. GS004关键保护
============================================================

测试：

future prior decision
comparison unknown
reasoner attribution

经过Adapter后：

不得变化。

但：

不要运行Phase 1.6完整Golden Regression。

这里只做：

targeted compatibility invariants。


============================================================
32. GS001 Summary-only
============================================================

GS001如果实际Inventory确认：

只有summary-level evidence

必须：

detected_family = SUMMARY_ONLY_LEGACY

Adaptation status：

PARTIAL
或
UNSUPPORTED

禁止：

通过summary重建完整：

Claims
Arguments
Forecasts
MethodSignals

建议：

canonical_reconstruction_forbidden = true

可以保留：

summary metadata
fixture metadata
source metadata

但不能伪造完整Golden。


============================================================
33. GS002 / GS003
============================================================

GS002 / GS003主要用于验证：

Legacy family compatibility。

目标：

Legacy Shape
→ Canonical Runtime View

不要求：

MA.1重新迁移。

缺少后期新增字段：

unknown

尤其注意：

reasoner attribution

comparison_basis

recognition_stage

recurrence fields

information set

不得使用后期知识补齐。


============================================================
34. GS004 / GS005
============================================================

MA.1 accepted artifacts预计属于：

near-canonical family

适配目标：

尽量LOSSLESS

或：

LOSSY_BUT_SAFE

但不要：

为了达到LOSSLESS

修改Canonical Schema。


============================================================
35. Detector优先于Adapter
============================================================

Compatibility Engine流程：

load raw
↓
detect
↓
if EXACT/STRONG:
    find adapter
else:
    return safe result
↓
adapt
↓
mapping/loss/quarantine
↓
canonical validation smoke

不要：

try every adapter until one works。


============================================================
36. Compatibility Engine API
============================================================

建议：

CompatibilityEngine(...)

.detect(document)

.adapt(
    document,
    target_schema_version="0.1.0"
) -> AdaptationResult

.adapt_file(
    input_path,
    output_path=None
)

Engine：

不得修改input document。


============================================================
37. Validator Integration
============================================================

Adapter完成后：

Canonical Bundle

必须能够传给：

Phase 1.3 ValidatorEngine

做：

runtime transport validation。

Phase 1.4只要求：

Validator能接受transport

schema version正确

object shapes可解析

refs行为符合当前mode

不要定义：

Golden expected semantic verdict。


============================================================
38. Validator错误处理
============================================================

Adapter结果如果Validator返回：

ERROR

不得：

Adapter自动修复。

AdaptationResult记录：

validator_report_summary

status可：

PARTIAL
或
LOSSY_BUT_SAFE

依据错误性质。

不要循环：

adapt
→ validator error
→ auto change semantics
→ validate again


============================================================
39. Complete vs Partial Bundle
============================================================

Adapter应明确声明：

recommended_validation_mode

complete_bundle
或
partial_bundle

如果旧数据本来就只是部分截取：

不要强行用complete_bundle。


============================================================
40. Legacy Unknown Fields
============================================================

如果Legacy object有Canonical当前不认识的字段：

不要默认删除。

分类：

known_nonsemantic
→ DROP_NONSEMANTIC

semantically meaningful but unsupported
→ PRESERVE_RAW + loss

unknown
→ PRESERVE_RAW + warning

不得把未知legacy字段静默丢弃。


============================================================
41. Loss Model
============================================================

建立：

AdaptationLoss

至少：

loss_id

source_path

category

severity

description

canonical_effect

preserved_raw

review_required

category可包括：

FIELD_UNREPRESENTABLE

SEMANTIC_UNKNOWN

ENUM_UNMAPPED

REFERENCE_UNRESOLVED

REQUIRED_FIELD_UNAVAILABLE

STRUCTURAL_LOSS

SUMMARY_ONLY_LIMITATION

UNKNOWN_LEGACY_FIELD


============================================================
42. Loss Severity
============================================================

建议：

INFO

WARNING

BLOCKING

BLOCKING：

导致该对象不能安全形成Canonical对象。

WARNING：

Canonical仍可安全表示，
但发生已知loss。

INFO：

非语义format loss。


============================================================
43. Lossless定义要严格
============================================================

只有当：

没有semantic loss

没有unknown新增

没有quarantine

没有unsupported meaningful fields

才允许：

LOSSLESS。

不要为了漂亮：

滥用LOSSLESS。


============================================================
44. CLI
============================================================

新增：

macromind compatibility detect

macromind compatibility adapt

例如：

macromind compatibility detect \
  --input legacy.json

macromind compatibility adapt \
  --input legacy.json \
  --output canonical_view.json \
  --contract-root ... \
  --registry-root ...

输出：

AdaptationResult JSON
或
DetectionResult JSON。


============================================================
45. CLI禁止in-place
============================================================

禁止：

--in-place

如果：

input.resolve() == output.resolve()

返回：

exit 2

INPUT_ERROR。


============================================================
46. CLI Exit Codes
============================================================

建议：

0
=
adaptation成功：
LOSSLESS
LOSSY_BUT_SAFE
PARTIAL

1
=
UNSUPPORTED
或
blocking adaptation failure

2
=
CLI / IO / malformed input error


============================================================
47. 原文件hash保护
============================================================

adapt前：

source_sha256_before

adapt后：

source_sha256_after

必须一致。

测试必须验证。


============================================================
48. Adaptation Manifest
============================================================

每个adapt执行输出：

adaptation_manifest.json

至少：

source_sha256

source_family

detection_status

adapter_id

adapter_version

target_ontology_version

target_schema_version

status

source_object_count

canonical_object_count

quarantined_object_count

unknown_count

loss_count

mapping_ledger_hash

canonical_bundle_hash

validator_summary

source_unchanged


============================================================
49. Deterministic Hash
============================================================

AdaptationResult semantic hash不得包含：

wall clock
run id
absolute path
filename
machine name

可包含：

source content hash

detected family

adapter version

canonical bundle

mapping ledger

losses

quarantine

target versions


============================================================
50. Filename Metamorphic Test
============================================================

同一Legacy bytes：

sample_002.json

banana.json

whatever.anyname

检测结果必须一致。

Adaptation semantic hash必须一致。


============================================================
51. Directory Metamorphic Test
============================================================

同一文件移动：

/golden_sample_004/

→

/tmp/random/

不得影响：

family
adapter
canonical IDs
semantic hash。


============================================================
52. Repeat Determinism
============================================================

同一artifact运行3次：

DetectionResult canonical JSON一致。

AdaptationResult semantic部分一致。

Canonical Bundle bytes一致。

Canonical IDs一致。


============================================================
53. Object Order测试
============================================================

如果某Legacy family语义上：

对象顺序不是语义，

对输入object order permutation：

Canonical semantic result应保持稳定。

只有：

明确position-semantic legacy format

可以保持顺序敏感。

如果存在这种情况：

必须文档化。


============================================================
54. Unknown Family
============================================================

随机未知shape：

Detector：

UNKNOWN

Engine：

UNSUPPORTED

不得：

fallback到最近似adapter。


============================================================
55. Ambiguous Family
============================================================

构造同时满足两个Family signature的synthetic input。

结果：

AMBIGUOUS

不得自动选Adapter。


============================================================
56. Schema不变
============================================================

Phase 1.4禁止修改：

src/macromind/schema/**

schemas/v0_3/**

如果Legacy适配无法表达：

生成：

phase1/phase1_4_schema_gap.json

不要修Schema。


============================================================
57. Registry Vocabulary不变
============================================================

默认禁止修改：

registries/v0_3/**

src/macromind/registry/**

如果发现：

当前compatibility确实缺registry vocabulary

生成：

phase1/phase1_4_registry_gap.json

不要自动增加词表。


============================================================
58. 五个Phase 1.3 Schema Gap
============================================================

必须继续保留：

conditional endorsement

Argument typed denominator/unit/transition evidence

controlled dimensional semantics

selected-edge analyst evidence scope

Skill promotion evidence

Phase 1.4不得因为适配旧数据：

偷偷解决这些Gap。


============================================================
59. Legacy accepted truth source优先级
============================================================

若同一个Golden存在：

raw

candidate

migrated

finalized

accepted

必须先建立：

artifact lineage。

不得：

随便选文件名看起来最新的。

正式accepted artifact：

作为当前Legacy compatibility输入的最高历史状态，

但：

raw历史仍不可删除。


============================================================
60. Artifact Lineage
============================================================

生成：

phase1_4_artifact_lineage.json

至少：

artifact

parent_artifact

transition_type

status

authority_level

sha256

known_human_adjudication

用于：

确定应该适配哪个历史状态。


============================================================
61. 不使用Modification Time判Authority
============================================================

禁止：

文件mtime最新
→ authority最高

禁止：

filename排序
→ authority最高

必须依据：

历史artifact metadata
finalization/adjudication records
accepted state。


============================================================
62. Targeted Golden Compatibility Fixtures
============================================================

允许使用GS001–GS005建立：

targeted compatibility fixtures。

但这些不是：

Full Golden Regression。

例如：

GS001:
summary-only stays partial

GS003:
Scenario remains Scenario

GS004:
future-prior historical decision preserved

GS005:
C005 remains Scenario

只测compatibility invariants。


============================================================
63. 不读取后续事实重新裁决
============================================================

Adapter不得问：

“这个Forecast后来准不准？”

不得问：

“这个观点今天看是否正确？”

Legacy compatibility：

只处理历史representation。


============================================================
64. Phase 1.4 Tests
============================================================

至少覆盖：

Detector

Adapter Registry

Mapping

Loss

Quarantine

IDs

Immutability

Determinism

Validator Integration

CLI

Legacy targeted fixtures


============================================================
65. Detector Tests
============================================================

至少：

explicit version → EXACT

unique shape → STRONG

ambiguous shape → AMBIGUOUS

unknown shape → UNKNOWN

filename rename → unchanged

directory rename → unchanged

Golden number rename → unchanged


============================================================
66. Adapter Tests
============================================================

至少：

COPY

RENAME

ENUM_MAP

REF_MAP

DEFAULT_UNKNOWN

PRESERVE_RAW

QUARANTINE

deterministic IDs

source input immutable

unsupported meaningful field


============================================================
67. Loss Tests
============================================================

至少：

missing optional legacy semantic
→ unknown/warning

missing canonical required semantic
→ quarantine/partial

unknown meaningful field
→ preserve raw

summary-only
→ PARTIAL

ambiguous family
→ UNSUPPORTED


============================================================
68. Validator Integration Tests
============================================================

至少：

known Legacy
→ adapt
→ canonical
→ Validator accepts canonical transport

不得：

Validator自动接受raw Legacy。

raw Legacy直接给Validator：

仍应保持：

unsupported_schema_version
或
canonical input error。

Compatibility Layer不能绕过Phase1.3边界。


============================================================
69. No Legacy Logic Inside Validator
============================================================

静态扫描：

src/macromind/validation/**

确认：

没有新增：

legacy
adapter
migration
GS00x
sample-specific compatibility

如果出现：

Phase 1.4 Gate FAIL。


============================================================
70. Existing Tests必须全部继续PASS
============================================================

运行：

所有已有：

Phase 1.0–1.3 tests

当前baseline：

207 PASS

但不要硬编码207作为唯一成功依据。

以实际collection为准。

要求：

FAILED=0
ERROR=0
SKIPPED=0


============================================================
71. Phase 1.4新测试
============================================================

必须单独统计：

existing tests

compatibility tests

total

要求：

全部PASS
无SKIP。


============================================================
72. Ruff / Format
============================================================

沿用现有项目：

ruff check

ruff format --check

不得：

为了通过lint修改Frozen、Golden、Schema、Registry或Phase1.3 Validator语义。


============================================================
73. Immutability Baseline
============================================================

在Phase 1.4开始前生成：

phase1_4_input_hashes.json

保护至少：

Frozen Contract

GS001–GS005原始及accepted历史资产

src/macromind/contract/**

src/macromind/schema/**

src/macromind/registry/**

src/macromind/validation/**

registries/v0_3/**

schemas/v0_3/**

Phase 1.3正式报告与manifest

不得重建旧baseline。


============================================================
74. Allowed Changes
============================================================

Phase 1.4默认只允许：

src/macromind/compatibility/**

tests/compatibility/**

CLI:
src/macromind/cli/main.py

scripts:
verify_phase1_4.py

docs:
Phase1.4 docs

phase1:
Phase1.4 artifacts

其它变化：

必须报告。


============================================================
75. CLI修改
============================================================

main.py允许：

新增compatibility子命令。

不得：

改变contract/schema/registry/validate已有语义。

必须运行现有CLI回归。


============================================================
76. Bounded Acceptance Script
============================================================

建立：

scripts/verify_phase1_4.py

和Phase1.3一样：

它是：

bounded engineering acceptance

不是：

Audit Runner

不得：

跑完整Golden semantic regression

不得：

迁移原文件

不得：

自动修复Legacy。


============================================================
77. Phase 1.4 Debt Overlay
============================================================

生成：

phase1/phase1_4_debt_overlay.json

不得修改：

freeze_debt_ledger.json

phase1/debt_status_overlay.json

phase1/phase1_3_debt_overlay.json


============================================================
78. D02
============================================================

Phase 1.4重点处理：

D02 Legacy schema compatibility。

即使完成：

默认最多：

substantially_addressed_phase1_4

不要标：

resolved

因为：

Phase 1.6 Golden Regression尚未完成。


============================================================
79. D04
============================================================

Legacy temporal compatibility完成后：

D04仍最多：

partially_addressed_phase1_4

因为：

真实Legacy temporal coverage
+
Golden Regression

尚未完全验证。


============================================================
80. D16
============================================================

Legacy role/stage/comparison mapping：

如果只实现：

safe mapping + unknown

则：

partially_addressed_phase1_4

不要声称解决typed unit/transition schema gap。


============================================================
81. D18
============================================================

Compatibility manifests/mapping/loss ledger：

只是为Audit做准备。

D18不能：

resolved

因为Phase 1.5 Audit Runner尚未实现。


============================================================
82. Unknown debt
============================================================

如果Phase 1.4发现新的legacy debt：

允许新增：

phase1_4_discovered_debt.json

但：

不要修改历史Freeze debt count

不要修改Freeze Audit。


============================================================
83. Compatibility Matrix
============================================================

生成：

docs/LEGACY_COMPATIBILITY_MATRIX.md

至少：

Family

Detection

Adapter

Expected Loss Profile

Target Schema

Validator Compatibility

Known Limitations

Representative Artifacts


============================================================
84. Adapter Policy
============================================================

生成：

docs/ADAPTER_POLICY.md

必须明确：

No LLM

No semantic reconstruction

No hindsight

No in-place mutation

Unknown > Guess

Mapping ledger required

Losses explicit

Quarantine before invention

Accepted human decisions preserved


============================================================
85. Architecture文档
============================================================

生成：

docs/PHASE1_4_COMPATIBILITY_ARCHITECTURE.md

至少描述：

Legacy Inventory

Detector

Adapter Registry

Adapter

Canonical Runtime View

Mapping Ledger

Loss Model

Quarantine

Validator Integration

Determinism

Immutability

Scope boundaries


============================================================
86. Machine Artifacts
============================================================

至少生成：

phase1/
  phase1_4_legacy_inventory.json
  phase1_4_artifact_lineage.json
  phase1_4_adapter_catalog.json
  phase1_4_manifest.json
  phase1_4_test_report.json
  phase1_4_gate_result.json
  phase1_4_debt_overlay.json
  phase1_4_immutability_report.json
  phase1_4_schema_gap.json
  phase1_4_registry_gap.json
  phase1_4_execution_progress.json
  phase1_4_execution_progress.jsonl


============================================================
87. Adapter Catalog
============================================================

phase1_4_adapter_catalog.json

至少：

adapter_id

adapter_version

source_family

target_schema_version

implementation

allowed_operations

loss_profile

supported

known_limitations


============================================================
88. Legacy Inventory必须真实
============================================================

Inventory必须来自：

实际当前workspace。

不要手写：

“GS002 probably legacy”

必须提供：

shape signature
source hash
检测证据。


============================================================
89. No fabricated conversion coverage
============================================================

如果某Family实际没有足够样本：

标：

insufficient_fixture_coverage

不要为了Gate：

造一个synthetic Legacy family
再宣称真实Family已支持。


============================================================
90. Targeted Real Legacy Tests
============================================================

至少使用真实历史资产覆盖：

summary-only family

至少一个pre-MA/V0.3 legacy family

至少一个MA.1 accepted family

如果Inventory发现family分类不同：

按实际family调整。

不要硬凑Family数量。


============================================================
91. Phase 1.4 Gate
============================================================

建立：

PHASE1_4_GATE

至少：

G01 Frozen Contract still PASS

G02 Phase1.0–1.3 existing tests all PASS

G03 Legacy inventory generated from actual artifacts

G04 Artifact lineage deterministic

G05 Detector deterministic

G06 Detector ignores filename

G07 Detector ignores Golden number

G08 Ambiguous shape not auto-selected

G09 Unknown shape safely unsupported

G10 Adapter Registry deterministic

G11 Adapter selection only by detected family + target schema

G12 Original legacy artifact unchanged

G13 No in-place mode

G14 No semantic re-extraction

G15 Unknown used instead of guess

G16 Deterministic canonical IDs

G17 Mapping ledger complete

G18 Loss ledger complete

G19 Unsupported meaningful fields preserved

G20 Quarantine works

G21 Summary-only artifact remains partial

G22 Legacy pre-MA/V0.3 artifact adapts conservatively

G23 MA.1 accepted artifact adapts safely

G24 GS004 accepted decisions preserved

G25 GS005 accepted decisions preserved

G26 Canonical Runtime View accepted by Phase1.3 Validator

G27 Raw Legacy still rejected by Phase1.3 Validator

G28 Adaptation deterministic

G29 Filename/directory metamorphism does not change semantic result

G30 Phase1.3 Validator source unchanged

G31 Schema unchanged

G32 Registry vocabulary unchanged

G33 Frozen unchanged

G34 Golden originals unchanged

G35 No Audit Runner

G36 No Golden Regression

G37 Phase1.5 NOT_STARTED

G38 Production Import false

G39 Analyst/Skills remain NOT_READY


============================================================
92. Gate结果
============================================================

最终只能：

READY_FOR_PHASE_1_5

或：

NOT_READY_COMPATIBILITY_BLOCKER

不得：

自动启动Phase 1.5。


============================================================
93. Phase 1.4 Schema Gap
============================================================

如果Legacy compatibility发现：

Canonical Schema无法安全表达某Legacy语义，

记录：

phase1_4_schema_gap.json

字段：

gap_id

source_family

source_path

required_semantics

missing_structure

impact

adaptation_status

recommended_future_action

不得修改Schema。


============================================================
94. Phase 1.4 Registry Gap
============================================================

如果发现：

Legacy enum / relation

无法安全映射当前Registry，

记录：

phase1_4_registry_gap.json

不得：

自动新增Vocabulary。


============================================================
95. No semantic upgrade
============================================================

例如Legacy：

role = unknown

不得：

因为Adapter知道对象来自财务章节
→ revenue

Legacy：

Scenario-like text

不得：

因为后期人类觉得像Forecast
→ Forecast

Compatibility Layer只处理：

representation compatibility。


============================================================
96. Raw Preservation
============================================================

每个AdaptationResult必须保留：

source_sha256

必要时：

raw payload hash

unsupported field snapshot/reference

确保：

任何loss都可以回溯原数据。


============================================================
97. Deterministic serialization
============================================================

所有机器Artifact：

sort keys

stable ordering

UTF-8

newline normalized

不要让：

absolute path
timestamp
run id

污染semantic hash。


============================================================
98. Operational timestamps
============================================================

如果需要：

created_at
run time

只能进入：

operational metadata

不得进入：

canonical bundle semantic hash

adaptation semantic hash。


============================================================
99. Acceptance历史保留
============================================================

如果第一次Phase1.4 Gate失败：

保留：

run_001

不要覆盖。

修复后：

run_002

以此类推。

历史失败永远保留。


============================================================
100. Gate不得自我放宽
============================================================

如果测试失败：

不能：

删test

降低severity

新增legacy exemption

按Golden ID硬编码

修改Schema

修改Validator

来强行过Gate。

先修Compatibility实现。

无法修：

NOT_READY_COMPATIBILITY_BLOCKER。


============================================================
101. Phase 1.4 Manifest
============================================================

phase1_4_manifest.json至少：

phase

compatibility_version

ontology_version

schema_version

validator_version

registry_version

adapter_count

legacy_family_count

supported_family_count

artifact_count

canonical_view_count

quarantine_count

loss_count

tests

gate_status

contract_semantic_hash

registry_hash

source hashes

generated artifact hashes

flags:

phase1_5 = NOT_STARTED
production_import_ready = false
analyst_model = NOT_READY
analyst_skill = NOT_READY
macromind_core_skill = NOT_READY


============================================================
102. Final Tests
============================================================

最终必须运行：

pytest全套

ruff check

ruff format --check

CLI:

macromind contract verify

macromind registry verify

macromind validate

macromind compatibility detect

macromind compatibility adapt

要求：

所有历史CLI语义保持。


============================================================
103. Test报告
============================================================

phase1_4_test_report.json

单独统计：

existing_before_phase1_4

phase1_4_new

total

FAILED

ERROR

SKIPPED

PASSED

禁止：

只报告total。


============================================================
104. Immutability报告
============================================================

phase1_4_immutability_report.json

必须分别：

frozen_changed

golden_changed

schema_changed

registry_changed

validator_changed

unexpected_changes

不要只给一个boolean。


============================================================
105. Final Scope Check
============================================================

静态确认：

没有：

src/macromind/audit
golden_regression
skill compiler
batch pilot
production import

如果存在原历史目录：

要区分：

pre-existing

vs

Phase1.4新增。

不要误报历史文件。


============================================================
106. Phase 1.4完成后的状态
============================================================

如果Gate PASS：

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
  COMPLETE

Phase 1.5:
  NOT_STARTED

Phase 1.6:
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
107. 最终执行摘要
============================================================

完成后只输出：

MacroMind Codex Phase 1.4 completed:
yes/no

Compatibility version:
...

Legacy artifacts inventoried:
...

Legacy families detected:
...

Adapters registered:
...

Adaptation status counts:
LOSSLESS:
LOSSY_BUT_SAFE:
PARTIAL:
UNSUPPORTED:

Canonical views generated:
...

Quarantined objects:
...

Mapping entries:
...

Losses:
...

Unknown defaults:
...

Existing tests:
PASSED:
FAILED:
ERROR:
SKIPPED:

Phase 1.4 tests:
PASSED:
FAILED:
ERROR:
SKIPPED:

Frozen changed:
yes/no

Golden changed:
yes/no

Schema changed:
yes/no

Registry vocabulary changed:
yes/no

Validator changed:
yes/no

Schema gaps:
...

Registry gaps:
...

Debt overlay:
D02:
D04:
D16:
D18:

Phase 1.5 executed:
false

Production Import Ready:
false

Analyst Model:
NOT_READY

Analyst Skill:
NOT_READY

MacroMind Core Skill:
NOT_READY

Phase 1.4 Gate:
READY_FOR_PHASE_1_5
or
NOT_READY_COMPATIBILITY_BLOCKER

Recommended next step:
Phase 1.5 Audit Runner