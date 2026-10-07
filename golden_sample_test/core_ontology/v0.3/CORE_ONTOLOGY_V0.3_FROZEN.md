# MacroMind Core Ontology V0.3 — FROZEN

## 1. Version Metadata

Ontology: MacroMind Core Ontology；Version: **0.3**；Freeze Commit: `CORE-ONTOLOGY-V0.3-FREEZE-COMMIT-1`；Freeze timestamp: `2026-09-27T00:45:14+08:00`。

本文件是正式冻结后唯一的人类可读 Canonical Contract。Schema、Validator、Registry、Migration、Audit Pipeline、Analyst Model 和 Skill Compiler 应引用本文件及配套 JSON，不再自行拼接历史 Patch。机器可读定义与本文件来自同一审计定义，字节哈希以 `freeze_manifest.json` 为准。

## 2. Freeze Status

**FROZEN VERSIONED SEMANTIC CONTRACT**。本状态仅在同目录 freeze_manifest.json 的 formal_freeze_executed=true 且完整性检查 ERROR=0 时有效。

采用 READY_TO_FREEZE_WITH_NONBLOCKING_DEBTS；Core blocker=0；没有新增、删除或改变 Core 语义。Analyst Model、9527 Analyst Skill、MacroMind Core Skill 均 NOT_READY，production_import_ready=false，Codex Phase 1=NOT_STARTED。

## 3. Scope

冻结14种核心类型、定义、15条语义边界及核心 provenance、temporal、Knowledge Cutoff/Information Set、Reasoner/Observer 原则。语义冻结不等于字段 schema、validator 或生产系统已实现。旧 Golden 的缺字段和待核验内容保留其历史状态。

## 4. 14 Core Objects

Source、Claim、Event、StructuralProcess、Actor、Indicator、Policy、Mechanism、Argument、Thesis、Forecast、Contradiction、Assessment、Heuristic。

不得增加或减少；辅助对象的重要性不构成晋升 Core 的依据。

## 5. Core Object Definitions

以下14条 core_definition **逐字复制已接受审计**，未进行定义改写。

### Source

信息载体及其来源身份；真实性评价与载体存在分离。

语义不变量：

- 信息载体及其来源身份；真实性评价与载体存在分离。
- Source ≠ Claim ≠ Reality 来源存在 不等于 来源内容为真。 准确引用 不等于 引用命题为现实事实。
- Truth不得自动从： Premise 传播到： Interpretation Causal Claim Conclusion Thesis 每层需独立证据或明确推理归属。
- 历史分析必须遵守： Knowledge Cutoff Information Set Source Version Content Chronology 不得使用未来信息改写历史判断。
- Source→片段/版本→Claim；独立 Assessment；按命题 origin 去重。

保留债务：D06, D07, D19。覆盖说明：跨版本/转载不是新 Core。

### Claim

带说话者、时间、Population、量词、模态与来源的可断言命题。

语义不变量：

- 带说话者、时间、Population、量词、模态与来源的可断言命题。
- Source ≠ Claim ≠ Reality 来源存在 不等于 来源内容为真。 准确引用 不等于 引用命题为现实事实。
- Truth不得自动从： Premise 传播到： Interpretation Causal Claim Conclusion Thesis 每层需独立证据或明确推理归属。
- 信息不足时： unknown / null / review 优于模型猜测。
- 历史分析必须遵守： Knowledge Cutoff Information Set Source Version Content Chronology 不得使用未来信息改写历史判断。
- 必须区分： analyst statement analyst reasoning model reconstruction model diagnostic human adjudication reasoner_id analysis_context annotation_observer 不得混用。
- Source→片段/版本→Claim；独立 Assessment；按命题 origin 去重。
- Claim 保存说法；Event 的状态和发生证据单列。
- Assessment 指向目标/标准/观察者；不改写原 Claim。

保留债务：D02, D05, D08, D20。覆盖说明：原话、事件与真实性不合并。

### Event

具有相对明确时间边界的状态变化；宣布/生效/发生分别记录。

语义不变量：

- 具有相对明确时间边界的状态变化；宣布/生效/发生分别记录。
- 单个Event不得自动升级为StructuralProcess。 StructuralProcess要求跨时间持续证据。
- Policy为持续状态。 宣布、实施、调整是Event。
- 历史分析必须遵守： Knowledge Cutoff Information Set Source Version Content Chronology 不得使用未来信息改写历史判断。
- Claim 保存说法；Event 的状态和发生证据单列。
- 跨期证据门槛；证据不足保留 Claim/Thesis。
- 以 Event subtype 和 registry 扩展表示通知动作。

保留债务：D05, D06。覆盖说明：通知是已宣布事件，不推出所宣称结果已实现。

### StructuralProcess

跨一段时间持续发生、由多时期观测/时间序列/多事件政策支持的现实结构变化。

语义不变量：

- 跨一段时间持续发生、由多时期观测/时间序列/多事件政策支持的现实结构变化。
- 单个Event不得自动升级为StructuralProcess。 StructuralProcess要求跨时间持续证据。
- 跨期证据门槛；证据不足保留 Claim/Thesis。

保留债务：D12。覆盖说明：需求正例与拒绝升格负例已覆盖；正式正例尚无。

### Actor

具有行动或决策归属的主体；同名地理位置和叙事角色不是主体身份。

语义不变量：

- 具有行动或决策归属的主体；同名地理位置和叙事角色不是主体身份。
- 主体身份与 location/role 关系分开。

保留债务：D07, D20。覆盖说明：国家作为主体与作为地理范围须分开引用。

### Indicator

可重复使用的指标定义及口径；某时值由辅助 Observation 承载。

语义不变量：

- 可重复使用的指标定义及口径；某时值由辅助 Observation 承载。
- Indicator定义变量。 IndicatorObservation记录实际时点观测。 Target Design Capacity Guidance Observed Value 不得混用。
- 信息不足时： unknown / null / review 优于模型猜测。
- 指标定义稳定，观测带 value_kind、period、comparison、role/stage。

保留债务：D11, D16。覆盖说明：flow/stock、价格/量、目标/实际为定义或观测字段。

### Policy

持续有效的制度/政策安排；宣布、调整、执行是相关 Event。

语义不变量：

- 持续有效的制度/政策安排；宣布、调整、执行是相关 Event。
- Policy为持续状态。 宣布、实施、调整是Event。
- 政策持久状态与宣布/实施事件分别记录并关联。

保留债务：D05, D07。覆盖说明：PL01 与 EV05 分开，未来生效不等于未来信息。

### Mechanism

在适用条件下可跨案例复用的因果机制；使用实例不等于共享机制作者。

语义不变量：

- 在适用条件下可跨案例复用的因果机制；使用实例不等于共享机制作者。
- Mechanism是可复用因果模型。 Argument是特定reasoner在特定语境中的实际推理链。
- 机制使用者 不自动成为 机制作者。 unknown不得为了字段完整被补成analyst。
- 机制保留可复用因果结构，Argument 保存本次前提和实际推理边。
- 共享机制和使用实例分别 attribution。

保留债务：D07, D10。覆盖说明：candidate 状态不妨碍类型存在。

### Argument

连接前提、推理边、中间与最终结论的论证；保存表达层、reasoner、距离及脆弱环节。

语义不变量：

- 连接前提、推理边、中间与最终结论的论证；保存表达层、reasoner、距离及脆弱环节。
- Truth不得自动从： Premise 传播到： Interpretation Causal Claim Conclusion Thesis 每层需独立证据或明确推理归属。
- Mechanism是可复用因果模型。 Argument是特定reasoner在特定语境中的实际推理链。
- 必须区分： analyst statement analyst reasoning model reconstruction model diagnostic human adjudication reasoner_id analysis_context annotation_observer 不得混用。
- model_reconstruction 不得直接成为： Analyst Method evidence 除非存在原始explicit或strongly implied证据。
- 机制保留可复用因果结构，Argument 保存本次前提和实际推理边。

保留债务：D11, D17。覆盖说明：model bridge 与 creator shortcut 不同；无需拆分 Core。

### Thesis

对事件、过程、指标组合的持久解释或结构判断，可由后续证据支持/反驳。

语义不变量：

- 对事件、过程、指标组合的持久解释或结构判断，可由后续证据支持/反驳。
- Truth不得自动从： Premise 传播到： Interpretation Causal Claim Conclusion Thesis 每层需独立证据或明确推理归属。
- 持久结构解释不等于时间绑定预测。
- 持久结构解释与带时间/条件的未来判断分别引用。

保留债务：D12, D15。覆盖说明：现实过程本身不重复包装成 Thesis。

### Forecast

主体对未来结果承担的判断：Claim + cutoff + window + modality + resolution criteria，受准入门槛约束。

语义不变量：

- 主体对未来结果承担的判断：Claim + cutoff + window + modality + resolution criteria，受准入门槛约束。
- Scenario表达： 条件分支 / possible branch。 Forecast要求： 主体对未来结果承担判断。 未endorsed的IF-THEN不得自动进入Forecast Ledger。
- 持久结构解释不等于时间绑定预测。
- 历史分析必须遵守： Knowledge Cutoff Information Set Source Version Content Chronology 不得使用未来信息改写历史判断。
- 持久结构解释与带时间/条件的未来判断分别引用。
- Scenario 保留分支；Forecast 必须满足主体判断准入；不以 resolvability 单独替代准入。

保留债务：D03, D15。覆盖说明：条件推演与押注区别；低可判定性不自动排除明确判断。

### Contradiction

跨时持续、多个目标/约束冲突并由多个 Event/Thesis 与互动支持的结构性张力。

语义不变量：

- 跨时持续、多个目标/约束冲突并由多个 Event/Thesis 与互动支持的结构性张力。

保留债务：D13, D20。覆盖说明：仅负例/拒绝自动生成覆盖；不能等同 claim_relation=CONTRADICTS。

### Assessment

特定观察者按标准、时点和信息集对目标作出的评价。

语义不变量：

- 特定观察者按标准、时点和信息集对目标作出的评价。
- Source ≠ Claim ≠ Reality 来源存在 不等于 来源内容为真。 准确引用 不等于 引用命题为现实事实。
- Truth不得自动从： Premise 传播到： Interpretation Causal Claim Conclusion Thesis 每层需独立证据或明确推理归属。
- 模型评价： “推理不足” 不等于： “原子事实为假”。 Assessment真值不得向Reality传播。
- 必须区分： analyst statement analyst reasoning model reconstruction model diagnostic human adjudication reasoner_id analysis_context annotation_observer 不得混用。
- Assessment 指向目标/标准/观察者；不改写原 Claim。
- 评价作用范围和真值不传播原则。

保留债务：D08, D20。覆盖说明：评价不是现实本身；source fidelity 不向因果真实性传播。

### Heuristic

潜在跨事件复用的分析动作或检查规则，具有适用范围、限制和失败条件；可处于候选状态。

语义不变量：

- 潜在跨事件复用的分析动作或检查规则，具有适用范围、限制和失败条件；可处于候选状态。
- AnalystMethodSignal → Repeated Signal → Candidate Pattern → Heuristic → Validated Skill Rule 单次Signal不得直接成为Skill Rule。
- model_reconstruction 不得直接成为： Analyst Method evidence 除非存在原始explicit或strongly implied证据。
- 局部行为观察→候选模式→规则，保留失败与匹配范围。
- Core Heuristic 可候选；Skill 需跨案稳定性、反例与验证。

保留债务：D14, D17。覆盖说明：MethodSignal 是局部观察，SkillRule 是经验证可执行产物；没有降级 Core 的结构证据。

## 6. Core Semantic Boundaries

以下冻结的是语义规则；implementation_status 原样承接审计，needs_validator/needs_field 不表示语义尚未冻结，stable 也不声明生产实现已完成。

| Boundary | 冻结规则 | 实现状态 / 层 | Debt |
| --- | --- | --- | --- |
| B01 Source ↔ Claim | Source→片段/版本→Claim；独立 Assessment；按命题 origin 去重。 | needs_validator / validator | D07, D20 |
| B02 Claim ↔ Event | Claim 保存说法；Event 的状态和发生证据单列。 | needs_validator / validator | D20 |
| B03 Event ↔ StructuralProcess | 跨期证据门槛；证据不足保留 Claim/Thesis。 | stable / validator | D12 |
| B04 Actor ↔ Geography | 主体身份与 location/role 关系分开。 | needs_validator / registry | D07, D20 |
| B05 Indicator ↔ IndicatorObservation | 指标定义稳定，观测带 value_kind、period、comparison、role/stage。 | needs_field / field | D16 |
| B06 Policy ↔ Policy Event | 政策持久状态与宣布/实施事件分别记录并关联。 | stable / field | D05 |
| B07 Mechanism ↔ Argument | 机制保留可复用因果结构，Argument 保存本次前提和实际推理边。 | stable / relation | D10, D11 |
| B08 Thesis ↔ Forecast | 持久结构解释与带时间/条件的未来判断分别引用。 | needs_validator / validator | D03, D15 |
| B09 Scenario ↔ Forecast | Scenario 保留分支；Forecast 必须满足主体判断准入；不以 resolvability 单独替代准入。 | needs_validator / validator | D03 |
| B10 Assessment ↔ Claim | Assessment 指向目标/标准/观察者；不改写原 Claim。 | stable / field | D20 |
| B11 Assessment ↔ Reality | 评价作用范围和真值不传播原则。 | needs_validator / validator | D20 |
| B12 Heuristic ↔ AnalystMethodSignal | 局部行为观察→候选模式→规则，保留失败与匹配范围。 | stable / auxiliary_object | D14, D17 |
| B13 Heuristic ↔ Skill Rule | Core Heuristic 可候选；Skill 需跨案稳定性、反例与验证。 | stable / review | D14 |
| B14 Mechanism ↔ MechanismUsage | 共享机制和使用实例分别 attribution。 | stable / auxiliary_object | D10 |
| B15 Event ↔ Market Infrastructure Event subtype | 以 Event subtype 和 registry 扩展表示通知动作。 | stable / registry | D07 |

### Forecast / Scenario / Thesis 准入与区分

**Forecast**：主体对未来结果承担的判断，以 Claim、KnowledgeCutoff、PredictionWindow、ModalStrength、ResolutionCriteria 为骨架，并保留主体、条件、原模态和来源。window/criteria 不明可降低可判定性并进入 review，不能自行造一个承诺。

**Scenario**：条件—结果或分支树，允许仅讨论可能性，没有必然的概率押注或选支。**Thesis**：跨单个时点的解释/结构判断，由 Argument 和证据支持，可持续修正，不等同过程本体或预测账本项。

最小判别：先问是否有主体的未来判断，再问条件被如何使用、是否选支；若只是枚举“可能 A 也可能 B”，保留场景；若解释的是持久原因/结构意义，建立 Thesis。明确但模糊时间的未来判断可保留低 resolvability，不能以不够好评分为由抹去原判断。

Forecast admission gate：unconditional_forecast、明确 branch_selection 或满足条件承诺与可判定要求的 resolvable_conditional_forecast。Scenario-only gate：没有主体背书/选支或仅条件推演；GS005 C005/SC01 的已验收理由正是 condition_not_endorsed_no_branch_selection。Thesis durability gate：超越单条新闻复述，包含原因/后果/结构意义之一，有来源论证链和后续支持反证接口。

GS003 FC-C026 的两种未来分支及 Addendum 旧准入习惯值得重审，46 条不能整批宣称现代 admission 合格。现有 Scenario 已足以保留它们；D03 是规则对齐而不是新增核心类型。GS005 10 Forecast 与17 Scenario 提供实际区分证据。creator/model/human resolution criteria 和实际评分时间必须隔离。（E08、E09、E24、E34、E43）

### Event / StructuralProcess 证据门槛

Process 至少要求持久、跨时和多时期 Observation/时间序列/多个 Event 或 Policy 的支持；证据数量必须同时满足时间与现实变化语义，重复转载不能凑数。事件重要性、技术突破修辞、连续数天战争都不是自动升格条件。

GS002 的融资结构变化给出明确正向需求，V0.3 已提供对象；旧 JSON 仅在 Thesis/议题中提出，未建正式 Process。GS003–005 的 Process 集合均为空，合理保留负例但暴露 D12。GS005 的单次回收→操作复用→经济复用→商业可行→产业转型可以通过 Event、指标/观测、Argument、Thesis 及将来证据充分的 Process 表达；当前模型补链不是已发生过程。没有发现既不能归 Event 又不能由 Process/Claim/Thesis 表达的现实对象。（E03、E25、E32）

### Argument / Mechanism

Argument 保存本次 premise→inference edge→intermediate conclusion→final conclusion，边标 expression level/reasoner，另保存 inferential distance、creator shortcut 和 most_fragile_step。Mechanism 是可跨案例的因果结构，MechanismUsage 是本案如何使用。

GS002 数量到成本、GS004 时间比到90倍与 RPO 成本化、GS005 回收到降本，都是 Argument 可表达且可标缺陷的跨越；并非因为结论有问题就需要拆 Argument Core。GS004 AR05 显式步骤与模型补边分离，creator shortcut 保留其表达性质，不伪装完整证明。图边数与最长路径不能互代，脆弱环节必须可定位、unknown 可 review。（E06、E16、E18、E19、E26；D10/D11）

## 7. Core Cross-Object Principles

以下 P01–P16 来自本次授权 Prompt，仅折叠换行，不改动规则用词。

### P01 Source / Claim / Reality Separation

Source ≠ Claim ≠ Reality 来源存在 不等于 来源内容为真。 准确引用 不等于 引用命题为现实事实。

### P02 Truth Non-Propagation

Truth不得自动从： Premise 传播到： Interpretation Causal Claim Conclusion Thesis 每层需独立证据或明确推理归属。

### P03 Event / StructuralProcess

单个Event不得自动升级为StructuralProcess。 StructuralProcess要求跨时间持续证据。

### P04 Scenario / Forecast

Scenario表达： 条件分支 / possible branch。 Forecast要求： 主体对未来结果承担判断。 未endorsed的IF-THEN不得自动进入Forecast Ledger。

### P05 Thesis / Forecast

持久结构解释不等于时间绑定预测。

### P06 Indicator / Observation

Indicator定义变量。 IndicatorObservation记录实际时点观测。 Target Design Capacity Guidance Observed Value 不得混用。

### P07 Policy / Policy Event

Policy为持续状态。 宣布、实施、调整是Event。

### P08 Mechanism / Argument

Mechanism是可复用因果模型。 Argument是特定reasoner在特定语境中的实际推理链。

### P09 Mechanism / MechanismUsage

机制使用者 不自动成为 机制作者。 unknown不得为了字段完整被补成analyst。

### P10 Assessment / Reality

模型评价： “推理不足” 不等于： “原子事实为假”。 Assessment真值不得向Reality传播。

### P11 Heuristic Lifecycle

AnalystMethodSignal → Repeated Signal → Candidate Pattern → Heuristic → Validated Skill Rule 单次Signal不得直接成为Skill Rule。

### P12 Unknown > Guess

信息不足时： unknown / null / review 优于模型猜测。

### P13 Temporal Integrity

历史分析必须遵守： Knowledge Cutoff Information Set Source Version Content Chronology 不得使用未来信息改写历史判断。

### P14 Golden Number ≠ Time

GS001、GS002等编号不是时间顺序。 recurrence prior资格必须按： content chronology 判断。

### P15 Reasoner / Observer Separation

必须区分： analyst statement analyst reasoning model reconstruction model diagnostic human adjudication reasoner_id analysis_context annotation_observer 不得混用。

### P16 Model Reconstruction Boundary

model_reconstruction 不得直接成为： Analyst Method evidence 除非存在原始explicit或strongly implied证据。

Heuristic 可处于 candidate；生命周期描述不把已有候选伪装为经过所有验证的规则。技术成功 ≠ 经济成功；Recovery ≠ Cost Decline；Order ≠ Revenue ≠ Cash Receipt；Design Target ≠ Observed Performance。这些区分沿用审计，不能用模型补链填成已证实事实。

## 8. Temporal Integrity

| 轴 | 冻结原则 | Evidence |
| --- | --- | --- |
| knowledge_cutoff | 资格边界按样本信息集保存，未知不可由编号推断。 | E05, E10, E15, E28 |
| asserted_at | 录制时间未知保持 null；publication proxy 与 media offset 单列。 | E23, E05 |
| reference_time | 命题谈论的时期/Population 与实际说话时间分开。 | E02, E07 |
| prediction_window | 可未知；不由评估时点倒填。 | E08, E43 |
| captured_at | 抓取晚不自动意味着全部内容晚；但无历史快照存在修改风险。 | E10, E11 |
| published_at | 整页发布日期不代表所有滚动条目时间。 | E10, E11 |
| SourceVersion | 保留 entry 时间、capture、cutoff eligibility、hash/未知历史修订。 | E10, E11 |
| InformationSet | 按 cutoff 与用途区分 creator reconstruction、外部核验、事后方法比较。 | E15, E28 |
| Forecast resolution time | 标准设定/批准/实际评估时间分开；未批准 model criteria 不评分。 | E08, E43 |
| recurrence chronology | GS003→GS004→GS005→GS002；GS001 无可排序 cutoff；evaluation_time 不重写历史先后。 | E15, E28, E36 |
| Event action times | announced/decided/scheduled/effective/occurred 不合并，EV03 是已知未来安排。 | E05, E12 |

样本 chronology 和当前 metadata 缺口属于证据/债务，不把它们硬编码为通用 validator 实现。公开时间、抓取时间、事件生效时间和预测结算时间不能互代。

## 9. Provenance

现有类型加辅助对象能够回答溯源问题；部分值未知是数据债，不是架构无法表示。

| 问题 | 可表达结构与本次证据 | 限制 |
| --- | --- | --- |
| 谁说的/什么时候说 | Claim.claimant/asserted_by、SourceSegment、asserted_at/proxy；E05、E23 | 录制时间未知不可用发布时间加偏移推算 |
| 基于哪个来源/是否转载 | Source→Version/Segment→ClaimOccurrence；origin family；E10、E11、E29 | 同源传播不增加独立支持；OC130 需内容对齐复核 |
| 模型是否补推理 | Argument expression_level、reasoner/context、DA01；E16、E26 | 模型桥接不归主播方法 |
| 哪次迁移/谁裁决 | migration/finalization metadata、prompt path/hash、decision_origin；E21、E38、E39 | 用户提供的外部裁决有来源记录，非独立身份鉴定 |
| 网页是否改过 | SourceVersion captured_at、历史快照/编辑未知状态；E10、E11 | 能表达风险，不宣称历史网页未修改 |

原始来源、版本、片段、命题、模型推理、迁移与裁决来源必须可追溯；未知的历史网页版本不能冒充已存档版本。证据索引 E01–E43 解析至 freeze_readiness/evidence_catalog.json，其文件 hash 记录在本次输入清单中。

## 10. Knowledge Cutoff / Information Set

冻结 P13/P14：信息资格必须按真实 content chronology、来源版本与用途区分。历史重建、外部核验、事后方法比较使用各自 Information Set；不能用事后 evaluation_time 把晚出现的样本变为历史 prior。GS 编号不是时间顺序。未来生效但 cutoff 前已宣布的决定，与 cutoff 后新信息不同。unknown 时间不自动获得资格；预测结算标准的 creator/model/human 来源和评分许可分开。

## 11. Reasoner / Observer Attribution

analyst statement 由 Claim 与源片段固定；analyst reasoning 由 explicit/strongly_implied 边承载；model reconstruction/diagnostic 由独立 reasoner_id、analysis_context、expression_level 承载；human adjudication 保存 decision_origin、来源 Prompt 哈希和 resolved_at。

GS004 AR05 的模型补链不计入主播方法证据，DA01 与 creator graph 分离。Failure 分开 observed_reasoner_id 与 annotation_observer；标签属于评价者判断，failure_origin 未核时维持 unknown。ME01–03 作者未知与 MU 的使用者已知并不矛盾。字段和辅助层已能表达，归为 D10/D17，不新增“推理观察者” Core。（E16–E19、E26、E35、E38–E39）

## 12. Reality / Claim / Assessment Separation

Source ≠ Claim ≠ Reality；准确引述不等于命题已核实。Assessment 保存目标、标准、时点、信息集与观察者；“论证不足”不是“原子事实为假”。前提的数据可信度不自动传播到因果、解释、结论或 Thesis。源文件披露范围、模型诊断和现实状态分别保留。现实不是此次新增的第15种对象。

## 13. Extension Policy

普通案例只能进行保持核心定义、边界和原则不变的 V0.3-compatible evolution：字段增加、enum 扩展、辅助对象与关系增加、Validator/Registry/Review policy、Analyst layer 和 Runtime 扩展。新增辅助对象不自动获得 Core 地位。实现细节可迭代，不能以字段或枚举名义绕过冻结语义。

## 14. Explicitly Non-Core Objects

SourceVersion, SourceEntry, SourceSegment, SourceFamily, ClaimOccurrence, TranscriptCorrection, IndicatorObservation, InformationSet, ExpectationSnapshot, SourceSegmentAnnotation, Scenario, ReviewQueue, AnalystModel, AnalystMethodSignal, MechanismUsage。

以上可属于 Auxiliary、Governance、Analyst、Temporal、Evidence 等层，具体格式与实现继续演化。它们不替代 Heuristic 等 Core；MechanismUsage 的使用归因不等于共享 Mechanism 的作者。

## 15. Explicitly Not Frozen

- field-level schema details
- enum registries
- semantic_role enum
- recognition_stage enum
- failure taxonomy
- recurrence taxonomy
- validator implementation
- validator rule count
- database schema
- DuckDB / SQLite / Neo4j implementation
- Context Manifest
- retrieval strategy
- Agent Runtime
- Hermes integration
- MCP/API
- Skill format
- Analyst Model format
- UI
- Prompt templates
- Model selection

上述内容允许在 Codex Phase 1、Batch Pilot、Analyst Mining 继续迭代，必须遵守已冻结核心语义。

## 16. Freeze Debt Reference

`freeze_debt_ledger.json` 是审计20项历史债务的逐字节副本。原 nonblocking_debt_count=20 与 D01 记录永远保留；`freeze_debt_status_overlay.json` 是本次新增覆盖层，仅当合同与 hash 校验成功才将 D01 标为 addressed_by_freeze_commit。其余19项不宣称解决。

保留 GS001 summary only、StructuralProcess/Contradiction 正式正例缺失、Heuristic validated Skill 缺失等限制。它们不是通过冻结消失，也不伪造正例。

## 17. Change Policy Reference

`CHANGE_POLICY.md` 是本版本的变更治理政策：普通兼容扩展与 Core Change RFC 分开；Core 改变须 RFC → Review → Migration Plan → Compatibility Plan → V0.4。Frozen artifact 不得静默编辑；错误用独立 errata/RFC，非语义修正也须 patch record、旧新 hash 和 semantic_hash 检查。

审计中 formal_freeze_executed=false 是历史事实，不回写。正式 true 状态仅由新的 manifest 建立。

## 18. Freeze Evidence

权威顺序：最终 Freeze Readiness Audit → Final Accepted Golden → Final Human Adjudication → 最新 Validator/Finalization Log → MA.1 → MA → V0.3.1 → V0.3 → 旧 Prompt/Draft。历史文件只用于溯源，不覆盖最终定义。

| 源 | 文件 | 本次整合用途 |
| --- | --- | --- |
| V02 | G:/youhegaojian/迭代/MacroMind V0.2 Patch.md | Expectation/Population 与评价分离历史 |
| V03 | G:/youhegaojian/迭代/MacroMind Ontology  Schema  Extraction Spec V0.3 Patch.md | StructuralProcess 与时间/来源/推理边界 |
| EX03 | G:/youhegaojian/prompt/V03.MD | V0.3 抽取规范中详细定义 |
| EX031 | G:/youhegaojian/prompt/V0.3.1.md | 样本 Prompt 的 Forecast 准入；不是独立 Patch |
| MA | G:/youhegaojian/迭代/MacroMind V0.3.1-MA.md | Analyst/Shared Knowledge、Reasoner、MechanismUsage |
| MA1 | G:/youhegaojian/迭代/MacroMind V0.3.1-MA.1 Minor Patch.md | 匹配精度、失败观察者、comparison、semantic role |

最终审计：14对象、15边界、20非阻塞债务、0 Core blocker。GS001 是摘要；GS002/003 保留旧最终可用文件；GS004 是 Finalized accepted；GS005 是 Hotfix 1.1 后 accepted，不取代为旧失败 Finalization。

具体输入路径、版本、read_status 和 SHA-256 见 ../../freeze_commit/input_manifest.json；所有正式输出哈希见 freeze_manifest.json，提交记录见 ../../freeze_commit/freeze_commit_log.json。源到 Canonical 的映射见 source_mapping.json。冻结不修改任何 Golden、旧 Patch 或审计产物。
