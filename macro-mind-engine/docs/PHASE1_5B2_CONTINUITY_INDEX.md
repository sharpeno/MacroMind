# Phase 1.5B-2：显式人工关系与论题成员索引

本阶段为已有人工连续性 Annotation 建立可查、可回溯的登记簿。它记录谁确认、谁拒绝、谁明确指定了哪个 Thread；不从文字相似性推断关系，不替人消解分歧，也不创建 AnalyticalThread 对象。

## 输入与可信边界

`load_input_bundle(bundle_bytes, explicitly_supplied_artifact_bytes, trusted_context_descriptor)` 接收原始 JSON 字节、显式提供的来源字节映射和独立提供的可信上下文。Bundle 的 `resolution_snapshot` 是映射中的 artifact ID。没有磁盘扫描、网络检索或默认已知引用。可信描述符固定 authority_id、source_version、snapshot_sha256、data_kind；它由调用方负责授权，不能从不可信 Bundle 自我声明得到。

哈希回答“内容是否改变”；外部授权回答“可以依赖哪份引用目录”。快照将精确 ref 绑定至来源 artifact、SHA-256、JSON Pointer。引用类型只作显式声明保留，不依据前缀或自然语言猜测。空快照不能证明任何实际引用存在。

严格 JSON 拒绝重复键、非有限数和无效 UTF-8；每份来源都核验字节哈希。原始 payload 与来源 Pointer 的值核对后原样保留。输入中的 known_refs 被拒绝；resolution_status 保留为原始声明，并用同一快照重新计算。CONFIRMED 不合法即整体失败，不能降级为候选。

VerifiedInput 只保存不可变 bytes 与 tuple，build 每次重新校验；不把 Pydantic frozen 当作深层不可变证明。来源文件只读，运行时不接触文件系统。

## 聚合规则及理由

Relation key 是有方向的 `[subject_ref, related_ref, relation_type]` 的规范 JSON SHA-256，前缀 relation:。reviewer 和 thread_ref 不参与该编号，因此两个人对同一关系的意见能汇集到一起。A→B 与 B→A 不同；同一对引用不同关系类型可以并存，不自动成为冲突。

原始 Annotation ID 一律唯一。完全重复也报错；同 ID 不同原始内容（包括时间、备注变化）另报内容冲突，不采用最后写入覆盖，不暗造 review history。

有确认且有拒绝就是 CONFLICTED；只有确认侧是 CONFIRMED；只有拒绝侧是 REJECTED；其余 PENDING。人数不用于投票。所有非空 Thread 指定都收集，包括候选与未解析指定：无指定为 NO_ASSERTION，一个为 UNIQUE_ASSERTION，多个为 CONFLICTED。null 表示没表态，不表示反对。

Membership 同时要求：关系已确认且无拒绝冲突；唯一 Thread 指定；至少一条已确认 Annotation 自己明确指定该 Thread；两个端点和 Thread 都在同一上下文解析；支持来源完整。因此“已确认但未指定 Thread”的意见，不能替另一条候选 Thread 指定背书。

合格 A→B,T 只产生 (T,A)、(T,B) 两行，按该二元组去重，同时保留全部支持关系、Annotation、端点角色和上下文哈希。A→B、B→C 不自动补出 A→C；一条关系有冲突不会传播到其他独立关系。

## 序列化与验收

UTF-8、LF、排序键的规范 JSON 区分字节 SHA-256 与语义 SHA-256。Annotation 语义投影仅含 ID、两端、类型、reviewer、review_status、thread_ref、重新解析状态、evidence_refs；备注、时间和 metadata 在原文及 provenance 中保留，但不改变语义编号和索引哈希。来源顺序和文件标签可以改变 provenance，不改变语义输出。

输出回读既核验字节与语义哈希，也检查反向索引、Membership 支持，并重新对照可信输入构造完整结果。人工测试还直接断言具体预期，避免只靠同一算法重复运行自证。

正式执行：在 workspace-parent 使用 `.venv/Scripts/python.exe macro-mind-engine/scripts/verify_phase1_5b2.py`（Python 由 engine 的虚拟环境提供）。每次新增 run_NNN，不覆盖失败证据。pytest 全量执行；既有 394 项身份与 B-1 run_002 JUnit 比较；Ruff 使用 workspace-parent cwd 和显式 config，仅格式化新阶段文件。

B201–B230 的逐项机器结论、原始命令、stdout/stderr、JUnit、输入检查、确定性、范围和不可变性证据见 `phase1/phase1_5b2_gate_result.json` 及 Manifest 指向的 evidence_run。本文不是通过证明，最终状态以实际运行证据为准。

## 真实输入范围

正式 verifier 对 baseline 中既有 phase1/Golden JSON 作有界来源核查，寻找包含 subject_ref、related_ref、relation_type、review_status 的显式记录；旧 annotation_id 本身不能成为连续性输入。发现候选或无法读的来源会阻止静默选择空输入。测试夹具不混入真实结果。

若核查后明确选择空集，输出 REAL / EMPTY_EXPLICIT_INPUT_SET，所有真实数量为 0，业务覆盖为 NOT_DEMONSTRATED。含义是登记簿可以处理没有记录的情况，绝不是已证明真实研究材料的连续性。非空行为由标注 SYNTHETIC 的测试验证。选入真实人工标注及其授权引用目录仍需后续独立工作。

## 与系统最初目标对照

《核心主旨》希望建立可审计的宏观分析方法基础：保存历史材料、分清当时能知道的证据、还原分析方法，让不同 Analyst Skills 独立分析并保留分歧。B-2 为“明确证据关系、人工意见可追溯”补基础；没有提前把工程错误模式当作分析师方法，没有用自动归题替代人工判断，方向与这个目标一致。

| 层级 | 当前证据与边界 |
|---|---|
| 原始资料、Frozen v0.3、Schema/Registry | 前序阶段已有；本阶段保护，不重写 |
| Validator、Legacy Compatibility | 前序已有实现与测试；本阶段只跑回归 |
| 1.5A 审计标准化 | 26,220 条已有工程记录，核验原验收清单 |
| 1.5B-1 工程模式聚合 | 已有工程模式索引，不能视作分析方法挖掘 |
| 1.5B-2 人工连续性索引 | 本阶段实现及正式验收；真实覆盖须另行看输入数量 |
| 1.5C、1.6 | NOT_STARTED；本阶段不执行 Runner 或 Golden Regression |
| 真实 Episode 批处理、方法信号、启发式审查 | 后续工作，尚未由本阶段证明 |
| Analyst Model / Skill / Production | NOT_READY |

主要进度风险是长期停留在工程设施建设，却迟迟不使用真实人工标注与研究材料验证价值。建议按原路线完成 1.5C/1.6 后安排有明确样本和成功标准的小批真实研究验证，再推进方法信号和 Analyst Skill；不能拿测试数量代替业务效果。

早期系统大纲用于核对长期方向，不能覆盖当前 Frozen v0.3 与阶段边界。历史 README / master 状态页可能滞后；本次不在授权路径外修改，可后续单独统一文档口径。
