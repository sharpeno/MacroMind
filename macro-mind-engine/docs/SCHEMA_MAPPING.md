# Schema Mapping

Ontology 0.3 / Schema 0.1.0. Generated from the verified frozen contract and model field metadata.

A = frozen_semantic_requirement; B = validated_auxiliary_contract; C = implementation_extension.
A marks a representation of frozen meaning, not a claim that the frozen contract prescribed this field name or requiredness.
B is sourced from the explicitly non-Core scope, accepted MA.1 auxiliary contract and the execution prompt.
Requiredness, reference encoding, nested shapes and storage types are implementation decisions.
Required nullable fields distinguish missing from null; explicit unknown is `{"state":"unknown"}` or an enum's `unknown`.
None means not recorded/not applicable as specified by the field; empty lists mean no references recorded, not proof of absence.
No validation here establishes truth, forecast admission, chronology eligibility, causal validity or evidence sufficiency.

## Auxiliary reference targets

Source.version_refs → SourceVersion; Source.segment_refs → SourceSegment; Source.family_ref → SourceFamily.
StructuralProcess.observation_refs → IndicatorObservation; Assessment.information_set_ref → InformationSet.
Claim source_refs → Source; ClaimOccurrence supplies version/segment/origin provenance.
MechanismUsage references Mechanism; AnalystMethodSignal remains distinct from Heuristic; Scenario remains distinct from Forecast.
References are opaque strings. Target existence and semantic consistency are Phase 1.3 responsibilities.

## MacroMindObjectBase

Executable Model: `macromind.schema.base.MacroMindObjectBase`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, object_type

Optional Fields: schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Discriminator; each concrete model fixes its registered type. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |

## Source

Executable Model: `macromind.schema.core.Source`

Frozen Definition: 信息载体及其来源身份；真实性评价与载体存在分离。

Frozen Principle Refs: P01, P02, P13
Known Debt Refs: D06, D07, D19

Frozen semantic invariants (verbatim):

- 信息载体及其来源身份；真实性评价与载体存在分离。
- Source ≠ Claim ≠ Reality 来源存在 不等于 来源内容为真。 准确引用 不等于 引用命题为现实事实。
- Truth不得自动从： Premise 传播到： Interpretation Causal Claim Conclusion Thesis 每层需独立证据或明确推理归属。
- 历史分析必须遵守： Knowledge Cutoff Information Set Source Version Content Chronology 不得使用未来信息改写历史判断。
- Source→片段/版本→Claim；独立 Assessment；按命题 origin 去重。

Required Fields: id, title, locator, publisher, published_at, version_refs, segment_refs, family_ref

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, version_refs, segment_refs, family_ref

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| title | frozen_semantic_requirement | Recorded source title | core_objects.json#Source; core_principles.json |
| locator | frozen_semantic_requirement | Carrier locator or original URL | core_objects.json#Source; core_principles.json |
| publisher | frozen_semantic_requirement | Source publisher identity | core_objects.json#Source; core_principles.json |
| published_at | frozen_semantic_requirement | Publication time, not assertion or capture time | core_objects.json#Source; core_principles.json |
| version_refs | frozen_semantic_requirement | Recorded source versions | core_objects.json#Source; core_principles.json |
| segment_refs | frozen_semantic_requirement | Source segments | core_objects.json#Source; core_principles.json |
| family_ref | frozen_semantic_requirement | Origin family; no inferred independent support | core_objects.json#Source; core_principles.json |

## Claim

Executable Model: `macromind.schema.core.Claim`

Frozen Definition: 带说话者、时间、Population、量词、模态与来源的可断言命题。

Frozen Principle Refs: P01, P02, P12, P13, P15
Known Debt Refs: D02, D05, D08, D20

Frozen semantic invariants (verbatim):

- 带说话者、时间、Population、量词、模态与来源的可断言命题。
- Source ≠ Claim ≠ Reality 来源存在 不等于 来源内容为真。 准确引用 不等于 引用命题为现实事实。
- Truth不得自动从： Premise 传播到： Interpretation Causal Claim Conclusion Thesis 每层需独立证据或明确推理归属。
- 信息不足时： unknown / null / review 优于模型猜测。
- 历史分析必须遵守： Knowledge Cutoff Information Set Source Version Content Chronology 不得使用未来信息改写历史判断。
- 必须区分： analyst statement analyst reasoning model reconstruction model diagnostic human adjudication reasoner_id analysis_context annotation_observer 不得混用。
- Source→片段/版本→Claim；独立 Assessment；按命题 origin 去重。
- Claim 保存说法；Event 的状态和发生证据单列。
- Assessment 指向目标/标准/观察者；不改写原 Claim。

Required Fields: id, statement, claimant, asserted_at, reference_time, population, quantifier, modal_strength, scope, source_refs, reasoner_id, analysis_context, annotation_observer

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, reference_time, source_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| statement | frozen_semantic_requirement | Asserted proposition | core_objects.json#Claim; core_principles.json |
| claimant | frozen_semantic_requirement | Speaker or claimant attribution | core_objects.json#Claim; core_principles.json |
| asserted_at | frozen_semantic_requirement | Assertion time, preserved independently of publication | core_objects.json#Claim; core_principles.json |
| reference_time | frozen_semantic_requirement | Time the proposition concerns | core_objects.json#Claim; core_principles.json |
| population | frozen_semantic_requirement | Population the proposition quantifies over | core_objects.json#Claim; core_principles.json |
| quantifier | frozen_semantic_requirement | Original quantifier | core_objects.json#Claim; core_principles.json |
| modal_strength | frozen_semantic_requirement | Original modality, without invented strength | core_objects.json#Claim; core_principles.json |
| scope | frozen_semantic_requirement | Scope of assertion | core_objects.json#Claim; core_principles.json |
| source_refs | frozen_semantic_requirement | Source attribution | core_objects.json#Claim; core_principles.json |
| reasoner_id | frozen_semantic_requirement | Reasoner attribution | core_objects.json#Claim; core_principles.json |
| analysis_context | frozen_semantic_requirement | Analysis context | core_objects.json#Claim; core_principles.json |
| annotation_observer | frozen_semantic_requirement | Observer recording the claim | core_objects.json#Claim; core_principles.json |

## Event

Executable Model: `macromind.schema.core.Event`

Frozen Definition: 具有相对明确时间边界的状态变化；宣布/生效/发生分别记录。

Frozen Principle Refs: P03, P07, P13
Known Debt Refs: D05, D06

Frozen semantic invariants (verbatim):

- 具有相对明确时间边界的状态变化；宣布/生效/发生分别记录。
- 单个Event不得自动升级为StructuralProcess。 StructuralProcess要求跨时间持续证据。
- Policy为持续状态。 宣布、实施、调整是Event。
- 历史分析必须遵守： Knowledge Cutoff Information Set Source Version Content Chronology 不得使用未来信息改写历史判断。
- Claim 保存说法；Event 的状态和发生证据单列。
- 跨期证据门槛；证据不足保留 Claim/Thesis。
- 以 Event subtype 和 registry 扩展表示通知动作。

Required Fields: id, description, announced_at, decided_at, scheduled_at, effective_at, occurred_at, occurrence_status, evidence_refs, actor_refs, policy_refs, subtype

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, evidence_refs, actor_refs, policy_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata, subtype

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| description | frozen_semantic_requirement | Time-bounded state change | core_objects.json#Event; core_principles.json |
| announced_at | frozen_semantic_requirement | Announcement time | core_objects.json#Event; core_principles.json |
| decided_at | frozen_semantic_requirement | Decision time | core_objects.json#Event; core_principles.json |
| scheduled_at | frozen_semantic_requirement | Scheduled time | core_objects.json#Event; core_principles.json |
| effective_at | frozen_semantic_requirement | Effective time | core_objects.json#Event; core_principles.json |
| occurred_at | frozen_semantic_requirement | Occurrence time | core_objects.json#Event; core_principles.json |
| occurrence_status | frozen_semantic_requirement | Recorded occurrence status, not inferred from a Claim | core_objects.json#Event; core_principles.json |
| evidence_refs | frozen_semantic_requirement | Occurrence evidence | core_objects.json#Event; core_principles.json |
| actor_refs | frozen_semantic_requirement | Actors involved | core_objects.json#Event; core_principles.json |
| policy_refs | frozen_semantic_requirement | Related policy states | core_objects.json#Event; core_principles.json |
| subtype | implementation_extension | Implementation extension: event subtype; not a new Core | Phase 1 implementation |

## StructuralProcess

Executable Model: `macromind.schema.core.StructuralProcess`

Frozen Definition: 跨一段时间持续发生、由多时期观测/时间序列/多事件政策支持的现实结构变化。

Frozen Principle Refs: P03
Known Debt Refs: D12

Frozen semantic invariants (verbatim):

- 跨一段时间持续发生、由多时期观测/时间序列/多事件政策支持的现实结构变化。
- 单个Event不得自动升级为StructuralProcess。 StructuralProcess要求跨时间持续证据。
- 跨期证据门槛；证据不足保留 Claim/Thesis。

Required Fields: id, description, period, event_refs, observation_refs, policy_refs, evidence_refs

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, event_refs, observation_refs, policy_refs, evidence_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| description | frozen_semantic_requirement | Persistent real structural change | core_objects.json#StructuralProcess; core_principles.json |
| period | frozen_semantic_requirement | Evidence period | core_objects.json#StructuralProcess; core_principles.json |
| event_refs | frozen_semantic_requirement | Supporting events; no invented minimum count | core_objects.json#StructuralProcess; core_principles.json |
| observation_refs | frozen_semantic_requirement | Cross-period observations | core_objects.json#StructuralProcess; core_principles.json |
| policy_refs | frozen_semantic_requirement | Supporting policy states | core_objects.json#StructuralProcess; core_principles.json |
| evidence_refs | frozen_semantic_requirement | Supporting evidence; sufficiency deferred | core_objects.json#StructuralProcess; core_principles.json |

## Actor

Executable Model: `macromind.schema.core.Actor`

Frozen Definition: 具有行动或决策归属的主体；同名地理位置和叙事角色不是主体身份。

Frozen Principle Refs: none explicitly assigned
Known Debt Refs: D07, D20

Frozen semantic invariants (verbatim):

- 具有行动或决策归属的主体；同名地理位置和叙事角色不是主体身份。
- 主体身份与 location/role 关系分开。

Required Fields: id, display_name, identity_evidence_refs, aliases, location, roles

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, identity_evidence_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata, aliases

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| display_name | frozen_semantic_requirement | Display name distinct from identity | core_objects.json#Actor; core_principles.json |
| identity_evidence_refs | frozen_semantic_requirement | Evidence for acting or decision-making identity | core_objects.json#Actor; core_principles.json |
| aliases | implementation_extension | Implementation extension: recorded aliases without automatic merge | Phase 1 implementation |
| location | frozen_semantic_requirement | Geography distinct from Actor identity | core_objects.json#Actor; core_principles.json |
| roles | frozen_semantic_requirement | Narrative roles distinct from identity | core_objects.json#Actor; core_principles.json |

## Indicator

Executable Model: `macromind.schema.core.Indicator`

Frozen Definition: 可重复使用的指标定义及口径；某时值由辅助 Observation 承载。

Frozen Principle Refs: P06, P12
Known Debt Refs: D11, D16

Frozen semantic invariants (verbatim):

- 可重复使用的指标定义及口径；某时值由辅助 Observation 承载。
- Indicator定义变量。 IndicatorObservation记录实际时点观测。 Target Design Capacity Guidance Observed Value 不得混用。
- 信息不足时： unknown / null / review 优于模型猜测。
- 指标定义稳定，观测带 value_kind、period、comparison、role/stage。

Required Fields: id, name, definition, measurement_scope, unit, source_refs

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, source_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| name | frozen_semantic_requirement | Reusable variable name | core_objects.json#Indicator; core_principles.json |
| definition | frozen_semantic_requirement | Variable definition | core_objects.json#Indicator; core_principles.json |
| measurement_scope | frozen_semantic_requirement | Measurement population and basis | core_objects.json#Indicator; core_principles.json |
| unit | frozen_semantic_requirement | Defined measurement unit | core_objects.json#Indicator; core_principles.json |
| source_refs | frozen_semantic_requirement | Definition sources | core_objects.json#Indicator; core_principles.json |

## Policy

Executable Model: `macromind.schema.core.Policy`

Frozen Definition: 持续有效的制度/政策安排；宣布、调整、执行是相关 Event。

Frozen Principle Refs: P07
Known Debt Refs: D05, D07

Frozen semantic invariants (verbatim):

- 持续有效的制度/政策安排；宣布、调整、执行是相关 Event。
- Policy为持续状态。 宣布、实施、调整是Event。
- 政策持久状态与宣布/实施事件分别记录并关联。

Required Fields: id, description, effective_period, actor_refs, event_refs, source_refs

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, actor_refs, event_refs, source_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| description | frozen_semantic_requirement | Persistent institutional arrangement | core_objects.json#Policy; core_principles.json |
| effective_period | frozen_semantic_requirement | Period of validity | core_objects.json#Policy; core_principles.json |
| actor_refs | frozen_semantic_requirement | Responsible actors | core_objects.json#Policy; core_principles.json |
| event_refs | frozen_semantic_requirement | Separate announcement, implementation or adjustment events | core_objects.json#Policy; core_principles.json |
| source_refs | frozen_semantic_requirement | Policy evidence | core_objects.json#Policy; core_principles.json |

## Mechanism

Executable Model: `macromind.schema.core.Mechanism`

Frozen Definition: 在适用条件下可跨案例复用的因果机制；使用实例不等于共享机制作者。

Frozen Principle Refs: P08, P09
Known Debt Refs: D07, D10

Frozen semantic invariants (verbatim):

- 在适用条件下可跨案例复用的因果机制；使用实例不等于共享机制作者。
- Mechanism是可复用因果模型。 Argument是特定reasoner在特定语境中的实际推理链。
- 机制使用者 不自动成为 机制作者。 unknown不得为了字段完整被补成analyst。
- 机制保留可复用因果结构，Argument 保存本次前提和实际推理边。
- 共享机制和使用实例分别 attribution。

Required Fields: id, statement, causal_structure, applicability_conditions, domain_scope, reasoner_id, analysis_context, annotation_observer, source_refs

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, source_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| statement | frozen_semantic_requirement | Reusable causal structure | core_objects.json#Mechanism; core_principles.json |
| causal_structure | frozen_semantic_requirement | Causal relationships | core_objects.json#Mechanism; core_principles.json |
| applicability_conditions | frozen_semantic_requirement | Conditions for reuse | core_objects.json#Mechanism; core_principles.json |
| domain_scope | frozen_semantic_requirement | Applicable domain | core_objects.json#Mechanism; core_principles.json |
| reasoner_id | frozen_semantic_requirement | Mechanism author; usage analyst is not automatically author | core_objects.json#Mechanism; core_principles.json |
| analysis_context | frozen_semantic_requirement | Context of mechanism attribution | core_objects.json#Mechanism; core_principles.json |
| annotation_observer | frozen_semantic_requirement | Observer recording attribution | core_objects.json#Mechanism; core_principles.json |
| source_refs | frozen_semantic_requirement | Sources for the mechanism | core_objects.json#Mechanism; core_principles.json |

## Argument

Executable Model: `macromind.schema.core.Argument`

Frozen Definition: 连接前提、推理边、中间与最终结论的论证；保存表达层、reasoner、距离及脆弱环节。

Frozen Principle Refs: P02, P08, P15, P16
Known Debt Refs: D11, D17

Frozen semantic invariants (verbatim):

- 连接前提、推理边、中间与最终结论的论证；保存表达层、reasoner、距离及脆弱环节。
- Truth不得自动从： Premise 传播到： Interpretation Causal Claim Conclusion Thesis 每层需独立证据或明确推理归属。
- Mechanism是可复用因果模型。 Argument是特定reasoner在特定语境中的实际推理链。
- 必须区分： analyst statement analyst reasoning model reconstruction model diagnostic human adjudication reasoner_id analysis_context annotation_observer 不得混用。
- model_reconstruction 不得直接成为： Analyst Method evidence 除非存在原始explicit或strongly implied证据。
- 机制保留可复用因果结构，Argument 保存本次前提和实际推理边。

Required Fields: id, premises, steps, intermediate_conclusions, final_conclusion, expression_level, reasoner_id, analysis_context, inferential_distance, creator_shortcuts, most_fragile_step, source_refs

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, premises, steps, source_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| premises | frozen_semantic_requirement | Premise references | core_objects.json#Argument; core_principles.json |
| steps | frozen_semantic_requirement | Attributed inference graph edges | core_objects.json#Argument; core_principles.json |
| intermediate_conclusions | frozen_semantic_requirement | Intermediate conclusion nodes | core_objects.json#Argument; core_principles.json |
| final_conclusion | frozen_semantic_requirement | Final conclusion reference | core_objects.json#Argument; core_principles.json |
| expression_level | frozen_semantic_requirement | Recorded expression level | core_objects.json#Argument; core_principles.json |
| reasoner_id | frozen_semantic_requirement | Argument reasoner | core_objects.json#Argument; core_principles.json |
| analysis_context | frozen_semantic_requirement | Reconstruction versus diagnostic context | core_objects.json#Argument; core_principles.json |
| inferential_distance | frozen_semantic_requirement | Recorded distance and counting basis; edge count is not longest path | core_objects.json#Argument; core_principles.json |
| creator_shortcuts | frozen_semantic_requirement | Creator shortcuts retained as expressed | core_objects.json#Argument; core_principles.json |
| most_fragile_step | frozen_semantic_requirement | Local step refs or paths; unknown allowed | core_objects.json#Argument; core_principles.json |
| source_refs | frozen_semantic_requirement | Argument sources | core_objects.json#Argument; core_principles.json |

## Thesis

Executable Model: `macromind.schema.core.Thesis`

Frozen Definition: 对事件、过程、指标组合的持久解释或结构判断，可由后续证据支持/反驳。

Frozen Principle Refs: P02, P05
Known Debt Refs: D12, D15

Frozen semantic invariants (verbatim):

- 对事件、过程、指标组合的持久解释或结构判断，可由后续证据支持/反驳。
- Truth不得自动从： Premise 传播到： Interpretation Causal Claim Conclusion Thesis 每层需独立证据或明确推理归属。
- 持久结构解释不等于时间绑定预测。
- 持久结构解释与带时间/条件的未来判断分别引用。

Required Fields: id, statement, scope, argument_refs, event_refs, process_refs, indicator_refs, supporting_evidence_refs, counterevidence_refs

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, argument_refs, event_refs, process_refs, indicator_refs, supporting_evidence_refs, counterevidence_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| statement | frozen_semantic_requirement | Persistent explanatory or structural judgment | core_objects.json#Thesis; core_principles.json |
| scope | frozen_semantic_requirement | Scope of structural explanation | core_objects.json#Thesis; core_principles.json |
| argument_refs | frozen_semantic_requirement | Supporting arguments | core_objects.json#Thesis; core_principles.json |
| event_refs | frozen_semantic_requirement | Events explained | core_objects.json#Thesis; core_principles.json |
| process_refs | frozen_semantic_requirement | Processes explained | core_objects.json#Thesis; core_principles.json |
| indicator_refs | frozen_semantic_requirement | Indicator combination explained | core_objects.json#Thesis; core_principles.json |
| supporting_evidence_refs | frozen_semantic_requirement | Supporting evidence | core_objects.json#Thesis; core_principles.json |
| counterevidence_refs | frozen_semantic_requirement | Interface for later counterevidence | core_objects.json#Thesis; core_principles.json |

## Forecast

Executable Model: `macromind.schema.core.Forecast`

Frozen Definition: 主体对未来结果承担的判断：Claim + cutoff + window + modality + resolution criteria，受准入门槛约束。

Frozen Principle Refs: P04, P05, P13
Known Debt Refs: D03, D15

Frozen semantic invariants (verbatim):

- 主体对未来结果承担的判断：Claim + cutoff + window + modality + resolution criteria，受准入门槛约束。
- Scenario表达： 条件分支 / possible branch。 Forecast要求： 主体对未来结果承担判断。 未endorsed的IF-THEN不得自动进入Forecast Ledger。
- 持久结构解释不等于时间绑定预测。
- 历史分析必须遵守： Knowledge Cutoff Information Set Source Version Content Chronology 不得使用未来信息改写历史判断。
- 持久结构解释与带时间/条件的未来判断分别引用。
- Scenario 保留分支；Forecast 必须满足主体判断准入；不以 resolvability 单独替代准入。

Required Fields: id, claim_ref, knowledge_cutoff, prediction_window, modal_strength, resolution_criteria, claimant, conditions, branch_selection, resolution_status, source_refs

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, claim_ref, source_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| claim_ref | frozen_semantic_requirement | Subject's future judgment expressed by Claim | core_objects.json#Forecast; core_principles.json |
| knowledge_cutoff | frozen_semantic_requirement | Knowledge cutoff, not evaluation time | core_objects.json#Forecast; core_principles.json |
| prediction_window | frozen_semantic_requirement | Prediction window; unknown allowed | core_objects.json#Forecast; core_principles.json |
| modal_strength | frozen_semantic_requirement | Original modality | core_objects.json#Forecast; core_principles.json |
| resolution_criteria | frozen_semantic_requirement | Criteria and origin; unknown allowed | core_objects.json#Forecast; core_principles.json |
| claimant | frozen_semantic_requirement | Subject assuming the judgment | core_objects.json#Forecast; core_principles.json |
| conditions | frozen_semantic_requirement | Conditions of judgment | core_objects.json#Forecast; core_principles.json |
| branch_selection | frozen_semantic_requirement | Recorded branch selection without inferring endorsement | core_objects.json#Forecast; core_principles.json |
| resolution_status | frozen_semantic_requirement | Recorded resolution status | core_objects.json#Forecast; core_principles.json |
| source_refs | frozen_semantic_requirement | Original judgment sources | core_objects.json#Forecast; core_principles.json |

## Contradiction

Executable Model: `macromind.schema.core.Contradiction`

Frozen Definition: 跨时持续、多个目标/约束冲突并由多个 Event/Thesis 与互动支持的结构性张力。

Frozen Principle Refs: none explicitly assigned
Known Debt Refs: D13, D20

Frozen semantic invariants (verbatim):

- 跨时持续、多个目标/约束冲突并由多个 Event/Thesis 与互动支持的结构性张力。

Required Fields: id, description, period, conflicting_goals, constraints, event_refs, thesis_refs, interactions

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, event_refs, thesis_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| description | frozen_semantic_requirement | Persistent structural tension, not a claim disagreement edge | core_objects.json#Contradiction; core_principles.json |
| period | frozen_semantic_requirement | Persistence across time | core_objects.json#Contradiction; core_principles.json |
| conflicting_goals | frozen_semantic_requirement | Recorded competing goals | core_objects.json#Contradiction; core_principles.json |
| constraints | frozen_semantic_requirement | Recorded competing constraints | core_objects.json#Contradiction; core_principles.json |
| event_refs | frozen_semantic_requirement | Supporting events | core_objects.json#Contradiction; core_principles.json |
| thesis_refs | frozen_semantic_requirement | Supporting theses | core_objects.json#Contradiction; core_principles.json |
| interactions | frozen_semantic_requirement | Recorded interactions supporting the tension | core_objects.json#Contradiction; core_principles.json |

## Assessment

Executable Model: `macromind.schema.core.Assessment`

Frozen Definition: 特定观察者按标准、时点和信息集对目标作出的评价。

Frozen Principle Refs: P01, P02, P10, P15
Known Debt Refs: D08, D20

Frozen semantic invariants (verbatim):

- 特定观察者按标准、时点和信息集对目标作出的评价。
- Source ≠ Claim ≠ Reality 来源存在 不等于 来源内容为真。 准确引用 不等于 引用命题为现实事实。
- Truth不得自动从： Premise 传播到： Interpretation Causal Claim Conclusion Thesis 每层需独立证据或明确推理归属。
- 模型评价： “推理不足” 不等于： “原子事实为假”。 Assessment真值不得向Reality传播。
- 必须区分： analyst statement analyst reasoning model reconstruction model diagnostic human adjudication reasoner_id analysis_context annotation_observer 不得混用。
- Assessment 指向目标/标准/观察者；不改写原 Claim。
- 评价作用范围和真值不传播原则。

Required Fields: id, observer, target_ref, assessment_kind, criteria, information_set_ref, assessment_time, verification_status, detail

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, target_ref, information_set_ref

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| observer | frozen_semantic_requirement | Observer making this assessment | core_objects.json#Assessment; core_principles.json |
| target_ref | frozen_semantic_requirement | Target evaluated | core_objects.json#Assessment; core_principles.json |
| assessment_kind | frozen_semantic_requirement | Kind of assessment, independent of truth | core_objects.json#Assessment; core_principles.json |
| criteria | frozen_semantic_requirement | Evaluation criteria | core_objects.json#Assessment; core_principles.json |
| information_set_ref | frozen_semantic_requirement | Information available to observer | core_objects.json#Assessment; core_principles.json |
| assessment_time | frozen_semantic_requirement | Evaluation time | core_objects.json#Assessment; core_principles.json |
| verification_status | frozen_semantic_requirement | Attributed verification judgment | core_objects.json#Assessment; core_principles.json |
| detail | frozen_semantic_requirement | Assessment detail, never written back to reality | core_objects.json#Assessment; core_principles.json |

## Heuristic

Executable Model: `macromind.schema.core.Heuristic`

Frozen Definition: 潜在跨事件复用的分析动作或检查规则，具有适用范围、限制和失败条件；可处于候选状态。

Frozen Principle Refs: P11, P16
Known Debt Refs: D14, D17

Frozen semantic invariants (verbatim):

- 潜在跨事件复用的分析动作或检查规则，具有适用范围、限制和失败条件；可处于候选状态。
- AnalystMethodSignal → Repeated Signal → Candidate Pattern → Heuristic → Validated Skill Rule 单次Signal不得直接成为Skill Rule。
- model_reconstruction 不得直接成为： Analyst Method evidence 除非存在原始explicit或strongly implied证据。
- 局部行为观察→候选模式→规则，保留失败与匹配范围。
- Core Heuristic 可候选；Skill 需跨案稳定性、反例与验证。

Required Fields: id, statement, scope, trigger_conditions, required_inputs, analytical_action, allowed_outputs, forbidden_leaps, counterexamples, failure_conditions, status, provenance

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, provenance

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| statement | frozen_semantic_requirement | Reusable analytical action or check | core_objects.json#Heuristic; core_principles.json |
| scope | frozen_semantic_requirement | Applicability scope | core_objects.json#Heuristic; core_principles.json |
| trigger_conditions | frozen_semantic_requirement | Conditions triggering the action | core_objects.json#Heuristic; core_principles.json |
| required_inputs | frozen_semantic_requirement | Inputs needed | core_objects.json#Heuristic; core_principles.json |
| analytical_action | frozen_semantic_requirement | Action to perform | core_objects.json#Heuristic; core_principles.json |
| allowed_outputs | frozen_semantic_requirement | Permitted results | core_objects.json#Heuristic; core_principles.json |
| forbidden_leaps | frozen_semantic_requirement | Unsupported leaps to avoid | core_objects.json#Heuristic; core_principles.json |
| counterexamples | frozen_semantic_requirement | Counterexample evidence | core_objects.json#Heuristic; core_principles.json |
| failure_conditions | frozen_semantic_requirement | Failure conditions | core_objects.json#Heuristic; core_principles.json |
| status | frozen_semantic_requirement | Recorded candidate status; no Skill promotion | core_objects.json#Heuristic; core_principles.json |
| provenance | frozen_semantic_requirement | Evidence and attribution | core_objects.json#Heuristic; core_principles.json |

## SourceVersion

Executable Model: `macromind.schema.auxiliary.SourceVersion`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, source_ref, version_label, content_time, published_at, captured_at, content_sha256, revision_status, source_refs

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, source_ref, source_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| source_ref | validated_auxiliary_contract | Versioned carrier | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| version_label | validated_auxiliary_contract | Recorded version label | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| content_time | validated_auxiliary_contract | Content chronology | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| published_at | validated_auxiliary_contract | Publication time | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| captured_at | validated_auxiliary_contract | Capture time | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| content_sha256 | validated_auxiliary_contract | Hash of captured bytes, unknown if no snapshot | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| revision_status | validated_auxiliary_contract | Historical edits unknown unless evidenced | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| source_refs | validated_auxiliary_contract | Version provenance | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |

## SourceSegment

Executable Model: `macromind.schema.auxiliary.SourceSegment`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, source_ref, source_version_ref, locator, text, content_time

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, source_ref, source_version_ref

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| source_ref | validated_auxiliary_contract | Parent source | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| source_version_ref | validated_auxiliary_contract | Actual source version if recorded | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| locator | validated_auxiliary_contract | Page, offset or entry locator | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| text | validated_auxiliary_contract | Original segment text | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| content_time | validated_auxiliary_contract | Segment-specific time, independent of page date | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |

## SourceFamily

Executable Model: `macromind.schema.auxiliary.SourceFamily`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, description, source_refs, evidence_refs

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, source_refs, evidence_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| description | validated_auxiliary_contract | Common proposition origin, not blanket source independence | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| source_refs | validated_auxiliary_contract | Sources sharing evidenced origin | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| evidence_refs | validated_auxiliary_contract | Origin matching evidence | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |

## ClaimOccurrence

Executable Model: `macromind.schema.auxiliary.ClaimOccurrence`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, claim_ref, source_segment_ref, source_version_ref, origin_family_ref, asserted_at

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, claim_ref, source_segment_ref, source_version_ref, origin_family_ref

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| claim_ref | validated_auxiliary_contract | Canonical proposition | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| source_segment_ref | validated_auxiliary_contract | Specific occurrence location | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| source_version_ref | validated_auxiliary_contract | Recorded source version | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| origin_family_ref | validated_auxiliary_contract | Proposition origin family | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| asserted_at | validated_auxiliary_contract | Occurrence assertion time | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |

## TranscriptCorrection

Executable Model: `macromind.schema.auxiliary.TranscriptCorrection`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, source_segment_ref, original_text, corrected_text, reason, observer, source_refs

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, source_segment_ref, source_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| source_segment_ref | validated_auxiliary_contract | Original transcript segment | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| original_text | validated_auxiliary_contract | Unmodified original text | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| corrected_text | validated_auxiliary_contract | Attributed correction | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| reason | validated_auxiliary_contract | Correction evidence | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| observer | validated_auxiliary_contract | Correction author | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| source_refs | validated_auxiliary_contract | Supporting evidence | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |

## IndicatorObservation

Executable Model: `macromind.schema.auxiliary.IndicatorObservation`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, indicator_ref, value, unit, period, value_kind, comparison_basis, semantic_role, semantic_role_detail, recognition_stage, storage_role, source_refs

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, indicator_ref, source_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| indicator_ref | validated_auxiliary_contract | Reusable indicator definition | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| value | validated_auxiliary_contract | Recorded number or explicit unknown | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| unit | validated_auxiliary_contract | Recorded unit without conversion | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| period | validated_auxiliary_contract | Observation period | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| value_kind | validated_auxiliary_contract | Target/design/guidance/observed category | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| comparison_basis | validated_auxiliary_contract | Reported comparison structure | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| semantic_role | validated_auxiliary_contract | Economic role | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| semantic_role_detail | validated_auxiliary_contract | Other or legacy specialized role | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| recognition_stage | validated_auxiliary_contract | Recorded recognition stage | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| storage_role | validated_auxiliary_contract | Recorded storage role; unknown retained | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| source_refs | validated_auxiliary_contract | Observation sources | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |

## InformationSet

Executable Model: `macromind.schema.auxiliary.InformationSet`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, knowledge_cutoff, purpose, source_version_refs, content_refs, observer

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, source_version_refs, content_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| knowledge_cutoff | validated_auxiliary_contract | Information eligibility boundary | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| purpose | validated_auxiliary_contract | Purpose of information set | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| source_version_refs | validated_auxiliary_contract | Specific source versions | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| content_refs | validated_auxiliary_contract | Available content refs | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| observer | validated_auxiliary_contract | Information-set observer | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |

## ExpectationSnapshot

Executable Model: `macromind.schema.auxiliary.ExpectationSnapshot`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, population, reference_time, captured_at, statement, source_refs

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, reference_time, source_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| population | validated_auxiliary_contract | Population holding the expectation | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| reference_time | validated_auxiliary_contract | Expectation reference time | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| captured_at | validated_auxiliary_contract | Snapshot time | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| statement | validated_auxiliary_contract | Expectation as recorded | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| source_refs | validated_auxiliary_contract | Evidence sources | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |

## Scenario

Executable Model: `macromind.schema.auxiliary.Scenario`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, claim_refs, branches, source_refs, reasoner_id

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, claim_refs, source_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| claim_refs | validated_auxiliary_contract | Original conditional statements | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| branches | validated_auxiliary_contract | Possible branches, without forecast inheritance | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| source_refs | validated_auxiliary_contract | Scenario provenance | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| reasoner_id | validated_auxiliary_contract | Scenario reasoner | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |

## ReviewQueueItem

Executable Model: `macromind.schema.auxiliary.ReviewQueueItem`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, target_ref, field_path, reason, status, observer, decision_origin, resolved_at

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, target_ref

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata, field_path, status

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| target_ref | validated_auxiliary_contract | Target needing review | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| field_path | implementation_extension | Field or nested path needing review | Phase 1 implementation |
| reason | validated_auxiliary_contract | Reason for review | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| status | implementation_extension | Recorded review state; never waives schema validity | Phase 1 implementation |
| observer | validated_auxiliary_contract | Reviewer attribution | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| decision_origin | validated_auxiliary_contract | Decision source | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| resolved_at | validated_auxiliary_contract | Resolution time | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |

## AnalystMethodSignal

Executable Model: `macromind.schema.auxiliary.AnalystMethodSignal`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, analyst_id, signal_type, statement, source_segment_refs, argument_refs, claim_refs, domain, expression_level, transferability, recurrence_status, recurrence_match, matched_prior_signal_refs, matched_scope, recurrence_evidence, reasoner_id, analysis_context, annotation_observer, observed_reasoner_id, observed_action, failure_assessment, failure_type, assessment_confidence

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, source_segment_refs, argument_refs, claim_refs, matched_prior_signal_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| analyst_id | validated_auxiliary_contract | Analyst being observed | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| signal_type | validated_auxiliary_contract | Type of local behavior | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| statement | validated_auxiliary_contract | Observed local behavior | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| source_segment_refs | validated_auxiliary_contract | Original expression evidence | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| argument_refs | validated_auxiliary_contract | Related arguments | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| claim_refs | validated_auxiliary_contract | Related claims | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| domain | validated_auxiliary_contract | Recorded domain | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| expression_level | validated_auxiliary_contract | Expression strength | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| transferability | validated_auxiliary_contract | Recorded transferability | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| recurrence_status | validated_auxiliary_contract | Recorded recurrence, no counting or chronology inference | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| recurrence_match | validated_auxiliary_contract | Precision of match, separate from frequency | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| matched_prior_signal_refs | validated_auxiliary_contract | Recorded prior matches; no eligibility assertion | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| matched_scope | validated_auxiliary_contract | Exact sub-operation matched | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| recurrence_evidence | validated_auxiliary_contract | Evidence supporting recorded recurrence | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| reasoner_id | validated_auxiliary_contract | Reasoner attribution | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| analysis_context | validated_auxiliary_contract | Analysis context | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| annotation_observer | validated_auxiliary_contract | Annotator distinct from observed reasoner | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| observed_reasoner_id | validated_auxiliary_contract | Observed reasoner for failure analysis | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| observed_action | validated_auxiliary_contract | Action being assessed | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| failure_assessment | validated_auxiliary_contract | Observer's failure assessment | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| failure_type | validated_auxiliary_contract | Failure categories, None if not applicable | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| assessment_confidence | validated_auxiliary_contract | Confidence in failure assessment, not original assertion confidence | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |

## MechanismUsage

Executable Model: `macromind.schema.auxiliary.MechanismUsage`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, mechanism_ref, analyst_id, reasoner_id, usage_context, expression_level, source_refs, argument_refs, domain_scope, confidence

Optional Fields: object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

Auxiliary References / reference-bearing fields: provenance_refs, mechanism_ref, source_refs, argument_refs

Implementation Extensions: id, object_type, schema_version, ontology_version, created_at, provenance_refs, metadata

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable opaque identity. Display names do not establish identity. | Phase 1 implementation |
| object_type | implementation_extension | Registered object discriminator. | Phase 1 implementation |
| schema_version | implementation_extension | Implementation schema version, independent of ontology. | Phase 1 implementation |
| ontology_version | implementation_extension | Referenced frozen ontology version. | Phase 1 implementation |
| created_at | implementation_extension | Record creation time; None means not recorded. | Phase 1 implementation |
| provenance_refs | implementation_extension | Provenance record references; empty means no refs recorded. | Phase 1 implementation |
| metadata | implementation_extension | Implementation metadata, never a substitute for canonical fields. | Phase 1 implementation |
| mechanism_ref | validated_auxiliary_contract | Shared mechanism used | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| analyst_id | validated_auxiliary_contract | Using analyst | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| reasoner_id | validated_auxiliary_contract | Reasoner of this usage only | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| usage_context | validated_auxiliary_contract | Usage context | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| expression_level | validated_auxiliary_contract | Recorded usage expression | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| source_refs | validated_auxiliary_contract | Usage evidence | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| argument_refs | validated_auxiliary_contract | Arguments using mechanism | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| domain_scope | validated_auxiliary_contract | Domain of use | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |
| confidence | validated_auxiliary_contract | Recorded confidence, no inference | Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract |

## ComparisonBasis

Executable Model: `macromind.schema.common.ComparisonBasis`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: comparison_type, baseline_value, baseline_period, baseline_source_ref, delta_value, delta_unit

Optional Fields: none

Auxiliary References / reference-bearing fields: baseline_source_ref

Implementation Extensions: 

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| comparison_type | validated_auxiliary_contract | Reported comparison category, including unknown. | MA.1 comparison_basis |
| baseline_value | validated_auxiliary_contract | Reported baseline; never calculated. | MA.1 comparison_basis |
| baseline_period | validated_auxiliary_contract | Baseline period independent of observation period. | MA.1 comparison_basis |
| baseline_source_ref | validated_auxiliary_contract | Baseline provenance, None when unrecorded. | MA.1 comparison_basis |
| delta_value | validated_auxiliary_contract | Reported delta, not inferred from values. | MA.1 comparison_basis |
| delta_unit | validated_auxiliary_contract | Preserve percent versus percentage point or original ambiguity. | MA.1 comparison_basis |

## ReasoningStep

Executable Model: `macromind.schema.common.ReasoningStep`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, premises, conclusion_ref, statement, expression_level, reasoner_id, analysis_context, source_refs

Optional Fields: none

Auxiliary References / reference-bearing fields: premises, conclusion_ref, source_refs

Implementation Extensions: id

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Stable step identifier within an Argument. | Phase 1 implementation |
| premises | frozen_semantic_requirement | Premise node references. | Argument/P08 |
| conclusion_ref | frozen_semantic_requirement | Conclusion node reference; None when unrecorded. | Argument/P08 |
| statement | frozen_semantic_requirement | Recorded inference, without judging its validity. | Argument/P08 |
| expression_level | frozen_semantic_requirement | Attribution of expression, separate from truth. | P15/P16 |
| reasoner_id | frozen_semantic_requirement | Reasoner of this specific edge; never inherited by inference. | P15 |
| analysis_context | frozen_semantic_requirement | Context of this edge. | P15 |
| source_refs | frozen_semantic_requirement | Evidence for this edge. | P01/P15 |

## ResolutionCriteria

Executable Model: `macromind.schema.common.ResolutionCriteria`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: description, reasoner_id, analysis_context, set_at, approved_at, evaluation_time, scoring_permitted

Optional Fields: none

Auxiliary References / reference-bearing fields: none

Implementation Extensions: 

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| description | frozen_semantic_requirement | Original or explicitly attributed resolution criterion. | Forecast/P13 |
| reasoner_id | frozen_semantic_requirement | Criterion originator; creator/model/human kept distinct. | P15 |
| analysis_context | frozen_semantic_requirement | Criterion origin context. | P15 |
| set_at | frozen_semantic_requirement | Time criterion was set. | P13 |
| approved_at | frozen_semantic_requirement | Approval time, independent of evaluation time. | P13 |
| evaluation_time | frozen_semantic_requirement | Actual evaluation time. | P13 |
| scoring_permitted | frozen_semantic_requirement | Recorded scoring permission; no automatic approval. | Forecast temporal contract |

## ScenarioBranch

Executable Model: `macromind.schema.common.ScenarioBranch`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: id, condition, outcome

Optional Fields: child_branch_refs

Auxiliary References / reference-bearing fields: child_branch_refs

Implementation Extensions: id, child_branch_refs

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| id | implementation_extension | Local branch identifier. | Phase 1 implementation |
| condition | validated_auxiliary_contract | Branch condition, with no implied endorsement. | B09 |
| outcome | validated_auxiliary_contract | Possible consequence, not a forecast commitment. | B09 |
| child_branch_refs | implementation_extension | Optional branch-tree links. | Phase 1 implementation |

## TimeReference

Executable Model: `macromind.schema.common.TimeReference`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: text

Optional Fields: start, end, source_ref

Auxiliary References / reference-bearing fields: source_ref

Implementation Extensions: text, start, end, source_ref

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| text | implementation_extension | Original temporal expression; no inferred exact date. | Phase 1 implementation |
| start | implementation_extension | Recorded start, if known. | Phase 1 implementation |
| end | implementation_extension | Recorded end, if known. | Phase 1 implementation |
| source_ref | implementation_extension | Evidence for this temporal expression. | Phase 1 implementation |

## UnknownValue

Executable Model: `macromind.schema.common.UnknownValue`

Non-Core/base/nested implementation mapping. No new Core definition.

Required Fields: 

Optional Fields: state

Auxiliary References / reference-bearing fields: none

Implementation Extensions: state

| Executable field | Origin | Requirement / representation | Source |
| --- | --- | --- | --- |
| state | implementation_extension | Explicit known-but-undetermined value. | Phase 1 implementation |
