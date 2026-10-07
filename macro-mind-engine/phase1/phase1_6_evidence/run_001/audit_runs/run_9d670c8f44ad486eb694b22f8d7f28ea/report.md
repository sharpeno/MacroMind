# 审计运行报告

执行状态：COMPLETED
资料检查：BLOCKING_FINDINGS

执行完成不代表资料合格；工程模式不代表分析方法。

## 实际覆盖
{"analyst_model":"NOT_READY","analyst_skill":"NOT_READY","continuity_business_coverage":"NOT_DEMONSTRATED","continuity_input":"NOT_PROVIDED","data_kind":"REAL","input_mode":"LEGACY","phase1_6_executed":false,"production":"NOT_READY"}

## 实际数量
{"continuity":{"annotations":0,"memberships":0,"relations":0,"review_conflicts":0,"thread_assignment_conflicts":0},"dispositions":{"OPAQUE_EXCLUDED":10766,"PATTERN_ELIGIBLE":10529,"SUMMARY_ONLY":0,"TRACE_ONLY":14038},"patterns":264,"record_types":{"ADAPTATION_LOSS":7400,"MAPPING_EVENT":14038,"QUARANTINE":342,"UNKNOWN_ENGINEERING_RECORD":10766,"VALIDATION_FINDING":2787},"records":35333,"review_items":19361}

## 阶段
- capture: COMPLETED
- foundation: COMPLETED
- adaptation: COMPLETED
- validation: COMPLETED
- normalization: COMPLETED
- patterns: COMPLETED
- continuity: COMPLETED
- report: COMPLETED
- persistence: COMPLETED

## 溯源入口
input_manifest.json → source_bytes/；review_queue.json → provenance_index.json → 来源 JSON Pointer。
适配来源另见 adaptation.json 的 mapping_ledger；完整验证见 validation.json。

业务语义哈希：d74c543e9cc6771cd95f3a5322959672d356e35532b6559afea8b383ab0bde36

未执行：分析者框架、自动论题推断、可视化、Phase 1.6。
