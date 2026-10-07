import re,json,hashlib,collections
from pathlib import Path
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'golden_sample_004';OUT.mkdir(exist_ok=True)
BASE=Path(r'G:\BilibiliDown.v6.41.release\download\有何高见9527')
SRT=next(BASE.glob('*七百三四期*.srt'));TXT=next(BASE.glob('*七百三四期*.自动转写.txt'));MP4=next(BASE.glob('*七百三四期*.mp4'))
PROMPT=Path(r'G:\youhegaojian\prompt\V0.3.1.md')
CUT='2026-08-05T09:48:48+08:00';NOW=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
AN='analyst_youhegaojian9527';MO='model_gpt6';HC='historical_reconstruction';MD='model_diagnostic'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,o):(OUT/n).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
cues=[]
for block in re.split(r'\n\s*\n',SRT.read_text(encoding='utf-8-sig').strip()):
    ls=block.splitlines()
    if ls and ls[0].isdigit():
        a,b=ls[1].split(' --> ');cues.append(dict(cue_id=int(ls[0]),start=a,end=b,raw_text='\n'.join(ls[2:])))
assert len(cues)==767
def raw(a,b):return '\n'.join(c['raw_text'] for c in cues[a-1:b])
def bd(a,b):return dict(cue_start=a,cue_end=b,start=cues[a-1]['start'],end=cues[b-1]['end'])
sources=[];versions=[];families={}
def source(i,t,url,role,pub,fam,orig=None,read='body_read',typ='article'):
    v='V-'+i
    s=dict(source_id=i,title=t,location=str(url),source_type=typ,role=role,published_at=pub,recorded_at=None,captured_at=NOW,read_status=read,source_family_id=fam,origin_family_ids=orig or [fam],derived_from=[],independence='unknown',source_version_ref=v)
    if not str(url).startswith('http'):
        p=Path(url)
        if p.exists():s.update(sha256=sha(p),bytes=p.stat().st_size)
    sources.append(s)
    versions.append(dict(source_version_id=v,source_id=i,displayed_publication_time=pub,captured_at=NOW,historical_snapshot_available=False,version_mutation_risk=bool(str(url).startswith('http')),edited_at=None,cutoff_status='eligible_by_displayed_date' if pub else 'metadata_unknown',content_hash=s.get('sha256'),note='current tool-return capture, not historical HTML' if str(url).startswith('http') else 'local immutable input; hash tracked'))
    families.setdefault(fam,dict(family_id=fam,kind='source_family',members=[]))['members'].append(i)
    for f in orig or []:families.setdefault(f,dict(family_id=f,kind='origin_family',members=[]))['members'].append(i)
source('S01','原视频',MP4,'primary_corpus',CUT,'F9527',read='file_found_hashed_audio_not_reviewed',typ='video')
source('S02','自动转写原文',TXT,'transcript',None,'F9527',typ='asr')
source('S03','SRT原文',SRT,'timestamp_anchor',None,'F9527',typ='asr_subtitle')
for s in sources[1:3]:s.update(derived_from=['S01'],independence='same_origin')
source('S04','北美四朵云、卖铲人到用铲人','https://www.cls.cn/detail/2444783','user_supplied_reference','2026-08-04T09:38:00+08:00','FCLS_A',['FAMZN','FMSFT','FGOOG','FBROKER','FMARKET_UNKNOWN'])
source('S05','DeepSeek-V4-Flash成本比较','https://www.cls.cn/detail/2444045','user_supplied_reference','2026-08-03T15:12:00+08:00','FCLS_B',['FAA','FDEEPSEEK'])
source('S06','13州税收优惠政策进度','https://wallstreetcn.com/articles/3778569','user_supplied_reference','2026-08-03T16:40:00+08:00','FWSCN',['FTHEINFORMATION','FSTATE_POLICY_UNRESOLVED'])
source('S07','金融危机以来美债信号','https://www.cls.cn/detail/2434646','user_supplied_reference_not_observed_used_in_transcript','2026-07-23','FCLS_D',['FBOND_DATA_UNKNOWN'])
source('S08','何以解码中国共产党','https://www.qstheory.cn/20260715/1ebf8503161c448a9027393008f810f7/c.html','user_supplied_reference','2026-07-16T09:00:00+08:00','FQIUSHI')
source('S09','V0.3.1-MA任务提示',PROMPT,'user_authorized_instruction',None,'FPROMPT',typ='prompt')
source('S10','微软FY26Q4指标表','https://www.microsoft.com/en-us/investor/earnings/fy-2026-q4/metrics','model_supplement','2026-07-29','FMSFT')
source('S11','微软FY26Q4财报公告','https://www.microsoft.com/en-us/investor/earnings/fy-2026-q4/press-release-webcast','model_supplement','2026-07-29','FMSFT')
source('S12','亚马逊Q2财报公告','https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Second-Quarter-Results/default.aspx?mode=light','model_supplement','2026-07-30','FAMZN')
source('S13','Alphabet Q2公告SEC版本','https://www.sec.gov/Archives/edgar/data/1652044/000165204426000066/googexhibit991q22026.htm','model_supplement','2026-07-22','FGOOG')
source('S14','Artificial Analysis 0731评估','https://artificialanalysis.ai/articles/deepseek-v4-flash-0731-scores-50-on-the-artificial-analysis-intelligence-index-10-points-above-previous-deepseek-v4-flash','model_supplement','2026-07-31','FAA')
source('S15','GS001摘要（仅方法与注册表对比）',ROOT/'golden_report.md','method_recurrence_registry_only',None,'FREGISTRY_GS001',typ='prior_extraction_summary')
source('S16','GS002对象（仅方法与注册表对比）',ROOT/'golden_sample_002/golden_sample_002.json','method_recurrence_registry_only',None,'FREGISTRY_GS002',read='heuristics_and_registry_sections_read',typ='prior_extraction')
source('S17','GS003对象（仅方法与注册表对比）',ROOT/'golden_sample_003/golden_sample_003.json','method_recurrence_registry_only',None,'FREGISTRY_GS003',read='heuristics_and_registry_sections_read',typ='prior_extraction')
SM={s['source_id']:s for s in sources}
for s in sources:
    if s['source_id'] in ['S02','S03','S09']:next(v for v in versions if v['source_id']==s['source_id'])['cutoff_status']='instruction_or_same_video_derivative_not_independent_historical_fact'
segments=[]
topics=[(1,27,'开场与两题说明'),(28,84,'云股反弹与资金约束'),(85,129,'AWS超预期与90倍泡沫推算'),(130,166,'税收、电网与成本分支'),(167,174,'低价模型竞争'),(175,220,'国内应用与移动支付类比'),(221,243,'ROI、Azure、RPO与谷歌财报'),(244,312,'传统云模型、订单与硬件'),(313,345,'存量当增量的叙事诊断'),(346,370,'追涨者心理与反弹持续性'),(371,426,'折旧、回报与延长寿命'),(427,476,'手机类比与折旧跳升'),(477,520,'存量经营、共识与结论'),(521,562,'汇率救市类比及反弹结论'),(563,618,'鸿蒙智行公关目标'),(619,648,'投诉比例与时间分母'),(649,713,'路人视角、争取对象与历史类比'),(714,745,'组织约束、自省与求是引用'),(746,767,'频道方法自述与最终判断')]
for i,(a,b,t) in enumerate(topics,1):segments.append(dict(segment_id=f'SEG{i:02}',topic=t,source_id='S03',source_version_ref='V-S03',**bd(a,b)))
claims=[];ss=[];occ=[]
def add(n,a,b,k,t):
    cid=f'C{n:03}';sid='SS-'+cid
    ss.append(dict(source_segment_id=sid,source_id='S03',source_version_ref='V-S03',origin_family_ids=['F9527'],semantic_segment_refs=[s['segment_id'] for s in segments if s['cue_start']<=b and s['cue_end']>=a],raw_text=raw(a,b),**bd(a,b)))
    claims.append(dict(claim_id=cid,statement=t,claimant_id=AN,asserted_by_id=AN,attribution_chain=[AN],attribution_status='reported_only',claim_type=k,derivation_type='explicit_transcript',temporal_mode='future' if k=='forecast' else ('conditional' if k=='conditional_claim' else 'unknown'),asserted_at=CUT,asserted_at_basis='publication_proxy_recording_unknown',reference_time=None,knowledge_cutoff=CUT,population=None,quantifier=None,raw_quantifier=None,certainty_expressed=None,scope=t,condition_expression=None,source_segment_refs=[sid],atomicity_group_id=f'AG{a:03}',reasoner_id=AN,analysis_context=HC,corpus_origin='creator_transcript',verified_knowledge_eligible=False))
    occurrence(cid,a,b,'first','high')
def occurrence(cid,a,b,kind='restatement',gain='low'):
    occ.append(dict(occurrence_id=f'OC{len(occ)+1:03}',claim_id=cid,source_id='S03',source_version_ref='V-S03',origin_family_ids=['F9527'],surface_text=raw(a,b),occurrence_type=kind,information_gain=gain,**bd(a,b)))
rows='''1|1|1|reported_claim|主播称SpaceX财报亮眼。
2|1|2|interpretation|科技股此次反弹由亮眼财报推动。
3|33|33|reported_claim|贝索斯套现1500亿；币种与时间未给。
4|31|32|reported_claim|亚马逊前天收涨约4.5%。
5|33|33|reported_claim|亚马逊时隔61个交易日再创历史新高。
6|34|34|reported_claim|亚马逊总市值超过3万亿美元。
7|35|35|reported_claim|谷歌股价上涨超过4%。
8|35|35|reported_claim|微软股价上涨超过4%。
9|36|36|reported_claim|Meta股价上涨超过6%。
10|37|37|reported_claim|甲骨文单日上涨超过9%。
11|38|45|interpretation|相同谷歌财报既被解释为上周下跌原因又被解释为上涨原因。
12|43|49|interpretation|短期行情受解释权影响，但分析仍应从事实出发。
13|50|59|analogy|事实像地心引力，额外支撑消失后叙事不能无限维持。
14|75|84|interpretation|AI泡沫的根本约束是美国拿不出继续推升所需资金，此次反弹没有解决。
15|77|80|retrospective_claim|主播称去年及五月已测算过再涨20%需要难以承担的资金。
16|86|87|reported_claim|AWS二季度净销售422.3亿美元。
17|88|88|reported_claim|分析师此前预计AWS净销售405.7亿美元。
18|89|89|reported_claim|AWS营收增速创18个季度新高。
19|90|95|calculation|主播将销售额超过预期的幅度估作不到5%，差额约20亿美元。
20|96|118|interpretation|季度约5%的增量被一天约5%的股价上涨兑现，因此泡沫至少约90倍。
21|121|126|conditional_claim|若维持此增长叙事，下季须超预期更多；原转写数值为“3040亿5亿美元”。
22|131|137|reported_claim|美国13个州已经取消数据中心税收优惠。
23|134|134|conditional_claim|按相关税收变动测算，每GW数据中心成本可能增加30亿美元。
24|138|144|interpretation|数据中心扩张及电力需求波动已给民生和电网稳定带来压力。
25|145|153|interpretation|取消补贴是为升级电网和储能筹钱。
26|155|160|conditional_claim|若数据中心需求继续增长，额外运营及电网平衡收费将出现。
27|161|166|conditional_claim|能赚钱的数据中心会吸引更多利益相关方收费，成本增加将压低盈利。
28|167|167|reported_claim|美国研究机构评估DeepSeek V4 Flash运行成本约为Fable的1%。
29|168|168|conditional_claim|若数据中心成本难以维持，唯一选择是替换成最便宜模型。
30|168|172|conditional_claim|低价模型替换将降低数据需求量和单价，使此前投入为他人作嫁衣。
31|175|178|reported_claim|主播观察到国内AI应用已进入一线工程及现场分析。
32|179|179|reported_claim|部分一线应用使用免费的豆包等工具。
33|180|182|reported_claim|部分专业公司维护自己的模型，面向较单一场景。
34|183|193|interpretation|个人用消费级AI完成商业交付，意味着应用从C端向B端延展。
35|195|198|forecast|此类使用场景继续培育将带来整体生产力跃迁。
36|199|211|historical_analogy|AI习惯扩散类似移动支付改变消费和业态的过程。
37|213|217|interpretation|美国尚未实现这种广泛应用，云收入暴增不能证明已经实现。
38|218|220|reported_claim|部分分析者或观众认为云业务表现好给上涨提供了坚实基础；主播反对。
39|222|224|forecast|亚马逊CEO称距离服务器与网络设备投资盈亏平衡不到三年。
40|224|224|reported_claim|亚马逊CEO称AI投入回报的良性循环初步形成。
41|226|227|reported_claim|微软云计算业务收入同比增长43%。
42|228|228|reported_claim|分析师预期微软相关云业务增长39.98%。
43|229|229|calculation|主播把40%到43%的差描述为3%。
44|230|230|reported_claim|微软本季度末未交付订单额为6780亿美元。
45|230|230|reported_claim|微软上季度未交付订单额为6270亿美元。
46|231|232|calculation|主播估算微软未交付订单环比增加近500亿美元。
47|232|232|calculation|主播估算该未交付订单增速约10%。
48|233|237|conditional_claim|若要维持行情，亚马逊下次财报需从超预期5%变为10%。
49|238|240|reported_claim|谷歌云收入增长82%。
50|241|243|interpretation|整体市场正在形成云计算将很热门的预期。
51|245|263|historical_claim|云服务是运行十多年、甚至二十年的成熟商业模式。
52|247|255|interpretation|主播把SaaS解释为通过服务交付收费，并与租用算力的轻前端模式相联系。
53|256|258|reported_claim|这种业务会把合同金额约40%用于向云商购买服务。
54|264|273|interpretation|当前云业务主要是算力需求骤增且需求类型发生变化。
55|284|286|method_statement|应追问6780亿美元订单里有多少是传统业务原本就应交付的部分。
56|287|295|interpretation|未交付订单是云商有意储备、平滑需求波动的手段。
57|297|302|conditional_claim|举例需求增加三份只投两份硬件，可降低未来需求萎缩造成的过度投入损失。
58|303|310|interpretation|硬件损耗和淘汰应计入云服务成本。
59|313|324|interpretation|市场把应当算成本的固定投入或冗余准备讲成未来收入与旺盛需求。
60|329|337|interpretation|投资者把过去存量当成新增量，夸大增长预期。
61|337|345|interpretation|夸大预期让估值显得便宜，信息差会诱使不熟悉行业的人买入。
62|348|355|interpretation|前期亏损会促使投资者把反弹当成回本机会。
63|357|367|conditional_claim|无论追涨者跑早、碰巧成功还是跑晚，都可能强化下一次风险。
64|367|370|forecast|本轮反弹支撑不了多久，不能改变泡沫破裂趋势。
65|374|383|conditional_claim|云商硬件周期内收入超过折旧则赚钱，反之赔钱；这是主播的简化模型。
66|388|394|interpretation|算力卡面临技术更新淘汰和自然损坏两类折旧压力。
67|395|397|interpretation|当前折旧压力主要来自技术更新。
68|398|405|conditional_claim|拉长评估周期可降低当前财报中的折旧成本。
69|406|421|conditional_claim|用旧卡补充损坏算力并拉长周期，可使报表折旧更漂亮。
70|423|426|conditional_claim|折旧年限可以从三年到五年、七年，但无法无限延长。
71|430|437|personal_observation|主播拿旧iPhone 8比较，已开不了机，并以2016与2026作十年对照。
72|438|446|conditional_claim|若将算力卡周期拉长至七到十年，代际差距将迫使最终确认损失。
73|447|465|conditional_claim|旧卡无法继续补损后，以新卡价格替换会使资本支出及折旧成本上台阶。
74|471|472|forecast|折旧费用很快会迎来台阶式上升。
75|473|476|conditional_claim|费用跳升可能是数倍乃至十倍，从而重创盈利预期。
76|477|491|method_statement|存量行业需精算成本，追增量风口者可能忽略这些细账，导致扩展空间判断分歧。
77|492|498|interpretation|市场共识已出现裂痕，这会制造不稳定并限制持续上涨。
78|499|500|conditional_claim|没有上涨带来的赚钱效应，市场吸引力将下降并可能自我踩踏。
79|503|508|interpretation|本轮反弹缺乏业务变化、应用质变和长期真实需求支撑。
80|513|520|method_statement|主播要求上涨叙事拿出足够底层支撑，认为目前理由不足。
81|520|520|forecast|反弹迟早会回落，而且速度很快。
82|521|546|historical_analogy|本轮反弹类似美日联合汇率救市：花钱而效果不足、分歧出现后易反转。
83|563|565|value_judgment|主播认为鸿蒙智行此次公关回应是巨大灾难。
84|571|575|reported_claim|鸿蒙智行眼前的问题是销量下滑。
85|576|580|interpretation|销量下滑是既有粉丝已购买、消费潜力耗尽所致。
86|580|608|recommendation|品牌应通过柔和形象争取路人转粉，而非继续强化现有粉丝。
87|583|597|interpretation|此前针对粉丝的成功打法正在损害非粉丝观感。
88|609|618|interpretation|回应侧重法律和数据证明自己没错，没有服务修复路人观感的公关目的。
89|619|624|reported_claim|回应中称投诉约170多条。
90|621|621|reported_claim|回应所用总体内容规模为“55.5点几万条”；确切数值待音频。
91|624|628|estimate|主播估计早期总体相关内容仅几百至上千，170多条的当时占比可能很高。
92|635|639|interpretation|用后期膨胀的总量当分母稀释早期投诉比例，是不当时间口径比较。
93|629|642|interpretation|粗暴投诉触发口碑爆发，随后这种比例回应会进一步增加恶感。
94|649|653|method_statement|应暂时放下粉丝身份，以路人视角评估行为是在招黑还是扩大接受度。
95|662|668|conditional_claim|即使反感者中有小米粉丝，也不能把所有人当不可争取的敌人。
96|687|711|method_statement|提炼共同的主要问题，是为争取对手并把彼此冲突降为次要，而非单纯识别敌我。
97|679|708|historical_analogy|以抗日主线团结原本敌对力量的历史，类比品牌争取路人。
98|714|722|interpretation|粉丝把所有人视为敌人，与品牌破圈目标相反。
99|724|736|recommendation|品牌应承认问题；否认问题会使局面更差。
100|738|743|interpretation|余承东及团队不能接受失败，因此难以采取自嘲等柔和公关选择。
101|742|743|analogy|品牌组织内每步看似正确却整体变差，与美国困境相似。
102|744|745|reported_claim|主播推荐求是7月16日文章作为组织自我修正的参考。
103|746|747|personal_report|主播称在会员频道批评华为会损失付费会员，但仍选择表达真实想法。
104|748|749|method_statement|与其猜人物私心和未来行动，不如先找其所受限制，再据边界分析走势。
105|750|750|interpretation|主播认为按这些边界给出的情况只能被处理得更差，不会更好，称之为保下线。
106|751|751|personal_report|主播承认自身接收信息有限，不能全知或准确预知未来。
107|752|754|conditional_claim|不认可节目价值可能因为观众识别力不足，也可能因为水平高于主播；他说二选一。
108|761|765|forecast|主播悲观地认为华为难以纠正错误，因为尚未承认错误。'''
for line in rows.splitlines():
    n,a,b,k,t=line.split('|',4);add(int(n),int(a),int(b),k,t)
CM={c['claim_id']:c for c in claims}
def upd(n,**kw):CM[f'C{n:03}'].update(kw)
for n,actor,chain in [(16,'amazon',['amazon','S04',AN]),(17,'analysts_unknown',['analysts_unknown','S04',AN]),(18,'amazon',['amazon','S04',AN]),(28,'artificial_analysis',['artificial_analysis','S05',AN]),(39,'andy_jassy',['andy_jassy','S04',AN]),(40,'andy_jassy',['andy_jassy','S04',AN]),(41,'microsoft',['microsoft','S04',AN]),(42,'analysts_unknown',['analysts_unknown','S04',AN]),(44,'microsoft',['microsoft','S04',AN]),(45,'microsoft',['microsoft','S04',AN]),(49,'alphabet',['alphabet','S04',AN]),(89,'hima',['hima',AN]),(90,'hima',['hima',AN])]:
    upd(n,claimant_id=actor,attribution_chain=chain,derivation_type='secondhand_report')
for n,q in [(3,'1500亿'),(4,'4.5%吧'),(5,'61个交易日'),(6,'3万亿美元'),(7,'超4%'),(8,'超4%'),(9,'超6%'),(10,'超9%'),(16,'422.3亿美元'),(17,'405.7亿美元'),(18,'18个季度'),(19,'不到5%；多了20亿美元'),(20,'最少1比90；百倍左右'),(21,'3040亿5亿美元'),(22,'13个周'),(23,'每千兆瓦30亿美元'),(26,'板上钉钉指日可待'),(28,'1%'),(29,'唯一'),(39,'不到3年'),(41,'43%'),(42,'39.98%'),(43,'3%'),(44,'6780亿美元'),(45,'6270亿美元'),(46,'将近500亿美元'),(47,'10%'),(48,'5%到10%翻一翻'),(49,'82%'),(53,'40%左右'),(57,'三份；两份'),(70,'三年；五年；七年；70年'),(71,'2026；2016；iPhone8'),(72,'七年、十年'),(75,'10倍；几倍'),(89,'170多个'),(90,'55.5点几万'),(91,'几百条上千条'),(95,'所有'),(107,'两种；自选其一')]:upd(n,quantifier=q,raw_quantifier=q)
for n in [4,5,6,7,8,9,10]:upd(n,reference_time='前天；按发布日理解为2026-08-03，录制时点未知',temporal_mode='past')
for n in [16,18,41,44,49]:upd(n,reference_time='截至2026-06-30季度（源核对；财年口径不同）',temporal_mode='past')
upd(45,reference_time='上季度末',temporal_mode='past');upd(15,reference_time='去年及五月；原节目未取得',temporal_mode='past')
for n,a,b,k,g in [(14,79,84,'restatement','low'),(44,285,286,'elaboration','medium'),(51,280,283,'restatement','low'),(64,503,512,'summary','low'),(64,549,562,'summary','low'),(96,754,757,'elaboration','medium'),(86,599,608,'restatement','low')]:occurrence(f'C{n:03}',a,b,k,g)
# 分离同一句里的可独立核实子命题。
upd(19,statement='主播将AWS销售超预期幅度估作不到5%。')
add(109,92,95,'calculation','主播把AWS实际与预期销售差额粗估为20亿美元。')
upd(71,statement='主播称自己的旧iPhone 8已开不了机。')
add(110,427,441,'analogy','主播以2016到2026十年手机变化说明多年算力代际差距；提到iPhone 8，年份对应待核。')
upd(93,statement='主播认为早期投诉行为触发口碑与讨论量的爆发。')
add(111,640,648,'conditional_claim','被识破的比例小聪明会让公关受众更反感。')
upd(38,statement='部分分析者或观众认为云业务表现好给上涨提供坚实基础。',claimant_id='commenters_unknown',attribution_chain=['commenters_unknown',AN])
add(112,218,221,'interpretation','主播明确不接受用云业务表现好证明此轮上涨有坚实基础。')
# 外部证据仅作核查，绝不纳入主播Method Signal。
def external(cid,source_id,t,actor,locator,origin):
    seg='SS-'+cid
    ss.append(dict(source_segment_id=seg,source_id=source_id,source_version_ref='V-'+source_id,origin_family_ids=[origin],locator=locator,raw_text=None,paraphrase=t))
    c=dict(claim_id=cid,statement=t,claimant_id=actor,asserted_by_id=source_id,attribution_chain=[actor,source_id],attribution_status='source_verified',claim_type='source_claim',derivation_type='external_source',temporal_mode='past',asserted_at=SM[source_id]['published_at'],asserted_at_basis='displayed_source_date',reference_time=None,knowledge_cutoff=CUT,population=None,quantifier=None,raw_quantifier=None,certainty_expressed=None,scope=t,condition_expression=None,source_segment_refs=[seg],atomicity_group_id=cid,reasoner_id=MO,analysis_context=MD,corpus_origin='external_verification',verified_knowledge_eligible=False)
    claims.append(c);occ.append(dict(occurrence_id=f'OC{len(occ)+1:03}',claim_id=cid,source_id=source_id,source_version_ref='V-'+source_id,source_segment_ref=seg,origin_family_ids=[origin],surface_text=None,paraphrase=t,occurrence_type='first',information_gain='high'))
external('X01','S10','微软商业RPO是未履行合同的未来收入义务，不是已经投入的硬件资产成本。','microsoft','Commercial remaining performance obligation definition','FMSFT')
external('X02','S10','微软商业RPO FY26Q3为6270亿美元、Q4为6780亿美元。','microsoft','Q326/Q426 columns','FMSFT')
external('X03','S11','微软FY26Q4 Azure及其他云服务同比增长43%；不是全部Microsoft Cloud。','microsoft','Business Highlights','FMSFT')
external('X04','S12','亚马逊报告AWS二季度销售约422亿美元，同比增长约37%。','amazon','AWS results bullet','FAMZN')
external('X05','S13','Alphabet报告2026Q2 Google Cloud收入同比增长82%。','alphabet','headline results / Cloud','FGOOG')
external('X06','S06','报道区分四州取消或暂停与九州研究类似政策，不能统称13州已经取消。','the_information','开头政策进度','FTHEINFORMATION')
external('X07','S06','每GW约30亿美元是按7%销售税及设备购置规模估算的增量，不是年度通用运营费。','wscn','成本估算段','FTHEINFORMATION')
external('X08','S05','3美分与3.15美元比较的是指定智能指数任务的估算成本，不是整个数据中心成本。','artificial_analysis','任务成本段','FAA')
external('X09','S14','0731版本输入/输出Token价格不变，缓存折扣和任务Token使用影响成本比较。','artificial_analysis','Pricing / token usage','FAA')
external('X10','S04','新闻将云收入与订单改善解释为AI回报兑现信号，并使用卖铲到用铲的标题框架。','cls_editor','标题/ROI段','FBROKER')
external('X11','S08','文章强调组织自我检视与纠错；网页显示7月16日，URL含0715。','qiushi_author','日期/自省段','FQIUSHI')
models=[('M01','营收超预期转换成股价重估需利润率、持续性、未来现金流和折现率。'),('M02','市场价格反映未来多期现金流，不能用季度90天除以一天推出90倍高估。'),('M03','RPO转成AI增长证据需拆AI与传统业务、新签与续约、履约期限及取消条件。'),('M04','模型任务成本下降对云商利润的净效应取决于调用弹性、部署位置、采购价格和定价能力。'),('M05','延长会计折旧年限、资产经济寿命、减值测试及新购设备现金支出是不同变量。'),('M06','从盈利压力到市场必然暴跌仍需估值、预期差、流动性和时间触发条件。'),('M07','早期投诉分子与后期总量分母确实错位，需两组时间戳、覆盖群体和原始回应证明。'),('M08','由销量下降推出粉丝消费耗尽，需控制产品周期、交付、竞争和定价。')]
for cid,t in models:
    claims.append(dict(claim_id=cid,statement=t,claimant_id=MO,asserted_by_id=MO,attribution_chain=[MO],attribution_status='model_authored',claim_type='model_reconstruction',derivation_type='model_reconstruction',temporal_mode='analytical',asserted_at=NOW,asserted_at_basis='analysis_time',reference_time=None,knowledge_cutoff=CUT,population=None,quantifier=None,raw_quantifier=None,certainty_expressed=None,scope='诊断必要条件，不是主播说法',condition_expression=None,source_segment_refs=[],atomicity_group_id=cid,reasoner_id=MO,analysis_context=MD,corpus_origin='model_diagnostic',verified_knowledge_eligible=False))
CM={c['claim_id']:c for c in claims};SS={s['source_segment_id']:s for s in ss}
corrections=[]
for a,b,before,after,conf in [(1,1,'spaceX','保留SpaceX，不能凭常识改为其他公司','low'),(3,3,'红木之行','鸿蒙智行','high'),(33,33,'1500亿','数字币种保留待核','low'),(36,36,'没塔','Meta','high'),(56,56,'摇唇骨折','摇唇鼓舌','high'),(64,64,'粉丝太名','粉饰太平','high'),(124,124,'3040亿5亿美元','30/40/50亿美元？不应用','low'),(132,132,'13个周','13个州','high'),(166,167,'deeps / fiable','DeepSeek / Fable；来源支持语义，声学未知','medium'),(248,249,'SAS / 萨s','SaaS；不据此替换主播定义','high'),(559,559,'诱度','诱多','high'),(620,621,'170多个 / 55.5点几万','保留待听音及官方回应核对','low'),(738,738,'于成东','余承东','high'),(740,740,'竹治料','unknown，不猜具体梗','low')]:
    corrections.append(dict(correction_id=f'TC{len(corrections)+1:02}',**bd(a,b),raw_text=raw(a,b),raw_form=before,proposed_normalized_form=after,status='needs_audio_review',semantic_confidence=conf,acoustic_confidence='unknown',applied=False))
annotations=[]
for a,b,t,n in [(47,49,'rhetorical_exaggeration','“真相不重要”紧接“分析从真相开始”，不是主播放弃事实'),(90,118,'mixed_fact_and_opinion','收入数、超预期、日股价与90倍泡沫推断分开'),(166,166,'self_correction','营收成本改为运营成本；仅文字层可见'),(285,324,'ambiguous_reference','从未交付订单转向冗余硬件成本，对象可能偷换'),(430,437,'needs_audio_review','2016/十年/iPhone8并列，不能确认主播真实口误'),(620,638,'ambiguous_reference','170及55万的时点/集合未经原文证实'),(742,742,'self_correction','每一步“都是错”改为“都是对”'),(748,750,'ambiguous_reference','“保下线”与只能更差的界限方向不清')]:annotations.append(dict(annotation_id=f'AN{len(annotations)+1:02}',annotation_type=t,**bd(a,b),note=n,speaker_slip_confirmed=False))
actors=[dict(actor_id=i,name=n) for i,n in [(AN,'有何高见9527'),(MO,'抽取模型'),('amazon','亚马逊'),('andy_jassy','安迪·贾西'),('microsoft','微软'),('alphabet','Alphabet/谷歌'),('meta','Meta'),('oracle','甲骨文'),('nvidia','英伟达'),('spacex','SpaceX'),('bezos','杰夫·贝索斯'),('artificial_analysis','Artificial Analysis'),('deepseek','DeepSeek'),('anthropic','Anthropic'),('huawei','华为'),('hima','鸿蒙智行'),('yu_chengdong','余承东'),('xiaomi','小米'),('analysts_unknown','未具名分析师集合'),('commenters_unknown','主播转述的观众集合'),('the_information','The Information'),('wscn','华尔街见闻'),('cls_editor','财联社/科创板日报编者'),('qiushi_author','冀永义'),('us_states','美国州政府集合')]]
events=[]
def event(i,t,refs,ann=None,status='reported_only'):
    events.append(dict(event_id=i,statement=t,claim_refs=refs,decision_at=None,announced_at=ann,scheduled_at=None,effective_at=None,occurred_at=None,status=status))
event('EV01','亚马逊发布二季度财报',['C016','X04'],'2026-07-30','primary_release_observed')
event('EV02','微软发布FY26Q4财报',['C041','C044','X01','X03'],'2026-07-29','primary_release_observed')
event('EV03','Alphabet发布Q2财报',['C049','X05'],'2026-07-22','primary_release_observed')
event('EV04','一组科技股上涨',['C004','C007','C008','C009','C010'],status='reported_market_move_date_relative')
event('EV05','鸿蒙智行发表回应',['C083','C088','C089','C090'],status='creator_report_original_statement_not_retrieved')
event('EV06','AA发布0731评估',['X09'],'2026-07-31','primary_evaluation_publication')
event('EV07','美国州税收政策异步调整/研究',['C022','X06'],status='aggregate_mixed_stage_not_single_effective_event')
# 四期数据存在并不自动证明技术商业化结构变化；只记录必要对照点，不强造Process。
indicators=[];observations=[]
def ob(cid,name,val,unit,mt,period=None,den=None,status='reported',currency=None,group=None,numerator=None):
    iid=group or f'IN{len(indicators)+1:02}'
    if not any(x['indicator_id']==iid for x in indicators):indicators.append(dict(indicator_id=iid,name=name,measurement_type=mt,definition_status='partial' if period is None else 'specified_as_reported'))
    observations.append(dict(observation_id=f'OB{len(observations)+1:02}',indicator_id=iid,claim_ref=cid,value=val,unit=unit,currency=currency,measurement_type=mt,value_status=status,numerator=numerator,denominator=den,gross_net='unknown',period_basis='unknown' if period is None else period,reference_period=period,released_at=CM[cid]['asserted_at'],vintage_at=None,classification_version=None,source_segment_refs=CM[cid]['source_segment_refs'],definition_caveat='按原命题口径，不将报道自动改成已验证观测'))
for n,name,val,unit,mt in [(3,'贝索斯套现金额',1500,'亿；币种未知','amount'),(4,'亚马逊单日股价变动',4.5,'%','growth_rate'),(5,'距前高交易日',61,'交易日','count'),(6,'亚马逊市值',3,'万亿美元','stock'),(7,'谷歌单日股价变动','>4','%','growth_rate'),(8,'微软单日股价变动','>4','%','growth_rate'),(9,'Meta单日股价变动','>6','%','growth_rate'),(10,'甲骨文单日股价变动','>9','%','growth_rate')]:ob(f'C{n:03}',name,val,unit,mt)
ob('C016','AWS季度净销售',422.3,'亿美元','flow','2026Q2',currency='USD')
ob('C017','AWS季度净销售共识',405.7,'亿美元','flow','2026Q2',status='estimated',currency='USD')
ob('C019','AWS收入超共识幅度','约5','%','ratio',den='预期销售405.7亿美元',numerator='实际减预期',status='calculated')
ob('C109','AWS销售超预期差额','约20','亿美元','amount',status='calculated',currency='USD')
ob('C020','主播估算泡沫倍数',90,'倍','ratio',den='一天',numerator='一季度约90天',status='estimated')
ob('C022','称已取消优惠州数',13,'州','count')
ob('C023','税收变化设备成本影响',30,'亿美元/GW','amount',status='projected',currency='USD')
ob('C028','DeepSeek对Fable任务成本比','约1','%','ratio',den='Fable指定评测成本',status='reported')
ob('C039','公司预期投资回本剩余时间','<3','年','level',status='projected')
ob('C041','Azure与其他云收入增速',43,'%','growth_rate','FY26Q4同比')
ob('C042','Azure增速共识',39.98,'%','growth_rate','FY26Q4同比',status='estimated')
ob('C043','主播所述增长率差',3,'%（原话）','amount',status='calculated')
ob('C044','微软商业RPO期末余额',6780,'亿美元','stock','FY26Q4末',currency='USD',group='IN_RPO')
ob('C045','微软商业RPO期末余额',6270,'亿美元','stock','FY26Q3末',currency='USD',group='IN_RPO')
ob('C046','RPO环比增额','近500','亿美元','amount',status='calculated',currency='USD')
ob('C047','RPO环比增速','约10','%','growth_rate',den='上季6270亿美元',status='calculated')
ob('C049','Google Cloud收入增速',82,'%','growth_rate','2026Q2同比')
ob('C053','合同金额中云采购比例',40,'%','share',den='客户合同金额')
ob('C075','设想折旧费上升倍数','数倍至10','倍','ratio',den='此前折旧费用',status='projected')
ob('C089','回应所称投诉数量','170多','条','count')
ob('C090','回应所称相关内容量','55.5点几万','条','count')
ob('C091','主播估计早期内容量','几百至上千','条','count',status='estimated')
calculations=[dict(calculation_id='CAL01',input_claim_refs=['C016','C017'],formula='(422.3-405.7)/405.7*100',value=(422.3-405.7)/405.7*100,unit='%',meaning='销售超共识幅度，非同比增长；沿用转写输入条件计算',reasoner_id=MO),dict(calculation_id='CAL02',input_claim_refs=['C016','C017'],formula='422.3-405.7',value=422.3-405.7,unit='亿美元',meaning='16.6不等于20；近似幅度需保留',reasoner_id=MO),dict(calculation_id='CAL03',input_claim_refs=['C041','C042'],formula='43-39.98',value=43-39.98,unit='百分点',meaning='不是3.02%的营收增量',reasoner_id=MO),dict(calculation_id='CAL04',input_claim_refs=['C044','C045'],formula='(6780-6270)/6270*100',value=(6780-6270)/6270*100,unit='%',meaning='约8.13%，环比RPO余额增长',reasoner_id=MO)]
policies=[dict(policy_id='PO01',claim_refs=['C022','X06'],name='美国数据中心州税优惠调整集合',status='mixed_proposed_paused_cancelled',announced_at=None,effective_at=None,jurisdiction='multiple_states_unresolved',limitation='未取得13州逐项法规，不把研究/暂停/附加条件合并为生效取消')]
expectations=[dict(expectation_snapshot_id='EX01',as_of=CUT,observer=AN,population='主播泛指美股云投资者，未给样本',target='cloud_prospects',expectation='云业务会变得热门',claim_refs=['C050'],evidence_type='creator_inference_not_survey'),dict(expectation_snapshot_id='EX02',as_of='2026Q2财报发布前，具体日期未知',observer='analysts_unknown',population='AWS销售一致预期提供者未明',target='AWS_Q2_sales',expectation=405.7,unit='亿美元',claim_refs=['C017'],evidence_type='reported_consensus')]
assessments=[]
for c in claims:
    k=c['claim_type'];cid=c['claim_id']
    assessments.append(dict(assessment_id='VA-'+cid,claim_ref=cid,observer=MO,assessed_at=NOW,knowledge_cutoff=CUT,veracity='unverifiable' if k in ['value_judgment','recommendation'] else 'uncertain',scope='命题内容，不是只核实说过此话',evidence_refs=[],counterevidence_refs=[],independent_source_family_count=0,origin_family_ids=[],limitations='文字证据可追溯；不自动证明现实、因果或未来。',verified_knowledge_eligible=False))
VA={a['claim_ref']:a for a in assessments}
def assess(cid,status,note,refs=[],orig=[],counter=[]):
    VA[cid].update(veracity=status,limitations=note,evidence_refs=refs,counterevidence_refs=counter,independent_source_family_count=len(set(orig)),origin_family_ids=orig)
for cid in ['C044','C045']:assess(cid,'likely_true','金额与公司商业RPO一致；视频云业务标签过宽。确认公司披露值，不证实其缓冲硬件解释。',['S10'],['FMSFT'])
assess('C041','likely_true','43%对应Azure及其他云服务，不是整个Microsoft Cloud；后者另有口径。',['S11'],['FMSFT'])
assess('C049','likely_true','公司公告给出Google Cloud同比82%；不等于AI独立收入或ROI。',['S13'],['FGOOG'])
assess('C016','uncertain','官方概览约422亿美元支持量级；本次未锁定422.3的明细精度。',['S12'],['FAMZN'])
assess('C018','likely_true','公司公告称18季度最高增速，新闻与公告同源不加计。',['S12'],['FAMZN'])
assess('C017','uncertain','新闻把预期405.7写为“亿元”，转写为亿美元；原共识数据未取得，不能悄悄改新闻币种。',['S04'])
assess('C019','likely_true','按视频两个美元数计算约4.09%，确实不到5%；只是条件算术，不能核实输入数据。',['CAL01'])
assess('C109','disputed','按视频精确数差16.6亿美元，20是较粗近似。',['CAL02'])
assess('C020','false','90天/1天不能作为估值倍数估计器；此判定仅针对推导有效性，不断言市场不存在泡沫。',counter=['M01','M02'])
VA['C020']['scope']='derivation_validity_only_not_market_valuation_truth'
assess('C022','disputed','参考文为4州取消/暂停加9州研究，不能由此证明13州均已取消。',counter=['X06'])
assess('C028','uncertain','新闻1%是指定任务成本比；AA正文确认价格与缓存因素，但本次未在其正文找到3美分对3.15完整表。',['S05','S14'],['FAA'])
assess('C043','disputed','差为3.02个百分点，不能与营收超预期百分比直接对比。',['CAL03'])
assess('C047','disputed','按6270基数是8.13%，不是精确10%。近似不能支持下一季必须翻倍。',['CAL04'])
assess('C056','uncertain','RPO定义证明有待履约合同，不能证明公司刻意拖延来管理产能。',counter=['X01'])
assess('C059','disputed','合同收入义务与固定硬件投入不同；原话指代有歧义，需听音确认是否偷换。',counter=['X01','M03'])
assess('C084','uncertain','未取得同品牌同口径销量序列；销量下降本身和原因都未核。')
assess('C085','uncertain','粉丝购买耗尽只是解释；不能由总销量下降排除产品、交付和价格因素。',counter=['M08'])
assess('C092','uncertain','时间分母检查是合理动作；实际分子分母是否错位仍须原回应和传播时间线。',counter=['M07'])
for cid in ['X01','X02','X03','X04','X05','X09']:
    s=SS[CM[cid]['source_segment_refs'][0]];assess(cid,'verified','仅核实公开文件中的定义或所披露数值；不传播到商业化/市场方向。',[s['source_id']],s['origin_family_ids']);VA[cid]['verified_knowledge_eligible']=True
for c in claims:c['verified_knowledge_eligible']=VA[c['claim_id']]['verified_knowledge_eligible']
narratives=[dict(assessment_id='NA01',observer='cls_editor',source_refs=['S04'],claim_refs=['X10'],frame='卖铲到用铲；云收入/订单被作为回报兑现信号'),dict(assessment_id='NA02',observer=AN,claim_refs=['C055','C059','C064','C112'],frame='拒绝将成熟云业务重新包装成新行情充分基础；转向存量订单、折旧与持续资金约束',acceptance='承认财报增长与上涨，拒绝由此推出新一轮行情'),dict(assessment_id='NA03',observer=MO,claim_refs=['C019','C020','C059'],frame='质疑叙事是实际动作，但90倍与RPO成本化仍需独立审计'),dict(assessment_id='NA04',observer=AN,claim_refs=['C083','C086','C096'],frame='用是否促进破圈/争取对象评判品牌公关')]
arguments=[]
def arg(i,title,edges,conclusion,weak,lim,shortcuts=None,analogy=None,reasoner=AN):
    steps=[];nodes=set();inc=collections.Counter();adj=collections.defaultdict(list)
    for j,(f,t,l,m,limit) in enumerate(edges,1):
        nodes.update([f,t]);inc[t]+=1;adj[f].append(t)
        steps.append(dict(step_id=f'{i}-E{j}',from_claim_refs=[f],to_claim_ref=t,relation='SUPPORTS_CONDITIONALLY',inference_mode=m,expression_level=l,reasoner_id=MO if l=='model_reconstruction' else reasoner,analysis_context=MD if l=='model_reconstruction' or reasoner==MO else HC,evidence_refs=CM[f]['source_segment_refs']+CM[t]['source_segment_refs'],limitations=limit))
    q=collections.deque(n for n in nodes if not inc[n]);dist={n:0 for n in nodes};visited=0
    while q:
        f=q.popleft();visited+=1
        for t in adj[f]:
            dist[t]=max(dist[t],dist[f]+1);inc[t]-=1
            if inc[t]==0:q.append(t)
    assert visited==len(nodes)
    cnt=collections.Counter(e['expression_level'] for e in steps)
    a=dict(argument_id=i,title=title,premises=sorted(nodes-{e['to_claim_ref'] for e in steps}),steps=steps,conclusion=[conclusion],reasoner_id=reasoner,analysis_context=HC if reasoner==AN else MD,inference_mode=sorted(set(e['inference_mode'] for e in steps)),expression_level=sorted(cnt),inferential_distance=dict(edge_count=len(steps),longest_path_length=max(dist.values()),model_bridge_count=cnt['model_reconstruction'],explicit_shortcut_count=len(shortcuts or []),strongly_implied_edge_count=cnt['strongly_implied'],explicit_edge_count=cnt['explicit']),limitations=lim,most_fragile_step=weak,creator_shortcuts=shortcuts or [],claim_refs=sorted(nodes),distance_scope='代表性审计展开图，不声称唯一完整认知路径')
    if analogy:a.update(argument_type='historical_analogy',**analogy)
    arguments.append(a)
E='explicit';I='strongly_implied';M='model_reconstruction'
arg('AR01','收入超预期与90倍估值推导',[('C016','C019',E,'statistical','必须与同币种共识比较'),('C017','C019',E,'statistical','新闻币种有冲突'),('C019','C020',E,'speculation','营收惊喜不能除以价格反应时间'),('C004','C020',E,'speculation','股价是未来现金流重估，不是一日收入'),('C020','C021',E,'speculation','超预期必须不断加倍缺估值模型')],'C021','AR01-E3','量纲错误及期间混淆；5%不是AWS同比增长，更不是整个公司利润增速。',[dict(from_claim='C019',to_claim='C020',description='约5%超预期→90倍泡沫')])
arg('AR02','税收和电网成本限制盈利',[('C024','C025',E,'causal','电网压力不证明取消税惠所得被专款用于电网'),('C025','C026',E,'causal','地方差异与政策阶段未明'),('C026','C027',E,'causal','需固定收入和成本转嫁等条件')],'C027','AR02-E1','4+9政策阶段不同；30亿美元是设备成本条件估算，不能直接计年度运营费。')
arg('AR03','廉价模型威胁云商收益',[('C028','C029',E,'causal','任务账单比不等于同质服务总成本'),('C029','C030',E,'causal','低价模型可增加调用而非只压缩收入'),('C030','M04',M,'causal','部署位置与需求弹性缺资料'),('M04','C064',M,'speculation','净效应未知，不能确认反弹失败')],'C064','AR03-E2','模型能力、API价格、每任务成本、硬件成本和云商收入不同层，不能替换。')
arg('AR04','传统订单、增量与新叙事',[('C051','C055',E,'direct','成熟不等于没有新增需求'),('C044','C055',E,'direct','总额需要分解'),('C055','C056',E,'speculation','提出问题不能证明刻意延期'),('C056','C059',E,'causal','RPO与硬件成本对象转移'),('C059','C060',E,'causal','尚未计算实际存量/增量'),('C060','C061',E,'causal','没有市场投资者认知测量'),('C061','C064',I,'speculation','高预期不自动决定下跌时点')],'C064','AR04-E4','“有多少传统订单”是合理问题；但未经拆分便归为成本冗余和骗局，结论过强。')
arg('AR05','硬件寿命、替换与盈利台阶',[('C066','C067',E,'causal','技术淘汰压力相对自然故障的量级未测'),('C067','C068',E,'causal','未指明哪家真的改变年限'),('C068','C069',E,'causal','旧GPU补位须兼容并有可用存量'),('C069','C072',E,'causal','生命周期场景不是明确财报政策事实'),('C072','C073',E,'causal','减值、折旧、采购现金流区别未处理'),('C073','C074',E,'speculation','成本跳升时间缺资产批次与采购价'),('C074','C075',E,'speculation','数倍十倍没有测算'),('C075','M06',M,'causal','盈利变化不等于股价必然同幅变化'),('M06','C064',M,'speculation','需预期差及定价条件')],'C064','AR05-E7','观察成本结构可复用；3/5/7年是举例，十倍是可能值，非公司已披露改折旧事实。',[dict(from_claim='C074',to_claim='C064',description='折旧压力→反弹不可持续')])
arg('AR06','习惯扩散与生产力类比',[('C031','C034',E,'causal','个案不能量化全国采用'),('C034','C035',E,'analogy','效率改善没有产出质量与劳动投入对照'),('C036','C035',E,'analogy','移动支付和AI经济机制不同')],'C035','AR06-E2','应用可观察线索不等于已经发生全社会生产率跃迁。',analogy=dict(source_case='移动支付习惯扩散',target_case='AI应用向商业交付扩散',shared_mechanism='使用习惯扩散可能改变流程和业态',limits_of_analogy='成本、可靠性、组织整合、监管与渗透路径不同'))
arg('AR07','共识与赚钱效应的反身性',[('C060','C077',I,'causal','未测实际共识分布'),('C077','C078',E,'causal','分歧并不必然阻止上涨'),('C078','C064',E,'speculation','可能负反馈不代表必然马上回落')],'C064','AR07-E3','须区分“若不涨”条件与“必然跌”的分支选择。')
arg('AR08','品牌增长约束与公关目标',[('C084','C085',E,'causal','销量下降有多个竞争解释'),('C085','C086',E,'causal','目标市场和粉丝渗透率未测'),('C087','C088',I,'causal','公众反应缺样本'),('C088','C098',E,'causal','品牌/粉丝/公司主体不同'),('C098','C108',I,'speculation','当前做法不能证明无法纠错')],'C108','AR08-E1','没有销量序列和用户构成数据；公关目的判断不能代替事实核查。')
arg('AR09','时间分母与投诉比例',[('C089','C091',E,'statistical','当时总体规模是估计'),('C090','C092',E,'statistical','后期分母时间尚未核'),('C091','C092',E,'statistical','需确认同一内容集合'),('C093','C092',I,'causal','传播增长是否投诉所致未知'),('C092','C111',E,'causal','识破后的受众反应未测')],'C111','AR09-E3','可观察到检查分母的分析动作，但结论缺原回应和同时间口径数据。')
arg('AR10','共同目标、对手转化与组织约束',[('C097','C096',E,'analogy','历史政治联合与商业公关不是同一决策空间'),('C096','C086',E,'causal','共同目标是否被路人接受未证'),('C100','C108',E,'causal','团队内部动机未取得独立材料')],'C108','AR10-E3','规范性“应当”与现实“能否”分开；主要矛盾是观察者的战略Assessment。',analogy=dict(source_case='抗日背景下争取原本敌对力量',target_case='品牌争取路人/竞争品牌用户',shared_mechanism='以共同目标减少对立并扩大支持',limits_of_analogy='战争组织、国家目标与消费者选择的约束不同，不能证明公关效果'))
arg('AR11','以约束边界代替人物预测',[('C106','C104',E,'direct','信息有限支持谨慎，不证明边界已完整'),('C104','C105',E,'speculation','约束并不自动给出可证明的最好或最坏结果')],'C105','AR11-E2','这是方法自述，不等于每次实际分析都遵守；“只能更差”可能忽略创新和政策改变。')
# 单独给模型诊断图，不能变成9527的方法。
arg('DA01','财报到新行情必须跨过的条件（模型审计）',[('C041','M03',M,'direct','先拆AI贡献、新旧订单及真实需求'),('M03','M04',M,'causal','再看采用弹性和价格/工作量'),('M04','M05',M,'causal','核总成本、经济寿命和现金投入'),('M05','M01',M,'causal','核利润率、持续现金流与估值'),('M01','M06',M,'causal','最后核预期差和市场触发')],'M06','DA01-E5','五个诊断环节为模型补充；不声称主播提出或赞同这些完整判准。',reasoner=MO)
arg('AR12','技术寿命的手机类比',[('C110','C072',E,'analogy','手机十年变化不能定量给GPU折旧率')],'C072','AR12-E1','设备负载、替换需求和残值不同，不能由类比推出数倍成本。',analogy=dict(source_case='手机十年代际差异',target_case='算力卡七至十年经济寿命',shared_mechanism='小的年度差异可累积成显著代际差距',limits_of_analogy='不能给出GPU寿命、兼容性及减值比例；iPhone年份待听音'))
arg('AR13','救市效果不足与反弹类比',[('C082','C064',E,'analogy','汇率救市和云股估值不是相同干预机制')],'C064','AR13-E1','前期节目与救市原始材料未核，类比只留有限机制。',analogy=dict(source_case='主播所称美日联合汇率救市',target_case='云股反弹',shared_mechanism='投入与效果失配可能破坏预期协同',limits_of_analogy='政策主体、价格工具、资产现金流不同'))
arg('AR14','拒绝新故事的本期判断门槛',[('C112','C080',E,'direct','不接受外部结论之后要求给出支撑'),('C079','C080',E,'direct','业务与需求无质变的断言尚未证明'),('C080','C064',E,'speculation','未见足够证据支持上涨不等于证明必然下跌'),('C014','C064',E,'causal','持续资金不足未量化')],'C064','AR14-E3','可恢复拒绝门槛，但不可补成完整买入/看多规则；仍有从证据不足到反向确定性的跳跃。')
arg('AR15','追涨结果的分支解释',[('C062','C063',E,'causal','回本动机不能证明所有投资者均有同样心理')],'C063','AR15-E1','早退、幸运与晚退均可讲成负面，会降低可反证性；这里只登记原文明示的情景组织。')
arg('AR16','路人视角与争取对象',[('C094','C086',E,'direct','视角切换有助于设问，不能直接量化销售效果'),('C096','C086',E,'analogy','共同目标是否成立需受众研究')],'C086','AR16-E2','这是主播使用的规范性分析动作，原文没有给出实践转化率。')
AM={a['argument_id']:a for a in arguments}
mechanisms=[dict(mechanism_id='ME01',status='canonical_candidate_not_promoted',name='投入品税负/公共配套成本向项目回报传导',nodes=['税负或费用变化','边际成本变化','回报变化'],limitations='收入不变及不能完全转嫁时方向才明确',claim_refs=['C026','C027'],argument_refs=['AR02']),dict(mechanism_id='ME02',status='canonical_candidate_not_promoted',name='资本设备经济寿命与回收期错配',nodes=['技术迭代/损坏','剩余可用年限','替换支出与成本确认','现金回收压力'],limitations='会计折旧与经济寿命要分开',claim_refs=['C065','C066','C073'],argument_refs=['AR05']),dict(mechanism_id='ME03',status='canonical_candidate_not_promoted',name='价格回报与资金吸引力反馈',nodes=['预期回报','新增资金参与','价格','预期反馈'],limitations='可以正反馈也可以负反馈，不能自动选方向',claim_refs=['C062','C077','C078'],argument_refs=['AR07'])]
usages=[dict(usage_id=f'MU{i:02}',analyst_id=AN,mechanism_ref=m['mechanism_id'],expression_level='explicit',reasoner_id=AN,analysis_context=HC,claim_refs=m['claim_refs'],argument_refs=m['argument_refs'],source_segment_refs=[s for c in m['claim_refs'] for s in CM[c]['source_segment_refs']],qualification='只归因原文明确使用部分，不把模型补足条件视为主播动作') for i,m in enumerate(mechanisms,1)]
scenarios=[]
scenario_rows=[('C021','维持相同估值增长叙事','下季需要更多超预期收入','数值断裂；是必要条件论述非未来收入预测'),('C023','税惠取消且设备采购适用约7%销售税','每GW设备成本增加约30亿美元','外部成本测算，非全行业已发生值'),('C026','数据中心业务持续增长','额外运营/电网平衡收费','强情态但州、时间和收费标准未明确；候选预测不入正式ledger'),('C027','项目获利吸引收费且不能转嫁','盈利受挤压','机制性IF-THEN'),('C029','成本无法维持','采用更便宜模型','唯一选择断言需审计'),('C030','采用廉价替代且需求不补偿','量价及既有收益受压','原话未控制弹性；净方向未定'),('C048','继续维持炒作节奏','超预期幅度从5变10','不是下季收入将增长10%的预测'),('C057','需求增三份且只投资两份','未来萎缩时降低过投风险','举例'),('C063','追涨者跑早/碰巧成功/跑晚','各分支都可能增加下次风险','分支讨论不当成逐项未来事件'),('C065','周期收入大于或小于折旧','赚或赔','利润简化遗漏其他成本'),('C068','延长会计评估年限','当前折旧费用降低','方法举例不是已发生公司政策'),('C069','旧卡可兼容补损','报表与支出压力暂缓','物理可行性未证'),('C070','年限反复延长','最终仍有淘汰极限','边界讨论'),('C072','七至十年技术差距累积','必须确认部分损失','不是指定年份必然巨亏'),('C073','旧设备不可用且需按新品价补足','资本支出/成本上升','合约及采购价未知'),('C075','发生折旧跳升','可能数倍或十倍','无概率/窗口测算；不建十倍预测'),('C078','缺乏赚钱效应','吸引力下降及踩踏风险','不能视为无条件崩盘'),('C095','反感者中包含竞争品牌用户','仍可分层争取','规范性反事实'),('C107','观众不认可价值','可能能力不足或高于主播','二分并不穷尽其他原因'),('C111','受众识破不当比例比较','公关效果变差','未测受众反应')]
for i,(cid,cond,out,note) in enumerate(scenario_rows,1):
    CM[cid]['condition_expression']=cond
    scenarios.append(dict(scenario_id=f'SC{i:02}',claim_refs=[cid],reasoner_id=AN,analysis_context=HC,condition_expression=cond,outcome=out,branch_probability=None,branch_selected=False,source_segment_refs=CM[cid]['source_segment_refs'],forecast_admission='not_admitted',reason=note))
forecasts=[]
for cid,target,direction,window,mod,typ,reasoner in [('C035','整体生产力','跃迁','培育一段时间；未知','likely','unconditional',AN),('C039','服务器及网络投资盈亏平衡','距回本不足三年','从CEO发言起不足三年，发言日期未核','likely','unconditional','andy_jassy'),('C064','本轮科技股反弹/泡沫','反弹不持久且不能逆转破裂趋势','支撑不了多久；未知','near_certain','branch_selection',AN),('C074','算力折旧费用','台阶式上升','很快；未知','likely','unconditional',AN),('C081','科技股反弹','回落速度很快','迟早；未知','near_certain','unconditional',AN),('C108','华为纠错','难以纠正','未知','likely','branch_selection',AN)]:
    c=CM[cid]
    forecasts.append(dict(forecast_id='FC-'+cid,claim_id=cid,forecaster_id=reasoner,reasoner_id=reasoner,analysis_context=HC,ledger_type=typ,made_at=c['asserted_at'] if cid!='C039' else None,made_at_basis='video publication proxy' if cid!='C039' else 'original CEO speech time not verified; video secondary report at cutoff',knowledge_cutoff=CUT,target=target,direction=direction,prediction_window=window,conditions=c['condition_expression'],modal_strength=mod,original_modality=SS[c['source_segment_refs'][0]]['raw_text'],resolvability='medium' if cid=='C039' else 'low',admission_reason='明确方向承诺或分支选择，不仅是讨论IF-THEN',resolution_criteria=dict(creator_specified=window,model_proposed='预先锁定指标/对象、基期、期限和阈值；回本需明确资产批次与现金流口径。',human_approved=None,accepted_for_scoring=False),evaluation_status='not_scored'))
    c['reference_time']=window
theses=[]
registry=dict(scope='local_only',searched=['golden_report.md','golden_sample_002/golden_sample_002.json','golden_sample_003/golden_sample_003.json'],limitation='部分既有样本晚于本期，只作Registry/Method比较；不补入历史InformationSet。')
for i,t,arids,decision,need in [('TH01','9527认为当前云财报与订单叙事不足以启动新一轮行情，资金及成本约束仍占主导。',['AR01','AR03','AR04','AR05','AR07'],'related','跟踪真实AI收入、利润、现金流、资产寿命和估值；若持续新增现金回报且成本受控，应更新。'),('TH02','9527认为品牌扩张受既有粉丝打法与内部纠错约束影响，需要改变争取对象的方式。',['AR08','AR09','AR10'],'new','需品牌销量/客群/公关反应与组织行动的跨期证据；目前不证明长期结构冲突。')]:
    traces=[]
    for arid in arids:
        for cid in AM[arid]['claim_refs']:
            for seg in CM[cid]['source_segment_refs']:traces.append(dict(argument_id=arid,claim_id=cid,source_segment_id=seg,source_id=SS[seg]['source_id'],source_version_ref=SS[seg]['source_version_ref'],origin_family_ids=SS[seg]['origin_family_ids']))
    theses.append(dict(thesis_id=i,statement=t,reasoner_id=AN,analysis_context=HC,status='candidate_unverified',resolution=decision,resolution_provisional=True,registry_search=registry,argument_refs=arids,traceability=traces,followup_support_and_falsification=need))
method_signals=[]
def signal(i,typ,text,cids,ars,why,lim,trans='potentially_general',level=E,rec='first_observation',prior=None):
    method_signals.append(dict(signal_id=i,analyst_id=AN,reasoner_id=AN,analysis_context=HC,annotation_observer=MO,signal_type=typ,statement=text,source_segment_refs=[s for c in cids for s in CM[c]['source_segment_refs']],argument_refs=ars,claim_refs=cids,expression_level=level,domain='AI/cloud and brand/organization analysis' if typ in ['attention_pattern','question_pattern'] else '本期相应讨论域',transferability=trans,recurrence_status=rec,matched_prior_signal_refs=prior or [],confidence='high_textual_evidence_not_method_validity',why_this_is_method_not_conclusion=why,limitations=lim,promotion_status='observed_candidate_only_not_skill_rule'))
signal('MS01','attention_pattern','先问叙事维持所需资金、持续运行成本和可执行边界，再判断新闻解释是否足够。',['C014','C080','C104'],['AR14','AR11'],'原文明确说明选择变量的次序，并在云成本及末尾自述重复。','不是已经证明资金约束无解，也不能推断所有未来视频均如此；GS001仅摘要可比，不能声称逐句复核。',rec='repeated',prior=['GS003/HC01','GS001/summary:结构力量优先于政治人物'])
signal('MS02','question_pattern','追问总量中的旧业务和新贡献，并检查比较数字的分母及发生时间。',['C055','C091','C092'],['AR04','AR09'],'分别向云订单与投诉比例提出口径问题，是对证据的操作。','没有证据证明其得到的拆分答案正确；也不等同GS002完整的增量看趋势存量看空间。')
signal('MS03','mechanism_usage','把资本设备寿命与周期回报匹配作为云业务能否赚钱的检查点。',['C066','C072','C073'],['AR05'],'检查资本回收与成本的方式可以跨资本密集行业使用。','只归因原文明确部分；会计/经济折旧的完整区分来自模型审计；与前期仅成本/周期子动作复现。',trans='domain_specific',rec='repeated',prior=['GS003/HC02'])
signal('MS04','judgment_pattern','本期不把财报超预期和股价反弹作为充分证据，要求能解释持续上涨的业务、应用及需求支撑。',['C079','C080','C112'],['AR14'],'出现了接受或拒绝叙事的条件式判断动作。','只观察到拒绝门槛；没有足够证据恢复一套何时愿意买入/相信故事的完整政策。')
signal('MS05','analogy_pattern','用成熟技术习惯与设备代际变化解释新技术的扩散和寿命边界。',['C036','C110'],['AR06','AR12'],'在两处使用跨案例共享机制，不只是重复结论。','类比不证明同幅生产率提升、同寿命或同折旧金额。',trans='potentially_general')
signal('MS06','failure_pattern','从季度与日度时间比直接推90倍泡沫，未提供估值模型。',['C019','C020'],['AR01'],'可明确定位的量纲/推导动作缺陷；未来可检查是否重复。','标注者是模型；记录的是显式原文跳跃，不把M01/M02补全当主播方法；尚非稳定失败模式。',trans='unknown')
signal('MS07','question_pattern','暂时转换为非粉丝视角，并围绕增长目标判断是否在争取可转化人群。',['C086','C094','C096'],['AR16'],'是问题选择及观察位置的改变，适用于解释公关选择。','主张能争取不等于实际转化有效；政治联合类比有边界。',trans='potentially_general')
signal('MS08','branching_pattern','把追涨后的跑早、侥幸成功、跑晚分别展开，但都归入下一次风险增加。',['C063'],['AR15'],'观察到组织不确定性的方法，而非逐项预测未来结果。','分支结果全导向同一结论，有封闭解释风险；不能据此证明穷尽或稳定方法。',trans='unknown')
method_groups=dict(analyst_id=AN,attention_patterns=[],question_patterns=[],evidence_preferences=[],mechanism_usage_signals=[],branching_patterns=[],judgment_patterns=[],analogy_patterns=[],falsification_patterns=[],failure_patterns=[])
typekey={'attention_pattern':'attention_patterns','question_pattern':'question_patterns','evidence_preference':'evidence_preferences','mechanism_usage':'mechanism_usage_signals','branching_pattern':'branching_patterns','judgment_pattern':'judgment_patterns','analogy_pattern':'analogy_patterns','falsification_pattern':'falsification_patterns','failure_pattern':'failure_patterns'}
for m in method_signals:method_groups[typekey[m['signal_type']]].append(m)
recurrence=[dict(candidate='A 公开叙事后看执行能力/约束',status='repeated',prior_refs=['GS003/HC01'],current_refs=['MS01'],scope='同类分析动作，主题与具体结论不同'),dict(candidate='B 增量看趋势、存量看空间',status='unclear',prior_refs=['GS002/HC01'],current_refs=['MS02'],scope='本期有存量/增量拆分，但未观察到存量推潜在空间的完整规则，不能硬判复现'),dict(candidate='C 分阶段比较持续成本与承受能力',status='repeated',prior_refs=['GS003/HC02'],current_refs=['MS03'],scope='本期把硬件使用周期与回报对比；只复现成本/周期子模式，不含上期60天算法')]
heuristics=[] # Method Signal不自动晋升；既有candidate只做引用匹配。
reviews=[]
def rq(sev,typ,refs,issue,action):reviews.append(dict(review_id=f'RQ{len(reviews)+1:03}',severity=sev,review_type=typ,target_refs=refs,issue=issue,required_action=action,status='open'))
rq('Critical','excessive_inference',['C020','AR01','MS06'],'以90天/1天得90倍泡沫，量纲与估值对象错误。','保留原推理；用正式现金流/估值模型另审，不能改写成主播做过。')
rq('Critical','measurement_definition',['C056','C059','AR04'],'RPO从合同义务被转成成本/硬件冗余。','核原声指代和订单说明；将合同存量、收入、产能、CapEx分开。')
rq('Critical','model_reconstruction_leakage',['DA01','MS01','MS02','MS03','MS04','MS05','MS06','MS07','MS08'],'DA01条件链不能成为9527方法训练正样本。','校验Method只引用creator Claim与对应显式/强蕴含动作，保留标注者身份。')
rq('High','source_conflict',['C022','X06','PO01'],'13州已取消与4取消/暂停+9研究不一致。','逐州官方法案、阶段、生效时间；不能把政策研究当完成。')
rq('High','measurement_definition',['C023','X07'],'30亿美元/GW是设备税负情景，不是通用年度AI运营成本。','保存税率、设备基数、州和更新周期。')
rq('High','numerical_conflict',['C016','C017','C019','C109'],'销售额精度与新闻共识币种不一致，差额被粗估20。','读取公司明细及原共识数据；不能静默修复新闻“亿元”。')
rq('High','measurement_definition',['C041','C042','C043','C044','C045','C047'],'Azure、Microsoft Cloud、商业RPO范围不同；百分点/百分比/环比混用。','按公司指标定义单列，3.02个百分点和8.13%仅条件计算。')
rq('High','unsupported_claim',['C003'],'贝索斯套现1500亿缺币种、时间及交易材料。','查原声明/申报并听音，不依据市值推套现额。')
rq('High','asr_uncertain',['C001','TC01'],'SpaceX财报名称未核。','回听首20秒并核指定财报；不能自动改成Tesla。')
rq('High','asr_uncertain',['C021','TC07'],'3040亿5亿美元无法可靠解析。','回听06:08–06:17；未确定数值不得做Observation点估计。')
rq('High','measurement_definition',['C028','C029','C030','X08','X09'],'任务成本1%不等于硬件、云商总成本或等能力替换。','锁模型版本/任务/缓存/能力/Token量，再评估调用弹性。')
rq('High','argument_bridge',['C029','C030','AR03'],'唯一选择与量价同时下降没有替代路径比较。','检查效率促进需求的相反分支，不替主播补为已说。')
rq('High','measurement_definition',['C065','C068','C069','C073','M05'],'折旧、减值、资本支出、现金盈利混为一层。','区分资产批次、经济寿命、会计估计与总运营成本。')
rq('High','unsupported_claim',['C069','C074','C075'],'旧GPU替补兼容性、折旧很快跳升及数倍十倍无测算。','取得设备结构和资产政策；幅度仅情景，不建十倍预测。')
rq('High','unsupported_claim',['C084','C085','M08'],'未核同口径销量与粉丝渗透，不能验证下降原因。','查截止前月度交付、车型/价格/用户结构。')
rq('High','attribution_chain',['C083','C088','C089','C090','C091','C092'],'原公关回应和传播序列未取得。','找到原版本、分子分母时间和覆盖集合；方法动作与事实结论分别评估。')
rq('High','unsupported_claim',['C100','C108'],'组织不能接受失败等动机来自主播推测。','区分可见行为、内部动机和未来纠错；不升级为组织事实。')
rq('High','forecast_lineage',['C015','C082','C108'],'去年、五月、星期一、半年前预测未得原节目。','不要反填历史Forecast；核原版本与时间。')
rq('High','scenario_forecast_confusion',['C026','C075','C078'],'强情态条件句也不自动入正式ledger。','SC03等列候选，补可判定触发/结果/窗口后人工决定。')
rq('High','forecast_lineage',['FC-C035','FC-C039','FC-C064','FC-C074','FC-C081','FC-C108'],'窗口或指标普遍不足，回本预测原发言时间未锁。','预注册判准；禁止用截止后的市场结果回填。')
rq('Medium','source_dependency',['S04','S10','S11','S12','S13'],'新闻多公司起源混合，官方转述不能再算独立支持。','使用片段origin family，不把同一财报算双源。')
rq('Medium','source_conflict',['S04','S05','S06','S07','S08','S10','S11','S12','S13','S14'],'当前网页不是cutoff历史快照。','保留version_mutation_risk；剔除动态推荐、后续版本，不宣称消除全部污染风险。')
rq('Medium','analyst_attribution',['S07','X10'],'美债资料和卖铲/用铲标题不能被默认为主播显式机制。','原片未搜到美债/收益率/债券/卖铲/用铲；语义阅读也未发现利率链。')
rq('Medium','speaker_slip_review',['C071','C110','TC14'],'2016十年类比与iPhone8并列、竹治料等ASR不清。','回听后区分口误与机器错字。')
rq('Medium','method_signal_overreach',['MS01','MS03','MS04','MS08'],'复现是有限子动作，拒绝门槛非完整判断政策，单期分支非稳定风格。','跨样本反例检验；不写成以后所有新闻都如此分析。')
rq('Medium','premature_heuristic_promotion',['MS01','MS02','MS03','MS04','MS05','MS06','MS07','MS08'],'方法信号不等于已验证Heuristic/Skill。','本期新增CandidateHeuristic=0，保留未来复现和审查。')
rq('Medium','process_boundary',['TH01','TH02'],'两季度余额或一次反弹不足证明AI商业化及品牌结构过程。','积累按同口径跨期数据并定义结构变量后再建Process。')
rq('Medium','mechanism_duplication',['ME01','ME02','ME03'],'没有完整共享机制库。','只建共享候选和Usage，入库前查重，不创建9527专属复制机制。')
rq('Medium','unsupported_claim',['C031','C032','C033','C035','C037'],'国内工程使用的个人观察不能代表总体渗透，更不能证明美国未实现。','补案例、分母、生产率评估及对照。')
rq('Medium','measurement_definition',['C053'],'合同40%购买云服务缺对象和行业分布。','核具体项目；不可作为云行业统一成本率。')
rq('Medium','method_signal_overreach',['C105','C107'],'只能更差和观众二选一可能封闭解释。','保留为单次推理薄弱点，未升级稳定failure_pattern。')
rq('Low','asr_uncertain',[x['correction_id'] for x in corrections if x['semantic_confidence']=='high'],'名称与术语语义可纠，但未听音。','候选与raw并存，accepted=0。')
reviews.sort(key=lambda r:['Critical','High','Medium','Low'].index(r['severity']))
issues=[]
for cl,p,fix in [('schema_field_issue','增长率、超预期比例与百分点需要不同measurement语义','Observation增加comparison_basis与numerator/denominator，金额币种不得推定。'),('auxiliary_object_issue','Scene与Forecast准入还需保留强情态但不可判定的候选','Scenario保存asserted_modality/commitment及admission_reason；不强行转正式预测。'),('schema_field_issue','RPO合同、产能、资产和费用之间对象容易偷换','标注accounting_role/recognition_stage/scope，保持14核心对象。'),('auxiliary_object_issue','failure_pattern的标注者和被观察推理者不同','保存annotation_observer=model与reasoner_id=analyst，原边必须可追溯。'),('registry_issue','关系、Claim类型与机制无完整机器注册表','本包为局部候选注册值；正式入库前映射，不宣称生产Schema验证。'),('prompt_issue','标题聚焦云平台而视频后半为品牌公关，给定美债材料未见使用','覆盖全片并区分user_supplied、creator_used与model_supplement；不硬造利率Mechanism。'),('schema_field_issue','同期不同企业/业务范围不可加总','保留company、segment、period_basis、currency及origin_family_ids。'),('auxiliary_object_issue','方法复现可能只是先前规则的一部分','recurrence保留matched_scope/partial而不只布尔；较晚样本只比方法不补历史。'),('core_ontology_issue','本期未发现必须新增核心对象的反复重要概念','保留14核心对象；Scenario/MethodSignal/MechanismUsage均用既有辅助层。')]:issues.append(dict(issue_id=f'IS{len(issues)+1:02}',classification=cl,problem=p,proposal=fix,new_core_object_required=False))
questions={
'A Core Arguments':'AR01：收入超预期→90倍泡沫；AR04：传统云/RPO→存量被包装成增量；AR05：硬件寿命/折旧→盈利压力→反弹难持续；AR03：低价模型→替换与量价压力；AR09：投诉分子分母时点→公关比例失真。前四条构成云题主线，最后一条提供另一域的方法证据。',
'B 四层分离':[
dict(topic='云财报',Observed_Reality='已读取公司公告，核实披露行为和定义；并非独立审计其全部经营事实。',Source_Claim='微软Azure增43%、商业RPO6780；新闻将其解释为AI回报兑现。',Analyst_Interpretation='旧业务/存量被当增量，市场过度解释。',Thesis_Forecast='TH01 / C064；前提披露真实不证明这一预测正确。'),
dict(topic='模型成本',Observed_Reality='AA公开了0731评估及Token价格说明。',Source_Claim='新闻比较的是任务成本，AA说明缓存及Token用量。',Analyst_Interpretation='低价替代会迫使云商降量降价，为他人作嫁衣。',Thesis_Forecast='支持TH01的条件场景SC05/06，不是已经验证的云利润崩溃。'),
dict(topic='税惠',Observed_Reality='本次未逐州读取法规，政策实际生效范围仍未知。',Source_Claim='报道为4州取消/暂停，9州研究；设备购置税负估算。',Analyst_Interpretation='13州已取消，是电网成本转嫁的开端。',Thesis_Forecast='成本压利润支持TH01；额外收费列Scenario，未将所有条件句入Forecast。'),
dict(topic='公关',Observed_Reality='没有取得官方回应原始版本及内容流量底表。',Source_Claim='主播转述170多投诉与55万量级总体。',Analyst_Interpretation='后期分母稀释早期分子，并违背破圈目标。',Thesis_Forecast='TH02及C108尚不能Verified。')],
'C 卖铲人→用铲人':'这是SRC-A新闻标题框架。转写没有逐字使用“卖铲/用铲”，但主播明确回应并反对“云业绩好→本轮上涨坚实”。他承认云增长和AI工作负载变化，重新聚焦成熟租赁业务、存量合同与成本；不能写成接受“切换已经完成”。',
'D 变量分离':dict(creator_explicit=['销售/超预期','单日股价','未交付订单存量与增量','税惠与电网费用','低价模型替换','使用场景','硬件迭代/故障/折旧周期','持续资金与赚钱效应','公关分母/时点/目标受众'],model_diagnostic=['AI与传统收入拆分','任务质量/缓存/部署位置','需求价格弹性','现金流与会计折旧/减值分开','利润率及边际回报','履约期限与取消条款','预期差和估值折现','可反证的窗口阈值']),
'E StructuralProcess':'本期不建立。RPO有Q3/Q4对照，证明一个可比余额变动，不足以单独证明AI商业化/云平台崛起。国内应用属未给时点/分母的个人观察。AA同价且任务Token变化也不能推全行业成本下降。新闻多州进度缺逐州有效事件，不强造结构过程。',
'F Scenario vs Forecast':'动态数量见第29节。正式预测只收方向承诺或分支选择；条件机制、设备举例、可能十倍与需要超预期翻倍不计预测。这落实了新版分离规则，但未做同一语料V0.3对照实验，不能声称量化证明误判率下降。',
'G Argument Distance':'AR05是最长代表性链：9边，其中2条模型边；“折旧上升→反弹不能持续”是显式捷径。用户指定的“云收入→AI商业化→新行情”在本期是主播质疑的外部叙事，不能伪作主播正向推导。DA01单独摊开5个模型诊断环节：收入订单拆分→需求弹性→全成本/寿命→现金流估值→预期差与触发。',
'H Mechanism':'ME01税费到成本回报、ME02设备寿命和回收期错配、ME03回报与资金反馈可作为共享候选，另存9527 Usage。90倍、13州全取消、十倍折旧、贝索斯套现和单次公关不建机制。缺全库Registry，canonical仅候选而非已审核。',
'I Method Signals':'8条：Attention MS01；Question MS02与MS07；Mechanism Usage MS03；Judgment MS04；Analogy MS05；Failure MS06；Branching MS08。Evidence Preference不建立稳定偏好：本期虽引用财报，后又强调底层逻辑、不从数据得结论，不能据单片宣称偏爱现金流。Falsification Pattern=none，未见清楚的可操作推翻条件。',
'J 复现性':recurrence,
'K Specific vs General':'MS01/02/04/05/07可能跨域；MS03偏资本密集行业；MS06/08目前transferability=unknown。没有证据证明这些规则仅9527独有，所以不为突出个性硬标analyst_specific。',
'L Model Leakage Audit':'none detected in structured Method Signal refs：没有M前缀Claim、DA01或model_reconstruction边被用作方法证据。Failure由模型标注，但所观察的是C020的显式动作；不等于模型桥接成为方法。',
'M Judgment Policy':'insufficient evidence。可见拒绝单靠股价/财报/RPO的门槛，并要求业务/应用/需求真实变化；没有明示达到哪些可测阈值就相信新故事。不能补成“收入+利润+订单就买入”的规则。',
'N Failure Signals':'正式单次候选MS06为90倍量纲跳跃。另记录待追踪但不升级：RPO成本化、API任务成本到整个云利润、涨幅必须越来越超预期、所有交易分支均通向坏结果、销量到粉丝耗尽、只会更差边界、观众二选一。不同意市场结论本身不算失败模式。',
'O Core Ontology Stability':'No。本次需要字段、准入状态、来源起源及方法标注者的细化，未发现必须新增核心对象。也未生成9527 Skill。'}
tests=[('股价≠产业结构','C004/TH01分开，Process=0'),('Cloud≠AI收入','C041/X03限定Azure范围，未生成AI收入值'),('AI使用≠ROI','C031/35与C039/40分开'),('模型成本≠全经济成本','X08与AR03/M04诊断分开'),('CapEx≠未来利润','未凭投入创建利润已增长Claim'),('季度财报≠长期Process','仅记录RPO余额对照'),('标题≠主播判断','NA01与NA02分别观察者'),('模型补全≠Method','DA01与M01–M08不进入方法证据'),('公司结构不可加总','AWS、Azure、Microsoft商业RPO、Google分开'),('能力价格成本回报估值分开','Observation和Argument逐层区分；未给变量不补值')]
stress=[dict(test_id=f'T{i:02}',test=t,status='pass_with_review_limits',evidence=n) for i,(t,n) in enumerate(tests,1)]
sumtypes=collections.Counter(f['ledger_type'] for f in forecasts);mc=collections.Counter(m['signal_type'] for m in method_signals)
summary=dict(source_count=len(sources),source_family_count=len(set(s['source_family_id'] for s in sources)),origin_family_count=len(set(f for s in sources for f in s['origin_family_ids'])),claim_count=len(claims),creator_claim_count=sum(c['corpus_origin']=='creator_transcript' for c in claims),model_diagnostic_claim_count=len(models),external_verification_claim_count=11,claim_occurrence_count=len(occ),actor_count=len(actors),event_count=len(events),structural_process_count=0,indicator_count=len(indicators),observation_count=len(observations),argument_count=len(arguments),creator_argument_count=sum(a['reasoner_id']==AN for a in arguments),model_diagnostic_argument_count=1,mechanism_count=len(mechanisms),mechanism_usage_count=len(usages),scenario_count=len(scenarios),thesis_count=len(theses),forecast_count=len(forecasts),unconditional_forecast_count=sumtypes['unconditional'],conditional_forecast_count=sumtypes['scenario_conditional'],branch_selection_forecast_count=sumtypes['branch_selection'],creator_forecast_count=sum(f['forecaster_id']==AN for f in forecasts),attributed_company_forecast_count=sum(f['forecaster_id']!=AN for f in forecasts),contradiction_count=0,candidate_heuristic_count=0,method_signal_count=len(method_signals),method_signal_counts={k:mc[k] for k in typekey},review_queue_count=len(reviews),review_severity_counts=dict(collections.Counter(r['severity'] for r in reviews)))
executive=dict(status='extraction_complete_review_pending',knowledge_cutoff=CUT,recorded_at=None,post_cutoff_contamination=dict(encountered=True,used_in_historical_reconstruction=False,residual_risk='当前网页抓取不能排除未披露修改，保留version_mutation_risk。',excluded='AA/见闻页尾8月下旬及9月推荐、搜索后期模型与市场结果'),major_uncertainties=['未听音，accepted correction=0','SpaceX、套现额、数字断裂及投诉规模待核','原公关声明、13州法案和共识原始数据未取得','RPO成本化、90倍推导及折旧台阶是主要审计断点'],core_structural_judgment='主播拒绝以当前云财报启动新行情的充分性，重选资金/存量/折旧变量；这属于待验证判断，尚非产业结构事实。',audio_review_performed=False,method_extraction_scope='8条单次/有限复现信号，不晋升Heuristic或Analyst Skill',coverage='全片767 cues，含29分钟后品牌公关及方法自述',independent_evidence_count_rule='按每Claim起源家族计数；文件数量与独立支持数不同')
sections=[('01_EXECUTIVE_EXTRACTION_REPORT',executive),('02_SOURCES',sources),('03_SOURCE_VERSIONS',versions),('04_SOURCE_FAMILIES_ORIGIN_FAMILIES',list(families.values())),('05_TRANSCRIPT_CORRECTIONS',dict(accepted=[],candidate_corrections=corrections,needs_audio_review=[x['correction_id'] for x in corrections])),('06_SOURCE_SEGMENT_ANNOTATIONS',annotations),('07_SEMANTIC_SEGMENTS',segments),('08_CLAIMS',claims),('09_CLAIM_OCCURRENCES',occ),('10_ACTORS',actors),('11_EVENTS',events),('12_STRUCTURAL_PROCESSES',[]),('13_INDICATORS_OBSERVATIONS',dict(indicators=indicators,observations=observations,model_calculations=calculations)),('14_POLICIES',policies),('15_EXPECTATION_SNAPSHOTS',expectations),('16_VERACITY_ASSESSMENTS',assessments),('17_NARRATIVE_ASSESSMENTS',narratives),('18_ARGUMENTS',arguments),('19_MECHANISMS',mechanisms),('20_MECHANISM_USAGE',usages),('21_SCENARIOS',scenarios),('22_THESES',theses),('23_FORECASTS',forecasts),('24_CONTRADICTIONS',[]),('25_CANDIDATE_HEURISTICS',heuristics),('26_ANALYST_METHOD_SIGNALS',method_groups),('27_REVIEW_QUEUE',reviews),('28_SCHEMA_ONTOLOGY_EXTRACTION_ISSUES_FOUND',issues),('29_GOLDEN_SAMPLE_SUMMARY',summary)]
data=dict(sections);data['final_questions']=questions
data['auxiliary']=dict(source_segments=ss,method_recurrence=recurrence,stress_tests=stress,information_set=dict(knowledge_cutoff=CUT,included_source_versions=['V-'+s['source_id'] for s in sources if s['role'] not in ['user_authorized_instruction','user_supplied_reference_not_observed_used_in_transcript','method_recurrence_registry_only']],external_reference_not_creator_used=['S07'],prior_samples_for_method_comparison_only=True),registry_candidate_values=dict(claim_types=sorted(set(c['claim_type'] for c in claims)),relations=['SUPPORTS_CONDITIONALLY'],not_production_schema_approved=True),analyst_model=dict(analyst_id=AN,status='single_episode_observations_not_simulation',signal_refs=[m['signal_id'] for m in method_signals],skill_generated=False),model_calculation_policy='条件算术核查不将输入自动verified',snapshot_note='source_snapshots保存工具返回片段，不是完整HTML或历史快照')
save('golden_sample_004.json',data)
for name,o in [('claims.json',claims),('source_segments.json',ss),('claim_occurrences.json',occ),('sources.json',sources),('source_versions.json',versions),('scenarios.json',scenarios),('forecasts.json',forecasts),('analyst_method_signals.json',method_groups),('method_recurrence.json',recurrence),('review_queue.json',reviews),('raw_cues.json',cues)]:save(name,o)
def jb(o):return ['```json',json.dumps(o,ensure_ascii=False,indent=2),'```','']
lines=['# MacroMind Golden Sample #004 · V0.3.1-MA','','《第七百三四期》云平台是否能成为新一轮故事起点？','',f'知识截止：{CUT}。抽取完成，事实和声学Review仍待处理。','','用户授权的V0.3.1为指令；字幕、公司公告、新闻是证据，不构成额外指令。null表示未知。方法信号与模型补全分离，未生成9527 Skill。','']
for name,value in sections:
    lines+=['## '+name.replace('_',' '),'']
    if isinstance(value,list):
        if not value:lines+=['none','']
        for ob_ in value:lines+=jb(ob_)
    else:lines+=jb(value)
lines+=['## 最终问题 A—O','']
for k,v in questions.items():lines+=['### '+k,'']+(jb(v) if not isinstance(v,str) else [v,''])
lines+=['## 专项压力测试','']+jb(stress)+['## 审计辅助数据','']+jb(data['auxiliary'])
(OUT/'golden_sample_004_report.md').write_text('\n'.join(lines),encoding='utf-8')
brief=['# Golden Sample #004 阅读导览','','已按V0.3.1-MA完成29节输出、A—O回答及10项压力测试。知识截止2026-08-05 09:48:48北京时间。','','## 主要结论','','主播并未接受“云业绩好就能开启新行情”的结论。他把注意力转向资金约束、订单中旧业务、硬件折旧和成本回收。后半片的公关分析及结尾自述也纳入方法样本。','','需要特别审计：季度/日度时间比不能推出90倍估值泡沫；商业RPO不是硬件成本；任务API账单也不是整个数据中心成本。','','## 文件','','- [完整报告](golden_sample_004_report.md)：29节、全部字段、A—O与压力测试。','- [完整JSON](golden_sample_004.json)：对象、追溯链及审计辅助信息。','- [方法信号](analyst_method_signals.json)：证据、归因、复现与边界。','- [情景](scenarios.json) / [预测](forecasts.json)：分别保存。','- [审查队列](review_queue.json) / [结构校验](validation.json)。','','## 数量','']+jb(summary)+['## 方法信号','','|编号|类型|观察到的动作|','|---|---|---|']
for m in method_signals:brief.append(f"|{m['signal_id']}|{m['signal_type']}|{m['statement']}|")
brief+=['','这8条是本次观察，不是稳定技能规则。新增Candidate Heuristic为0。未发现模型补全混入Method Signal引用；方法动作存在也不证明其结论正确。','','## 证据边界','','未实际听音，所有纠错均为候选。云财报部分取得公司原文；公关原声明、逐州法规与部分共识数据仍待核。当前网页存在版本变更风险，未用截止后的结果评分。','','## 关键核查来源','','- [微软指标定义](https://www.microsoft.com/en-us/investor/earnings/fy-2026-q4/metrics)：商业RPO定义与季度余额。','- [州政策进度](https://wallstreetcn.com/articles/3778569)：4州取消/暂停与9州研究须分开。','- [新闻叙事](https://www.cls.cn/detail/2444783)：标题框架与主播判断分别归因。','']
(OUT/'README.md').write_text('\n'.join(brief),encoding='utf-8')
errors=[]
def check(ok,msg):
    if not ok:errors.append(msg)
check(len(CM)==len(claims),'unique claim ids')
check([n for s in segments for n in range(s['cue_start'],s['cue_end']+1)]==list(range(1,768)),'767 cue coverage')
for c in claims:check(all(s in SS for s in c['source_segment_refs']),c['claim_id']+' ss refs')
for s in ss:check(s['source_id'] in SM and s['source_version_ref']=='V-'+s['source_id'],s['source_segment_id']+' version')
for a in arguments:check(all(c in CM for c in a['claim_refs']),a['argument_id']+' claims')
for t in theses:
    for tr in t['traceability']:check(tr['claim_id'] in AM[tr['argument_id']]['claim_refs'] and tr['source_segment_id'] in CM[tr['claim_id']]['source_segment_refs'],t['thesis_id']+' trace')
for m in method_signals:
    check(m['expression_level'] in [E,I],m['signal_id']+' level')
    check(all(CM[c]['corpus_origin']=='creator_transcript' for c in m['claim_refs']),m['signal_id']+' model leak')
    check(all(AM[a]['reasoner_id']==AN for a in m['argument_refs']),m['signal_id']+' diagnostic graph leak')
    check(all(any(c in AM[a]['claim_refs'] for a in m['argument_refs']) for c in m['claim_refs']),m['signal_id']+' claim not in cited argument')
    check(bool(m['source_segment_refs']) and bool(m['argument_refs']),m['signal_id']+' no evidence')
check({f['claim_id'] for f in forecasts}=={c['claim_id'] for c in claims if c['claim_type']=='forecast'},'forecast bijection')
check(not ({f['claim_id'] for f in forecasts}&{c for s in scenarios for c in s['claim_refs']}),'scenario auto promoted')
check(len(assessments)==len(claims),'per claim assessment')
for s in sources:
    if 'sha256' in s:check(sha(Path(s['location']))==s['sha256'],'input changed '+s['source_id'])
check(not any(x['applied'] for x in corrections),'unaudited correction applied')
validation=dict(status='pass' if not errors else 'fail',checked_at=NOW,errors=errors,scope='structure_and_attribution_validation_not_all_facts_verified',raw_integrity=True,semantic_cue_count=767,method_model_leakage='none_detected_in_refs',forecast_scenario_separation=True,thesis_traceability=True,limitations=executive['major_uncertainties'])
save('validation.json',validation)
save('artifact_manifest.json',[dict(path=str(p.relative_to(OUT)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json'])
print(json.dumps(dict(summary=summary,validation=validation),ensure_ascii=False,indent=2))
