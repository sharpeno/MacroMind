# 审计运行报告

执行状态：COMPLETED
资料检查：INDETERMINATE

执行完成不代表资料合格；工程模式不代表分析方法。

## 实际覆盖
{"analyst_model":"NOT_READY","analyst_skill":"NOT_READY","continuity_business_coverage":"NOT_DEMONSTRATED","continuity_input":"NOT_PROVIDED","data_kind":"REAL","input_mode":"CANONICAL","phase1_6_executed":false,"production":"NOT_READY"}

## 实际数量
{"continuity":{"annotations":0,"memberships":0,"relations":0,"review_conflicts":0,"thread_assignment_conflicts":0},"dispositions":{"OPAQUE_EXCLUDED":0,"PATTERN_ELIGIBLE":5259,"SUMMARY_ONLY":0,"TRACE_ONLY":0},"patterns":49,"record_types":{"VALIDATION_FINDING":5259},"records":5259,"review_items":9}

## 阶段
- capture: COMPLETED
- foundation: COMPLETED
- adaptation: NOT_APPLICABLE
- validation: COMPLETED
- normalization: COMPLETED
- patterns: COMPLETED
- continuity: COMPLETED
- report: COMPLETED
- persistence: COMPLETED

## 溯源入口
input_manifest.json → source_bytes/；review_queue.json → provenance_index.json → 来源 JSON Pointer。
适配来源另见 adaptation.json 的 mapping_ledger；完整验证见 validation.json。

业务语义哈希：07abfc7260b16932c1cc7e5b4f664ea90aafe3ad0720fc4585a2582334773b70

未执行：分析者框架、自动论题推断、可视化、Phase 1.6。
