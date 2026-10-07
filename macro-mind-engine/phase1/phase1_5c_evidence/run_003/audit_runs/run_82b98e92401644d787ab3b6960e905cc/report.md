# 审计运行报告

执行状态：COMPLETED
资料检查：BLOCKING_FINDINGS

执行完成不代表资料合格；工程模式不代表分析方法。

## 实际覆盖
{"analyst_model":"NOT_READY","analyst_skill":"NOT_READY","continuity_business_coverage":"NOT_DEMONSTRATED","continuity_input":"NOT_PROVIDED","data_kind":"REAL","input_mode":"LEGACY","phase1_6_executed":false,"production":"NOT_READY"}

## 实际数量
{"continuity":{"annotations":0,"memberships":0,"relations":0,"review_conflicts":0,"thread_assignment_conflicts":0},"dispositions":{"OPAQUE_EXCLUDED":9498,"PATTERN_ELIGIBLE":8298,"SUMMARY_ONLY":0,"TRACE_ONLY":9102},"patterns":253,"record_types":{"ADAPTATION_LOSS":6442,"MAPPING_EVENT":9102,"QUARANTINE":345,"UNKNOWN_ENGINEERING_RECORD":9498,"VALIDATION_FINDING":1511},"records":26898,"review_items":16684}

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

业务语义哈希：978a28dbf5a3f5f938ead78f244da78a4dc9c16080b94ff47ff4338c1c5b72b7

未执行：分析者框架、自动论题推断、可视化、Phase 1.6。
