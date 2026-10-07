# MacroMind Codex Phase 1 Engineering Plan

## 一、Phase 1 的最终目标

Phase 1 完成时，我们要得到的不是一个“能跑的大模型应用”，而是一个稳定的 **MacroMind Semantic Infrastructure V0.1**：

```
Frozen Semantic Contract
        ↓
Executable Schema
        ↓
Registry
        ↓
Validator Engine
        ↓
Legacy Compatibility
        ↓
Audit Runner
        ↓
Golden Regression Suite
        ↓
Phase 1 Engineering Gate
```

成功标准可以压缩成一句：

> **任何新的 Golden / Episode 进入系统后，都能够按照 V0.3 Frozen Contract 被解析、验证、审计、版本化，而不需要重新解释 Ontology。**

现在 Core Ontology 已冻结、Codex Phase 1 仍为 `NOT_STARTED`，Analyst Model、Skill、Production 也都还没有Ready，所以这一步应该严格停留在“基础设施工程化”，不要提前进入 Analyst Mining 或 Skill。  freeze_manifest

------

# 二、Phase 1 总体架构

推荐将工程依赖做成单向结构：

```
Frozen Contract
      ↓
Contract Loader
      ↓
Executable Schema
      ↓
Registry
      ↓
Validator Engine
      ↓
Legacy Adapters
      ↓
Audit Pipeline
      ↓
CLI / API
      ↓
Regression Tests
```

关键原则：

```
下层可以依赖上层
上层绝不能反向依赖下层

Golden不能定义Schema
Validator不能改Ontology
Migration不能修事实
Review不能豁免Schema合法性
```

这一点非常重要。

我们前面最大的经验之一就是：

> ```
> ReviewState ≠ SchemaValidity
> ```

以后这应该成为系统结构，而不是靠Prompt提醒。

------

# 三、推荐代码库结构

建议 `macro-mind-engine/` 以后演化成这样：

```
macro-mind-engine/
│
├── pyproject.toml
├── README.md
│
├── contracts/
│   └── v0_3/
│       ├── CORE_ONTOLOGY_V0.3_FROZEN.md
│       ├── core_objects.json
│       ├── core_boundaries.json
│       ├── core_principles.json
│       ├── freeze_manifest.json
│       └── CHANGE_POLICY.md
│
├── src/macromind/
│
│   ├── contract/
│   │   ├── loader.py
│   │   ├── integrity.py
│   │   ├── version.py
│   │   └── semantic_hash.py
│
│   ├── schema/
│   │   ├── base.py
│   │   ├── core/
│   │   │   ├── source.py
│   │   │   ├── claim.py
│   │   │   ├── event.py
│   │   │   ├── structural_process.py
│   │   │   ├── actor.py
│   │   │   ├── indicator.py
│   │   │   ├── policy.py
│   │   │   ├── mechanism.py
│   │   │   ├── argument.py
│   │   │   ├── thesis.py
│   │   │   ├── forecast.py
│   │   │   ├── contradiction.py
│   │   │   ├── assessment.py
│   │   │   └── heuristic.py
│   │   │
│   │   └── auxiliary/
│   │       ├── source_version.py
│   │       ├── source_segment.py
│   │       ├── claim_occurrence.py
│   │       ├── indicator_observation.py
│   │       ├── information_set.py
│   │       ├── expectation_snapshot.py
│   │       ├── scenario.py
│   │       ├── review_queue.py
│   │       ├── analyst_method_signal.py
│   │       └── mechanism_usage.py
│
│   ├── registry/
│   │   ├── object_types.py
│   │   ├── relations.py
│   │   ├── enums.py
│   │   ├── identity.py
│   │   ├── schema_versions.py
│   │   └── validator_rules.py
│
│   ├── validation/
│   │   ├── engine.py
│   │   ├── result.py
│   │   ├── severity.py
│   │   └── rules/
│   │       ├── schema.py
│   │       ├── references.py
│   │       ├── provenance.py
│   │       ├── temporal.py
│   │       ├── boundaries.py
│   │       ├── argument.py
│   │       ├── forecast.py
│   │       ├── analyst.py
│   │       └── governance.py
│
│   ├── migration/
│   │   ├── detector.py
│   │   ├── engine.py
│   │   ├── result.py
│   │   └── adapters/
│   │       ├── gs001_summary.py
│   │       ├── v0_2.py
│   │       ├── v0_3_legacy.py
│   │       └── ma1.py
│
│   ├── audit/
│   │   ├── runner.py
│   │   ├── manifest.py
│   │   ├── diff.py
│   │   └── bundle.py
│
│   └── cli/
│       └── main.py
│
├── registries/
│   └── v0_3/
│       ├── object_types.yaml
│       ├── relations.yaml
│       ├── semantic_roles.yaml
│       ├── recognition_stages.yaml
│       ├── recurrence.yaml
│       └── failures.yaml
│
├── schemas/
│   └── v0_3/
│       ├── core/
│       └── auxiliary/
│
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── validator/
│   ├── migration/
│   └── golden/
│       ├── gs001/
│       ├── gs002/
│       ├── gs003/
│       ├── gs004/
│       └── gs005/
│
└── docs/
    ├── PHASE1_ARCHITECTURE.md
    ├── VALIDATOR_RULES.md
    ├── MIGRATION_POLICY.md
    └── PHASE1_GATE.md
```

不要一开始引入 Neo4j、向量库、MCP、Agent Runtime。

这些都明确属于 Frozen Contract 之外的实现层，可以以后迭代。  semantic_contract_projection

Phase 1 先把**语义正确性基础设施**做好。

------

# 四、Phase 1.0 — Frozen Contract Loader

这是第一块代码，而且应该很小。

### 任务

让程序能够读取：

```
CORE_ONTOLOGY_V0.3_FROZEN.md
core_objects.json
core_boundaries.json
core_principles.json
freeze_manifest.json
```

然后确认：

```
version = 0.3
status = FROZEN
formal_freeze_executed = true
core_object_count = 14
boundary_count = 15
hash match
semantic hash match
```

如果不匹配：

```
FAIL CLOSED
```

程序停止。

### 核心接口

```
load_contract("0.3") -> FrozenContractverify_contract(contract) -> ContractIntegrityReport
```



`FrozenContract` 可以包含：

```
versionstatusobjectsboundariesprinciplesmanifestsemantic_hash
```



### Gate

必须做到：

```
错误版本 → fail
文件被修改 → fail
hash不一致 → fail
少一个Core → fail
多一个Core → fail
```

这是以后所有模块的“地基”。

------

# 五、Phase 1.1 — Executable Schema

这是整个Phase 1最重要的第一大模块。

推荐：

```
Python
+
Pydantic v2
+
JSON Schema export
```

Pydantic作为运行时Contract，JSON Schema作为跨语言Contract。

## 1. Core Models

为14个Frozen Core建立正式模型：

```
SourceClaimEventStructuralProcessActorIndicatorPolicyMechanismArgumentThesisForecastContradictionAssessmentHeuristic
```



定义必须来源于Frozen Contract，不允许Codex自己“优化”。

Core定义已经明确被逐字冻结。  CORE_ONTOLOGY_V0.3_FROZEN

## 2. Auxiliary Models

Phase 1至少实现当前已经被真实案例证明需要的：

```
SourceVersion
SourceSegment
ClaimOccurrence
TranscriptCorrection
IndicatorObservation
InformationSet
ExpectationSnapshot
Scenario
ReviewQueue
AnalystMethodSignal
MechanismUsage
```

这些明确属于Non-Core，未来可以继续演化。  semantic_contract_projection

## 3. Unknown必须是一等公民

不要设计成：

```
semantic_role: SemanticRole
```



然后逼模型填一个值。

应该允许：

```
semantic_role: SemanticRole = UNKNOWN
```



或：

```
semantic_role: SemanticRole | None
```



具体使用 `UNKNOWN` 还是 `None` 由Registry定义。

核心原则：

```
Unknown > Guess
```

------

# 六、Phase 1.2 — Registry System

Schema回答：

> “结构长什么样？”

Registry回答：

> “允许出现什么？”

至少建立6类Registry：

```
ObjectType Registry
Relation Registry
Enum Registry
Identity Registry
Schema Version Registry
Validator Rule Registry
```

## ObjectType Registry

记录：

```
Claim:
  kind: core
  ontology_version: 0.3

Scenario:
  kind: auxiliary

AnalystMethodSignal:
  kind: analyst_auxiliary
```

## Relation Registry

例如：

```
SUPPORTED_BY
CONTRADICTS
ASSERTED_BY
OBSERVED_AS
USES_MECHANISM
DERIVED_FROM
LOCATED_IN
INSTANCE_OF
```

以后不能让每个Golden自己造relation字符串。

## Enum Registry

包括：

```
semantic_role
recognition_stage
comparison_type
expression_level
analysis_context
failure_type
recurrence_status
recurrence_match
verification_status
```

## Identity Registry

解决：

```
同一公司不同名字
同一Source不同转载
Actor vs Geography
Mechanism reuse
```

这直接对应目前仍存在的全库Registry债务。D07就明确指出正式对象/关系/enum/identity registry还不完整。  freeze_debt_ledger

------

# 七、Phase 1.3 — Validator Engine

这一块要从“Golden专用脚本”升级成真正通用引擎。

建议统一接口：

```
validate(    document,    contract_version="0.3",    schema_version=None) -> ValidationReport
```



统一Issue结构：

```
ValidationIssue(    rule_id="V-MA111",    severity="ERROR",    object_ref="MS02",    json_path="...",    message="...",    evidence_refs=[],    review_required=False)
```



## Validator分成7层

```
L1 Schema
L2 Reference
L3 Provenance
L4 Temporal
L5 Semantic Boundary
L6 Reasoning
L7 Governance
```

### L1 Schema

检查：

```
必填字段
enum合法性
对象形状
canonical field presence
```

Review open不能豁免。

### L2 Reference

```
ID存在
引用存在
类型匹配
无dangling refs
```

### L3 Provenance

例如：

```
Source → Claim
Claim → SourceSegment
origin family
SourceVersion
```

### L4 Temporal

重点正式实现：

```
KnowledgeCutoff
ReferenceTime
AssertedAt
PredictionWindow
ComparisonTime
ContentTime
SourceVersion
Prior Eligibility
```

尤其要把GS004发现变成系统规则：

```
Golden number != chronology
```

### L5 Semantic Boundary

直接实现Frozen 15 Boundary。

例如：

```
B01 Source ↔ Claim
B02 Claim ↔ Event
B05 Indicator ↔ Observation
B08 Thesis ↔ Forecast
B09 Scenario ↔ Forecast
B11 Assessment ↔ Reality
```

Freeze已经明确：这些语义边界虽然被冻结，但部分还处于 `needs_validator / needs_field` 状态。  semantic_contract_projection

### L6 Reasoning

检查：

```
Argument graph
denominator
unit
role transitions
inferential distance
creator shortcut
most fragile step
unsupported causal jump
```

### L7 Governance

检查：

```
model_diagnostic不能进入Analyst method
unknown不得被偷填
future evidence不能当prior
single MethodSignal不能变Skill Rule
```

------

# 八、第一批必须工程化的Validator

不要一次写100条。

Phase 1第一批我建议只做最重要的20–30条。

重点覆盖：

```
Source → Claim provenance
Claim ≠ Event
Event ≠ StructuralProcess
Indicator ≠ Observation
Scenario ≠ Forecast
Thesis ≠ Forecast
Assessment ≠ Reality
Mechanism ≠ MechanismUsage
Mechanism ≠ Argument
Golden number ≠ chronology
future prior leakage
model diagnostic → method evidence forbidden
role/stage transformation
percent vs percentage point
Argument denominator/unit integrity
```

这些都已经在Frozen边界或GS004/005中真实踩过坑，而不是理论上想出来的。

比如Frozen Contract已经明确规定 Scenario只能保存分支，而Forecast必须满足主体判断准入。  CORE_ONTOLOGY_V0.3_FROZEN

------

# 九、Phase 1.4 — Legacy Compatibility Layer

这一块非常重要。

目前：

```
GS001
GS002
GS003
GS004
GS005
```

并不是同一种Schema。

绝不能做：

```
全部重新让LLM抽一次
```

正确做法：

```
原始对象
↓
Version Detector
↓
Legacy Adapter
↓
Canonical Runtime View
```

## Adapter设计

例如：

```
detect_version(document)
```



结果可能：

```
GS001-summary
V0.2
V0.3-legacy
MA1
```

然后：

```
adapt(document)
```



返回：

```
AdaptationResult(    original_unchanged=True,    canonical_view=...,    warnings=[],    unknowns=[],    migration_needed=False,)
```



### 关键规则

Adapter可以：

```
rename
normalize enum
add unknown
map known legacy field
```

Adapter不能：

```
重新判断事实
重新构造Argument
重新生成Claim
猜semantic_role
猜recognition_stage
```

------

# 十、Phase 1.5 — Audit Runner

这一步把我们过去几周手工做的东西产品化。

最后应该能运行：

```
macromind contract verify

macromind validate golden.json

macromind adapt golden.json

macromind audit golden.json
```

最好还支持：

```
macromind regression
```

一次audit输出标准包：

```
.audit/
└── run_20260927_xxx/
    ├── input_manifest.json
    ├── canonical_view.json
    ├── validation.json
    ├── review_queue.json
    ├── diff.json
    ├── audit_log.jsonl
    └── run_summary.json
```

这样以后每一期视频进来，都走统一Pipeline。

------

# 十一、Phase 1.6 — Golden Regression Suite

这是Phase 1能不能真正可靠的核心。

GS001–GS005不再只是“开发资料”，而应该成为：

# Regression Fixtures

不是验证：

```
输出是不是和以前一字不差
```

而是验证：

```
关键语义不变量不能退化
```

## GS001

测试：

```
Expectation/Population
Claim时间
Source conflict
Forecast modal strength
```

由于GS001只有summary，要明确标：

```
partial fixture
```

不能造不存在的对象。

## GS002

测试：

```
Event vs StructuralProcess
increment vs stock
Argument chain
Heuristic candidate
```

## GS003

测试：

```
Scenario ≠ Forecast
SourceVersion
rolling source
physical constraint ≠ political deadline
market infrastructure Event subtype
```

## GS004

至少锁死：

```
GS002不能因编号更小而成为GS004历史prior
MS01 = first_observation / uncertain
共享Mechanism attribution可unknown
OB20 3%不能自动变3pp
model edge不能变creator method evidence
```

## GS005

至少锁死：

```
C005 = Scenario only
condition_not_endorsed_no_branch_selection
technical success != economic success
recovery != cost decline
orders != revenue
ReviewState != SchemaValidity
Finalization第一次失败历史必须保留
```

------

# 十二、Golden Regression不要锁“WARNING数量”

这点很重要。

例如现在：

```
GS004 WARNING=80
GS005 WARNING=69
```

未来Validator增强后：

```
WARNING可能变成83
也可能变成76
```

这是允许的。

真正要锁的是：

```
ERROR invariants
semantic invariants
human decisions
object identity
temporal safety
provenance
```

不要做脆弱测试：

```
assert warnings == 80
```



应该做：

```
assert no_future_leakageassert c005_not_forecastassert model_diagnostic_not_method
```



------

# 十三、Phase 1 Gate

Phase 1结束时不要凭感觉说“完成”。

必须正式过一个Gate。

建议叫：

```
CODEX-PHASE1-GATE-1
```

验收至少包括：

```
G01 Frozen Contract integrity PASS

G02 14 Core executable models present

G03 required Auxiliary models present

G04 Registry loads successfully

G05 Validator deterministic

G06 all references resolvable

G07 Temporal validator active

G08 Scenario/Forecast validator active

G09 Truth propagation guard active

G10 Reasoner attribution validator active

G11 Legacy schema detection works

G12 GS001 adapter works conservatively

G13 GS002 adapter works

G14 GS003 adapter works

G15 GS004 accepted passes

G16 GS005 accepted passes

G17 Original Goldens byte-unchanged

G18 Audit bundle reproducible

G19 Unknown not auto-filled

G20 Golden regression suite PASS
```

最终状态只能是：

```
READY_FOR_BATCH_PILOT

或

NOT_READY_ENGINEERING_BLOCKER
```

------

# 十四、Phase 1期间哪些Debt应该解决

现在D01已经由Freeze Commit解决；历史Ledger仍保留，这个处理已经正确记录。  freeze_debt_status_overlay

Phase 1主要针对：

```
D02 legacy schema compatibility
D03 Scenario / Forecast validator
D04 recurrence chronology
D07 Registry
D11 Argument validator
D16 comparison/role/stage schema
D18 audit/regression tooling
D20 truth/boundary validation
```

其中D02不要求把GS001–003全部迁移成MA.1。

**有Adapter即可先过Phase 1。**

这是一个很重要的范围控制。

其他例如：

```
D08 ASR/Data Quality
D12 StructuralProcess正式正例
D13 Contradiction正式正例
D14 validated Heuristic
```

主要留给Batch Pilot或Pre-Skill。

不要把Phase 1变成“清完所有Debt”。

------

# 十五、推荐实施顺序

实际Codex执行，我建议严格这么来：

```
Step 1
建立工程骨架
        ↓
Step 2
Contract Loader + Hash Verification
        ↓
Step 3
Pydantic Base Models
        ↓
Step 4
14 Core Models
        ↓
Step 5
Auxiliary Models
        ↓
Step 6
JSON Schema Export
        ↓
Step 7
Registry
        ↓
Step 8
Validator Result / Rule Framework
        ↓
Step 9
基础Schema + Reference Validators
        ↓
Step 10
Temporal Validators
        ↓
Step 11
Semantic Boundary Validators
        ↓
Step 12
Argument / Analyst Validators
        ↓
Step 13
Legacy Version Detector
        ↓
Step 14
Adapters
        ↓
Step 15
Audit Runner
        ↓
Step 16
CLI
        ↓
Step 17
GS001–005 Regression
        ↓
Step 18
Phase 1 Gate
```

不要让Codex“一次把整个MacroMind写完”。

每一个Step都：

```
implementation
↓
tests
↓
gate
↓
commit
```

这样出了问题可以定位。

------

# 十六、建议的技术选型

Phase 1尽量克制：

```
Language:
Python 3.12+

Models:
Pydantic v2

Schema:
JSON Schema 2020-12

Testing:
pytest

CLI:
Typer

Serialization:
stdlib json / PyYAML

Hash:
hashlib SHA-256

Storage:
暂不绑定数据库

Logging:
structured JSONL
```

先不要引入：

```
Neo4j
Kafka
Celery
Redis
Vector DB
Kubernetes
```

MacroMind Phase 1现在最大的风险不是性能，而是：

> **把错误的语义快速地工程化。**

所以优先级是：

```
correctness
> auditability
> determinism
> performance
```

------

# 十七、Phase 1最重要的工程原则

我建议以后把下面这几条写进项目README首页：

```
Frozen Contract is authoritative.

Schema does not redefine Ontology.

Validator does not repair facts.

Migration does not re-extract semantics.

Review does not waive schema validity.

Unknown is valid data.

Model inference is attributed.

Original artifacts are immutable.

All transformations are diffable.

Every run is auditable.
```

这基本就是我们从GS001跑到Freeze付出的所有学费，浓缩成10句话。

------

# 十八、Phase 1结束后的项目形态

现在：

```
MacroMind
≈ 一套严谨规范
+ 5个Golden
+ 一堆验证出来的方法
```

Phase 1完成之后应该变成：

```
MacroMind Engine
│
├─ understands contract versions
├─ validates semantic objects
├─ knows registries
├─ handles legacy data
├─ preserves provenance/time
├─ detects semantic violations
├─ creates review queues
├─ emits audit bundles
└─ regression-tests itself
```

这时才真正有资格进入：

```
30–50期 Batch Pilot
```

因为那时候我们测试的是：

> **系统能不能规模化。**

而不是：

> “第6个案例又让我们手工改一堆Prompt。”

------

# 十九、项目主路线现在正式更新为

```
Core Ontology Research                ✅
Golden #001–#005                      ✅
MA / MA.1                             ✅
Migration / Finalization              ✅
Freeze Readiness                      ✅
Core Ontology V0.3 Freeze             ✅

                ↓

Codex Phase 1                         ← 当前
├── Contract Loader
├── Executable Schema
├── Registry
├── Validator Engine
├── Legacy Compatibility
├── Audit Runner
└── Golden Regression

                ↓

Phase 1 Gate
                ↓
30–50 Episode Batch Pilot
                ↓
Pipeline Evaluation
                ↓
Analyst Method Mining
                ↓
9527 Analyst Model V0.1
                ↓
Skill Compilation
                ↓
9527 Skill V0.1
                ↓
Holdout / Blind Evaluation
```

而且Frozen Contract已经明确允许Schema、Enum、Validator、Registry、Analyst Layer和Runtime在不改变核心语义的情况下继续演化，所以Phase 1正是这个版本政策允许的下一步。  CHANGE_POLICY

**我的建议是：这份 Engineering Plan 先作为Phase 1设计基线，不直接让Codex一口气实现全部。下一步应该再生成一个 MacroMind Codex Phase 1.0–1.2 Execution Prompt，先完成工程骨架、Contract Loader、Executable Schema和Registry；验收通过后，再进入Validator Engine。**