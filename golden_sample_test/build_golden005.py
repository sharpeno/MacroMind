import re,json,hashlib,collections
from pathlib import Path
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'golden_sample_005'; OUT.mkdir(exist_ok=True)
BASE=Path(r'G:\BilibiliDown.v6.41.release\download\有何高见9527')
SRT=next(BASE.glob('*七百四五期*.srt')); TXT=next(BASE.glob('*七百四五期*.自动转写.txt'))
PROMPT=Path(r'G:\youhegaojian\prompt\V0.3.1-minor.md')
CUT='2026-08-20T10:37:33+08:00'; NOW=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
AN='analyst_youhegaojian9527'; MO='model_gpt6'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,o):(OUT/n).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def cb(kind=None,period=None,base=None,delta=None,unit=None):return dict(comparison_type=kind,baseline_period=period,baseline_value=base,delta_value=delta,delta_unit=unit)
cues=[]
for b in re.split(r'\n\s*\n',SRT.read_text(encoding='utf-8-sig').strip()):
 l=b.splitlines()
 if l and l[0].isdigit():
  a,z=l[1].split(' --> ');cues.append(dict(cue_id=int(l[0]),start=a,end=z,raw_text='\n'.join(l[2:])))
assert len(cues)==639
def bd(a,b):return dict(cue_start=a,cue_end=b,start=cues[a-1]['start'],end=cues[b-1]['end'])
def raw(a,b):return '\n'.join(x['raw_text'] for x in cues[a-1:b])
sources=[]; versions=[]
def src(i,title,loc,role,pub=None,origin=None,read='body_read',elig='eligible_by_displayed_date'):
 s=dict(source_id=i,title=title,location=str(loc),role=role,published_at=pub,updated_at=None,captured_at=NOW,source_version_ref='V-'+i,read_status=read,origin_family_ids=origin or [i],creator_used_status='not_established',historical_information_set_eligible=elig=='eligible_by_displayed_date')
 if not str(loc).startswith('http') and Path(loc).exists():s['sha256']=sha(Path(loc))
 sources.append(s);versions.append(dict(source_version_id='V-'+i,source_id=i,published_at=pub,updated_at=None,retrieved_at=NOW,cutoff_status=elig,historical_snapshot_available=False,content_hash=s.get('sha256'),version_caveat='现在读取的版本；发布日期不等于已取得截止时存档' if str(loc).startswith('http') else '本地输入按SHA256固定'))
src('S01','自动转写文本',TXT,['creator_used','primary_corpus'],origin=['F9527'],elig='same_video_derivative')
src('S02','SRT时间锚',SRT,['creator_used','primary_corpus'],origin=['F9527'],elig='same_video_derivative')
src('P01','V0.3.1-minor / MA.1任务指令',PROMPT,['user_authorized_instruction'],elig='instruction_not_evidence')
src('SRC-A','朱雀三号遥二回收报道','https://www.cls.cn/detail/2457733',['user_supplied_reference','verification_source'],'2026-08-19T08:01:00+08:00',['FLANDSPACE'])
src('SRC-B','着陆腿与20次复用能力报道','https://www.cls.cn/detail/2458013',['user_supplied_reference','verification_source'],'2026-08-19T12:59:09+08:00',['FCCTV'])
src('SRC-C','Moderna盘前行情与试验报道','https://www.cls.cn/detail/2458597',['user_supplied_reference','verification_source'],'2026-08-19T19:50:00+08:00',['FMODERNA_MERCK','FMARKET_UNKNOWN'])
src('SRC-D','贝森特回购与OT类比报道','https://www.cls.cn/detail/2458977',['user_supplied_reference','verification_source'],'2026-08-20T08:42:00+08:00',['FTREASURY','FMARKET_COMMENT'])
src('SRC-E','Reuters空间文化专题（用户指定原URL）','https://www.reuters.com/investigates/special-report/space-exploration-china-culture/',['user_supplied_reference','unused_reference'],origin=['FREUTERS'],read='original_fetch_failed',elig='unknown_quarantined')
src('V01','国家航天局转载蓝箭任务通报','https://www.cnsa.gov.cn/n6758823/n6758838/c10768762/content.html',['verification_source','model_supplement'],'2026-08-19',['FLANDSPACE'])
src('V02','Moderna CEO试验公告','https://www.modernatx.com/ir-insights-phase-3-intesmeran',['verification_source','model_supplement'],'2026-08-19',['FMODERNA_MERCK'])
src('V03','美国财政部回购公告','https://home.treasury.gov/news/press-releases/sb0607',['verification_source','model_supplement'],'2026-08-19',['FTREASURY'])
src('V04','FCC 2026年1月Gen2授权公告','https://docs.fcc.gov/public/attachments/DOC-417881A1.pdf',['verification_source','model_supplement'],'2026-01-09',['FFCC'],read='search_full_announcement_return_read')
src('V05','FCC勘误中的卫星数量（只读搜索片段）','https://docs.fcc.gov/public/attachments/DOC-424235A1.pdf',['model_supplement','unused_reference'],origin=['FFCC','FSPACEX'],read='snippet_read_pdf_403',elig='unknown_quarantined')
src('V06','Reuters同题Investing转载','https://www.investing.com/news/world-news/in-china-rocket-launches-fuel-tourism-and-spaceage-dreams-4868434',['model_supplement','unused_reference'],origin=['FREUTERS'],elig='timezone_and_version_unknown_quarantined')
sources[-1].update(displayed_published_at='Aug 19, 2026, 07:02 PM',displayed_updated_at='Aug 19, 2026, 09:00 PM',display_timezone=None)
src('V07','Reuters Connect同题图片','https://www.reutersconnect.com/item/the-wider-image-in-china-rocket-launches-fuel-tourism-and-space-age-dreams/dGFnOnJldXRlcnMuY29tLDIwMjY6bmV3c21sX1JDMkhWTUFUREpMNQ',['model_supplement','unused_reference'],origin=['FREUTERS'],read='caption_and_metadata_read',elig='publication_unknown_photo_date_not_publication')
src('V08','TimesLIVE同题Reuters转载','https://www.timeslive.co.za/news/world/2026-08-20-in-china-rocket-launches-fuel-tourism-and-space-age-dreams/',['model_supplement','unused_reference'],origin=['FREUTERS'],read='search_return_read',elig='timezone_unknown_quarantined')
sources[-1]['displayed_published_at']='August 20, 2026 at 8:55 am; timezone not shown'
for n,p in [(1,ROOT/'golden_report.md'),(2,ROOT/'golden_sample_002/golden_sample_002.json'),(3,ROOT/'golden_sample_003/golden_sample_003.json'),(4,ROOT/'golden_sample_004/golden_sample_004.json')]:
 src(f'R0{n}',f'Golden #{n:03} 方法/Thesis目录',p,['method_registry_only'],read='summary_only' if n==1 else 'method_and_thesis_sections_read',elig='excluded_from_historical_evidence')
SM={s['source_id']:s for s in sources}
for s in sources[:2]:s.update(creator_used_status='primary_utterance_derivative',independence='same_ASR_origin_not_two_witnesses')
for s in sources:
 if s['source_id'] in ['SRC-A','SRC-B','SRC-C','SRC-D']:s['creator_used_status']='topic_overlap_only_exact_article_use_not_proven'
topics=[(1,27,'回收与技术追赶'),(28,78,'举国研发与公私互补'),(79,150,'航天话语权与远期文明情景'),(151,181,'太空算力及低成本跳跃'),(182,212,'存储机器人资本市场类比'),(213,248,'太空算力成本审查'),(249,290,'星链规模需求及融资约束'),(291,350,'国家投资产业链与竞争'),(351,363,'Moderna行情及AI流动性情景'),(364,399,'财政回购信用解释'),(400,438,'月球海南华尔街类比及融资竞争'),(439,481,'技术话语权汇率'),(482,513,'美债数字与美元根基'),(514,545,'上市时间自纠及发射失败舆论'),(546,600,'AI比较与药物盈利推断'),(601,639,'投资节奏人才财富预测')]
segments=[dict(segment_id=f'SEG{i:02}',source_id='S02',topic=t,**bd(a,b)) for i,(a,b,t) in enumerate(topics,1)]
claims=[]; ss=[]; occ=[]
def add(i,a,b,k,t,pop=None,q=None,certainty=None):
 cid=f'C{i:03}'; sid='SS-'+cid; seg=[s['segment_id'] for s in segments if s['cue_start']<=b and s['cue_end']>=a]
 ss.append(dict(source_segment_id=sid,source_id='S02',source_version_ref='V-S02',raw_text=raw(a,b),semantic_segment_refs=seg,**bd(a,b)))
 c=dict(claim_id=cid,segment_id=seg,claimant=AN,claimant_id=AN,statement=t,claim_type=k,derivation_type='explicit_transcript_normalized_no_fact_repair',temporal_mode='future' if k=='forecast' else 'conditional' if k=='conditional_claim' else 'unknown',asserted_at=None,asserted_at_basis='recorded_at_unknown',publication_proxy=CUT,reference_time=None,knowledge_cutoff=CUT,population=pop,quantifier=q,certainty_expressed=certainty,source_segment=sid,source_segment_refs=[sid],atomicity_group_id=f'AG-{a}',reasoner_id=AN,analysis_context='historical_reconstruction',comparison_basis=cb(),semantic_role=None,verified_knowledge_eligible=False)
 claims.append(c);occ.append(dict(occurrence_id=f'OC{len(occ)+1:03}',claim_id=cid,source_segment_ref=sid,information_gain='high',occurrence_type='initial'))
rows='''1|1|1|reported_claim|朱雀三号回收成功。
2|1|1|interpretation|中国花十年追上美国十年前的回收水平。
3|2|4|interpretation|SpaceX近十年没有明显跨越式技术进步。
4|3|4|inference|中国当前水平与美国主流相差不大，差距只是数据积累。
5|10|11|conditional_claim|如果中国保持当前进步速度，很快会超过美国。
6|16|21|inference|回收技术门槛是中国独立攻克，而非因为马斯克开源。
7|29|30|inference|此次成功验证了举国体制饱和式研发有效。
8|31|35|reported_claim|中国此前实现海上回收；具体方式转写为信往回舟。
9|36|48|interpretation|国家队承担风险更大的探索，商业航天跟进并重视商业价值，形成互补。
10|53|54|interpretation|中国公私协作方式可能比美国依赖SpaceX更可靠。
11|55|75|interpretation|蓝色起源等竞争者在规模化和可靠性方面缺乏明显进展。
12|86|89|interpretation|航天进展和2030年登月的重要意义之一是争取话语权。
13|96|111|hypothetical_assumption|人类未来可能走意识上传与虚拟化的向内发展路径。
14|112|127|hypothetical_assumption|人类未来可能走向太空并成为太空生命。
15|115|124|analogy|地球生命走向太空类似水生生命走上陆地。
16|131|150|interpretation|低成本把物资送入太空是向外发展的基础，可复用火箭是第一步。
17|135|139|conditional_claim|若建成太空电梯，运输成本还会下降。
18|140|145|hypothetical_assumption|太空发射站之后可开发月球行星，再进行星际远航。
19|151|156|reported_claim|SpaceX上市叙事结合了AI和太空算力。
20|159|161|interpretation|太空算力在散热方面没有优势。
21|161|161|interpretation|太空算力在运输成本方面没有优势。
22|162|165|interpretation|太空太阳能发电可能折损更小。
23|165|165|interpretation|太空发电的不稳定性更强。
24|167|173|interpretation|太空算力是借SpaceX独有运输优势包装的资本故事。
25|169|170|reported_claim|SpaceX运输成本为其他竞争者的十分之一。
26|174|175|inference|中国掌握回收技术后，已经也能非常低成本地把物资送入太空。
27|176|181|interpretation|中国入场削弱SpaceX太空算力故事的独特性。
28|184|185|reported_claim|长鑫已上市；实体名称需核验。
29|185|185|reported_claim|长江相关企业准备上市；主体和状态需核验。
30|188|202|reported_claim|宇树已上市；转写存在语速、语数等变体。
31|190|201|reported_claim|美国尚无相应已上市机器人题材企业。
32|194|196|reported_claim|特斯拉Model X产线用于擎天柱机器人生产。
33|197|202|interpretation|中国机器人企业上市高估值打破只有华尔街能够募资的叙事。
34|208|210|interpretation|回收技术突破打开巨大商业想象空间。
35|213|218|interpretation|SpaceX火星移民故事空间有限，因而转向太空算力。
36|221|223|interpretation|太空辐射使精密芯片较快损坏。
37|224|226|inference|芯片损坏较快会提高折旧或替换成本。
38|227|227|reported_claim|SpaceX把每克物质送入太空仍需大几百美元。
39|230|232|hypothetical_assumption|太空算力芯片可能一两年至三四年就损坏需要替换。
40|237|242|conditional_claim|地面扩大太阳能布局并综合使用多种能源可能成本更低。
41|243|244|reported_claim|中国已经通过转写所称六网升级实践综合能源方案。
42|246|248|interpretation|若不靠太空算力故事，SpaceX高估值缺乏支撑。
43|249|249|reported_claim|星链是SpaceX唯一现在赚钱的项目。
44|251|252|reported_claim|星链现有规模饱和，当前有20万颗卫星；保留原始数字待核。
45|254|258|reported_claim|主播转述马斯克第二阶段计划发射200万颗星链卫星。
46|259|260|conditional_claim|卫星数量增加十倍会使带宽增加十倍。
47|260|260|conditional_claim|卫星数量增加十倍会使网速增加十倍。
48|261|263|conditional_claim|规模扩大后成本可下降十倍。
49|264|265|conditional_claim|星链扩容循环完成后可完全替代地面光纤网络。
50|268|268|interpretation|星链必须先融资部署网络，才有更好服务和市场渗透。
51|268|269|reported_claim|军方曾持续支持星链从零到20万颗的建设。
52|269|269|reported_claim|星链服务曾用于俄乌战场并成为对乌克兰施压的工具。
53|269|270|interpretation|军方现有需求已经满足，缺乏为十倍扩容出钱的动力。
54|270|270|interpretation|马斯克找不到支持宏大扩容的更多财源。
55|270|274|conditional_claim|需求数量扩大带动供应链规模后，竞争壁垒会增强。
56|278|281|conditional_claim|若航天需求被激活，中国工业产能会转化为成本竞争优势。
57|282|290|interpretation|SpaceX没有利用十年窗口充分补齐需求与产业规模。
58|297|304|interpretation|中国月球及太空计划兼有需求和国家任务，可由国家投资拉动产业循环。
59|305|308|reported_claim|朱雀三号背后的企业准备在雄安建设航天产业链；主体转写蓝天航天。
60|311|316|forecast|国家投资与商业发射将强化中国火箭供应链。
61|315|318|forecast|形成成本优势后，中国将统合世界所有火箭发射需求。
62|319|323|reported_claim|主播转述马斯克称只有中国可以与美国竞争。
63|325|341|historical_analogy|借曹操刘备煮酒论英雄解释马斯克赞许中国时的居高临下。
64|344|348|forecast|国家投资和需求可能使中国航天产业链规模增长快于美国。
65|355|357|reported_claim|Moderna黑色素瘤治疗研究出现利好消息。
66|357|357|reported_claim|Moderna市值在消息后增加190%多；同句另称翻两倍。
67|354|358|interpretation|Moderna大涨体现AI创造的流动性充裕。
68|357|358|conditional_claim|若AI泡沫破裂，流动性和借债投资意愿会下降。
69|358|359|conditional_claim|流动性消失后，未来产业融资支持将不足。
70|359|363|interpretation|下行期可借国家信用发行国债，间接投资未来项目。
71|364|367|interpretation|美国长期国债表现糟糕说明长期信用破产。
72|371|376|reported_claim|贝森特采取短债换长债式操作；转写称QT及Operation Twist。
73|379|382|inference|回购说明美国长债正常发行已卖不掉、没人买，只能自己买。
74|384|387|conditional_claim|若人们不信任一国政府，长期信任需求会转移给更有能力的政府。
75|388|399|interpretation|国家未来规划加上回收技术突破，使中国投资故事比美国更吸引人。
76|401|401|historical_claim|海南开发曾吸引大量资金，后来烂尾。
77|401|404|historical_analogy|类比海南开发，如果中国登月后开发月球，也可吸引投资。
78|406|410|interpretation|让外国资本参与中国未来投资可缓解其对中国出口获利的不满。
79|413|419|historical_analogy|借华尔街吸纳世界财富的模式解释中国航天叙事的融资可能。
80|421|425|interpretation|金融和航天投资故事可以并存，中美投资也非必然非此即彼。
81|427|431|interpretation|同题材下信任越高融资成本越低，不信任则成本更高。
82|432|437|conditional_claim|成本压力可以迫使竞争方提升效率，效率落后者可能被淘汰。
83|443|453|conditional_claim|更多技术赶超案例可积累话语权并提高中国资产估值。
84|458|462|reported_claim|近几年美元持续贬值、人民币持续升值。
85|464|464|reported_claim|当前人民币兑美元报价为6点7几；报价口径未明。
86|465|465|interpretation|美元走弱导致日元被动升值。
87|466|467|forecast|人民币继续升至6.5问题不大。
88|470|472|retrospective_claim|主播称年初曾预测2026年人民币大概率强劲升值。
89|473|480|interpretation|中国技术突破削弱美国资源，资源不足推动特朗普受迫性失误。
90|482|482|reported_claim|美国官方债务已突破40万亿美元。
91|483|483|historical_claim|美国债务在2022年突破30万亿美元。
92|484|485|derived_claim|美国债务在四年内增加约10万亿美元。
93|486|490|reported_claim|主播称耶伦2023年国会听证预测到2028年美债达40万亿美元。
94|491|492|inference|当前美债达到40万亿比上述预测提前约一年半。
95|494|496|forecast|美债从40万亿增至50万亿美元绝对不需四年。
96|496|497|forecast|主播倾向美债2028年突破50万亿美元，一两年为所选分支。
97|499|507|inference|朱雀三号等技术追赶削弱支撑美元坚挺的根基。
98|514|517|reported_claim|SpaceX前段时间上市并带动市值大涨；主播自纠年初说法。
99|519|525|interpretation|资本市场要故事承接AI流动性，而竞争者使维持故事的成本上升。
100|529|532|reported_claim|前几天某火箭发射失败，引发网络嘲讽；型号转写长长试仪。
101|533|545|interpretation|中美发射失败舆论双重标准反映对中国威胁美国领先叙事的担心。
102|546|549|interpretation|美国可见的领先叙事只剩芯片和航天等少数领域。
103|550|553|interpretation|美国用AI高估值和融资规模作为技术领先的证明。
104|556|557|reported_claim|美国官方禁止中国AI模型；范围未知。
105|558|560|reported_claim|主播声称特朗普自己的公司通过特许经营出售中国模型访问权牟利。
106|561|561|interpretation|中美AI能力差距不大。
107|562|564|interpretation|中国AI具有显著成本优势但未反映在估值中。
108|566|567|interpretation|中国AI股票泡沫小于美国。
109|571|572|reported_claim|主播再次称Moderna单日涨三倍；涨幅与倍数口径不明。
110|575|577|inference|个性化黑色素瘤治疗听起来价格不便宜。
111|578|579|inference|治疗昂贵意味着企业盈利空间很小。
112|579|585|interpretation|单次治疗技术突破不足以支撑大幅上涨的市值，还需要后续技术完善。
113|589|592|reported_claim|主播将不能长期欺骗所有人的名言由里根自纠为林肯。
114|593|597|analogy|以欺骗不能长期持续类比资本泡沫不能长久维系。
115|601|608|forecast|国家会平衡未来产业投资节奏，避免估值暴涨让研究者转向炒股。
116|611|614|interpretation|官方航天待遇偏低暂时约束行业估值。
117|616|620|conditional_claim|成功商业公司带来关注并改善航天人才待遇，形成正循环。
118|623|625|forecast|年轻人进入这些新技术领域有可能赚到钱。
119|626|630|interpretation|过去航天难赚钱是因为话语权不在中国手中。
120|631|637|forecast|未来航天会创造大量财富，趋势在转写35年的时间内更明显。
121|634|635|forecast|未来航天将产生新富豪。
122|82|85|interpretation|产业竞争正在洗牌，尖端行业尤其猛烈。
123|540|542|interpretation|反复试验失败不可怕，最终会取得成功。'''
for l in rows.splitlines():
 n,a,b,k,t=l.split('|',4);add(int(n),int(a),int(b),k,t)
CM={c['claim_id']:c for c in claims}
def C(n):return f'C{n:03}'
def patch(n,**kw):CM[C(n)].update(kw)
for n in [1,8,28,29,30,32,41,43,44,45,51,52,59,65,66,72,84,85,90,98,100,104,105,109]:patch(n,temporal_mode='present_or_recent_report',reference_time='相对录制时间，精确日期unknown')
for n in [91,93,94,113,119]:patch(n,temporal_mode='past')
for n in [2,3,4,25,26,38,46,47,48,64,66,84,85,90,91,92,94,95,96,107,108,109,120]:patch(n,comparison_basis=cb('unspecified_comparison'))
patch(25,comparison_basis=cb('ratio_to_competitors',None,None,0.1,'ratio'),population='SpaceX vs unnamed competitors',semantic_role='operating_cost')
patch(38,population='SpaceX launch; orbit/payload unknown',semantic_role='operating_cost',comparison_basis=cb('cost_per_mass'),raw_value='一克/大几百美元',normalized_value=None)
patch(44,population='Starlink satellites; orbit/operational status unspecified',quantifier='20万',raw_value='20万颗',normalized_value=200000)
patch(45,population='Starlink claimed stage-two plan',quantifier='200万',attribution_chain=[AN,'Elon Musk (reported not original verified)'])
for n in [46,47,48]:patch(n,comparison_basis=cb('conditional_tenfold',None,None,10,'倍; cost direction ambiguous'),quantifier='10倍')
patch(66,comparison_basis=cb('market_cap_change',None,None,190,'percent_more_than'),raw_value='翻了两倍，190%多',semantic_role='valuation')
patch(109,comparison_basis=cb('unspecified_price_or_market_cap',None,None,None,'涨三倍'),semantic_role='valuation')
patch(92,comparison_basis=cb('absolute_change','2022',30,10,'USD trillion'),derivation_type='creator_arithmetic',reference_time={'start':'2022','end':'2026'})
patch(95,certainty_expressed='绝对不要4年',population='US federal debt; definition unstated')
patch(96,certainty_expressed='很有可能',reference_time='2028',population='US federal debt; definition unstated')
patch(87,certainty_expressed='问题不大',population='RMB/USD quote; onshore/offshore and fixing/spot unknown',reference_time='未来，未定截止日')
patch(64,certainty_expressed='很有可能/可能',population='China vs US aerospace supply chain scale')
patch(60,certainty_expressed='到时候…把闭环搞起来',semantic_role='capacity')
patch(61,certainty_expressed='所有/全部',quantifier='all',population='world rocket launch demand')
patch(118,certainty_expressed='有可能',population='进入新技术领域的年轻人')
patch(120,certainty_expressed='不信走着瞧；趋势越来越明显',raw_prediction_window='35年的时间',prediction_window_normalized=None)
patch(121,certainty_expressed='会有',population='航天领域')
patch(115,certainty_expressed='肯定/会有平衡',population='中国国家投资决策')
patch(88,temporal_mode='retrospective',reference_time='2026年初（被声称的预测时间）',original_forecast_source=None)
for n in [26,56]:patch(n,semantic_role='operating_cost')
for n in [54,70,75,78,79,81]:patch(n,semantic_role='funding')
for n in [33,42,83,98,103,107,108,112]:patch(n,semantic_role='valuation')
for n in [43,111,118,120]:patch(n,semantic_role='profit')
for n in [13,14,17,18,39,40,46,47,48,49,55,56,68,69,74,77,82,83,117]:patch(n,temporal_mode='hypothetical_or_conditional')
# External assertions remain separate from the creator's argument premises.
ext=[('X01','V01','官方转载蓝箭通报：8月19日07:35发射。','reported_claim','蓝箭航天','L12','2026-08-19T07:35:00+08:00'),('X02','V01','官方转载蓝箭通报：8月19日07:41一级陆地回收。','reported_claim','蓝箭航天','L12','2026-08-19T07:41:00+08:00'),('X03','SRC-B','央视报道所称20次复用能力的对象是着陆腿。','reported_claim','央视新闻（原采访者unknown）','L8',None),('X04','SRC-C','财联社报道Moderna盘前股价上涨超过80%。','reported_claim','财联社','L2','2026-08-19盘前'),('X05','V02','Moderna公告其与Merck合作的III期联合疗法取得积极主要结果。','reported_claim','Moderna','L120','2026-08-19'),('X06','V03','财政部宣布长期债流动性支持回购每次上限从20亿美元提高至至少40亿美元。','policy_announcement','US Treasury','L335','2026-08-19'),('X07','V03','回购调整计划9月9日生效，持续至11月4日。','reported_plan','US Treasury','L336','2026-09-09/2026-11-04'),('X08','V04','FCC一月授权Gen2总量15,000颗，授权不等于已在轨。','reported_claim','FCC','search full announcement','2026-01-09'),('X09','SRC-A','蓝箭称一级硬件复用可摊薄成本；报道没有给出本箭复飞后的实测单位成本。','reported_claim','蓝箭航天（经财联社）','L11',None),('X10','SRC-B','报道预期成本将降低到70%以上，降到与下降的口径存在歧义。','reported_claim','央视新闻（原受访者unknown）','L15',None)]
for cid,source,t,k,who,anchor,rt in ext:
 sid='SS-'+cid; ss.append(dict(source_segment_id=sid,source_id=source,source_version_ref='V-'+source,locator=anchor,raw_text=None,evidence_paraphrase=t,quotation_status='paraphrase_not_verbatim',snapshot_directory='source_snapshots'))
 claims.append(dict(claim_id=cid,segment_id=None,claimant=who,claimant_id=who,statement=t,claim_type=k,derivation_type='external_source_paraphrase',temporal_mode='planned' if cid=='X07' else 'reported',asserted_at=SM[source]['published_at'],reference_time=rt,knowledge_cutoff=CUT,population=None,quantifier=None,certainty_expressed=None,source_segment=sid,source_segment_refs=[sid],atomicity_group_id=cid,reasoner_id=who,analysis_context='verification_not_creator_reconstruction',comparison_basis=cb(),semantic_role=None,verified_knowledge_eligible=False))
CM.update({c['claim_id']:c for c in claims})
CM['X03'].update(population='朱雀三号着陆腿',value=20,value_status='claimed_capability_design_target_or_engineering_estimate_unresolved',demonstrated_reuse_count=None,semantic_role='technology')
CM['X04'].update(population='Moderna common stock premarket',semantic_role='valuation',comparison_basis=cb('premarket_price_change','previous_close',None,80,'percent_more_than'))
CM['X06'].update(semantic_role='policy_operation_limit',comparison_basis=cb('announced_limit_increase','prior_operation_limit',2,2,'USD billion_at_least'))
CM['X10'].update(value_status='media_projection_not_observed',comparison_basis=cb('lower_to_vs_lower_by_ambiguous',None,None,70,'percent'),semantic_role='operating_cost')
CM['X08'].update(value=15000,value_status='regulatory_authorization',population='Gen2 only')
SSM={s['source_segment_id']:s for s in ss}
def repeat(n,a,b,gain='redundant'):
 sid=f'SS-OC{len(occ)+1:03}';ss.append(dict(source_segment_id=sid,source_id='S02',source_version_ref='V-S02',raw_text=raw(a,b),**bd(a,b)));occ.append(dict(occurrence_id=f'OC{len(occ)+1:03}',claim_id=C(n),source_segment_ref=sid,information_gain=gain,occurrence_type='restatement'));CM[C(n)]['source_segment_refs'].append(sid)
for n,a,b,g in [(24,219,220,'redundant'),(30,197,202,'low'),(30,621,621,'redundant'),(44,266,269,'low'),(45,268,270,'low'),(27,524,528,'medium'),(3,213,218,'low'),(112,580,585,'low')]:repeat(n,a,b,g)
SSM={s['source_segment_id']:s for s in ss}
scenarios=[]
def scenario(ns,cond,result,admit=False,why='未明确选择分支或触发条件/时间难以结算'):
 scenarios.append(dict(scenario_id=f'SC{len(scenarios)+1:02}',claim_refs=[C(n) for n in ns],condition=cond,result=result,branch_probability=None,condition_endorsed=None,reasoner_id=AN,analysis_context='historical_reconstruction',forecast_admitted=admit,admission_reason=why,source_segment_refs=[CM[C(n)]['source_segment'] for n in ns]))
scenario([5],'保持中国当前进步速度','很快超过美国')
scenario([13],'意识上传及虚拟化可实现','向内发展；算力和能源成为约束')
scenario([14,17,18],'廉价入轨及太空电梯、太空站等相继可实现','向外拓展文明空间')
scenario([39],'特定太空芯片在辐射下快速损坏','一至数年替换；无指定任务、器件与轨道')
scenario([40],'地面能源规模扩张并综合利用','可比太空方案便宜')
scenario([46,47,48,49],'卫星部署与规模扩大十倍','带宽/网速增长及成本下降，替代光纤；四个子结论分Claim')
scenario([55,56],'需求足够大','供应链规模和成本竞争力提升')
scenario([60,61,64],'国家投资、需求和供应链形成闭环','规模增长及全球需求集中',True,'主播作出方向承诺；进入分支选择Forecast，低可结算性不能伪造精确条件')
scenario([68,69],'AI泡沫破裂','流动性和风险投资意愿下降；没有自动预测泡沫日期')
scenario([70,74],'私营项目低信心且信任国家信用','国债中介融资或信任跨国转移')
scenario([77],'中国登月后推出月球开发叙事','吸引投资；反问未提供概率或规模')
scenario([78,79,80],'世界资金可以参与中国未来项目','缓解出口不满；融资故事并存')
scenario([82],'竞争者融资成本增加','激发效率改进；竞争失败分支为淘汰')
scenario([83],'技术赶超案例持续增加','话语权及资产估值提高')
scenario([95,96],'债务增加10万亿的用时缩短为约两年','2028年突破50万亿',True,'很有可能明确选择两年分支；95与96是嵌套时间承诺而非两条独立成功证据')
scenario([115],'估值飙升可能分散研发人员注意力','国家平衡投资节奏',True,'肯定/会表达接受该未来方向')
scenario([117],'成功的商业航天公司出现','关注和人才待遇改善的正循环')
forecasts=[]
forecastspec={60:('branch_selection_forecast','likely','low',None,'中国航天供应链能力','increase','规模指标与基期未指定'),61:('branch_selection_forecast','near_certain','low',None,'全球发射需求集中于中国','all_to_china','需定义市场范围/安全限制及所有需求，不能只用份额上升结算'),64:('branch_selection_forecast','plausible','low',None,'中美航天产业链规模增长差','China_faster','需选择同口径收入/产能/发射次数；主播未选'),87:('unconditional_forecast','likely','low',None,'人民币兑美元达到6.5','RMB_appreciates','指定CNY/CNH、盘中/收盘和最后观察日后才可结算'),95:('unconditional_forecast','certain','medium','less than 4 years from current 40T milestone','美债达到50万亿美元用时','shorter','首个50万亿日距40万亿日少于四年；债务定义需确认'),96:('branch_selection_forecast','likely','medium','2028（年内/年末未定）','美债超过50万亿美元','increase','核对同口径联邦总债务；不得用公众持有债替代'),115:('branch_selection_forecast','near_certain','low',None,'国家平衡未来产业投资节奏','moderation','何种政策证明平衡未定义'),118:('unconditional_forecast','possible','low',None,'年轻人进入新技术领域的赚钱机会','increase','人群、收益门槛、反事实均未指定'),120:('unconditional_forecast','likely','low',None,'航天财富创造趋势','increase','先回听35年或3—5年，再定义财富指标，暂不可自动结算'),121:('unconditional_forecast','likely','low',None,'航天新富豪出现','increase','富豪门槛、来源及截止日未知')}
for n,(kind,modal,res,win,target,direction,criteria) in forecastspec.items():
 forecasts.append(dict(forecast_id=f'FC{len(forecasts)+1:02}',claim_ref=C(n),forecaster_id=AN,made_at=None,made_at_proxy=CUT,knowledge_cutoff=CUT,target=target,direction=direction,prediction_window=win,conditions=next((s['condition'] for s in scenarios if C(n) in s['claim_refs']),None),forecast_type=kind,modal_strength=modal,modal_mapping_observer=MO,certainty_expressed=CM[C(n)]['certainty_expressed'],resolution_criteria=criteria,resolvability=res,resolution_status='not_evaluated',source_segment_refs=CM[C(n)]['source_segment_refs']))
forecasts[4]['dependency_group']='debt50T';forecasts[5]['dependency_group']='debt50T'
arguments=[]
def arg(i,title,ns,edges,lim,mode='causal_inference',shortcuts=(),implied=()):
 ids=[C(n) for n in ns];ee=[]
 for a,b in edges:
  ee.append(dict(from_claim=C(a),to_claim=C(b),expression_level='strongly_implied' if (a,b) in implied else 'explicit',relation='creator_inference_not_verified_causation',is_shortcut=(a,b) in shortcuts,reasoner_id=AN))
 incoming={n:[] for n in ids}
 for e in ee:incoming[e['to_claim']].append(e['from_claim'])
 def depth(n,seen=()):
  assert n not in seen
  return max([1+depth(p,seen+(n,)) for p in incoming[n]] or [0])
 conclusions=[n for n in ids if n not in {e['from_claim'] for e in ee}]
 premises=[n for n in ids if not incoming[n]]
 arguments.append(dict(argument_id=f'AR{i:02}',title=title,reasoner_id=AN,analysis_context='historical_reconstruction',argument_type='historical_analogy' if mode=='historical_analogy' else 'argument',premises=premises,steps=ee,conclusion=conclusions,claim_refs=ids,inference_mode=mode,expression_level='mixed_explicit_strongly_implied' if implied else 'explicit',hop_count=max(depth(n) for n in ids),edge_count=len(ee),longest_path_length=max(depth(n) for n in ids),model_bridge_count=0,explicit_shortcut_count=sum(e['is_shortcut'] for e in ee),limitations=lim,source_segment_refs=list(dict.fromkeys(CM[n]['source_segment'] for n in ids))))
arg(1,'追上十年前水平被解释为追上今日主流',[1,2,3,4,5],[(1,2),(2,4),(3,4),(4,5)],'最弱处3→4：单一回收里程碑不能覆盖载荷、复飞、频次、可靠性和成本；条件速度也未量化。',shortcuts=[(3,4)])
arg(2,'独立攻关与公私研发互补',[1,6,7,8,9,10,11],[(1,6),(1,7),(8,9),(1,9),(9,10),(11,10)],'排除其他国家未成功并不能证明技术来源；两个任务不构成举国研发相对效率的充分反事实。',shortcuts=[(1,7)])
arg(3,'低成本运输作为远期开发前提',[14,15,16,17,18,34],[(15,14),(16,17),(17,18),(18,34)],'这是文明情景；低成本运输非充分条件，太空电梯和市场制度均未建立；生物演化类比无工程预测力。',mode='analogy',implied=[(16,17)])
arg(4,'回收成功被直接转成低成本及竞争叙事',[1,25,26,27,34],[(1,26),(25,27),(26,27),(26,34)],'关键错误入口1→26：没有复飞、翻修总成本、回收载荷损失与频次数据；不能把竞争者成本搬到中国。',shortcuts=[(1,26),(26,34)])
arg(5,'太空算力的成本与估值质疑',[20,21,22,23,24,36,37,38,39,40,42],[(36,37),(39,37),(37,24),(38,24),(20,24),(21,24),(23,24),(22,24),(40,24),(24,42)],'一克几百美元高风险；寿命、轨道、抗辐射、散热工程及可比地面成本均未测算；昂贵不等于所有场景不经济。')
arg(6,'中国企业上市的融资示范',[28,29,30,31,32,33,34],[(28,33),(29,33),(30,33),(31,33),(32,33),(33,34)],'上市状态需原始披露；高估值不等于可持续募资、更不等于航天现金流，行业类比范围有限。',mode='historical_analogy',implied=[(33,34)])
arg(7,'星链扩容飞轮及资金瓶颈',[43,44,45,46,47,48,49,50,51,52,53,54,55,57],[(44,45),(45,46),(45,47),(46,48),(47,48),(48,49),(45,50),(51,53),(52,53),(53,54),(50,54),(54,57),(55,57)],'20万/200万必须音频核对；卫星数量不是带宽、用户速度、单位成本的线性充分变量；政府意愿和无融资结论均无财务证据。',shortcuts=[(45,46),(45,47),(48,49)])
arg(8,'国家任务到产业规模及全球发射集中',[1,56,58,59,60,61,64],[(1,56),(58,60),(59,60),(60,56),(56,61),(60,64)],'最弱处56→61：成本优势不代表全球需求全流入，忽略国家安全、采购、贸易与客户结构；计划不等于capex到账或订单。',shortcuts=[(56,61)],implied=[(1,56)])
arg(9,'AI流动性退潮与国债融资替代',[65,66,67,68,69,70],[(65,67),(66,67),(68,69),(69,70)],'价格涨幅不能识别AI流动性的资金来源；下行也可能有其他融资渠道，国债信用不能自动证明项目效率。',shortcuts=[(66,67)])
arg(10,'财政回购到主权信任迁移',[71,72,73,74,75],[(72,73),(73,71),(71,74),(74,75)],'回购≠一级市场无人购买；OT类比≠QT；信任流失不必转向单一国家，政策自身目的与主播解释须分开。',shortcuts=[(72,73),(73,71)])
arg(11,'海南月球和华尔街的融资类比',[75,76,77,78,79,80,81,82],[(76,77),(77,75),(79,78),(75,81),(81,82)],'海南房地产与月球的可达性、产权、现金流、退出机制不可直接比；华尔街金融中介能力不是故事本身。',mode='historical_analogy',implied=[(75,81)])
arg(12,'技术案例到话语权和人民币',[1,27,33,75,81,83,84,85,86,87,89,97,99],[(1,27),(27,75),(33,75),(75,83),(83,87),(84,87),(85,87),(86,87),(83,89),(89,97),(27,99),(81,83)],'83→87以及89→97最弱：缺跨境资金、利差、风险溢价、国际收支与储备配置证据。此为叙事链，不是计量识别。',shortcuts=[(83,87),(89,97)],implied=[(75,83),(81,83)])
arg(13,'债务历史增量外推加速',[90,91,92,93,94,95,96,97],[(90,92),(91,92),(93,94),(90,94),(92,95),(94,95),(95,96),(96,97)],'历史4年增加10万亿不足推出未来2年；50万亿需赤字、利息和名义增长假设，30/40/50必须同口径。',shortcuts=[(92,95)],implied=[(96,97)])
arg(14,'估值叙事和选择性舆论的解释',[98,99,100,101,102,103,104,105,106,107,108],[(98,99),(100,101),(102,101),(103,106),(104,106),(105,106),(106,107),(107,108)],'由政策/牟利传言判断AI技术相等跳跃过大；主体、政策范围、模型基准和成本定义未明；动机推测不能用作事实。',shortcuts=[(105,106),(107,108)])
arg(15,'昂贵治疗到利润及估值拒绝门槛',[65,66,109,110,111,112,113,114],[(110,111),(111,112),(66,112),(109,112),(113,114)],'110→111最弱：患者价格高不等于企业单位成本高或利润低；缺医保支付、市场规模、毛利和适应症数据；名言不提供泡沫结算时间。',shortcuts=[(110,111)])
arg(16,'资本关注人才激励与航天财富前景',[34,60,115,116,117,118,119,120,121],[(34,120),(60,117),(115,117),(116,117),(117,118),(117,120),(119,120),(120,121)],'34→120和117→120缺持续客户、交付、现金流和利润证据；35年疑似3—5年但未回听，不定结算窗。',shortcuts=[(34,120),(117,120)],implied=[(60,117),(115,117)])
AM={a['argument_id']:a for a in arguments}
analogy_fields={3:('水生生命上陆/远期太空设想','人类进入太空','环境边界扩展','演化隐喻没有技术时间、投资回报可比性'),6:('存储、机器人企业上市','航天产业融资机会','技术题材吸引资本','上市地点、监管、客户和盈利模式各异'),11:('海南开发/华尔街吸纳资金','月球开发与中国资本吸引力','未来叙事聚集融资','区位、产权、退出、工程风险及失败史不同')}
for i,(s,t,m,l) in analogy_fields.items():AM[f'AR{i:02}'].update(source_case=s,target_case=t,shared_mechanism=m,limits_of_analogy=l)
arg(17,'煮酒论英雄类比竞争者话语',[62,63],[(62,63)],'文学/历史叙事不能证实马斯克实际心理与原话时点。',mode='historical_analogy')
arguments[-1].update(source_case='曹操与刘备煮酒论英雄的通俗叙事',target_case='马斯克评价中国竞争力',shared_mechanism='领先者界定谁配做对手',limits_of_analogy='文学情节、真实人物动机和商业竞争不能视为同一事实')
AM={a['argument_id']:a for a in arguments}
# Model diagnostics are assertions about missing evidence, not repaired creator steps.
diag_specs=[('M01','只有回收事件不能证明稳定复飞，需同硬件编号的多次任务和成功率。',1),('M02','判断经济复用需损伤、翻修时间/成本、替换部件、复飞可靠性、回收载荷损失、频次。',26),('M03','单位成本需同轨道、载荷、可靠性、含固定成本及回收设备的完整口径。',26),('M04','商业可行性还需付费客户、签约/交付、收入确认和现金流，订单不能直接转成利润。',61),('M05','产业结构变化需跨期可比Observation或跨期Event，单个回收不够。',120)]
for cid,t,n in diag_specs:
 claims.append(dict(claim_id=cid,segment_id=None,claimant=MO,claimant_id=MO,statement=t,claim_type='model_diagnostic',derivation_type='model_reconstruction',temporal_mode='atemporal',asserted_at=NOW,reference_time=None,knowledge_cutoff=CUT,population=None,quantifier=None,certainty_expressed=None,source_segment=None,source_segment_refs=[],context_source_segment_refs=[CM[C(n)]['source_segment']],atomicity_group_id=cid,reasoner_id=MO,analysis_context='model_diagnostic',comparison_basis=cb(),semantic_role=None,verified_knowledge_eligible=False))
CM={c['claim_id']:c for c in claims}
diagnostic=dict(argument_id='DA01',title='Event→经济复用→商业与产业结果的模型证据门槛',reasoner_id=MO,analysis_context='model_diagnostic',premises=['C001'],claim_refs=['C001','M01','M02','M03','M04','M05'],steps=[dict(from_claim=a,to_claim=b,expression_level='model_reconstruction',relation='requires_evidence_not_historical_causal_assertion',reasoner_id=MO) for a,b in zip(['C001','M01','M02','M03','M04'],['M01','M02','M03','M04','M05'])],conclusion=['M05'],inference_mode='diagnostic_requirements',expression_level='model_reconstruction',hop_count=5,edge_count=5,longest_path_length=5,model_bridge_count=5,explicit_shortcut_count=0,limitations='五跳为审计粒度的证据门槛图，不是产业必经时间表，更不是9527已经表达过的链。')
arguments.append(diagnostic)
# Separate a number from the analyst's saturation interpretation.
add(124,251,251,'interpretation','星链现有规模已经饱和。',pop='Starlink business scope unspecified')
CM['C044']['statement']='星链当前有20万颗卫星；保留转写数字待核。'
CM.update({c['claim_id']:c for c in claims});SSM={s['source_segment_id']:s for s in ss}
AM['AR07']['claim_refs'].append('C124');AM['AR07']['premises'].append('C124');AM['AR07']['source_segment_refs'].append('SS-C124')
CM['X09']['statement']='蓝箭称一级硬件多次复用可摊薄发射成本。'
SSM['SS-X09']['evidence_paraphrase']=CM['X09']['statement']
mechanisms=[dict(mechanism_id='ME01',status='candidate',name='需求牵引的供应链规模与成本优势',nodes=['可兑现的需求','供应链扩产和规模','成本竞争优势'],argument_refs=['AR07','AR08'],limits='需求未必兑现；规模不保证单位全成本下降；不纳入全球全部需求这一极端结论'),dict(mechanism_id='ME02',status='candidate',name='可信技术案例与融资条件',nodes=['可信技术里程碑','对未来项目的信任','融资吸引力或融资成本','后续投资'],argument_refs=['AR11','AR12'],limits='技术可信度≠现金流；利率制度和资本流动限制影响传导'),dict(mechanism_id='ME03',status='candidate',name='资本设备寿命与总使用成本',nodes=['损坏或寿命缩短','替换/折旧负担','单位服务经济性'],argument_refs=['AR05'],limits='须区分物理损坏、会计折旧、资本回收；不包含主播未经核实的具体寿命与美元数')]
mechanism_usages=[dict(usage_id=f'MU{i:02}',mechanism_ref=f'ME{i:02}',reasoner_id=AN,claim_refs=[C(n) for n in ns],argument_refs=mechanisms[i-1]['argument_refs'],expression_level='explicit',use_status='creator_applies_candidate_not_validated',source_segment_refs=[CM[C(n)]['source_segment'] for n in ns]) for i,ns in [(1,[50,55,56,58,60]),(2,[75,81,83]),(3,[36,37,39])]]
# Existing GS004 ME02 is a canonical candidate, not a promoted law. Reference its relevant subpath instead of cloning it.
mechanisms[2]=dict(mechanism_id='GS004/ME02',record_type='existing_candidate_reference',source_ref='R04',name='资本设备经济寿命与回收期错配',status='canonical_candidate_not_promoted',resolution='reuse_existing_candidate_subpath',observed_subpath=['物理损坏/寿命缩短','替换或折旧成本负担'],not_observed_here=['完整现金回收期计算'],argument_refs=['AR05'],limitations='本期只使用既有机制的一部分，不把完整回收期模型归给主播。')
mechanism_usages[2].update(mechanism_ref='GS004/ME02',use_scope='partial_subpath',new_mechanism_created=False)
registry_search=dict(scope='local_partial_registry',read_sources=['R01','R02','R03','R04'],full_registry_available=False,note='GS002发布时间晚于本期，允许事后方法比对，禁止成为本期可知事实；无修改既有样本。')
theses=[]
for i,t,ars,decision,related,support,falsify in [
 (1,'9527判断技术追赶叠加国家任务、工业规模和资本参与，将打开中国航天产业的财富创造阶段。',['AR04','AR08','AR16'],'new',[],'多次复飞、同口径单位成本、付费需求与企业现金流及跨期人才收入','反复回收不稳定、全成本未下降、真实需求不足或回报不能覆盖投入'),
 (2,'9527判断中国技术追赶将削弱美国的资本叙事优势，增强中国资产吸引力并影响货币竞争。',['AR10','AR11','AR12','AR13'],'related',['GS001/美国安全资产属性结构性弱化摘要','GS002/TH03（较晚样本仅目录比较）'],'分币种真实流量、估值与利差、技术产出的连续观察','技术进展未带来资本流入或风险溢价下降，汇率由其他变量主导')]:
  trace=[]
  for ar in ars:
   for cid in AM[ar]['claim_refs']:
    for sid in CM[cid]['source_segment_refs'][:1]:trace.append(dict(argument_id=ar,claim_id=cid,source_segment_id=sid,source_id=SSM[sid]['source_id']))
  theses.append(dict(thesis_id=f'TH{i:02}',statement=t,owner=AN,status='candidate_unverified',resolution=decision,resolution_provisional=True,related_theses=related,registry_search=registry_search,argument_refs=ars,traceability=trace,support_needed=support,falsification=falsify,verified_knowledge_eligible=False))
corrections={'accepted_ASR_corrections':[],'candidate_corrections':[],'needs_audio_review':[]}
for a,b,r,n,why in [(2,4,'splay X/sweX','SpaceX','后文多处英文全名和语境一致，仅实体规范化'),(18,19,'可服用','可复用','火箭回收语境唯一明确'),(32,35,'信往回舟','海上网系回收','国家航天局通报与海上/陆地对照支持；非逐音确认'),(174,180,'太空算律/三类/算计中心','太空算力/计算中心','同一段多次一致话题'),(249,258,'新练/训练/经店/星练','星链','同段明确出现星链实体'),(276,276,'朱雀山','朱雀三号','本期标题与任务对应'),(306,306,'蓝天航天','蓝箭航天','朱雀三号研制主体由V01明确；不据此确认雄安建设计划'),(355,357,'莫德娜/黑色素流','Moderna（莫德纳）/黑色素瘤','SRC-C与V02一致；默沙东是另一主体不可合并')]:
 corrections['accepted_ASR_corrections'].append(dict(correction_id=f'AC{len(corrections["accepted_ASR_corrections"])+1:02}',raw=r,normalized=n,basis=why,status='accepted_textual_normalization',confidence='high_contextual_not_audio',source_id='S02',**bd(a,b)))
for a,b,r,n,why in [(185,185,'长新/长江','长鑫存储/长江存储','实体候选，不确认上市状态'),(188,202,'语速/语数','宇树','机器人语境强，但仍须实体与IPO披露'),(244,244,'六网升级','电网升级?','词不明确，保留原文'),(373,376,'QT / operation twist','OT?','可能ASR也可能主播术语混淆，不自动修成正确金融说法'),(531,531,'长长试仪','unknown','不能根据近期新闻猜型号'),(584,585,'莫啥东','默沙东? Moderna?','语义对象摇摆'),(636,637,'35年','3—5年?','相邻口语不用太长只能提供候选，不能代替听音')]:
 corrections['candidate_corrections'].append(dict(raw=r,candidate=n,basis=why,status='pending_audio_or_primary',source_id='S02',**bd(a,b)))
for a,b,why in [(227,227,'每克大几百美元；质量单位、数字、成本/报价'),(252,270,'20万/200万/180万及十倍数量关系'),(357,357,'190%多/翻两倍与市值口径'),(482,497,'30/40/50万亿、年份和一两年'),(571,572,'涨三倍是涨到三倍还是增长三倍'),(636,637,'预测窗口35年或3—5年')]:corrections['needs_audio_review'].append(dict(source_id='S02',reason=why,review_status='not_listened',**bd(a,b)))
annotations=[dict(annotation_id='SA01',type='self_correction',source_id='S02',**bd(514,515),statement='年初→不是年初、前段时间；后者为有效时间表述，原说法保留'),dict(annotation_id='SA02',type='self_correction',source_id='S02',**bd(589,589),statement='里根→林肯；自纠并不验证名言出处'),dict(annotation_id='SA03',type='ambiguous_reference',source_id='S02',**bd(355,357),statement='莫沙东/莫德娜切换，后半明确莫德娜；涉及两家合作公司'),dict(annotation_id='SA04',type='speaker_slip_candidate',source_id='S02',**bd(373,376),statement='QT与Operation Twist不对应，未听音不能确认责任在ASR还是主播'),dict(annotation_id='SA05',type='ambiguous_reference',source_id='S02',**bd(584,585),statement='否定单家公司能力时公司归属摇摆'),dict(annotation_id='SA06',type='mixed_fact_and_opinion',source_id='S02',**bd(1,4),statement='回收报道与追平技术的解释混合，已拆C001—C004'),dict(annotation_id='SA07',type='mixed_fact_and_opinion',source_id='S02',**bd(357,359),statement='药物消息、行情数字与AI资金来源、危机情景混合，已拆C065—C070')]
actors=[dict(actor_id=i,name=n,role=r,entity_resolution_status=s) for i,n,r,s in [('A01','有何高见9527','analyst','user_attributed'),('A02','蓝箭航天','rocket_developer','V01_supported'),('A03','SpaceX','launch_and_satellite_business','text_normalized'),('A04','Elon Musk','reported_speaker','quotes_not_original_verified'),('A05','中国政府/国家队','policy_funding_aggregate','specific_agency_scope_varies'),('A06','美国军方','alleged_customer_and_funder','specific_contract_unknown'),('A07','Moderna','drug_developer','V02_supported'),('A08','Merck/默沙东','drug_partner','V02_supported'),('A09','美国财政部/贝森特','policy_actor','V03_supported'),('A10','特朗普','political_actor','personal_business_allegation_unverified'),('A11','宇树','robotics_issuer_claim','IPO_status_unverified'),('A12','蓝色起源/贝索斯','comparison','operational_comparison_unverified'),('A13','NASA/欧洲航天机构','comparison_context','not_interchangeable_with_US_all_launchers'),('A14','长鑫/长江存储','issuer_candidates','entity_and_listing_review'),('A15','耶伦','reported_historical_forecaster','original_testimony_not_found')]]
events=[dict(event_id='EV01',name='朱雀三号遥二发射及一级着陆',event_status='reported_success_supported_by_origin_release',launch_at='2026-08-19T07:35:00+08:00',landing_at='2026-08-19T07:41:00+08:00',announced_at='2026-08-19',time_precision='launch/landing minute; announcement day',claim_refs=['C001','X01','X02'],source_refs=['SRC-A','V01'],evidence_family='FLANDSPACE',demonstrated_boundary='本次一级着陆；不填成功复飛次数，不宣称20次整箭复用'),dict(event_id='EV02',name='此前海上网系回收',event_at='2026-07-10',claim_refs=['C008'],source_refs=['V01','SRC-A'],status='context_report_not_independent_process_series'),dict(event_id='EV03',name='Moderna/Merck试验结果公告',event_at='2026-08-19',claim_refs=['C065','X05'],source_refs=['V02'],status='company_announced_not_approval_or_cure'),dict(event_id='EV04',name='财政部回购规模调整公告',event_at='2026-08-19',effective_at='2026-09-09',claim_refs=['C072','X06','X07'],source_refs=['V03'],status='announced_policy_not_already_executed'),dict(event_id='EV05',name='SpaceX上市回顾',event_at=None,raw_time='前段时间（自纠年初）',claim_refs=['C019','C098'],status='creator_report_requires_primary'),dict(event_id='EV06',name='未知型号火箭失败',event_at=None,raw_time='前几天',claim_refs=['C100'],status='unresolved_model_requires_audio')]
policies=[dict(policy_id='PO01',name='美国长期国债流动性支持回购规模调整',actor='US Treasury',announced_at='2026-08-19',effective_at='2026-09-09',end_at='2026-11-04',source_claim_refs=['X06','X07'],policy_status='announced',not_equivalent_to=['QT','QE','央行OT','长债完全无买家']),dict(policy_id='PO02',name='中国月球及太空开发计划（主播提及）',policy_status='reported_plan_scope_unspecified',target_time='2030登月为主播提到的时间',claim_refs=['C012','C058'],specific_budget=None,actual_disbursement=None),dict(policy_id='PO03',name='美国禁止中国AI模型（主播声称）',policy_status='unverified_policy_claim',claim_refs=['C104'],legal_instrument=None,scope=None)]
indicators=[];observations=[]
def obs(i,name,cid,val,unit,vs,role,period=None,pop=None):
 iid=f'I{i:02}';indicators.append(dict(indicator_id=iid,name=name,unit=unit,population=pop,semantic_role=role,canonical_status='candidate'))
 observations.append(dict(observation_id=f'O{i:02}',indicator_ref=iid,claim_ref=cid,value=val,unit=unit,value_status=vs,value_origin=CM[cid]['claimant_id'],reference_time=period,population=pop,semantic_role=role,comparison_basis=CM[cid]['comparison_basis'],verified_observation=False,source_segment_refs=CM[cid]['source_segment_refs']))
obs(1,'SpaceX相对发射成本','C025',0.1,'ratio','creator_report_unverified','operating_cost',pop='unnamed_competitors')
obs(2,'单位质量入轨成本（原始克口径）','C038',None,'USD/g','ASR_suspect_no_normalization','operating_cost',pop='orbit/payload_unknown')
obs(3,'星链卫星规模','C044',200000,'satellites','ASR_or_speaker_error_unresolved','capacity',pop='status_unknown')
obs(4,'星链二期部署计划','C045',2000000,'satellites','creator_reported_plan_unverified','capacity',pop='plan_not_orbit')
obs(5,'Moderna市值变动','C066',190,'percent_more_than','creator_report_window_unknown','valuation','昨天')
obs(6,'Moderna盘前股价变动','X04',80,'percent_more_than','media_report','valuation','2026-08-19 premarket')
obs(7,'人民币兑美元报价','C085',None,'CNY_or_CNH_per_USD_unresolved','creator_report_6.7x','price','现在')
obs(8,'美国债务规模','C090',40,'USD trillion exceeded','creator_report_primary_not_read','debt_stock','2026 current')
obs(9,'美国债务历史规模','C091',30,'USD trillion exceeded','creator_historical_report','debt_stock','2022')
obs(10,'着陆腿复用能力','X03',20,'uses','reported_engineering_capability_not_demonstrated_count','technology',pop='landing_leg_not_entire_rocket')
obs(11,'国债回购每次操作上限','X06',4,'USD billion_at_least','announced_limit_not_transaction','policy_operation_limit','effective 2026-09-09')
obs(12,'FCC Gen2许可规模','X08',15000,'satellites','regulatory_authorization_not_deployment','authorization','2026-01-09')
obs(13,'媒体成本下降预计','X10',70,'percent_ambiguous_to_or_by','media_projection_not_observed','operating_cost')
obs(14,'太空芯片寿命情景','C039',None,'years','creator_hypothesis_one_to_four_not_measurement','technology')
for o in observations:
 if o['claim_ref']=='C038':o['raw_value']='一克…大几百美元'
 if o['claim_ref']=='C085':o['raw_value']='6点7几'
# No measured public expectation was observed: statements about market psychology remain narrative assessments.
expectations=[]
veracity=[]
specific={
 'C001':('supported_limited',['X01','X02'],'V01与SRC-A共享蓝箭来源，支持任务回收，不独立证明复用经济性。'),
 'C008':('supported_limited',[],'V01有此前海上网系回收；措辞校正基于语境，未听音。'),
 'C026':('insufficient_evidence',[],'把回收能力转成已实现低成本，缺DA01证据门槛。'),
 'C038':('high_risk_numeric_or_unit_error',[],'原文每克几百美元；没有静默改为每千克。'),
 'C044':('high_risk_numeric_unverified',['X08'],'FCC授权数字不可直接反证全部在轨数，但不支持20万；V05片段亦显著不同，因时间不明未纳入事实底座。'),
 'C045':('unverified_reported_plan',[],'缺马斯克原话及星座代际定义，不能拿不同星座申报数字替换。'),
 'C065':('supported_as_company_announcement',['X05'],'支持试验利好公告，不是治愈癌症或批准上市。'),
 'C066':('unresolved_measurement',['X04'],'盘前80%与主播190%不同时间/对象，既不能直接等同也不能直接判矛盾。'),
 'C072':('partly_supported_terminology_review',['X06','X07'],'财政部回购确有公告；QT/OT及短债资金来源需分别验证。'),
 'C073':('unsupported_inference',['X06'],'官方给出流动性支持目的，不能据此推出一级市场无人买债。'),
 'C090':('provisionally_corroborated_not_primary_verified',[],'同期新闻检索支持跨40万亿方向，官方历史API读取失败，原始日表与总债务口径仍待审。'),
 'C093':('unverified_original_source_missing',[],'未定位耶伦2023听证原话及其所指债务口径。'),
 'C105':('unverified_serious_allegation',[],'保留主播归属；没有原始许可、公司和交易证据，不进入事实库。'),
 'C109':('unresolved_measurement',[],'涨三倍/涨到三倍与190%并列，可能近似也可能不一致，需同窗口与音频。'),
 'C111':('unsupported_inference',[],'患者价格、生产成本、销售收入和企业利润是不同角色。'),
 'C113':('self_correction_observed_attribution_unverified',[],'只证实转写中自纠；名言真实出处未核。'),
 'X03':('supported_as_media_capability_statement',[],'20次属部件声称能力；设计目标或工程估计无法再细分；实飞完成次数unknown。'),
 'X10':('ambiguous_media_projection',[],'原文降低到70%以上有歧义，不规范化为下降70%。')}
for c in claims:
 cid=c['claim_id'];k=c['claim_type']
 if cid in specific:status,ev,why=specific[cid]
 elif cid.startswith('M'):status,ev,why='model_diagnostic_not_creator_fact',[],'模型提出可检验的证据要求，不回填主播论证。'
 elif cid.startswith('X'):status,ev,why='supported_as_source_assertion',[],'已读来源支持其作出该声明；该机构声明本身不等于独立实证。'
 elif k=='forecast':status,ev,why='not_yet_evaluated',[],'只登记预测；未使用截止后结果评分。'
 elif k in ['conditional_claim','hypothetical_assumption','analogy','historical_analogy']:status,ev,why='scenario_or_analogy_not_observed_fact',[],'条件结果/类比不是已发生事实；见关联Argument限制。'
 elif k in ['interpretation','inference','derived_claim']:status,ev,why='creator_reasoning_not_verified',[],'论证出处可追溯不等于推理正确；重要限制逐Argument列出。'
 else:status,ev,why='unverified',[],'缺完整同口径原始来源核验；不因多次转述提高可信度。'
 veracity.append(dict(assessment_id='VA-'+cid,claim_ref=cid,observer=MO,assessed_at=NOW,as_of=CUT,status=status,evidence_claim_refs=ev,explanation=why,verified_knowledge_eligible=False))
narratives=[dict(assessment_id='NA01',observer=AN,claim_refs=['C024','C035','C099'],statement='主播把太空算力解释为承接AI流动性的资本故事。',evidence_status='creator_interpretation'),dict(assessment_id='NA02',observer=AN,claim_refs=['C071','C073','C074'],statement='主播把财政回购解释为信用失灵及信任迁移。',evidence_status='creator_interpretation'),dict(assessment_id='NA03',observer=AN,claim_refs=['C075','C083','C097'],statement='主播把航天技术事件放进中美话语权、资产及货币竞争。',evidence_status='creator_interpretation'),dict(assessment_id='NA04',observer=MO,claim_refs=['C026','C111','C112'],statement='经济性证据门槛在两类案例间不对称；这是待审的分析过程信号，不能推断心理动机。',evidence_status='model_diagnostic'),dict(assessment_id='NA05',observer=AN,claim_refs=['C101','C103'],statement='主播以叙事领先受威胁解释舆论差异，并拒绝将估值等同技术能力。',evidence_status='attributed_not_verified')]
methods=[]
def method(i,typ,statement,ns,ars,why,lim,level='explicit'):
 methods.append(dict(signal_id=f'MS{i:02}',analyst_id=AN,observed_reasoner_id=AN,annotation_observer=MO,signal_type=typ,statement=statement,claim_refs=[C(n) for n in ns],argument_refs=ars,source_segment_refs=[CM[C(n)]['source_segment'] for n in ns],expression_level=level,analysis_context='method_observation_after_argument_extraction',why_this_is_method_not_conclusion=why,limitations=lim,recurrence_status='candidate_pending_precision_match',promotion_status='candidate_not_stable_skill',confidence='textual_support_not_method_validity'))
method(1,'attention_pattern','首先选择相对竞争位置和话语权，而非复飞统计。',[2,3,4,12],['AR01','AR03'],'记录面对同一新闻的变量选择顺序。','单期开头不证明长期固定排序；C012作为旁证不承担算法。')
method(2,'question_pattern','追问扩容的真实需求、付款者以及资本从哪里来。',[50,53,54,58],['AR07','AR08'],'把市场形成与资金供给拆开追问，可跨行业操作。','不能把他对军方动机和融资无门的答案当事实。')
method(3,'mechanism_usage','通过芯片寿命、替换与运输成本检验太空算力经济性。',[36,37,38,39,40],['AR05'],'观察如何审查单位服务成本与资产寿命。','本期数字与轨道假设不足；没有完整算过回报率。')
method(4,'judgment_pattern','拒绝把单次药物突破或高估值直接作为可持续盈利的充分证据。',[110,111,112,103],['AR15','AR14'],'识别拒绝门槛而非某家公司涨跌结论。','仅恢复拒绝门槛；价格昂贵→利润低的中间推断本身有缺陷。')
method(5,'judgment_pattern','对国内航天，以技术里程碑、国家任务、产业规模潜力和资本人才循环作正向机会判断。',[26,58,60,117,120],['AR04','AR08','AR16'],'尝试恢复把技术新闻升级为产业机会的观察门槛。','这是本期实际采用的非量化门槛；未观察到稳定复飞、客户订单、现金流的强制验证规则。','strongly_implied')
method(6,'analogy_pattern','用已发生的开发热潮和金融集资模式推想新领域融资空间。',[76,77,79],['AR11'],'可复用的跨案例融资机制寻找动作。','海南与月球工程条件不同，不能从相似叙事推出同回报。')
method(7,'failure_pattern','由单次回收直接推已经低成本，再把成本优势推到全球全部需求集中。',[1,26,56,61],['AR04','AR08'],'存在明确证据台阶跳过，未来可检查是否重复。','模型观察到的是推理缺口；不能证明最终预测一定错误。')
method(8,'failure_pattern','把数量倍数直接传给带宽、网速和成本，缺少系统约束。',[45,46,47,48,49],['AR07'],'相同数量变换动作可跨案例检验。','在轨数本身待听音；即使数字修正，线性比例推理也需机制证据。')
method(9,'failure_pattern','把患者治疗价格高直接推为药企盈利空间小。',[110,111,112],['AR15'],'Semantic Role转换错误候选，可在其他成本利润推断中检验。','价格高也可能反映成本高或支付困难，但本期未提供这些证据。')
method(10,'branching_pattern','区分私营风险资本狂热期与退潮后的国家信用融资情景。',[68,69,70],['AR09'],'依据融资环境改变支持主体的情景组织方式。','没有预测AI泡沫何时破裂，不是完整周期模型。')
method(11,'evidence_preference','在美国AI/药物话题中偏重成本盈利而不接受估值作为技术与利润的充分证据。',[103,110,112],['AR14','AR15'],'本期有明确比较两种证据的动作。','局部、单期偏好信号；中国上市高估值被正面引用C033，是适用范围边界，不能升级普遍偏好。')
# MS01 C012 appears outside AR03; include its actual interpretive context as a premise rather than inventing an edge.
AM['AR03']['claim_refs'].append('C012');AM['AR03']['premises'].append('C012');AM['AR03']['source_segment_refs'].append('SS-C012')
recurrence=[]
def rec(i,prior,current,match,shared,missing,status='matched'):
 recurrence.append(dict(recurrence_id=f'MR{i:02}',prior_ref=prior,current_signal_refs=current,match_type=match,match_status=status,shared_operation=shared,not_shared_or_unknown=missing,evaluation_time=NOW,historical_evidence_use=False,stable_skill_promotion=False))
rec(1,'GS001/summary:结构力量优先于政治人物',['MS02'],'analogous','资金与任务约束被用来解释主体行为','GS001只有摘要；不能验证具体判断步骤或原句。')
rec(2,'GS002/HC01',[],None,'未观察到增量看趋势、存量看空间的完整动作','星链规模讨论不能冒充同一增量/存量方法；GS002较晚。','not_observed')
rec(3,'GS002/HC02',['MS02'],'analogous','追问结果背后的执行条件','本期不是确权、债权人谈判或化债成本；不可判exact。')
rec(4,'GS003/HC01',['MS02','MS03'],'partial','追问叙事的实际执行能力和约束','本期不含海峡实际控制标准，也未统一核验国内经济复用。')
rec(5,'GS003/HC02',['MS10'],'partial','按资金环境分阶段比较支持能力','未使用冲突阶段划分和双方持续成本计算。')
rec(6,'GS004/MS01',['MS02','MS03'],'partial','资金与持续成本约束复现','没有完整重现GS004组织执行边界的全部操作。')
rec(7,'GS004/MS03',['MS03'],'partial','资本硬件寿命影响持续成本','本期没有明确完整周期回报比较，不能把寿命子动作判exact。')
rec(8,'GS004/MS04',['MS04'],'partial','拒绝价格/单点消息作为充分证据','本期对象、正向接受条件不同。')
rec(9,'GS004/MS05',['MS06'],'analogous','跨案例找可迁移机制','手机习惯或折旧与月球融资不是同一共享机制。')
rec(10,'GS004/MS06',['MS08'],'analogous','从一个比例跳到另一个结论量','时间比→泡沫倍数与卫星数→网速成本变量不同；不能叫同一错误已复现。')
rec(11,'GS004/MS02',[],None,'无明确同口径分母审查复现','本期数字口径多处未澄清，不能借模型纠错补出方法。','not_observed')
rec(12,'GS004/MS07',[],None,'未观察到非粉丝视角与转化对象审查','资本客户话题不等于公关人群方法。','not_observed')
rec(13,'GS004/MS08',[],None,'未观察到跑早/跑晚分支全导向同结果的模式','本期AI融资分支不同。','not_observed')
for m in methods:
 matches=[r for r in recurrence if m['signal_id'] in r['current_signal_refs']]
 m['recurrence_refs']=[r['recurrence_id'] for r in matches];m['recurrence_status']='limited_match' if matches else 'first_observation_in_available_registry'
method_bundle=dict(analyst_id=AN,signals=methods,method_recurrence=recurrence,exact_match_count=0,stable_method_count=0,falsification_patterns=[],negative_findings=['未观察到要求稳定重复回收、实际复飞、翻修成本的必经审查。','没有把20次设计能力当实飞的主播证据，不能创建此Failure。','未观察到以订单优先于技术参数的明确偏好。'],judgment_gate_answer='本期正向判断依靠技术赶超、国家任务与工业潜力；完整可操作接受规则仍insufficient evidence。')
reviews=[]
def review(priority,category,refs,issue,action):reviews.append(dict(review_id=f'RQ{len(reviews)+1:02}',priority=priority,category=category,object_refs=refs,issue=issue,required_action=action,status='open',blocks_verified_promotion=True))
review('Critical','Data/ASR',['C044','C045','C046','C047','C048','C049','C051'],'20万、200万、180万及十倍推导影响整条星链论证。','逐句听252—270；分开在轨、许可、计划、客户数量；找当时公司披露，不猜修正数。')
review('Critical','Data/ASR',['C038'],'每克大几百美元的质量单位、数字和成本/报价高风险。','回听227并找同轨道同载荷报价与成本，不自动改千克。')
review('Critical','Reasoning',['AR04','AR08','TH01'],'成功回收→已低成本→全球全部需求，跨层级。','补DA01明确列出的经济复用和商业需求证据，保留原Shortcut。')
review('Critical','Attribution',['C105'],'针对特朗普私人公司的牟利指控没有可审计来源。','定位原新闻、公司、许可文件及交易；在此之前只作attributed allegation。')
review('High','Source/time',['SRC-E','V06','V07','V08'],'原Reuters页失败；转载时区与原版发布时间未知。','核原页JSON-LD或可信存档，确认首次发稿和更新时间；不能因照片8月10日推文章可知。')
review('High','Source/version',['SRC-A','SRC-B','SRC-C','SRC-D','V01','V02','V03'],'当前网页版本不等于2026-08-20截止时版本。','取得历史存档或修订记录；SRC-D虽08:42早于10:37，录制是否早于发稿仍未知。')
review('High','Data/semantic_role',['X03','O10'],'20次是着陆腿能力，目标/估计依据未区分。','查原工程说明和部件测试；拒绝写成整箭实际20次复飞。')
review('High','Data/comparison',['X10'],'降低到70%以上可能应为下降70%以上，且基期未知。','核央视原稿或视频；保留两解释，不自行订正。')
review('High','Data/comparison',['C066','C109','X04'],'190%多、翻两倍、涨三倍与盘前80%时间/对象混淆。','回听并核同一日盘前、盘中、收盘价格及股本；区分价格和市值。')
review('High','ASR/Policy',['C072','SA04'],'QT与Operation Twist并列。','听音判ASR或口误；核财政部操作而非套美联储工具。')
review('High','Reasoning',['C071','C073','AR10'],'回购推无人买、再推信用破产。','查拍卖投标倍数、尾差、期限溢价及回购券种；债券流动性不等于偿付能力。')
review('High','Data/time',['C090','C091','C092'],'30/40万亿美元未读到原始历史日表。','获取Treasury历史日表，统一total public debt outstanding与debt held by public。')
review('High','Source',['C093','C094'],'耶伦2023预测2028达40万亿原话未定位。','查听证稿与同期CBO口径，不能用2026报道回填2023信息。')
review('High','Forecast',['C095','C096'],'历史四年增量不足推出未来两年；相互嵌套时间承诺。','核赤字/利息模型；两预测按同一dependency_group计评价，勿双计命中。')
review('High','Forecast/ASR',['C120','C121'],'结尾35年疑似3—5年，财富/富豪阈值模糊。','回听636后定时间窗口，并与人工协商指标；不靠语感归一。')
review('High','Reasoning',['C110','C111','C112'],'个性化治疗昂贵→利润小缺价格/成本区分。','核单位成本、支付能力、定价、患者规模；不能把患者花费当企业成本。')
review('High','Source/medical',['C065','X05'],'公司topline不等于完整临床证据、治愈或商业化。','查试验注册、预设终点、效应量、随访和监管状态；本期仅公告级。')
review('High','Source',['C104','C106','C107','C108'],'禁用范围、AI能力和成本可比性未核。','定位政策主体与适用场景，基准同模型任务、硬件、定价/成本分开。')
review('High','Data/Forecast',['C084','C085','C087'],'连续升值表述及6.7x/6.5报价口径不明。','核截止前CNY/CNH、中间价/即期及观察窗，预测不可无限期等待。')
review('High','Source',['C043','C053','C054','C057'],'唯一盈利项目、军方无动力、无财源均缺财务与合同证据。','读同期财报、募资及采购；去除Starlink/Starshield/商业客户混同。')
review('Medium','ASR/entity',['C028','C029','C030','C032'],'长鑫/长江/宇树名称与上市/产线状态。','校名字并独立核交易所文件与特斯拉披露。')
review('Medium','ASR/entity',['C059'],'蓝天候选蓝箭；产业链主体可能涉及关联公司。','核雄安项目签约、出资、主体与已建产能，不能用集团关系代替。')
review('Medium','ASR/entity',['C100'],'失败火箭型号未知。','回听531定位，不能拿Reuters同题长征7A直接补。')
review('Medium','ASR/entity',['C041'],'六网升级不明确。','回听244并确认政策/工程名称。')
review('Medium','Source/Attribution',['C062','C063'],'马斯克仅中美原话未核，煮酒论英雄是动机类比。','原始访谈定位，禁止把类比当真实心理证据。')
review('Medium','Reasoning',['C003','C004','C011'],'无重大进步/仅数据差距缺同指标技术比较。','分产品版本、载荷、复用、可靠性、频次和价格比较。')
review('Medium','Reasoning',['C020','C021','C022','C023','C036','C037','C039','C040'],'太空与地面算力对比缺任务轨道和全生命周期口径。','技术原始资料核辐射寿命、散热、能源、通信和维护。')
review('Medium','Historical analogy',['AR03','AR06','AR11','AR17'],'生物演化、上市示范、海南月球及曹刘的类比边界。','分别核源案例，不将相似当同一。')
review('Medium','Forecast',['C060','C061','C064','C115','C118'],'方向明确但规模、时间、条件与对象弱可结算。','保留低resolvability，不补伪精确窗口。')
review('Medium','Ontology',['DA01','method_recurrence','comparison_basis'],'本地未提供机器Schema；声明自定义字段需映射。','审核扩展清单后导入，不能称生产Schema验证通过。')
review('Medium','Ontology/temporal',['R02','TH02'],'GS002较晚样本只能事后注册表/方法匹配。','禁止创建指向本期历史信息集的evidence边。')
review('Medium','Method',['MS05','MS07','MS11'],'正向门槛与负向门槛不对称是模型观察，非稳定心理解释。','跨期盲审对称案例；Failure必须保留双observer字段。')
review('Low','Attribution',['C113'],'林肯名言归属未核。','查可靠原始文献，保留自纠，不从名言推出泡沫期限。')
review('Low','Coverage/audio',['S01','S02'],'639个字幕块来自同一ASR，没有独立听音；并非两个独立证人。','优先回听Critical/High时间段；其余不能称人工逐句校对。')
review('High','StructuralProcess',['EV01','EV02','TH01'],'两个不同技术任务是跨期事件，但还不足以形成商业产业结构过程。','观察同一指标跨期序列；不能只因为满足多Event字面条件就升级Reality。')
review('Medium','Source',['V05'],'FCC勘误PDF403且发文日未知，片段中10,200不是本期可安全采用的即时值。','取得原PDF及SEC原披露并核截止资格；不参与当前事实纠正。')
review('Medium','Source/version',['V01'],'通报末段使用复飞任务措辞，但没有硬件序列号与前次飞行履历。','核复飞是型号第二次还是同一级重飞；不从单词推Operational Reusability。')
# Attach grouped reviews to each relevant claim; uncovered minor claims have an explicit status rather than guessed verification.
for c in claims:
 c['review_refs']=[r['review_id'] for r in reviews if c['claim_id'] in r['object_refs']]
 if not c['review_refs'] and c['claim_id'].startswith('C'):c['review_refs']=['RQ34']
for v in veracity:v['review_refs']=CM[v['claim_ref']].get('review_refs',[])
issues=[
 dict(issue_id='IS01',area='prompt_version',problem='当前提示词实际在39节的exact/partial/analogous处结束，无后续输出顺序和可执行Schema。',handling='按前样本29节骨架组织输出，MA.1字段以明确辅助结构补充；不假装读到不存在的后半文件。'),
 dict(issue_id='IS02',area='time',problem='Publication、recorded_at、utterance media offset不可互换。',handling='主播asserted_at/made_at=null；publication_proxy为cutoff；保存每段media offset。'),
 dict(issue_id='IS03',area='source_version',problem='同日转载的时区、原发时刻和修订时刻未明；日期相同不足以准入。',handling='SRC-E/V06/V08隔离；不强判已确认post-cutoff。'),
 dict(issue_id='IS04',area='component_scope',problem='20次复用指着陆腿，不是整箭，也不是实际次数。',handling='population=landing_leg、value_status与demonstrated_count分存；能力类别细分不足进入Review。'),
 dict(issue_id='IS05',area='measurement',problem='价格变动、总市值变动、增长倍数与最终倍数、盘前与全日不可互换。',handling='Comparison Basis全Claim显式存在，未知null；同句数字变体保留，不平均。'),
 dict(issue_id='IS06',area='semantic_role',problem='技术能力→已实现运营成本，价格→企业利润存在角色跨越。',handling='Claim/Observation标角色；Failure Signal以模型observer标缺口，模型诊断不回写历史Claim。'),
 dict(issue_id='IS07',area='distance',problem='跳数依赖节点粒度及叙述拼接，单一hop_count不能代表可信度。',handling='逐边expression_level；综合链与单Argument分别计；diagnostic requirement边不是因果边。'),
 dict(issue_id='IS08',area='source_independence',problem='CNSA转载蓝箭与媒体采访同源、TXT/SRT同ASR，不是四份独立证据。',handling='origin_family_ids保存来源依赖，不能按URL数量叠加置信度。'),
 dict(issue_id='IS09',area='forecast',problem='方向承诺但条件与窗口模糊；回顾过去预测不是原始预测。',handling='不删弱预测但标low；只有Scenario未选分支者不进Ledger；C088不生成年初Forecast。'),
 dict(issue_id='IS10',area='forecast_dependency',problem='不到4年和2028两个承诺嵌套，不能双计命中。',handling='dependency_group=debt50T；新字段是明确辅助扩展。'),
 dict(issue_id='IS11',area='recurrence_precision',problem='相似主题易误判为方法exact；本期只有局部动作或类比匹配。',handling='match_type仅exact/partial/analogous；未观察项为null+not_observed，不创造第四匹配等级。'),
 dict(issue_id='IS12',area='failure_observer',problem='模型评估的失败模式易归给主播自认。',handling='observed_reasoner_id=AN且annotation_observer=MO；future human review可改评估者，不能改被观察者。'),
 dict(issue_id='IS13',area='structural_process',problem='多个技术事件不自动足以证明经济产业过程。',handling='本样本StructuralProcess=0，保留两个技术Event及待检验Thesis。'),
 dict(issue_id='IS14',area='expectation',problem='主播猜军方/投资者心理不等于明确Population的实测预期。',handling='保留Narrative Assessment，不强建ExpectationSnapshot。'),
 dict(issue_id='IS15',area='registry_scope',problem='旧样本目录不齐，GS001只有摘要且样本编号不按时间排序。',handling='local_partial_registry；相关而非覆盖更新；GS002不进入8月20日信息集。'),
 dict(issue_id='IS16',area='enum_extensions',problem='未提供生产JSON Schema及完整枚举。',handling='本地 descriptive enum：model_diagnostic, reported_plan, policy_operation_limit, context_source_segment_refs, comparison_basis, dependency_group；需正式导入映射，不能偷偷视为新核心本体。')]
distance=dict(counting_rule='边数是可见推理连接，最长路径按DAG计算；不是已证因果数量。',creator_local_shortcut=['C001','C026','C034'],creator_local_shortcut_edge_count=2,integrated_industry_chain=['C001','C026','C034','C120','C121'],integrated_industry_edge_count=4,integrated_expression_levels=['explicit','explicit','strongly_implied_cross_segment','explicit'],cross_segment_stitch_observer=MO,source_arguments=['AR04','AR16'],model_bridge_count_in_creator_graph=0,diagnostic_graph='DA01',diagnostic_gate_count=5,diagnostic_caveat='补足数据门槛并不证明结论成立；不把DA01计入9527方法。',finance_long_chain=['C001','C027','C075','C083','C089','C097'],finance_long_chain_edge_count=5,finance_chain_limits='技术→叙事→话语权→美国资源→美元根基，中段跨段拼接，非全链显式单句；详AR12逐边。')
audit_matrix=[dict(level='Technical Reusability',what_supported='本次回收通报',what_not_supported='长期成功率',claim_refs=['C001','X02']),dict(level='Operational Reusability',what_supported='没有同箭重复飞行数据',what_not_supported='稳定重复/快速周转',claim_refs=['M01']),dict(level='Economic Reusability',what_supported='主播成本优势判断与来源一般摊销说法',what_not_supported='本箭实际复用全成本',claim_refs=['C026','X09','M02','M03']),dict(level='Commercial Viability',what_supported='需求与国家计划解释',what_not_supported='实际客户、订单兑现、现金流和利润',claim_refs=['C058','C060','M04']),dict(level='Industry Transformation',what_supported='待检验Thesis',what_not_supported='持续产业结构变化',claim_refs=['C120','M05'])]
questions={
 'A_核心论证链':[
 'AR01/AR04：回收里程碑→追上主流→已低成本→商业想象空间。关键未证边为C001→C026。',
 'AR07/AR08：星链需求受融资约束；中国国家任务→供应链规模→成本优势→全球需求集中。融资观察可研究，数量和排他结果均未证。',
 'AR09/AR10/AR11：AI流动性退潮情景→国家信用融资；美债回购被解释为信用危机→中国技术规划更吸引资本。',
 'AR12/AR13：技术追赶→话语权与资本吸引力→汇率及美元根基；债务历史增量另被外推成2028预测。',
 'AR16：资本关注和商业公司→人才待遇→财富与新富豪；缺现金流及跨期产业证据。'],
 'B_事实解释推论三层':[
 dict(fact='X01/X02：来源报道具体发射回收',interpretation='C007/C009：举国研发及公私互补',structural_inference='C026/C060/C120：低成本、供应链强化、财富阶段；后两层未随事实自动验证'),
 dict(fact='X05：公司宣布试验积极结果；X04：媒体盘前行情',interpretation='C067：AI流动性推动，C111：昂贵所以利润小',structural_inference='C112/C114：估值不可持续；不能把临床结果当推论证据全部成立'),
 dict(fact='X06/X07：财政部宣布回购调整',interpretation='C073：没人买长债',structural_inference='C071/C074/C075：信用破产与信任迁移；此跨越不受公告直接支持')],
 'C_分析方法与稳定性':'需求付款者和融资来源、成本寿命、估值拒绝门槛是可观察操作。MR表只得partial/analogous，exact=0，尚不能称已验证稳定Skill。国内正向门槛包含国家任务与潜在规模，未看到复飞或现金流的必经审查。',
 'D_不能进入Verified_Knowledge':['C026：中国已经实现可比低成本','C044/C045：星链20万/200万','C061：全部全球需求归中国','C073：美债没人买','C105：私人公司特许牟利指控','C111：治疗昂贵必然低利润','C097：单一技术事件削弱美元根基','所有Forecast：只能入预测账本','X03：整箭实际20次复用从未被来源证明'],
 'E_Schema不足':'优先修复部件/系统能力范围、日期时区与版本、价格/成本/利润的角色转换、跨段推理图粒度、嵌套预测相关性、双observer以及recurrence精度。详IS01—IS16；未取得生产Schema，不声称通过生产导入验证。',
 'F_未来30期复用对象':dict(indicators=['同口径单位入轨成本I02（本期数值不可用）','星座规模I03（计划/许可/在轨严格分开）','部件复用能力I10（不要当整箭实飞数）'],mechanisms=['ME01需求规模成本','ME02技术可信度与融资条件','ME03寿命和使用成本'],theses=['TH01航天产业机会','TH02技术资本货币竞争（高推理距离）'],heuristic_candidates='本期新建0；优先跟踪MS02/MS03/MS04，审计MS07/MS08/MS09，不立即制作Analyst Skill。'),
 'G_技术Event到产业时代跨几跳':distance,
 'H_20次如何归类':'外部来源部件能力声称，design_target或engineering_estimate尚不能区分；既不是observed reuse count=20，也不是主播的Forecast。',
 'I_StructuralProcess判断':'0。可记录EV01/EV02两项不同技术事件，但缺一组可比的复用经济性及商业规模序列；TH01保留为观点。',
 'J_MethodGate':'支持其看好航天的是赶超、国家投资、产业潜力与资本人才反馈；需要什么数量的成本/客户证据才愿意接受，仍insufficient evidence。',
 'K_Reuters时间':'未确认原始页的published_at/updated_at。Investing显示Aug19 19:02与21:00但无时区；若为EDT则北京时间Aug20 07:02/09:00，可能在cutoff前，此仅条件换算，不能据此认定原页准入。也不能因较晚转载/照片日期就硬判原文post-cutoff。全部隔离不用于论证。'}
questions['F_未来30期复用对象']['mechanisms']=['ME01需求规模成本','ME02技术可信度与融资条件','GS004/ME02资本设备寿命成本（复用已有候选子路径）']
snapshot_map={'SRC-A':['gs005_initial_1.txt','GS005sources.txt'],'SRC-B':['GS005sources3.txt','article_2458013.json'],'SRC-C':['gs005_finalweb.txt','GS005sources3.txt'],'SRC-D':['gs005_finalweb.txt','GS005sources3.txt'],'SRC-E':['gs005_primary_search.txt','gs005_initial_1.txt'],'V01':['gs005_verified.txt'],'V02':['gs005_verified.txt'],'V03':['gs005_timecheck.txt'],'V04':['gs005_primary_search.txt'],'V05':['gs005_primary_search.txt','gs005_verified.txt'],'V06':['gs005_timecheck.txt'],'V07':['gs005_verified.txt'],'V08':['gs005_primary_search.txt']}
for s in sources:
 s['snapshot_refs']=['source_snapshots/'+p for p in snapshot_map.get(s['source_id'],[]) if (OUT/'source_snapshots'/p).exists()]
for v in versions:
 v['capture_hashes']=[dict(path=p,sha256=sha(OUT/p)) for p in SM[v['source_id']]['snapshot_refs']]
counts=dict(Claim=len(claims),CreatorClaim=sum(c['claim_id'].startswith('C') for c in claims),ExternalClaim=len(ext),ModelDiagnosticClaim=len(diag_specs),Argument=len(arguments),CreatorArgument=len(arguments)-1,ModelDiagnosticArgument=1,Mechanism=len(mechanisms),NewMechanismCandidate=2,ReusedMechanismCandidate=1,MechanismUsage=len(mechanism_usages),Thesis=len(theses),Forecast=len(forecasts),Scenario=len(scenarios),StructuralProcess=0,Contradiction=0,Heuristic=0,AnalystMethodSignal=len(methods),ReviewQueue=len(reviews),Source=len(sources),SemanticSegment=len(segments),SourceSegment=len(ss),RawCue=len(cues))
executive=dict(status='extraction_complete_review_pending',video_title='《第七百四五期》朱雀三号成功陆上回收，航空航天的好时代来了吗？',prompt_version='V0.3.1-MA.1 as supplied in V0.3.1-minor.md',knowledge_cutoff=CUT,recorded_at=None,publication_time_basis='user_authorized_prompt_not_independently_verified_platform_metadata',analysis_context='historical_reconstruction_and_method_observation',largest_uncertainty=['高风险ASR数字未听音','回收到经济复用与全球需求的推论证据不足','部分网页版本和Reuters时间资格未知'],core_structural_judgment='本期源材料支持具体技术Event的报道；主播据此提出产业机会与资本竞争Thesis，尚不支持已形成持续经济产业过程。',post_cutoff_contamination='未将已知截止后结果用于历史Claim/Argument；时间未知来源隔离。当前网页版本可能修订，不能宣称历史版本污染风险为零。',verified_knowledge_promotion='none_in_this_review_pass',audio_status='not_listened',cutoff_separation='原语料与外部核验分开；外部X不进入creator Argument；R注册表仅事后方法比较',counts=counts)
bundle={
 '01_EXECUTIVE_EXTRACTION_REPORT':executive,'02_SOURCES':sources,'03_SOURCE_VERSIONS':versions,
 '04_SOURCE_FAMILIES_ORIGIN_FAMILIES':dict(origin_families={f:[s['source_id'] for s in sources if f in s['origin_family_ids']] for f in sorted({f for s in sources for f in s['origin_family_ids']})},independence_policy='same-origin转载和ASR衍生不计独立证据'),
 '05_TRANSCRIPT_CORRECTIONS':corrections,'06_SOURCE_SEGMENT_ANNOTATIONS':annotations,'07_SEMANTIC_SEGMENTS':segments,'08_CLAIMS':claims,'09_CLAIM_OCCURRENCES':occ,'10_ACTORS':actors,'11_EVENTS':events,'12_STRUCTURAL_PROCESSES':[],'13_INDICATORS_OBSERVATIONS':dict(indicators=indicators,observations=observations),'14_POLICIES':policies,'15_EXPECTATION_SNAPSHOTS':expectations,'16_VERACITY_ASSESSMENTS':veracity,'17_NARRATIVE_ASSESSMENTS':narratives,'18_ARGUMENTS':arguments,'19_MECHANISMS':mechanisms,'20_MECHANISM_USAGE':mechanism_usages,'21_SCENARIOS':scenarios,'22_THESES':theses,'23_FORECASTS':forecasts,'24_CONTRADICTIONS':[],'25_CANDIDATE_HEURISTICS':[],'26_ANALYST_METHOD_SIGNALS':method_bundle,'27_REVIEW_QUEUE':{p:[r for r in reviews if r['priority']==p] for p in ['Critical','High','Medium','Low']},'28_SCHEMA_ONTOLOGY_EXTRACTION_ISSUES_FOUND':issues,'29_GOLDEN_SAMPLE_SUMMARY':counts,'final_questions':questions,'auxiliary':dict(source_segments=ss,argument_distance=distance,technical_to_industry_audit=audit_matrix,registry_search=registry_search,forecast_exclusions=['C005条件速度与很快不足可结算，留Scenario','C013/C014/C017/C018远期文明思辨，不作概率押注','C088声称以前预测过，未回填历史Forecast','X03工程能力不是20次已发生或主播未来判断'],contradiction_decision='none：没有建立双方长期目标约束持续互动且多Thesis多事件的结构性矛盾；论证错误/数字疑点不等于Contradiction。',coverage_policy='全639字幕块按16语义段覆盖；礼貌语、重复填充和修辞不另建Claim，重复以Occurrence保留。')}
# Referential and epistemic validation: meaningful data checks, not claims of factual verification.
errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
for c in claims:
 check(all(x in SSM for x in c['source_segment_refs']),c['claim_id']+' missing source segment')
 check(set(c['comparison_basis'])=={'comparison_type','baseline_period','baseline_value','delta_value','delta_unit'},c['claim_id']+' comparison fields')
 if c['claim_id'].startswith('C'):check(c['asserted_at'] is None,c['claim_id']+' fabricated speech time')
check(len({c['claim_id'] for c in claims})==len(claims),'duplicate Claim IDs')
check({v['claim_ref'] for v in veracity}==set(CM),'every Claim needs assessment')
for a in arguments:
 for cid in a['claim_refs']:check(cid in CM,a['argument_id']+' dangling claim')
 for e in a['steps']:check(e['from_claim'] in a['claim_refs'] and e['to_claim'] in a['claim_refs'],a['argument_id']+' edge outside nodes')
 if a['reasoner_id']==AN:check(all(n.startswith('C') for n in a['claim_refs']),a['argument_id']+' external/model contamination')
 check(bool(a['limitations']),a['argument_id']+' limitation absent')
for m in methods:
 check(all(n.startswith('C') for n in m['claim_refs']),m['signal_id']+' model diagnostic becomes method')
 for cid in m['claim_refs']:check(any(cid in AM[ar]['claim_refs'] for ar in m['argument_refs']),m['signal_id']+' evidence not in associated argument '+cid)
 if m['signal_type']=='failure_pattern':check(m['observed_reasoner_id']==AN and m['annotation_observer']==MO,m['signal_id']+' observer mixed')
for f in forecasts:check(CM[f['claim_ref']]['claim_type']=='forecast',f['forecast_id']+' type mismatch')
for u in mechanism_usages:check(u['mechanism_ref'] in {m['mechanism_id'] for m in mechanisms},u['usage_id']+' mechanism reference')
check({f['claim_ref'] for f in forecasts}=={c['claim_id'] for c in claims if c['claim_type']=='forecast'},'forecast Claim ledger coverage')
for t in theses:
 for tr in t['traceability']:check(tr['claim_id'] in AM[tr['argument_id']]['claim_refs'] and tr['source_segment_id'] in CM[tr['claim_id']]['source_segment_refs'] and SSM[tr['source_segment_id']]['source_id']==tr['source_id'],'thesis trace invalid')
check([n for s in segments for n in range(s['cue_start'],s['cue_end']+1)]==list(range(1,640)),'semantic coverage gaps')
validation=dict(status='passed' if not errors else 'failed',errors=errors,checks=['unique IDs','all claim source references','per-Claim veracity coverage','all Forecast claims in Ledger','no X/M in creator arguments','no model diagnostic in method evidence','all methods linked to arguments','failure dual-observer fields','Thesis→Argument→Claim→SourceSegment→Source','full 639 cue segmentation','Comparison Basis keys','no publication+offset absolute timestamps'],not_validated=['audio accuracy','all historical factual accuracy','production JSON Schema compatibility'],counts=counts)
save('golden_sample_005.json',bundle)
for name,obj in [('claims',claims),('sources',sources),('source_versions',versions),('source_segments',ss),('raw_cues',cues),('claim_occurrences',occ),('arguments',arguments),('forecasts',forecasts),('scenarios',scenarios),('analyst_method_signals',method_bundle),('method_recurrence',recurrence),('review_queue',reviews),('validation',validation)]:save(name+'.json',obj)
save('manifest.json',dict(created_at=NOW,inputs=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in [PROMPT,SRT,TXT]],snapshot_files=[dict(path=str(p.relative_to(OUT)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted((OUT/'source_snapshots').glob('*')) if p.is_file()],source_snapshot_note='web tool-return captures, not historical publisher archives',audio_review_performed=False))
report=['# MacroMind Golden Sample #005 — 朱雀三号\n',f'知识截止：{CUT}。状态：extraction_complete_review_pending。\n','本文件为完整可审计对象报告；先读 README.md 与下方核心回答可快速定位。主播原句保留在末尾 SourceSegment。数字和观点保留原归属，不做事实化修饰。\n']
for key,value in bundle.items():
 if key=='auxiliary':continue
 report.append('## '+key.replace('_',' ')+'\n')
 report.append('none\n' if value==[] else '```json\n'+json.dumps(value,ensure_ascii=False,indent=2)+'\n```\n')
report.append('## 附录：SourceSegment 原文与来源定位\n\n```json\n'+json.dumps(ss,ensure_ascii=False,indent=2)+'\n```\n')
report.append('## 附录：技术—产业证据层级\n\n```json\n'+json.dumps(audit_matrix,ensure_ascii=False,indent=2)+'\n```\n')
report.append('## 原始外部来源链接\n')
for s in sources:
 if s['location'].startswith('http'):report.append(f"- [{s['source_id']} {s['title']}]({s['location']}) — {s['read_status']}\n")
(OUT/'golden_sample_005_report.md').write_text('\n'.join(report),encoding='utf-8')
readme=f'''# Golden Sample #005 — 抽取导览

已按用户授权的 V0.3.1-minor.md（V0.3.1-MA.1）执行。知识截止为 **2026-08-20 10:37:33，北京时间**。状态：**抽取完成，人工复核未完成**。

提示文件确实止于第39节，未提供机器Schema；本次沿用前样本29节输出骨架，全部辅助字段和枚举扩展在IS01—IS16中显式说明。

## 最重要的发现

1. 本期首先把回收视为技术赶超和叙事竞争的里程碑，又直接推到已低成本、产业机会。最薄弱的一步是 **C001→C026：回收成功→已经低成本**。原推理保留，模型没有替他补成已证实的完整机制。
2. 已读国家航天局转载通报给出本次发射、着陆时间，但这与财联社任务报道主要同源，不能算多个独立验证。没有据此认定稳定复飞或经济复用。[任务通报](https://www.cnsa.gov.cn/n6758823/n6758838/c10768762/content.html)
3. “20次”属于外部报道的**着陆腿能力**；不是整箭已飞20次，也不是主播说过的数字。能力究竟是设计目标还是工程估计仍待核。[着陆腿报道](https://www.cls.cn/detail/2458013)
4. 融资、需求和成本是可见方法动作；对国内技术的正向门槛比对太空算力/药物的盈利审查宽。这是模型提出的待审Failure Signal，不能据单期认定稳定偏差。
5. 星链20万/200万、每克几百美元、涨190%/三倍、结尾35年均未擅改。**没有听音；不能把两份同源ASR视作相互印证。**
6. Reuters原URL读取失败。同题转载显示8月19日晚间时间但未给时区，不能自动认定截止后，也不能准入历史证据。详RQ05与问题K。

## 核心链与推理距离

- 技术线：回收→已低成本→商业空间，原始局部链2跳；跨段拼接到财富和新富豪为4跳，跨段连接显式标明模型整理。
- 产业线：国家任务/投资→供应链规模→成本优势→全球全部需求，需求兑现与排他性结果未证。
- 金融线：技术案例→资本故事吸引力→话语权→美国资源压力→美元根基，5跳的合并路径需要大量独立证据。
- DA01另列5个模型诊断门槛：重复运营、翻修及可靠性、同口径全成本、商业现金流、跨期产业观察。这不是主播表达过的五步。

## 数量

{counts['CreatorClaim']}条主播Claim，{counts['ExternalClaim']}条外部声明，{counts['ModelDiagnosticClaim']}条模型诊断；{counts['CreatorArgument']}条主播Argument另加1条诊断图；{counts['Mechanism']}个Mechanism Candidate、{counts['Thesis']}个Thesis、{counts['Forecast']}条Forecast、{counts['Scenario']}个Scenario、{counts['AnalystMethodSignal']}个Method Signal；{counts['ReviewQueue']}项Review。

机制中2个为本期新候选，1个复用Golden #004已有ME02的寿命—替换成本子路径，没有复制创建同一机制。

StructuralProcess、Contradiction、新Heuristic均为0。没有将候选方法升级为稳定Skill。跨样本exact匹配为0；partial和analogous分开保存。

## 文件

- [完整报告](golden_sample_005_report.md)：29节对象、全部问题回答、原文证据附录。
- [完整JSON](golden_sample_005.json)：机器可读全量对象。
- [方法信号](analyst_method_signals.json) / [复现匹配](method_recurrence.json)。
- [Review Queue](review_queue.json)：按优先级组织；Critical 4项优先听音与补证。
- [校验结果](validation.json)：引用与归属检查；不代表事实和音频全部验证。
- [输入及快照清单](manifest.json)：输入SHA256与抓取快照哈希。

本次不升级任何待核命题到Verified Knowledge，不使用截止后结果判定主播预测成败。网页核验能支持“某来源作出某声明”，不能抹去其时间、来源依赖或推理限制。
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
print(json.dumps(validation,ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
