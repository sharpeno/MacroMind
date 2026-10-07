# MacroMind Core Ontology V0.3 Change Policy

V0.3 是 FROZEN VERSIONED SEMANTIC CONTRACT。普通案例不得直接改变14个 Core 类型、核心定义、核心边界、provenance、temporal、cutoff 或 reasoner/observer 原则。

## V0.3-compatible evolution

允许字段增加、enum 扩展、Auxiliary Object/Relation 增加、Validator 规则增加、Registry 扩展、Review policy 调整、Analyst layer 与 Runtime 扩展；前提是既有核心语义不变。为实现层版本建立独立版本和变更记录，不静默编辑 Frozen 文件。

## Core Change RFC

RFC 必须给出 problem statement、affected Core Objects、affected Goldens、尽可能跨案例证据，逐项说明 field、Auxiliary Object、Relation、Validator、Review 为什么不足，给出 proposed Core change、migration impact、backward compatibility risk、new version target。

新增类型还须回答：现有14类型为何不能表达，为什么不能作为字段、辅助对象、关系或 Assessment，是否有至少两个独立 Golden，以及不新增会导致何种具体重复语义错误。重要性或实现便利不足以构成必要性。

只有通过 RFC → Review → Migration Plan → Compatibility Plan，才进入 Core Ontology V0.4；不得把普通案例困难变成 V0.3 静默重设计。

## Frozen artifact 不可原地静默修改

CORE_ONTOLOGY_V0.3_FROZEN.md、core_objects.json、core_boundaries.json、core_principles.json、freeze_manifest.json 都是不可静默编辑的历史版本。发现问题先建立独立 errata 或 RFC。

typo、broken link、metadata 等非语义修复也须 patch record，保存旧字节 hash、新 hash、原因、作者/时间、影响和 semantic_hash 检查。不覆盖或抹去历史产物；优先生成独立修订记录。semantic_hash 必须保持不变，或明确记录变化并进入相应语义变更流程。

## Hash 与审计链

SHA-256 是文件原始字节完整性校验。semantic_hash 是 semantic_contract_projection.json 的排序键、UTF-8、ensure_ascii=false、无多余空白 JSON 序列化的 SHA-256；它覆盖14定义与语义不变量、15规则、16原则、时间/溯源/归因规则、扩展范围和本政策。它不替代人的语义审查，也不是同义改写的自动等价证明。

freeze_manifest.json 记录输入与合同输出 hash，不自引用自己的 hash；freeze_commit_log.json 记录 manifest 和所有交付文件 hash，不自引用 log 的 hash。外部仓库或签名可以进一步提供防篡改锚点，本任务不创建 Git commit 或外部签名。

原审计 formal_freeze_executed=false 和20项债务必须保留。新的 Freeze Manifest 才记录正式冻结。D01 仅在独立 overlay 标为 addressed_by_freeze_commit，其他债务继续待后续阶段处理；Core 冻结不传播为 Skill 或 Production Ready。
