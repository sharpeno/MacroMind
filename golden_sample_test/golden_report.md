# Golden Sample #001 — 第765期（V0.1 Draft）

## 结论
本样本证明 MacroMind 的四层结构可用：Evidence → Knowledge → Reasoning → Framework。
最有价值的不是视频摘要，而是以下三类结构化资产：

1. **来源冲突**：主播关于“决议前市场认为只加一次”的叙述，与其列出的决议前财联社参考文发生直接冲突。
2. **作用层次差异**：主播说加息解决不了能源供给源头；沃什则明确把Fed作用限定为防止二级、三级通胀扩散。这不是简单真假二选一。
3. **叙事拆解**：主播对沃什“经济走强/资本竞争/地缘政治”三项长期收益率解释逐一重新定位为表象、结果或更深层结构信号。

## 统计
- Sources: 9（其中用户给出的内容/参考源7，新增官方验证源2）
- Semantic segments: 9 
- Key claims: 33
- Events: 5
- Assessments: 5（示例核心项）
- Arguments: 7
- Mechanisms: 5
- Theses: 5
- Forecasts: 6
- Candidate heuristics: 4
- Review queue: 13

## 当前不应升级为“已验证框架”的内容
- “结构力量优先于政治人物”目前只是 Candidate Heuristic。
- “美国安全资产属性结构性弱化”只是高推理距离 Thesis，不是事实。
- “AI泡沫即将破裂”是 Forecast，不是事实。
- “美国已进入滞胀”当前资料包不足以验证。

## V0.1 对Schema/Extraction Spec的反馈
1. `Claim.verification` 最终应逐步迁移为独立 Assessment；本草稿为便于人工阅读暂时保留摘要字段。
2. 必须增加 `source_conflict` 和 `forecast_lineage` 两类 Review Queue。
3. `Argument` 中应明确区分 explicit / strongly_implied / model_reconstruction。
4. Forecast 必须有 resolvability 概念；主播很多预测方向明确但时间窗口模糊。
5. Narrative Deconstruction 应成为正式阶段，而不是普通 Claim Verification 的附属步骤。
