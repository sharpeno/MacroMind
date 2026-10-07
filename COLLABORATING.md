# 多人、多设备协作

仓库：https://github.com/sharpeno/MacroMind 。所有者在仓库设置中添加同事访问权限。每人使用自己的 GitHub 账号和 Git 提交身份，每台设备独立克隆，不通过网盘同步 .git。

## 首次使用

```powershell
git clone https://github.com/sharpeno/MacroMind.git
cd MacroMind
python -m venv macro-mind-engine/.venv
./macro-mind-engine/.venv/Scripts/python.exe -m pip install -e "./macro-mind-engine[test]"
```

macOS/Linux 使用 .venv/bin/python。音视频不随 Git 克隆，需按 MEDIA_MANIFEST.csv 从素材持有者获取，放回相对路径并核对哈希；需要素材的操作应先确认输入完整。

## 开始任务

先读 START_HERE.md、当前 STATUS.md 和 GitHub 开放 PR，沟通负责人及文件范围。每项任务使用独立分支，下列名字仅为示例：

```powershell
git switch main
git pull --ff-only
git switch -c work/alice-method-review
```

复制 progress/TEMPLATE.md 为独立任务文件，填写目标、负责人和范围，提交推送后在 GitHub 创建 Draft PR。一个设备并行处理多个任务时使用独立克隆或 Git worktree，避免多个终端在同一目录切换分支。

## 推进与交接

每完成一个小步骤、遇到阻塞或结束本轮工作时，更新任务记录并推送：

```powershell
git status --short
git diff
git add <本任务改动的文件或目录>
git diff --cached --stat
git commit -m "说明本次完成的具体工作"
git push -u origin HEAD
```

通过 Draft PR 查看未合并进度；main 只显示已合并工作。GitHub 不会自动同步终端动作、聊天记录、未提交文件或未推送提交。

接手前确认原负责人已推送，约定同一分支同一时间只有一位写入者。执行 git fetch origin，然后 git switch --track origin/<分支名>；本地已有分支则切换后 git pull --ff-only。失败先检查分叉，不用强制推送或 reset --hard 解决同步。

## 合并与验证

完成后将 PR 标记为可审核，由同事检查后合并。任务分支需要最新主线时执行 git fetch origin 和 git merge origin/main，处理冲突后重新验证。

业务结论只更新 macro-mind-engine/docs/current/STATUS.md；任务文件记录行动和交接，不重复维护业务计数。历史封存产物不可覆盖，新实验使用独立目录，latest 指针按现有流程更新。

数据或指针变化后，在工程目录运行 ./.venv/Scripts/python.exe scripts/operations/project_status.py；代码变更运行相应测试。记录实际命令、结果及未验证范围。工程检查通过不代表语义验收。

仓库使用 `.gitattributes` 保留原始字节，避免跨系统换行转换破坏封存哈希。不要批量格式化历史证据。
