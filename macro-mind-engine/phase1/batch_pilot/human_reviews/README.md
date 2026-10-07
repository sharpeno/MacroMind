# 人工审核文件归档

run_001/exports/日期/：工作台累计快照导出暂存区。首次在页面选择exports文件夹；目录授权由浏览器处理。

run_001/batch_001/raw/：用户提交的第一批原始JSON，按字节保留，不改写。receipt.json保存校验信息，reviewed_records.json索引10条已审意见，next_actions.json列出待执行工作。

后续正式接收依次建立batch_002等目录。按来源运行编号分组，不能把run_002的审阅混进run_001。每次导出是累计快照，归档时按记录ID和更新时间比较增量，不能重复累计已审数量。原raw永不覆盖，纠正另存新批次。

第一批下一步详见run_001/batch_001/NEXT_STEPS.md。语义修订和重新审计尚未执行，扩样尚未批准。
