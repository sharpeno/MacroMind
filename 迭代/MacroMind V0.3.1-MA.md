# MacroMind V0.3.1-MA

## Multi-Analyst Architecture Patch

**Version:** `0.3.1-MA-draft`
**Based on:** MacroMind V0.3.1 + Golden Sample #001–#003 + Final Product Goal Clarification
**Nature:** Architecture Extension
**Core Ontology Change:** None

------

# 0. 最终目标确认

MacroMind最终定义为：

> **MacroMind 是一个基于长期证据库、时间化知识图谱和多分析师 Skill 的可审计宏观分析系统。系统通过大量历史语料重建不同分析者的分析方法，将其沉淀为可独立调用的 Analyst Skill；面对新事件时，可以调用单一分析师框架，也可以让多个分析框架基于同一事实底座进行独立分析、比较和综合。**

当前第一位重点研究对象：

```text
Analyst:
有何高见9527
```

目标之一仍然明确是：

```text
1900期历史语料
↓
9527 Analyst Model
↓
9527 Analyst Skill
↓
可独立调用
↓
使用他的分析方法处理新的事实和问题
```

MacroMind不是替代9527 Skill。

MacroMind负责：

```text
共享证据
共享现实知识
时间完整性
验证
检索
多分析师管理
跨Skill比较
最终综合
```

9527 Skill负责：

```text
用9527长期形成的分析程序处理问题
```

------

# Part A — Architecture Boundary

# A1. 三层正式分离

MacroMind从V0.3.1-MA开始正式区分：

```text
Layer 1
Shared Reality / Knowledge

Layer 2
Analyst Models / Analyst Skills

Layer 3
MacroMind Synthesis
```

完整结构：

```text
                   MacroMind
                       │
       ┌───────────────┴────────────────┐
       │                                │
 Shared Evidence / Knowledge       Analyst Layer
       │                                │
 Source                           9527 Analyst Model
 Claim                            Analyst B Model
 Event                            Analyst C Model
 StructuralProcess                     │
 Indicator                             ↓
 Policy                          Analyst Skills
       │                                │
       └──────────────┬─────────────────┘
                      ↓
             MacroMind Synthesis
```

------

# A2. Shared Knowledge不属于任何分析师

以下对象原则上是公共层：

```text
Source
SourceVersion
SourceEntry
SourceFamily
SourceSegment

Actor
Event
StructuralProcess
Indicator
IndicatorObservation
Policy

Canonical factual Claims
```

它们不因为：

```text
9527
分析师B
分析师C
MacroMind
```

而复制多份。

------

# A3. 分析师之间共享Reality，不共享判断

例如：

```text
Reality:
霍尔木兹海峡实际通行量下降20%
```

所有Analyst Skill读取同一个Observation。

但：

```text
9527:
重点解释为控制权和战争持续能力

能源Analyst:
重点解释为桶/日、库存和保险

宏观Analyst:
重点解释为通胀和利率
```

这些进入各自Analyst Layer。

------

# Part B — 新增辅助对象 AnalystModel

# B1. AnalystModel定义

AnalystModel：

> 对一个真实分析者历史分析行为的结构化描述。

它不是：

```text
Actor
```

的替代品。

Actor表示现实中的人。

AnalystModel表示：

> 这个人作为分析者表现出的可复用认知和推理模式。

------

# B2. AnalystModel Schema

```yaml
id:
object_type: analyst_model

analyst_id:
actor_ref:

display_name:

status:
  collecting
  building
  provisional
  benchmarked
  skill_candidate
  skill_published
  archived

corpus_scope:
  source_count:
  time_start:
  time_end:
  domains: []

method_assets:
  attention_patterns: []
  question_patterns: []
  mechanism_usage_refs: []
  heuristic_refs: []
  branching_patterns: []
  judgment_patterns: []
  failure_pattern_refs: []

skill_ref:
  null

skill_version:
  null

evidence_coverage:
  golden_samples:
  analyzed_sources:
  reviewed_sources:

provenance:
```

------

# B3. 9527初始对象

建议：

```yaml
analyst_id:
  analyst_youhegaojian9527

actor_ref:
  actor_youhegaojian9527

status:
  building
```

------

# Part C — Reasoner Attribution

# C1. 所有Reasoning对象必须知道“是谁的推理”

V0.3.1以后，重要Reasoning对象增加：

```yaml
reasoner_id:

analysis_context:
```

适用：

```text
Argument
Thesis
Forecast
Assessment
Heuristic Candidate
Scenario
```

------

# C2. reasoner_id允许值

例如：

```text
analyst_youhegaojian9527
analyst_xxx

macromind
model_gpt6
human_reviewer
```

------

# C3. analysis_context

正式使用：

```text
historical_reconstruction
current_application
analyst_simulation
macromind_synthesis
model_diagnostic
```

------

# C4. 五种Context含义

## historical_reconstruction

回答：

> 历史材料中，这位分析师当时实际上是怎样推理的？

Golden Sample默认属于这里。

------

## current_application

回答：

> 当前正式调用某Analyst Skill分析一个新事件。

例如：

```text
Use 9527 Skill
→ analyze current Fed decision
```

------

## analyst_simulation

回答：

> 模型推测这位分析师可能会如何想。

这不是历史事实。

默认不进入Analyst Skill学习数据。

------

## macromind_synthesis

MacroMind综合多个Analyst Skill后的独立分析。

------

## model_diagnostic

模型为了检查某Argument逻辑是否完整而补出的桥接推理。

例如：

```text
model_bridge
```

属于这里。

------

# Part D — 严禁把Model Reconstruction污染Analyst Model

# D1. 核心规则

以下内容：

```text
expression_level = model_reconstruction
```

不得直接成为：

```text
9527 Attention Pattern
9527 Heuristic
9527 Question Policy
9527 Judgment Policy
```

------

# D2. Analyst Skill Promotion只接受

默认只允许：

```text
explicit
strongly_implied
```

进入Analyst Method Mining。

------

# D3. model_reconstruction作用

它只用于：

```text
审计逻辑
暴露缺失前提
计算推理距离
设计验证任务
发现可能的失败模式
```

而不是：

> “替9527把逻辑补漂亮以后，再说这是9527的方法。”

------

# Part E — Mechanism与MechanismUsage正式分离

# E1. Mechanism是共享知识

例如：

```text
战争风险↑
→ 保险成本↑
→ 船东通行意愿↓
→ 运力↓
→ 交付成本↑
```

这可以是：

```text
Canonical Mechanism
```

不需要复制：

```text
9527机制
能源专家机制
MacroMind机制
```

------

# E2. 新增辅助对象 MechanismUsage

```yaml
id:
object_type: mechanism_usage

mechanism_ref:

analyst_id:

usage_context:
  historical_reconstruction
  current_application

expression_level:
  explicit
  strongly_implied
  partial

source_refs:
  []

argument_refs:
  []

first_observed_at:

observed_count:

domain_scope:
  []

confidence:

provenance:
```

------

# E3. 这样未来可以回答

```text
哪些Mechanism是9527高频使用？

哪些Mechanism多个分析师共同使用？

哪些Mechanism只出现在能源领域？

哪些Mechanism历史预测效果较差？
```

------

# Part F — Heuristic Attribution V0.3.1-MA

# F1. Heuristic必须明确来源

增加：

```yaml
origin_analyst_id:
```

例如：

```yaml
origin_analyst_id:
  analyst_youhegaojian9527
```

------

# F2. 新增 method_scope

```yaml
method_scope:
  analyst_specific
  domain_specific
  cross_domain_candidate
  potentially_general
```

------

# F3. 新增 transfer_status

用于描述这条方法与MacroMind Core Skill的关系：

```yaml
transfer_status:
  analyst_only
  candidate_for_macromind
  adapted_for_macromind
  promoted_to_macromind
  rejected_for_macromind
```

------

# F4. 新增 macromind_transformation

```yaml
macromind_transformation:

  status:
    none
    inherited
    adapted
    rejected

  original_rule:

  transformed_rule:

  change_reason:

  validation_refs:
    []

  counterexample_refs:
    []
```

------

# F5. 示例

9527历史方法：

```text
强硬声明可能说明对方实际上心虚。
```

可能记录：

```yaml
origin_analyst:
  9527

transfer_status:
  adapted_for_macromind
```

MacroMind版本：

```text
强硬声明不能直接证明实际能力；
应比较公开表态、真实行动、资源和持续执行能力。
```

MacroMind版本不能覆盖9527原始Heuristic。

两者同时存在。

------

# Part G — AnalystMethodSignal

# G1. 新增辅助对象

```
AnalystMethodSignal
```

定义：

> 在某一具体历史分析中，出现的一次潜在分析方法行为。

它不是Heuristic。

它是：

> Heuristic形成以前的原始观察。

------

# G2. 为什么需要

不能看到一次：

```text
“增量看趋势，存量看空间”
```

马上建立稳定Skill规则。

应该：

```text
MethodSignal
↓
Repeated MethodSignal
↓
Candidate Pattern
↓
Heuristic
↓
Validated Analyst Skill Rule
```

------

# G3. AnalystMethodSignal Schema

```yaml
id:
object_type: analyst_method_signal

analyst_id:

signal_type:
  attention_pattern
  question_pattern
  mechanism_usage
  branching_pattern
  judgment_pattern
  evidence_preference
  analogy_pattern
  falsification_pattern
  failure_pattern

statement:

source_segment_refs:
  []

argument_refs:
  []

claim_refs:
  []

domain:

expression_level:
  explicit
  strongly_implied

transferability:
  unknown
  analyst_specific
  domain_specific
  potentially_general

recurrence_status:
  first_observation
  repeated
  frequent
  candidate_pattern

confidence:

provenance:
```

------

# Part H — 七类Analyst Method资产

成熟AnalystModel最终主要沉淀以下七类资产。

------

# H1. Attention Policy

回答：

> 这个分析师面对复杂信息时首先关注什么？

例如9527候选：

```text
控制权
时间窗口
执行能力
成本承受能力
资金流
利益分配
增量/存量
```

------

# H2. Question Policy

回答：

> 他经常继续追问什么？

例如：

```text
谁真正受益？

谁承担成本？

能持续多久？

谁拥有真正执行能力？

公开解释遗漏了什么？

这个结果是原因还是结果？

如果事情继续发展，下一约束在哪里？
```

------

# H3. Mechanism Library Usage

回答：

> 他经常调用哪些可复用机制？

------

# H4. Heuristic Library

回答：

> 他反复使用哪些判断规则？

------

# H5. Branching Policy

回答：

> 面对未来不确定性，他怎样划分IF-THEN？

例如：

```text
第一周
一个月
40天
60天
```

属于一种时间分支模式。

------

# H6. Judgment Policy

回答：

> 在什么条件下，他从：

Hypothesis

升级为：

Assert / Forecast / Strong Judgment？

这个资产尤其重要。

------

# H7. Failure Patterns

回答：

> 他经常在哪里推得过远？

例如可能包括：

```text
动机归因过强
历史类比迁移过强
物理约束升级为政治必然
把数量变化当价格变化
把局部事件升级为长期结构结论
```

Failure Pattern也必须来自案例统计，不能凭印象生成。

------

# Part I — 9527 Skill正式定义

# I1. 9527 Skill不是观点数据库

禁止定义为：

```text
“美国会衰落”
“美元会下跌”
“油价会涨”
```

这类只是历史观点或Thesis。

------

# I2. 9527 Skill定义

> 9527 Skill 是依据大量历史材料重建出的、可复用的9527分析程序。

包含：

```text
Attention Policy
Question Policy
Mechanism Usage
Heuristics
Branching Policy
Judgment Policy
Failure Awareness
Retrieval Policy
```

------

# I3. Skill运行目标

给定：

```text
新事实 / 新新闻 / 新问题
```

9527 Skill应该：

```text
使用9527历史方法
↓
确定关注变量
↓
提出追问
↓
调用Mechanism
↓
形成IF-THEN
↓
在证据允许时形成判断
```

而不是：

```text
根据历史立场猜主播今天会说什么
```

------

# Part J — Analyst Skill输出模式

建议所有Analyst Skill执行时默认使用四种输出语义：

```text
ASSERT
IF_THEN
HYPOTHESIS
ANALYST_SIMULATION
```

------

# J1. ASSERT

当前证据支持。

------

# J2. IF_THEN

机制存在，但结果依赖条件。

------

# J3. HYPOTHESIS

值得验证，但证据不足。

------

# J4. ANALYST_SIMULATION

只有用户明确要求：

> “你觉得9527会怎么看？”

才允许开启。

必须明确：

```text
这不是9527已发表观点，
而是基于历史Analyst Model的模拟。
```

------

# Part K — 9527 Skill Promotion Pipeline

正式定义：

```text
Historical Sources
↓
Claims
↓
Arguments
↓
Mechanism Usage
↓
AnalystMethodSignals
↓
Repeated Signals
↓
Candidate Patterns
↓
Candidate Heuristics
↓
Counterexample Search
↓
Failure Analysis
↓
Human Review
↓
9527 Analyst Model
↓
9527 Skill
```

------

# K1. 禁止直接Promotion

禁止：

```text
一次Golden Sample
↓
Skill Rule
```

------

# K2. Candidate Pattern最低要求

暂定：

```text
至少跨多个不同事件出现
```

具体次数暂不写死。

30–50期以后根据实际分布确定。

------

# Part L — MacroMind Core Skill Promotion Pipeline

MacroMind Core Skill与9527 Skill必须完全分开建设。

正式Pipeline：

```text
9527 Analyst Skill
Analyst B Skill
Analyst C Skill
       ↓
Cross-Analyst Comparison
       ↓
Historical Validation
       ↓
Counterexamples
       ↓
Failure Analysis
       ↓
Method Adjudication
       ↓
Inherited / Adapted / Rejected
       ↓
MacroMind Core Analyst Skill
```

------

# L1. MacroMind不是“平均多个专家”

禁止：

```text
Analyst A认为X
Analyst B认为Y
→ MacroMind取中间值
```

MacroMind应该比较：

```text
使用了什么证据？
调用了什么机制？
哪一步推理不同？
哪套方法在哪类历史案例表现更好？
```

------

# L2. MacroMind Skill未来性质

可以描述为：

```text
Evidence-constrained Analytical Policy
```

即：

> 基于多分析师历史方法和跨案例验证形成的、证据约束的分析政策。

------

# Part M — Multiple Analyst Comparison

未来同一个Context Manifest可以：

```text
                Shared Evidence Pack
                        │
          ┌─────────────┼─────────────┐
          │             │             │
       9527 Skill   Analyst B     Analyst C
          │             │             │
          └─────────────┼─────────────┘
                        ↓
                Disagreement Map
                        ↓
                MacroMind Synthesis
```

------

# M1. Disagreement不是只比较最终结论

应该比较：

```text
Attention差异

Evidence差异

Mechanism差异

Assumption差异

Scenario差异

Argument差异

最终Judgment差异
```

------

# Part N — Golden Sample输出新增Section

从Golden #004开始，在现有Extraction输出中新增：

# ANALYST METHOD SIGNALS

只记录强证据。

输出：

```text
Attention Patterns
Question Patterns
Mechanism Usage
Branching Patterns
Judgment Patterns
Failure Patterns
```

没有就写：

```text
none
```

------

# N1. 禁止为了完整强行生成

一条视频不一定能够观察到：

```text
Judgment Policy
Failure Pattern
```

允许为空。

------

# N2. Method Signal与Heuristic关系

```text
AnalystMethodSignal
≠
Heuristic
```

Method Signal：

> 一次观察。

Heuristic：

> 多案例反复出现以后抽象出来的方法规则。

------

# Part O — Golden Sample新增最终问题

从#004开始，Golden Prompt最后增加：

### I.

本期出现了哪些Analyst Method Signals？

分别按：

```text
Attention
Question
Mechanism Usage
Branching
Judgment
Failure
```

输出。

### J.

其中哪些可能：

```text
analyst_specific
domain_specific
potentially_general
```

### K.

哪些Method Signal来自9527明确表达？

哪些只是strongly implied？

严禁把model reconstruction作为9527 Method Signal。

------

# Part P — Existing Golden #001–#003 Migration

不重跑。

执行一次轻量Migration即可。

------

# P1. Arguments

已有主播推理：

```yaml
reasoner_id:
  analyst_youhegaojian9527

analysis_context:
  historical_reconstruction
```

------

# P2. Model Bridges

已有：

```text
model_reconstruction
```

增加：

```yaml
reasoner_id:
  model

analysis_context:
  model_diagnostic
```

------

# P3. Heuristics

已有Candidate Heuristic：

```yaml
origin_analyst_id:
  analyst_youhegaojian9527

transfer_status:
  analyst_only
```

或：

```text
candidate_for_macromind
```

但暂不正式promote。

------

# P4. Mechanisms

Canonical Mechanism保持共享。

增加相应：

```text
MechanismUsage
```

指向9527。

------

# P5. Method Signals

允许基于已审查Argument回填少量高置信Signal。

禁止重新“脑补”整个#001—#003。

------

# Part Q — 推荐目录结构更新

```text
macro-mind-knowledge/
│
├── evidence/
├── knowledge/
├── reasoning/
├── framework/
│
├── analysts/
│   │
│   ├── registry.yaml
│   │
│   └── youhegaojian9527/
│       ├── profile.yaml
│       ├── method_signals/
│       ├── attention_patterns/
│       ├── question_patterns/
│       ├── mechanism_usage/
│       ├── heuristics/
│       ├── branching_patterns/
│       ├── judgment_patterns/
│       ├── failure_patterns/
│       └── skill/
│
├── macromind/
│   ├── core_skill/
│   ├── promoted_heuristics/
│   ├── adapted_heuristics/
│   ├── rejected_heuristics/
│   └── synthesis/
│
└── evaluation/
```

------

# Part R — Skill文件结构候选

未来9527成熟Skill：

```text
analysts/youhegaojian9527/skill/

├── skill.md
├── attention_policy.yaml
├── question_policy.yaml
├── mechanism_policy.yaml
├── heuristics.yaml
├── branching_policy.yaml
├── judgment_policy.yaml
├── failure_modes.yaml
└── retrieval_policy.yaml
```

------

# Part S — Validation Rules新增

### R046 — Reasoner Attribution

重要Reasoning Object必须拥有：

```text
reasoner_id
analysis_context
```

------

### R047 — Model Reconstruction Isolation

`model_reconstruction`不得直接进入Analyst Method资产。

------

### R048 — Analyst Method Provenance

任何AnalystMethodSignal必须具有：

```text
analyst_id
source evidence
expression_level
```

------

### R049 — Heuristic Analyst Attribution

任何Analyst Heuristic必须具有：

```text
origin_analyst_id
```

------

### R050 — Canonical Mechanism Dedup

同一现实机制不得因为不同Analyst使用而复制Canonical Mechanism。

应使用MechanismUsage。

------

### R051 — Analyst / MacroMind Separation

Analyst Heuristic不得自动进入MacroMind Core Skill。

------

### R052 — Transfer Status

进入MacroMind候选池的方法必须明确：

```text
transfer_status
```

------

### R053 — Simulation Isolation

`analyst_simulation`输出不得作为：

```text
historical analyst evidence
```

进入AnalystModel。

------

### R054 — Skill Rule Evidence

正式Analyst Skill Rule不能仅由单一Golden Sample支持。

------

### R055 — Failure Pattern Evidence

Failure Pattern必须由实际错误、薄弱Argument或反例支持。

不得因为模型不同意Analyst观点就创建Failure Pattern。

------

# Part T — Heuristic生命周期更新

新生命周期：

```text
MethodSignal
↓
RepeatedSignal
↓
CandidatePattern
↓
CandidateHeuristic
↓
ReviewedHeuristic
↓
AnalystValidatedHeuristic
↓
        ┌───────────────┐
        │               │
Analyst Skill      MacroMind Evaluation
                        │
             ┌──────────┼──────────┐
             │          │          │
          Inherit      Adapt      Reject
```

------

# Part U — 9527 Skill与MacroMind Skill的根本区别

## 9527 Skill

目标：

```text
忠实重建9527的分析程序
```

即使发现：

> 某些方法有系统性缺陷，

仍应保存于9527 Skill及Failure Modes。

------

## MacroMind Core Skill

目标：

```text
尽可能形成更加可靠、可审计、
可跨案例验证的宏观分析程序。
```

它可以：

```text
继承9527

修改9527

拒绝9527

吸收其他Analyst
```

------

# Part V — 不能发生的错误

禁止：

```text
9527说过X
→ MacroMind认为X
```

禁止：

```text
模型为了补完整Argument写了Y
→ 9527 Skill学会Y
```

禁止：

```text
多个Analyst都相信Z
→ Z就是事实
```

禁止：

```text
Analyst历史预测正确
→ 其所有Heuristic自动Validated
```

禁止：

```text
MacroMind修改9527规则
→ 回写并覆盖9527原始规则
```

------

# Part W — 新事件调用模式

未来支持三种正式模式。

## Mode 1 — Analyst Mode

```text
使用9527 Skill分析这个问题
```

只调用指定Analyst Skill。

------

## Mode 2 — Multi-Analyst Mode

```text
分别使用9527、
Analyst B、
Analyst C分析
```

各自独立运行。

然后输出Disagreement Map。

------

## Mode 3 — MacroMind Mode

系统：

```text
识别问题领域
↓
选择相关Analyst Skills
↓
创建共享Evidence Pack
↓
独立运行
↓
比较Arguments
↓
验证关键分歧
↓
MacroMind Synthesis
```

------

# Part X — Analyst Skill不拥有自己的Reality数据库

这是硬性架构原则。

禁止：

```text
9527 Knowledge DB

Analyst B Knowledge DB

Analyst C Knowledge DB
```

正确：

```text
One Shared Evidence / Knowledge Base
          │
          ├── 9527 Skill
          ├── Analyst B Skill
          └── Analyst C Skill
```

分析师之间不同的是：

```text
关注
提问
机制调用
推理
判断
```

不是：

> 基础事实世界。

------

# Part Y — Method Evaluation未来需要的指标

当前不实现评分公式。

先预留：

```text
recurrence_count

cross_domain_recurrence

success_cases

failure_cases

counterexamples

evidence_quality

inferential_distance

calibration

applicability_scope
```

30–50期以后再设计正式Heuristic Evaluation。

------

# Part Z — 当前项目路线

正式调整为：

```text
V0.3.1
↓
V0.3.1-MA
↓
Golden #004
↓
Golden #005
↓
Core Ontology Freeze Candidate
↓
Codex Phase 1
↓
30–50期9527 Corpus
↓
Analyst Method Mining
↓
9527 Analyst Model V0.1
↓
9527 Skill V0.1
↓
更多9527语料
↓
第二个Analyst Model / Skill
↓
Multi-Analyst Comparison
↓
MacroMind Core Skill V0.1
```

------

# Final Architecture Formula

## MacroMind

```text
MacroMind =
Shared Evidence
+ Temporal Knowledge
+ Auditable Reasoning
+ Analyst Models
+ Analyst Skills
+ Cross-Analyst Evaluation
+ Synthesis
```

------

## Analyst Model

```text
Analyst Model =
Observed Historical Reasoning Behavior
+ Method Signals
+ Repeated Patterns
+ Failure Patterns
```

------

## Analyst Skill

```text
Analyst Skill =
Attention Policy
+ Question Policy
+ Mechanism Usage
+ Heuristics
+ Branching Policy
+ Judgment Policy
+ Failure Awareness
```

------

## MacroMind Core Skill

```text
MacroMind Core Skill =
Validated Analyst Methods
+ Adapted Methods
+ Cross-Analyst Evidence
+ Counterexamples
+ MacroMind Judgment Policy
```

------

# 最终原则

MacroMind不是为了回答：

> “9527会说什么？”

首先要做到：

> “9527是怎样分析问题的？”

然后做到：

> “能否按照他的分析程序处理一个新问题？”

再进一步做到：

> “哪些分析师在同一个问题上使用了不同方法？”

最后才做到：

> “经过证据和历史案例验证，MacroMind自己应该采用哪些分析方法？”

因此：

```text
9527 Skill
```

仍然是一个完整产品。

而：

```text
MacroMind
```

是能够容纳9527 Skill以及未来多个Analyst Skill的更高层分析系统。

两者不是替代关系。

而是：

```text
9527 Skill
      ↓
one Analyst Mind
      ↓
MacroMind
      ↓
many Analyst Minds
+ one shared reality
+ auditable synthesis
```