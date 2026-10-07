# 人工审核后的注释质量门禁

本阶段将首五期人工审核中发现的错误，转成编译前可执行的保留性检查。它不是自动语义提取器，也不验证观点的事实正确性。

## 已实现

`src/macromind/quality/annotations.py`检查原始字幕指纹、cue与引用完整性、唯一编号、已审关键措辞、局部理由的连接范围、背景展望不得重新进入预测候选、被人工保留为上下文的段落不得自动补成主张。所有新增、删除或改变的注释记录均进入待复核，即使仍包含关键词。

`review_disposition`要求正面下拉判定附有文字意见时先处理意见，避免忽略“忠实，但请补条件”。它提供分类辅助，不自动理解或执行自由文本。

`scripts/compile_reviewed_episode.py`是新的受控入口：必须提供配置文件哈希；先检查，再编译。退出0仅表示门禁通过，1表示有新变化需审核，2表示存在阻断问题。拒绝或待复核时不会创建编译目录。可以只生成检查报告，也可以通过`--compile-to`编译到新的试验目录；不会覆盖既有run。

旧封存的`build_episode.py`保持不动，直接运行旧脚本会绕过新门禁。后续注释修订应使用新的受控入口。尚未将其接入一个不存在的自动提取服务或生产部署。

## 调用方式

从工程根目录使用虚拟环境Python，并将PYTHONPATH设为工程的src目录：

```powershell
$env:PYTHONPATH = 'G:/youhegaojian/macro-mind-engine/src'
.\.venv\Scripts\python.exe scripts/compile_reviewed_episode.py `
  --annotation phase1/batch_pilot/run_003/EP005/annotation.json `
  --segments phase1/batch_pilot/run_003/EP005/segments.json `
  --policy phase1/extraction_quality/run_001/policies/EP005.json `
  --policy-sha256 '<从policy_manifest.json取得并核对的EP005哈希>' `
  --report '<新的报告路径>'
```

如需编译，追加`--compile-to`及`phase1/batch_pilot`下一个尚不存在的直接子目录。报告路径也必须全新。原样可核查的实际命令见证据目录中的`*.command.json`。

## 边界

- 配置是可追溯的人工审核约束，并非不可更改的自然语言标准。合理改写也可能触发门禁；应复核后生成新版本配置和哈希，不能为了通过而静默放宽。
- 当前约束针对本次五期材料。基线中的其他内容没有因哈希匹配获得人工认可；`unreviewed_ids`是保守标记，不是完整的历史审核台账。
- 只要文字改变即要求复核，可拦截“关键词保留但另加错误结论”，但无法发现基线中尚未识别的语义错误。
- 宽泛展望仍保留为作者观点；仅禁止把已标注背景观点放进具体预测候选。本工程尚无预测准确率评分器，也没有把该约束假称为已经执行的评分改进。
- 这次在未审C07上验证的是新表述会进入审核队列，不是对留出集测得了准确率。
- 下一步若评估规则的泛化效果，应单独选择未参与配置设计的小样本、保存原提取结果，再作人工核对；不自动扩大素材规模。

## 证据

`phase1/extraction_quality/run_001`保存五份固定配置、配置哈希、26个新增测试的原始输出、全量测试与lint/格式输出、五期实际检查及正负CLI集成记录。成功试编译位于`phase1/batch_pilot/quality_compile_trial_002`，它是工程试验产物，不是新的人工作品版本。

最终版本还对预测候选列表单独作变更追踪：即使主张文字未变，修改预测分类也必须复核。早期配置存于policies_v1，最终固定配置为policies，最终CLI集成文件以前缀v2_区分。
