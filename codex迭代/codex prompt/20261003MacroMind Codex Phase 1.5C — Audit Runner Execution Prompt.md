# MacroMind Codex Phase 1.5C — Audit Runner Execution Prompt

版本：1.0；制定日期：2026-10-03（Asia/Shanghai）。
性质：下一阶段执行指令。本文件的制定不代表已经执行或验收 Phase 1.5C。

## 一、任务目标与产品方向

执行 Phase 1.5C：Audit Runner、Audit Report、Self-stability、Cross-run comparison。
把已验收的 Validator、Legacy Compatibility、Audit Normalization、Engineering Pattern Aggregation 和 Human-reviewed Continuity Index，通过明确输入、固定步骤、可信文件和完整运行证据连接起来。

长期产品目标：从新闻、数据与分析者历史材料中提炼可替换的分析框架；新材料进入后可调用 9527 或其他人的框架分析；展示证据、显式分析步骤与结论；与分析者后续观点及现实发展分别验证，并保留框架版本。1.5C 只建设上述能力需要的审计执行底座，不能宣称已经能执行分析者框架。

本阶段成功意味着：指定输入后，一条命令能产生可回读、可追溯、不改源文件的审计包；执行失败与数据问题分开；相同输入业务输出稳定；两个明确指定的已完成运行可以作有边界的工程比较。

## 二、依据和当前基线

工作区：G:/youhegaojian
工程：G:/youhegaojian/macro-mind-engine
Frozen：G:/youhegaojian/golden_sample_test/core_ontology/v0.3

先完整读取本文件，再检查适用的 AGENTS.md、当前文件与修改状态，以及以下依据：
- 核心主旨.md
- codex迭代/MacroMind Codex Phase 1 Engineering Plan.md（Phase 1.5、1.6 及后续路线）
- prompt/MacroMind 主设计 02 — Reasoning Continuity.md（B1-OBS-01/02/03、后续路线）
- docs/PHASE1_5B2_CONTINUITY_INDEX.md
- phase1/phase1_5a_*、phase1_5b1_*、phase1_5b2_* 的正式 Gate、Manifest、输入选择及最新证据。

制定本 Prompt 时实查：B-2 Gate=READY_FOR_PHASE_1_5C；Manifest 的 228 个文件哈希一致；run_004 的 394 个既有测试和 83 个新增测试通过，共 477，fail/error/skip=0。
B-2 真实连续性输入为 EMPTY_EXPLICIT_INPUT_SET，业务覆盖 NOT_DEMONSTRATED，不得当作非空真实业务覆盖。
A 的 26,220 条是工程记录，不是新闻数或分析方法数。B-1 的 281 个 Pattern 也是工程模式。
这些数字只是待复核基线，不是本轮自动通过证明。

执行前重新核验前序 Gate、Manifest、JUnit 身份与实际文件。先找已有的 1.5C 文件和中断记录，从未完成处续接，不重建、不覆盖旧 baseline 或失败 run。
若没有 Git，采用文件清单、SHA-256 和可读差异报告；不能因为没有 Git 就省略修改审查。

## 三、修改范围与保护边界

允许新增和修改：
- src/macromind/audit/runner/**
- src/macromind/cli/audit.py
- tests/audit_runner/**（使用不与旧测试冲突的文件名）
- scripts/verify_phase1_5c.py
- docs/PHASE1_5C_AUDIT_RUNNER.md
- phase1/phase1_5c_*

唯一允许修改的既有源码：src/macromind/cli/main.py。
限于导入及注册新 audit 命令，必要时更正顶层帮助说明；旧命令参数、退出码和行为必须保留，业务逻辑放新文件。保存该文件修改前字节、SHA-256、修改后哈希和逐行 diff，验证改动仅涉及注册。注册位置必须兼容 console entry point 与 python -m 调用。

其他既有源码、测试、CLI 行为、前序验证脚本、前序正式产物、Frozen、Schema、Registry、Validator、Compatibility、Golden 输入均受保护。禁止修改旧模块以适配新 Runner。
前序 Manifest 如包含获准修改的 main.py：先记录修改前精确通过，修改后如实报告唯一批准的集成差异及旧命令回归；不得重写旧 Manifest 或把修改后哈希不一致说成逐字未变。除此之外的历史差异均需解释、阻断，不得扩展豁免。

.hermes/**、其他外部 operational 文件只读；先记录 baseline。执行期间出现未知变更，保存准确路径和前后哈希，停止受影响部分，向用户确认。旧阶段的单文件豁免不自动适用。

不修改 README、主状态页、pyproject.toml，不引入依赖。正式验证的 Runner 输出必须位于 phase1_5c_* 授权目录。产品 CLI 的用户输出根目录须显式提供。
如果确有无法绕开的接口设计缺口，保存 phase1_5c_design_gap.json，说明证据、影响和最小方案；不临时放宽受保护语义。

## 四、使用现有真实接口

先读取实现与测试，不按本节摘要猜测内部字段：
- validation.ValidatorEngine(contract_root, registry_root).validate(value, context)
- validation.ValidationContext
- compatibility.CompatibilityEngine(...).adapt(...) / 已有文件读取适配接口
- audit.AuditInputArtifact、AuditInputBundle、AuditNormalizer.normalize_bundle(...)
- audit.patterns.PatternAggregator、validate_conservation
- audit.continuity_index.load_input_bundle、ContinuityIndexer.build、load_result_bytes、verify_result

Runner 使用库接口，不能调用前序 verify_phase*.py 充当业务管线，也不能触发它们写回旧目录。
不向 Frozen Ontology 或 Registry 注册 Runner 工程模型。
B-2 仍只接收明确人工 Annotation 和外部可信 Snapshot，不从审计记录、Pattern、Golden 文本推导 Annotation。

## 五、统一执行入口与明确输入

提供可测试的 Python API，并注册真实 CLI：
macromind audit run --request <request.json> --output-root <dir>
macromind audit compare --left <completed-run-dir> --left-manifest-sha256 <sha256> --right <completed-run-dir> --right-manifest-sha256 <sha256> --output-root <dir>

按现有 Typer 风格实现；写明命令实际完整示例。非空 continuity 使用单独的 --trusted-context <descriptor.json> 参数（Python API 同样单独传入），不能让不可信 Bundle 自行提供授权。compare 的两个 manifest 预期哈希由调用方显式提供，不能从待核验 manifest 自我读取作为预期值。

AuditRunRequest 至少明确：
request_version、data_kind=REAL|SYNTHETIC、input_mode、显式来源清单及预期字节 SHA-256、contract/registry 根路径与内容清单哈希、版本、ValidationContext、可选 continuity 输入及其来源清单、运行策略版本。
所有相对输入路径以 request 所在目录解析，不依赖 cwd；可信目录的清单哈希包含排序后的相对路径及文件哈希，不把绝对位置纳入语义身份。

input_mode 采用互斥、有明确契约的三种方式：
1. CANONICAL：已结构化、可由现有 Validator 接收的输入。只验证，不适配。
2. LEGACY：明确来源交给已有 Compatibility 引擎，保留完整适配结果、隔离与损失，再使用既有验证结果/接口完成规范视图的验证。
3. ENGINEERING_REPORTS：显式选择已有工程报告，按 A 的支持类别构造 AuditInputBundle，不假称本次重新验证了原始 Golden。

首版每次 CANONICAL/LEGACY run 接受一个主输入；ENGINEERING_REPORTS 可接受多份显式报告。多案例调度、并发队列、文件监听不是本阶段内容。
不得根据文件名猜 input_mode，不得从目录自动递归收集业务输入。格式检测仅沿用已有 Compatibility 的能力。相同内容重复输入必须明确拒绝或按已文档化的精确规则处理，不能隐性重复计数。

没有 continuity 输入时记录 NOT_PROVIDED，生成明确空集和零绑定的 B-2 输入，不声称解析了真实引用；有非空输入但缺可信上下文时必须报错，不能改为空集。
可信 descriptor 必须由调用方在 Annotation Bundle 之外显式给出并固定 snapshot byte hash、authority、version、data_kind；Runner 不得从不可信内容构造信任依据。
REAL/SYNTHETIC 不得混合或替换标签。无论有多少审计记录，真实 Annotation 为零时，连续性业务覆盖仍 NOT_DEMONSTRATED。

## 六、执行顺序与来源完整性

按固定依赖次序执行：
1. 严格读取 request、可信描述符和显式来源字节，检查版本、重复 JSON keys、非有限值、预期哈希、路径及来源重复。
2. 校验 Frozen/Registry，并捕获输入字节、版本和 ValidationContext；不得用运行日期替代内容时间/knowledge_cutoff，不补猜缺失历史上下文。
3. 根据 input_mode 执行已有适配/验证或接受已核验报告。CANONICAL 的 adaptation 阶段为 NOT_APPLICABLE；ENGINEERING_REPORTS 的原始适配/验证阶段为 NOT_APPLICABLE，不能写 PASS。
4. 将本轮真正生成或明确输入的工程报告按 A 契约标准化。
5. 按 B-1 原契约聚合，验证 disposition 守恒和完整 occurrence 索引。
6. 独立按 B-2 契约验证和构建连续性索引。
7. 生成确定性 review queue、报告、完整 provenance 与源文件不可变性检查。
8. 落盘回读、校验所有产物与索引，最后提交 completed run manifest。

Compatibility 已有 validation_report 时，先核对它的上下文与本轮要求。不可同时将同一报告导入两次。若现有适配接口不支持用户指定上下文，不得假称已应用：必要时由 Runner 显式调用 Validator 重验证，并区分原适配内嵌报告与本轮权威验证报告的用途及哈希。报告规范化计数只能按声明的来源清单发生一次。
不为了 Runner 改变现有 normalizer 的“不支持形状”行为。unsupported_inputs、quarantine、loss、indeterminate 等不得丢弃或偷偷补全。
完整来源链至少支持：Runner issue/review item → 原模块结果 → source artifact + hash + JSON Pointer；适配后对象还可经 mapping ledger 回查原始材料。
不能把不能追溯的摘要包装成完整 evidence。全量索引与来源保留，examples 不能代替明细。

## 七、状态、错误和退出码

区分三条独立状态轴，并设计模型而非自由文本：
- execution_status：RUNNING / COMPLETED / FAILED / INTERRUPTED。
- findings_status：NO_BLOCKING_FINDINGS / BLOCKING_FINDINGS / INDETERMINATE / NOT_ASSESSED。
- coverage：输入模式、各阶段适用性、真实/合成、continuity 是否选入及是否具备真实覆盖。

COMPLETED 只表示本次审计按声明流程完整执行，不代表源数据合格、债务清零或 Analyst Skill 可用。
忠实保留原 severity、outcome、review_required；写明汇总优先级及依据，UNKNOWN/INDETERMINATE 不得默认为通过。
阶段状态使用 COMPLETED / FAILED / NOT_APPLICABLE / NOT_RUN（以及运行中的 RUNNING）；业务上的 EMPTY 是数量情况，不能充作“未运行”。

CLI 退出码固定并测试：
0：执行完成，NO_BLOCKING_FINDINGS；
1：执行完成但有 BLOCKING_FINDINGS 或 INDETERMINATE；
2：输入、配置、版本或信任校验错误；
3：执行、持久化、输出完整性故障。
中断可以使用既有平台中断退出码，但必须可识别且没有成功标志。
非法参数等 Typer 自身错误与应用输入错误可同为 2；不能靠解析日志文本判断成功。

负向样本正确返回 1/2/3 是相应测试 PASS，不是把负向输入本身写为合格。
失败保存 error_code、stage、关联 artifact/pointer、原始异常记录，后续依赖步骤 NOT_RUN。不产生可被 compare 接受的 completed 标志。

## 八、运行目录、不可变性及安全写入

运行输出根目录显式指定；拒绝输出覆盖输入文件、Frozen/Registry 树或历史运行目录。解析实际路径并检查符号链接/Windows junction 导致的别名碰撞；路径穿越不得写出分配的运行目录。
每次原子创建全新唯一 run 目录，不覆盖、不清理旧目录。run_id、wall clock、耗时是 operational metadata，不是分析时间，不进入业务语义哈希。
写文件采用同目录临时文件及原子替换；只有本次新目录内未完成文件可替换。最后发布 completion manifest。一次失败、中断留下的目录必须被识别为 incomplete，不得复用为成功结果。
可写入时持续追加 audit_log.jsonl；不能因日志写失败反而返回成功。写入失败无法保存完整包时，对 stderr/退出码真实报告。
不要求断点复用半成品：恢复可新建 run 从同一不可变输入重跑；保留历史失败与中断记录。

输入与产物的 authority 是原始 bytes + SHA-256，不是浅层 frozen model。读取一次捕获原始字节；校验后用副本调用模块；完成前检查实际来源文件哈希未变。若期间有变更，失败并记录。

## 九、标准审计包

成功 run 至少输出：
request_snapshot.json、input_manifest.json、source_bytes/（内容寻址的来源快照）
versions.json、stage_results.json、adaptation.json、canonical_view.json、validation.json
normalized_audit.json、pattern_aggregation.json、continuity_result.json
review_queue.json、provenance_index.json、immutability_report.json
semantic_summary.json、run_summary.json、report.md、audit_log.jsonl、manifest.json。

不适用的 adaptation/canonical/validation 文件使用显式 status/reason 包装，不能伪造空 PASS；适用时完整保存旧模块的原输出，包装层不改其契约。
continuity_result 遵循 B-2，外部可信描述符及所用 Snapshot/来源字节同时保存，方便回读；保存它们不代表它们能自我授权。
review_queue 只从已有错误、隔离、损失、待审查标记、连续性冲突等明确结构字段产生，保留 source status/severity 与完整来源；不自然语言推断，不替人作审查裁决。
report.md 用中文说明本轮做了什么、发现什么、未检查什么、真实覆盖、输入与规则版本、证据入口；仅从结构化结果确定性生成，不调用 LLM。
manifest 包含所有已完成产物的相对路径、类型、字节哈希，以及组件语义哈希与明确投影版本。禁止绝对/上级路径逃逸，禁止文件缺失和额外未声明业务产物被静默忽略。
关闭日志并计算最后字节哈希后才写最终 manifest；manifest 不包含自身哈希，不哈希仍增长的 stdout/log。manifest 哈希由外部验收清单/compare 显式预期哈希固定。

## 十、确定性与 Self-stability

明确区分：
A. 整个文件的字节哈希，包含原始来源与运行证据；
B. 业务语义哈希，排除时间戳、run_id、耗时、绝对路径和展示标签等 operational 字段。
不能要求不同时间运行的整个目录字节完全一致，也不能把所有差异都删除以制造一致。

制定版本化、正向枚举字段的语义投影。源内容、规则版本、实际 ValidationContext、审核意见、显式引用和业务结果的实质改变必须能影响对应语义哈希。沿用 A/B-1/B-2 身份，不重定义旧 record/pattern/relation ID。
运行生成的报告先形成稳定的组件业务产物，再包装 operational 信息；避免时间/路径进入生成报告的身份链。
相同完整输入连续运行三次：组件业务输出、语义汇总、队列与索引稳定，运行目录独立；输入顺序/路径标签变化不改变本不依赖它们的语义；source provenance 如实变化。
证明 source bytes 和内嵌 payload 未变；嵌套模型被修改、源文件期间被替换、输出被篡改都应被检测。
Runner 的输出不得自动重新进入本轮输入；没有显式选择就不得反馈吸收自己的报告、日志或旧 run，避免审计记录逐轮膨胀。

## 十一、Cross-run comparison 的严格边界

compare 只读取调用方指定的两个已完成审计包及外部固定的 manifest SHA-256。先核验全部字节、路径、版本和完成状态，再比较。缺失、截断、篡改、伪造 completion 或不兼容数据性质必须硬失败/明确不可比较，不生成“无变化”的成功假象。
REAL 与 SYNTHETIC 禁止比较为真实结果。组件版本/签名投影版本不同，受影响组件标为 NOT_COMPARABLE；ValidationContext 不同必须显式报告，不能把不同时间口径结果包装为等价。
允许上下文变化的运行作信息展示，但不可宣称相同条件回归；未受影响组件是否可比由明确的兼容性矩阵决定。

compare 输出新建 comparison 目录，含 request、input manifests 固定值、compatibility、diff.json、report.md、manifest，不改左右 run。
比较内容至少有：输入增减/哈希变化、运行配置差异、record disposition 数量变化、Pattern 的 added/removed/common 和 occurrence 数量变化、明确 Relation/Membership 的 added/removed/common/changed、continuity 上下文变化及覆盖限制。
Pattern 的跨报告/跨运行身份严格使用 B-1 原签名，不重新设计。不同报告中的相同签名必须聚为同一模式，同时保存各来源 occurrence；跨 run 的 occurrence 使用 (run content identity, record_id) 等不丢来源的显式复合引用，不能把重跑同一资料算成新的独立证据。
record_id 依赖源哈希，报告内容变了可能整体换 ID；不得靠文本相似把不同 ID 对齐或声称同一问题已修复。removed 仅表示本次选入范围中未出现，不等于 resolved。
不同选材范围必须提示；零 continuity 输入只能给出零结构差异，并写业务覆盖未证明。
这是工程比较，不是 Evidence Delta、Judgment Delta、观点演化判断或因果解释。不能用 Pattern 重现推断分析方法重现。

## 十二、正式输入与验证用例

先复核并显式选入 A 的原始来源清单及其 bytes，使用 ENGINEERING_REPORTS 路径重跑 A→B-1；应得到与已接受输入相符的 26,220 条记录及 281 个 Pattern（所有子计数以真实旧产物为准）。差异必须定位，不改源输入或过滤记录凑数。
该 replay 只消费指定原始报告，不把 A/B-1 自身汇总结果当成同类原始记录重复投入。
另选现有一个 CANONICAL 输入、一个 LEGACY 输入作真实 CLI 集成烟测。明确输入版本、上下文、预期问题与实际覆盖。可利用 Golden 作为只读样本验证 Runner 的接线，但不新建 Phase 1.6 Golden Regression Suite，也不重跑旧 verifier。
若不存在可合法选入的真实某模式输入，真实覆盖标记未证明；使用明确 SYNTHETIC fixture 覆盖该分支，不能从文本编造真实对象。此限制在报告中显式列出。
B-2 正式真实空集可继续使用；另以 SYNTHETIC 验证非空确认、拒绝冲突、Thread 冲突、未解析引用、禁止借用确认等分支。不存在真实 Annotation 时不阻止纯工程 Gate，但不能改变业务覆盖结论。

必须新增的测试组：
- 三种输入模式的适用性、真实库接口调用和来源链；CLI/API 一致性；旧 CLI 回归。
- 重复 JSON key、非有限值、缺文件、错误 hash、错误版本/authority、非空 continuity 缺上下文、重复输入、混合 REAL/SYNTHETIC。
- 业务不合格但执行完成；阶段异常时后续 NOT_RUN；unsupported、quarantine、indeterminate 保留；退出码矩阵。
- 写失败、中断、目录冲突、路径穿越、输出与输入别名碰撞、incomplete run 不能比较；使用可控故障注入，不删改真实资料。
- 三次稳定、输入排列/位置变体、源字节不变、深层对象篡改、输出/manifest 篡改和回读；防自反馈膨胀。
- 非空跨 artifact、跨 run 相同 Pattern 身份，完整 occurrence 与来源；差异增减；范围变化不等于修复；上下文/版本不兼容标记。
- 完整反向索引及连续性冲突行为、没有自动 Thread 或推断关系。

既有 477 个测试身份逐个对照 B-2 run_004 JUnit，不能删除、改名、跳过以降基线。全部既有及新增测试 fail/error/skip=0。
执行 Ruff check（src、tests、本阶段 verifier）和 scoped Ruff format --check（仅本阶段新文件及获准 main.py），使用已验证的 workspace-parent cwd、显式 pyproject.toml；只修新阶段问题，不能格式化历史树。

## 十三、正式验收脚本与产物

建立 scripts/verify_phase1_5c.py，只负责本阶段 bounded acceptance，与产品 Runner 分离。
本轮 verifier 的测试报告不能在同一次运行中被 Runner 当作输入，形成自引用。
执行前保存不可覆盖 baseline：源码、全部前序正式产物、Frozen/Golden、外部 operational 文件、所用 Prompt 的 SHA-256，以及获准 main.py 的原始字节。
每次验收建立 phase1/phase1_5c_evidence/run_NNN/，不覆盖历史 run；把 Runner 输出放本轮独立子目录。

phase1/ 顶层至少保存：
phase1_5c_input_selection.json
phase1_5c_input_hashes.json
phase1_5c_test_report.json
phase1_5c_prerequisite_verification.json
phase1_5c_stability_report.json
phase1_5c_cross_run_report.json
phase1_5c_immutability_report.json
phase1_5c_scope_report.json
phase1_5c_gate_result.json
phase1_5c_manifest.json
phase1_5c_acceptance_report.md
phase1_5c_execution_progress.json
phase1_5c_execution_progress.jsonl

每个 evidence run 保存：完整 argv/cwd/exit_code、原始 stdout/stderr、JUnit、真实输入选择与固定哈希、三次运行结果、比较包、回读/篡改检查、provenance/守恒检查、scope/immutability、CLI 注册 diff、本轮正式产物快照。
Manifest 列明 phase、runner/report/comparison/projection 版本、component versions、实际输入及真实覆盖、测试分类统计、Gate、证据路径、来源与产物 byte/semantic hashes、flags；不包含自身哈希，不包含仍写入的日志哈希。
最终独立重读清单，核实文件确实存在且 hash 相符。报告不能只引用 progress 或程序自己声称 PASS。

## 十四、逐项 Gate

每项输出 PASS/FAIL/NOT_VERIFIED、实际观察、证据路径。只有执行过且证据充分才能 PASS。

C101：A/B-1/B-2 前置 Gate 与 Manifest 基线核验通过。
C102：既有 477 个测试身份保留，全部通过，零 error/skip。
C103：新测试全部通过；lint/format 通过。
C104：CLI 注册正确，旧命令兼容，Python API 与 CLI 结果一致。
C105：请求/版本/输入 hash/目录与外部信任校验，负向输入正确拒绝。
C106：CANONICAL 分支调用既有 Validator，适配 NOT_APPLICABLE。
C107：LEGACY 分支沿用既有 Compatibility，完整保留规范视图、损失、隔离及验证来源。
C108：ENGINEERING_REPORTS 分支准确复现已接受 A→B-1 的完整计数与来源。
C109：连续性按 B-2 独立处理；缺信任硬失败；真实空输入明确覆盖限制。
C110：Normalization/Pattern/Continuity 守恒和双向索引通过，无重复规范化。
C111：execution、findings、coverage 独立，退出码与负向业务结果一致。
C112：阶段失败/中断/写失败不产生可消费的成功包，恢复不覆盖历史。
C113：唯一目录、路径边界、输入输出别名和历史运行保护通过。
C114：标准包完整，manifest 不自引用、不哈希增长中文件，落盘回读与篡改检测通过。
C115：review queue、报告和 provenance 完整可逆，不伪造无问题结论。
C116：相同输入三次业务语义稳定；operational 差异明确分离。
C117：输入排列/位置变体规则通过；源字节与 payload 未改变；无自反馈膨胀。
C118：同签名 Pattern 跨 artifact/run 身份稳定且 occurrence 来源完整。
C119：compare 校验左右运行和外部固定哈希；输出完整增减变化，左右输入不变。
C120：比较范围、版本、上下文兼容性明确；removed 不等于 resolved；无模糊对齐。
C121：REAL/SYNTHETIC 隔离，真实业务覆盖与合成测试覆盖分开报告。
C122：获准 CLI diff 最小；其他受保护源码、前序正式产物、Frozen/Golden 未改变。
C123：无 LLM/network/NLP/embedding、分析框架挖掘、语义推断或自动 Thread。
C124：全部机器产物、原始输出、逐项验收、manifest 和可续接进度真实存在。
C125：Phase 1.6 executed=false；Phase 1 Final Gate 未完成；Analyst Model/Skill/Production=NOT_READY。

所有必要 Gate 通过才输出 READY_FOR_PHASE_1_6。
任一必要 Gate 失败或无法验证则 NOT_READY_AUDIT_RUNNER_BLOCKER。
Gate 通过仅表明 1.5C 工程完成，不得称 Core Engineering Foundation V0.1 已总验收，不得自动开始 1.6。
实际遗留的非阻塞观察、真实样本缺失和业务覆盖限制要保留，不能因为 Gate 通过而消失。

## 十五、禁止事项

不实现新闻爬取、数据订阅、语音转写、自动事实抽取、RAG、LLM 分析、9527 方法挖掘、Analyst Model/Skill、前端或可视化界面。
不增加 Evidence Delta、Judgment Delta、Decision Trigger、自动论题归并、Thread/Episode 新 Ontology。
不修改 Frozen/Schema/Registry/Validator/Compatibility 语义，不自动修复源数据，不执行 Phase 1.6，不把工程 Pattern 当分析方法。
可视化的未来接口只体现为完整、稳定、可查询的来源与步骤记录；不为了未来 UI 建设本阶段之外的服务。

## 十六、执行、恢复和最终交付

分阶段执行：基线与接口核对 → 契约与失败模型 → Runner/CLI → 报告及比较 → 测试与正式验收 → 逐项交付。
每阶段保存产物、原始输出、进度，自动进入下一阶段，不等逐步确认。仅遇到用户必须决定的语义缺口、范围变动或外部并行改动时暂停相关工作。
若中断，尽可能记录：实际已完成项、准确未完成项、验证结果、失败原因、最后命令、当前 evidence run、下一步。恢复先核对文件/hash，不能把进度 complete 当验收证明。

最终用中文报告：
- 1.5C completed yes/no，版本与最终 Gate。
- CLI/API 实际可执行方式；真实输入类型和数据来源。
- normalization、Pattern、Continuity 实际数量；真实/合成覆盖及限制。
- 审计执行成功与源资料有问题的区别，真实 run 的实际 findings/退出码。
- 稳定性、跨次比较、完整性、失败恢复与不可变性结果。
- 既有/新增测试 PASS/FAIL/ERROR/SKIP；C101–C125 逐项证据。
- 获准 CLI 变更和受保护文件状态；完整报告/manifest/原始输出链接。
- 已完成、未完成、非阻塞观察及下一步；不得越过本阶段。
- 用非计算机专业用户能理解的例子解释本次新增能力，并说明距“新新闻→9527 框架分析→可视化溯源→后续验证”仍缺哪些部分。
