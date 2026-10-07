# Golden Sample #003 阅读导览

完整报告按V0.3要求的24节及13问排列；JSON保留全部字段。

**状态：抽取完成，Review待处理。没有使用3月3日17:30之后的战况或油价为主播预测评分。**

## 主要发现

1. 储油空间耗尽与消费库存耗尽不同；20多天→30→60不能证明政治停战上限。
2. 航道控制→定价权→美国独享收益缺关键证据。
3. 120与200必须附情景和归属；新闻中的200属于机构极端情景。
4. Platts部分报价规则变化属于有限Event；未建立StructuralProcess或Contradiction。
5. 未实际听音，所有ASR纠错保留候选。

## 数量

```json
{
  "source_count": 13,
  "source_family_count": 7,
  "claim_count": 130,
  "creator_claim_count": 108,
  "external_context_claim_count": 15,
  "model_claim_count": 7,
  "claim_occurrence_count": 133,
  "event_count": 9,
  "structural_process_count": 0,
  "indicator_count": 18,
  "observation_count": 18,
  "argument_count": 12,
  "mechanism_count": 3,
  "thesis_count": 3,
  "forecast_count": 46,
  "contradiction_count": 0,
  "heuristic_count": 2,
  "review_queue_count": 36,
  "review_severity_counts": {
    "Critical": 4,
    "High": 20,
    "Medium": 11,
    "Low": 1
  }
}
```

## 核心Argument距离

|链|边数|最长路径|模型边|显式捷径|最脆弱处|
|---|---:|---:|---:|---:|---|
|AR01 不完全封锁也能影响运输成本|8|6|3|1|AR01-E6|
|AR02 从公开讲话推断美国失控|3|2|0|0|AR02-E2|
|AR03 首周撤退分支|3|3|0|0|AR03-E2|
|AR04 追加行动分支到120|2|2|0|0|AR04-E2|
|AR05 储油容量推到60天停战上限|8|7|3|1|AR05-E3|
|AR06 历史封锁经验外推|2|2|0|0|AR06-E1|
|AR07 中东失利外推到东亚|5|3|0|0|AR07-E2|
|AR08 战败与霸权信誉|4|3|2|0|AR08-E3|
|AR09 控制海峡到长期高油价和收益独占|6|4|4|2|AR09-E4|
|AR10 战事和AI资本支撑|5|3|2|0|AR10-E4|
|AR11 美元短期避险与长期信用透支|2|2|0|0|AR11-E2|
|AR13 Platts规则响应：模型补充分析|2|1|1|0|AR13-E1|

## 价格情景（单位/基准未说清时不补）

|归属|条件|窗口|价格方向|Claim|
|---|---|---|---|---|
|A9527|基线：冲突未迅速终结且未出现极端破坏|战争头一周；起点待核|上涨到80–90，约20%–30%|C025|
|A9527|美国撤退且伊朗开放|撤退后未明|适度回落或停止上涨|C032|
|A9527|升级并扰乱海运、成本提高|首周后追加行动约一个月|约120|C035|
|A9527|撤退/和谈关联；与120分支的相容性待核|约40天|90–110并可能回落|C037|
|A9527|当前局面延续；未明示失效触发器|约一个月|缓慢上涨，无巨大波动|C075|
|A9527|突发大涨且预期尚未到位|急涨后未明|回调|C076|
|A9527|伊朗控制海峡|伊朗控制后|回落|C079|
|A9527|美国控制海峡|相当长|100–126（ASR待核）|C080|
|A9527|供应定价控制且油价提高|美国控制之后|仅美国获益|C083|
|A9527|伊朗掌握海峡|伊朗获胜后|六七十或七八十|C085|
|A9527|美国获胜|长期|100甚至120|C086|
|AJPM|外运受阻使储罐满并减产|战争超过三周后|120美元/桶|X01|
|ADB|海峡全面封闭的极端情景|unknown|200美元/桶|X02|
|ABOA|战争快速结束|战争快速结束后|60–70美元/桶|X03|
|ABOA|伊朗攻击邻国能源设施|unknown|超过100美元/桶|X14|

## 阅读文件

- golden_sample_003_report.md：完整报告
- golden_sample_003.json：完整机器可读对象及审计辅助表
- source_segments.json：Claim对应原文、cue与时码
- source_versions.json：直播条目cutoff名单
- review_queue.json：按严重性分类的待审问题
- validation.json：结构校验结果
- source_snapshots/：工具返回的网页片段；不是完整历史网页存档

## 核查来源

- [财联社油气情景报道](https://www.cls.cn/detail/2300559)：机构预测各有条件，储油约束是出口受阻后库容占满。
- [财联社滚动直播](https://www.cls.cn/detail/2298102)：只采纳版本表中cutoff前条目。
- [Platts成品油MOC通知](https://www.spglobal.com/energy/en/pricing-benchmarks/our-methodology/subscriber-notes/030226-platts-suspends-bids-and-offers-for-persian-gulf-ports-within-strait-of-hormuz-in-middle-east-refined-products-moc-assessment-process)：只验证特定报价流程调整。
- [EIA历史统计说明](https://www.eia.gov/todayinenergy/detail.php?id=65504)：分母和年份可核查，重刊版本时间仍待确认。
