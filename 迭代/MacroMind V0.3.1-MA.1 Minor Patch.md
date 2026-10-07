# MacroMind V0.3.1-MA.1 Minor Patch

**Version:** `0.3.1-MA.1-draft`
**Based on:** Golden Sample #001–#004
**Nature:** Minor Schema / Method-Mining Patch
**Core Ontology Change:** None
**Pipeline Change:** None

------

# 0. Patch定位

MA.1只解决Golden #004暴露出的四个问题：

```text
1. Method recurrence不能只有“重复/未重复”
2. Failure Pattern必须区分“谁推理”与“谁判定其存在缺陷”
3. IndicatorObservation需要统一的comparison_basis
4. 企业/产业分析中必须防止合同、收入、资产、产能、成本等Semantic Role偷换
```

不增加新的核心Ontology对象。

14个核心对象维持不变：

```text
Source
Claim
Event
StructuralProcess
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

------

# Part A — Method Recurrence升级

## A1. 问题

V0.3.1-MA已有：

```text
first_observation
repeated
frequent
candidate_pattern
```

但“repeated”过粗。

例如：

Golden #003：

```text
分阶段比较各方持续成本与承受能力
```

Golden #004：

```text
比较设备使用周期与投资回报周期
```

二者存在共同的：

```text
cost / duration constraint
```

但并不是同一条完整方法。

不能简单写：

```text
repeated = true
```

------

# A2. 新增 recurrence_match

AnalystMethodSignal增加：

```yaml
recurrence_match:
  none
  exact
  partial
  analogous
  uncertain
```

解释：

### exact

核心分析动作、适用条件和变量结构高度一致。

### partial

只复现原方法的一部分。

### analogous

操作结构相似，但变量或机制不同。

### uncertain

可能相关，但证据不足。

------

# A3. 新增 matched_scope

```yaml
matched_prior_signal_refs:
  []

matched_scope:
  string | null

recurrence_evidence:
  []
```

例如：

```yaml
recurrence_match:
  partial

matched_scope:
  "仅复现成本—时间约束子模式，不包含冲突阶段划分"
```

------

# A4. 禁止抽象过度

如果两条方法都可以被一句极其宽泛的话概括：

> “他喜欢看底层逻辑。”

这不构成有效recurrence。

复现必须指向：

```text
具体分析动作
具体变量
具体判断操作
```

------

# Part B — Failure Signal Provenance

## B1. 问题

例如：

```text
9527：
用90天 / 1天推出“90倍泡沫”
```

这是9527的推理行为。

但是：

> “这是量纲错误/估值推理缺陷”

是GPT-6或人工Reviewer的Assessment。

两者不能混成：

```text
9527 failure pattern
```

------

# B2. Failure Pattern拆成两层

### Observed Reasoning Behavior

```text
reasoner_id:
  analyst_youhegaojian9527
```

### Failure Assessment

```text
annotation_observer:
  model_gpt6
```

或者：

```text
human_reviewer
macromind
```

------

# B3. Failure Signal Schema

```yaml
signal_id:

signal_type:
  failure_pattern

observed_reasoner_id:

analysis_context:
  historical_reconstruction

annotation_observer:

observed_action:

failure_assessment:

failure_type:
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

source_segment_refs:
  []

argument_refs:
  []

claim_refs:
  []

expression_level:
  explicit
  strongly_implied

assessment_confidence:

recurrence_match:

matched_prior_signal_refs:
  []

matched_scope:

promotion_status:
  observed_candidate_only
```

------

# B4. Failure Pattern不是事实

禁止：

```text
Model认为这个推理不好
→ 9527具有稳定失败模式
```

必须先：

```text
single failure signal
↓
cross-case recurrence
↓
counterexample check
↓
review
↓
candidate failure pattern
```

------

# Part C — IndicatorObservation Comparison Basis

## C1. 问题

以下不能都简单记录成：

```text
measurement_type = rate
```

因为含义完全不同：

```text
同比增长43%

比预期高4%

提高3个百分点

环比下降5%

市场份额增加2个百分点

实际值比Consensus高20亿美元
```

------

# C2. 新增 comparison_basis

```yaml
comparison_basis:

  comparison_type:
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

  baseline_value:
    null

  baseline_period:
    null

  baseline_source_ref:
    null

  delta_value:
    null

  delta_unit:
    null
```

------

# C3. Percent与Percentage Point严格分开

例如：

```text
40% → 43%
```

是：

```yaml
delta_value: 3
delta_unit: percentage_points
```

不是：

```text
增长3%
```

------

# C4. “超预期”必须保存预期对象

例如：

```text
实际422亿美元
Consensus 406亿美元
```

保存：

```yaml
comparison_type:
  versus_consensus

actual:
  422

baseline_value:
  406
```

不得把：

```text
超预期约4%
```

误认为：

> 同比增长4%。

------

# Part D — Semantic Role / Recognition Stage

## D1. 问题

企业与产业分析中经常出现：

```text
订单
合同
RPO
收入
CapEx
服务器
产能
资产
折旧
费用
现金流
利润
```

它们之间相关，但不是同一个对象。

尤其禁止：

```text
订单余额
→ 硬件资产
→ 冗余成本
```

不经过中间证明。

------

# D2. Indicator / Claim增加semantic_role

通用枚举：

```yaml
semantic_role:
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
```

------

# D3. 增加 recognition_stage

```yaml
recognition_stage:
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
```

------

# D4. Object Role Shift必须显式建Argument Edge

如果主播推理：

```text
RPO↑
→ 必须建设更多服务器
→ 服务器可能未来闲置
→ 折旧压力↑
```

不能把它压成一个Claim。

必须至少拆为：

```text
contract/backlog
↓
capacity requirement
↓
asset deployment
↓
future utilization
↓
depreciation/cost
```

每一跳单独接受验证。

------

# D5. Role Shift本身不是错误

例如：

```text
订单增加
→ 收入增加
```

可能完全合理。

MA.1只是要求：

> 不允许静默跨层。

------

# Part E — AnalystMethodSignal Schema更新

更新后：

```yaml
AnalystMethodSignal:

signal_id:

analyst_id:

signal_type:

statement:

source_segment_refs:
  []

argument_refs:
  []

claim_refs:
  []

expression_level:
  explicit
  strongly_implied

domain:

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

recurrence_match:
  none
  exact
  partial
  analogous
  uncertain

matched_prior_signal_refs:
  []

matched_scope:

annotation_observer:

confidence:

why_this_is_method_not_conclusion:

limitations:

promotion_status:
```

------

# Part F — Validation Rules

新增：

### R056 — Method Recurrence Specificity

任何：

```text
repeated / frequent
```

必须同时说明：

```text
recurrence_match
matched_scope
```

------

### R057 — No Vague Recurrence

仅有抽象共同描述，例如：

```text
“都关注底层逻辑”
```

不能判exact/partial recurrence。

------

### R058 — Failure Observer Separation

任何Failure Signal必须同时保存：

```text
observed_reasoner_id
annotation_observer
```

------

### R059 — Failure ≠ Stable Pattern

单次Failure Signal不得自动升级：

```text
Analyst Failure Pattern
```

------

### R060 — Comparison Basis Required

涉及：

```text
同比
环比
超预期
百分点变化
基准差
```

的Observation必须尽量记录：

```text
comparison_basis
```

------

### R061 — Percent / Percentage Point Integrity

`percent`和`percentage_points`不得互换。

------

### R062 — Semantic Role Integrity

涉及企业经营链条时：

```text
order
contract
revenue
capacity
asset
expense
profit
```

必须保持角色区分。

------

### R063 — Role Shift Edge

跨semantic_role进行推理时：

必须显式建立Argument Edge或进入Review Queue。

------

# Part G — Golden #004轻量迁移

不重跑。

只需要：

### MS01—MS08

补：

```text
recurrence_match
matched_scope
```

------

### MS06

补：

```text
observed_reasoner_id:
  analyst_youhegaojian9527

annotation_observer:
  model_gpt6

failure_type:
  dimensional_error
```

------

### 云业务Observation

补充适用的：

```text
comparison_basis
semantic_role
recognition_stage
```

尤其：

```text
Azure增长
AWS超预期
RPO
CapEx
折旧
```

------

# Part H — 不修改的内容

MA.1不修改：

```text
StructuralProcess定义
Scenario / Forecast边界
SourceVersion
SourceFamily
ClaimOccurrence
MechanismUsage
Reasoner Attribution
Truth Non-Propagation
Analyst / MacroMind隔离
```

这些已经通过#004初步验证。

------

# Part I — 当前稳定状态

截至Golden #004：

```text
Core Ontology:
Freeze Candidate

MA Layer:
Stable Candidate

Scenario / Forecast:
Stable Candidate

MethodSignal:
Validated enough for continued testing
```

但：

```text
9527 Skill:
NOT READY

MacroMind Core Skill:
NOT READY
```

------

# MA.1最终原则

方法复现必须回答：

> 到底重复了哪一步？

失败模式必须回答：

> 谁做了这个推理，谁判断它有问题？

数字比较必须回答：

> 和什么比较？

企业对象转换必须回答：

> 这是订单、收入、资产、成本还是利润？

只要这四个问题保持清楚，

MA层就不会因为样本越来越多而逐渐混乱。