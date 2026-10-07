# MacroMind Golden Sample Extraction Prompt — GPT-6-Astra

你正在为一个名为 MacroMind 的可审计宏观推理系统创建 Golden Sample。
你的任务不是总结视频，也不是模仿主播口吻，而是严格重建：
Evidence → Claim → Event/Indicator → Assessment → Argument → Mechanism → Thesis → Forecast → Contradiction → Heuristic Candidate。

## 输入
我会提供：
1. 视频标题与精确发布时间；
2. TXT自动转写稿；
3. SRT（若有）；
4. 视频简介及主播列出的新闻URL；
5. 可选的外部验证资料。

自动转写可能存在严重的人名、数字、专业术语和英文识别错误。

## 最高优先级规则
1. 永远区分：
   - 原始事实
   - 新闻/官方来源自己的解释
   - 主播9527的观点
   - 你的模型推断
2. 不要静默修正Raw Transcript。
3. 数字、日期、利率、汇率、专有名词有歧义时，进入 Review Queue。
4. 主播后来说“我几个月前预测过”时，只创建 retrospective claim；除非找到当时原视频/原时间戳，否则不得创建历史Forecast。
5. “重大/一般”“主要/次要矛盾”“烟雾弹/障眼法”“真假”都不是对象永久属性，必须以带 Observer + Time + Scope 的 Assessment 表达。
6. 不要强迫所有内容进入 Contradiction。
7. 不要从单条视频直接创建 validated heuristic，只能创建 candidate heuristic。
8. 不要为了结构完整而编造中间证据。你可以补充 model_reconstruction，但必须明确标注。
9. 任何 Thesis 必须能够向下追溯到 Argument → Claim → SourceSegment → Source。
10. 以视频发布时间作为默认 knowledge_cutoff；发布时间之后的信息不得用于重建主播当时的推理，只能放入单独的 post-cutoff evaluation。

## Phase 1 — Source Registration
逐一注册：
- 视频/音频/转写；
- 每篇新闻；
- 每个官方文件；
- 外部验证源。
标明 role：
primary_evidence / creator_reference / verification_added。

## Phase 2 — Transcript Normalization
输出：
A. 高置信度ASR纠错；
B. 不能确定的疑点；
C. `needs_audio_review` 项。

高置信纠错也必须同时保留 raw_text 与 normalized_text。

## Phase 3 — Semantic Segmentation
按完整论证/主题切段，不按固定分钟机械切。
每段给：
segment_id / start / end / topic。

## Phase 4 — Claim Extraction
Claim必须能独立理解。
每条至少输出：
- claim_id
- segment_id
- claimant
- statement
- claim_type:
  factual / interpretive / causal / comparative / normative /
  motive_attribution / counterfactual / forecast
- derivation_type:
  quoted / paraphrased / calculated / inferred /
  causal_inference / historical_analogy / recommendation / model_generated
- temporal_mode:
  ex_ante / contemporaneous / ex_post / retrospective
- source_segment
- knowledge_cutoff
- certainty_expressed

不要把一整段视频概括成一个Claim，也不要把每句口语都拆成Claim。

## Phase 5 — Objective Knowledge Resolution
从Claims解析：
Actor / Event / Indicator / IndicatorObservation / Policy。
同一Event不得因为出现在多篇新闻中而重复创建。

## Phase 6 — Verification
优先级：
官方原始来源 > 原始数据/讲话 > 高质量直接报道 > 二次报道 > 主播引用 > 模型推断。

对重要Claim创建veracity Assessment：
verified / likely_true / uncertain / disputed / likely_false / false / unverifiable。

如果来源冲突：
保留双方Claim + CONTRADICTS关系，不要替它们自动和解。

## Phase 7 — Narrative Deconstruction
重点分析9527如何定位新闻Claim。
逐项检查：
- 他是否接受事实？
- 是否接受因果解释？
- 他认为它是原因、结果、表象还是相关性？
- 是否认为遗漏了重要变量？
- 是否认为存在安抚、障眼、烟雾弹、因果遮蔽、选择性披露等叙事作用？
- 他认为真正的信息增量在哪里？

只在主播明确表达或上下文强烈支持时创建9527的Narrative Assessment。
如果是你自己的判断，observer必须写 model，不得冒充9527。

## Phase 8 — Argument Reconstruction
每条Argument输出：
- analyst
- premises
- conclusion
- steps
- 每一步 relation
- inference_mode:
  direct / statistical / causal / analogy / elimination / speculation
- expression_level:
  explicit / strongly_implied / model_reconstruction
- evidence_refs
- mechanism_refs
- hop_count
- limitations

特别检查“结果被当成原因”“缺失中间步骤”“历史类比”。

## Phase 9 — Mechanism Resolution
优先复用已有Mechanism。
只有跨案例可复用的因果链才创建Mechanism Candidate。
单次事件链不要轻易升级成Mechanism。

## Phase 10 — Thesis Resolution
只有具备跨时间/结构意义、需要未来支持或反证的判断才成为Thesis。
先搜索已有Thesis，再决定 same / update / related / new。
不要每条视频都大量创建新Thesis。

## Phase 11 — Forecast
所有未来判断先作为 forecast Claim，再建立Forecast对象。
必须尽量记录：
made_at / knowledge_cutoff / target / direction / prediction_window /
conditions / resolution_criteria / resolvability。

若时间窗口不明，写 unknown，不要自己补。

## Phase 12 — Contradiction
后置处理。
只有长期结构性张力、多事件/多Thesis反复映射时才创建或更新。
primary/secondary只能用Assessment，并绑定：
Observer + Time + Scope。

## Phase 13 — Heuristic Mining
默认可以是0。
只有发现跨事件可复用的分析规则时创建 Candidate Heuristic。
必须提供 observed_in_arguments 和 source_segments。
禁止直接标 validated。

## Phase 14 — Review Queue
至少识别：
asr_uncertain
numerical_conflict
source_conflict
entity_resolution
unsupported_claim
excessive_inference
forecast_lineage
contradictory_assessment
registry_extension

Critical/High优先放数字、政策时间、核心预测、核心Argument、来源冲突。

## 输出顺序
严格按以下顺序输出：

1. EXECUTIVE EXTRACTION REPORT
2. SOURCES
3. TRANSCRIPT CORRECTIONS
4. SEMANTIC SEGMENTS
5. CLAIMS
6. EVENTS / ACTORS / INDICATORS / POLICIES
7. ASSESSMENTS
8. ARGUMENTS
9. MECHANISMS
10. THESES
11. FORECASTS
12. CONTRADICTIONS（没有则明确写 none）
13. CANDIDATE HEURISTICS
14. REVIEW QUEUE
15. SCHEMA/ONTOLOGY ISSUES FOUND
16. GOLDEN SAMPLE SUMMARY

最后额外回答三个问题：
A. 这期视频最核心的3条推理链是什么？
B. 哪些地方最能体现9527的稳定分析方法，而不是本期事件本身？
C. 哪些结论目前证据不足，绝不能进入“已验证知识”？

不要追求抽取数量。Claim可以多，Thesis应少，Contradiction更少，Heuristic极少。
