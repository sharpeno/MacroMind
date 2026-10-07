# MacroMind V0.2 Patch

**Status:** Draft Patch
**Based on:** Golden Sample #001 + Cross-Model Review + Human Adjudication
**Purpose:** 修正V0.1在时间语义、市场共识、Claim原子性、ASR纠错与主播口误、预测强度等方面暴露的问题。

------

# Part A — Ontology V0.2 Patch

## A1. 核心Ontology不扩张

V0.1的13个核心对象保持不变：

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

Golden Sample #001没有证明需要新增核心对象。

V0.2主要增加辅助语义结构。

------

## A2. 新增辅助对象：ExpectationSnapshot

### 定义

ExpectationSnapshot表示：

> 某一特定时间点或时间窗口内，某一特定群体对一个未来事件或变量的预期状态。

它不是事实预测本身，也不是某个分析师个人Forecast。

例如：

市场在2026-08-28如何定价9月Fed加息。

### 用途

解决以下模糊表达：

“市场认为……”

“市场普遍预计……”

“大家都觉得……”

“主流观点是……”

这些表达不能再直接作为无时间、无群体的Claim。

ExpectationSnapshot必须包含：

- target
- as_of
- population
- expectation
- evidence

------

## A3. 新增分析维度：Population

Population用于回答：

> “谁的共识？”

第一版Registry：

```text
market_pricing
desk_survey
economist_survey
sell_side_research
financial_media
policy_makers
fomc_participants
institutional_investors
retail_investors
social_media
unspecified_market
```

例如：

利率期货定价 ≠ 经济学家调查 ≠ 财经媒体叙事。

即使同一时间给出完全不同结论，也不构成Source Conflict。

------

## A4. 新增辅助概念：NarrativeRegime

NarrativeRegime暂不作为Canonical核心对象。

它属于Derived / Generated Structure。

定义：

> 某一时间窗口内，市场、媒体或分析群体围绕某一主题主要在讨论什么问题。

例如：

```text
Regime A:
“会降息多少？”

↓

Regime B:
“会不会重新加息？”

↓

Regime C:
“9月会不会加？”

↓

Regime D:
“这次是一次性还是连续加息？”
```

NarrativeRegime应由：

ExpectationSnapshot + Claims + Sources

重建。

不得由单篇新闻直接产生。

------

## A5. Source Conflict重新定义

V0.1：

```text
Claim A != Claim B
→ Source Conflict
```

过于简单。

V0.2要求至少满足：

```text
Same Proposition
+
Same Reference Time
+
Same Population
+
Same Scope
+
Logically Incompatible
```

才能建立：

```text
CONTRADICTS
```

否则优先考虑：

```text
TEMPORALLY_EVOLVES_FROM
DIFFERS_BY_POPULATION
DIFFERS_BY_SCOPE
QUALIFIES
```

------

## A6. ASR Error 与 Speaker Slip正式分离

必须区分：

### ASR Error

主播实际说的是：

“沃什”

机器识别成：

“卧实”

这是Evidence transcription error。

可以修正Normalized Transcript。

### Speaker Slip

主播实际说的是：

“30年期房贷直接挂钩30年期美债”

经过回听确认转写正确，但事实口误。

此时：

Raw Transcript与Normalized Transcript均保留：

“30年期美债”

另外建立：

```text
SourceSegmentAnnotation
annotation_type:
  speaker_slip_confirmed
```

Canonical Knowledge层另存：

“30年固定房贷通常更紧密关联10年期美债收益率”。

禁止用事实层内容倒改主播原话。

------

## A7. 新增辅助对象：SourceSegmentAnnotation

用于记录：

```text
speaker_slip
self_correction
ambiguous_reference
rhetorical_exaggeration
unclear_audio
mixed_fact_and_opinion
```

它与TranscriptCorrection分离。

TranscriptCorrection回答：

> “机器有没有听错？”

SourceSegmentAnnotation回答：

> “机器听对了，但说话本身有什么值得标注的地方？”

------

# Part B — Schema V0.2 Patch

## B1. Claim增加 reference_time

V0.1：

```yaml
asserted_at:
knowledge_cutoff:
```

V0.2：

```yaml
asserted_at:
  # 什么时候说这句话

reference_time:
  # 这句话描述的是哪个时间点/时期

knowledge_cutoff:
  # 说这句话时可获得的信息截止时间
```

例如：

```yaml
statement:
  当时市场普遍认为不会加息

asserted_at:
  2026-09-17

reference_time:
  start: 2026-05-01
  end: 2026-08-28

temporal_mode:
  retrospective
```

------

## B2. Forecast时间结构扩展

Forecast统一使用：

```yaml
made_at:
knowledge_cutoff:

prediction_window:
  start:
  end:

reference_baseline:
```

四者禁止混用。

------

## B3. Assessment增加 valid_time

```yaml
assessment:
  assessed_at:
  valid_time:
  scope:
  observer:
```

例如：

“中美竞争是主要矛盾”

必须说明：

> 哪个时期有效？

------

## B4. Claim增加 population

凡Claim涉及：

```text
市场
大家
投资者
官员
分析师
主流观点
```

优先解析：

```yaml
population:
```

例如：

```yaml
population:
  market_pricing
```

如果无法确定：

```yaml
population:
  unspecified_market
```

并降低可验证性。

------

## B5. Claim增加 quantifier

Golden Sample #001证明：

“有些”

“多数”

“普遍”

“所有”

“唯一”

不能当成普通修辞忽略。

增加：

```yaml
quantifier:
  one
  some
  many
  majority
  median
  nearly_all
  all
  exclusive
  unknown
```

例如：

```text
“现在唯一争议就是加几次”
```

应记录：

```yaml
quantifier:
  exclusive
```

这比：

“市场开始讨论加几次”

是更强的Claim。

------

## B6. Claim Atomicity Rule正式进入Schema规范

### Rule CA-001

如果一个语句的不同子句：

- Claim Type不同；
- Veracity Assessment可能不同；
- Evidence来源不同；
- Reference Time不同；
- Population不同；
- Quantifier不同；

则必须拆成不同Claim。

例如禁止：

```yaml
statement:
  FOMC全票加息，因此内部争议已经只剩加几次。
```

应拆成：

```text
Claim A:
12:0通过加息。

Claim B:
绝大多数SEP参与者预计年内还需加息。

Claim C:
决议后市场讨论重心转向后续政策路径。

Claim D:
内部唯一争议只是加一次、两次还是多次。
```

A/B/C/D分别接受Verification。

------

## B7. Atomicity Group

为了避免拆散以后丢失原句结构，增加：

```yaml
atomicity_group_id:
  ag_765_xxx

source_sentence_id:
```

这样系统知道：

四个Claim原本来自同一句/同一段话。

------

## B8. Forecast增加 modal_strength

解决：

“可能”

和：

“确定会”

不能算同一强度预测。

```yaml
modal_strength:
  possible
  plausible
  likely
  very_likely
  near_certain
  certain
```

如果主播说：

“绝对不会降息”

应明显区别于：

“可能继续加息”。

------

## B9. Forecast增加 resolvability

```yaml
resolvability:
  high
  medium
  low
  unresolvable
```

以及：

```yaml
missing_resolution_fields:
```

例如：

“AI泡沫要破”

若没有：

资产篮子 / 时间 / 阈值

则：

```yaml
resolvability:
  low
```

------

## B10. ExpectationSnapshot Schema

```yaml
id:
object_type: expectation_snapshot

target_ref:

as_of:
  Temporal

reference_window:
  start:
  end:

population:
  market_pricing
  desk_survey
  economist_survey
  sell_side_research
  financial_media
  policy_makers
  fomc_participants
  other

expectation_type:
  probability_distribution
  majority_view
  median_forecast
  narrative_state
  qualitative

expectation:
  {}

sample_size:
  integer | null

source_refs:
  []

confidence:
  0-1

provenance:
  ...
```

------

## B11. Example：Fed 2026年9月

允许同时存在：

```yaml
snapshot_A:
  as_of: 2026-07-29
  population: market_pricing
  expectation:
    september_hike: strongly_priced
```

以及：

```yaml
snapshot_B:
  as_of: 2026-07-29
  population: desk_survey
  expectation:
    median_view: no_change_2026
```

两者不是冲突。

------

## B12. SourceSegmentAnnotation Schema

```yaml
id:
object_type: source_segment_annotation

source_segment_id:

annotation_type:
  speaker_slip_confirmed
  self_correction
  rhetorical_exaggeration
  ambiguous_reference
  unclear_audio
  mixed_fact_and_opinion

raw_spoken_content:

canonical_reference:
  ref | null

confidence:

evidence_refs:
  []

reviewed_by:
```

------

# Part C — Extraction Spec V0.2 Patch

## C1. Phase 02拆成两步

V0.1：

Transcript Normalization

V0.2：

```text
02A ASR Normalization
02B Spoken-Content Annotation
```

### 02A

处理：

卧实 → 沃什
asthropic → Anthropic

### 02B

处理：

30年美债 → 主播确实这样说，但属于speaker slip。

禁止混在同一Correction系统。

------

## C2. Claim Extraction前增加 Atomicity Test

每句话先问：

```text
这句话能否被一个统一的Verification结果覆盖？
```

如果不能：

Split。

再问：

```text
不同子句是否存在不同：
时间？
人口？
Claim Type？
证据？
量词？
```

任一为Yes：

Split。

------

## C3. 新增 Phase 04.5 — Temporal & Population Resolution

每个重要Claim必须依次回答：

```text
什么时候说？
→ asserted_at

说的是哪个时期？
→ reference_time

说话时最多知道什么？
→ knowledge_cutoff

在说谁的观点？
→ population

量词强度是什么？
→ quantifier
```

缺失则明确：

```text
unknown
```

禁止模型自动补齐。

------

## C4. Consensus Claim特殊规则

出现以下触发词：

```text
市场普遍
市场认为
大家认为
所有人
主流观点
投资者都
官员们
分析师普遍
```

不得使用单篇新闻直接验证。

必须尝试建立：

```text
ExpectationSnapshot[]
```

至少比较：

```text
market_pricing
survey
media/research
```

中可获得的类别。

------

## C5. Consensus Evidence Hierarchy

验证：

“市场预计Fed加息”

优先：

```text
1. 利率期货 / 市场定价
2. 官方Desk Survey
3. 大型调查
4. Sell-side研究
5. 新闻报道
6. 个别评论员
```

新闻标题不能自动代表：

“整个市场”。

------

## C6. Narrative Regime Reconstruction

如果连续资料显示讨论问题发生变化：

```text
A → B → C
```

可以生成Derived：

```text
NarrativeRegimeTimeline
```

例如：

```text
是否宽松
↓
是否重新加息
↓
9月是否加息
↓
一次还是连续加息
```

这属于Derived Output，不作为未经审核的Canonical事实。

------

## C7. Source Conflict Validator V0.2

在标记：

```text
CONTRADICTS
```

之前必须检查：

```text
proposition_match
reference_time_match
population_match
scope_match
```

若：

```text
reference_time_match = false
```

则优先：

```text
TEMPORAL_EVOLUTION
```

若：

```text
population_match = false
```

则：

```text
POPULATION_DIVERGENCE
```

------

## C8. 新增 Consensus Divergence

MacroMind应主动保留：

```text
市场定价认为A

但

经济学家调查认为B
```

不能强行决定哪一个代表“真正市场”。

这种分歧本身就是Signal。

------

## C9. Narrative Deconstruction增加“量词检查”

当9527使用：

```text
唯一
全部
根本
绝对
所有
没有任何
```

Extraction Agent必须额外问：

> 外部证据支持的是“方向”，还是支持这么强的量词？

例如：

外部证据可能支持：

“后续加息路径成为主要讨论焦点”

但不支持：

“唯一争议就是加几次”。

此时：

```text
core_claim:
  supported

quantifier_strength:
  unsupported_or_overstated
```

------

## C10. Forecast Lineage扩展为 Lead-Time Tracking

确认历史Forecast后记录：

```yaml
forecast:
  made_at:

consensus_crossing:
  first_market_majority_at:
  first_survey_majority_at:
  first_media_regime_shift_at:

event_outcome_at:
```

由此生成：

```text
Analyst Lead Time
```

注意：

不同Population必须分别计算。

------

## C11. 禁止用事后Consensus回写历史

例如：

9月16日市场已经普遍讨论继续加息。

不能因此推断：

7月市场也早已普遍如此。

必须用当时来源重建ExpectationSnapshot。

------

# Part D — Golden Sample #001 Adjudication Patch

## D1. C02重新拆分

原C02废弃为复合Claim。

拆成：

### C02-A

```text
FOMC以12:0通过本次25bp加息。
```

类型：

```text
factual
```

状态：

```text
verified
```

------

### C02-B

```text
绝大多数SEP参与者预计2026年仍需至少再加息一次。
```

类型：

```text
factual
```

Population：

```text
fomc_participants
```

Quantifier：

```text
nearly_all
```

状态：

```text
verified
```

------

### C02-C

```text
决议后，公开市场和财经讨论的焦点明显转向后续加息路径。
```

类型：

```text
interpretive / consensus_state
```

Population：

```text
financial_media + market_commentary
```

状态：

```text
supported
```

------

### C02-D

```text
现在唯一的争议只是加一次、两次还是多次。
```

类型：

```text
interpretive
```

Quantifier：

```text
exclusive
```

状态：

```text
partially_supported / overstrong_quantifier
```

原因：

外部材料支持“后续路径成为核心讨论”，但不足以证明内部不存在其他重要分歧。

------

## D2. 原C04 Source Conflict降级

原：

```text
C04 CONTRADICTS pre-FOMC source
```

修改为：

```text
temporal_scope_unresolved
```

并拆解不同reference_time。

------

## D3. 但不自动接受“7—8月市场完全不相信加息”

Golden Sample人工裁决必须保留：

2026年7月已经存在明显鹰派委员；

市场定价与调查结果同时出现分歧。

因此：

```text
“7—8月主流完全不认为会加息”
```

本身也必须进一步限定：

```text
哪一天？
哪个Population？
什么量化标准？
```

------

## D4. 房贷Claim裁决

主播原话：

```text
30年房贷直接挂钩30年美债
```

人工听审确认：

```text
speaker_slip_confirmed
```

Evidence Transcript：

不修改。

Canonical Knowledge：

另存正确事实。

------

## D5. ASR人工裁决

确认高置信：

```text
卧室 / 卧实 / 沃实
→ 沃什

asthropic / asropic
→ Anthropic
```

这些进入：

```text
TranscriptCorrection.status = accepted
```

------

# Part E — V0.2新增Validation Rules

### R013 — Claim Atomicity

若复合语句不同子句可获得不同Assessment：

必须拆分。

### R014 — Reference Time

Retrospective、Consensus、Historical Comparison Claim：

原则上必须具有reference_time。

### R015 — Population

涉及“市场/主流/大家/官员普遍”等集体主体：

必须具有population或明确unknown。

### R016 — Quantifier

出现所有、唯一、多数、普遍等量词：

必须保存quantifier。

### R017 — Conflict Alignment

建立CONTRADICTS前必须检查：

reference_time + population + scope。

### R018 — Speaker Slip

已确认主播口误不能通过Transcript Normalization删除。

### R019 — Consensus Verification

不得用单篇新闻证明“市场普遍”。

### R020 — Forecast Modal Strength

Forecast必须尽量保存modal_strength。

### R021 — Consensus Lead Time

Analyst Lead Time只能和同一Population的ExpectationSnapshot比较。

------

# Part F — V0.2核心变化总结

V0.1主要解决：

```text
谁说了什么？
依据是什么？
如何推出结论？
```

V0.2进一步解决：

```text
他什么时候说？
他说的是哪个时期？
他说的是哪一群人的观点？
这群人的观点当时究竟如何分布？
他说的是“可能”“多数”还是“所有”？
后来市场是在反驳他，还是只是发生了时间演化？
```

因此新的核心表达变为：

```text
Claim =
Statement
+ Claimant
+ AssertedAt
+ ReferenceTime
+ Population
+ Quantifier
+ Scope
+ Evidence
```

Forecast：

```text
Forecast =
Claim
+ KnowledgeCutoff
+ PredictionWindow
+ ModalStrength
+ ResolutionCriteria
```

Consensus：

```text
ConsensusState =
Proposition
+ Population
+ AsOfTime
+ Distribution
+ Evidence
```

Conflict：

```text
Conflict =
Same Proposition
+ Same Time
+ Same Population
+ Same Scope
+ Incompatible Values
```

这四个公式作为MacroMind V0.2的时间与共识建模基础。