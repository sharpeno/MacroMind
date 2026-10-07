# 方法表达与追溯原型 v0.1

当前原型从已确认的EP002/C23出发，将方法拆成条件、问题和步骤，再把案例证据逐项对应。通用执行器不包含9527的专用判断分支；方法内容在JSON中。但目前只实际构建和测试了一套方法，不能据此声称已经验证多分析师系统。

## 如何查看

打开[公开案例追溯页](../../phase1/method_prototype/run_001/public_case_trace_v2/TRACE.html)，点击某个步骤，再展开“原话与案例证据”。每一步同时展示方法原话、案例材料、助手映射理由和缺失信息。页面只读；本轮没有新增必须人工逐项填写的审核任务。

- [方法卡](../../phase1/method_prototype/run_001/method.json)
- [案例输入](../../phase1/method_prototype/run_001/public_case.packet.json)
- [实际分析输出](../../phase1/method_prototype/run_001/public_case_trace_v2/analysis.json)
- [实现与验证报告](../../phase1/method_prototype/run_001/REPORT.md)

## 本次示例的含义

使用2024-08-23鲍威尔官方讲话的两个短选段，属于新加入系统的历史案例，并非最新新闻。方法来自后续整理的材料，因此显式标记为retrospective_transfer（回看迁移），不算当时可用的预测或历史回测成绩。

结果为INCOMPLETE_METHOD_EVIDENCE：材料能支持进入“行动主体如何认识并调整做法”的提问，却不足以证明提前识别、预备方案、与群体同行和择机带领纠错的完整过程。缺证据不等于现实中没有这个过程。

方法原话和案例证据严格分开；EP002/C16仍是博主假想应用，没有被改写成现实央行讲话。用户确认过方法文字，不代表本次助手整理的适用条件与映射另获人工确认。

## 程序实际上做什么

1. 接受结构化方法、案例和来源指纹；要求每个条件与步骤都有映射。
2. 检查文件SHA-256、原话片段、记录定位、来源用途及材料日期。
3. 根据已编写的supported/contradicted/unknown映射，生成状态、开放问题和追溯页。
4. 只写新运行目录，拒绝覆盖旧产物。始终保留语义未验收、方法有效性未验证、Skill未准入。

程序不自动阅读新闻得出这些映射，也不判断锚定原话是否真的支持理由。测试专门保留一个“引用真实但推理错误”的例子，证明引用检查不会被包装成语义验证。方法条件与提问是助手操作化，不是原视频中的形式化规则。

## 状态含义

| 状态 | 含义 |
|---|---|
| NOT_APPLICABLE | 有条件反证，当前材料不适合套入这套方法 |
| INSUFFICIENT_SCOPE_EVIDENCE | 还不能确定是否适用 |
| COUNTEREVIDENCE | 某个方法步骤存在反证 |
| INCOMPLETE_METHOD_EVIDENCE | 条件可进入检查，但步骤证据不完整 |
| TRACE_COMPLETE_NOT_VALIDATED | 显式映射完整，仍不证明事实、因果或方法有效性 |

## 新案例运行

在工程目录，以实际新目录名替换example_next；重复运行同一输出会被拒绝：

```powershell
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe scripts/run_method_prototype.py --packet phase1/method_prototype/run_001/public_case.packet.json --output phase1/method_prototype/example_next
```

输入由本轮公共案例packet示范，日期和来源指纹不能省略。as_of_analysis模式禁止使用截止日期之后才可用的方法；历史迁移需要明确选择retrospective_transfer。日期是输入元数据，程序仅检查其一致性，不自动查证原始发布时间。

下一步应扩大“证据足以回答的方法问题”的覆盖：选一份含行动前准备、行动过程及后续结果的完整案例，检验条件和步骤是否可操作；再引入第二种方法，比较它们关注的问题和分歧。当前只读页不是自动分析产品，也未扩展冻结本体。
