# 2026-10-04 结构整理验收报告

## 结论

本轮整理完成。采用统一当前入口、按用途分层的文档、只读导航校验、独立维护证据目录。既有业务代码、数据、审核结果和封存证据没有改变；未把目录整理当作新业务阶段验收。

## 实际改动

- 工作区新增START_HERE.md；将此前为空的MACROMIND_MASTER_STATE.md填为导航索引。
- 工程README修正“Phase1.3未开始”和“没有validate/audit”等过时说明，原文备份为README.before.md。
- 新增docs/current/README.md、STATUS.md、STRUCTURE.md、OPERATIONS.md，分别提供入口、目标对齐、目录职责和操作指引。
- 新增scripts/operations/project_status.py，读取三个既有latest指针，不复制第四套当前版本；核对一致性、当前两份封存清单和实际对象计数。
- 新增tests/operations/test_project_status.py，共7项检查，覆盖实际状态、越界、缺失、篡改、空清单、指针冲突、摘要与对象不一致。
- 新增maintenance/20261004_structure，集中保存本轮基线、命令、原始输出、退出码和报告。

封存目录没有搬迁。历史代码和清单依赖原路径，整体搬家会引入无必要的证据兼容风险；本次优化的是查找入口、责任划分与后续文件放置规则。个人资料不属于本轮范围。

## 验证结果

| 验证 | 结果 | 原始输出 |
|---|---|---|
| 首次基线测试 | 517通过、107初始化错误；系统Temp目录拒绝访问，不能算通过 | before.stdout.txt、before.stderr.txt |
| 指定独立工程内临时目录后，原有全量基线 | 624通过，1条缓存写入警告 | baseline_retry.stdout.txt |
| 整理后全量测试 | 631通过，1条缓存写入警告 | after.stdout.txt |
| 当前导航与封存、数量核对 | 通过；当前run_005；182个封存条目 | navigation.stdout.txt |
| 新增代码lint、格式 | 均通过 | changed_lint.stdout.txt、changed_format.stdout.txt |
| 全库lint | 不通过；26项既有导入排序问题 | global_lint.stdout.txt |
| 核心CLI帮助 | 退出0；validate、audit、compatibility等入口存在 | cli_help.stdout.txt |
| 原有文件完整性 | 3706份基线中仅README预期变化，3705份保持一致 | integrity.json |
| 试点与质量历史封存 | 检查1576条artifacts/generated_artifact_hashes/implementation记录，无差异 | seal_details.json |
| 首五期原始输入 | 25份与最初input_manifest一致 | original_input_details.json |
| 新入口Markdown链接 | 28个本地链接可解析 | integrity.json |

每项命令都有同名前缀.command.json、.result.json、.stdout.txt、.stderr.txt。全库lint涉及的原有代码在baseline.json比对中未变，因此未将其归为本轮新增缺陷。未自动修复这些文件，以免修改封存实现哈希。pytest缓存警告不影响测试执行；系统Temp初始化错误通过使用独立basetemp解决，失败记录保留。

历史封存检查限于batch_pilot与extraction_quality目录内上述三类条目，不冒称重跑全部Phase验收。整个engine已有文件的本轮前后对比另由3706份基线覆盖，排除虚拟环境、缓存、.git和maintenance。原始材料25份另核对。工作区其他个人目录没有扫描或重排。

## 与核心目标对齐

现阶段有证据归一化、引用校验、隔离、审计、人工反馈闭环，方向与可追溯分析系统一致。当前还没有可调用的多分析师框架、新新闻自动分析闭环或完整推理图。run_005的121条主张和19条结构可用论证链不能当作121条已验证事实或19种有效方法。

最近人工反馈促使方法与应用分离，是朝核心目标的一步；九项语义自检仍漏掉过核心方法，不能把表格完整度当语义质量。下一步建议用已审方法建立有限的框架表达原型，再用新案例检验，避免无限扩写摘要和审核页面。

## 未完成项与续接

本轮结构整理没有未完成阻塞项。以下为保留的项目后续工作，不是本轮通过项：

- 26项历史导入排序lint问题，需单独说明封存版本与当前代码的升级关系后处理。
- 53项非引用未决信息以及已有时长、转写、历史引用及时序问题。
- 方法—条件—步骤—案例—证据原型；明确“不适用/证据不足”输出。
- 新事件分析、第二分析者框架、多框架比较、可视化推理及后续验证机制。

继续时先运行project_status.py，再读docs/current/STATUS.md和最新report。不要重建run_005，也不要覆盖旧验收和人工导出。这里只完成整理，没有自动启动下一功能阶段。
