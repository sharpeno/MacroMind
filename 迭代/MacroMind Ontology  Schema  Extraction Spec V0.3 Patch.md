# MacroMind Ontology / Schema / Extraction Spec V0.3 Patch

**Version:** `0.3-draft`
**Based on:** Golden Sample #001 + Golden Sample #002 + Human Adjudication
**Nature:** Incremental Patch, not full redesign

------

# 0. V0.3目标

V0.1解决：

> 有哪些知识对象？

V0.2重点解决：

> 谁在什么时候、针对哪个时期、对哪一群人说了什么？

V0.3进一步解决：

> **现实中的长期变化是什么？一个数字究竟是什么口径？多个Source到底是不是独立证据？一条观点到底是谁说的、谁转述的？复杂推理究竟跨了多远？**

V0.3核心原则：

```text
不扩张没有必要的Ontology
只吸收跨题材已经被Golden Sample验证的缺口
```

------

# Part I — Ontology V0.3

# 1. 新增核心对象：StructuralProcess

V0.3将核心对象从13个增加为14个：

```text
Source
Claim
Event
StructuralProcess   ← NEW
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

# 2. StructuralProcess定义

StructuralProcess：

> 在一段时间内持续发生、能够通过多个Observation/Event观察到的现实结构变化。

例如：

```text
中国融资结构多元化
人口老龄化
房地产去杠杆
能源转型
产业升级
银行脱媒
人民币国际化
AI资本开支扩张
全球供应链重构
```

这些通常不是一个离散Event。

------

# 3. StructuralProcess与其他对象边界

## Event

回答：

> 某件事什么时候发生？

例如：

```text
美联储2026-09-16加息25bp
```

------

## StructuralProcess

回答：

> 某个结构在一段时期内怎样持续变化？

例如：

```text
中国银行贷款在融资结构中的相对占比长期下降，
直接融资渠道逐渐扩大。
```

------

## Thesis

回答：

> 分析者如何解释这个StructuralProcess，以及认为它将造成什么结果？

例如：

```text
融资结构多元化最终将迫使银行改变盈利模式。
```

这是Thesis，不是StructuralProcess本身。

------

## Mechanism

回答：

> 为什么这种变化可能产生某种结果？

例如：

```text
早期企业现金流不稳定
→ 固定偿债契约适配下降
→ 股权资本相对更适合
```

------

# 4. StructuralProcess不得等同趋势结论

禁止：

```text
9527认为中国正在金融崛起
→ StructuralProcess
```

这仍可能只是Thesis。

StructuralProcess必须尽量建立在：

```text
IndicatorObservation
Event
Policy
可观察状态变化
```

上。

------

# 5. StructuralProcess状态

建议：

```text
candidate
observed
ongoing
stabilizing
reversing
completed
disputed
```

V0.3不建立复杂趋势评分公式。

------

# 6. 新增辅助对象：ClaimOccurrence

ClaimOccurrence表示：

> 同一个Canonical Claim在不同SourceSegment中的一次具体出现。

目的：

解决：

```text
主播重复三次同一个数字
主播第一次说A、后面又重复A
主播先说A、随后修正为A'
同一个官方数字在文章中被多次朗读
```

不能因此建立多个同权Claim。

结构变为：

```text
Claim
├── Occurrence #1
├── Occurrence #2
└── Occurrence #3
```

------

# 7. ClaimOccurrence不是Claim Version

如果：

> 同一命题被重复表达

使用Occurrence。

如果：

> 命题本身发生实质变化

建立新的Claim或Claim Revision。

------

# 8. 新增辅助结构：SourceFamily

Source数量：

≠

独立证据数量。

例如：

```text
央行原文
↓
财联社转载
↓
9527引用
```

可能只有一个主要信息源。

再例如：

```text
TXT
SRT
```

来自同一次ASR，也不是两份独立证据。

因此增加：

```text
SourceFamily
```

用于表示共同来源血缘。

------

# 9. SourceFamily与Source lineage

关系至少支持：

```text
DERIVED_FROM
TRANSCRIBED_FROM
MIRRORS
SYNDICATES
QUOTES
REPACKAGES
```

验证系统以后统计：

> 有多少独立证据支持Claim

应优先按独立SourceFamily统计，而不是Source文件数量。

------

# 10. Attribution Chain正式进入Ontology规则

V0.3正式区分：

```text
谁实际说出了这句话？
谁被认为是这句话原本的观点拥有者？
当前Source是谁？
原始Source是谁？
```

例如：

```text
9527视频：
“潘功胜说直接融资占比提高。”
```

可能是：

```text
asserted_by = 9527
claimant = 潘功胜
```

而：

```text
9527说：
“潘功胜其实是在给市场吃定心丸。”
```

则：

```text
asserted_by = 9527
claimant = 9527
about = 潘功胜文章
```

不得混淆。

------

# Part II — Schema V0.3

# 11. StructuralProcess Schema

```yaml
id:
object_type: structural_process

name:

process_type:
  financial_structure
  demographic
  industrial
  technological
  energy
  fiscal
  monetary
  geopolitical
  social
  trade
  institutional
  other

status:
  candidate
  observed
  ongoing
  stabilizing
  reversing
  completed
  disputed

reference_time:
  start:
  end:

geography_scope:
  []

actor_refs:
  []

indicator_refs:
  []

event_refs:
  []

policy_refs:
  []

dimensions:
  - dimension:
    direction:
      rising
      falling
      widening
      narrowing
      shifting
      diversifying
      concentrating
      unknown
    evidence_refs: []

source_refs:
  []

provenance:
  ...
```

------

# 12. StructuralProcess最小验证规则

Canonical StructuralProcess原则上至少需要：

```text
两个不同reference_time的Observation
```

或者：

```text
一个明确的时间序列Source
```

或者：

```text
多个Event / Policy变化共同支持过程存在
```

单个观点不足以证明StructuralProcess。

------

# 13. 中国金融结构案例

应该建：

```yaml
StructuralProcess:
  中国融资结构多元化

dimensions:
  - bank_intermediation_relative_share:
      direction: falling

  - direct_financing_relative_share:
      direction: rising
```

然后：

```text
TH01：
这种融资结构变化正在推动资金投向和产业结构调整
```

仍然单独作为Thesis。

Golden #002本身已经明确指出：金融结构变化首先是持续过程，而不是一个Event；其原因和结果解释才属于Thesis。

------

# 14. IndicatorObservation V0.3扩展

这是V0.3最重要的Schema更新之一。

新增：

```yaml
measurement_type:
  stock
  flow
  level
  rate
  growth_rate
  share
  ratio
  index
  count
  amount

value_status:
  observed
  reported
  calculated
  projected
  target
  estimated

value:

unit:

currency:
  string | null

numerator:
  indicator_ref | description | null

denominator:
  indicator_ref | description | null

gross_net:
  gross
  net
  unknown

period_basis:
  point_in_time
  period_total
  period_average
  year_to_date
  trailing_12m
  yoy
  qoq
  mom
  cumulative
  unknown

reference_period:

released_at:

vintage_at:
  datetime | null

revision_number:
  integer | null

classification_version:
  string | null
```

------

# 15. 为什么必须这样做

V0.3禁止仅保存：

```yaml
direct_financing:
  33%
```

必须尽量知道：

```text
33%是什么？

新增融资占比？
融资存量占比？
某一年？
截至某月？
什么分母？
是否包括政府债？
是否净融资？
```

Golden #002已经暴露出贷款、间接融资、增量和存量被跨口径换用会直接改变结论。

------

# 16. Ratio / Share强制规则

若：

```text
measurement_type = ratio/share
```

则必须尝试保存：

```text
numerator
denominator
```

无法确定时：

```yaml
numerator: null
denominator: null
```

并进入：

```text
ReviewQueue.data_definition
```

禁止猜。

------

# 17. Observed与Projected严格分离

例如：

> 平陆运河预计每年节约运输成本X亿元

不是：

```text
Observed Annual Benefit
```

而应：

```yaml
value_status:
  projected
```

社会效益、项目现金收入、利润、回本期不得自动互换。

Golden #002正是因此提出了Observation必须区分 observed / projected / calculated / reported。

------

# 18. Source Schema V0.3扩展

增加：

```yaml
source_family_id:

lineage:
  parent_source_refs: []

independence:
  independent
  derived
  same_origin
  unknown
```

------

# 19. Evidence Support不再简单计数Source

禁止：

```text
5 Sources support Claim
```

却实际上：

```text
1篇原文
+3篇转载
+1个视频引用
```

建议未来派生：

```text
independent_evidence_family_count
```

但V0.3不设硬性“几家来源才验证”的门槛。

------

# 20. Claim Attribution Schema V0.3

Claim增加：

```yaml
claimant_id:
  # 命题语义上属于谁

asserted_by_id:
  # 当前证据里实际说/写出的人

attribution_chain:
  - actor_id:
    attribution_type:
      direct
      quote
      paraphrase
      reported_speech
      inferred_attribution

original_source_ref:
  ref | null

attribution_status:
  direct
  source_verified
  reported_only
  inferred
  uncertain
```

------

# 21. Attribution验证原则

如果视频里9527说：

> “潘功胜认为X”

但没有找到潘功胜原文：

允许：

```text
asserted_by = 9527
claimant = 潘功胜
attribution_status = reported_only
```

不能因为9527说过，就把：

> 潘功胜确实认为X

标成Verified。

Golden #002明确暴露了 claimant / asserted_by / attributed_to 不能混成一个字段。

------

# 22. ClaimOccurrence Schema

```yaml
id:
object_type: claim_occurrence

claim_id:

source_segment_id:

surface_text:

occurrence_role:
  first
  repeat
  restatement
  elaboration
  summary
  self_correction
  contradiction

information_gain:
  high
  medium
  low
  redundant

local_context:
  string | null

provenance:
  ...
```

------

# 23. Claim Dedup规则

若两处表达满足：

```text
same proposition
same claimant
same reference_time
same scope
```

优先建立：

```text
同一Claim + 多个Occurrence
```

而不是重复Claim。

------

# 24. Event时间结构 V0.3

Golden #002出现：

> 日本央行已经在knowledge cutoff之前宣布政策，但政策未来才正式生效。

所以仅有：

```text
occurred_at
```

不够。

Event增加：

```yaml
decision_at:
  Temporal | null

announced_at:
  Temporal | null

scheduled_for:
  Temporal | null

effective_at:
  Temporal | null

occurred_at:
  Temporal | TimeRange | null
```

------

# 25. Knowledge Cutoff判断原则

是否属于事后信息，主要看：

> 在knowledge_cutoff之前，这件信息是否已经公开可知？

而不是只看：

> 政策什么时候正式生效。

例如：

```text
9月18日宣布
9月24日生效
```

如果视频9月21日发布：

> “9月24日将生效”

可以属于当时InformationSet。

不能因为effective_at > knowledge_cutoff就删掉。

------

# 26. Source时间进一步分开

Source建议区分：

```yaml
written_at:
published_at:
updated_at:
captured_at:
```

均允许null。

视频：

```yaml
recorded_at:
published_at:
```

分开。

不得把：

```text
发布时间 + 视频offset
```

伪装成真实说话绝对时间。

------

# 27. Argument Metrics V0.3

弃用单独依赖：

```text
hop_count
```

改为：

```yaml
path_metrics:

  edge_count:
    integer

  longest_path_length:
    integer

  model_bridge_count:
    integer

  explicit_shortcut_count:
    integer

  strongly_implied_edge_count:
    integer

  explicit_edge_count:
    integer
```

------

# 28. 为什么修改Inferential Distance

同一个分析可能：

主播直接说：

```text
A → E
```

但要让逻辑成立，模型诊断得到：

```text
A → B → C → D → E
```

此时：

```text
主播表达距离 = 1
分析结构距离 = 4
model_bridge_count = 3
```

比单纯：

```text
hop_count=?
```

更有意义。

Golden #002的“融资结构变化→人民币风险资本→挑战美国”正好出现这种问题：模型为了检查逻辑补出了多条桥接边，而主播原文存在显式捷径。

------

# 29. Forecast Resolution Criteria V0.3

正式拆成：

```yaml
resolution_criteria:

  creator_specified:
    ...

  model_proposed:
    ...

  human_approved:
    ...

  accepted_for_scoring:
    boolean
```

模型提出：

> “可用ROE判断银行利润下降”

不代表9527原预测就是：

> “ROE会下降”。

禁止事后替预测重新定义成功标准。

------

# 30. Forecast评分条件

只有：

```text
accepted_for_scoring = true
```

才进入正式Forecast Score。

否则保持：

```text
unresolved / low_resolvability
```

Golden #002对17条Forecast全部保留了“模型提出的判据不能倒灌成主播承诺”的边界，这是应正式吸收的。

------

# 31. TranscriptCorrection V0.3细化

继续保持：

```text
ASR Error
≠
Speaker Slip
```

TranscriptCorrection增加：

```yaml
correction_status:
  proposed
  accepted
  rejected
  needs_audio_review

acoustic_confidence:
  0-1 | null

semantic_confidence:
  0-1 | null
```

例如：

```text
“潘刚盛”
```

文本语义上几乎肯定是潘功胜，

但没听音频以前：

```text
semantic_confidence = high
acoustic_confidence = unknown
status = needs_audio_review
```

这比笼统一个confidence更准确。

------

# Part III — Extraction Spec V0.3

# 32. V0.3完整Pipeline

```text
00 Input Registration

01 Source Registration
01B Source Family / Lineage Resolution

02A ASR Normalization
02B Spoken Content Annotation

03 Semantic Segmentation

04 Claim Extraction
04A Claim Atomicity Test
04B Temporal / Population / Quantifier Resolution
04C Attribution Resolution
04D Claim Occurrence Consolidation

05 Reality Object Resolution
   Actor
   Event
   StructuralProcess
   Indicator
   Policy

05B Indicator Observation Normalization

06 Verification
06B Evidence Independence Check

07 Narrative Deconstruction

08 Argument Reconstruction
08B Argument Distance Audit

09 Mechanism Resolution

10 Thesis Resolution

11 Forecast Resolution

12 Contradiction Mapping

13 Heuristic Mining

14 Validation

15 Review Queue

16 Commit
```

------

# 33. Phase 01B — Source Family Resolution

每个Source注册后问：

```text
是否来自另一个已有Source？
是否是转载？
是否是转录？
是否是同一次ASR产生？
是否只是同一官方材料的二次报道？
```

建立：

```text
source_family_id
```

------

# 34. Phase 04C — Attribution Resolution

对每个Claim依次问：

```text
谁在当前Source中说出来？
是谁的原始观点？
这是直接引用、转述还是主播解释？
有没有找到原始Source？
```

禁止简单使用一个：

```text
speaker
```

解决全部归属问题。

------

# 35. Phase 04D — ClaimOccurrence Consolidation

Claim初抽后执行一次：

```text
Claim Dedup Pass
```

比较：

```text
statement semantics
claimant
reference_time
scope
```

重复项转为：

```text
ClaimOccurrence
```

------

# 36. Phase 05 — StructuralProcess Detection

当看到：

```text
近年来
长期
逐渐
持续下降
不断增加
结构发生变化
正在转型
过去十年
```

不能直接判StructuralProcess。

Agent应问：

```text
是否存在至少两个时期的可观察状态？
```

如果有：

Candidate StructuralProcess。

如果只有主播一句判断：

仍是Claim。

------

# 37. Phase 05B — Financial Data Normalization

所有重要数字必须先回答：

```text
它是Stock还是Flow？

绝对值还是占比？

如果占比：
分子是什么？
分母是什么？

Gross还是Net？

时间点还是期间？

同比、环比还是累计？

Observed还是Projected？

使用哪个数据Vintage？
```

无法回答：

Review。

------

# 38. 禁止跨口径自动推理

例如禁止：

```text
新增贷款占比下降
→
银行贷款存量下降
```

也禁止：

```text
直接融资增量超过贷款
→
直接融资存量已经超过贷款
```

除非对应数据支持。

Golden #002中“增量排名→存量退居次席”已经被列为Critical Review项。

------

# 39. Phase 06B — Evidence Independence Check

Verification除了：

```text
有几个Source支持？
```

必须再问：

```text
有几个独立SourceFamily支持？
```

同源转载：

不能重复加权。

------

# 40. Evidence继承禁止

这是V0.3新增硬规则：

> 前提是真的，不代表结论自动获得相同真实性。

例如：

```text
直接融资占比上升      verified
        ↓
银行利润一定下降      ?
```

后者必须独立Assessment。

不能发生：

```text
Premise verified
→ Conclusion verified
```

的自动传播。

Golden #002明确将数据层、解释层和结构结论分开，并指出前提数据可信不能自动传递到“化债基本解决”“银行利润下降”“中美风险资本地位变化”等结论。

------

# 41. Phase 08B — Argument Distance Audit

每条核心Argument完成后生成：

```text
Original Shortcut

vs

Expanded Reasoning Path
```

例如：

```text
主播：
社融结构变化
→
中国挑战美国风险资本

系统诊断：
社融结构变化
→
去除政府债影响
→
识别早期股权资本
→
识别人民币计价资本
→
验证规模增长
→
与美国同阶段数据比较
→
验证退出/收益/创新能力
→
才能讨论竞争地位
```

中间边：

```text
model_reconstruction
```

不得改写成主播观点。

------

# 42. Thesis生成规则加强

StructuralProcess存在后：

禁止把：

> “结构发生变化”

重复做成Thesis。

Thesis必须包含至少一个：

```text
原因解释
未来后果
机制解释
结构意义
```

------

# 43. StructuralProcess → Thesis关系

建议使用：

```text
INTERPRETS
EXPLAINS
PREDICTS_EFFECT_OF
```

Relation registry暂不扩展过多。

若正式关系尚无：

使用：

```text
x_candidate_<relation>
```

进入Registry Review。

------

# 44. Review Queue新增类别

增加：

```text
measurement_definition
source_dependency
attribution_chain
process_boundary
claim_duplication
argument_bridge
event_timing
```

------

# Part IV — V0.3 Validation Rules

# R022 — Structural Process Boundary

StructuralProcess不得只有单一孤立Claim支持。

------

# R023 — Observation Type

每个重要IndicatorObservation必须具有：

```text
measurement_type
value_status
reference_period
```

------

# R024 — Ratio Definition

Ratio/Share必须：

```text
numerator + denominator
```

或者显式：

```text
unknown + review_required
```

------

# R025 — Source Independence

同一SourceFamily不能被计为多个独立支持来源。

------

# R026 — Attribution Chain

当：

```text
asserted_by != claimant
```

必须存在：

```text
attribution_chain
```

------

# R027 — Claim Occurrence

语义重复Claim不得仅因出现位置不同重复建对象。

------

# R028 — Event Time

存在：

```text
announcement != effective date
```

时必须分别保存。

------

# R029 — Knowledge Cutoff

已公开但尚未生效的信息允许进入InformationSet。

截止时间后首次公开的信息不得进入。

------

# R030 — Argument Distance

包含model reconstruction的Argument必须保存：

```text
model_bridge_count
```

------

# R031 — Forecast Criteria Provenance

模型提出的resolution criteria：

不得自动：

```text
accepted_for_scoring=true
```

------

# R032 — Truth Non-Propagation

任何：

```text
Claim A verified
```

不得自动提升：

```text
Claim B
Argument
Thesis
Forecast
```

的Veracity。

------

# R033 — Stock / Flow Integrity

禁止在没有明确转换依据的情况下：

```text
Flow → Stock
Stock → Flow
Growth → Level
Share → Absolute Amount
```

------

# R034 — Projected / Observed Integrity

Projected value不得作为Observed fact。

------

# Part V — V0.3正式吸收与暂缓吸收

## 正式吸收

```text
StructuralProcess
ClaimOccurrence
SourceFamily
Attribution Chain
Event multi-time model
Financial Observation semantics
Argument distance metrics
Forecast criteria provenance
Evidence independence
Truth non-propagation
```

------

## 暂缓吸收

以下继续作为Candidate，不进入正式核心Ontology：

```text
case_based_signal_inference
mixed_statistical_and_analogy
新的细粒度Argument Type大全
大量新的Relation Type
自动StructuralProcess评分
自动Thesis重要性评分
复杂证据权重公式
```

原因：

> 目前主要来自Golden #002单一案例，跨题材证据不足。

------

# Part VI — 对Golden #001 / #002的迁移

## Golden #001

主要迁移：

```text
Fed加息
→ Event

“市场重新定价”
→ ExpectationSnapshot / Narrative Regime

长期紧缩环境
→ 是否升级StructuralProcess
暂不自动升级，需时间序列支持

TXT/SRT
→ same SourceFamily

Forecast
→ creator criteria / model criteria分离
```

------

## Golden #002

主要迁移：

```text
中国融资结构变化
→ StructuralProcess Candidate

2013前、2025、2026等融资数字
→ IndicatorObservation

增量 / 存量
→ measurement_type严格分开

TXT/SRT
→ same SourceFamily

求是原文 / 财联社转载
→ lineage family

9527朗读潘功胜
→ attribution_chain

重复数据朗读
→ ClaimOccurrence

中美风险资本竞争
→ 高model_bridge_count Thesis
```

------

# Part VII — V0.3以后如何判断StructuralProcess

以“中国融资结构多元化”为例：

正确：

```text
Observation 2013以前
银行间接融资占比较高

Observation 2025
债券/股票/政府债融资占比变化

Observation 2026
存量结构继续变化
        ↓
StructuralProcess
“中国融资结构多元化”
```

然后：

```text
9527：
这个变化意味着银行长期利润结构改变
        ↓
Thesis
```

然后：

```text
为什么？
        ↓
Mechanism
```

三层严格分开。

------

# Part VIII — Heuristic仍保持克制

Golden #002出现两个值得继续追踪的方法：

```text
增量看趋势，存量看空间
```

以及：

```text
不要只看债务处理结果，
继续追问确权、谈判、成本和执行过程
```

但仍保持：

```text
candidate_only
```

因为一条视频不足以证明稳定分析框架。Golden #002自己也明确要求继续统计复现、适用条件、反例与错误率。

------

# Part IX — V0.3工程意义

如果V0.3稳定，MacroMind就拥有五种不同层次：

```text
现实世界

Event
StructuralProcess
IndicatorObservation
        ↓

知识表达

Claim
Assessment
        ↓

分析推理

Argument
Mechanism
Thesis
Forecast
        ↓

高层结构

Contradiction
Heuristic
```

这意味着：

> MacroMind不再只是“新闻知识图谱”。

它开始能够表达：

```text
离散事件
长期结构变化
数据状态
分析师观点
具体推理链
可复用机制
长期命题
未来预测
分析方法
```

------

# Part X — V0.3之后的实施路线

不建议再立即升级V0.4。

下一阶段：

```text
V0.3
↓
迁移Golden #001 / #002
↓
Golden #003
↓
Golden #004
↓
Golden #005
```

\#003—#005应故意选择不同领域，例如：

```text
地缘政治
企业/产业
社会或国内政策
```

目标不是继续完善得越来越复杂，而是观察：

> **V0.3以后是否仍出现“缺核心对象”的问题。**

如果只出现：

```text
字段小修
Registry新增
Relation枚举调整
Prompt调整
```

而不再需要：

```text
新增核心Ontology对象
```

则认为：

# Ontology进入稳定期。

此时可以开始Codex工程实现。

------

# Part XI — Codex启动门槛

满足：

```text
Golden #001—#005
```

后，如果：

1. Event / StructuralProcess / Thesis边界稳定；
2. Claim Atomicity基本稳定；
3. Attribution稳定；
4. 时间语义稳定；
5. 数据口径稳定；
6. 不再出现重大Ontology缺失；

即可让Codex实现第一阶段：

```text
Schema
Validator
Registry
ID generator
Source lineage
ClaimOccurrence
Audit
Review Queue
Golden Benchmark Runner
```

暂时仍不要让Codex自己决定：

```text
什么是主要矛盾
什么是Validated Heuristic
什么Thesis最重要
```

这些继续由高能力模型 + 人工控制。

------

# V0.3最终核心公式

## Reality

```text
Reality =
Event
+ StructuralProcess
+ IndicatorObservation
+ Policy State
```

## Claim

```text
Claim =
Proposition
+ Claimant
+ AssertedBy
+ Attribution
+ AssertedAt
+ ReferenceTime
+ Population
+ Quantifier
+ Evidence
```

## Evidence

```text
Evidence Strength
≠ Number of Sources

Evidence Strength
depends on
Independent Source Families
+ Source Quality
+ Source Fidelity
```

## Argument

```text
Argument =
Explicit Edges
+ Strongly Implied Edges
+ Model Bridges
+ Limitations
```

## Thesis

```text
Thesis =
Interpretation
of
Events / StructuralProcesses / Indicators
through
Arguments / Mechanisms
```

## Forecast

```text
Forecast =
Future Claim
+ KnowledgeCutoff
+ PredictionWindow
+ ModalStrength
+ Creator Criteria
+ Approved Resolution Criteria
```

## Golden Sample原则

```text
不是证明9527正确。

而是准确保存：

他说了什么
→
他说的是谁的观点
→
描述哪个时期
→
用了什么数据
→
数据是什么口径
→
如何一步步推理
→
中间跳过了什么
→
哪些后来可以验证
→
哪些方法在不同案例反复出现
```

这就是MacroMind V0.3。