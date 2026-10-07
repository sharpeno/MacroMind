# 常用操作与续接

在macro-mind-engine目录执行：

```powershell
# 只读：解析当前指针、核对封存哈希、重算对象数量
.\.venv\Scripts\python.exe scripts/operations/project_status.py
# 核心CLI真实命令，以help为准
.\.venv\Scripts\python.exe -m macromind.cli.main --help
# 全量回归
.\.venv\Scripts\python.exe -m pytest -q
```

project_status返回0表示导航、指定封存清单和计数检查通过；返回1表示缺文件、哈希变化或指针冲突等。它不写入资料，不批准语义，也不执行审计。nonreference_indeterminate取各期既有摘要之和，其他对象计数同时与bundle核对。

继续工作先运行导航检查，读取其report/review_receipt/policies路径，再读本次维护PROGRESS。不要仅根据聊天摘要恢复；不要重新执行会覆盖旧产物的历史apply/verify脚本。部分历史verify脚本也有写入行为，不能把所有名为verify的脚本当只读命令。

当前质量编译入口仍为scripts/compile_reviewed_episode.py；语义包检查入口仍为scripts/validate_semantic_review.py。使用--help了解参数，不在原run目录重跑编译。新一轮先建新目录保存结果。

历史工程README已原样备份在maintenance/20261004_structure/README.before.md。此次整理前后测试、完整性比对与已知失败项保存于同目录。恢复旧README只涉及说明入口；不应回滚任何已验收业务数据。
