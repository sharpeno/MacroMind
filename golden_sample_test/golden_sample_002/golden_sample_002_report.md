# MacroMind Golden Sample #002 — V0.2 可审计抽取

视频：《第七百六八期》当前背景下如何深刻认识中国金融结构变迁

知识截止：**2026-09-21T10:32:21+08:00**。抽取与核验日期：2026-09-24。

主文件是本报告和 [完整结构化JSON](G:/youhegaojian/golden_sample_test/golden_sample_002/golden_sample_002.json)。原句与字幕位置见 [逐Claim证据](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md)，完整731条字幕的独立层见 [转写层](G:/youhegaojian/golden_sample_test/golden_sample_002/normalized_transcript.md)。本目录未改动任何原始TXT、SRT、MP3或MP4。

## 1. EXECUTIVE EXTRACTION REPORT

**status：抽取完成，待音频及数据复核；尚不可标为已验证Golden。** 原字幕跨度为00:00:00,090—00:35:11,540，分为17个语义主题。125条来自主播表达或其转述，另6条明确标为model_reconstruction。

最大不确定性是语音未实听、数字口径不全，以及从比例变化跨越到成本、偿债能力和国际竞争的推理。已发现本地音视频并做哈希，不能因此声称已经听验。accepted ASR correction及speaker_slip_confirmed均为0；候选专名修正不改原话。

核心结构判断：本期确实围绕融资渠道和投向变化展开，但“隐债基本解决”“银行总利润必降”“中国挑战美国风险资本优势”均不能仅凭这些比例进入Verified Knowledge。金融结构变迁更适合持续过程；关于过程的解释才升级为少量Thesis。

**post-cutoff contamination：未将截止后结果用于原始Argument。** 检索发生在截止后，网页历史版本未获得。日本央行当前首页的9月24日状态已隔离；采用9月18日宣布、9月24日生效的原决定，区别已知未来安排与事后事实。没有进行事后预测评分。

## 2. SOURCES

| ID | Source / role | time | version | read_status |
| --- | --- | --- | --- | --- |
| SRC01 | 原视频 / primary_evidence | 2026-09-21T10:32:21+08:00 | SHA256:4ff4d5cb5cd87344970dfe47661322bd4a77fffd246f6f065dc45afc8b405d41 | registered_and_hashed_not_played |
| SRC02 | 自动转写TXT / primary_evidence | 2026-09-21T10:32:21+08:00 | SHA256:f8ab609c0fb2df5ec8d9ea9ca780b5ed6516ea87bdc3c64f07437a8d631e8722 | full_text_read |
| SRC03 | SRT字幕 / primary_evidence | 2026-09-21T10:32:21+08:00 | SHA256:e265640a84a5b8ee5ede256601b2190a03c5403aa6fe63bf40650bd241f5b8ad | full_text_read |
| SRC04 | 本地音频 / primary_evidence | 2026-09-21T10:32:21+08:00 | SHA256:a998602bb6985582371e8847c58dfd083dde6c72936097fd8c0a8595491014ab | registered_and_hashed_not_played |
| SRC05 | [财联社参考文章](https://www.cls.cn/detail/2484394) / creator_reference | 2026-09-16T09:43:00+08:00 | live_page_retrieved_2026-09-24; historical snapshot unavailable | full_article_read; HTML returned |
| SRC06 | [潘功胜求是原文](https://www.qstheory.cn/20260915/1c41fc49b4b44db4b2550ddd41f40315/c.html) / verification_added | 2026-09-16T09:00:00+08:00 | live_page_retrieved_2026-09-24; historical snapshot unavailable | full_article_read |
| SRC07 | [发改委：平陆运河正式开工建设](https://www.ndrc.gov.cn/fggz/dqjj/202209/t20220909_1368749.html) / verification_added | 2022-09-09 | live_page_retrieved_2026-09-24; historical snapshot unavailable | search_returned_article_text_read |
| SRC08 | [发改委：平陆运河全线动工建设](https://www.ndrc.gov.cn/fggz/dqjj/202305/t20230529_1368966.html) / verification_added | 2023-05-29 | live_page_retrieved_2026-09-24; historical snapshot unavailable | search_returned_article_text_read |
| SRC09 | [FOMC statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm) / verification_added | 2026-09-16T14:00:00-04:00 | live_page_retrieved_2026-09-24; historical snapshot unavailable | search_returned_full_statement_read |
| SRC10 | [日本央行9月18日决定](https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2026/k260918a.pdf) / verification_added | 2026-09-18T11:54:00+09:00 | live_page_retrieved_2026-09-24; historical snapshot unavailable | PDF_extracted_text_all_6_pages_read; not_visual_QA |
| SRC11 | [ECB monetary policy decisions](https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp260910~314e508016.en.html) / verification_added | 2026-09-10 | live_page_retrieved_2026-09-24; historical snapshot unavailable | search_returned_full_statement_read |
| SRC12 | [财政部2024年中国财政政策执行情况报告](https://www.mof.gov.cn/zhengwuxinxi/caizhengxinwen/202503/t20250324_3960464.htm) / verification_added | 2025-03-24 | live_page_retrieved_2026-09-24; historical snapshot unavailable | relevant_search_excerpt_read; not_full_report |
| SRC13 | [财政部2024和2025地方专项债务余额表](https://yss.mof.gov.cn/2025zyczys/202503/t20250324_3960454.htm) / verification_added | 2025-03-24 | live_page_retrieved_2026-09-24; historical snapshot unavailable | search_returned_table_and_notes_read |
| SRC14 | [帝国战争博物馆：1938慕尼黑和平文件说明](https://www.iwm.org.uk/sites/default/files/documents/2017_05_22_transforming_iwm_london_2.pdf) / verification_added | 2017-05-22（URL日期，文档确切首发unknown） | live_page_retrieved_2026-09-24; historical snapshot unavailable | search_excerpt_only; temporal_provenance_not_fully_verified |
| SRC15 | 用户提供视频标题、发布时间与参考链接 / primary_evidence | message_time_unknown | current_conversation | read |
| SRC16 | 已有Golden #001摘要（registry search only） / verification_added | unknown | SHA256:20e588f192b8db87c3b24dd261ca8dc6d26c742d507ad0ea4fbff3fa067eaec4 | full_read_for_registry_search_only |
| SRC17 | [日本央行当前首页（排除使用）](https://www.boj.or.jp/en/) / post_cutoff_source | page includes rates effective 2026-09-24 | search snapshot 2026-09-24 | search_excerpt_seen_quarantined |
| SRC18 | [中国人民银行人民币国际化报告（2025），熊猫债章节](https://www.pbc.gov.cn/huobizhengceersi/214481/3871621/5885243/2025103108544623039.pdf) / verification_added | 2025（报告年度）；2025-10-31（文件路径日期） | PDF retrieved as search excerpt 2026-09-24; no historical archive | relevant_search_excerpt_read_not_full_report |
| SRC19 | [SEC投资者教育公告：What Are Corporate Bonds?](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/what-are) / verification_added | 2013-06-04 | dated bulletin retrieved as search excerpt 2026-09-24 | definition_and_equity_comparison_excerpt_read |

SRC01—04是同一视频证据家族，TXT/SRT不是独立验证；SRC05是SRC06文章的转载来源，不能叠加证据权重。用户仅提供一个参考链接，没有完整视频简介或平台视频URL。检索发现但未采用的旁支结果不作为支持来源；年度原始金融数据未找到，不能宣称核实完毕。

## 3. TRANSCRIPT CORRECTIONS

### accepted ASR corrections

none。

### candidate corrections / needs_audio_review

以下均未应用。高置信是文字和实体匹配置信度，不是已听验置信度。

| ID | 原转写 | 候选规范形式 | 置信度 | SRT cues | 处理 |
| --- | --- | --- | --- | --- | --- |
| TC01 | 潘刚盛 | 潘功胜 | high | 1—1 | needs_audio_review; applied=false |
| TC02 | 潘光盛 | 潘功胜 | high | 280—280 | needs_audio_review; applied=false |
| TC03 | 潘东升 | 潘功胜 | high | 669—674 | needs_audio_review; applied=false |
| TC04 | 求市 | 求是 | high | 1—1 | needs_audio_review; applied=false |
| TC05 | 平论运河 | 平陆运河 | high | 438—478 | needs_audio_review; applied=false |
| TC06 | 平路运河 | 平陆运河 | high | 432—432 | needs_audio_review; applied=false |
| TC07 | 评论和 | 平陆运河 | medium | 439—439 | needs_audio_review; applied=false |
| TC08 | 闪击波澜 | 闪击波兰 | high | 137—137 | needs_audio_review; applied=false |
| TC09 | 清江 | 钦江 | high | 457—461 | needs_audio_review; applied=false |
| TC10 | 素台德 | 苏台德 | high | 139—139 | needs_audio_review; applied=false |
| TC11 | worker | 沃尔克 | medium | 31—31 | needs_audio_review; applied=false |
| TC12 | 退居慈禧 | 退居次席 | high | 276—276 | needs_audio_review; applied=false |
| TC13 | 隐形债务 | 隐性债务 | high | 301—301 | needs_audio_review; applied=false |
| TC14 | 专细查 | 赚息差 | high | 511—511 | needs_audio_review; applied=false |
| TC15 | 表白业务 | 表外业务 | high | 595—595 | needs_audio_review; applied=false |
| TC16 | 涉容涉零 | 社融/信贷？ | low | 282—282 | needs_audio_review; applied=false |
| TC17 | 134年 | 十三四年？ | medium | 445—445 | needs_audio_review; applied=false |
| TC18 | 20% | 2%？ | medium | 339—339 | needs_audio_review; applied=false |
| TC19 | 百分之百2020年上半年 | 2026年上半年？ | medium | 502—502 | needs_audio_review; applied=false |
| TC20 | 100万就是0万人民币 | unknown | low | 703—704 | needs_audio_review; applied=false |
| TC21 | 进攻/天河堡 | unknown（或指慕尼黑/其他会面地点） | low | 144—144 | needs_audio_review; applied=false |

数字禁止按算术静默修正。“134”不能擅自改成“十三四”，“20%”不能自动改“2%”；“10%股票占比”保留为C080，另做算术诊断。

## 4. SOURCE SEGMENT ANNOTATIONS

speaker_slip_confirmed：none。self_correction仅指文本可见的自我重述，不声称音频确证。疑似事实/概念错误均留Review。

| ID | annotation_type | cues | 说明 |
| --- | --- | --- | --- |
| AN01 | self_correction | 393—394 | 转写中先说低成本换成，接着改说高成本换成低成本；保留两次表述。 |
| AN02 | self_correction | 513—514 | 转写中直接融资改为间接融资；不将前半句独立认作金融理论。 |
| AN03 | self_correction | 545—546 | 百分之百随即限定为接近百分之百。 |
| AN04 | ambiguous_reference | 144—145 | 本人在转写中说我忘了；地点不明。 |
| AN05 | ambiguous_reference | 25—25 | 大家的Population未知。 |
| AN06 | ambiguous_reference | 282—285 | 负增长与剪刀差指标和基期未明确。 |
| AN07 | mixed_fact_and_opinion | 300—323 | 朗读融资分类说明后转入闭门谈判实操解释。 |
| AN08 | mixed_fact_and_opinion | 487—508 | 企业融资比值是引述数据；相对成本更低是主播推论。 |
| AN09 | mixed_fact_and_opinion | 548—556 | 存量占比引述与股票10%算术推断分开。 |
| AN10 | mixed_fact_and_opinion | 608—655 | 投向数据与发展机会判断、血液类比分开。 |
| AN11 | mixed_fact_and_opinion | 715—725 | 以已经观察到的趋势修辞强化中美竞争解释，官方并未直接提出该竞争命题。 |

## 5. SEMANTIC SEGMENTS

| segment_id | start | end | topic | cues |
| --- | --- | --- | --- | --- |
| SG01 | 00:00:00,090 | 00:01:59,250 | 文章时点、央行立场与外部加息 | 1—23 |
| SG02 | 00:01:59,250 | 00:05:11,120 | 紧缩情景、美元信用与短期策略 | 24—95 |
| SG03 | 00:05:11,120 | 00:08:19,220 | 债权人损失厌恶及二战历史类比 | 96—168 |
| SG04 | 00:08:19,220 | 00:09:09,730 | 文章结构与本期范围 | 169—190 |
| SG05 | 00:09:09,970 | 00:11:15,350 | 融资结构总论与直接/间接融资定义 | 191—231 |
| SG06 | 00:11:15,350 | 00:13:07,290 | 2013年分界、信任及2025年融资增量 | 232—276 |
| SG07 | 00:13:07,290 | 00:14:06,580 | 文章安抚功能与结构信息 | 277—299 |
| SG08 | 00:14:07,570 | 00:18:26,560 | 化债、成本叙事与谈判过程 | 300—389 |
| SG09 | 00:18:26,560 | 00:19:54,350 | 从融资分类变化推论化债成效 | 390—431 |
| SG10 | 00:19:54,350 | 00:22:43,530 | 平陆运河投资与政府信用信号 | 432—480 |
| SG11 | 00:22:43,530 | 00:25:20,060 | 企业融资比值、相对成本与国家信用空间 | 481—532 |
| SG12 | 00:25:20,060 | 00:27:15,540 | 存量结构、股票占比与未来比例 | 533—562 |
| SG13 | 00:27:15,540 | 00:29:05,910 | 银行利润、业务转型及职业选择 | 563—604 |
| SG14 | 00:29:06,090 | 00:31:12,550 | 信贷投向、机会识别与血液类比 | 605—655 |
| SG15 | 00:31:12,550 | 00:32:44,730 | 科技企业生命周期与非银行融资 | 656—696 |
| SG16 | 00:32:44,730 | 00:34:21,030 | 中美早期风险资本比较与汇率叙事 | 697—712 |
| SG17 | 00:34:21,140 | 00:35:11,540 | 人民币资本竞争结论与收束 | 713—731 |

按论证主题切分，边界采用SRT cue粒度；部分20秒长cue内包含多主题，未假装逐词对齐。

## 6. CLAIMS

以下每条均可回溯到同名SS-C…证据。`asserted_at`是录制时间unknown、发布时间proxy及SRT偏移的结构，不将发布时间加偏移冒充真实发言时刻。Claimant A001=9527，A002=潘功胜（由9527转述）；model=模型补出的条件。原文重复通过ClaimOccurrence合并，损坏重读不覆盖首次读数。

### C001 · 潘功胜在9月13日发表本期讨论的求是文章。

- `segment_id`: SG01；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:00:00,090","media_offset_end":"00:00:20,090","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2026-09-13（年份依本期语境）；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: one_article；`quantifier`: one；`certainty_expressed`: 肯定陈述。

- `source_segment`: [SS-C001](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c001)；`atomicity_group_id`: AG-SG01；`information_gain`: medium。

### C002 · 美联储刚刚加息。

- `segment_id`: SG01；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:00:00,090","media_offset_end":"00:00:40,090","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2026-09 视频发布前；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Federal_Reserve；`quantifier`: one；`certainty_expressed`: 肯定陈述。

- `source_segment`: [SS-C002](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c002)；`atomicity_group_id`: AG-SG01；`information_gain`: medium。

### C003 · 日本央行也已加息。

- `segment_id`: SG01；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:01:33,820","media_offset_end":"00:01:37,570","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2026-09 视频发布前；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Bank_of_Japan；`quantifier`: one；`certainty_expressed`: 肯定陈述。

- `source_segment`: [SS-C003](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c003)；`atomicity_group_id`: AG-SG01；`information_gain`: medium。

### C004 · 欧洲央行也加息。

- `segment_id`: SG01；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:01:37,570","media_offset_end":"00:01:39,180","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2026-09 视频发布前；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: ECB（欧洲依语境解析）；`quantifier`: one；`certainty_expressed`: 肯定陈述。

- `source_segment`: [SS-C004](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c004)；`atomicity_group_id`: AG-SG01；`information_gain`: medium。

### C005 · 潘功胜写文章时应已深刻把握美联储的处境及选择。

- `segment_id`: SG01；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: motive_attribution；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:00:20,090","media_offset_end":"00:01:00,090","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 文章写作时，确切日期unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Pan_Gongsheng；`quantifier`: one；`certainty_expressed`: 我认为；应该；非常非常清楚。

- `source_segment`: [SS-C005](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c005)；`atomicity_group_id`: AG-SG01；`information_gain`: medium。

### C006 · 文章没有直接写外国却为中国之外金融系统变化提供背景定调。

- `segment_id`: SG01；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:01:08,240","media_offset_end":"00:01:23,910","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 本篇文章；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: one_article；`quantifier`: one；`certainty_expressed`: 我觉得；可能。

- `source_segment`: [SS-C006](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c006)；`atomicity_group_id`: AG-SG01；`information_gain`: medium。

### C007 · 2024年以来的宽松环境已经转为紧缩。

- `segment_id`: SG01；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:01:40,210","media_offset_end":"00:01:59,250","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2024至2026-09；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: global_financial_environment；`quantifier`: unknown；`certainty_expressed`: 彻底反过来。

- `source_segment`: [SS-C007](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c007)；`atomicity_group_id`: AG-SG01；`information_gain`: medium。

### C008 · 9527自称此前讲过八年宽松、两年紧缩的美元潮汐节奏。

- `segment_id`: SG01；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: retrospective。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:01:44,790","media_offset_end":"00:01:50,720","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 此前unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: 9527_prior_content；`quantifier`: one；`certainty_expressed`: 之前聊过。

- `source_segment`: [SS-C008](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c008)；`atomicity_group_id`: AG-SG01；`information_gain`: medium。

### C009 · 美元潮汐的通常节奏是八年宽松、两年紧缩。

- `segment_id`: SG01；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:01:44,790","media_offset_end":"00:01:59,250","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 历史区间unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: US_monetary_cycles；`quantifier`: unknown；`certainty_expressed`: 一般化陈述。

- `source_segment`: [SS-C009](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c009)；`atomicity_group_id`: AG-SG01；`information_gain`: medium。

### C010 · 大家普遍认为此次紧缩不会持续很久。

- `segment_id`: SG02；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:02:01,160","media_offset_end":"00:02:04,490","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 视频录制时unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: unspecified；`quantifier`: majority；`certainty_expressed`: 普遍。

- `source_segment`: [SS-C010](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c010)；`atomicity_group_id`: AG-SG02；`information_gain`: medium。

### C011 · 此次紧缩可能持续很长时间。

- `segment_id`: SG02；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:02:04,640","media_offset_end":"00:02:17,420","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 视频之后unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: US_monetary_policy；`quantifier`: unknown；`certainty_expressed`: 如果；可能。

- `source_segment`: [SS-C011](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c011)；`atomicity_group_id`: AG-SG02；`information_gain`: medium。

### C012 · worker所指时代美联储曾一下子加息到20%。

- `segment_id`: SG02；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:02:17,440","media_offset_end":"00:02:24,510","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 历史时期unknown（疑指沃尔克时期）；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Federal_Reserve；`quantifier`: one；`certainty_expressed`: 一下子；从未有先例。

- `source_segment`: [SS-C012](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c012)；`atomicity_group_id`: AG-SG02；`information_gain`: medium。

### C013 · 现有美债规模使美联储不能把利率升到此前所述高位。

- `segment_id`: SG02；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:02:26,870","media_offset_end":"00:02:35,200","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 当下及假设高利率情景；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: US_federal_debt；`quantifier`: unknown；`certainty_expressed`: 现在的说法。

- `source_segment`: [SS-C013](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c013)；`atomicity_group_id`: AG-SG02；`information_gain`: medium。

### C014 · 若利率升到所讨论高位，债务利息成本会超过美国GDP。

- `segment_id`: SG02；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: counterfactual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:02:37,320","media_offset_end":"00:02:51,550","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 假设高利率情景；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: US_federal_debt；`quantifier`: unknown；`certainty_expressed`: 就已经比GDP更高。

- `source_segment`: [SS-C014](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c014)；`atomicity_group_id`: AG-SG02；`information_gain`: medium。

### C015 · 暴力加息可能首先损害美元信用。

- `segment_id`: SG02；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:02:40,680","media_offset_end":"00:03:10,580","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来条件情景；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: USD_credit；`quantifier`: unknown；`certainty_expressed`: 可能最先。

- `source_segment`: [SS-C015](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c015)；`atomicity_group_id`: AG-SG02；`information_gain`: medium。

### C016 · 若竞争对手更差且缺替代品，美国仍能保持相对优势。

- `segment_id`: SG02；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:03:28,380","media_offset_end":"00:03:45,180","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 一般条件情景；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: US_and_alternatives；`quantifier`: unknown；`certainty_expressed`: 只要；就可能。

- `source_segment`: [SS-C016](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c016)；`atomicity_group_id`: AG-SG02；`information_gain`: medium。

### C017 · 美国可能从一开始就没有偿还债务的打算。

- `segment_id`: SG02；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: motive_attribution；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:03:56,170","media_offset_end":"00:04:04,740","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 债务形成时unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: US_government；`quantifier`: unknown；`certainty_expressed`: 有没有可能。

- `source_segment`: [SS-C017](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c017)；`atomicity_group_id`: AG-SG02；`information_gain`: medium。

### C018 · 美国可能利用激进加息的短期收益与长期副作用的时差过关。

- `segment_id`: SG02；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:04:04,740","media_offset_end":"00:04:41,970","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: US_policy_makers；`quantifier`: unknown；`certainty_expressed`: 是不是可能选择。

- `source_segment`: [SS-C018](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c018)；`atomicity_group_id`: AG-SG02；`information_gain`: medium。

### C019 · 美国在提高利率时仍不停扩表。

- `segment_id`: SG03；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:05:11,120","media_offset_end":"00:05:21,260","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 本轮紧缩，区间unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Federal_Reserve；`quantifier`: unknown；`certainty_expressed`: 不停。

- `source_segment`: [SS-C019](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c019)；`atomicity_group_id`: AG-SG03；`information_gain`: medium。

### C020 · 加息同时扩表会加快美债规模膨胀。

- `segment_id`: SG03；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:05:21,290","media_offset_end":"00:05:29,800","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: US_federal_debt；`quantifier`: unknown；`certainty_expressed`: 会。

- `source_segment`: [SS-C020](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c020)；`atomicity_group_id`: AG-SG03；`information_gain`: medium。

### C021 · 大量美债持有者可能因损失厌恶而更容忍美国政策风险。

- `segment_id`: SG03；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:05:29,800","media_offset_end":"00:06:00,290","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: large_Treasury_holders；`quantifier`: unknown；`certainty_expressed`: 会不会；可能。

- `source_segment`: [SS-C021](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c021)；`atomicity_group_id`: AG-SG03；`information_gain`: medium。

### C022 · 英法容忍德国挑衅是为将其引向对抗苏联。

- `segment_id`: SG03；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: motive_attribution；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:06:00,290","media_offset_end":"00:06:23,370","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 二战前；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: UK_and_France_governments；`quantifier`: unknown；`certainty_expressed`: 因果肯定。

- `source_segment`: [SS-C022](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c022)；`atomicity_group_id`: AG-SG03；`information_gain`: medium。

### C023 · 一战损失使二战前英法社会极度厌战。

- `segment_id`: SG03；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:06:32,610","media_offset_end":"00:06:55,640","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 一战后至二战前；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: UK_and_France_societies；`quantifier`: all；`certainty_expressed`: 肯定都不想再打仗。

- `source_segment`: [SS-C023](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c023)；`atomicity_group_id`: AG-SG03；`information_gain`: medium。

### C024 · 英法对德国闪击波兰采取视而不见态度。

- `segment_id`: SG03；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:06:51,880","media_offset_end":"00:07:09,150","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 1939 波兰战役语境；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: UK_and_France_governments；`quantifier`: all；`certainty_expressed`: 都是睁只眼闭只眼。

- `source_segment`: [SS-C024](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c024)；`atomicity_group_id`: AG-SG03；`information_gain`: medium。

### C025 · 张伯伦在战争已打响后与希特勒谈判并回国宣称带来和平。

- `segment_id`: SG03；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:07:09,150","media_offset_end":"00:07:25,470","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 所指谈判日期unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Neville_Chamberlain；`quantifier`: one；`certainty_expressed`: 战争都已经打响。

- `source_segment`: [SS-C025](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c025)；`atomicity_group_id`: AG-SG03；`information_gain`: medium。

### C026 · 美联储可能像类比中的行动者一样利用对方损失厌恶取得优势。

- `segment_id`: SG03；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: historical_analogy；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:07:30,750","media_offset_end":"00:07:57,180","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Federal_Reserve_and_counterparties；`quantifier`: unknown；`certainty_expressed`: 可不可能。

- `source_segment`: [SS-C026](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c026)；`atomicity_group_id`: AG-SG03；`information_gain`: medium。

### C027 · 识别上述外部风险才是该文章未明说而值得关注的逻辑。

- `segment_id`: SG03；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:08:00,300","media_offset_end":"00:08:19,220","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 本篇文章；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: one_article；`quantifier`: one；`certainty_expressed`: 真正值得关注。

- `source_segment`: [SS-C027](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c027)；`atomicity_group_id`: AG-SG03；`information_gain`: medium。

### C028 · 央行行长首先必定站在银行利益立场上。

- `segment_id`: SG05；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: motive_attribution；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:09:22,910","media_offset_end":"00:09:28,360","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 本篇文章语境；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: central_bank_governor；`quantifier`: one；`certainty_expressed`: 肯定首先。

- `source_segment`: [SS-C028](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c028)；`atomicity_group_id`: AG-SG05；`information_gain`: medium。

### C029 · 中国以银行贷款为主体的间接融资占比近年来下降。

- `segment_id`: SG05；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:09:28,360","media_offset_end":"00:09:39,100","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 近年来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_financing；`quantifier`: unknown；`certainty_expressed`: 持续。

- `source_segment`: [SS-C029](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c029)；`atomicity_group_id`: AG-SG05；`information_gain`: medium。

### C030 · 中国直接融资占比近年来上升。

- `segment_id`: SG05；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:09:39,100","media_offset_end":"00:09:46,550","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 近年来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_financing；`quantifier`: unknown；`certainty_expressed`: 稳步。

- `source_segment`: [SS-C030](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c030)；`atomicity_group_id`: AG-SG05；`information_gain`: medium。

### C031 · 2013年以前新增间接融资占社融增量超过80%。

- `segment_id`: SG05；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:10:00,680","media_offset_end":"00:10:16,600","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2013年以前，起点unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_TSF_increment；`quantifier`: unknown；`certainty_expressed`: 80%以上。

- `source_segment`: [SS-C031](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c031)；`atomicity_group_id`: AG-SG05；`information_gain`: medium。

### C032 · 直接融资就是资金需求方向资金持有方借款。

- `segment_id`: SG05；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:10:19,440","media_offset_end":"00:10:43,440","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 概念定义；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: direct_financing；`quantifier`: all；`certainty_expressed`: 定义式。

- `source_segment`: [SS-C032](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c032)；`atomicity_group_id`: AG-SG05；`information_gain`: medium。

### C033 · 发行股票相当于发债券、打借条。

- `segment_id`: SG05；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:10:31,950","media_offset_end":"00:10:37,250","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 概念定义；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: equity_financing；`quantifier`: all；`certainty_expressed`: 也是；相当于。

- `source_segment`: [SS-C033](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c033)；`atomicity_group_id`: AG-SG05；`information_gain`: medium。

### C034 · 间接融资由银行连接储蓄者和借款企业并赚取息差。

- `segment_id`: SG05；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:10:47,520","media_offset_end":"00:11:15,350","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 一般银行业务；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: commercial_banks；`quantifier`: unknown；`certainty_expressed`: 定义式。

- `source_segment`: [SS-C034](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c034)；`atomicity_group_id`: AG-SG05；`information_gain`: medium。

### C035 · 过去民间融资困难源于互不信任和缺少合适投资市场。

- `segment_id`: SG06；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:11:15,350","media_offset_end":"00:11:47,650","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2013年以前语境；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_private_financing；`quantifier`: unknown；`certainty_expressed`: 非常非常难。

- `source_segment`: [SS-C035](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c035)；`atomicity_group_id`: AG-SG06；`information_gain`: medium。

### C036 · 2013年美国发生次贷危机次生灾害，使中国获得金融市场发展空间。

- `segment_id`: SG06；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:11:47,650","media_offset_end":"00:12:20,140","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2013年；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_US_financial_markets；`quantifier`: unknown；`certainty_expressed`: 肯定陈述。

- `source_segment`: [SS-C036](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c036)；`atomicity_group_id`: AG-SG06；`information_gain`: medium。

### C037 · 2025年社融增量为35.6万亿元。

- `segment_id`: SG06；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:12:20,260","media_offset_end":"00:12:26,000","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2025全年；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_TSF_increment；`quantifier`: unknown；`certainty_expressed`: 数值陈述。

- `source_segment`: [SS-C037](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c037)；`atomicity_group_id`: AG-SG06；`information_gain`: medium。

### C038 · 2025年企业债、政府债和股票融资合计占社融增量约47%。

- `segment_id`: SG06；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:12:26,000","media_offset_end":"00:12:30,620","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2025全年；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_TSF_increment；`quantifier`: unknown；`certainty_expressed`: 约47%。

- `source_segment`: [SS-C038](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c038)；`atomicity_group_id`: AG-SG06；`information_gain`: medium。

### C039 · 2025年债券和股票融资合计增量首次超过贷款。

- `segment_id`: SG06；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:12:30,620","media_offset_end":"00:12:32,420","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2025全年及此前历史；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_TSF_increment；`quantifier`: one；`certainty_expressed`: 首次。

- `source_segment`: [SS-C039](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c039)；`atomicity_group_id`: AG-SG06；`information_gain`: medium。

### C040 · 贷款在新增融资中的占比从八成以上降到47%以下，几乎腰斩。

- `segment_id`: SG06；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: comparative；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:12:32,420","media_offset_end":"00:12:53,810","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2013年前 对比2025；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_loan_increment；`quantifier`: unknown；`certainty_expressed`: 几乎腰斩。

- `source_segment`: [SS-C040](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c040)；`atomicity_group_id`: AG-SG06；`information_gain`: medium。

### C041 · 上述增量变化代表银行间接融资渠道已退居次席。

- `segment_id`: SG06；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:12:53,810","media_offset_end":"00:13:07,290","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2025；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_financing_channels；`quantifier`: unknown；`certainty_expressed`: 已经。

- `source_segment`: [SS-C041](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c041)；`atomicity_group_id`: AG-SG06；`information_gain`: medium。

### C042 · 最近社融扩张不好且经常负增长。

- `segment_id`: SG07；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:13:07,290","media_offset_end":"00:13:31,850","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 最近一段时间unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_TSF；`quantifier`: unknown；`certainty_expressed`: 老是负增长。

- `source_segment`: [SS-C042](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c042)；`atomicity_group_id`: AG-SG07；`information_gain`: medium。

### C043 · 文章写作背景是为不佳金融数据稳定人心。

- `segment_id`: SG07；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: motive_attribution；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:13:07,290","media_offset_end":"00:14:06,580","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 文章写作时；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: one_article；`quantifier`: one；`certainty_expressed`: 稳稳态度；稳定人心。

- `source_segment`: [SS-C043](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c043)；`atomicity_group_id`: AG-SG07；`information_gain`: medium。

### C044 · 该文章的结构分析价值超出安抚需求。

- `segment_id`: SG07；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:13:31,850","media_offset_end":"00:14:06,580","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 本篇文章；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: one_article；`quantifier`: one；`certainty_expressed`: 质量非常扎实。

- `source_segment`: [SS-C044](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c044)；`atomicity_group_id`: AG-SG07；`information_gain`: medium。

### C045 · 政府债融资与隐性债务置换推高债券占比。

- `segment_id`: SG08；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:14:07,570","media_offset_end":"00:14:33,160","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去几年unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_financing；`quantifier`: unknown；`certainty_expressed`: 使。

- `source_segment`: [SS-C045](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c045)；`atomicity_group_id`: AG-SG08；`information_gain`: medium。

### C046 · 银行核销不良贷款促使贷款占比下降。

- `segment_id`: SG08；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:14:07,570","media_offset_end":"00:14:33,160","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去几年unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_financing；`quantifier`: unknown；`certainty_expressed`: 使。

- `source_segment`: [SS-C046](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c046)；`atomicity_group_id`: AG-SG08；`information_gain`: medium。

### C047 · 所讨论地方政府借债成本约4%甚至5%。

- `segment_id`: SG08；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:15:15,580","media_offset_end":"00:15:37,690","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: local_government_related_borrowing；`quantifier`: some；`certainty_expressed`: 有的；4%往上。

- `source_segment`: [SS-C047](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c047)；`atomicity_group_id`: AG-SG08；`information_gain`: medium。

### C048 · 由中央出面发债可以把成本压至2%以下。

- `segment_id`: SG08；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: counterfactual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:15:37,690","media_offset_end":"00:16:10,440","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 假设置换场景；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: central_government_borrowing；`quantifier`: unknown；`certainty_expressed`: 可以；2%以下。

- `source_segment`: [SS-C048](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c048)；`atomicity_group_id`: AG-SG08；`information_gain`: medium。

### C049 · 中央可以在外边发行熊猫债。

- `segment_id`: SG08；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:15:37,690","media_offset_end":"00:16:00,200","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 融资方式语境；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: central_government；`quantifier`: one；`certainty_expressed`: 无论；或者。

- `source_segment`: [SS-C049](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c049)；`atomicity_group_id`: AG-SG08；`information_gain`: medium。

### C050 · 以年化2%的债置换4%的债能降低付息压力。

- `segment_id`: SG08；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: counterfactual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:16:05,900","media_offset_end":"00:16:22,820","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 假设相同本金置换；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: debtors；`quantifier`: unknown；`certainty_expressed`: 一下子释放很大负担。

- `source_segment`: [SS-C050](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c050)；`atomicity_group_id`: AG-SG08；`information_gain`: medium。

### C051 · 隐性债务合规与确权问题会增加重组过程成本。

- `segment_id`: SG08；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:16:22,820","media_offset_end":"00:17:12,600","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去化债实践unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: hidden_debt_workouts；`quantifier`: many；`certainty_expressed`: 很多；非常严重。

- `source_segment`: [SS-C051](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c051)；`atomicity_group_id`: AG-SG08；`information_gain`: medium。

### C052 · 债务认定和重组结果受到历史私人关系及逐案谈判影响。

- `segment_id`: SG08；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:17:12,600","media_offset_end":"00:18:26,560","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去至当前unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: local_debt_workouts；`quantifier`: exclusive；`certainty_expressed`: 完全取决于关系。

- `source_segment`: [SS-C052](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c052)；`atomicity_group_id`: AG-SG08；`information_gain`: medium。

### C053 · 过去隐债置换都是一事一议闭门谈判展期。

- `segment_id`: SG09；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:18:26,560","media_offset_end":"00:18:49,780","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去几年unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: hidden_debt_swaps；`quantifier`: all；`certainty_expressed`: 都是。

- `source_segment`: [SS-C053](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c053)；`atomicity_group_id`: AG-SG09；`information_gain`: medium。

### C054 · 融资比例变化说明政府债务压力已骤减。

- `segment_id`: SG09；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:18:49,780","media_offset_end":"00:19:27,730","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去几年至当前；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_government_debt；`quantifier`: unknown；`certainty_expressed`: 骤然。

- `source_segment`: [SS-C054](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c054)；`atomicity_group_id`: AG-SG09；`information_gain`: medium。

### C055 · 过去隐性债务问题已经基本妥善解决。

- `segment_id`: SG09；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:19:17,800","media_offset_end":"00:19:27,730","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 截至视频时；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_hidden_debt；`quantifier`: nearly_all；`certainty_expressed`: 基本妥善解决。

- `source_segment`: [SS-C055](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c055)；`atomicity_group_id`: AG-SG09；`information_gain`: high。

### C056 · 2023年美国金融机构曾预言中国债务大爆发。

- `segment_id`: SG09；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:19:27,730","media_offset_end":"00:19:54,350","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2023年；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: US_financial_institutions_unspecified；`quantifier`: unknown；`certainty_expressed`: 那些金融机构。

- `source_segment`: [SS-C056](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c056)；`atomicity_group_id`: AG-SG09；`information_gain`: medium。

### C057 · 到2026年已无人再提中国债务爆发问题。

- `segment_id`: SG09；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:19:27,730","media_offset_end":"00:19:54,350","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2026年最近；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: unspecified；`quantifier`: all；`certainty_expressed`: 已经没人提。

- `source_segment`: [SS-C057](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c057)；`atomicity_group_id`: AG-SG09；`information_gain`: medium。

### C058 · 9527自称前几天讨论过平陆运河。

- `segment_id`: SG10；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: retrospective。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:19:54,350","media_offset_end":"00:19:56,580","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 前几天unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: 9527_prior_content；`quantifier`: one；`certainty_expressed`: 我前几天。

- `source_segment`: [SS-C058](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c058)；`atomicity_group_id`: AG-SG10；`information_gain`: medium。

### C059 · 推进长回收期大型工程体现政府决心与公信力。

- `segment_id`: SG10；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:19:56,580","media_offset_end":"00:20:10,390","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 平陆运河建设时期；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_government；`quantifier`: one；`certainty_expressed`: 本身就代表。

- `source_segment`: [SS-C059](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c059)；`atomicity_group_id`: AG-SG10；`information_gain`: medium。

### C060 · 平陆运河整体投资规模为700多亿元。

- `segment_id`: SG10；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:20:10,390","media_offset_end":"00:20:24,520","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 项目建设投资预算；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Pinglu_Canal；`quantifier`: one；`certainty_expressed`: 700多个亿。

- `source_segment`: [SS-C060](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c060)；`atomicity_group_id`: AG-SG10；`information_gain`: medium。

### C061 · 平陆运河每年创造五十多亿元综合社会效益。

- `segment_id`: SG10；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:20:18,220","media_offset_end":"00:20:33,430","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 运营后预测年unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Pinglu_Canal；`quantifier`: one；`certainty_expressed`: 五十几个亿。

- `source_segment`: [SS-C061](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c061)；`atomicity_group_id`: AG-SG10；`information_gain`: medium。

### C062 · 平陆运河按所述效益计算大概需要134年回本。

- `segment_id`: SG10；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: calculated；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:20:33,430","media_offset_end":"00:20:37,210","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 假设静态回收；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Pinglu_Canal；`quantifier`: one；`certainty_expressed`: 大概。

- `source_segment`: [SS-C062](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c062)；`atomicity_group_id`: AG-SG10；`information_gain`: medium。

### C063 · 平陆运河乐观估计也要三四十年才能回本。

- `segment_id`: SG10；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:20:37,340","media_offset_end":"00:21:39,750","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 投运后约30至40年；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Pinglu_Canal；`quantifier`: one；`certainty_expressed`: 乐观估计；难得回本。

- `source_segment`: [SS-C063](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c063)；`atomicity_group_id`: AG-SG10；`information_gain`: medium。

### C064 · 平陆运河工程量巨大。

- `segment_id`: SG10；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:20:59,750","media_offset_end":"00:22:12,440","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 项目建设阶段；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Pinglu_Canal；`quantifier`: one；`certainty_expressed`: 工程量巨大。

- `source_segment`: [SS-C064](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c064)；`atomicity_group_id`: AG-SG10；`information_gain`: medium。

### C065 · 长期建设决心所形成的信心是有效化债的关键。

- `segment_id`: SG10；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:22:12,440","media_offset_end":"00:22:41,930","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 长期一般命题；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: government_creditors；`quantifier`: unknown；`certainty_expressed`: 真正有效的信心。

- `source_segment`: [SS-C065](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c065)；`atomicity_group_id`: AG-SG10；`information_gain`: medium。

### C066 · 剔除化债等因素后中国融资结构变化依然显著。

- `segment_id`: SG11；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:22:43,530","media_offset_end":"00:22:58,530","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去几年unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_financing；`quantifier`: unknown；`certainty_expressed`: 显著。

- `source_segment`: [SS-C066](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c066)；`atomicity_group_id`: AG-SG11；`information_gain`: medium。

### C067 · 企业债券融资增量与同期贷款增量之比在2023年为7%。

- `segment_id`: SG11；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:22:58,530","media_offset_end":"00:23:05,060","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2023年；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_corporate_financing；`quantifier`: unknown；`certainty_expressed`: 7%。

- `source_segment`: [SS-C067](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c067)；`atomicity_group_id`: AG-SG11；`information_gain`: medium。

### C068 · 同一企业债融资与贷款增量之比在2026上半年接近20%。

- `segment_id`: SG11；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:23:05,060","media_offset_end":"00:23:08,370","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2026上半年；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_corporate_financing；`quantifier`: unknown；`certainty_expressed`: 近20%。

- `source_segment`: [SS-C068](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c068)；`atomicity_group_id`: AG-SG11；`information_gain`: medium。

### C069 · 当前银行对优质项目贷款成本低且信贷条件宽松。

- `segment_id`: SG11；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:23:13,880","media_offset_end":"00:23:32,770","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 视频时点；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: high_quality_borrowers；`quantifier`: unknown；`certainty_expressed`: 极宽松；打开绿灯。

- `source_segment`: [SS-C069](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c069)；`atomicity_group_id`: AG-SG11；`information_gain`: medium。

### C070 · 债券融资相对贷款增长表明直接融资成本比低息银行贷款还低。

- `segment_id`: SG11；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:23:43,080","media_offset_end":"00:23:57,300","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2023至2026上半年；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_corporate_financing；`quantifier`: unknown；`certainty_expressed`: 还要低。

- `source_segment`: [SS-C070](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c070)；`atomicity_group_id`: AG-SG11；`information_gain`: high。

### C071 · 国有银行间接融资占用国家信用资本。

- `segment_id`: SG11；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:23:57,300","media_offset_end":"00:24:27,410","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 一般融资结构；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: state_owned_banks；`quantifier`: unknown；`certainty_expressed`: 国家信用担保。

- `source_segment`: [SS-C071](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c071)；`atomicity_group_id`: AG-SG11；`information_gain`: medium。

### C072 · 更多直接融资、较少银行担保将为国家未来举债释放空间。

- `segment_id`: SG11；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:24:19,580","media_offset_end":"00:25:20,060","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 当前至未来；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_state_credit_capacity；`quantifier`: unknown；`certainty_expressed`: 很大；有利条件。

- `source_segment`: [SS-C072](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c072)；`atomicity_group_id`: AG-SG11；`information_gain`: high。

### C073 · 贷款或间接融资占比下降时绝对值仍在增加。

- `segment_id`: SG11；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:25:00,060","media_offset_end":"00:25:40,060","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 当前趋势，统计区间unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_lending；`quantifier`: unknown；`certainty_expressed`: 不是绝对值；绝对值还在增加。

- `source_segment`: [SS-C073](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c073)；`atomicity_group_id`: AG-SG11；`information_gain`: medium。

### C074 · 20世纪90年代初间接融资占社融存量接近100%。

- `segment_id`: SG12；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:25:20,060","media_offset_end":"00:26:26,480","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 20世纪90年代金融市场建设早期；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_TSF_stock；`quantifier`: nearly_all；`certainty_expressed`: 接近百分之百。

- `source_segment`: [SS-C074](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c074)；`atomicity_group_id`: AG-SG12；`information_gain`: medium。

### C075 · 90年代融资几乎必须通过银行，是因为陌生人之间信用成本很高。

- `segment_id`: SG12；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:25:40,060","media_offset_end":"00:26:22,300","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 20世纪90年代；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_nonkin_borrowers；`quantifier`: nearly_all；`certainty_expressed`: 所有；必须；除非亲戚朋友。

- `source_segment`: [SS-C075](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c075)；`atomicity_group_id`: AG-SG12；`information_gain`: medium。

### C076 · 2026年6月末间接融资占社融存量约三分之二。

- `segment_id`: SG12；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:26:28,790","media_offset_end":"00:26:36,250","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2026-06-30；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_TSF_stock；`quantifier`: unknown；`certainty_expressed`: 约三分之二。

- `source_segment`: [SS-C076](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c076)；`atomicity_group_id`: AG-SG12；`information_gain`: medium。

### C077 · 同期贷款余额占社融存量约60%。

- `segment_id`: SG12；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:26:36,520","media_offset_end":"00:26:39,710","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2026-06-30；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_TSF_stock；`quantifier`: unknown；`certainty_expressed`: 约60%。

- `source_segment`: [SS-C077](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c077)；`atomicity_group_id`: AG-SG12；`information_gain`: medium。

### C078 · 同期直接融资余额占社融存量约三分之一。

- `segment_id`: SG12；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:26:39,710","media_offset_end":"00:26:42,850","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2026-06-30；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_TSF_stock；`quantifier`: unknown；`certainty_expressed`: 约三分之一。

- `source_segment`: [SS-C078](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c078)；`atomicity_group_id`: AG-SG12；`information_gain`: medium。

### C079 · 同期债券融资占社融存量约30%。

- `segment_id`: SG12；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:26:42,850","media_offset_end":"00:26:46,100","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2026-06-30；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_TSF_stock；`quantifier`: unknown；`certainty_expressed`: 约30%。

- `source_segment`: [SS-C079](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c079)；`atomicity_group_id`: AG-SG12；`information_gain`: medium。

### C080 · 反推可得股票融资占比约10%。

- `segment_id`: SG12；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: calculated；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:26:46,110","media_offset_end":"00:26:54,250","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2026-06-30；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_TSF_stock；`quantifier`: unknown；`certainty_expressed`: 基本上10%左右。

- `source_segment`: [SS-C080](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c080)；`atomicity_group_id`: AG-SG12；`information_gain`: high。

### C081 · 中国融资结构已从间接融资主导转为直接与间接协调发展。

- `segment_id`: SG12；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:26:54,250","media_offset_end":"00:27:00,920","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 截至2026-06；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_financing；`quantifier`: unknown；`certainty_expressed`: 已经。

- `source_segment`: [SS-C081](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c081)；`atomicity_group_id`: AG-SG12；`information_gain`: medium。

### C082 · 直接融资比重未来仍会继续积极扩大。

- `segment_id`: SG12；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:27:00,960","media_offset_end":"00:27:11,360","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_direct_financing；`quantifier`: unknown；`certainty_expressed`: 肯定还会。

- `source_segment`: [SS-C082](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c082)；`atomicity_group_id`: AG-SG12；`information_gain`: medium。

### C083 · 直接融资占三分之二、间接占三分之一是合理状态。

- `segment_id`: SG12；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: normative；`derivation_type`: recommendation；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:27:06,380","media_offset_end":"00:27:15,540","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来理想状态；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_financing；`quantifier`: unknown；`certainty_expressed`: 我认为；应该。

- `source_segment`: [SS-C083](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c083)；`atomicity_group_id`: AG-SG12；`information_gain`: medium。

### C084 · 许多银行从业者最近抱怨日子不好过。

- `segment_id`: SG13；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:27:15,540","media_offset_end":"00:27:30,810","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 最近unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: commercial_bank_employees；`quantifier`: many；`certainty_expressed`: 很多很多。

- `source_segment`: [SS-C084](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c084)；`atomicity_group_id`: AG-SG13；`information_gain`: medium。

### C085 · 若结构趋势延续且不转型，银行整体盈利能力将继续下降。

- `segment_id`: SG13；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:27:23,950","media_offset_end":"00:27:51,590","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: commercial_banks；`quantifier`: unknown；`certainty_expressed`: 还会继续；除非。

- `source_segment`: [SS-C085](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c085)；`atomicity_group_id`: AG-SG13；`information_gain`: high。

### C086 · 传统银行业务萎缩趋势非常确定。

- `segment_id`: SG13；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:27:46,840","media_offset_end":"00:28:03,940","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: traditional_bank_business；`quantifier`: unknown；`certainty_expressed`: 非常非常确定。

- `source_segment`: [SS-C086](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c086)；`atomicity_group_id`: AG-SG13；`information_gain`: medium。

### C087 · 银行未来盈利规模会随趋势下降。

- `segment_id`: SG13；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:27:56,770","media_offset_end":"00:28:00,220","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: commercial_banks；`quantifier`: unknown；`certainty_expressed`: 会。

- `source_segment`: [SS-C087](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c087)；`atomicity_group_id`: AG-SG13；`information_gain`: medium。

### C088 · 银行表外业务是未来十年级别的利润来源方向。

- `segment_id`: SG13；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:28:15,120","media_offset_end":"00:28:47,770","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 十年级，精确起止unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: commercial_banks；`quantifier`: unknown；`certainty_expressed`: 肯定；大趋势。

- `source_segment`: [SS-C088](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c088)；`atomicity_group_id`: AG-SG13；`information_gain`: high。

### C089 · 银行从业者应优先选择能创造额外利润的业务方向。

- `segment_id`: SG13；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: normative；`derivation_type`: recommendation；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:28:15,120","media_offset_end":"00:29:05,910","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来职业选择；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: commercial_bank_employees；`quantifier`: unknown；`certainty_expressed`: 你得瞄准。

- `source_segment`: [SS-C089](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c089)；`atomicity_group_id`: AG-SG13；`information_gain`: medium。

### C090 · 为公司创造额外利润的人将获得更高内部地位。

- `segment_id`: SG13；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:28:44,930","media_offset_end":"00:28:51,070","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: employees_generating_extra_profit；`quantifier`: all；`certainty_expressed`: 谁能；谁就。

- `source_segment`: [SS-C090](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c090)；`atomicity_group_id`: AG-SG13；`information_gain`: medium。

### C091 · 近十年房地产与基建新增贷款占比从60%以上降到约10%。

- `segment_id`: SG14；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:29:13,500","media_offset_end":"00:29:24,540","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 近十年，端点unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_property_infrastructure_new_loans；`quantifier`: unknown；`certainty_expressed`: 60%以上至10%左右。

- `source_segment`: [SS-C091](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c091)；`atomicity_group_id`: AG-SG14；`information_gain`: medium。

### C092 · 金融五篇大文章领域新增贷款占比超过70%。

- `segment_id`: SG14；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:29:24,540","media_offset_end":"00:29:34,120","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 当前统计期unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: five_finance_fields_new_loans；`quantifier`: unknown；`certainty_expressed`: 70%以上。

- `source_segment`: [SS-C092](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c092)；`atomicity_group_id`: AG-SG14；`information_gain`: medium。

### C093 · 科技型中小企业贷款增速近几年约20%。

- `segment_id`: SG14；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:29:35,700","media_offset_end":"00:29:41,990","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去几年unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: technology_SMEs；`quantifier`: unknown；`certainty_expressed`: 约20%。

- `source_segment`: [SS-C093](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c093)；`atomicity_group_id`: AG-SG14；`information_gain`: medium。

### C094 · 贷款整体规模在下降。

- `segment_id`: SG15；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:31:24,920","media_offset_end":"00:31:27,150","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 当前趋势unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_lending；`quantifier`: unknown；`certainty_expressed`: 整体规模下降。

- `source_segment`: [SS-C094](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c094)；`atomicity_group_id`: AG-SG15；`information_gain`: medium。

### C095 · 普惠小微贷款近几年年均增速约20%。

- `segment_id`: SG14；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:29:41,990","media_offset_end":"00:29:45,210","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去几年unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: inclusive_small_micro_loans；`quantifier`: unknown；`certainty_expressed`: 年均约20%。

- `source_segment`: [SS-C095](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c095)；`atomicity_group_id`: AG-SG14；`information_gain`: medium。

### C096 · 绿色贷款保持两位数以上增长。

- `segment_id`: SG14；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:29:45,210","media_offset_end":"00:29:49,410","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去几年unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: green_loans；`quantifier`: unknown；`certainty_expressed`: 两位数以上。

- `source_segment`: [SS-C096](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c096)；`atomicity_group_id`: AG-SG14；`information_gain`: medium。

### C097 · 养老产业贷款保持两位数以上增长。

- `segment_id`: SG14；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:29:45,210","media_offset_end":"00:29:49,410","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去几年unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: pension_industry_loans；`quantifier`: unknown；`certainty_expressed`: 两位数以上。

- `source_segment`: [SS-C097](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c097)；`atomicity_group_id`: AG-SG14；`information_gain`: medium。

### C098 · 上述重点领域贷款增速均高于全部贷款增速。

- `segment_id`: SG14；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: comparative；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:29:49,410","media_offset_end":"00:29:52,220","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去几年unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: listed_loan_categories；`quantifier`: all；`certainty_expressed`: 均明显高于。

- `source_segment`: [SS-C098](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c098)；`atomicity_group_id`: AG-SG14；`information_gain`: medium。

### C099 · 资金流向能够指示市场机会所在。

- `segment_id`: SG14；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:29:52,220","media_offset_end":"00:30:07,610","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 一般分析方法；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: economic_sectors；`quantifier`: unknown；`certainty_expressed`: 就流向市场机会。

- `source_segment`: [SS-C099](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c099)；`atomicity_group_id`: AG-SG14；`information_gain`: medium。

### C100 · 获得更充分金融供给的领域未来更有发展条件。

- `segment_id`: SG14；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: inferred；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:30:07,610","media_offset_end":"00:31:12,550","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: supported_sectors；`quantifier`: unknown；`certainty_expressed`: 很有想象空间；更有条件。

- `source_segment`: [SS-C100](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c100)；`atomicity_group_id`: AG-SG14；`information_gain`: medium。

### C101 · 贷款未覆盖的高科技产业在直接融资市场增长得更快。

- `segment_id`: SG15；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: comparative；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:31:27,150","media_offset_end":"00:31:41,960","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 当前unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: high_tech_nonloan_financed_sectors；`quantifier`: unknown；`certainty_expressed`: 增长更厉害。

- `source_segment`: [SS-C101](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c101)；`atomicity_group_id`: AG-SG15；`information_gain`: medium。

### C102 · 科技企业融资需求随初创、成长和成熟阶段不同。

- `segment_id`: SG15；`claimant`: A002；`asserted_by`: A001。9527转述潘功胜；不据此推断朗读全文

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:31:41,960","media_offset_end":"00:32:04,930","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 企业生命周期；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: technology_firms；`quantifier`: unknown；`certainty_expressed`: 阶段式陈述。

- `source_segment`: [SS-C102](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c102)；`atomicity_group_id`: AG-SG15；`information_gain`: medium。

### C103 · 银行缺乏承担科技企业早期高失败风险的能力。

- `segment_id`: SG15；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:32:01,570","media_offset_end":"00:32:10,610","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 早期融资阶段；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: commercial_banks；`quantifier`: all；`certainty_expressed`: 没能力。

- `source_segment`: [SS-C103](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c103)；`atomicity_group_id`: AG-SG15；`information_gain`: medium。

### C104 · 民间天使投资在早期科技企业融资中起主角作用。

- `segment_id`: SG15；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:32:10,610","media_offset_end":"00:32:21,320","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 早期融资阶段；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: early_stage_technology_firms；`quantifier`: majority；`certainty_expressed`: 主要部分；主角。

- `source_segment`: [SS-C104](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c104)；`atomicity_group_id`: AG-SG15；`information_gain`: medium。

### C105 · 这些早期投资与银行没有关系。

- `segment_id`: SG15；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:32:21,320","media_offset_end":"00:32:23,560","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 当下早期融资；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: early_stage_financing；`quantifier`: all；`certainty_expressed`: 没关系。

- `source_segment`: [SS-C105](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c105)；`atomicity_group_id`: AG-SG15；`information_gain`: medium。

### C106 · 早期非银行融资比例正在迅速增高。

- `segment_id`: SG15；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:32:23,880","media_offset_end":"00:32:26,830","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 当前unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: early_stage_nonbank_financing；`quantifier`: unknown；`certainty_expressed`: 迅速。

- `source_segment`: [SS-C106](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c106)；`atomicity_group_id`: AG-SG15；`information_gain`: medium。

### C107 · 上述融资转向说明新旧动能转换正在实际落地。

- `segment_id`: SG15；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:32:27,590","media_offset_end":"00:32:44,730","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 当前unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_industrial_transition；`quantifier`: unknown；`certainty_expressed`: 非常具体地落地。

- `source_segment`: [SS-C107](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c107)；`atomicity_group_id`: AG-SG15；`information_gain`: high。

### C108 · 早期风险投资是美国传统优势业务。

- `segment_id`: SG16；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: comparative；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:32:44,730","media_offset_end":"00:32:59,840","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: US_vs_China_venture_capital；`quantifier`: unknown；`certainty_expressed`: 非常有优势。

- `source_segment`: [SS-C108](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c108)；`atomicity_group_id`: AG-SG16；`information_gain`: medium。

### C109 · 过去美国资本较愿意为中国企业早期机会提供启动资金。

- `segment_id`: SG16；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:32:59,840","media_offset_end":"00:33:19,840","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: US_investors_in_China_startups；`quantifier`: many；`certainty_expressed`: 很多；稍微有一点机会。

- `source_segment`: [SS-C109](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c109)；`atomicity_group_id`: AG-SG16；`information_gain`: medium。

### C110 · 过去这类早期融资机会只能在美国找到。

- `segment_id`: SG16；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: comparative；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:33:19,840","media_offset_end":"00:33:39,840","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: early_stage_funding_opportunities；`quantifier`: exclusive；`certainty_expressed`: 只能。

- `source_segment`: [SS-C110](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c110)；`atomicity_group_id`: AG-SG16；`information_gain`: medium。

### C111 · 100万美元折成人民币的数额在原转写中为将近100万就是0万。

- `segment_id`: SG16；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:33:19,840","media_offset_end":"00:33:59,840","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 汇率时点unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: USD_CNY_conversion；`quantifier`: one；`certainty_expressed`: 数字损坏。

- `source_segment`: [SS-C111](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c111)；`atomicity_group_id`: AG-SG16；`information_gain`: medium。

### C112 · 对美国投资者100万美元投资的主观负担类似国内投资者投1万元人民币。

- `segment_id`: SG16；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: comparative；`derivation_type`: inferred；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:33:39,840","media_offset_end":"00:33:59,840","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去投资语境unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: US_vs_China_investors；`quantifier`: unknown；`certainty_expressed`: 差不多。

- `source_segment`: [SS-C112](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c112)；`atomicity_group_id`: AG-SG16；`information_gain`: medium。

### C113 · 汇率和金融资本优势使美元投资中国新兴产业更划算。

- `segment_id`: SG16；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: causal；`derivation_type`: causal_inference；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:33:59,840","media_offset_end":"00:34:21,030","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: USD_investors_in_China；`quantifier`: unknown；`certainty_expressed`: 事半功倍。

- `source_segment`: [SS-C113](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c113)；`atomicity_group_id`: AG-SG16；`information_gain`: medium。

### C114 · 人民币资本现在走上台前是已经观察到的趋势。

- `segment_id`: SG17；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:34:24,300","media_offset_end":"00:34:48,240","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去几年至当前；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: RMB_risk_capital；`quantifier`: unknown；`certainty_expressed`: 不是一厢情愿；数据观察。

- `source_segment`: [SS-C114](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c114)；`atomicity_group_id`: AG-SG17；`information_gain`: medium。

### C115 · 中国正在挑战美国传统金融优势领域。

- `segment_id`: SG17；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: interpretive；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:34:51,050","media_offset_end":"00:34:59,190","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 当前unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_vs_US_risk_capital；`quantifier`: unknown；`certainty_expressed`: 这才是关键。

- `source_segment`: [SS-C115](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c115)；`atomicity_group_id`: AG-SG17；`information_gain`: high。

### C116 · 本篇文章写在本次美联储加息之前。

- `segment_id`: SG01；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:00:20,090","media_offset_end":"00:00:40,090","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2026-09；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: article_and_FOMC；`quantifier`: one；`certainty_expressed`: 注意；之前。

- `source_segment`: [SS-C116](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c116)；`atomicity_group_id`: AG-SG01；`information_gain`: medium。

### C117 · 2013年发生过第二次金融危机或次贷危机的次生灾害。

- `segment_id`: SG06；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:11:50,300","media_offset_end":"00:12:07,060","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 2013年；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: unspecified_financial_crisis；`quantifier`: one；`certainty_expressed`: 不是第二次吗。

- `source_segment`: [SS-C117](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c117)；`atomicity_group_id`: AG-SG06；`information_gain`: medium。

### C118 · 融资结构变化将为未来国家举债打开空间。

- `segment_id`: SG11；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:24:57,460","media_offset_end":"00:25:20,060","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_sovereign_borrowing_capacity；`quantifier`: unknown；`certainty_expressed`: 打开很好的空间。

- `source_segment`: [SS-C118](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c118)；`atomicity_group_id`: AG-SG11；`information_gain`: medium。

### C119 · 创造额外利润的员工晋升速度会加快。

- `segment_id`: SG13；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:28:51,070","media_offset_end":"00:28:56,100","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: employees_generating_extra_profit；`quantifier`: all；`certainty_expressed`: 就会加快。

- `source_segment`: [SS-C119](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c119)；`atomicity_group_id`: AG-SG13；`information_gain`: medium。

### C120 · 创造额外利润的员工调配资源会更顺畅。

- `segment_id`: SG13；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: forecast；`derivation_type`: paraphrased；`temporal_mode`: ex_ante。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:28:52,050","media_offset_end":"00:28:58,300","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 未来unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: employees_generating_extra_profit；`quantifier`: all；`certainty_expressed`: 也会。

- `source_segment`: [SS-C120](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c120)；`atomicity_group_id`: AG-SG13；`information_gain`: medium。

### C121 · 所讨论长期债务成本都是压在20%。

- `segment_id`: SG08；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:16:00,200","media_offset_end":"00:16:01,580","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 债务置换语境unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: long_term_debt_unspecified；`quantifier`: all；`certainty_expressed`: 都是；20%。

- `source_segment`: [SS-C121](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c121)；`atomicity_group_id`: AG-SG08；`information_gain`: medium。

### C122 · 中国30年期国债收益率在2%点几。

- `segment_id`: SG08；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:16:01,580","media_offset_end":"00:16:05,200","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 时点unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: China_30Y_government_bond；`quantifier`: one；`certainty_expressed`: 2%点几。

- `source_segment`: [SS-C122](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c122)；`atomicity_group_id`: AG-SG08；`information_gain`: medium。

### C123 · 许多隐债经手人后来被抓或被双规。

- `segment_id`: SG08；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:16:33,350","media_offset_end":"00:16:43,460","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 过去unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: hidden_debt_handlers；`quantifier`: many；`certainty_expressed`: 很多。

- `source_segment`: [SS-C123](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c123)；`atomicity_group_id`: AG-SG08；`information_gain`: medium。

### C124 · 平陆运河相关河道从几米深挖到十几米深。

- `segment_id`: SG10；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:21:19,750","media_offset_end":"00:21:39,750","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 工程建设期unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Pinglu_Canal_channel；`quantifier`: unknown；`certainty_expressed`: 几米到十几米。

- `source_segment`: [SS-C124](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c124)；`atomicity_group_id`: AG-SG10；`information_gain`: medium。

### C125 · 平陆运河相关河道从几米宽拓到几十米宽。

- `segment_id`: SG10；`claimant`: A001；`asserted_by`: A001。9527自身陈述；有嵌套归因者另注

- `claim_type`: factual；`derivation_type`: paraphrased；`temporal_mode`: ex_post。

- `asserted_at`: {"recorded_at":null,"publication_proxy":"2026-09-21T10:32:21+08:00","media_offset_start":"00:21:39,750","media_offset_end":"00:21:59,750","precision":"录制绝对时间unknown；不得将发布时间加偏移当实际发言时间"}

- `reference_time`: 工程建设期unknown；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: Pinglu_Canal_channel；`quantifier`: unknown；`certainty_expressed`: 几米到几十米。

- `source_segment`: [SS-C125](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-c125)；`atomicity_group_id`: AG-SG10；`information_gain`: medium。

### MC01 · 假如直接融资替代的是银行原可取得的贷款，银行可获得的传统信贷需求相对反事实减少。

- `segment_id`: SG13；`claimant`: model；`asserted_by`: model。诊断推理所需的条件；非9527原话

- `claim_type`: causal；`derivation_type`: model_generated；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":null,"extracted_at":"2026-09-24"}

- `reference_time`: 条件式机制，非新增事实；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: conditional_scope；`quantifier`: unknown；`certainty_expressed`: conditional。

- `source_segment`: [SS-MC01](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-mc01)；`atomicity_group_id`: AG-MODEL；`information_gain`: high。

### MC02 · 若利差、定价及其他收入不能补偿，减少的贷款需求会压低传统信贷净收益。

- `segment_id`: SG13；`claimant`: model；`asserted_by`: model。诊断推理所需的条件；非9527原话

- `claim_type`: causal；`derivation_type`: model_generated；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":null,"extracted_at":"2026-09-24"}

- `reference_time`: 条件式机制，非新增事实；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: conditional_scope；`quantifier`: unknown；`certainty_expressed`: conditional。

- `source_segment`: [SS-MC02](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-mc02)；`atomicity_group_id`: AG-MODEL；`information_gain`: high。

### MC03 · 还需假定规模增长、信用成本下降及非信贷收入均不足补偿，才能推出银行总利润下降。

- `segment_id`: SG13；`claimant`: model；`asserted_by`: model。诊断推理所需的条件；非9527原话

- `claim_type`: causal；`derivation_type`: model_generated；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":null,"extracted_at":"2026-09-24"}

- `reference_time`: 条件式机制，非新增事实；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: conditional_scope；`quantifier`: unknown；`certainty_expressed`: conditional。

- `source_segment`: [SS-MC03](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-mc03)；`atomicity_group_id`: AG-MODEL；`information_gain`: high。

### MC04 · 若直接融资风险真正由外部投资者承担且无国家回兜，银行体系的潜在公共信用支持负担才可能下降。

- `segment_id`: SG11；`claimant`: model；`asserted_by`: model。诊断推理所需的条件；非9527原话

- `claim_type`: causal；`derivation_type`: model_generated；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":null,"extracted_at":"2026-09-24"}

- `reference_time`: 条件式机制，非新增事实；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: conditional_scope；`quantifier`: unknown；`certainty_expressed`: conditional。

- `source_segment`: [SS-MC04](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-mc04)；`atomicity_group_id`: AG-MODEL；`information_gain`: high。

### MC05 · 要从社融结构推到人民币早期风险资本扩张，须证明新增直接融资中相应币种与投资阶段资金确有增长。

- `segment_id`: SG15；`claimant`: model；`asserted_by`: model。诊断推理所需的条件；非9527原话

- `claim_type`: causal；`derivation_type`: model_generated；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":null,"extracted_at":"2026-09-24"}

- `reference_time`: 条件式机制，非新增事实；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: conditional_scope；`quantifier`: unknown；`certainty_expressed`: conditional。

- `source_segment`: [SS-MC05](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-mc05)；`atomicity_group_id`: AG-MODEL；`information_gain`: high。

### MC06 · 要从国内融资扩张推到中美竞争地位改善，须证明同口径资金、创新产出与退出能力相对美国改善。

- `segment_id`: SG16；`claimant`: model；`asserted_by`: model。诊断推理所需的条件；非9527原话

- `claim_type`: causal；`derivation_type`: model_generated；`temporal_mode`: contemporaneous。

- `asserted_at`: {"recorded_at":null,"publication_proxy":null,"extracted_at":"2026-09-24"}

- `reference_time`: 条件式机制，非新增事实；`knowledge_cutoff`: 2026-09-21T10:32:21+08:00。

- `population`: conditional_scope；`quantifier`: unknown；`certainty_expressed`: conditional。

- `source_segment`: [SS-MC06](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md#ss-mc06)；`atomicity_group_id`: AG-MODEL；`information_gain`: high。

## 7. ACTORS / EVENTS / INDICATORS / OBSERVATIONS / POLICIES

### Actors

| ID | 规范实体 | aliases | kind |
| --- | --- | --- | --- |
| A001 | 有何高见9527 | ["9527","主播"] | person_or_channel |
| A002 | 潘功胜 | ["潘刚盛","潘光盛","潘东升","潘行长"] | person |
| A003 | 中国人民银行 | ["央行","人民银行","PBOC"] | institution |
| A004 | 商业银行 | ["银行系统","银行"] | population |
| A005 | 中国中央政府 | ["中央","国家（财政信用语境）"] | government |
| A006 | 中国地方政府 | ["地方政府"] | population |
| A007 | 科技型企业 | ["高科技企业","科技企业"] | population |
| A008 | 美联储 | ["美国央行","Federal Reserve"] | institution |
| A009 | 日本银行 | ["日本央行"] | institution |
| A010 | 欧洲中央银行 | ["欧洲这边（加息语境）"] | institution |
| A011 | 美国政府 | ["美国（财政债务语境）"] | government |
| A012 | 美债大额持有者 | ["国家以及民间持有者"] | population |
| A013 | 天使及风险投资者 | ["天使投资","民间早期资本"] | population |
| A014 | 英国政府 | ["英方"] | government |
| A015 | 法国政府 | ["法方"] | government |
| A016 | 纳粹德国及希特勒 | ["德国（该历史语境）"] | historical_actor_group |
| A017 | 张伯伦 | ["Neville Chamberlain"] | person |
| A018 | 银行从业者 | ["银行工作人员"] | population |
| A019 | 美国金融机构（未具名） | ["那些金融机构"] | unresolved_population |
| A020 | 国有银行 | ["国有商业银行"] | population |
| A021 | 苏联 | ["苏联"] | historical_state |
| A022 | 中国企业 | ["企业"] | population |

### Events

| ID | 现实状态变化 | occurred_at | effective_at | 来源/属性 |
| --- | --- | --- | --- | --- |
| EV01 | 潘功胜求是文章公开发表 | 2026-09-16T09:00:00+08:00 | null | SRC06 / publication_verified; writing_date_unknown |
| EV02 | FOMC宣布加息 | 2026-09-16T14:00:00-04:00 | null | SRC09 / verified |
| EV03 | 日本央行宣布利率调整 | 2026-09-18T11:54:00+09:00 | 2026-09-24 | SRC10 / announced_at_cutoff; effective_after_cutoff |
| EV04 | ECB宣布加息 | 2026-09-10 | 2026-09-16 | SRC11 / verified |
| EV05 | 批准增加地方债务限额用于隐债置换 | 2024-11-08 | null | SRC13 / verification_added; not_claimed_as_specific_date_by_creator |
| EV06 | 平陆运河项目开工 | 2022-08-28 | null | SRC07 / verification_added; not_inferred_debt_resolution |

不把中国金融结构变化建成一次Event；不把未指明的2013危机建成既定Event。

### Indicators

| ID | 指标 | 类型 | 定义/分母 | unit |
| --- | --- | --- | --- | --- |
| I01 | 社会融资规模增量 | flow | 一定期间实体经济从金融体系获得的融资 | 万亿元 |
| I02 | 新增间接融资占社融增量比重 | flow_share | 间接融资增量/社融增量 | % |
| I03 | 债券与股票合计占社融增量比重 | flow_share | 政府债+企业债+股票融资增量/社融增量 | % |
| I04 | 企业债融资增量与同期贷款增量之比 | flow_ratio | 企业债融资增量/同期贷款增量；贷款分母范围待定 | % |
| I05 | 间接融资占社融存量比重 | stock_share | 间接融资余额/社融余额 | % |
| I06 | 贷款占社融存量比重 | stock_share | 贷款余额/社融余额 | % |
| I07 | 直接融资占社融存量比重 | stock_share | 直接融资余额/社融余额 | % |
| I08 | 债券融资占社融存量比重 | stock_share | 债券融资余额/社融余额 | % |
| I09 | 股票融资占社融存量比重 | stock_share | 股票融资余额/社融余额 | % |
| I10 | 房地产与基建新增贷款占比 | ambiguous_share | 分子为新增贷款；全部贷款分母是新增还是存量不明 | % |
| I11 | 五篇大文章领域新增贷款占比 | flow_share_unresolved | 分母及交叉分类去重不明 | % |
| I12 | 科技型中小企业贷款增速 | growth | 统计口径及基期unknown | % |
| I13 | 普惠小微贷款年均增速 | average_growth | 算术或复合平均unknown | % |
| I14 | 绿色贷款增速 | growth | 基期unknown | % |
| I15 | 养老产业贷款增速 | growth | 基期unknown | % |
| I16 | 平陆运河项目投资 | investment_budget | 估算总投资，不等于决算 | 亿元 |
| I17 | 运河相关年运输费用节约 | projected_external_benefit | 非项目现金流 | 亿元/年 |
| I18 | 银行利润 | profit | 净利润/利润总额及群体口径未确定 | unknown |
| I19 | 人民币早期风险资本规模 | flow_or_stock_unresolved | 币种、阶段、投融资口径需单独建序列 | unknown |
| I20 | 贷款绝对规模 | stock_or_flow_unresolved | 未明确贷款余额还是新增额 | unknown |
| I21 | 隐性债务余额 | stock | 认定范围与或有负债需注明 | 亿元 |
| I22 | 中国30年国债收益率 | yield | 日期与券种unknown | % |

### IndicatorObservations

| ID | Indicator / Claim | reference_period | released_at | value / unit | previous / revision | kind |
| --- | --- | --- | --- | --- | --- | --- |
| OB01 | I01 / C037 | 2025 | 2026-09-16T09:00:00+08:00 | 35.6 万亿元 | null / null | reported |
| OB02 | I02 / C031 | 2013以前 | 2026-09-16T09:00:00+08:00 | >80 % | null / null | reported |
| OB03 | I03 / C038 | 2025 | 2026-09-16T09:00:00+08:00 | ~47 % | null / null | reported |
| OB04 | I04 / C067 | 2023 | 2026-09-16T09:00:00+08:00 | 7 % | null / null | reported |
| OB05 | I04 / C068 | 2026H1 | 2026-09-16T09:00:00+08:00 | ~20 % | null / null | reported |
| OB06 | I05 / C074 | 1990年代早期 | 2026-09-16T09:00:00+08:00 | ~100 % | null / null | reported |
| OB07 | I05 / C076 | 2026-06-30 | 2026-09-16T09:00:00+08:00 | ~66.7 % | null / null | reported_rounded_fraction |
| OB08 | I06 / C077 | 2026-06-30 | 2026-09-16T09:00:00+08:00 | ~60 % | null / null | reported |
| OB09 | I07 / C078 | 2026-06-30 | 2026-09-16T09:00:00+08:00 | ~33.3 % | null / null | reported_rounded_fraction |
| OB10 | I08 / C079 | 2026-06-30 | 2026-09-16T09:00:00+08:00 | ~30 % | null / null | reported |
| OB11 | I09 / C080 | 2026-06-30 | null | ~10 % | null / null | creator_calculated_quarantined |
| OB12 | I10 / C091 | 近十年起点unknown | 2026-09-16T09:00:00+08:00 | >60 % | null / null | reported_denominator_unresolved |
| OB13 | I10 / C091 | 近十年终点unknown | 2026-09-16T09:00:00+08:00 | ~10 % | null / null | reported_denominator_unresolved |
| OB14 | I11 / C092 | unknown | 2026-09-16T09:00:00+08:00 | >70 % | null / null | reported_denominator_unresolved |
| OB15 | I12 / C093 | 过去几年unknown | 2026-09-16T09:00:00+08:00 | ~20 % | null / null | reported |
| OB16 | I13 / C095 | 过去几年unknown | 2026-09-16T09:00:00+08:00 | ~20 % | null / null | reported |
| OB17 | I14 / C096 | 过去几年unknown | 2026-09-16T09:00:00+08:00 | 两位数以上 % | null / null | reported |
| OB18 | I15 / C097 | 过去几年unknown | 2026-09-16T09:00:00+08:00 | 两位数以上 % | null / null | reported |
| OB19 | I16 / C060 | 预算阶段unknown | null | 700多 亿元 | null / null | creator_reported |
| OB20 | I17 / C061 | 运营预测年unknown | null | 50多 亿元/年 | null / null | creator_metric_mismatch_quarantined |
| OB21 | I22 / C122 | unknown | null | 2%点几 % | null / null | creator_reported_unverified |
| OB22 | I16 / null | 2022年开工时估算 | 2022-09-09 | 727.3 亿元 | null / null | official_reported_estimate |
| OB23 | I17 / null | 建成运营后预测年unknown | 2023-05-29 | >=52 亿元/年 | null / null | projected_transport_cost_saving |

所有报告性观测保留来源身份，非已审计事实。OB11（股票10%）和OB20（社会效益50多亿）隔离，不作为canonical。三分之一记作~33.3仅为结构化近似表达，不提高原精度。

### Policies


```json
[
  {
    "policy_id": "PL01",
    "name": "地方政府债务限额置换存量隐性债务安排",
    "source_ids": [
      "SRC12",
      "SRC13"
    ],
    "event_id": "EV05",
    "implementing_period": "2024—2026（限额安排）",
    "claim_refs": [
      "C045",
      "C050",
      "C053"
    ],
    "interpretation": "地方债务限额政策，不能改写为中央直接接管全部债务或仅闭门展期。"
  },
  {
    "policy_id": "PL02",
    "name": "金融五篇大文章",
    "source_ids": [
      "SRC06"
    ],
    "claim_refs": [
      "C092",
      "C093",
      "C095",
      "C096",
      "C097"
    ],
    "implementing_period": "unknown",
    "interpretation": "政策分类、资金投向观测和效率结果分开；本期列举不是完整五项定义。"
  }
]
```

## 8. EXPECTATION SNAPSHOTS

none。“大家普遍认为紧缩不久”缺Population边界；企业选择债券不自动等于可观察的集体预期。

## 9. VERACITY ASSESSMENTS

以下逐Claim评估。时间为2026-09-24、as_of固定知识截止；observer=model。verified只表示该命题已有足够直接支持，不把引述匹配当底层事实全部核实。

| assessment_id | Claim | veracity | evidence_sources | 理由 |
| --- | --- | --- | --- | --- |
| VA-C001 | C001 | uncertain | ["SRC06"] | 网页标示9月16日；网址路径9月15日也不能代替发布时间，未确认是否另有提前版本。 |
| VA-C002 | C002 | verified | ["SRC09"] | 9月16日FOMC公告支持加息事实。 |
| VA-C003 | C003 | likely_true | ["SRC10"] | 9月18日已宣布，9月24日生效；只有按宣布口径成立。 |
| VA-C004 | C004 | verified | ["SRC11"] | 9月10日决定加息，9月16日生效。 |
| VA-C005 | C005 | unverifiable | [] | 同为央行行长不能证明私人认知或写作意图。 |
| VA-C006 | C006 | uncertain | ["SRC06"] | 是9527的潜台词解读，不能归给官方。 |
| VA-C007 | C007 | uncertain | ["SRC09","SRC10","SRC11"] | 部分央行加息不足以判定全球金融条件总体转向。 |
| VA-C008 | C008 | unverifiable | [] | 未定位历史节目，不创建历史Forecast。 |
| VA-C009 | C009 | uncertain | [] | 没有周期定义和统计序列。 |
| VA-C010 | C010 | unverifiable | [] | 无人群边界、调查时间和样本，不建ExpectationSnapshot。 |
| VA-C011 | C011 | uncertain | [] | 情景讨论而非基准预测，时窗未知。 |
| VA-C012 | C012 | uncertain | [] | 人名、利率种类、渐进还是单次均需核验，不接受数字纠错。 |
| VA-C013 | C013 | uncertain | [] | 9527转述的未署名观点；需债务期限、再定价及财政约束模型。 |
| VA-C014 | C014 | uncertain | [] | 缺债务口径、实际付息率、GDP和再定价速度；不能当现状数据。 |
| VA-C015 | C015 | uncertain | [] | 财政信用与利差吸引力方向可能相反，未给判别条件。 |
| VA-C016 | C016 | uncertain | [] | 相对优势机制可讨论，但竞争者变差与替代约束未被证明。 |
| VA-C017 | C017 | unverifiable | [] | 猜测意图，且滚续不等于拒绝履约。 |
| VA-C018 | C018 | uncertain | [] | 缺行为证据，收益主体与成本承担者混用。 |
| VA-C019 | C019 | uncertain | ["SRC09"] | 维持充足准备金不等于已验证持续扩表，需资产负债表序列。 |
| VA-C020 | C020 | uncertain | [] | 央行资产负债表与财政债务不是同一变量，缺传导机制。 |
| VA-C021 | C021 | uncertain | [] | 也可能减持、对冲或要求更高风险溢价。 |
| VA-C022 | C022 | uncertain | [] | 单一动机解释，未提供历史档案。 |
| VA-C023 | C023 | uncertain | [] | 方向可讨论，人口全称与具体因果未获验证。 |
| VA-C024 | C024 | uncertain | [] | 需区分宣战、军事实效、此前绥靖，并需音频确认原句。 |
| VA-C025 | C025 | likely_false | ["SRC14"] | 如指慕尼黑协议，则1938年在波兰战争之前；地名和引语也待听。 |
| VA-C026 | C026 | uncertain | [] | 历史类比不能证明当代意图或效果。 |
| VA-C027 | C027 | uncertain | ["SRC06"] | 9527解读，未见文章直接论述该阴谋式策略。 |
| VA-C028 | C028 | unverifiable | [] | 央行和商业银行职责不能等同，缺个人意图证据。 |
| VA-C029 | C029 | likely_true | ["SRC06"] | 原文方向相符，原始统计表未独立复算。 |
| VA-C030 | C030 | likely_true | ["SRC06"] | 原文方向相符；不代表纯民间股权融资。 |
| VA-C031 | C031 | likely_true | ["SRC06"] | 引用相符；间接融资不能完全等同贷款。 |
| VA-C032 | C032 | uncertain | ["SRC19"] | 债权情形有解释力，但把股权融资概括为借款不充分。 SEC 2013教育公告明确区分股票所有权与债券偿债义务；不代表已听验原话。 |
| VA-C033 | C033 | likely_false | ["SRC19"] | 股权与债权偿付义务不同；仍须音频排除识别错误。 SEC 2013教育公告明确区分股票所有权与债券偿债义务；不代表已听验原话。 |
| VA-C034 | C034 | likely_true | [] | 是简化描述，不是完整货币创造或风险模型。 |
| VA-C035 | C035 | uncertain | [] | 信任机制合理但未排除监管、市场基础设施等因素。 |
| VA-C036 | C036 | uncertain | [] | 事件界定不清，因果未证实；需拆出2013事件事实核验。 |
| VA-C037 | C037 | likely_true | ["SRC06"] | 与文章一致，但年度原始统计表尚未定位。 |
| VA-C038 | C038 | likely_true | ["SRC06"] | 引用口径相符；不是股权占47%。 |
| VA-C039 | C039 | likely_true | ["SRC06"] | 文章有此表述，首次仍需历史序列。 |
| VA-C040 | C040 | uncertain | ["SRC06"] | 起点是间接融资占比，终点是贷款比较上界，口径不严格相同。 |
| VA-C041 | C041 | uncertain | ["SRC06"] | 增量单年与存量主导地位不同，且直接融资包含政府债。 |
| VA-C042 | C042 | uncertain | [] | 存量、月增量、同比增长均未明确，转写涉容涉零待听。 |
| VA-C043 | C043 | unverifiable | [] | 9527对动机的归因，不是官方承认的目的。 |
| VA-C044 | C044 | unverifiable | [] | 评价性判断；与安抚动机并不逻辑矛盾。 |
| VA-C045 | C045 | likely_true | ["SRC06","SRC12"] | 分类替代机制有支持，定量贡献未分解。 |
| VA-C046 | C046 | uncertain | ["SRC06"] | 需区分贷款存量核销、社融增量中核销项和统计处理。 |
| VA-C047 | C047 | uncertain | [] | 地区、平台、币种、期限不明确。 |
| VA-C048 | C048 | uncertain | [] | 转写同时有20%、2%点几；还混合国债与地方专项债。 |
| VA-C049 | C049 | likely_false | ["SRC18"] | 熊猫债是境外机构在境内发行人民币债券；中国中央在境外发债不属该定义。原声音及是否口误仍需复核，不改转写。 |
| VA-C050 | C050 | likely_true | [] | 静态利差方向成立，规模期限费用及折价未计，不证明实际全部实现。 |
| VA-C051 | C051 | uncertain | [] | 未列案件；过程成本概念不能验证规模强度。 |
| VA-C052 | C052 | uncertain | [] | 强因果与量词无案件证据，不能概括全部化债。 |
| VA-C053 | C053 | disputed | ["SRC12"] | 存在法定限额及债券置换机制，谈判不是排他解释；不能抹去可能存在的谈判。 |
| VA-C054 | C054 | uncertain | [] | 分类变化不等于本金减少，也不充分测量现金流和偿付能力。 |
| VA-C055 | C055 | uncertain | ["SRC12"] | 历史政策存在不能验证截至2026年完成，需余额、违约和现金流证据。 |
| VA-C056 | C056 | unverifiable | [] | 未提供机构、报告或原句。 |
| VA-C057 | C057 | uncertain | [] | 与紧邻的经常看到危言耸听有表面张力，但人群范围可能不同。 |
| VA-C058 | C058 | unverifiable | [] | 历史源未提供，不推建历史Forecast。 |
| VA-C059 | C059 | uncertain | [] | 项目推进也可能来自补贴或行政动员，公信力非直接观测量。 |
| VA-C060 | C060 | likely_true | ["SRC07"] | 估算总投资727.3亿元支持数量级，非已完成决算。 |
| VA-C061 | C061 | uncertain | ["SRC08"] | 来源是预计节约运输费用，不是已实现综合效益或项目现金收入。 |
| VA-C062 | C062 | uncertain | [] | 134可能是十三四的ASR；即便除法正确也不能以运输节约充当现金回款。 |
| VA-C063 | C063 | uncertain | [] | 没有收入、费用、折现及爬坡模型，不能作为财务预测基准。 |
| VA-C064 | C064 | uncertain | ["SRC07"] | 工程总体存在，但具体水深水宽及水量说法未核验。 |
| VA-C065 | C065 | uncertain | [] | 项目存在不等于偿债能力改善，更不证明既有隐债已解决。 |
| VA-C066 | C066 | uncertain | ["SRC06"] | 原文表达一致，但没有给出剔除方法或分解表。 |
| VA-C067 | C067 | likely_true | ["SRC06"] | 文本有支持，分母是否企业贷款及期限口径需原始表。 |
| VA-C068 | C068 | likely_true | ["SRC06"] | 首次读数清楚；后文重述转写损坏单独留Review。 |
| VA-C069 | C069 | uncertain | [] | 优质项目非全部企业，无报价和审批数据。 |
| VA-C070 | C070 | uncertain | [] | 数量比不能识别相对成本，受准入、期限和企业构成影响。 |
| VA-C071 | C071 | uncertain | [] | 隐性支持、显性担保及资本约束需分开，并非统一信用额度池。 |
| VA-C072 | C072 | uncertain | [] | 银行持债、承销、或有负债和政府债发行可能使风险仍回到银行或财政。 |
| VA-C073 | C073 | uncertain | [] | 概念区分明确，但统计范围未给；与C094需核对时间口径。 |
| VA-C074 | C074 | likely_true | ["SRC06"] | 文章如此描述，历史社融回溯序列未独立复核。 |
| VA-C075 | C075 | uncertain | [] | 信任因素非排他解释，忽略制度与市场准入。 |
| VA-C076 | C076 | likely_true | ["SRC06"] | 文章支持，待统计表复核。 |
| VA-C077 | C077 | likely_true | ["SRC06"] | 与间接融资不是同一指标。 |
| VA-C078 | C078 | likely_true | ["SRC06"] | 文章支持；不可直接解释为民间风险资本。 |
| VA-C079 | C079 | likely_true | ["SRC06"] | 需区分政府债和企业债。 |
| VA-C080 | C080 | likely_false | [] | 若同分母且直接融资仅由债券与股票构成，1/3减30%约3.3个百分点；不是核实的股票观测值。 |
| VA-C081 | C081 | uncertain | ["SRC06"] | 属于结构评价，协调没有可检验阈值。 |
| VA-C082 | C082 | uncertain | [] | 趋势外推无窗口，不能等同官方目标。 |
| VA-C083 | C083 | unverifiable | [] | 规范性比例主张，不冒充承诺达到该值的预测。 |
| VA-C084 | C084 | unverifiable | [] | 无抽样、机构和收入数据。 |
| VA-C085 | C085 | uncertain | [] | 占比不推出总利润，需净息差、规模、信用成本及证券业务。 |
| VA-C086 | C086 | uncertain | [] | 未界定萎缩指标，数量、占比和利润可异向。 |
| VA-C087 | C087 | uncertain | [] | 利润规模和盈利能力不同，必须单独评估。 |
| VA-C088 | C088 | uncertain | [] | 表外、非标、中间业务不能混为一类，需监管和风险调整收益。 |
| VA-C089 | C089 | unverifiable | [] | 职业建议不是事实，不能推出个体必然获益。 |
| VA-C090 | C090 | uncertain | [] | 组织任用还受风控、资历、考核和治理影响。 |
| VA-C091 | C091 | uncertain | ["SRC06"] | 原文也写在全部贷款中，增量/存量分母歧义须保留。 |
| VA-C092 | C092 | uncertain | ["SRC06"] | 分母、分类交叉去重和起止时间未给。 |
| VA-C093 | C093 | likely_true | ["SRC06"] | 文章支持；增速基期和定义须原表补充。 |
| VA-C094 | C094 | uncertain | [] | 与C073的绝对值仍增加不一致，但同时间同口径未满足，不直接建CONTRADICTS。 |
| VA-C095 | C095 | likely_true | ["SRC06"] | 与科技中小企业增速不合并，复合年均或算术平均未知。 |
| VA-C096 | C096 | likely_true | ["SRC06"] | 单独拆分，不把绿色与养老当一个指标。 |
| VA-C097 | C097 | likely_true | ["SRC06"] | 与绿色贷款是不同统计对象。 |
| VA-C098 | C098 | uncertain | ["SRC06"] | 逐年还是期间平均不明，需要同基期比较。 |
| VA-C099 | C099 | uncertain | [] | 政策扶持、风险补偿、纾困也可带来资金流入。 |
| VA-C100 | C100 | uncertain | [] | 供给是条件而非结果，血液类比不能替代收益和生产率证据。 |
| VA-C101 | C101 | uncertain | [] | 缺直接融资分行业、分阶段、净新增序列。 |
| VA-C102 | C102 | likely_true | ["SRC06"] | 有理论和文章支持，不等于所有企业同轨迹。 |
| VA-C103 | C103 | uncertain | ["SRC06"] | core_claim_supported但quantifier_overstated；约束不等于全部银行完全不能参与。 |
| VA-C104 | C104 | uncertain | ["SRC06"] | 方向有支持，民间占比和主导份额未证明。 |
| VA-C105 | C105 | uncertain | [] | 排他量词过强，需考虑银行系机构、托管和间接参与。 |
| VA-C106 | C106 | uncertain | [] | 社融直接融资包含政府债，不能当作创投份额序列。 |
| VA-C107 | C107 | uncertain | [] | 融资分类变化不是产出、效率或创新成功的充分指标。 |
| VA-C108 | C108 | uncertain | [] | 需募投退、阶段和币种可比数据。 |
| VA-C109 | C109 | uncertain | [] | 缺投资样本、选择机制和失败案例。 |
| VA-C110 | C110 | uncertain | [] | 强排他量词无支持，不能把相对优势改写成独占。 |
| VA-C111 | C111 | uncertain | [] | 保留损坏文本，数值设null，不猜600万或700万。 |
| VA-C112 | C112 | unverifiable | [] | 是主观类比，不是汇率换算或可比购买力观测。 |
| VA-C113 | C113 | uncertain | [] | 需共同币种、估值、回报、退出和汇率风险比较。 |
| VA-C114 | C114 | uncertain | [] | 援引文章总体数据不能单独证明人民币早期风险资本增长。 |
| VA-C115 | C115 | uncertain | [] | 跨越融资类别、产业、币种及跨国比较多个层级，缺直接比较证据。 |
| VA-C116 | C116 | likely_true | ["SRC06","SRC09"] | 网页公开早于FOMC公告可支持文章先已写成；未获手稿或确切写作时间。 |
| VA-C117 | C117 | uncertain | [] | 事件地域和定义不明，不能擅自映射为中国钱荒或欧债危机。 |
| VA-C118 | C118 | uncertain | [] | 从风险转移机制进一步外推主权举债能力，非既有事实。 |
| VA-C119 | C119 | uncertain | [] | 晋升与地位不同，需组织层面验证。 |
| VA-C120 | C120 | uncertain | [] | 组织规则未知，不能与晋升共用验证结论。 |
| VA-C121 | C121 | uncertain | [] | 与相邻2%以下不一致，疑似ASR但不改原句。 |
| VA-C122 | C122 | uncertain | [] | 未指定日期、券种和到期收益率口径。 |
| VA-C123 | C123 | unverifiable | [] | 没有案件、样本和人名，不能据此推断化债全貌。 |
| VA-C124 | C124 | uncertain | [] | 水深、挖深和底高程可能混淆，需设计断面。 |
| VA-C125 | C125 | uncertain | [] | 需航道设计资料，不能以工程存在确认尺寸。 |
| VA-MC01 | MC01 | uncertain | ["SRC03"] | 条件结构用于定位缺失环节；条件是否满足未获证明。 |
| VA-MC02 | MC02 | uncertain | ["SRC03"] | 条件结构用于定位缺失环节；条件是否满足未获证明。 |
| VA-MC03 | MC03 | uncertain | ["SRC03"] | 条件结构用于定位缺失环节；条件是否满足未获证明。 |
| VA-MC04 | MC04 | uncertain | ["SRC03"] | 条件结构用于定位缺失环节；条件是否满足未获证明。 |
| VA-MC05 | MC05 | uncertain | ["SRC03"] | 条件结构用于定位缺失环节；条件是否满足未获证明。 |
| VA-MC06 | MC06 | uncertain | ["SRC03"] | 条件结构用于定位缺失环节；条件是否满足未获证明。 |

所有数值类likely_true仍有对应Review；数字与原文一致、分母可靠、实际音频说法正确是三个不同检查。

## 10. NARRATIVE ASSESSMENTS


```json
[
  {
    "assessment_id": "NA01",
    "observer": "A001",
    "time": "2026-09-21T10:32:21+08:00",
    "scope": "SRC06文章外部语境",
    "narrative_role": "core_signal",
    "claim_refs": [
      "C006",
      "C027"
    ],
    "accepts_fact": "未否认文中融资变化",
    "accepts_causal": "添加未明说的美元风险因果",
    "cause_or_effect": "战略风险背景信号",
    "missing_variable": "未明确",
    "information_gain": "high",
    "note": "未称假新闻；潜台词属于9527。"
  },
  {
    "assessment_id": "NA02",
    "observer": "A001",
    "time": "2026-09-21T10:32:21+08:00",
    "scope": "SRC06文章沟通背景",
    "narrative_role": "reassurance",
    "claim_refs": [
      "C043",
      "C044"
    ],
    "accepts_fact": "接受文中数据",
    "accepts_causal": "不以安抚目的否定分析价值",
    "cause_or_effect": "安抚是背景；结构转向是信息增量",
    "missing_variable": "unknown",
    "information_gain": "high",
    "note": "背景、目的、本质在原话中来回调整，应保留而非定为烟雾弹。"
  },
  {
    "assessment_id": "NA03",
    "observer": "A001",
    "time": "2026-09-21T10:32:21+08:00",
    "scope": "高息换低息解释",
    "narrative_role": "causal_obscuring",
    "claim_refs": [
      "C050",
      "C051",
      "C052",
      "C053"
    ],
    "accepts_fact": "部分正确",
    "accepts_causal": "认为不是完整机制",
    "cause_or_effect": "成本下降解释遗漏实操过程",
    "missing_variable": "合规、确权、谈判与过程成本",
    "information_gain": "high",
    "note": "causal_obscuring为模型对9527明确批评的分类，不代表9527说该英文标签。"
  },
  {
    "assessment_id": "NA04",
    "observer": "A001",
    "time": "2026-09-21T10:32:21+08:00",
    "scope": "信贷投向统计",
    "narrative_role": "core_signal",
    "claim_refs": [
      "C091",
      "C099",
      "C100"
    ],
    "accepts_fact": true,
    "accepts_causal": "从投向追加机会与转型解释",
    "cause_or_effect": "市场机会的信号和成长条件",
    "missing_variable": "unknown",
    "information_gain": "high"
  },
  {
    "assessment_id": "NA05",
    "observer": "model",
    "time": "2026-09-24",
    "scope": "C114/C115借用官方权威",
    "narrative_role": "supporting_signal",
    "claim_refs": [
      "C114",
      "C115"
    ],
    "accepts_fact": "只能确认官方提供总体结构数据",
    "accepts_causal": false,
    "cause_or_effect": "数据到竞争结论尚缺桥梁",
    "missing_variable": "风险资本币种、阶段和跨国比较",
    "information_gain": "high",
    "note": "不得把9527关于中美竞争的结论归给潘功胜。"
  }
]
```

## 11. ARGUMENTS

推理边`INFERENTIAL_SUPPORT_CANDIDATE`是本次明确申报的候选关系，不冒充已有registry枚举。每步限制均保存于JSON；下文保留from/to、模式、表达层级、证据与最弱环节。

### AR01 · 由央行共同处境推断文章隐含外部风险信号

`argument_type`=causal；`premises`=["C002","C003","C004"]；`conclusion`=C027；`inference_mode`=["analogy","speculation"]；`expression_level`=["explicit"]；`hop_count`=3（列出边数，非总是最长路径）。

| step | from → to / relation | inference_mode | expression_level | evidence | 解释 / limitations |
| --- | --- | --- | --- | --- | --- |
| AR01.1 | ["C002","C003","C004"] → C005 / INFERENTIAL_SUPPORT_CANDIDATE | analogy | explicit | ["SS-C002","SS-C003","SS-C004","SS-C005"] | 同职业与相近政策环境被用作能够预判的理由 / 成立程度见逐Claim评估；最弱处是把角色相似推成私人认知，再把认知推成写作意图 |
| AR01.2 | ["C005"] → C006 / INFERENTIAL_SUPPORT_CANDIDATE | speculation | explicit | ["SS-C005","SS-C006"] | 从可预判推为文章潜台词 / 成立程度见逐Claim评估；最弱处是把角色相似推成私人认知，再把认知推成写作意图 |
| AR01.3 | ["C006","C026"] → C027 / INFERENTIAL_SUPPORT_CANDIDATE | speculation | explicit | ["SS-C006","SS-C026","SS-C027"] | 把美元风险场景读入文章 / 成立程度见逐Claim评估；最弱处是把角色相似推成私人认知，再把认知推成写作意图 |

**Argument limitation：最弱处是把角色相似推成私人认知，再把认知推成写作意图；发布时间先后不能验证目的。**

### AR02 · 高债务、相对优势与短期加息策略

`argument_type`=causal；`premises`=["C013","C014","C016"]；`conclusion`=C021；`inference_mode`=["causal","speculation"]；`expression_level`=["explicit"]；`hop_count`=3（列出边数，非总是最长路径）。

| step | from → to / relation | inference_mode | expression_level | evidence | 解释 / limitations |
| --- | --- | --- | --- | --- | --- |
| AR02.1 | ["C013","C014"] → C015 / INFERENTIAL_SUPPORT_CANDIDATE | causal | explicit | ["SS-C013","SS-C014","SS-C015"] | 高息增加负担而损害信用 / 成立程度见逐Claim评估；利息/GDP算术缺输入 |
| AR02.2 | ["C015","C016"] → C018 / INFERENTIAL_SUPPORT_CANDIDATE | speculation | explicit | ["SS-C015","SS-C016","SS-C018"] | 相对优势可能使短期收益先于长期成本兑现 / 成立程度见逐Claim评估；利息/GDP算术缺输入 |
| AR02.3 | ["C019","C020"] → C021 / INFERENTIAL_SUPPORT_CANDIDATE | speculation | explicit | ["SS-C019","SS-C020","SS-C021"] | 大额持仓的损失厌恶可能强化容忍 / 成立程度见逐Claim评估；利息/GDP算术缺输入 |

**Argument limitation：利息/GDP算术缺输入；财政与央行资产负债表不可混同；债权人也可能退出；三个分支非完整线性证明。**

### AR03 · 从英法绥靖类比美元债权人容忍

`argument_type`=historical_analogy；`premises`=["C022","C023","C024","C025"]；`conclusion`=C021；`inference_mode`=["analogy"]；`expression_level`=["explicit","strongly_implied"]；`hop_count`=2（列出边数，非总是最长路径）。

| step | from → to / relation | inference_mode | expression_level | evidence | 解释 / limitations |
| --- | --- | --- | --- | --- | --- |
| AR03.1 | ["C022","C023","C024","C025"] → C026 / INFERENTIAL_SUPPORT_CANDIDATE | analogy | explicit | ["SS-C022","SS-C023","SS-C024","SS-C025","SS-C026"] | 把损失厌恶与策略性试探迁移到美联储 / 成立程度见逐Claim评估；历史时序及总体动机有疑点 |
| AR03.2 | ["C026"] → C021 / INFERENTIAL_SUPPORT_CANDIDATE | analogy | strongly_implied | ["SS-C026","SS-C021"] | 以历史类比增强大而不能倒的可行性 / 成立程度见逐Claim评估；历史时序及总体动机有疑点 |

**Argument limitation：历史时序及总体动机有疑点；国家战争决策与可交易债券持仓的退出机制、目标和约束不同。**


```json
{
  "source_case": "二战前英法对纳粹德国的绥靖（按9527叙述）",
  "target_case": "美债持有者对美国激进政策的容忍",
  "shared_mechanism": "既有损失暴露与风险厌恶可能被策略性利用",
  "limits_of_analogy": "外交安全承诺不是可出售债券；不能用希特勒的意图证明美联储意图。"
}
```

### AR04 · 融资结构分类变化到化债基本解决

`argument_type`=causal；`premises`=["C045","C046","C050","C051","C053"]；`conclusion`=C055；`inference_mode`=["causal"]；`expression_level`=["explicit"]；`hop_count`=2（列出边数，非总是最长路径）。

| step | from → to / relation | inference_mode | expression_level | evidence | 解释 / limitations |
| --- | --- | --- | --- | --- | --- |
| AR04.1 | ["C045","C046","C053"] → C054 / INFERENTIAL_SUPPORT_CANDIDATE | causal | explicit | ["SS-C045","SS-C046","SS-C053","SS-C054"] | 把贷款转债券及谈判展期视作债务压力减轻的表现 / 成立程度见逐Claim评估；最弱是最后一步 |
| AR04.2 | ["C054"] → C055 / INFERENTIAL_SUPPORT_CANDIDATE | causal | explicit | ["SS-C054","SS-C055"] | 由压力缓释升级为基本解决 / 成立程度见逐Claim评估；最弱是最后一步 |

**Argument limitation：最弱是最后一步；统计分类替代、降息、展期、本金削减和可持续偿债分别不同；未给隐债余额及现金流，政府债也可能被银行持有。**

### AR05 · 平陆运河长期投入到化债信心

`argument_type`=case_based_signal_inference；`premises`=["C060","C061","C062","C063","C064"]；`conclusion`=C065；`inference_mode`=["causal"]；`expression_level`=["explicit"]；`hop_count`=2（列出边数，非总是最长路径）。

| step | from → to / relation | inference_mode | expression_level | evidence | 解释 / limitations |
| --- | --- | --- | --- | --- | --- |
| AR05.1 | ["C060","C061","C063","C064"] → C059 / INFERENTIAL_SUPPORT_CANDIDATE | causal | explicit | ["SS-C060","SS-C061","SS-C063","SS-C064","SS-C059"] | 长期低现金回报工程能够推进，被视作政府承诺可信 / 成立程度见逐Claim评估；社会运输成本节约不是项目现金流 |
| AR05.2 | ["C059"] → C065 / INFERENTIAL_SUPPORT_CANDIDATE | causal | explicit | ["SS-C059","SS-C065"] | 长期承诺转换为债权人信心 / 成立程度见逐Claim评估；社会运输成本节约不是项目现金流 |

**Argument limitation：社会运输成本节约不是项目现金流；投资/社会效益不是财务回收期；能动员项目资金不等于能偿还所有债务。**


```json
{
  "source_case": "平陆运河长期建设",
  "target_case": "政府化债信用",
  "shared_mechanism": "以可见的长期投入传递承诺",
  "limits_of_analogy": "本段是当期案例信号推理，并非历史跨案例类比；若强制只提供historical_analogy枚举会误分类。"
}
```

### AR06 · 企业融资数量比到直接融资成本更低

`argument_type`=causal；`premises`=["C067","C068","C069"]；`conclusion`=C070；`inference_mode`=["causal"]；`expression_level`=["explicit"]；`hop_count`=1（列出边数，非总是最长路径）。

| step | from → to / relation | inference_mode | expression_level | evidence | 解释 / limitations |
| --- | --- | --- | --- | --- | --- |
| AR06.1 | ["C067","C068","C069"] → C070 / INFERENTIAL_SUPPORT_CANDIDATE | causal | explicit | ["SS-C067","SS-C068","SS-C069","SS-C070"] | 在低贷款利率下仍转向债券，被解释为债券融资更便宜 / 成立程度见逐Claim评估；最弱是以数量选择反推价格 |

**Argument limitation：最弱是以数量选择反推价格；贷款分母变动、融资期限、主体资质、准入和发行政策都可产生同样数量比。**

### AR07 · 直接融资风险转移到主权举债空间

`argument_type`=causal；`premises`=["C071","C072"]；`conclusion`=C118；`inference_mode`=["causal"]；`expression_level`=["model_reconstruction"]；`hop_count`=2（列出边数，非总是最长路径）。

| step | from → to / relation | inference_mode | expression_level | evidence | 解释 / limitations |
| --- | --- | --- | --- | --- | --- |
| AR07.1 | ["C071","C072"] → MC04 / INFERENTIAL_SUPPORT_CANDIDATE | causal | model_reconstruction | ["SS-C071","SS-C072","SS-MC04"] | 拆出风险确实离开银行且财政不回兜的必要条件 / 最弱是把国家信用当固定额度池；直接融资不等于无银行、无担保、无财政风险；MC04条件未被主播证明。 |
| AR07.2 | ["MC04"] → C118 / INFERENTIAL_SUPPORT_CANDIDATE | causal | model_reconstruction | ["SS-MC04","SS-C118"] | 尚需财政担保负担与主权举债空间相连才能完成推导 / 最弱是把国家信用当固定额度池；直接融资不等于无银行、无担保、无财政风险；MC04条件未被主播证明。 |

**Argument limitation：最弱是把国家信用当固定额度池；直接融资不等于无银行、无担保、无财政风险；MC04条件未被主播证明。**

### AR08 · 直接融资替代到银行利润压力

`argument_type`=causal；`premises`=["C029","C030","C076","C078"]；`conclusion`=C088；`inference_mode`=["causal","speculation"]；`expression_level`=["model_reconstruction","strongly_implied","explicit"]；`hop_count`=6（列出边数，非总是最长路径）。

| step | from → to / relation | inference_mode | expression_level | evidence | 解释 / limitations |
| --- | --- | --- | --- | --- | --- |
| AR08.1 | ["C029","C030","C078"] → MC01 / INFERENTIAL_SUPPORT_CANDIDATE | causal | model_reconstruction | ["SS-C029","SS-C030","SS-C078","SS-MC01"] | 区分市场份额变化与真实贷款替代 / 最弱是传统信贷份额下降跳到总利润下降；直接融资可能增加银行持债、承销与托管收入；非标、表外和中间业务不等价；长期不能当短期择业保证。 |
| AR08.2 | ["MC01"] → MC02 / INFERENTIAL_SUPPORT_CANDIDATE | causal | model_reconstruction | ["SS-MC01","SS-MC02"] | 加入利差与收入补偿条件 / 最弱是传统信贷份额下降跳到总利润下降；直接融资可能增加银行持债、承销与托管收入；非标、表外和中间业务不等价；长期不能当短期择业保证。 |
| AR08.3 | ["MC02"] → C086 / INFERENTIAL_SUPPORT_CANDIDATE | causal | strongly_implied | ["SS-MC02","SS-C086"] | 传统业务承压是主播明说的方向，机制只部分交代 / 成立程度见逐Claim评估；最弱是传统信贷份额下降跳到总利润下降 |
| AR08.4 | ["C086"] → MC03 / INFERENTIAL_SUPPORT_CANDIDATE | causal | model_reconstruction | ["SS-C086","SS-MC03"] | 加入总量增长、信用成本、非信贷收入补偿条件 / 最弱是传统信贷份额下降跳到总利润下降；直接融资可能增加银行持债、承销与托管收入；非标、表外和中间业务不等价；长期不能当短期择业保证。 |
| AR08.5 | ["MC03"] → C087 / INFERENTIAL_SUPPORT_CANDIDATE | causal | model_reconstruction | ["SS-MC03","SS-C087"] | 条件均满足才推出总利润下降 / 最弱是传统信贷份额下降跳到总利润下降；直接融资可能增加银行持债、承销与托管收入；非标、表外和中间业务不等价；长期不能当短期择业保证。 |
| AR08.6 | ["C085","C087"] → C088 / INFERENTIAL_SUPPORT_CANDIDATE | speculation | explicit | ["SS-C085","SS-C087","SS-C088"] | 主播据此主张表外业务是未来利润方向 / 成立程度见逐Claim评估；最弱是传统信贷份额下降跳到总利润下降 |

**Argument limitation：最弱是传统信贷份额下降跳到总利润下降；直接融资可能增加银行持债、承销与托管收入；非标、表外和中间业务不等价；长期不能当短期择业保证。**

### AR09 · 资金流向到新产业机会

`argument_type`=mixed_statistical_and_analogy；`premises`=["C091","C092","C093","C095","C096","C097"]；`conclusion`=C107；`inference_mode`=["statistical","analogy","causal"]；`expression_level`=["explicit"]；`hop_count`=3（列出边数，非总是最长路径）。

| step | from → to / relation | inference_mode | expression_level | evidence | 解释 / limitations |
| --- | --- | --- | --- | --- | --- |
| AR09.1 | ["C091","C092","C093","C095","C096","C097"] → C099 / INFERENTIAL_SUPPORT_CANDIDATE | statistical | explicit | ["SS-C091","SS-C092","SS-C093","SS-C095","SS-C096","SS-C097","SS-C099"] | 把投向变化当市场机会分布的观察信号 / 成立程度见逐Claim评估；最弱是从资金供给推为转型结果 |
| AR09.2 | ["C099"] → C100 / INFERENTIAL_SUPPORT_CANDIDATE | analogy | explicit | ["SS-C099","SS-C100"] | 用血液供给比喻融资条件与未来成长空间 / 成立程度见逐Claim评估；最弱是从资金供给推为转型结果 |
| AR09.3 | ["C100","C106"] → C107 / INFERENTIAL_SUPPORT_CANDIDATE | causal | explicit | ["SS-C100","SS-C106","SS-C107"] | 由机会和早期资本扩张推到动能转换正在实现 / 成立程度见逐Claim评估；最弱是从资金供给推为转型结果 |

**Argument limitation：最弱是从资金供给推为转型结果；投向可能由政策补贴或纾困驱动，需产出、生产率及违约数据；血液比喻只提供启发。**


```json
{
  "source_case": "人体供血与组织功能（比喻）",
  "target_case": "产业融资供给和成长",
  "shared_mechanism": "资源支持影响活动空间",
  "limits_of_analogy": "生理系统与投资市场的资源配置机制不同；不是历史类比，更不是收益率证明。"
}
```

### AR10 · 科技企业生命周期与银行适配约束

`argument_type`=causal；`premises`=["C102"]；`conclusion`=C106；`inference_mode`=["causal","statistical"]；`expression_level`=["explicit"]；`hop_count`=3（列出边数，非总是最长路径）。

| step | from → to / relation | inference_mode | expression_level | evidence | 解释 / limitations |
| --- | --- | --- | --- | --- | --- |
| AR10.1 | ["C102"] → C103 / INFERENTIAL_SUPPORT_CANDIDATE | causal | explicit | ["SS-C102","SS-C103"] | 早期回报滞后及失败风险限制传统银行 / 成立程度见逐Claim评估；最弱是从功能适配推到已观测规模增长 |
| AR10.2 | ["C103"] → C104 / INFERENTIAL_SUPPORT_CANDIDATE | causal | explicit | ["SS-C103","SS-C104"] | 高风险承受能力由天使等资本补充 / 成立程度见逐Claim评估；最弱是从功能适配推到已观测规模增长 |
| AR10.3 | ["C104"] → C106 / INFERENTIAL_SUPPORT_CANDIDATE | statistical | explicit | ["SS-C104","SS-C106"] | 主播进一步断言此类资金比例迅速提升 / 成立程度见逐Claim评估；最弱是从功能适配推到已观测规模增长 |

**Argument limitation：最弱是从功能适配推到已观测规模增长；没能力与完全无关系是过强表述；需生命周期分组及银行系投资关系。**

### AR11 · 国内融资变化到中美风险资本竞争

`argument_type`=causal；`premises`=["C078","C102","C104","C106","C108"]；`conclusion`=C115；`inference_mode`=["statistical","causal"]；`expression_level`=["model_reconstruction"]；`hop_count`=4（列出边数，非总是最长路径）。

| step | from → to / relation | inference_mode | expression_level | evidence | 解释 / limitations |
| --- | --- | --- | --- | --- | --- |
| AR11.1 | ["C078","C106"] → MC05 / INFERENTIAL_SUPPORT_CANDIDATE | statistical | model_reconstruction | ["SS-C078","SS-C106","SS-MC05"] | 剥离政府债和普通企业债，要求识别人民币早期股权资金 / 最弱是两次跨口径迁移：社融直接融资→早期人民币风险资本，国内规模→相对美国竞争力；四步都是诊断性拆分，非主播逐句论证。 |
| AR11.2 | ["MC05","C104"] → C114 / INFERENTIAL_SUPPORT_CANDIDATE | causal | model_reconstruction | ["SS-MC05","SS-C104","SS-C114"] | 人民币风险资本确有扩张才支持走上台前 / 最弱是两次跨口径迁移：社融直接融资→早期人民币风险资本，国内规模→相对美国竞争力；四步都是诊断性拆分，非主播逐句论证。 |
| AR11.3 | ["C108","C114"] → MC06 / INFERENTIAL_SUPPORT_CANDIDATE | statistical | model_reconstruction | ["SS-C108","SS-C114","SS-MC06"] | 补同口径跨国、币种、阶段和退出能力比较 / 最弱是两次跨口径迁移：社融直接融资→早期人民币风险资本，国内规模→相对美国竞争力；四步都是诊断性拆分，非主播逐句论证。 |
| AR11.4 | ["MC06"] → C115 / INFERENTIAL_SUPPORT_CANDIDATE | causal | model_reconstruction | ["SS-MC06","SS-C115"] | 比较成立才支持相对竞争地位改善 / 最弱是两次跨口径迁移：社融直接融资→早期人民币风险资本，国内规模→相对美国竞争力；四步都是诊断性拆分，非主播逐句论证。 |

**Argument limitation：最弱是两次跨口径迁移：社融直接融资→早期人民币风险资本，国内规模→相对美国竞争力；四步都是诊断性拆分，非主播逐句论证。**


```json
{
  "creator_expressed_shortcuts": [
    {
      "from": "C106",
      "to": "C107",
      "expression_level": "explicit"
    },
    {
      "from": "C107",
      "to": "C115",
      "expression_level": "explicit"
    },
    {
      "from": "C108",
      "to": "C115",
      "expression_level": "explicit"
    }
  ],
  "expanded_bridge_edges": 4,
  "model_bridge_count": 4,
  "end_to_end_note": "若从科技生命周期起算，AR10前两步（显式）+C104到已增长C106（显式但证据不足）+AR11四步桥接共7个分析步骤；不是客观固定距离，不把捷径再重复相加。"
}
```

### AR12 · 美元汇率优势到美国早期投资优势

`argument_type`=causal；`premises`=["C109","C110","C111","C112"]；`conclusion`=C108；`inference_mode`=["causal"]；`expression_level`=["explicit"]；`hop_count`=2（列出边数，非总是最长路径）。

| step | from → to / relation | inference_mode | expression_level | evidence | 解释 / limitations |
| --- | --- | --- | --- | --- | --- |
| AR12.1 | ["C109","C111","C112"] → C113 / INFERENTIAL_SUPPORT_CANDIDATE | causal | explicit | ["SS-C109","SS-C111","SS-C112","SS-C113"] | 名义换算和主观负担类比被作为项目便宜的依据 / 成立程度见逐Claim评估；最弱是把币值面额差异等同真实资本成本优势 |
| AR12.2 | ["C113"] → C108 / INFERENTIAL_SUPPORT_CANDIDATE | causal | explicit | ["SS-C113","SS-C108"] | 投资划算被用来解释美国风险资本优势 / 成立程度见逐Claim评估；最弱是把币值面额差异等同真实资本成本优势 |

**Argument limitation：最弱是把币值面额差异等同真实资本成本优势；换算原句损坏，主观类比不可计算，且需估值、汇兑、退出和资本供给数据。**

## 12. MECHANISMS


```json
[
  {
    "mechanism_id": "ME01",
    "status": "candidate",
    "name": "融资契约与企业阶段风险适配",
    "chain": [
      "早期研发现金流不确定",
      "固定债务偿付与银行风控适配受限",
      "可承受亏损并分享上行的股权资本相对适配"
    ],
    "argument_refs": [
      "AR10",
      "AR08"
    ],
    "claim_refs": [
      "C102",
      "C103",
      "C104"
    ],
    "expression_level": "mixed_explicit_and_model_reconstruction",
    "scope": "早期高不确定企业，不泛化全部科技/绿色/养老",
    "limitations": "轻资产抵押不足来自外部原文可作候选补充，但本期没有完整展开，不冒充主播核心前提。"
  },
  {
    "mechanism_id": "ME02",
    "status": "candidate",
    "name": "融资渠道替代对银行收益的条件性影响",
    "chain": [
      "真实替代银行可做贷款",
      "传统信贷净收益承压",
      "证券投资及服务费等补偿决定总利润方向"
    ],
    "argument_refs": [
      "AR08"
    ],
    "claim_refs": [
      "C085",
      "C086",
      "C087",
      "MC01",
      "MC02",
      "MC03"
    ],
    "expression_level": "model_reconstruction_of_creator_direction",
    "scope": "必须控制总量、利差、信用损失和非息收入",
    "limitations": "占比下降本身不足以触发第二步，更不足以保证总利润下降。"
  },
  {
    "mechanism_id": "ME03",
    "status": "candidate",
    "name": "债务再融资的负担与分类效应",
    "chain": [
      "债务换券或展期降息",
      "融资统计分类及偿付时间分布改变",
      "现金流压力可能缓释而本金与风险未必消失"
    ],
    "argument_refs": [
      "AR04"
    ],
    "claim_refs": [
      "C045",
      "C050",
      "C051",
      "C053",
      "C054"
    ],
    "expression_level": "model_qualified_candidate",
    "scope": "同本金、期限和债权主体可识别的重组",
    "limitations": "不是认可闭门谈判穷尽全部政策，也不推出隐债基本解决。"
  }
]
```

只建3个Candidate；美元损失厌恶类比和运河信用信号保留在Argument，未急于升级成通用机制。

## 13. THESES


```json
[
  {
    "thesis_id": "TH01",
    "statement": "中国融资结构正走向渠道多元和投向重配，但产业转型成果尚不能仅由融资份额证明。",
    "creator_claim": "C081 / C107",
    "status": "candidate_with_model_scope_qualification",
    "resolution": "new_provisional",
    "argument_refs": [
      "AR09",
      "AR10"
    ],
    "claim_refs": [
      "C029",
      "C030",
      "C076",
      "C078",
      "C091",
      "C092",
      "C102",
      "C107"
    ],
    "support_needed": "同口径长期融资和实体产出序列",
    "falsification": "构成变化仅来自债务重分类或短期行政因素且缺持续投向变化",
    "registry_search": {
      "searched": [
        "golden_report.md",
        "workspace file inventory"
      ],
      "found": "只有Golden #001摘要，无正式Thesis registry或完整对象",
      "decision_scope": "不能声称全库无同题Thesis；临时new/related，待注册表核对"
    },
    "traceability": [
      {
        "argument_id": "AR09",
        "claim_id": "C091",
        "source_segment": "SS-C091",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR09",
        "claim_id": "C092",
        "source_segment": "SS-C092",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR09",
        "claim_id": "C107",
        "source_segment": "SS-C107",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR10",
        "claim_id": "C102",
        "source_segment": "SS-C102",
        "source_id": "SRC03"
      }
    ]
  },
  {
    "thesis_id": "TH02",
    "statement": "9527判断融资转型将长期压迫传统银行业务，促使利润来源转型。",
    "creator_claim": "C085 / C088",
    "status": "creator_thesis_unverified",
    "resolution": "new_provisional",
    "argument_refs": [
      "AR08"
    ],
    "claim_refs": [
      "C029",
      "C030",
      "C078",
      "C085",
      "C086",
      "C087",
      "C088"
    ],
    "support_needed": "银行分业务收益、资产规模、成本与监管序列",
    "falsification": "直接融资比重上升期间传统业务绝对利润持续增加或业务转型并无收益改善",
    "registry_search": {
      "searched": [
        "golden_report.md",
        "workspace file inventory"
      ],
      "found": "只有Golden #001摘要，无正式Thesis registry或完整对象",
      "decision_scope": "不能声称全库无同题Thesis；临时new/related，待注册表核对"
    },
    "traceability": [
      {
        "argument_id": "AR08",
        "claim_id": "C029",
        "source_segment": "SS-C029",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR08",
        "claim_id": "C030",
        "source_segment": "SS-C030",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR08",
        "claim_id": "C078",
        "source_segment": "SS-C078",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR08",
        "claim_id": "C085",
        "source_segment": "SS-C085",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR08",
        "claim_id": "C086",
        "source_segment": "SS-C086",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR08",
        "claim_id": "C087",
        "source_segment": "SS-C087",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR08",
        "claim_id": "C088",
        "source_segment": "SS-C088",
        "source_id": "SRC03"
      }
    ]
  },
  {
    "thesis_id": "TH03",
    "statement": "9527把国内融资变化理解为人民币风险资本挑战美国传统优势。",
    "creator_claim": "C115",
    "status": "high_inferential_distance_unverified",
    "resolution": "new_provisional_related_to_GS001_capital_competition_theme",
    "argument_refs": [
      "AR10",
      "AR11",
      "AR12"
    ],
    "claim_refs": [
      "C102",
      "C104",
      "C106",
      "C108",
      "C113",
      "C114",
      "C115",
      "MC05",
      "MC06"
    ],
    "support_needed": "分币种/阶段可比募投退、创新产出和跨境投资数据",
    "falsification": "剔除政府债后早期股权资本并未增加，或相对美国差距未改善",
    "registry_search": {
      "searched": [
        "golden_report.md",
        "workspace file inventory"
      ],
      "found": "只有Golden #001摘要，无正式Thesis registry或完整对象",
      "decision_scope": "不能声称全库无同题Thesis；临时new/related，待注册表核对"
    },
    "traceability": [
      {
        "argument_id": "AR10",
        "claim_id": "C102",
        "source_segment": "SS-C102",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR10",
        "claim_id": "C104",
        "source_segment": "SS-C104",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR10",
        "claim_id": "C106",
        "source_segment": "SS-C106",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR11",
        "claim_id": "C102",
        "source_segment": "SS-C102",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR11",
        "claim_id": "C104",
        "source_segment": "SS-C104",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR11",
        "claim_id": "C106",
        "source_segment": "SS-C106",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR11",
        "claim_id": "C108",
        "source_segment": "SS-C108",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR11",
        "claim_id": "C114",
        "source_segment": "SS-C114",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR11",
        "claim_id": "C115",
        "source_segment": "SS-C115",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR11",
        "claim_id": "MC05",
        "source_segment": "SS-MC05",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR11",
        "claim_id": "MC06",
        "source_segment": "SS-MC06",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR12",
        "claim_id": "C108",
        "source_segment": "SS-C108",
        "source_id": "SRC03"
      },
      {
        "argument_id": "AR12",
        "claim_id": "C113",
        "source_segment": "SS-C113",
        "source_id": "SRC03"
      }
    ]
  }
]
```

注册表检索范围仅限当前工作区与Golden #001摘要。上期的安全资产、AI等主题不等同本期融资结构；资本竞争主题仅related，不能虚构其Thesis ID。

## 14. FORECASTS


```json
[
  {
    "forecast_id": "FC01",
    "claim_id": "C011",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:02:04,640"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "US_tightening_duration",
    "direction": "longer",
    "prediction_window": "unknown",
    "conditions": "if tightening persists unexpectedly",
    "modal_strength": "possible",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "如果；可能",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "需先约定本轮起点及很长的期限阈值",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C011",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC02",
    "claim_id": "C015",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:02:40,680"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "USD_credit",
    "direction": "deteriorate_first",
    "prediction_window": "unknown",
    "conditions": "暴力加息",
    "modal_strength": "possible",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "可能最先",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "需美元信用指标及先于哪些变量的比较规则",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C015",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC03",
    "claim_id": "C018",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:04:04,740"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "US_policy_strategy",
    "direction": "short_run_gains",
    "prediction_window": "unknown",
    "conditions": "短期收益先于副作用且替代资产受限",
    "modal_strength": "possible",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "是不是可能选择",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "需政策目的与因果识别；不能仅凭短期市场涨跌",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C018",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC04",
    "claim_id": "C020",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:05:21,290"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "US_debt_growth",
    "direction": "accelerate",
    "prediction_window": "unknown",
    "conditions": "加息并扩表",
    "modal_strength": "likely",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "会",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "需债务口径、基准增速与政策贡献分解",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C020",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC05",
    "claim_id": "C021",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:05:29,800"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "Treasury_holder_tolerance",
    "direction": "increase",
    "prediction_window": "unknown",
    "conditions": "持仓巨大且替代选择有限",
    "modal_strength": "possible",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "会不会；可能",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "需持仓行为、风险溢价及态度证据",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C021",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC06",
    "claim_id": "C026",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:07:30,750"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "Federal_Reserve_strategy",
    "direction": "exploit_loss_aversion",
    "prediction_window": "unknown",
    "conditions": "历史类比机制可迁移",
    "modal_strength": "possible",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "可不可能",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "未指定行为与意图判据，不能把任何结果都解释为命中",
      "accepted_for_scoring": false
    },
    "resolvability": "unresolvable",
    "source_segment": "SS-C026",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC07",
    "claim_id": "C063",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:20:37,340"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "Pinglu_Canal_payback",
    "direction": "long",
    "prediction_window": "运营后约30—40年；运营起点未给",
    "conditions": "乐观估计，考虑爬坡",
    "modal_strength": "possible",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "乐观估计；难得回本",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "明确运营现金流、社会效益、补贴、折现和回本定义",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C063",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC08",
    "claim_id": "C082",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:27:00,960"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "direct_financing_share",
    "direction": "increase",
    "prediction_window": "unknown",
    "conditions": "结构趋势延续",
    "modal_strength": "near_certain",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "肯定还会",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "可观察份额方向；但必须先补窗口与统计口径",
      "accepted_for_scoring": false
    },
    "resolvability": "medium",
    "source_segment": "SS-C082",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC09",
    "claim_id": "C085",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:27:23,950"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "bank_profitability",
    "direction": "decrease",
    "prediction_window": "unknown",
    "conditions": "趋势持续且不开展替代业务",
    "modal_strength": "likely",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "还会继续；除非",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "先选ROA/ROE等盈利能力指标；不得改用利润规模代替",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C085",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC10",
    "claim_id": "C086",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:27:46,840"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "traditional_bank_business",
    "direction": "shrink",
    "prediction_window": "unknown",
    "conditions": "缺少转型",
    "modal_strength": "near_certain",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "非常非常确定",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "先区分份额、资产绝对额及收益；规定窗口",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C086",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC11",
    "claim_id": "C087",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:27:56,770"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "bank_aggregate_profit",
    "direction": "decrease",
    "prediction_window": "unknown",
    "conditions": "按上下文缺少转型",
    "modal_strength": "likely",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "会",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "定义银行样本和净利润绝对额，锁定起止年",
      "accepted_for_scoring": false
    },
    "resolvability": "medium",
    "source_segment": "SS-C087",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC12",
    "claim_id": "C088",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:28:15,120"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "bank_nontraditional_income",
    "direction": "become_profit_source",
    "prediction_window": "十年级；非明确截至2036承诺",
    "conditions": "合规开展新业务",
    "modal_strength": "near_certain",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "肯定；大趋势",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "先区分表外、非标、手续费及投资收益",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C088",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC13",
    "claim_id": "C090",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:28:44,930"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "employee_internal_status",
    "direction": "increase",
    "prediction_window": "unknown",
    "conditions": "创造额外利润",
    "modal_strength": "likely",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "谁能；谁就",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "样本、地位指标和组织制度需补充",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C090",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC14",
    "claim_id": "C100",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:30:07,610"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "supported_sector_growth",
    "direction": "more_opportunity",
    "prediction_window": "unknown",
    "conditions": "金融供给充分",
    "modal_strength": "plausible",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "很有想象空间；更有条件",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "先定义成长或机会指标；不得自行替换为股票回报",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C100",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC15",
    "claim_id": "C118",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:24:57,460"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "sovereign_borrowing_capacity",
    "direction": "increase",
    "prediction_window": "unknown",
    "conditions": "直接融资风险不回到银行/财政（后者为模型条件）",
    "modal_strength": "likely",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "打开很好的空间",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "需财政担保风险、债务容量和借款成本指标",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C118",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC16",
    "claim_id": "C119",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:28:51,070"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "employee_promotion_speed",
    "direction": "increase",
    "prediction_window": "unknown",
    "conditions": "创造额外利润",
    "modal_strength": "likely",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "就会加快",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "需可比样本及晋升时长",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C119",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  },
  {
    "forecast_id": "FC17",
    "claim_id": "C120",
    "made_at": {
      "recorded_at": null,
      "publication_proxy": "2026-09-21T10:32:21+08:00",
      "source_offset": "00:28:52,050"
    },
    "knowledge_cutoff": "2026-09-21T10:32:21+08:00",
    "target": "employee_resource_access",
    "direction": "improve",
    "prediction_window": "unknown",
    "conditions": "创造额外利润",
    "modal_strength": "likely",
    "modal_mapping": "model coding of original certainty; not numerical probability",
    "original_modality": "也会",
    "resolution_criteria": {
      "creator_specified": null,
      "model_proposed_for_future_review": "需资源调配指标及组织范围",
      "accepted_for_scoring": false
    },
    "resolvability": "low",
    "source_segment": "SS-C120",
    "evaluation_status": "not_resolved",
    "post_cutoff_evaluation": null
  }
]
```

C083的直接融资2/3是规范主张，未当成时间明确的预测。made_at用发布proxy并保留录制时间null。所有resolution_criteria均区分主播未给与模型建议，尚不可评分。

## 15. CONTRADICTIONS

none。没有满足“长期张力＋多事件＋多Thesis＋双方目标约束持续互动”的证据；中美、银行/资本市场和中央/地方不是自动Contradiction。

局部命题冲突检查另列，不混同结构性Contradiction：


```json
[
  {
    "id": "CF01",
    "claims": [
      "C073",
      "C094"
    ],
    "same_proposition": "unknown: absolute scale versus unclear scale",
    "same_reference_time": "unknown",
    "same_population": "likely_same",
    "same_scope": "unknown",
    "logically_incompatible": "only_if_same_metric_and_period",
    "relation": "UNRESOLVED_SCOPE",
    "decision": "no_CONTRADICTS"
  },
  {
    "id": "CF02",
    "claims": [
      "C057"
    ],
    "related_evidence": {
      "source_id": "SRC03",
      "cue_start": 420,
      "cue_end": 426,
      "start": "00:19:27,730",
      "end": "00:19:43,940",
      "raw_text": "最近一段时间我经常看到啊危言耸听的说。隐形债问题如何如何要爆发？我记得2023年的时候。当时的时候，美国那些金融机构，不就是说中国的债务问题要大爆发吗？中国政府要破产吗？对吧。现在2026年了，这个问题是不是已经没人提了，而且。",
      "alignment": "ASR cue boundary; not audio-verified"
    },
    "same_proposition": "related",
    "same_reference_time": "unclear",
    "same_population": "unknown: 最近评论者可能不同于2023美国机构",
    "same_scope": "unknown",
    "logically_incompatible": "not_established",
    "relation": "POSSIBLE_POPULATION_DIVERGENCE",
    "decision": "no_CONTRADICTS"
  },
  {
    "id": "CF03",
    "claims": [
      "C055"
    ],
    "source": "SRC12",
    "same_proposition": false,
    "same_reference_time": false,
    "same_population": "partly",
    "same_scope": "unknown",
    "logically_incompatible": false,
    "relation": "DIFFERS_BY_SCOPE_AND_TIME",
    "decision": "2025政策计划不能直接反证2026完成，但也不能证明完成"
  },
  {
    "id": "CF04",
    "claims": [
      "C001"
    ],
    "source": "SRC06",
    "same_proposition": "publication_variant_unknown",
    "same_reference_time": "unknown",
    "same_population": true,
    "same_scope": "print/online/written_unclear",
    "logically_incompatible": "not_established",
    "relation": "SOURCE_DATE_REVIEW",
    "decision": "不先定speaker_slip或CONTRADICTS"
  }
]
```

## 16. CANDIDATE HEURISTICS


```json
[
  {
    "heuristic_id": "HC01",
    "status": "candidate_only",
    "rule": "观察融资流量与存量结构来识别变化方向及潜在空间，再追问资金流向。",
    "observed_in_arguments": [
      "AR06",
      "AR08",
      "AR09"
    ],
    "source_segments": [
      "SS-C067",
      "SS-C068",
      "SS-C078",
      "SS-C099"
    ],
    "direct_method_evidence": {
      "source_id": "SRC03",
      "cue_start": 533,
      "cue_end": 533,
      "start": "00:25:20,060",
      "end": "00:25:40,060",
      "raw_text": "啊，这是积极的变化。其次呢是从存量来看呢，增量看趋势，存量看空间，存量看潜力，对吧？从存量看呢，直接融资占比稳步升至3分之1左右，就是未来的成长空间还有很大呢啊，把这个话给你翻译翻译。在20世纪90年代建设现代金融市。",
      "alignment": "ASR cue boundary; not audio-verified"
    },
    "why_method_not_conclusion": "主播明确说增量看趋势、存量看空间，并在多处把投向作为观察方法；可以迁移到其他行业。",
    "limits": "份额空间不代表均衡目标；流量比值不能当价格证据；仅本期无法确认长期稳定性。"
  },
  {
    "heuristic_id": "HC02",
    "status": "candidate_only",
    "rule": "对看似简单的债务处置结果，追问确权、利益相关者谈判与过程成本。",
    "observed_in_arguments": [
      "AR04"
    ],
    "source_segments": [
      "SS-C050",
      "SS-C051",
      "SS-C052"
    ],
    "why_method_not_conclusion": "关注解释中遗漏的执行过程是一种可跨政策复用的检查规则，不等于本期全部化债都靠谈判的判断。",
    "limits": "需要多期复现；方法有用不能替代具体案件证据。"
  }
]
```

## 17. REVIEW QUEUE

### Critical

| ID | 类别 | Claims | 问题 | 完成条件 |
| --- | --- | --- | --- | --- |
| RQ01 | Data | ["C080","C078","C079"] | 股票10%不由三分之一减30%推出。 | 听验26:46—26:54；确认同分母、分类和原统计表。模型3.3仅是算术诊断，不替换主播数字。 |
| RQ02 | Data | ["C031","C040","C041"] | 间接融资与贷款、流量与存量在论证中换用。 | 统一2013前与2025年分子分母后重算；不以增量排名推存量退居次席。 |
| RQ03 | Data | ["C073","C094"] | 占比下降且绝对量增加，与后文整体规模下降不一致。 | 听验25:00—25:20及31:24—31:27，确认同时间同口径；未完成前不建CONTRADICTS。 |
| RQ04 | Reasoning | ["C054","C055"] | 从重分类和谈判推到隐债基本解决。 | 补截至截止时间的隐债余额、期限、付息、拖欠、现金流及财政约束；先锁定基本解决判据。 |
| RQ05 | Reasoning | ["C067","C068","C070"] | 融资数量比被当成相对融资价格。 | 匹配同主体、期限、担保和费用的贷款/债券成本；排除分母收缩及发行结构。 |
| RQ06 | Reasoning | ["C085","C086","C087","MC01","MC02","MC03"] | 贷款份额变化跳到银行绝对盈利下降。 | 分解生息资产、净息差、信用成本、证券收益及手续费收入；验证替代而非新增互补。 |
| RQ07 | Reasoning | ["C106","C114","C115","MC05","MC06"] | 社融直接融资跳到人民币早期资本与中美竞争。 | 增加分币种、投资阶段、跨国可比募投退和创新产出序列；不可用政府债增长代替创投。 |

### High

| ID | 类别 | Claims | 问题 | 完成条件 |
| --- | --- | --- | --- | --- |
| RQ08 | ASR | ["C001","C005","C060","C024"] | 人名、刊物、运河及闪击波兰等专名。 | 按TC01—TC15回听；规范实体可先建立，ASR归因仍待确认。 |
| RQ09 | Source | ["C001","C116"] | 9月13口述、URL路径9月15、网页9月16存在三种时间。 | 回听开场并核纸刊、网站首次发布及修订记录；分别记录写作、印刷、上线时间。 |
| RQ10 | ASR | ["C047","C048","C050","C121","C122"] | 4%、5%、2%以下、20%、2%点几混杂。 | 回听15:15—16:22；每项绑定发行人、币种、期限和日期；不要据相邻句自动纠错。 |
| RQ11 | ASR | ["C062","C063"] | 134年可能是十三四年，30—40年另为粗估预测。 | 回听20:33及20:59；区分静态社会收益比和财务回收期。 |
| RQ12 | ASR | ["C068"] | 重复读数出现百分之百2020年上半年。 | 回听23:38—23:43；首读2026H1近20%保留，重复句记录redundant occurrence。 |
| RQ13 | ASR | ["C111","C112"] | 美元人民币金额转写损坏且混主观负担。 | 回听33:19—33:59；换算数值保持null，不凭常识补数。 |
| RQ14 | Data | ["C091","C092","C098"] | 新增贷款在全部贷款中分母歧义；领域可能交叉。 | 获取统计表、基期和去重规则；60/10/70不能直接相加。 |
| RQ15 | Data | ["C037","C038","C039"] | 35.6万亿、47%及首次仅匹配文章，未独立复算原始年表。 | 查截至知识截止时间可获得的央行2025年数据及修订版本。 |
| RQ16 | Data | ["C067","C068"] | 企业债/同期贷款比值的分母定义及全年对半年比较。 | 确认企业贷款还是全部贷款、净融资还是发行量；同比较期间。 |
| RQ17 | Data | ["C074","C076","C077","C078","C079"] | 存量占比四舍五入且间接项不全是贷款。 | 取得1990年代回溯及2026年6月存量分类；不强制近似值相加为100。 |
| RQ18 | Data | ["C060","C061","C063"] | 投资预算、年度运输节约、社会效益与项目回款混用。 | 核预算/决算、目标年、运量爬坡及收入归属；不把收益预测当实现值。 |
| RQ19 | Ontology | ["C032","C033"] | 股票被当债券/借条。 | 听验10:31—10:37；债权和股权单独分类，不在Normalized层修成正确金融常识。 |
| RQ20 | Ontology | ["C049","C048","C053"] | 熊猫债、中央国债、地方专项债和协商展期混用。 | 核发行人及债权债务主体；对照财政部法定额度，不以一事一议替代发债制度。 |
| RQ21 | Ontology | ["C071","C072","C118","MC04"] | 直接融资、银行风险与国家信用空间被当单一路径。 | 确认持债机构、显性/隐性担保、财政兜底与资本占用。 |
| RQ22 | Ontology | ["C088","C103","C104","C105"] | 非标、表外、天使投资、银行非传统业务并列混称。 | 拆金融工具、会计位置、风险承担主体及业务牌照；不把表外都视为高利润业务。 |
| RQ23 | Source | ["C024","C025","C022"] | 二战时序、谈判地点和反苏动机混杂。 | 先听验，再用确切早于截止时间的历史文献区分1938慕尼黑和1939波兰战争。 |
| RQ24 | Data | ["C012","C014"] | 20%加息与利息超过GDP缺指标和模型。 | 核利率种类、路径、债务总额、有效付息率与名义GDP；假设不得变现状。 |
| RQ25 | Data | ["C019","C020"] | 美联储扩表与美国财政债务膨胀混为一谈。 | 取截止前资产负债表序列和财政发行数据，分别核验存量、变化及因果。 |
| RQ26 | Source | ["C003"] | 日央行已宣布加息但生效日9月24在截止之后。 | 按9月18文件记录announced；不得用今天首页的已生效状态倒填。 |
| RQ27 | Forecast | ["C011","C015","C018","C020","C021","C026","C063","C082","C085","C086","C087","C088","C090","C100","C118","C119","C120"] | 大部分预测没有时间窗口、对象或阈值；职业结果亦条件不全。 | 按Forecast逐项补可接受判据；模型提案未经确认不可拿来评分。 |

### Medium

| ID | 类别 | Claims | 问题 | 完成条件 |
| --- | --- | --- | --- | --- |
| RQ28 | ForecastLineage | ["C008","C058","C056"] | 此前讲过/金融机构曾预测均无历史来源。 | 定位历史SourceSegment；只保留retrospective claim，不回造成功历史预测。 |
| RQ29 | Quantifier | ["C010","C023","C028","C052","C053","C057","C075","C103","C105","C110"] | 大家、全部、完全、只能等范围不明确或过强。 | 按主体和时点补样本；只支持方向时标core_claim_supported而非整句verified。 |
| RQ30 | Data | ["C042"] | 社融负增长与剪刀差所指指标unknown。 | 听验13:16—13:28，并核月增量、同比、余额及M1/M2是否真被说出。 |
| RQ31 | Data | ["C093","C095","C096","C097"] | 贷款增速基期、年均算法和分类口径未知。 | 取得统计原表；各类别独立检验，不用一个相近数字覆盖全部。 |
| RQ32 | Data | ["C064","C124","C125"] | 运河水深水宽及西江/钦江水量说法未核。 | 设计断面和水文资料核验，区分航道深度与开挖深度。 |
| RQ33 | Reasoning | ["C059","C065"] | 工程推进到公信力、再到化债有效性有代理变量跳跃。 | 补债权人行为和偿债现金流；项目能建不能代替政府财务可持续性。 |
| RQ34 | Reasoning | ["C005","C017","C022","C028","C043"] | 对央行、美国、英法的动机归因缺一手行为证据。 | 保留观察者归因，不升级为对象的客观动机。 |
| RQ35 | Source | ["C117","C036"] | 2013第二次危机事件不明确。 | 回听并定位具体事件，不自动新建模糊金融危机Event。 |
| RQ36 | Ontology | ["C083"] | 三分之二是合理状态还是确定预测？ | 暂按normative，不赋Forecast目标；须音频语气或后续说明才改变。 |
| RQ37 | Ontology | [] | 缺全量既有Thesis注册表。 | 取得注册表后重做same/update/related/new；当前new均为临时本地决定。 |
| RQ38 | EvidenceIntegrity | [] | 731个SRT cue中有多处20秒长段；TXT/SRT很可能同次ASR。 | 音频定位后细化边界；转写一致不能当两份独立证据。 |
| RQ41 | Source | ["C123"] | 多数隐债经手人受处分的样本不明确。 | 案件级资料核对；不将主播概括当事实比例。 |

### Low

| ID | 类别 | Claims | 问题 | 完成条件 |
| --- | --- | --- | --- | --- |
| RQ39 | Method | ["C099"] | 一集只能支持方法候选，不能证明稳定有效。 | 在未来30期统计方法复现、成功/失败及适用边界。 |
| RQ40 | Source | [] | 外部网页为当前检索版本，缺截止日前网页快照和完整原数据表。 | 保留引用日期及检索日志，后续补历史版本；不把本次检索日当源首发。 |

## 18. SCHEMA / ONTOLOGY / EXTRACTION ISSUES FOUND

| ID | 不足 | 建议 | 本次显式处理 |
| --- | --- | --- | --- |
| SC01 | 需将“何时说”与“何时公开”及视频偏移分开 | asserted_at.recorded_at允许null；published_at作为proxy；media_offset单列。 | structured asserted_at |
| SC02 | 政策宣布、实施、可知时间并不相同 | Event增加announced_at/effective_at；未来生效但已公布不是事后污染。 | effective_at |
| SC03 | Official quote matched 与 underlying proposition verified不同 | 分开source_fidelity/measurement_veracity；官方因果解释仍待验证。 | external_quote_match + independent Assessment |
| SC04 | 一条金融观测必须标流量、存量、增速、比值分母和时间窗 | 增加numerator/denominator、gross_net、period_basis、vintage及classification_version；无法确定即null。 | Indicator.definition + value_kind |
| SC05 | 预测的预期运输收益不能放进实现值观测 | Observation增加observed/projected/calculated/reported类型；社会成本节约与项目收入建不同Indicator。 | value_kind；OB20隔离 |
| SC06 | ASR不确定、口误、概念错误和算术错误不能用一个corrected标志表达 | correction_status、acoustic_confidence、semantic_confidence、speaker_slip_confirmation分别记录。 | 候选纠错applied=false；无speaker_slip_confirmed |
| SC07 | claimant、读出者、被转述观点和评价观察者不相同 | 增加asserted_by、attributed_to及归因链；SRC03证明9527说过不证明潘功胜作此判断。 | claimant + asserted_by + attribution |
| SC08 | Structural Process缺少正式对象但又不应强塞Event | 建议新增StructuralProcess/TrendObservation；本期暂不私自实例化，只在Thesis承载解释。 | none; schema proposal only |
| SC09 | Reasoning hop_count受拆分粒度影响，分支边数不等于最长路径 | 分别存edge_count、longest_path、explicit_shortcuts和model_bridge_count。 | hop_definition + distance_audit |
| SC10 | 非历史类比、比喻和当期案例信号没有合适argument_type | 开放case_based_signal_inference、mixed_statistical_and_analogy；只AR03为historical_analogy。 | AR05/AR09类型显式候选扩展 |
| SC11 | quantifier不能承担所有确定性与排他性 | 保存raw_quantifier和modal_strength；量词过强独立于核心方向是否有支持。 | certainty_expressed + VA reason + Forecast modality |
| SC12 | 模型提出的预测判据不可倒灌成主播承诺 | creator_criteria与proposed_criteria分开，未授权不评分。 | resolution_criteria.accepted_for_scoring=false |
| SC13 | 来源非独立：TXT/SRT同源、财联社/求是为转载链 | source_family、derived_from和证据独立性；不能凭四个Source计四次支持。 | source_family + independent_evidence |
| SC14 | 重复朗读的数字错误不能生成多个同权Claim | ClaimOccurrence持有每次原文及局部信息增量，唯一命题挂多个occurrence。 | claim_occurrences |
| SC15 | 强冲突关系与长期结构性Contradiction是两个层次 | claim_relation单独记录候选张力；五同条件未满足不建CONTRADICTS；结构矛盾更需多事件多Thesis。 | conflict_checks，不建立Contradiction |
| SC16 | 规范目标比例与趋势预测在一句中并存 | C082为预测、C083为规范主张；不把2/3当官方或主播承诺目标。 | atomicity separated |
| SC17 | 推理边关系尚无提供的正式Relation registry | 使用显式候选INFERENTIAL_SUPPORT_CANDIDATE而不宣称已是正式关系；正式入库前映射。 | candidate relation namespace |

## 19. GOLDEN SAMPLE SUMMARY


```json
{
  "creator_claim_count": 125,
  "model_reconstruction_claim_count": 6,
  "claim_count": 131,
  "argument_count": 12,
  "mechanism_count": 3,
  "thesis_count": 3,
  "forecast_count": 17,
  "contradiction_count": 0,
  "heuristic_count": 2,
  "review_queue_count": 41,
  "review_by_priority": {
    "Critical": 7,
    "High": 20,
    "Medium": 12,
    "Low": 2
  },
  "semantic_segments": 17,
  "sources": 19,
  "source_cues": 731,
  "assessment_count": 131,
  "veracity_counts": {
    "uncertain": 86,
    "verified": 2,
    "likely_true": 24,
    "unverifiable": 14,
    "likely_false": 4,
    "disputed": 1
  }
}
```

本次完成的是可审计抽取包，不是消除全部不确定性的最终认证。Traceability链已结构化；音频真值和数据底表仍须通过Review闭环。

## 额外六个问题

### A. 本期最核心的3—5条Argument Chain

- AR04：官方所述债券/贷款分类变化 → 9527加入逐案谈判和展期 → 政府债务压力骤减 → 隐债基本解决。最后一步证据最弱。
- AR06/AR07：企业债/贷款增量比7%→近20% + 贷款被称为低成本 → 直接融资更便宜 → 国家信用占用减少 → 国家举债空间增大。价格推断与信用容量推断是两个不同的缺口。
- AR08：直接融资比重提高 → 真实替代银行贷款（模型条件） → 传统净收益承压（模型条件） → 缺补偿时总利润下降（模型条件） → 表外业务方向。主播说出了方向，但没有完整给出中间条件。
- AR09/AR10：贷款投向变化 → 9527按供血比喻识别机会 → 科技企业早期风险更适合天使资本 → 新旧动能转换落地。融资观察与产业结果不能合并。
- AR11/AR12：国内融资结构变化 → 人民币早期风险资本扩张（待证） → 与美国可比优势变化（待证） → 中国挑战美国。显式捷径和模型补出的四条桥接边分别保存。

### B. 事实数据 → 9527解释 → 9527结构性推论

- 数据层：C037/C038、C067/C068、C076—C079是文章报告的数据；本样本仅确认引述有出处，尚未独立复算底表，故多为likely_true而非verified。
- 解释层：C070把数量比解释为融资价格优势；C054把融资结构解释为化债压力下降；C099把投向解释为机会。均须单独核因果。
- 结构层：C055化债基本解决、C085—C088银行转型、C107产业转换、C115中美竞争地位变化。不能让前提数据的可信度自动传递到这些结论。
- “科技/绿色/养老”应分四层：政策重点（PL02）；文章报告的信贷流向（OB14—OB18等）；主播对未来机会的预测C100；实体转型解释C107。没有独立产业结果观测，因此不将最后一层写成事实。

### C. 哪些地方体现可复用分析方法

- 最直接的方法表达是25:20附近的“增量看趋势，存量看空间”，以及29:52后从资金流向寻找机会；HC01保存这种读数方法，同时记录本期把数量读成价格的失败风险。
- 16:22—18:26主动追问确权、谈判及过程成本，形成HC02。这是检查解释遗漏变量的方法，不能替代个案取证。
- 由本期不能证明“稳定”。必须在多期复现且记录失败样本后，才可讨论稳定性和有效性。

### D. 哪些观点绝不能进入Verified Knowledge

- C055隐债基本解决；C070直接融资一定更便宜；C072/C118腾出国家信用空间；C080股票约10%；C085—C088银行盈利与业务方向；C106早期非银行资本迅速扩张；C114/C115中美风险资本竞争。
- C005/C017/C022/C028/C043所有未经证实的动机归因；C014利息超过GDP；C061社会效益当现金回款；C062损坏回本年限；C111美元换算损坏数字。
- 全部Forecast保持待验证；MC01—MC06只是模型诊断条件，不是主播证据。

### E. V0.2仍难表达什么

- 至少需要SC01—SC17所列的时间、分母、数据版本、嵌套归因、预测观测、来源依赖、ClaimOccurrence、推理边与多路径距离等扩展。
- 金融结构变化首先是持续的Structural Process及指标序列，不是一次Event；关于其方向、原因和后果的解释才是Thesis；可迁移的局部因果机制才是Mechanism。V0.2缺StructuralProcess对象，本次不偷偷新增正式实体。
- 事实已宣布但未来生效（日本加息）与事后信息完全不同；必须按可知时间过滤，不按事件生效日期一刀切。

### F. 未来30期最值得复用的对象

- Indicator优先：社融流量/存量及债券、贷款、股权分项，企业债/贷款增量比，分行业贷款增速；新增银行分业务利润、人民币风险资本币种/阶段序列。先锁口径和vintage。
- Mechanism：ME01生命周期与融资适配、ME02替代与收益补偿、ME03债务分类/期限/成本变化；均为candidate，需跨案例检验。
- Thesis：TH01多元融资与投向重配、TH02银行收益结构转型；TH03竞争地位仅作为高推理距离待证假说。
- Heuristic Candidate：HC01、HC02；30期中统计复现、适用条件、反例及错误率，不预设最终validated。

## 附：复核入口

- 读数与原句：[逐Claim证据](G:/youhegaojian/golden_sample_test/golden_sample_002/evidence_segments.md)。
- 待听项目：[音频复核清单](G:/youhegaojian/golden_sample_test/golden_sample_002/audio_review.md)。
- 机器可读：[完整JSON](G:/youhegaojian/golden_sample_test/golden_sample_002/golden_sample_002.json)。
- 完整性结果：[validation.json](G:/youhegaojian/golden_sample_test/golden_sample_002/validation.json)。
- 原文件SHA256和检索依据：[sources.json](G:/youhegaojian/golden_sample_test/golden_sample_002/sources.json)。
