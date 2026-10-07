# Phase 1.5C — Audit Runner 1.0

本阶段把已经验收的模块串成可执行审计流程。运行成功表示完成了检查，不能表示资料全部合格，更不能表示已经形成 9527 的分析框架。

## 使用方式

在项目虚拟环境安装的 macromind 入口运行：

```text
macromind audit run --request REQUEST.json --output-root OUTPUT_DIRECTORY
macromind audit run --request REQUEST.json --trusted-context TRUST.json --output-root OUTPUT_DIRECTORY
macromind audit compare --left LEFT_RUN --left-manifest-sha256 LEFT_SHA256 --right RIGHT_RUN --right-manifest-sha256 RIGHT_SHA256 --output-root COMPARISON_DIRECTORY
```

也可使用 `.venv/Scripts/python.exe -m macromind.cli.main audit ...`。Python API 为 `AuditRunner().run(request_path, output_root, trusted_context_path=None)`、`compare_runs(left, left_hash, right, right_hash, output_root)`。返回运行目录、manifest 字节哈希、状态和退出码；输入契约或路径错误可能抛 RunnerError，CLI 转换为结构化 JSON 错误。

请求包含 request_version/policy_version=1.0、data_kind、input_mode、sources、contract、registry、validation_context 和可选 continuity。单条 source 明确 path、sha256、artifact_type、phase、component、data_kind。FoundationSpec 包含 path、tree_sha256（`tree_hash` 对排序后相对文件名及字节哈希清单求规范 JSON SHA-256）。相对路径以 request 目录为准。正式验收目录保留可直接复用的真实 *.request.json 示例，不依赖推测格式。

CANONICAL 与 LEGACY 各接受一个主文件；前者直接验证，后者沿用 Compatibility，保留它的完整结果，并按本轮显式 ValidationContext 重新验证 canonical_bundle。适配内嵌摘要是历史内部检查，不重复归入 validation_report。ENGINEERING_REPORTS 只接收明确报告清单，适配和原始验证 NOT_APPLICABLE。

非空连续性输入：continuity.bundle 为 SourceSpec，continuity.artifacts 为 artifact ID→SourceSpec 映射，外部 trusted descriptor 另由参数传入。所有来源和 descriptor 的 data_kind 与主请求一致。无连续性输入使用显式空目录，无已解析引用，并记录 NOT_PROVIDED / NOT_DEMONSTRATED。

## 状态与错误

execution_status 与 findings_status 分开，coverage 单独列出。审计完成可以同时发现 BLOCKING_FINDINGS。

| 退出码 | 意义 |
|---|---|
| 0 | 完成，未发现阻塞问题 |
| 1 | 完成，但有阻塞或不能确定的结果 |
| 2 | 输入、配置、版本、信任问题 |
| 3 | 执行、写入、完整性故障 |
| 130 | 可识别的用户中断 |

资料汇总优先级：明确 ERROR/BLOCKING/CRITICAL、失败 outcome 或 quarantine → BLOCKING_FINDINGS；其次待审查、opaque/unknown、适配损失、INDETERMINATE、未解决的人工关系/连续性冲突 → INDETERMINATE；否则 NO_BLOCKING_FINDINGS。原始 severity/outcome 不改写，WARNING 仍保留队列。此摘要不为历史 Gate 重新授予通过资格。

每个运行新建目录，先写阶段状态、持续日志，最后关闭日志并写 manifest。失败或中断没有可消费的 completed manifest；后续依赖阶段 NOT_RUN。失败目录不重用、不删除。源资料只读，在完成前再次核对实际字节。模块交互使用库接口，不执行旧验收脚本。

## 审计包与溯源

request_snapshot、input_manifest、内容寻址 source_bytes、versions、stage_results、adaptation、canonical_view、validation、normalized_audit、pattern_aggregation、continuity_result、review_queue、provenance_index、immutability_report、semantic_summary、run_summary、report.md、audit_log 和 manifest 均保存。不适用的视图明确 NOT_APPLICABLE。

每条标准化记录能通过 artifact/hash/JSON Pointer 回查原报告；适配映射继续关联原始材料。回读重建 Normalizer、Aggregator、ContinuityIndex 的结果，并核验完整字节、队列、数量与语义哈希。输入与模型的浅层 frozen 不是完整性依据。

run_id、日志时间、耗时和来源路径可不同；业务语义包含来源内容哈希、规则版本、实际 ValidationContext、各组件语义哈希、结构化队列及 findings。源位置、sample_label 等展示信息不作为业务身份。连续性待审查项的原始来源 sidecar 保留但不进入 queue 语义投影。投影版本 1.0。

## 跨次比较

只接收明确指定、具有外部预期 manifest 哈希的两个完整运行。先核验全部来源快照与产物。禁止 REAL 与 SYNTHETIC 混比。

Pattern 比较要求 Runner/projection/normalization/ontology/schema/pattern 版本、Foundation 与 ValidationContext 一致；Continuity 比较要求基础版本、continuity 版本和解析上下文哈希一致。不兼容组件 NOT_COMPARABLE，不能输出假“没有变化”。输入范围变化另列提示，不自动判定回归。

按原 Pattern/Relation/Membership ID 比较 added/removed/common/changed，保留 occurrence 的 (run content identity, record_id) 来源和计数变化。同一资料重跑保留相同 content identity，不当作独立证据。removed 只表示选入范围内未出现，不表示已修复。不按文本猜对应记录，不做观点演化推断。

## 验收与产品边界

scripts/verify_phase1_5c.py 是有界工程验收，独立于产品 Runner。重放 A 的 9 份明确来源，核对 26,220 条记录及 281 个工程 Pattern；执行三次真实重放、Canonical/Legacy CLI 烟测及真实比较，并核对原 477 项测试身份、新增测试、lint/format、源不变和最小 CLI 注册 diff。最新报告与实际状态见 phase1/phase1_5c_gate_result.json、phase1_5c_acceptance_report.md 和 Manifest 指向的 evidence run。

CLI main.py 仅新增 audit_app 导入及注册两行，其余前序文件受保护。审计输出供将来的可视化读取，但本阶段没有前端、新闻采集、分析框架提炼、LLM 推断或自动 Thread。真实连续性输入为空时，业务覆盖未证明。

Phase 1.5C 之后仍须 Phase 1.6 总回归，再进行真实案例批量验证、9527 方法提炼、未见材料分析、可视化和后续观点/事实双重检验。Analyst Model / Skill / Production 均 NOT_READY。
