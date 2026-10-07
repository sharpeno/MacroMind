你正在执行 MacroMind Phase 1.5B-2：
Human-Reviewed Analytical Continuity Index。

一、目标与边界

在已接受的 Phase 1.5A ContinuityAnnotation 基础上，
新增确定性、只读、可追溯的人工连续性 Relation 和
ExplicitThreadMembershipIndex。

不得重新设计或修改已接受的 ContinuityAnnotation。
不得创建 AnalyticalThread、AnalyticalEpisode 或新的 Frozen Ontology 对象。
不得自动发现关系。

本阶段完成仅表示连续性索引工程完成，不代表 Phase 1.5C、
Phase 1.6、Analyst Model、Analyst Skill 或 Production 已完成。

二、项目与权威输入

工作区：
G:\youhegaojian

工程：
G:\youhegaojian\macro-mind-engine

优先阅读：
phase1/phase1_5a_gate_result.json
phase1/phase1_5a_manifest.json
phase1/phase1_5b1_gate_result.json
phase1/phase1_5b1_manifest.json
phase1/phase1_5b1_evidence/run_002/
src/macromind/audit/continuity.py
src/macromind/audit/models.py
docs/ANALYTICAL_CONTINUITY_HOOK.md
docs/PHASE1_5B1_PATTERN_AGGREGATION.md
tests/audit/test_continuity.py
scripts/verify_phase1_5b1.py

并读取：
G:\youhegaojian\prompt\MacroMind 主设计 02 — Reasoning Continuity.md

Evidence Authority：
Final Gate
> Final Evidence Run
> Manifest / machine artifacts
> actual source / tests / verifier
> final docs
> progress
> agent prose。

搜索现有文件后再判断缺失。不得重建已完成内容。
不依赖 Git；使用 SHA-256 baseline。

已知前置状态：
Phase 1.5A ACCEPTED；
Phase 1.5B-1 ACCEPTED；
Current Gate READY_FOR_PHASE_1_5B_2；
既有测试参考数 394，但必须比较实际测试身份。
Phase 1.5B-2 实现尚未开始。

历史 Gate 中属于当时状态的 flags 不得被改写。
不要重新运行会覆盖历史正式产物的旧阶段 verifier。

三、允许文件范围

仅新增：
src/macromind/audit/continuity_index/**
tests/audit_continuity/**
scripts/verify_phase1_5b2.py
docs/PHASE1_5B2_CONTINUITY_INDEX.md
phase1/phase1_5b2_*

允许修改本次新增文件以修复问题。

不得修改：
已有 src/macromind/audit/*.py；
src/macromind/audit/patterns/**；
已有 tests/audit/**、tests/audit_patterns/**；
已有 verifier、CLI、Schema、Registry、Validator、Compatibility；
已有 Phase 1.0–1.5B-1 正式文件与机器产物；
Frozen、Golden、Continuity Hook；
README 和 MACROMIND_MASTER_STATE.md。

.hermes/** 是外部 operational workspace，不得写入。
如果执行期间发生外部变动，记录具体路径、旧/新哈希及外部来源，
停止相关工作等待用户确认；不得自动白名单整个目录。

四、实现结构与 API

建议新增：
models.py
inputs.py
resolution.py
identity.py
index.py
integrity.py
__init__.py

直接复用已有 ContinuityAnnotation、RelationType、ReviewStatus。
不要通过修改旧 __init__.py 导出新 API。

提供相当于以下职责的 API：

load_input_bundle(
    bundle_bytes,
    explicitly_supplied_artifact_bytes,
    trusted_context_descriptor
) -> verified input

ContinuityIndexer.build(verified_input) -> ContinuityIndexResult

运行时代码不得自动扫描磁盘、访问网络或写输入文件。
输入发现和证据输出仅由 bounded acceptance verifier 完成。

五、持久化输入与 Reference Resolution Snapshot

新增 ContinuityIndexInputBundle，至少包含：
contract_version
data_kind：REAL 或 SYNTHETIC
annotation_payloads
annotation_sources
resolution_snapshot
input_manifest
source_artifact_hashes
deterministic_hash

annotation_sources 为每条原始 payload 保留：
source artifact identity
source artifact SHA-256
稳定 JSON Pointer
payload 完整内容及其哈希。

ReferenceResolutionSnapshot 至少包含：
snapshot_version
authority_id
source_version
references
source_artifact_hashes
semantic_hash

每个已解析引用至少绑定：
ref
source_artifact_id
source_artifact_sha256
source_pointer
declared_object_type，可空。

调用方必须在输入内容之外明确提供可信上下文描述符，
包含权威来源、版本及预期 Snapshot 字节哈希。
Bundle 不得仅凭自身声明成为权威。

SHA-256 证明完整性，不证明权威性。
验证所有声明的来源字节哈希和引用 Pointer 绑定。
引用字符串精确匹配，不自动 trim、猜别名或按前缀判断类型。
同一 ref 的矛盾绑定必须硬失败。
一个 Bundle 只能使用一份上下文，不自动合并上下文。

加载顺序：
1. 校验所有输入字节、预期哈希及版本。
2. 校验可信 Snapshot 描述符及来源绑定。
3. 保存原始 Annotation payload。
4. 从副本加载 Annotation，注入同一份验证后的 known_refs。
5. 调用现有 ContinuityAnnotation 验证。
6. 使用重新计算的解析状态建立索引。

payload 中自带 known_refs 必须拒绝。
自称的 resolution_status 不具有权威性：
保留原声明与重新计算结果，但不得用声明控制解析。

CONFIRMED 缺 reviewer 或缺已解析引用时必须硬失败，
不能降级为候选或跳过该条。
不要修改旧模型来允许无上下文回读。

六、Relation identity 与 Annotation 唯一性

continuity_relation_key =
"relation:" + SHA256(canonical_json(
    [subject_ref, related_ref, relation_type]
))

不得包含：
reviewer、review_status、review_notes、evidence prose、
thread_ref、created_at、文件名、目录、运行 ID 或当前时间。

保留方向，A→B 与 B→A 不自动合并。
这是对早期“thread_ref 进入 Relation identity”建议的明确修正。
不同 Thread 指定必须在同一 Relation 上形成可见冲突。

同一有向引用对的不同 relation_type 可以并存，
不得自动判定冲突。

每条有效 Annotation 必须且只能进入一个 Relation。

第一版拒绝任何重复 annotation_id。
相同 ID 不同内容必须硬失败；完全重复也明确报错，
不得按文件顺序选择、按时间覆盖、去重后隐瞒或自动合并。
区分完全重复与内容冲突的错误代码。
不得发明 Review History 或 revision/event 模型。

七、Review 聚合

派生状态仅由原始状态的存在性决定：

同时有 CONFIRMED 和 REJECTED：CONFLICTED。
有 CONFIRMED 且无 REJECTED：CONFIRMED。
有 REJECTED 且无 CONFIRMED：REJECTED。
只有 UNREVIEWED/CANDIDATE：PENDING。

保存每种原始状态对应的全部 Annotation IDs。
不得多数票、评分、平均或自动裁决。
不得自动提升 CANDIDATE/UNREVIEWED。
不得推测 reviewer 身份或合并 reviewer 别名。

八、Thread assignment 与 Membership

ThreadAssignmentSummary 收集同一 Relation 下所有
Annotation 显式提供的非空 thread_ref，并保留来源和 review_status：

零个不同 Thread：NO_ASSERTION。
一个不同 Thread：UNIQUE_ASSERTION。
多个不同 Thread：CONFLICTED。

不同 Thread 指定即使来自 CANDIDATE/UNREVIEWED，
也保留为冲突并阻止该 Relation 的 Membership。
null 表示未指定，不等于反对。

Membership 必须同时满足：
1. Relation Review 状态 CONFIRMED；
2. 无 CONFIRMED/REJECTED 冲突；
3. 全部非空 Thread 指定只有一个值；
4. 至少一条 CONFIRMED Annotation 本身明确指定该 Thread；
5. subject、related、thread 在同一已验证上下文中解析；
6. 支撑 Annotation、Relation 和解析来源完整。

禁止借用一条未指定 Thread 的确认，
去确认另一条候选 Annotation 中的 Thread 指定。

Membership 行表示明确的 (thread_ref, member_ref)：
membership_id =
"membership:" + SHA256(canonical_json([thread_ref, member_ref]))

合格的 A→B、Thread T 关系支持 (T,A)、(T,B) 两行。
行内保存 supporting_relations、supporting_annotation_ids、
subject/related 角色和 resolution_context_hash。
同一行多个有效支持来源全部保留。

提供 by_thread、by_ref、by_relation 索引。
不能生成 AnalyticalThread 对象。
不能从 A→B、B→C 推导 A→C。
不能将共享 ref、文本相似、共同主题作为关系或 Membership 依据。
不同 Relation 之间不执行冲突传播或 Thread 自动合并。

九、数据模型与输出

至少设计并实现以下独立工程模型：

ContinuityIndexInputBundle
ReferenceResolutionSnapshot
ContinuityRelation
RelationReviewSummary
ThreadAssignmentSummary
ContinuityRelationIndex
ExplicitThreadMembershipIndex
ContinuityIndexResult

ContinuityRelation 至少包含：
continuity_relation_key
subject_ref
related_ref
relation_type
annotation_ids
review_summary
thread_assignment_summary
resolution_summary
membership_blockers

ContinuityRelationIndex 至少包含：
relations_by_key
relation_by_annotation
annotations_by_relation
relations_by_ref
relations_by_ref_pair
thread_assertions_by_relation

pair key 必须基于有序 [subject_ref, related_ref]，
条目中保留这两个引用。
所有相关索引必须完整，不能只保存 examples。

ContinuityIndexResult 至少包含：
index_version
data_kind
annotations
relation_index
membership_index
conflicts
counts
provenance
resolution_context_hash
deterministic_hash

不得将这些工程模型加入 Frozen Ontology、Schema 导出或 Registry。

十、真实输入和 Synthetic 隔离

先搜索现有项目，区分 ContinuityAnnotation 与历史其他 annotation。
不能因为存在 annotation_id 就认定属于本阶段。

正式运行只消费显式清单选择的真实输入。
不要从 Golden 文本、AuditRecord、Pattern 或旧注释自动产生 Annotation。

如果没有明确选择的真实 Annotation，允许生成并记录：
real_input_status = EMPTY_EXPLICIT_INPUT_SET
annotation_payloads = []
real_business_coverage = NOT_DEMONSTRATED

可使用明确声明的空引用上下文：
无引用绑定，不声称拥有任何已解析对象。
它不能让 CONFIRMED Annotation 通过。

零 Annotation 必须产生：
0 Relation
0 review conflicts
0 thread assignment conflicts
0 Membership
确定性空索引
Gate PASS（前提是其余工程检查通过）。

不能在发现非空输入但缺少必需上下文时，
静默改成空输入逃避错误。

Synthetic 测试数据必须明确标记，
与真实结果和真实统计隔离。
不得冒充真实 Analytical Thread。

十一、序列化、语义哈希和 provenance

统一 UTF-8、canonical JSON、稳定 key 排序、LF，
拒绝非有限数字和含糊的重复 JSON keys。

区分：
A. 完整原始/输出字节哈希；
B. 索引语义哈希。

语义投影应明确、可测试：
保留 Annotation identity、引用、关系类型、reviewer、
审查状态、显式 Thread 指定、重算的解析结果、
证据引用及确定性索引；
保留排序后的上下文语义绑定；
排除 created_at、文件位置、临时运行信息以及来源位置 sidecar。
notes/metadata 等原始信息完整保留在 provenance，
不得通过解析它们生成索引或身份。

输入 Bundle 的语义投影按 Annotation ID 和 ref 稳定排序。
Snapshot 的语义哈希也必须对引用记录排列不敏感。
原始上下文文件字节哈希与其语义哈希分开记录。

输入排列或文件改名可以改变原始来源位置/字节哈希，
但不能改变关系索引的语义输出。
相同完整输入三次运行的确定性输出必须一致。

同一 ID 不同原始内容的冲突检查，
不能因为 created_at 等字段不进入语义 identity 就忽略差异。

浅层 frozen 不能作为不可变性证明。
必须验证：
源文件 before/after 字节哈希；
原始 Annotation payload before/after 字节哈希；
输出落盘后重新读取的哈希及结构完整性。
不得原地注入 known_refs 或修改 source payload。

十二、错误与冲突处理

以下硬失败，不返回成功的部分索引：
输入/来源哈希不符；
上下文不可信或版本不支持；
引用绑定无效或矛盾；
重复 Annotation ID；
Annotation ID 与字段不符；
CONFIRMED 缺 reviewer 或未解析；
输入结构损坏；
索引不守恒或 provenance 不可回溯。

以下是正常数据，不是程序失败：
未解析的候选；
PENDING；
REJECTED；
Review conflict；
Thread assignment conflict；
无 thread_ref；
空输入。

正常数据中的冲突不得产生 Membership，但应完整输出。
机器错误报告需包含明确 error_code、相关 ID 和来源 Pointer。
不能猜测修复，也不能自动改写 review_status。

十三、测试要求

完整重跑现有测试，比较 actual collection：
既有测试身份不得减少；
FAILED/ERROR/SKIPPED 均为 0。

新增测试至少覆盖：
Bundle 序列化回读；
同一上下文恢复 CONFIRMED；
伪造 resolution_status 和 known_refs；
错误 context hash、错误来源绑定、嵌套输入篡改；
Relation 不含 reviewer/thread_ref；
方向变化；
同一 pair 多种 relation_type 并存；
不同 reviewer 汇集；
所有 Review 派生组合；
Review conflict 阻止 Membership；
不同 Thread 指定阻止 Membership；
候选指定不能借用其他 Annotation 的确认；
无 Thread、未解析引用；
完全重复和不同内容的重复 ID 硬失败；
全量 Annotation 守恒；
Relation/Annotation 双向索引；
Membership 多来源支持与回溯；
A→B、B→C 不生成 A→C；
不推断 episode 类型；
零真实输入；
Synthetic 与真实结果隔离；
输入顺序、文件名变化；
三次运行确定性；
源字节及 payload 不变；
输出落盘后读取和篡改检测。

新增测试必须全部 PASS，零 fail/error/skip。
运行 Ruff check 和 scoped Ruff format --check。
使用已记录的 workspace-parent Ruff cwd 和显式配置。
只修复本阶段授权文件，不能格式化历史文件。

十四、正式机器产物

在 phase1/ 下生成：
phase1_5b2_input_selection.json
phase1_5b2_input_manifest.json
phase1_5b2_input_bundle.json
phase1_5b2_resolution_snapshot.json
phase1_5b2_annotations.json
phase1_5b2_relation_index.json
phase1_5b2_thread_assignment_summary.json
phase1_5b2_explicit_thread_membership_index.json
phase1_5b2_conflicts.json
phase1_5b2_result.json
phase1_5b2_test_report.json
phase1_5b2_immutability_report.json
phase1_5b2_gate_result.json
phase1_5b2_manifest.json
phase1_5b2_execution_progress.json
phase1_5b2_execution_progress.jsonl
phase1_5b2_evidence/run_NNN/

保存完整原始 Annotation 与重验证结果的区别。
不得仅输出统计而丢掉来源和全量索引。

十五、Verifier 与 Manifest

建立 scripts/verify_phase1_5b2.py。
它仅负责 bounded acceptance，不是 Audit Runner 或产品 CLI。

执行开始前：
记录现有源码、正式产物、Frozen/Golden、外部 operational 文件
和所用执行 Prompt 的 SHA-256 baseline。
不得覆盖旧 baseline。

Verifier 至少：
验证 Phase 1.5A、B-1 Gate 和 Manifest；
核对正式输入选择；
校验可信上下文与来源字节；
运行全部测试、lint、format；
执行真实输入（允许明确的零输入）；
验证守恒、冲突规则和所有正反向索引；
执行三次运行及排列不变性检查；
验证输入不可变性和输出落盘完整性；
验证受保护文件与范围；
生成 Gate、Manifest、进度。

每个 run 保存：
命令 argv/cwd/exit_code；
原始 stdout/stderr；
JUnit；
input_verification.json；
prerequisite_verification.json；
index_integrity.json；
determinism_report.json；
immutability_report.json；
scope_check.json；
本轮正式产物快照。

Manifest 至少：
phase
index_version
input_bundle_semantic_hash
resolution_context_semantic_hash
resolution_context_byte_hash
source_artifact_hashes
real_input_status
real_business_coverage
annotation_count
relation_count
review_conflict_count
thread_assignment_conflict_count
explicit_membership_count
tests
gate_status
generated_artifact_hashes
flags

明确区分字节哈希与语义哈希。
Manifest 不自包含自身哈希。
所有证据路径必须真实存在。
失败、中断及修复前 run 不得覆盖或删除。

十六、验收 Gate

逐项输出以下 Gate、状态和证据路径：

B201 Phase 1.5A 仍 accepted。
B202 Phase 1.5B-1 仍 accepted。
B203 既有测试身份不减少且全部 PASS，零 error/skip。
B204 Bundle 稳定序列化和重建。
B205 CONFIRMED 在同一上下文下回读。
B206 不信任输入 resolution_status。
B207 Relation identity 不含 reviewer。
B208 Relation identity 不含 thread_ref。
B209 同 Relation、不同 reviewer 正确汇集。
B210 CONFIRMED+REJECTED 派生 CONFLICTED。
B211 Review conflict 不生成 Membership。
B212 不同 Thread 指定产生 assignment conflict。
B213 Assignment conflict 不生成 Membership。
B214 无 Thread 不生成 Membership。
B215 未解析引用不生成 Membership。
B216 零 Annotation 产生确定性空输出并通过。
B217 每个有效 Annotation 恰好进入一个 Relation。
B218 Relation/Annotation 双向索引一致。
B219 Membership/Relation/Annotation provenance 可逆。
B220 输入排列不改变语义输出。
B221 同一输入三次运行一致。
B222 源文件和 Annotation payload 字节未改变。
B223 无 LLM/network/NLP/embedding/fuzzy matching。
B224 无 transitive closure。
B225 不创建 AnalyticalThread 对象。
B226 Frozen/Golden/Schema/Registry/Validator/Compatibility 不变。
B227 Phase 1.5C NOT_STARTED。
B228 Phase 1.6 NOT_STARTED。
B229 Analyst Model/Skill NOT_READY。
B230 Production NOT_READY。

另外必须通过：
全部新增测试；
lint/format；
重复 ID 硬失败；
方向保留；
不同 relation_type 不自动冲突；
候选 Thread 指定不借用确认；
Synthetic 隔离；
Phase 1.5A/B-1 全部已有源码、测试和正式产物不变。

所有必要检查通过才可输出：
READY_FOR_PHASE_1_5C

否则输出：
NOT_READY_CONTINUITY_INDEX_BLOCKER

未运行或无法验证的检查不得写 PASS。
发现真实设计缺口，记录 phase1_5b2_design_gap.json，
说明是否阻塞，不得临时放宽规则。

十七、明确禁止

不得执行或生成：
Evidence Delta；
Judgment Delta；
Decision Trigger；
自动 SAME_ISSUE 判断；
AnalyticalThread 自动创建；
AnalyticalEpisode 新 Ontology；
topic/semantic clustering；
embedding、LLM 分类、fuzzy matching；
多数票或 review adjudication；
Method Signal Mining；
Analyst Model、Analyst Skill；
Golden Regression；
Audit Runner；
Phase 1.5C 或 Phase 1.6 实现；
Frozen/Schema/Registry 升级；
自动修复或修改来源数据。

十八、中断恢复

每阶段保存产物、原始输出和进度，然后自动进入下一阶段。
仅遇到必须由用户决定的事项暂停。

若认证、额度或执行错误中断：
尽可能保存已完成项、未完成项、当前验证结果、
最后命令、证据 run 和下一步。
恢复后先检查实际文件与哈希；
不能把 progress 的 complete 或旧 Gate 当作当前代码通过证明。

不要重建已经完成的内容，不要覆盖历史失败证据。

十九、最终交付

使用中文报告：
B-2 completed yes/no；
index version；
真实输入选择及数据性质；
Annotation、Relation、Review conflict、Thread conflict、
Explicit Membership 实际数量；
守恒、双向索引、确定性、持久化回读、不可变性结果；
既有/新增测试 PASS/FAIL/ERROR/SKIP；
B201–B230 逐项结果及证据路径；
受保护文件是否改变；
自动 AnalyticalThread 数量（必须 0）；
Phase 1.5C/1.6 executed=false；
Analyst Model/Skill/Production=NOT_READY；
已完成项、未完成项及最终 Gate。

真实输入为零时明确说明：
工程空输入路径通过，不代表已证明真实连续性业务覆盖。