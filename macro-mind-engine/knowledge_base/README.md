# 外部资料时间数据库

2026-10-09。保存新闻、研报、经济数据与每日市场行情，按资料公开时间重建信息集。它独立于作者观点和方法库，不把作者的推断当作外部事实。

数据库：[public_information.sqlite3](public_information.sqlite3)。当前为本地SQLite初版，支持命令行检索与JSON记录导入；未建设网页或语义搜索，也未配置自动抓取任务。

最新数值接入见[首批历史数据报告](batches/historical_001/REPORT.md)：15条股指收盘、5条当期CPI数据，有限日期覆盖，尚非自动行情服务。

## 已有数据

- 3篇新闻正文：环球网拜登讲话、纽约时报中文网国际关系分析、财联社2023-10-20环球市场。共4个来源条目，另1篇Reuters新闻保留待获取状态。
- 4条视频与登记来源关联。来源被登记不等于作者逐句引用，关系类型单列。
- 16个每日行情品种目录；另建6个明确口径的股指序列（15条收盘值）及5个经济序列（5条CPI值）。目录准备完成不代表历史数据覆盖完成。
- 仅扫描已曝光476、478两期字幕中的“研报/研究报告”字样，没有命中；这不是全库研报提取结果。没有编造报告名称或内容。
- 未读取剩余九份留出字幕，未改变任何旧实验新闻包。财联社文章现在进入独立资料库，不追溯补入旧实验。

## 时间和版本约定

新闻、研报、经济数据以有出处的公开时间为准，另外保存抓取时间（已知时）、数据库收录时间及原件指纹。事件日期、数据所属月份和文章公开时间不得混用。

仅精确到分钟时，保留该分钟的起止区间，查询以区间末为准。只知道公开日期、不知道时分时，保存该时区一整天的可能区间；同日中午查询不会自动认为该资料已公开。公开时间未知的资料不进入按时点的信息集查询，但可保存待查线索。视频时刻未知时，不擅自假定当天全部资料均可用。

后续更新和修订新增版本，不覆盖旧正文或旧数值。查询按截止时间选择当时已公开的版本；known-by可进一步限定数据库当时已收录的记录。默认查询依照来源公开时间，不拿2026年收录时间冒充2023年发布时间。

三篇新闻都是先前于2026年获取的快照，虽有2023年发布时间，尚未独立验证正文就是当年版本。结果会返回metadata_only状态；strict-version模式只接纳已验证的历史版本，因此严格查询不返回这三篇。首批新增股指报道也保留metadata_only；CPI官方当期历史稿单列archive_verified，边界详见批次报告。收录并不自动证明历史正文身份。

经济数据保存指标口径、所属时期、初值/修订值和每个版本公开时间。历史查询不能使用后续修订值。FRED/ALFRED的实时版本机制提供了类似区分：[官方说明](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html)。

## 首批每日行情范围

| 类别 | 目录 |
|---|---|
| 中国股指 | 上证指数、深证成指、沪深300、创业板指 |
| 美国股指 | 标普500、纳斯达克综合指数、道琼斯工业平均指数 |
| 商品期货 | WTI、布伦特、COMEX黄金、COMEX铜 |
| 汇率 | USD/CNY、USD/CNH、EUR/USD、USD/JPY、GBP/USD |

这是按用户范围制定的初始目录，可按视频需要扩展。原目录ID仍标记PENDING；首批已确认股指记录使用_PRESS_CLOSE后缀的新序列。口径未确定的目录不允许导入正式数值。

股指保存指数点位，不能用ETF价格替代。期货需识别具体合约；连续序列另记供应商、换月与调整规则，不能当作一张长期不变的合约。close和settlement是独立字段，查询默认只取close。CME对每日结算价有专门定义和程序，不能悄悄以其替代要求的收盘价：[CME说明](https://www.cmegroup.com/market-data/daily-settlements.html)。

外汇需确定供应商、时区及日界线；人民币中间价、参考汇率及fixing不能冒充close。目录中的时区只是拟用市场时区，尚不代表已经确认供应商日线口径。

导入close必须提供session_close_at，记录公开时间不得早于收盘时间或引用证据的公开时间。只有当天交易已完成且信息可得，才允许用于当时分析。每日收盘序列不能验证日内“先跌后涨”的具体路径。

## 研报与无链接资料

先保存字幕原话、cue/时间戳、机构及题名线索；原件未找到时保持pending，不能把搜索到的相似报告默认为同一份。确认后新建原件记录、公开时间及匹配证据，再处理待采集队列。发现日期、报告封面日期和公开传播日期分开，付费或未知公开状态不能假定人人当时可得。

仅需追踪未找到原件的报告时，可创建research_report类型的pending文档及mention，正文留空、不创建版本。数据库已有这个入口，尚未开展全开发语料的语义扫描。

## 使用方式

在macro-mind-engine目录执行，使用项目虚拟环境：

```powershell
.venv/Scripts/python.exe -m macromind.knowledge stats
.venv/Scripts/python.exe -m macromind.knowledge search 拜登 --as-of 2023-10-19T12:00:00+08:00
.venv/Scripts/python.exe -m macromind.knowledge search --as-of 2023-10-20T07:00:00+08:00 --strict-version
.venv/Scripts/python.exe -m macromind.knowledge series
.venv/Scripts/python.exe -m macromind.knowledge pending
.venv/Scripts/python.exe -m macromind.knowledge observations US_SP500_PRESS_CLOSE --as-of 2023-10-20T07:00:00+08:00
```

最后一条返回截至该时点已公开的10月18日、19日标普500收盘记录。原目录US_SP500仍无值，请使用上例的明确口径序列。

单条JSON导入：add-document、add-version、add-mention、add-series、add-observation、add-queue，各接收一个UTF-8 JSON文件，对应KnowledgeStore同名方法参数。版本导入返回不可覆盖的ID，供observation.source_version引用。resolve-queue接受queue_id与resolution，保留原待查原因并记录处理依据。改变品种口径使用新序列ID，不能覆盖原定义。

完整接口见[src/macromind/knowledge/store.py](../src/macromind/knowledge/store.py)。已有资料导入脚本seed_existing.py可重复运行，不产生重复正文和数值。

## 验证与后续边界

基础版本9项测试通过；首批数值接入后共11项通过（见批次报告）。基础测试涵盖：公开时间截止、时区及夏令时、日期精度、未知时间排除、正文版本、经济数据修订、收盘与结算隔离、研报线索不冒充正文、待查队列处理。实际库重复导入及SQLite完整性检查通过，详见[validation.json](validation.json)。

下一阶段是数据接入：围绕开发视频时段获取上述品种的历史日线，确认来源口径后导入正式序列；经济指标按视频实际使用情况补充公开发布与修订版本；扩大开发语料研报线索识别。尚未完成自动数据源接入或全历史回填，不把当前目录数量当作数据覆盖率。
