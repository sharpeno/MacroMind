# 常用操作与续接

在`macro-mind-engine`目录执行。依赖和虚拟环境由`uv`管理：

```text
uv sync
# 只读：解析当前指针、核对封存哈希、重算对象数量
uv run python scripts/operations/project_status.py
# 核心CLI真实命令，以help为准
uv run python -m macromind.cli.main --help
# 全量回归
uv run pytest -q
```

project_status返回0表示导航、指定封存清单和计数检查通过；返回1表示缺文件、哈希变化或指针冲突等。它不写入资料，不批准语义，也不执行审计。nonreference_indeterminate取各期既有摘要之和，其他对象计数同时与bundle核对。

继续工作先运行导航检查，读取其report/review_receipt/policies路径，再读本次维护PROGRESS。不要仅根据聊天摘要恢复；不要重新执行会覆盖旧产物的历史apply/verify脚本。部分历史verify脚本也有写入行为，不能把所有名为verify的脚本当只读命令。

当前质量编译入口仍为scripts/compile_reviewed_episode.py；语义包检查入口仍为scripts/validate_semantic_review.py。使用--help了解参数，不在原run目录重跑编译。新一轮先建新目录保存结果。

历史工程README已原样备份在maintenance/20261004_structure/README.before.md。此次整理前后测试、完整性比对与已知失败项保存于同目录。恢复旧README只涉及说明入口；不应回滚任何已验收业务数据。

## 跨平台路径检查

latest指针只保存以`/`分隔的仓库相对路径。状态脚本仍可读取历史的Windows或POSIX绝对路径，但迁移后不应继续生成机器相关路径。

在仓库根目录执行一次迁移：

```text
uv run python scripts/operations/migrate_project_paths.py
uv run python scripts/operations/project_status.py
```

Windows同事在工程目录使用项目虚拟环境中的Python执行：

```text
uv run python scripts\operations\migrate_project_paths.py
uv run python scripts\operations\project_status.py
uv run pytest tests\operations\test_project_status.py -q
```

macOS/Linux对应命令为：

```text
uv run python scripts/operations/migrate_project_paths.py
uv run python scripts/operations/project_status.py
uv run pytest tests/operations/test_project_status.py -q
```

路径测试覆盖仓库相对路径、Windows风格相对路径、历史Windows绝对路径、历史POSIX绝对路径、路径穿越、其他项目绝对路径和UNC路径。状态检查的`navigation_integrity`必须为`PASS`；测试还应确认`project_status.py`不修改封存产物。
