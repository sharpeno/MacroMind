# 审计运行报告

执行状态：COMPLETED
资料检查：BLOCKING_FINDINGS

执行完成不代表资料合格；工程模式不代表分析方法。

## 实际覆盖
{"analyst_model":"NOT_READY","analyst_skill":"NOT_READY","continuity_business_coverage":"NOT_DEMONSTRATED","continuity_input":"NOT_PROVIDED","data_kind":"REAL","input_mode":"ENGINEERING_REPORTS","phase1_6_executed":false,"production":"NOT_READY"}

## 实际数量
{"continuity":{"annotations":0,"memberships":0,"relations":0,"review_conflicts":0,"thread_assignment_conflicts":0},"dispositions":{"OPAQUE_EXCLUDED":9499,"PATTERN_ELIGIBLE":7311,"SUMMARY_ONLY":308,"TRACE_ONLY":9102},"patterns":281,"record_types":{"ADAPTATION_LOSS":6442,"DEBT_STATUS":4,"GATE_RESULT":40,"IMMUTABILITY_EVENT":10,"MAPPING_EVENT":9102,"QUARANTINE":345,"REGISTRY_GAP":135,"SCHEMA_GAP":352,"TEST_RESULT":254,"UNKNOWN_ENGINEERING_RECORD":9499,"VALIDATION_FINDING":37},"records":26220,"review_items":16292}

## 阶段
- capture: COMPLETED
- foundation: COMPLETED
- adaptation: NOT_APPLICABLE
- validation: NOT_APPLICABLE
- normalization: COMPLETED
- patterns: COMPLETED
- continuity: COMPLETED
- report: COMPLETED
- persistence: COMPLETED

## 溯源入口
input_manifest.json → source_bytes/；review_queue.json → provenance_index.json → 来源 JSON Pointer。
适配来源另见 adaptation.json 的 mapping_ledger；完整验证见 validation.json。

业务语义哈希：019bc3396b41b50f68c637b31f22b44fc088c7b852ecaf75503f78cbe00734f3

未执行：分析者框架、自动论题推断、可视化、Phase 1.6。
