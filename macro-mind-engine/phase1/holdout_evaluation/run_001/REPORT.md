# 第472期首例留出对照

## 结论
PARTIAL_METHOD_TRANSFER_WITH_CORE_REASONING_GAP。方法部分迁移，但漏掉博主的核心原因链；三项对照归纳等待人工审阅。不计算准确率，不标为语义验收通过。

这次分析由助手按冻结框架逐项生成，不是已经部署的自动推理引擎。主要对照六项人工批准扩展；继承方法中的历史环境比较也出现遗漏，不能声称所有基线方法均已充分检验。

## 实际执行顺序
1. 核对 v0.3 封存哈希；按既有时间顺序选择首个留出472，未先读内容。
2. 保存 target_metadata.json、protocol.json；取得两篇原新闻快照，一篇返回404。补充2023-10-16白宫访问计划声明的存档摘要。
3. 保存 news_input.json、answer_before_subtitle.json，再生成 answer_lock.json。
4. 核对答案哈希，写入 exposure.json 后读取第472期原字幕并比对原登记哈希。643条全部读取，读取分段0—229、230—459、460—642；完整原文在 reading.txt / target_transcript.json。
5. 保存 comparison.json；六项逐项对照，三个重点人工审阅项。原答案与冻结规则不回填。
6. 结构检查及两个负向检查、隔离Edge浏览器交互检查通过。

## 发现
- 系统识别支持表态不等于执行、参与方内部约束。
- 核心遗漏：博主从访问安排改变、停火传闻与官方否认、撤离迹象，推断以方管理控制可能脱节，解释美国为何亲自介入。系统只停留在普通分歧可能妨碍执行。
- 讲话者角色约束：博主认为“能支持双线”是财长在该位置不得不给出的回答，并进一步推断心虚；系统未复现这段具体推理。这个推断仍是博主观点。
- 博主等待访问后的言辞更新判断，并提出“起码3—5天和平”。完整保留，但和平的范围与起算点不清；暂不对历史结果评分。
- C06 没有找到充分对应的退出条件论证，明确标为证据不足；不强行匹配。
- 历史成功能否复制取决于环境（cue446—531）也未进入系统原答案。单次运用遗漏不等于框架必然无法表达，不应立刻修改规则。

## 来源和检验边界
- https://www.cls.cn/detail/1486755
- https://www.cls.cn/detail/1486209
- https://www.cls.cn/detail/1487000：空articleDetail，errno404，不当作已读证据。
- https://www.presidency.ucsb.edu/documents/statement-press-secretary-karine-jean-pierre-president-bidens-travel-israel-and-jordan ：官方声明的第三方存档；只使用当时宣布的计划。

获取记录：web.open三篇CLS均不可访问；首次Python请求遇到WinError10013，随后获自动审查放行，以只读方式下载上述三页。两篇取得文章及ctime，一篇404；原始响应HTML和解析JSON均在sources。没有上传本地材料。

时间口径为2023-10-17日级上界，无法确认视频与同日新闻精确先后。检索时看到更晚的访问及约旦行程取消/医院爆炸摘要，已在news_input.json登记；不纳入事实台账，但认知接触不可撤销。因此本例只能作历史材料上的方法迁移对照，不作干净的时序盲测或历史收益回测。

两篇新闻为媒体报道，未做全面独立事实核验；丢失一篇导致新闻输入与博主不完全等量。一次对照不能证明方法通用有效。主观差异判断等待用户审阅，工程测试通过不替代人工验收。

## 人工操作
打开 TRACE.html。审阅R01核心链、R02角色约束、R03时间判断三项。无需修改时选“准确，无需修改”；需修改时填写意见；不确定可明确选择。可查看连续原话和整期字幕。下载 JSON 后提交。本地暂存是浏览器备份，不等于仓库已收到新审阅。
自动下载使用浏览器配置的下载目录；本页不承诺能静默保存至指定工程目录。

## 页面QA
环境：file页面，Edge/Playwright，1440×1000、390×844。Browser plugin not available，使用既有Playwright，无新增依赖。
身份、非空白、无错误遮罩、控制台、截图及交互检查通过。测试路径：待审定位→展开证据→整期定位→填写→刷新恢复→部分/完整下载→导入往返；错误版本、重复/未知编号和非法选项均拒绝且保留原填写。桌面/手机截图已目视检查。其他浏览器未验证；测试选择不是人工审阅。
脚本和原始stdout/stderr、测试JSON与截图：G:/youhegaojian/review-ui-qa/holdout472/。

## 命令与产物
按顺序执行工程 .venv/Scripts/python.exe -X utf8，脚本为本目录 prepare.py、freeze_answer.py、expose.py、build_comparison.py、validate.py。
prepare.py只有公开新闻网络下载需要允许网络；其余为本地处理。构建/曝光脚本会重写时间和产物，封存后不可重跑以伪造未曝光过程；只能新建版本。
UI命令：C:/Users/无语/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe G:/youhegaojian/review-ui-qa/holdout472/check.cjs。
freeze.stdout.log / freeze.stderr.log 保存答案封存输出；validation.stdout.log / validation.stderr.log 保存最终检查原始输出。validation.json 保存结论。manifest.json 封存本目录文件。

## 当前进度与下一步
第472期已曝光，不能再标作未读留出；其余14份未读，名单在comparison.json及progress.json。当前等待三项人工对照审阅；之后决定仅改运用流程还是另拟新版本规则。后续案例先固定各自新闻和答案，再开目标字幕。事实与预测核验尚未执行，不填通过。