# MacroMind Extraction Spec V0.1

**Version:** `0.1-draft`
**Depends on:**

- MacroMind Ontology V0.1
- MacroMind Schema V0.1

**Primary purpose:**
规定 Agent 如何将：

```text
视频
音频
TXT / SRT
视频简介
参考新闻
官方文件
经济数据
```

转化为：

```text
Evidence
→ Claim
→ Event / Indicator
→ Assessment
→ Argument
→ Mechanism
→ Thesis
→ Forecast
→ Contradiction
→ Heuristic Candidate
```

本规范的第一原则不是“尽量多抽取”，而是：

> **宁可少抽，也不要把推断伪装成事实；宁可进入 Review Queue，也不要静默修正不确定内容。**

------

# 1. Pipeline 总览

标准流水线：

```text
00 Input Registration
        ↓
01 Source Registration
        ↓
02 Transcript Normalization
        ↓
03 Segmentation
        ↓
04 Claim Extraction
        ↓
05 Entity / Event / Indicator Resolution
        ↓
06 Verification
        ↓
07 Narrative Deconstruction
        ↓
08 Argument Reconstruction
        ↓
09 Mechanism Resolution
        ↓
10 Thesis Resolution
        ↓
11 Forecast Resolution
        ↓
12 Contradiction Mapping
        ↓
13 Heuristic Mining
        ↓
14 Validation
        ↓
15 Review Queue
        ↓
16 Commit
```

前7步主要解决：

> **他说了什么？发生了什么？依据是什么？**

8—13步主要解决：

> **他为什么这么判断？**

14—16步解决：

> **这些结果能不能正式进入知识库？**

------

# 2. 输入包 Input Bundle

一条视频作为一个 `ingestion_job`。

推荐目录：

```text
inbox/
└── job_20260917_765/
    ├── video.mp4
    ├── audio.wav
    ├── transcript.txt
    ├── transcript.srt
    ├── metadata.yaml
    ├── description.txt
    └── sources.yaml
```

其中：

```yaml
job_id:
  job_20260917_765

analyst:
  obs_youhegaojian9527

video_title:
  ...

video_published_at:
  2026-09-17T09:36:31+08:00

known_source_urls:
  - ...
```

### Input Required

最低需要：

```text
TXT 或 SRT
视频标题
发布时间
分析者
```

### Strongly Recommended

```text
TXT
SRT
原视频/音频
视频简介
视频作者列出的参考新闻
```

原因：

TXT适合全文处理。

SRT适合SourceSegment定位。

Audio用于Review Queue回听。

------

# 3. Phase 00 — Input Registration

目标：

> 建立本次处理任务，不进行任何内容分析。

生成：

```yaml
run_id:
job_id:

input_files:
  ...

analyst_id:
  obs_youhegaojian9527

started_at:

pipeline_version:
  extraction_spec_0.1

model_plan:
  normalization:
  extraction:
  verification:
  reasoning:
```

### 强制规则

任何后续生成对象必须能够追溯：

```text
object
→ run_id
→ job_id
→ original files
```

------

# 4. Phase 01 — Source Registration

对每一个原始来源建立 `Source`。

例如一条视频 + 六条新闻：

```text
1 × video Source
6 × news Source
```

不能：

```text
6条新闻
→ 一个“reference_news” Source
```

必须独立注册。

### Source关系

如果：

> 财联社文章引用Fed公告，

应建立：

```text
财联社 Source
DERIVED_FROM
Fed官方 Source
```

但只有能够确认时才建立。

不能仅凭Agent猜测来源血缘。

------

# 5. Phase 02 — Transcript Normalization

目标：

> 提升可读性和可抽取性，但不改变原始证据。

产生：

```text
Raw Transcript
+
Normalized Transcript
+
TranscriptCorrection[]
```

------

## 5.1 可以自动修正

高置信度、外部证据明确的：

```text
专有名词
已知人物
机构名
明显ASR同音词
明显标点
断句
```

例如：

```text
潘刚盛
→ 潘功胜
```

如果存在官方文章可以高置信确认。

------

## 5.2 不允许自动静默修正

以下必须进入 Review：

```text
数字
百分比
日期
利率
汇率
专有术语且上下文有歧义
疑似主播本人说错
```

例如出现：

> “股票融资约10%”

而上下文计算明显不一致。

不能改成3%。

必须：

```yaml
status:
  needs_audio_review
```

------

# 6. Phase 03 — Semantic Segmentation

不要机械按照一分钟一段。

需要把视频拆成：

# Semantic Segment

每个Segment应该尽量只包含：

> 一个相对完整的小论证或小主题。

例如第765期可以拆成：

```text
S01 Fed加息及未来路径
S02 对日本央行和日元的影响
S03 日美联合干预汇率
S04 黄金和油价旧预测复盘
S05 能源通胀与加息有效性
S06 AI估值与高利率
S07 政客与结构力量
S08 美国滞胀
S09 长债收益率解释
```

### Segment必须保留

```text
start_time
end_time
raw_text
normalized_text
topic_hint
```

------

# 7. Phase 04 — Claim Extraction

这是整个Pipeline最重要的一步。

### 基本原则

每一个Claim必须满足：

> **单独拿出来，仍然可以理解它在说什么。**

错误：

```text
“所以这个肯定不行。”
```

正确：

```text
“美联储加息无法直接解决能源供给冲击造成的通胀。”
```

------

# 8. Claim Granularity

避免两种极端。

### 太粗

错误：

```text
9527认为美国经济有问题。
```

信息量太低。

### 太细

错误：

每一句口语都建立一个Claim。

正确粒度：

> 一条能够被验证、反驳、支持或者作为论证步骤使用的陈述。

------

# 9. Claim 分类流程

每个Claim依次判断：

```text
它是在描述已经发生的事情？
→ factual

它是在解释意义？
→ interpretive

它在说A导致B？
→ causal

它在比较A和B？
→ comparative

它在判断某人的动机？
→ motive_attribution

它在表达应该怎样？
→ normative

它在说未来会发生什么？
→ forecast

它在说“如果A没有发生会怎样”？
→ counterfactual
```

允许：

```text
primary_type
+
secondary_tags
```

但V0.1建议主要保留一个主类型。

------

# 10. Claim Attribution

这是硬规则。

必须明确：

> 这句话到底是谁说的？

例如视频里：

> 沃什说长期收益率上涨有三个原因。

然后9527说：

> 这些解释“倒转因果”。

必须形成两个不同Claim：

```text
Claim A
claimant = Warsh
Claim B
claimant = 9527
```

不能合并。

------

# 11. Claim Derivation Type

每条Claim判断来源方式：

```text
quoted
paraphrased
calculated
inferred
causal_inference
historical_analogy
recommendation
model_generated
```

例如：

> “16/18官员认为还需要加息。”

如果直接来自点阵图：

```text
quoted / calculated
```

而：

> “所以这不是一次性加息。”

属于：

```text
inferred
```

------

# 12. Temporal Mode

每条Claim必须尽量识别：

```text
ex_ante
contemporaneous
ex_post
retrospective
```

尤其注意：

> “我五月就说过……”

这是：

```text
retrospective
```

不是自动变成五月的Forecast。

第765期中主播多次以“我5月份说过”“7月份提醒过”来复盘此前观点。

必须后续回查原视频。

------

# 13. Phase 05 — Actor / Event / Indicator / Policy Resolution

Claim抽出来后，再处理客观知识对象。

顺序：

```text
Claim
↓
它说到了谁？
→ Actor

它说到了什么发生的事情？
→ Event

它引用了什么可重复数据？
→ Indicator / Observation

它描述的是长期政策状态吗？
→ Policy
```

------

# 14. Event Extraction

创建Event前问：

> **现实世界是否真的发生了一次状态变化？**

例如：

```text
Fed宣布加息25bp
→ Event
```

但：

```text
美国高利率
→ 不是Event
```

它更可能是：

```text
State / Claim / Policy context
```

------

# 15. Event Deduplication

同一事件可能出现于20篇新闻。

禁止创建：

```text
event_fed_hike_reuters
event_fed_hike_cls
event_fed_hike_video
```

应该合并成：

```text
event_fed_20260916_rate_hike
```

不同Source共同支持它。

------

# 16. Indicator Extraction

出现：

```text
CPI
利率
汇率
社融
房贷利率
收益率
PMI
就业
```

优先判断是否已经存在Indicator。

存在：

> reuse。

不存在：

> Candidate Registry Entry。

不能随意生成大量同义Indicator：

```text
US mortgage rate
American mortgage interest
美国住房贷款利率
```

必须Entity Resolution。

------

# 17. Phase 06 — Verification

Verification只验证：

> **Claim与Evidence之间是什么关系。**

不负责判断：

> 它重要不重要。

------

## Verification Priority

优先顺序：

```text
L0 官方原始来源
L1 原始数据 / 原始讲话
L2 高质量媒体直接报道
L3 二次媒体
L4 视频引用
L5 模型推断
```

不要把这个顺序简单等同为：

> L0永远正确。

它只是：

> 越靠近原始来源。

------

# 18. Verification Output

产生Assessment：

```yaml
dimension:
  veracity

value_code:
  verified
  likely_true
  uncertain
  disputed
  likely_false
  false
  unverifiable
```

------

# 19. Source Conflict

如果：

```text
Source A says X
Source B says Y
```

不要强制选一个。

生成：

```text
Claim A
Claim B
CONTRADICTS
```

并进入：

```text
Review Queue / source_conflict
```

如果冲突重要。

------

# 20. Phase 07 — Narrative Deconstruction

这是MacroMind与普通新闻知识库最大的区别之一。

对象：

> 新闻中的Claim。

分析者：

> 9527。

目标：

> 记录9527如何评价新闻本身提供的解释。

------

# 21. Narrative Deconstruction Questions

对每一个被9527明确讨论或质疑的重要新闻Claim，依次问：

```text
1. 他接受这个事实吗？

2. 他接受这个因果关系吗？

3. 他认为它是原因、结果还是表象？

4. 他认为有没有关键内容被遗漏？

5. 他认为报道是否突出次要变量？

6. 他认为新闻是否在安抚市场？

7. 他认为新闻是否倒置因果？

8. 他认为真正值得关注的是什么？
```

------

# 22. Narrative Assessment

创建Assessment：

```text
veracity
completeness
causal_role
narrative_role
relevance
information_gain
```

例如：

```yaml
target:
  claim_warsh_economy_strong

observer:
  obs_youhegaojian9527

dimension:
  narrative_role

value_code:
  causal_obscuring
```

------

# 23. 禁止Agent自己替9527创造“烟雾弹”

如果9527没有表达类似意思：

不能因为模型自己觉得：

> 这条新闻像烟雾弹。

就写：

```text
observer = 9527
```

如果模型自己判断：

```text
observer = obs_macromind_analyzer
```

必须严格分开。

------

# 24. Phase 08 — Argument Reconstruction

Claim提取完成之后，再重建推理。

绝对不要：

> 一边听一句，一边直接创建Argument。

Argument必须在看到相对完整Segment后再创建。

------

# 25. Argument基本结构

```text
Premise
↓
Inference
↓
Intermediate Claim
↓
Inference
↓
Conclusion
```

例如：

```text
Fed加息
↓
未来高利率持续时间可能变长
↓
资金成本维持高位
↓
高估值资产压力增加
↓
AI估值风险上升
```

------

# 26. 每一跳必须分类

```text
direct
statistical
causal
analogy
elimination
speculation
```

不能只有：

```text
A → B
```

必须知道：

> 为什么能从A走到B。

------

# 27. Missing Step

如果9527直接：

```text
A
→
D
```

但中间需要B、C才能成立：

系统允许：

```text
missing_step_detected
```

模型可以提出：

```text
B / C candidate
```

但：

```text
origin = model_inference
```

绝不能伪装成9527原话。

------

# 28. Argument必须区分三种内容

### Explicit

9527明确说了。

### Strongly Implied

没有完整说出来，但语言关系非常清晰。

### Model Reconstruction

模型为了使推理图完整而补全。

这三个等级必须保留。

------

# 29. Phase 09 — Mechanism Resolution

Argument是：

> 某一期的具体推理。

Mechanism是：

> 跨案例重复使用的传导规律。

Agent不能看到一次：

```text
利率↑ → AI↓
```

马上建一个宏大Mechanism。

流程应该：

```text
先匹配已有Mechanism
↓
找到 → reuse
↓
找不到 → candidate mechanism
```

------

# 30. Mechanism Match

至少比较：

```text
输入变量
中间传导
输出变量
条件
领域
```

例如：

```text
Interest Rate
→ Funding Cost
→ Discount Rate
→ High Duration Asset Valuation
```

多次出现以后形成稳定机制。

------

# 31. Phase 10 — Thesis Resolution

Claim不是都值得变成Thesis。

创建Thesis必须满足：

至少出现一个：

```text
跨时间意义
结构意义
需要未来验证
可以累积支持/反证
能够连接多个Event
```

------

# 32. 新Thesis还是旧Thesis？

Agent必须先：

```text
search existing thesis
```

再判断：

```text
same
update
related
new
```

禁止：

> 每条视频都创建新的Thesis。

------

# 33. Thesis Update

如果当前视频提供：

```text
新证据
```

应该建立：

```text
Claim SUPPORTS Thesis
```

而不是直接重写Thesis文本。

如果结构性含义真的变化：

```text
Thesis V2
SUPERSEDES
Thesis V1
```

------

# 34. Phase 11 — Forecast Resolution

所有Future Claim都先作为：

```text
claim_type = forecast
```

再创建Forecast对象。

------

# 35. Forecast Resolution要求

必须尽量得到：

```text
预测对象
方向
时间范围
条件
阈值
```

如果主播只说：

> “后面还会加。”

时间范围不明确：

```text
prediction_window = unknown
```

不能自己补：

> 3个月内。

------

# 36. Retrospective Forecast Rule

如果今天说：

> “我今年五月已经说过AI泡沫要破。”

系统只创建：

```text
Retrospective Claim
```

然后触发：

```text
forecast_lineage review
```

Agent去历史数据寻找五月原话。

只有找到：

```text
历史SourceSegment
```

才能创建五月Forecast。

------

# 37. Phase 12 — Contradiction Mapping

这是最容易被过度使用的阶段。

硬规则：

> **Contradiction是后置分析，不是前置分类器。**

不能看到：

```text
中美
```

就自动：

```text
US-China contradiction
```

------

# 38. Contradiction创建条件

至少应满足：

```text
长期存在
双方/多方目标存在结构性张力
多个事件都能映射进去
多个Thesis可被该结构解释
```

------

# 39. Primary / Secondary

Agent禁止：

```text
contradiction.primary = true
```

只能：

```yaml
assessment:
  dimension:
    contradiction_role

  value:
    primary

  scope:
    global_geopolitics

  observer:
    obs_youhegaojian9527
```

如果没有足够材料：

```text
do not assess
```

------

# 40. Phase 13 — Heuristic Mining

这是整个项目最后才应该做的一步。

不是每个视频都必须输出Heuristic。

默认：

```text
0 candidate heuristic
```

比：

```text
每期强行总结3条方法论
```

好得多。

------

# 41. Heuristic创建条件

只有发现：

> 这不是关于具体事件的判断，而是更一般的分析规则。

才可以Candidate。

例如：

> “不要高估政治人物对结构性经济力量的控制能力。”

属于Heuristic Candidate。

而：

> “沃什会继续加息。”

不是。

------

# 42. Heuristic Candidate必须附Evidence

```yaml
status:
  candidate

observed_in_arguments:
  - argument_x

source_segments:
  - seg_x
```

累计更多案例：

```text
candidate
↓
repeated
↓
reviewed
↓
validated
```

------

# 43. Phase 14 — Validation

每次Extraction完成必须自动跑Validator。

检查：

```text
Schema validation
Reference validation
Time validation
Source provenance
Claim attribution
Forecast lineage
Circular reasoning
Duplicate objects
Illegal assessment
Missing source
```

------

# 44. Circular Knowledge Pollution

这是硬规则。

禁止：

```text
MacroMind自己的推论
↓
下一轮被当成外部事实
↓
再用于支持自己的Thesis
```

所以：

```text
origin = model_generated
```

的Claim不能自动升级为：

```text
verified factual claim
```

除非获得独立外部Evidence。

------

# 45. Phase 15 — Review Queue

以下情况必须进入Review Queue。

### ASR类

```text
人名不确定
数字不确定
日期不确定
专业术语不确定
```

### Evidence类

```text
Source冲突
找不到原始来源
关键数字无证据
```

### Reasoning类

```text
推理跳跃过大
无法判断是谁的观点
事实/解释混杂
```

### Forecast类

```text
主播声称过去预测过
但没找到历史证据
```

### Ontology类

```text
无法归类
需要新Relation
需要新Event Type
```

### Importance类

```text
疑似重大结构变化
```

建议高能力模型/人工检查。

------

# 46. Review Priority

建议：

```text
Critical
High
Medium
Low
```

### Critical

会污染大量后续推理的：

```text
核心人物识别错误
关键政策时间错误
关键数据数量级错误
主要Thesis归属错误
```

### High

```text
预测血缘
核心Argument
Contradiction变化
```

### Medium

```text
Claim分类
Narrative Role
Entity Alias
```

### Low

```text
轻微断句
普通拼写
非关键背景信息
```

------

# 47. Phase 16 — Commit

Extraction输出先进入：

```text
staging/
```

不能直接写Canonical。

流程：

```text
extract
↓
validate
↓
review
↓
approve
↓
commit
```

正式进入：

```text
knowledge/
```

------

# 48. Canonical输出目录

一次处理后可能产生：

```text
staging/job_20260917_765/

├── source/
├── segments/
├── corrections/
├── claims/
├── actors/
├── events/
├── indicators/
├── observations/
├── assessments/
├── arguments/
├── mechanisms/
├── theses/
├── forecasts/
├── contradictions/
├── heuristics/
├── edges/
├── review_queue.json
└── extraction_report.json
```

------

# 49. Extraction Report

每次必须生成摘要。

例如：

```yaml
job_id:

sources_registered:
  7

segments:
  42

claims:
  86

claims_by_type:
  factual: 21
  causal: 25
  interpretive: 18
  forecast: 9
  ...

events:
  6

indicator_observations:
  14

arguments:
  11

candidate_theses:
  3

candidate_heuristics:
  1

review_items:
  critical: 0
  high: 3
  medium: 7
  low: 4
```

这让人可以快速判断：

> 这期抽取是不是离谱。

------

# 50. Extraction数量不是KPI

这是必须写进Spec的规则。

禁止Agent为了：

```text
“看起来抽得很丰富”
```

而：

```text
每期建20个Thesis
每期建5个Contradiction
每期建10个Heuristic
```

正常情况应该是：

```text
Claims很多
Events少
Thesis更少
Contradiction很少
Heuristic极少
```

一个大致合理的数量关系可能是：

```text
100 Claim
↓
10–20 Argument
↓
2–5 Thesis updates
↓
0–2 Contradiction updates
↓
0–1 Heuristic Candidate
```

只是经验范围，不作为硬阈值。

------

# 51. Narrative Deconstruction特别规则

9527对新闻的质疑是本项目核心资产之一。

因此每次出现：

```text
“其实”
“真正原因”
“表面上”
“这不是原因”
“这是结果”
“话里话外”
“潜台词”
“市场在安抚”
“障眼法”
“骗人的”
“没有告诉你的是”
```

都应该作为：

# Narrative Trigger

进入候选分析。

但：

> Trigger ≠ 最终Assessment。

仍然必须看完整上下文。

------

# 52. Historical Analogy特别规则

9527经常使用历史类比。

必须单独标：

```text
argument_type:
  historical_analogy
```

并记录：

```text
source_case
target_case
shared_mechanism
limits_of_analogy
```

如果没有表达：

```text
limits_of_analogy
```

允许为空。

不要自动认为：

> 两个事件完全相同。

------

# 53. Missing Information推断

如果新闻只说一半：

系统允许创建：

```text
Missing Context Candidate
```

但不能直接创建事实。

例如：

```yaml
assessment:
  dimension:
    completeness

  value:
    materially_incomplete
```

并记录：

```text
missing_context:
  - 某变量
```

如果缺失变量是模型推断：

```text
origin:
  model_inference
```

------

# 54. Information Gain

V0.1先不设计复杂公式。

可以采用：

```text
high
medium
low
redundant
unknown
```

重点回答：

> 这条Claim相比当前Knowledge State增加了多少新东西？

不是：

> 这条新闻有多轰动。

------

# 55. Importance Extraction

Extraction Agent原则上：

> 不直接做最终Importance Score。

它只抽取可能影响重要性的证据：

```text
影响范围
影响人数
持续时间
是否跨市场
是否政策变化
是否触及主要Thesis
```

之后由：

```text
Assessment Agent
```

生成Importance。

------

# 56. Model职责分工 V0.1

结合你目前的工具，我建议：

## Hermes / GPT-5.5

主要负责：

```text
视频处理
文件整理
Source注册
Transcript初步Normalization
Segment
Claim初抽
Actor/Event初抽
已有对象匹配
低风险Schema填充
```

原则：

> 做“结构化劳动”。

------

## GPT-6 Astra

主要负责：

```text
高风险ASR判断
Narrative Deconstruction
复杂Argument Reconstruction
Mechanism判断
Thesis Resolution
Forecast lineage
Contradiction Mapping
Heuristic Candidate
高优先级Review
```

原则：

> 做“高推理密度工作”。

------

# 57. 不建议现在做全自动

V0.1推荐：

```text
Hermes
↓
自动初抽
↓
GPT-6 Astra
↓
关键层审核
↓
Human
↓
少量最终Review
```

经过约：

```text
10–30期
```

以后再统计：

> 哪些任务GPT-5.5已经足够稳定。

再逐步自动化。

------

# 58. 一个完整示例

原始新闻：

> Fed加息25bp。

主播说：

> 这不是一次性加息，后面还会继续。

产生：

```text
Event E1
Fed加息25bp
Claim C1
Fed加息25bp
type=factual
Claim C2
本轮加息可能不是一次性的
type=forecast
```

Argument：

```text
点阵图
↓
多数官员倾向继续加息
↓
C2
```

然后：

```text
C1 DESCRIBES E1
C_dotplot SUPPORTS C2
```

Forecast：

```text
F1
claim=C2
```

如果主播继续：

> 日本压力会增加。

产生：

```text
Claim C3
```

Argument：

```text
C2
↓
日美利差路径
↓
日本政策空间
↓
C3
```

而不是：

```text
Fed加息
CAUSES
日本崩溃
```

把中间逻辑全部吃掉。

------

# 59. Extraction Agent系统提示的核心原则

后续可以把下面内容写进Agent System Prompt：

> 你的任务不是总结视频，而是重建一个可审计的证据—知识—推理结构。

> 永远区分事实、来源的观点、分析者的观点和模型自己的推断。

> 不要为了结构完整而创造不存在的证据。

> 不确定时进入Review Queue。

> 不覆盖Raw Evidence。

> 不把后来的自述当成过去真实发生的预测。

> 不把“主要”“重大”“烟雾弹”等评价写成对象永久属性。

> 不强迫所有内容进入Contradiction。

> 不从单个案例直接产生Validated Heuristic。

------

# 60. V0.1 Acceptance Criteria

拿10条视频跑完以后，Extraction Spec V0.1成功的标准不是：

> 全自动率100%。

而是满足：

### Traceability

任意Thesis都能向下追：

```text
Thesis
→ Argument
→ Claim
→ SourceSegment
→ 原视频
```

### Attribution

任意Claim都知道：

> 谁说的。

### Temporal Integrity

预测不会出现：

> 事后信息污染事前判断。

### Epistemic Separation

系统能区分：

```text
事实
观点
推论
预测
类比
模型补全
```

### Narrative Separation

系统能表达：

> “这句话可能是真的，但9527认为它只是结果而不是原因。”

### Historical Integrity

新结论不会覆盖旧判断。

### Low Pollution

不确定内容会进入Review，而不是偷偷写进知识库。

------

# 61. V0.1压力测试后的重点统计

完成10条视频以后建议统计：

```text
每期平均Claim数
平均Argument数
Thesis复用率
新Thesis比例
Review Queue比例
ASR错误比例
模型补全比例
无法分类比例
Forecast可验证比例
Narrative Assessment数量
Heuristic Candidate数量
```

最关键的三个指标：

```text
1. Thesis复用率
2. Review Queue质量
3. 同一视频不同模型抽取的一致性
```

如果：

> Thesis复用率很低，

说明系统可能正在制造“视频摘要型垃圾”。

如果：

> Heuristic每期都有好几个，

说明抽得太激进。

如果：

> Review Queue几乎为空，

反而要警惕Agent是不是过度自信。

------

# 62. MacroMind Extraction最终原则

整个Extraction过程可以压缩成九个问题：

```text
① 原话是什么？

② 谁说的？

③ 他说的是事实、解释还是预测？

④ 现实到底发生了什么？

⑤ 外部证据支持到哪一步？

⑥ 9527接受新闻的哪些部分，又质疑哪些部分？

⑦ 他是怎么一步一步推出结论的？

⑧ 这个结论是否更新了已有Thesis？

⑨ 这种分析方式是否在历史上反复出现？
```

只要九个问题都能留下结构化、可追溯答案，MacroMind真正有价值的知识就开始形成了。

------

# 63. V0.1实施顺序

建议实际执行时严格按照：

```text
Ontology V0.1
        ↓
Schema V0.1
        ↓
Extraction Spec V0.1
        ↓
2条现有视频人工Golden Sample
        ↓
再补8条不同领域视频
        ↓
形成10条Benchmark
        ↓
修订到V0
```