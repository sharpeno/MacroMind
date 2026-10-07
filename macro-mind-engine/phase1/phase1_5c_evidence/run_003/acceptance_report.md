# Phase 1.5C 正式验收

最终 Gate：READY_FOR_PHASE_1_6

真实输入重放：26,220 条记录 / 281 个工程 Pattern；数量是否匹配以 real_replay_checks.json 为准。
真实 continuity 未选入，Annotation/Relation/Membership 为 0；业务覆盖 NOT_DEMONSTRATED。

测试：{"existing": {"PASS": 477, "FAIL": 0, "ERROR": 0, "SKIP": 0}, "new": {"PASS": 55, "FAIL": 0, "ERROR": 0, "SKIP": 0}}

| Gate | 项目 | 结果 | 证据 |
|---|---|---|---|
|C101|前置验收与实际哈希|PASS|[prerequisites.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/prerequisites.json)|
|C102|既有 477 测试身份与通过|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml)|
|C103|新增测试 lint format|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [ruff_check.stdout.txt](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/ruff_check.stdout.txt), [ruff_format.stdout.txt](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/ruff_format.stdout.txt)|
|C104|CLI/API 与旧命令|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C105|输入与信任负向校验|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C106|Canonical 接线与适用性|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C107|Legacy 接线与完整来源|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C108|真实 A→B-1 重放|PASS|[real_replay_checks.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_replay_checks.json)|
|C109|独立连续性及真实覆盖|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C110|守恒与完整索引|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C111|状态与退出码|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C112|失败中断恢复|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C113|路径和运行目录保护|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C114|标准包及篡改检测|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C115|报告队列及来源|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C116|三次真实运行稳定|PASS|[stability.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/stability.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml)|
|C117|顺序不变源不变防自反馈|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C118|跨来源及跨运行模式身份|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C119|比较来源校验和完整增减|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C120|范围上下文版本比较边界|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C121|真实合成隔离|PASS|[test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json), [tests.xml](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/tests.xml), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|
|C122|保护边界与最小 CLI diff|PASS|[scope_check.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/scope_check.json), [cli_registration.diff](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/cli_registration.diff)|
|C123|无语义推断或越阶段实现|PASS|[runtime_review.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/runtime_review.json)|
|C124|机器产物与证据齐全|PASS|[invocation.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/invocation.json), [pytest.command.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/pytest.command.json), [test_report.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/test_report.json)|
|C125|后续阶段未执行|PASS|[runtime_review.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/runtime_review.json), [real_cli_smoke.json](G:/youhegaojian/macro-mind-engine/phase1/phase1_5c_evidence/run_003/real_cli_smoke.json)|

执行完成不代表输入资料合格：真实 replay 的 findings=BLOCKING_FINDINGS，退出码=1。

Phase 1.6 未执行；Core Foundation 尚未总验收；Analyst Model / Skill / Production=NOT_READY。

剩余业务工作：真实连续性样本、分析者方法提炼、新新闻分析、可视化及后续观点/事实双重验证。
