# MacroMind Schema V0.1

**版本：** 0.1-draft
**依赖：** MacroMind Ontology V0.1
**目标：** 定义 MacroMind 各类对象的数据结构、字段约束、引用方式与跨对象校验规则。

------

## 1. Schema设计原则

MacroMind V0.1采用四条底层原则。

### 1.1 对象与评价分离

对象本身记录“它是什么”。

评价记录：

- 是否真实
- 是否重要
- 是否完整
- 是否烟雾弹
- 是否主要矛盾
- 是否可信

因此禁止：

```yaml
event:
  importance: major

claim:
  truth: false

contradiction:
  primary: true
```

统一改成：

```yaml
assessment:
  target_id: xxx
  dimension: importance
  value_code: major
```

------

### 1.2 原始证据不可覆盖

必须保留：

```text
原视频
原音频
Raw Transcript
Normalized Transcript
Correction
```

Normalized版本不能覆盖Raw版本。

------

### 1.3 关系与对象分离

对象文件主要记录对象本身的属性。

复杂关系统一进入：

```text
edges
```

例如：

```text
claim_x SUPPORTS thesis_y
event_x TRIGGERS event_y
mechanism_x TRANSMITS_TO outcome_y
```

避免同一个关系同时维护在多个文件里产生不一致。

------

### 1.4 所有分析必须允许带时间、范围、观察者

宏观判断必须能够回答：

```text
谁认为？
什么时候认为？
在什么范围内认为？
根据什么认为？
```

------

# 2. Schema目录建议

```text
schemas/

├── common/
│   ├── base-object.schema.json
│   ├── reference.schema.json
│   ├── temporal.schema.json
│   ├── spatial.schema.json
│   ├── provenance.schema.json
│   └── scope.schema.json
│
├── core/
│   ├── source.schema.json
│   ├── claim.schema.json
│   ├── event.schema.json
│   ├── actor.schema.json
│   ├── indicator.schema.json
│   ├── policy.schema.json
│   ├── mechanism.schema.json
│   ├── argument.schema.json
│   ├── thesis.schema.json
│   ├── forecast.schema.json
│   ├── contradiction.schema.json
│   ├── assessment.schema.json
│   └── heuristic.schema.json
│
├── auxiliary/
│   ├── source-version.schema.json
│   ├── source-segment.schema.json
│   ├── transcript-correction.schema.json
│   ├── indicator-observation.schema.json
│   └── information-set.schema.json
│
└── graph/
    └── edge.schema.json
```

------

# 3. 公共 BaseObject

除纯原始媒体文件外，所有正式对象必须继承：

```yaml
id: string
object_type: string

schema_version: "0.1"

revision: integer

lifecycle_status:
  active | deprecated | superseded | archived

created_at: datetime
updated_at: datetime

created_by:
  type:
    human | agent | pipeline | import

  id: string

provenance:
  run_id: string | null
  model_id: string | null
  prompt_version: string | null
  input_refs: []

supersedes:
  - object_id

tags:
  - string
```

### ID不得改变

对象名称可以修改：

```text
“中国金融结构转型”
```

ID不能随名称变化。

推荐：

```text
src_
seg_
claim_
event_
actor_
indicator_
obs_
policy_
mechanism_
argument_
thesis_
forecast_
contradiction_
assessment_
heuristic_
edge_
```

------

# 4. Reference

系统内部引用统一：

```yaml
ref_id: string
ref_type: string
```

示例：

```yaml
ref_id: event_20260916_fed_rate_hike
ref_type: event
```

后期允许程序只存ID，但V0.1建议保留类型方便校验。

------

# 5. Temporal

统一时间对象：

```yaml
value: datetime | date | null

precision:
  second
  minute
  hour
  day
  month
  quarter
  year
  unknown

certainty:
  exact
  approximate
  inferred
  disputed
```

时间范围：

```yaml
start:
  <Temporal>

end:
  <Temporal> | null
```

------

# 6. Scope

Scope表示：

> 这个判断在哪个分析范围内成立。

```yaml
domains:
  - domain_code

geographies:
  - geography_id

topics:
  - topic_code

time_range:
  start:
  end:
```

例如：

```yaml
domains:
  - geopolitics

geographies:
  - global
  - east_asia
```

------

# 7. Provenance

所有AI生产的重要对象必须知道是怎么来的：

```yaml
origin_type:
  direct_extraction
  normalized_extraction
  model_inference
  human_input
  imported_data

source_refs:
  - ref

source_segment_refs:
  - ref

model:
  provider: string | null
  model_id: string | null

prompt_version:
  string | null

run_id:
  string | null
```

这会允许未来回答：

> 这批Claim究竟是谁、用哪个模型、哪一版Prompt抽出来的？

------

# 8. Source Schema

表示一个原始信息载体。

```yaml
id:
object_type: source

source_type:
  video
  audio
  news_article
  official_document
  speech
  social_post
  dataset
  research_report
  meeting_record
  book
  other

title: string

canonical_url:
  string | null

publisher_actor_id:
  string | null

author_actor_ids:
  - string

language:
  zh-CN | en | ja | ...

published_at:
  Temporal | null

recorded_at:
  Temporal | null

captured_at:
  Temporal

content_hash:
  string | null

media_ref:
  string | null

parent_source_id:
  string | null

provenance:
  ...
```

### Validation

Source至少满足：

```text
published_at
或
recorded_at
或
captured_at
```

其中之一存在。

------

# 9. SourceVersion Schema

网页内容可能变化，因此Source与SourceVersion分离。

```yaml
id:
object_type: source_version

source_id:

captured_at:

content_hash:

mime_type:

local_path:

text_path:

snapshot_path:

is_current:
  boolean
```

------

# 10. SourceSegment Schema

这是证据定位的核心。

```yaml
id:
object_type: source_segment

source_id:

source_version_id:
  string | null

segment_type:
  transcript
  paragraph
  article_section
  table
  chart
  quote
  data_cell

time_offset:
  start_seconds: number | null
  end_seconds: number | null

text_position:
  start_line: integer | null
  end_line: integer | null

raw_text:
  string

normalized_text:
  string | null

language:

provenance:
  ...
```

必须至少拥有：

```text
time_offset
或
text_position
```

之一。

------

# 11. TranscriptCorrection Schema

```yaml
id:
object_type: transcript_correction

source_segment_id:

raw_text:

normalized_text:

correction_type:
  asr_entity_resolution
  number_correction
  terminology_correction
  punctuation
  segmentation
  probable_speaker_error
  unknown

confidence:
  number # 0~1

status:
  proposed
  accepted
  rejected
  needs_audio_review

evidence_refs:
  - ref

reviewed_by:
  string | null
```

### 强制规则

`needs_audio_review`状态下：

Normalized结果不得升级为verified事实。

------

# 12. Claim Schema

Claim是MacroMind最重要的对象之一。

```yaml
id:
object_type: claim

statement:
  string

claimant_id:
  string

claim_type:
  factual
  interpretive
  causal
  comparative
  normative
  motive_attribution
  counterfactual
  forecast

derivation_type:
  quoted
  paraphrased
  calculated
  inferred
  causal_inference
  historical_analogy
  recommendation
  model_generated

temporal_mode:
  ex_ante
  contemporaneous
  ex_post
  retrospective

asserted_at:
  Temporal

knowledge_cutoff:
  Temporal | null

about_refs:
  - ref

source_segment_refs:
  - ref

certainty_expressed:
  certain
  high
  medium
  low
  speculative
  unknown

provenance:
  ...
```

### Claim禁止直接拥有

```text
truth
importance
smoke_screen
primary
```

这些全部由Assessment提供。

### 强制规则

正常的人类Claim必须有：

```text
claimant_id
asserted_at
source_segment_refs
```

如果：

```yaml
derivation_type: model_generated
```

则允许没有SourceSegment，但必须有：

```text
provenance.model
provenance.input_refs
```

------

# 13. Actor Schema

```yaml
id:
object_type: actor

actor_type:
  country
  government
  central_bank
  organization
  company
  person
  social_group
  market_group
  institution
  other

canonical_name:

aliases:
  - string

geography_refs:
  - geography_id

parent_actor_id:
  string | null

valid_from:
  Temporal | null

valid_to:
  Temporal | null

external_identifiers:
  {}
```

Actor和Geography必须分开。

例如：

```text
Actor：中国政府
Geography：中国
```

不是同一对象。

------

# 14. Event Schema

```yaml
id:
object_type: event

name:

event_types:
  - political
  - geopolitical
  - diplomatic
  - military
  - social
  - economic_policy
  - fiscal_policy
  - monetary_policy
  - industrial
  - technology
  - infrastructure
  - company
  - financial_market
  - data_release
  - other

occurred_at:
  TimeRange

event_status:
  scheduled
  ongoing
  completed
  cancelled
  disputed
  unknown

actor_refs:
  - actor_id

spatial:
  origin_locations: []
  direct_scope: []
  affected_scope: []
  propagation_scope: []

evidence_refs:
  - ref

provenance:
  ...
```

### Event不得包含

```text
重大
一般
核心
烟雾弹
主要矛盾
```

这些全部属于Assessment。

------

# 15. Indicator Schema

Indicator定义“指标是什么”。

```yaml
id:
object_type: indicator

name:

short_name:

category:
  macro
  monetary
  fiscal
  financial_market
  industrial
  social
  demographic
  company
  commodity
  other

unit:

frequency:
  realtime
  daily
  weekly
  monthly
  quarterly
  annual
  irregular

geography_scope:

source_authority_actor_id:

methodology_summary:

seasonally_adjusted:
  boolean | null

revision_possible:
  boolean

provenance:
  ...
```

------

# 16. IndicatorObservation Schema

记录一次具体经济数据。

```yaml
id:
object_type: indicator_observation

indicator_id:

reference_period:
  TimeRange

released_at:
  Temporal

value:
  number | string | null

unit:

previous_value:
  number | string | null

consensus_value:
  number | string | null

revised_from:
  number | string | null

revision_number:
  integer | null

source_refs:
  - ref

provenance:
  ...
```

### 强制规则

必须严格区分：

```text
reference_period
released_at
```

例如：

> 9月发布8月CPI。

------

# 17. Policy Schema

```yaml
id:
object_type: policy

name:

policy_type:
  monetary
  fiscal
  industrial
  trade
  technology
  regulatory
  social
  foreign_policy
  other

issuer_actor_id:

status:
  proposed
  announced
  active
  suspended
  ended
  superseded

valid_from:
  Temporal | null

valid_to:
  Temporal | null

geographic_scope:
  []

instruments:
  - string

official_objectives:
  - string

source_refs:
  - ref

provenance:
  ...
```

### 区别

```text
Policy：
长期存在的政策状态

Event：
某次宣布、修改、加息、执行动作
```

例如：

```text
Fed政策框架 = Policy

2026-09-16加息25bp = Event
```

------

# 18. Mechanism Schema

```yaml
id:
object_type: mechanism

name:

description:

domain_codes:
  - string

status:
  candidate
  established
  disputed
  deprecated

input_concepts:
  - ref

intermediate_steps:
  - sequence: integer
    concept_refs: []
    description: string

output_concepts:
  - ref

conditions:
  - string

countervailing_factors:
  - string

source_refs:
  - ref

provenance:
  ...
```

例如：

```text
利率↑
→
融资成本↑
→
折现率↑
→
高估值资产承压
```

Mechanism是可复用模型，不等于客观事实。

------

# 19. Argument Schema

Argument记录：

> 某一次具体分析是怎样从前提走向结论的。

```yaml
id:
object_type: argument

analyst_id:

argument_type:
  causal
  comparative
  historical_analogy
  abductive
  elimination
  counterfactual
  narrative_deconstruction
  mixed

asserted_at:
  Temporal

knowledge_cutoff:
  Temporal | null

premise_refs:
  - ref

conclusion_refs:
  - ref

steps:
  - step_id:
    sequence:

    from_refs:
      - ref

    to_refs:
      - ref

    relation_type:
      causes
      contributes_to
      supports
      implies
      suggests
      analogizes_to
      contradicts
      reframes

    mechanism_id:
      string | null

    evidence_refs:
      - ref

    inference_mode:
      direct
      statistical
      causal
      analogy
      elimination
      speculation

path_metrics:
  hop_count:
    integer

source_segment_refs:
  - ref

provenance:
  ...
```

### Inferential Distance

不再作为Claim永久属性。

定义为：

```text
argument.path_metrics.hop_count
```

------

# 20. Thesis Schema

Thesis表示持续存在的结构判断。

```yaml
id:
object_type: thesis

title:

statement:

owner_id:
  string

status:
  candidate
  active
  strengthening
  weakening
  resolved
  rejected
  superseded

created_at_analysis:
  Temporal

valid_from:
  Temporal | null

valid_to:
  Temporal | null

scope:
  Scope

provenance:
  ...
```

Supporting Claim、Contradicting Claim、Mechanism等关系：

**不直接手工写入Thesis文件。**

统一通过Edge：

```text
claim SUPPORTS thesis
claim CONTRADICTS thesis
thesis USES_MECHANISM mechanism
```

这样避免双重维护。

------

# 21. Forecast Schema

Forecast是Claim的特殊扩展对象。

```yaml
id:
object_type: forecast

claim_id:

made_at:
  Temporal

knowledge_cutoff:
  Temporal

target_refs:
  - ref

prediction_window:
  TimeRange

direction:
  rise
  fall
  stable
  occur
  not_occur
  above
  below
  custom

threshold:
  number | string | null

conditions:
  - string

resolution_criteria:
  string

resolution_status:
  open
  resolved
  expired
  unresolvable

resolved_at:
  Temporal | null

outcome_refs:
  - ref

provenance:
  ...
```

### 强制规则

Forecast引用的：

```text
claim_id
```

必须满足：

```yaml
claim_type: forecast
```

而且：

```text
made_at <= prediction_window.start
```

------

# 22. Contradiction Schema

```yaml
id:
object_type: contradiction

name:

description:

domain_codes:
  - string

scope:
  Scope

poles:
  - pole_id:
    label:
    actor_refs: []
    objective_claim_refs: []

valid_from:
  Temporal | null

valid_to:
  Temporal | null

status:
  candidate
  active
  transformed
  resolved
  deprecated

provenance:
  ...
```

至少两个：

```text
poles
```

### 严格禁止

```yaml
primary: true
```

主要/次要必须通过Assessment记录。

------

# 23. Assessment Schema

Assessment是整个系统弹性的关键。

```yaml
id:
object_type: assessment

target_ref:
  ref

observer_id:

assessed_at:
  Temporal

scope:
  Scope

dimension:
  veracity
  completeness
  relevance
  importance
  information_gain
  causal_role
  narrative_role
  contradiction_role
  aspect_role
  confidence
  source_quality

value_code:
  string | null

score:
  number | null

components:
  {}

reason:
  string | null

evidence_refs:
  - ref

argument_ref:
  ref | null

provenance:
  ...
```

------

## 23.1 Veracity Values

```text
verified
likely_true
uncertain
disputed
likely_false
false
unverifiable
```

------

## 23.2 Completeness Values

```text
complete
mostly_complete
partial
materially_incomplete
unknown
```

------

## 23.3 Causal Role

```text
root_cause
contributing_cause
transmission
symptom
consequence
correlation_only
causal_inversion
unknown
```

------

## 23.4 Narrative Role

```text
core_signal
supporting_signal
background
noise

distraction
smoke_screen
reassurance
narrative_management
selective_disclosure
agenda_setting
blame_shifting
causal_obscuring
```

------

## 23.5 Contradiction Role

```text
primary
secondary
emerging
declining
latent
```

------

# 24. Importance Assessment

重要性采用多维结构：

```yaml
dimension:
  importance

score:
  0.84

components:

  magnitude:
    0.8

  scope:
    0.9

  persistence:
    0.7

  systemic_effect:
    0.8

  propagation:
    0.9

  novelty:
    0.6

  irreversibility:
    0.5

  policy_authority:
    0.9

  market_surprise:
    0.7

  contradiction_centrality:
    0.9

value_code:
  major
```

### V0.1禁止写死权重

即暂时不规定：

```text
magnitude × 0.2
+
scope × 0.1
...
```

权重在真实数据压力测试后再确定。

UI可暂时显示：

```text
major
important
normal
background
```

但底层保留各维度。

------

# 25. Heuristic Schema

Heuristic代表分析者反复使用的分析方法。

```yaml
id:
object_type: heuristic

name:

statement:

analyst_id:

status:
  candidate
  repeated
  reviewed
  validated
  deprecated

domain_codes:
  - string

trigger_conditions:
  - string

procedure_steps:
  - sequence:
    instruction:

known_exceptions:
  - string

counterexamples:
  - ref

first_observed_at:
  Temporal | null

provenance:
  ...
```

Heuristic与Argument关系：

```text
argument OBSERVES_PATTERN heuristic
```

或：

```text
argument USES heuristic
```

具体relation名称后续可调整。

### 规则

模型第一次发现：

```text
“9527似乎总是先找资金流向”
```

只能建立：

```yaml
status: candidate
```

不能直接validated。

------

# 26. InformationSet Schema

这个对象专门防止“事后诸葛亮”。

```yaml
id:
object_type: information_set

observer_id:

cutoff:
  Temporal

available_source_refs:
  - ref

available_event_refs:
  - ref

available_indicator_observation_refs:
  - ref

known_claim_refs:
  - ref

generation_method:
  exact
  reconstructed
  approximate

confidence:
  number
```

尤其用于：

```text
Forecast
Argument
Retrospective Evaluation
```

------

# 27. Edge Schema

复杂关系统一存Edge。

```yaml
id:
object_type: edge

from_ref:
  ref

relation_type:
  string

to_ref:
  ref

asserted_by:
  observer_id | system

valid_from:
  Temporal | null

valid_to:
  Temporal | null

scope:
  Scope | null

claim_basis_refs:
  - claim_id

evidence_refs:
  - ref

provenance:
  ...
```

V0.1核心Relation：

```text
CONTAINS
DERIVED_FROM
TRANSCRIBED_FROM
CORRECTS

ASSERTS
ABOUT
DESCRIBES
MENTIONS

SUPPORTS
WEAKENS
CONTRADICTS
QUALIFIES
LIMITS

CAUSES
CONTRIBUTES_TO
TRANSMITS_TO
TRIGGERS
AFFECTS

PRECEDES
FOLLOWS

CHANGES
APPLIES_TO

INTERPRETS
USES_MECHANISM
USES_EVIDENCE

SUPERSEDES
VALIDATES
INVALIDATES
```

------

# 28. Registry机制

很多值不要直接硬编码进JSON Schema。

应该存在：

```text
_system/registries/
```

包括：

```text
source_types.yaml
claim_types.yaml
derivation_types.yaml
event_types.yaml
actor_types.yaml
policy_types.yaml
domains.yaml
topics.yaml
geographies.yaml
relations.yaml
assessment_dimensions.yaml
assessment_values.yaml
observers.yaml
```

Schema负责：

> 字段必须是string。

Registry负责：

> 这个string是否合法。

这样以后增加：

```text
AI infrastructure
semiconductor
robotics
```

不需要修改全部Schema。

------

# 29. 扩展值规则

如果Agent遇到Registry不存在的类别：

禁止随便创建正式值。

可以暂存：

```text
x_candidate_<name>
```

例如：

```yaml
event_type:
  x_candidate_financial_sovereignty
```

进入：

```text
review_queue
```

人工确认后再加入Registry。

------

# 30. Observer Registry

Observer不完全等于Actor。

建议独立：

```yaml
observer_id: obs_youhegaojian9527

observer_type:
  analyst

display_name:
  有何高见9527

actor_ref:
  actor_xxx | null
```

系统观察者：

```yaml
observer_id: obs_macromind_verifier

observer_type:
  system
```

模型：

```yaml
observer_id: obs_gpt6_astra

observer_type:
  model
```

这样系统能准确表达：

```text
9527认为A
Reuters认为B
MacroMind verifier认为C
```

而不会混起来。

------

# 31. Cross-object Validation Rules

这一部分以后应该直接变成validator代码。

### R001

Claim正常情况下必须存在：

```text
claimant_id
asserted_at
source_segment_ref
```

------

### R002

```
claim_type=forecast
```

必须：

```text
knowledge_cutoff != null
```

并建立Forecast对象。

------

### R003

Forecast的：

```text
made_at
```

不能晚于预测目标已经发生的时间。

否则进入人工Review。

------

### R004

Event不得直接拥有：

```text
importance
primary
secondary
```

------

### R005

Contradiction不得直接拥有：

```text
primary
secondary
```

------

### R006

Claim不得直接拥有：

```text
true
false
smoke_screen
```

------

### R007

```
narrative_role=smoke_screen
```

只能存在于Assessment中，并必须拥有：

```text
observer_id
```

------

### R008

如果Assessment：

```text
dimension = contradiction_role
value = primary
```

必须同时存在：

```text
scope
assessed_at
observer_id
```

------

### R009

如果SourceSegment经过：

```text
needs_audio_review
```

则其相关事实Claim不能自动获得：

```text
veracity=verified
```

------

### R010

AI生成Claim必须保留：

```text
model_id
prompt_version
input_refs
```

------

### R011

Thesis不能因为新证据出现直接改写历史版本。

重大语义变化必须：

```text
revision + 1
```

或：

```text
SUPERSEDES
```

------

### R012

后来的：

> “我之前预测过X”

只能创建：

```text
retrospective claim
```

不能直接创建历史Forecast。

必须找到原始历史SourceSegment以后才能生成Forecast。

------

# 32. Review Queue Schema建议

虽然不属于Ontology核心对象，但工程必须有。

```yaml
review_id:

issue_type:
  asr_uncertain
  numerical_conflict
  source_conflict
  entity_resolution
  unsupported_claim
  excessive_inference
  registry_extension
  forecast_lineage
  contradictory_assessment
  other

severity:
  low
  medium
  high
  critical

target_refs:
  []

description:

suggested_action:

created_at:

status:
  open
  resolved
  ignored

resolved_by:
```

这样低成本模型可以大量工作，把真正困难的问题送到GPT-6 Astra或人工。

------

# 33. 一个完整的小例子

新闻事实：

> 美联储加息25bp。

可以形成：

```yaml
event:
  id: event_fed_20260916_hike
  event_types:
    - monetary_policy

  occurred_at:
    start:
      value: 2026-09-16
      precision: day
      certainty: exact
```

对应事实Claim：

```yaml
claim:
  id: claim_fed_hike_001

  statement:
    美联储将目标利率区间上调25bp

  claim_type:
    factual

  derivation_type:
    quoted

  claimant_id:
    obs_federal_reserve
```

9527进一步说：

```yaml
claim:
  id: claim_765_014

  statement:
    此次加息可能不是一次性行为

  claim_type:
    forecast

  claimant_id:
    obs_youhegaojian9527

  temporal_mode:
    ex_ante

  knowledge_cutoff:
    2026-09-17T09:36:31+08:00
```

Forecast：

```yaml
forecast:
  claim_id:
    claim_765_014

  direction:
    occur

  target_refs:
    - fed_future_rate_hike

  resolution_status:
    open
```

Argument：

```text
点阵图显示多数官员预计继续加息
        ↓
本次加息可能不是一次性的
        ↓
高利率持续时间延长
        ↓
日本政策空间进一步受压
```

再由Edge保存：

```text
claim_dotplot
SUPPORTS
claim_765_014
```

------

# 34. Canonical Data 与 Generated Data

建议严格区分。

### Canonical

真正的知识源：

```text
Sources
Segments
Claims
Events
Indicators
Arguments
Theses
Assessments
...
```

人工和Agent都可以经过规则修改。

### Generated

由Canonical自动产生：

```text
graph/nodes.jsonl
graph/edges.jsonl
index.json
topic timelines
search indexes
Neo4j projection
vector index
```

Generated坏了：

> 重新生成。

Canonical坏了：

> 才是真的数据事故。

------

# 35. V0.1暂时不解决的问题

以下内容明确留到V0.2以后：

```text
重要性具体权重
预测评分体系
矛盾主次自动识别算法
Heuristic升级阈值
Knowledge Graph数据库选型
向量数据库选型
自动新闻抓取策略
自动新闻可信度评级
自动交易/投资建议
```

V0.1首先确保：

> 数据不会乱。

------

# 36. V0.1冻结范围

建议冻结以下内容：

### 核心对象

```text
Source
Claim
Event
Actor
Indicator
Policy
Mechanism
Argument
Thesis
Forecast
Contradiction
Assessment
Heuristic
```

### 辅助对象

```text
SourceVersion
SourceSegment
TranscriptCorrection
IndicatorObservation
InformationSet
Edge
ReviewQueue
```

### 三个核心原则

```text
证据可追溯

评价 = Observer + Time + Scope

历史不可覆盖
```

------

# 37. Schema V0.1通过标准

这版Schema不是看“设计得漂不漂亮”。

真正通过标准应该是：

选10个类型明显不同的9527视频。

每个视频完整跑：

```text
Source
↓
Segments
↓
Claims
↓
Events / Indicators
↓
Assessments
↓
Arguments
↓
Mechanisms
↓
Theses
↓
Forecasts
↓
Candidate Heuristics
```

然后检查：

### A. 是否有内容无法合理装入现有对象？

如果大量出现：

> “这个不知道该放哪里。”

Ontology可能有问题。

### B. 是否同一种内容经常可以放两个地方？

例如：

> Claim还是Thesis？

说明边界不够清楚。

### C. 是否存在大量字段永远为空？

说明Schema过度设计。

### D. 是否经常出现缺字段？

说明Schema不完整。

### E. 不同模型处理同一视频是否产生完全不同结构？

说明Extraction Spec还需要加强。

------

# 38. 下一阶段

Schema V0.1之后，不建议立刻做完整产品。

下一份真正关键的规范应该是：

# 《MacroMind Extraction Spec V0.1》

也就是正式告诉Hermes / GPT-5.5 / GPT-6 Astra / Codex：

> **拿到一条视频、字幕和6篇新闻以后，到底应该按照什么顺序，把这些Schema填出来。**

例如会明确规定：

```text
先做Source注册
→
再做Transcript Normalization
→
再拆Claim
→
再查事实
→
再做Narrative Deconstruction
→
再抽Argument
→
再匹配已有Thesis
→
最后才能提出Candidate Heuristic
```

这样Schema负责：

> **装什么。**

Extraction Spec负责：

> **怎么装。**

两者完成以后，Codex才真正有足够稳定的输入开始实现MacroMind V0.1。