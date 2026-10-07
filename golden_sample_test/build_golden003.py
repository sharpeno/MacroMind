import json,re,hashlib,collections
from pathlib import Path
from datetime import datetime,timezone,timedelta

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'golden_sample_003'; OUT.mkdir(exist_ok=True)
CUT='2026-03-03T17:30:00+08:00'
NOW=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
BASE=Path(r'G:\BilibiliDown.v6.41.release\download\有何高见9527')
SRT=next(BASE.glob('*六百二七期*.srt')); TXT=next(BASE.glob('*六百二七期*.自动转写.txt')); VIDEO=next(BASE.glob('*六百二七期*.mp4'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
cues=[]
for b in re.split(r'\n\s*\n',SRT.read_text(encoding='utf-8-sig').strip()):
    a=b.splitlines()
    if a and a[0].isdigit():
        start,end=a[1].split(' --> ')
        cues.append(dict(cue_id=int(a[0]),start=start,end=end,raw_text='\n'.join(a[2:])))
assert len(cues)==899
def raw(a,b):return '\n'.join(c['raw_text'] for c in cues[a-1:b])
def bounds(a,b):return dict(cue_start=a,cue_end=b,start=cues[a-1]['start'],end=cues[b-1]['end'])
segments=[]
topics=[(1,28,'问题设定与美国AI资本动机'),(29,109,'海峡控制、岸基威胁、保险与实物流'),(110,165,'战争话语与美国处境判断'),(166,198,'首周油价及决策分叉'),(199,255,'撤退与选择性开放情景'),(256,324,'升级情景、120与40天口径'),(325,369,'40天撤退与国内胜利包装'),(370,440,'中东向东亚外推与军工产量'),(441,472,'情报公开、盟友与战争成本'),(473,530,'储油容量、30乘2与60天上限'),(531,565,'持久控制、和谈、以色列与霸权'),(566,620,'无敌舰队类比与信誉杠杆'),(621,649,'一个月波动和40天判断'),(650,705,'海峡控制者、定价权及租金'),(706,743,'美国国内廉价油与分配假说'),(744,779,'能源转型、军事AI与资本回流'),(780,810,'美元避险与信用透支'),(811,850,'美国大概率失败与反讽假设'),(851,877,'胜者秩序与邻国关系'),(878,899,'旧比喻、立场和保留判断')]
for i,(a,b,t) in enumerate(topics,1):segments.append(dict(segment_id=f'SEG{i:02}',topic=t,source_id='S03',**bounds(a,b)))
sources=[]
def src(i,title,loc,role,typ,pub=None,fam=None,parent=None,read='read',version=None):
    sources.append(dict(source_id=i,title=title,location=str(loc),role=role,source_type=typ,published_at=pub,recorded_at=None,captured_at=NOW,read_status=read,source_family_id=fam or i,derived_from=parent or [],independence='derived' if parent else 'unknown',version=version or 'current_capture_not_historical_archive'))
src('S01',VIDEO.stem,VIDEO,'primary_corpus','video',CUT,'F9527',read='file_found_hashed_audio_not_reviewed',version='local_file_sha256')
src('S02','自动转写原文',TXT,'transcript','asr_text',None,'F9527',['S01'],version='local_file_sha256')
src('S03','SRT原文',SRT,'timestamp_anchor','asr_subtitle',None,'F9527',['S01'],version='local_file_sha256')
src('S04','美伊战火“点燃”油气市场，价格能涨至多高？一文读懂','https://www.cls.cn/detail/2300559','creator_cited_reference','news','2026-03-03T08:48:00+08:00','FCLS_OIL',read='article_body_read_tool_capture')
src('S05','财联社持续更新直播；标题已变化','https://www.cls.cn/detail/2298102','creator_cited_reference','rolling_news','2026-02-28T14:26:00+08:00','FCLS_LIVE',read='selected_entries_read_current_page_contains_post_cutoff',version='current_page_selected_entry_whitelist')
ru='https://www.reuters.com/world/middle-east/platts-reviewing-mideast-crude-pricing-mechanism-amid-us-israel-attacks-iran-2026-03-02/'
src('S06','Reuters / Platts 原链接',ru,'user_supplied_reference','news','2026-03-02','FREUTERS_PLATTS',read='open_failed_not_read')
src('S07','Reuters稿件的Business Recorder转载','https://www.brecorder.com/news/40409686/platts-reviewing-mideast-crude-pricing-mechanism-amid-us-israel-attacks-on-iran','reference_recovery','syndication','2026-03-02','FREUTERS_PLATTS',['S06'],read='article_body_read',version='Mar2_11:33_timezone_unknown_current_capture')
pu='https://www.spglobal.com/energy/en/pricing-benchmarks/our-methodology/subscriber-notes/'
src('S08','Platts成品油MOC海峡内港口报价调整',pu+'030226-platts-suspends-bids-and-offers-for-persian-gulf-ports-within-strait-of-hormuz-in-middle-east-refined-products-moc-assessment-process','model_supplement','methodology_notice','2026-03-02','FPLATTS')
src('S09','Platts评估是否继续发布中东运费',pu+'030226-platts-reviewing-middle-east-freight-assessment-publication','model_supplement','methodology_notice','2026-03-02','FPLATTS')
src('S10','Platts确认继续发布中东运费评估',pu+'030226-platts-to-publish-middle-east-freight-assessments-including-clean-arab-gulf-japan-lr1-55kt','model_supplement','methodology_notice','2026-03-02','FPLATTS')
src('S11','EIA：霍尔木兹流量与分母','https://www.eia.gov/todayinenergy/detail.php?id=65504','model_supplement','statistical_analysis','2025-06-16','FEIA_VORTEXA',version='page_notes_reposted_label_correction_date_unknown')
src('S12','V03.MD',r'G:\youhegaojian\prompt\V03.MD','user_authorized_instruction','prompt',None,'FINSTRUCTIONS',version='local_file_sha256')
src('S13','V0.3追加.md',r'G:\youhegaojian\prompt\V0.3追加.md','user_authorized_instruction_and_metadata','prompt',None,'FINSTRUCTIONS',version='local_file_sha256')
for s in sources:
    p=Path(s['location'])
    if not s['location'].startswith('http') and p.exists():s.update(sha256=sha(p),bytes=p.stat().st_size)
source_map={s['source_id']:s for s in sources}
versions=[]
def ver(i,time,topic,status='eligible_by_displayed_timestamp',note=None):
    versions.append(dict(version_id=i,source_id='S05',item_published_at=time,topic=topic,cutoff_status=status,captured_at=NOW,historical_snapshot_available=False,edit_history_known=False,note=note))
ver('LV01','2026-03-03T04:19:00+08:00','伊朗军方顾问声称关闭；报道同时注明尚无革命卫队官方声明')
ver('LV02','2026-03-03T00:58:00+08:00','特朗普称计划4至5周、可更久，并声称摧毁舰艇')
ver('LV03','2026-03-02T12:27:00+08:00','拉里贾尼表态不与美国谈判')
ver('LV04','2026-03-01T21:54:00+08:00','革命卫队声称向林肯号发射4枚导弹')
ver('LV05','2026-03-02','以色列拟逐步重新开放空域；最早当地当晚',note='日期已知，时刻未可靠记录；仅作为计划报道，不能当成实际开放')
ver('LV06','2026-03-03T21:26:00+08:00','王毅与以外长通话','post_cutoff')
ver('LV07','2026-03-03T23:08:00+08:00','伊朗战果声明','post_cutoff')
ver('LV08','2026-03-04','后续直播条目整组','post_cutoff')
ver('LV09','2026-03-05','后续直播条目整组','post_cutoff')
ver('LV10',None,'无独立条目时间的当前页标题、页首综述','review_required')
source_segments=[]; claims=[]; occurrences=[]; assessments=[]; forecasts=[]; reviews=[]
def review(severity,typ,targets,issue,action):
    reviews.append(dict(review_id=f'RQ{len(reviews)+1:03}',severity=severity,review_type=typ,target_refs=targets,issue=issue,required_action=action,status='open'))
def claim(n,a,b,text,kind='interpretation',q=None,pop=None,certainty=None,ref=None,claimant='A9527',deriv=None):
    cid=f'C{n:03}'; sid='SS-'+cid
    source_segments.append(dict(source_segment_id=sid,source_id='S03',semantic_segment_refs=[s['segment_id'] for s in segments if s['cue_start']<=b and s['cue_end']>=a],**bounds(a,b),raw_text=raw(a,b)))
    c=dict(claim_id=cid,statement=text,claimant_id=claimant,asserted_by_id='A9527',attribution_chain=[claimant,'A9527'] if claimant!='A9527' else ['A9527'],attribution_status='reported_only',claim_type=kind,derivation_type=deriv or ('reported' if claimant!='A9527' else 'explicit_transcript'),temporal_mode='future' if kind=='forecast' else ('past' if kind in ['retrospective_claim','historical_claim'] else 'unknown'),asserted_at=CUT,asserted_at_basis='video_publication_proxy_not_recording_time',reference_time=ref,knowledge_cutoff=CUT,population=pop,quantifier=q,raw_quantifier=q,certainty_expressed=certainty,scope=text,source_segment_refs=[sid],atomicity_group_id=f'AG-{a:03}',corpus_origin='creator_transcript',verified_knowledge_eligible=False)
    claims.append(c); occurrence(cid,a,b,'first','high');return c
def occurrence(cid,a,b,typ='repeat',gain='redundant'):
    occurrences.append(dict(occurrence_id=f'OC{len(occurrences)+1:03}',claim_id=cid,source_id='S03',**bounds(a,b),surface_text=raw(a,b),occurrence_type=typ,information_gain=gain))
# 不把外部核查补写成主播原话；表述为语义摘录，原文逐条随SourceSegment保留。
rows='''1|2|3|reported_claim|有分析师谈到油价120或200；转写将其中机构称为“大摩”。
2|3|5|interpretation|油价路径主要取决于战争进程，具体是美国对战局的主导权。
3|13|20|interpretation|特朗普发动战争的一项动机是让中东避险资金流向美国。
4|16|18|forecast|中东资金赴美将为美国AI泡沫接盘。
5|34|35|forecast|首周若伊朗屈服，地区局面将由美国主导。
6|36|40|reported_claim|特朗普提出消灭伊朗海军的战争目标。
7|38|40|interpretation|消灭伊朗海军的真实目标是夺取霍尔木兹控制权。
8|49|50|factual_claim|霍尔木兹最窄处宽约30公里。
9|55|60|factual_claim|伊朗临海一侧有复杂山地与高差。
10|59|63|interpretation|岸基武器可以威胁海峡，海军被消灭也不等于破坏运输能力消失。
11|65|69|factual_claim|海峡最繁忙时每天通过上几百条油轮。
12|68|69|factual_claim|这些油轮有几十万吨级运载规模；原句含“几十吨”的疑似改口。
13|70|70|factual_claim|最繁忙时平均6分钟通过一艘船。
14|73|84|interpretation|零星袭击的风险足以增加船主保险成本。
15|83|84|interpretation|增加的保费会转嫁到运输货物的成本。
16|86|89|interpretation|运输风险促使通行密度降低，削弱运力。
17|90|95|hypothetical_assumption|以运量减少20%、需求不变或增加作为演示情景。
18|95|102|interpretation|运出受阻会限制海湾产油国的产出上限，无须完全封锁。
19|104|109|interpretation|仅靠摧毁海军取得完全海峡控制权的计划不能成立。
20|111|113|interpretation|美国正在逐渐失去局势控制。
21|128|130|interpretation|没有看到美国庆祝伊朗友好投降的表态，说明尚未达到这一结果。
22|133|135|reported_claim|特朗普向《大西洋月刊》表示伊朗提出谈判。
23|136|143|reported_claim|特朗普表示原计划军事行动4至5周，也准备进行更长时间。
24|146|154|interpretation|宣称可以打很久，实际是施压缩短战争并暴露内心不确定。
25|163|180|forecast|首周油价缓慢上涨约20%至30%，到80至90左右。
26|183|198|forecast|美国首周之后可能撤退，也可能追加行动。
27|206|207|reported_claim|林肯号航母已经后退约900公里。
28|212|228|forecast|若美国撤出并让伊朗面对国际压力，伊朗会妥协开放海峡。
29|234|235|forecast|美国可以在约一周后把撤退包装成已实现胜利。
30|236|242|reported_claim|以色列昨天宣布重新开放空域；主播借此说明宣布开放不等于实际安全。
31|245|249|forecast|撤退分支下伊朗自有出口可通过海峡并继续向外运输。
32|253|255|forecast|撤退及开放分支下油价会适度回落或停止上涨。
33|261|269|interpretation|即使无法控制近岸，美国仍有远洋海军阻断伊朗友好船运的能力。
34|273|285|forecast|追加行动分支中，美国可能以打击亲伊朗船只来阻止伊朗获利。
35|286|296|forecast|追加行动带来成本上升，之后约一个月油价可逐渐到120左右。
36|297|314|interpretation|首周加后续一个月被叙述为约4周、40天，并与哈梅内伊40天哀悼期联系。
37|319|323|forecast|约40天时油价或在90至110区间并开始下降；先说90至100再改口。
38|325|329|interpretation|美国缺乏明确战略目的，因此无法持续投入。
39|330|344|forecast|约40天美国可能撤退或谈判，伊朗掌握海峡则美国实质失败。
40|346|355|forecast|特朗普可用击杀哈梅内伊包装胜利，失败未必影响国内选举。
41|373|374|factual_claim|霍尔木兹占全世界油供的30%至40%。
42|375|376|forecast|伊朗不可能永久封锁海峡。
43|380|381|interpretation|伊朗石油可替代，而中国工业品不可替代。
44|383|383|hypothetical_assumption|把中国民用工业全部转向军工生产作为设想。
45|384|388|reported_claim|鲁比奥称美国制造六七枚拦截弹的时间，伊朗能造100枚攻击导弹。
46|389|392|hypothetical_assumption|主播把中国产量推演成同期1万枚、美国仍六七枚。
47|393|398|forecast|按这一军工差距，美国舰队在东亚将无法有效对抗中国。
48|403|405|forecast|主播认为台湾已是囊中之物，未来统一只剩成本问题。
49|408|413|interpretation|中国当前战略是通过对日行动把美国力量逐出东亚。
50|415|415|interpretation|韩国已清楚理解上述战略局面。
51|416|425|reported_claim|驻韩美军而非韩国空军曾与中国对峙；时间先说国庆节后又说春节前。
52|421|429|interpretation|驻韩美军对峙是在缺乏其他突破口时刷存在感。
53|433|439|retrospective_claim|主播称自己在2024或2025年的往期节目说过台湾问题已升级为日本问题。
54|442|445|hypothetical_assumption|中国卫星获取的信息可以向外公开。
55|446|449|forecast|若各方判断美国打不了，就不会参战，也不会替美国分担成本。
56|449|464|interpretation|战争成本无人分担会限制美国持续作战能力。
57|473|477|reported_claim|主播转述摩根大通测算：海湾油储只能支撑20多天。
58|478|480|interpretation|因产油量会减少，主播将油储可支撑时间放宽到约30天。
59|481|483|interpretation|再以“料敌以宽”把30天翻倍成两个月。
60|484|486|forecast|若伊朗实控封锁两个月，任何域外国家都必须妥协。
61|490|495|forecast|如果美国不能解决海峡通行，海湾国家会迫其谈判，甚至可能翻脸。
62|499|503|factual_claim|海湾主权基金向美国投资市场提供大量资本。
63|504|511|forecast|海湾资金施压与反战合力会迫使特朗普停止战争。
64|512|515|forecast|美国战争时间窗口最大60天，超过60天绝对不可能。
65|517|524|historical_claim|过去霍尔木兹封锁60天之后各方都妥协，今天会更早妥协；未指明历史案例。
66|528|530|interpretation|大家若相信海峡最终必须开放，60天上限就有把握。
67|531|535|forecast|若封锁超过40天，伊朗将大胜，美国将主动求和。
68|537|547|forecast|美国与伊朗和解将以牺牲以色列利益为交换。
69|548|565|forecast|若美国因此失去中东主导权，全球霸权将显著衰退，过程可能很长。
70|566|574|historical_claim|西班牙无敌舰队败于英国后，西班牙便失势而英国上升。
71|575|582|historical_analogy|这场中东战争正在成为美国的“无敌舰队覆灭”时刻。
72|586|595|interpretation|克制美国的武器可以跨地区使用，因此其他地区也可限制美国行动。
73|596|619|forecast|美国战败会暴露实力边界，更多参与者将挑战其依靠威慑建立的杠杆。
74|610|617|interpretation|美国在战术上进攻、战略上防守，需借战争证明霸主能力。
75|623|628|forecast|未来约一个月油价不会特别剧烈波动，而会缓慢上涨。
76|631|635|forecast|若油价突然猛涨，因市场预期尚未到位会回调。
77|634|638|interpretation|美国目前仍部分掌握战场主动，局面尚未完全失控。
78|641|644|forecast|约40天后美国胜负将有明确结论。
79|646|649|forecast|若伊朗控制霍尔木兹，油价会回落。
80|650|651|forecast|若美国控制霍尔木兹，油价长期维持“100到126”区间；数值待听音。
81|656|656|factual_claim|美国控制着委内瑞拉。
82|657|667|interpretation|美国可通过掌握供应权与定价权把国际油价定高。
83|669|674|forecast|美国控制海峡并抬高油价后，额外收益只会落到美国手中。
84|676|683|analogy|军事控制变现类似街头收保护费，营业额越高可收取越多。
85|685|689|forecast|伊朗占上风时油价可能回到六七十或七八十。
86|690|693|forecast|若美国获胜，油价长期维持100甚至120是可能的。
87|697|702|historical_claim|过去2023年及2000年前的高油价利润主要由海湾产油国与俄罗斯赚取。
88|706|717|forecast|若美国主导，特朗普将为连任把高油价收益转成国内廉价用油安排。
89|718|741|forecast|这类分配主要有利于资本，普通人只够温饱，其他商品价格仍上涨。
90|744|749|forecast|若美国无法主导，石油美元将成为过去，未来转向新能源时代。
91|753|757|reported_claim|本轮对伊军事行动已广泛使用AI进行数据分析、预测和指挥。
92|758|765|forecast|军事与信息战应用场景将为AI泡沫提供价值支撑。
93|768|771|reported_claim|战争已把中东资金挤向美国，其中不少也去了中国。
94|772|778|forecast|全球风险增加带来的赴美资金将给AI题材提供新资金来源。
95|773|774|interpretation|此前AI泡沫难以继续扩张主要因为缺钱。
96|781|785|reported_claim|特朗普刚上台时曾保证美元不会贬值。
97|787|791|interpretation|制造国际动荡和减少安全投入，是支撑美元的一条路径。
98|793|803|interpretation|美元既有规模和惯性会通过地缘动荡自我维持。
99|804|810|forecast|通过动荡维持美元信用不可持续，透支后美国衰退会加速。
100|818|819|forecast|本轮战争美国大概率会输。
101|849|850|forecast|美国本土出现所谓圣战的情景不太可能。
102|851|854|interpretation|只有战场打不赢，才会诉诸对方后方的恐怖袭击。
103|855|875|forecast|若伊朗确立海峡秩序主导权，会更愿意向邻国示好而非持续宗派对抗。
104|878|888|retrospective_claim|此前用沙特与伊朗狮王争霸作比喻；美国参战后该比喻不再适用。
105|892|898|value_judgment|主播乐见美国陷入不利局面，同时表示未来仍需边发展边观察。'''
for line in rows.splitlines():
    n,a,b,k,t=line.split('|',4);claim(int(n),int(a),int(b),t,k)
CM={c['claim_id']:c for c in claims}
def upd(n,**kw):CM[f'C{n:03}'].update(kw)
for n,actor in [(1,'AANALYST_UNKNOWN'),(6,'ATRUMP'),(22,'ATRUMP'),(23,'ATRUMP'),(45,'ARUBIO'),(57,'AJPM'),(96,'ATRUMP')]:upd(n,claimant_id=actor,attribution_chain=[actor,'A9527'])
for n,q in [(8,'差不多30公里'),(11,'上几百条'),(12,'几十吨的几十万吨'),(13,'6分钟'),(17,'假设少20%'),(23,'4到5个星期；更长'),(25,'20%到30%；80到90'),(27,'900公里'),(35,'一个月；120'),(36,'一个星期；一个月；4个星期；40天'),(37,'90到100；90到110'),(41,'30%到40%'),(44,'全部'),(45,'六七枚；100枚'),(46,'1万枚；六七枚'),(53,'24年还是25年'),(57,'20多天'),(58,'30天'),(59,'翻倍；两个月'),(60,'任何一个'),(62,'很多很多'),(64,'最大上限；超过60天绝对不可能'),(65,'没有哪一个不妥协'),(75,'一个月左右；不会特别巨大'),(78,'40天'),(80,'100到126；相当长'),(83,'只是落在美国手里'),(85,'六七十七八十都有可能'),(86,'100甚至120；长期'),(87,'2023年；2000年以前'),(100,'大概率'),(101,'不太有可能'),(102,'只有')]:upd(n,quantifier=q,raw_quantifier=q)
for n in [1,23,45,57,96]:upd(n,derivation_type='secondhand_report')
for n in [53,104]:upd(n,reference_time='prior_episode_date_unknown',temporal_mode='past')
upd(65,temporal_mode='mixed_past_and_future',reference_time='unidentified_historical_cases')
# 历史事实与未来外推强度不同，再拆一条，避免混合。
upd(65,statement='过去霍尔木兹封锁60天之后各方都妥协；未指明历史案例。',temporal_mode='past')
claim(106,521,524,'有以往妥协教训，各方这次会更早妥协。','forecast')
upd(30,statement='以色列昨天宣布重新开放空域。',claimant_id='AISRAEL',attribution_chain=['AISRAEL','A9527'])
claim(107,238,242,'宣布空域开放不等于证明民航实际安全。','interpretation')
claim(108,171,178,'主播取战前油价70为估算基数；没有指明油种、交易所和时点。','hypothetical_assumption',q='60到70；按70算')
claim(109,312,314,'哈梅内伊哀悼期为40天。','reported_claim',q='40天')
# 相同命题的再次出现不增加Claim数量。
for args in [(2,29,31,'restatement','low'),(3,779,779,'summary','redundant'),(4,772,778,'elaboration','medium'),(25,288,288,'repeat','redundant'),(42,528,529,'restatement','low'),(64,529,530,'summary','low'),(79,685,688,'restatement','low'),(82,704,705,'summary','low')]:
    n,a,b,t,g=args;occurrence(f'C{n:03}',a,b,t,g)
occurrence('C037',319,320,'self_correction','medium');occurrence('C037',321,323,'self_correction','high')
occurrence('C029',234,235,'self_correction','medium')
# 外部来源Claim并非9527主张。网页文本仅保留简短转述和定位，完整返回保存在snapshot。
def ext(cid,sid,locator,text,actor,kind='factual_claim',time=None,version=None):
    seg='SS-'+cid
    source_segments.append(dict(source_segment_id=seg,source_id=sid,locator=locator,version_id=version,raw_text=None,excerpt_policy='paraphrase; see captured tool response'))
    c=dict(claim_id=cid,statement=text,claimant_id=actor,asserted_by_id=sid,attribution_chain=[actor,sid] if actor!=sid else [sid],attribution_status='source_verified',claim_type=kind,derivation_type='external_source_report',temporal_mode='future' if kind=='forecast' else 'unknown',asserted_at=time or source_map[sid]['published_at'],asserted_at_basis='source_displayed_publication_time',reference_time=None,knowledge_cutoff=CUT,population=None,quantifier=None,raw_quantifier=None,certainty_expressed=None,scope=text,source_segment_refs=[seg],atomicity_group_id=cid,corpus_origin='external_context_not_creator',verified_knowledge_eligible=False)
    claims.append(c);CM[cid]=c
    occurrences.append(dict(occurrence_id=f'OC{len(occurrences)+1:03}',claim_id=cid,source_id=sid,source_segment_id=seg,surface_text=None,paraphrase=text,occurrence_type='first',information_gain='high'))
ext('X01','S04','JPM段','若战争持续超过三周、无法外运导致储罐容量用尽并迫使停产，布伦特可达120美元。','AJPM','forecast')
ext('X02','S04','Deutsche Bank段','全面封闭海峡的极端情景下，布伦特可能达到200美元。','ADB','forecast')
ext('X03','S04','BoA段','若战争快速结束，布伦特可能回到60至70美元。','ABOA','forecast')
ext('X04','S04','Kpler段','2025年经海峡外运约占全球海运石油出口的三分之一。','AKPLER')
ext('X05','S05','3月3日04:19条','军方顾问宣称海峡关闭；该条同时注明未有革命卫队正式声明。','AIRAN_ADVISER',time='2026-03-03T04:19:00+08:00',version='LV01')
ext('X06','S05','3月3日00:58条','特朗普声称已击沉10艘伊朗舰艇。','ATRUMP',time='2026-03-03T00:58:00+08:00',version='LV02')
ext('X07','S05','3月1日21:54条','革命卫队声称向林肯号发射4枚弹道导弹。','AIRGC',time='2026-03-01T21:54:00+08:00',version='LV04')
ext('X08','S07','正文首两段','Platts因海峡航运安全与停航通知审查海湾原油交付可行性。','APLATTS')
ext('X09','S08','methodology notice body','Platts即日起排除部分须通过海峡的港口成品油MOC买卖报价，相关价格评估继续。','APLATTS')
ext('X10','S09','methodology notice body','Platts审查中东运费评估能否继续发布。','APLATTS')
ext('X11','S10','methodology notice body','Platts随后确认继续发布中东运费评估，并可结合市场资料判断。','APLATTS')
ext('X12','S11','正文2024流量段','EIA估算2024年海峡日均油流2000万桶，约为全球石油液体消费量20%。','AEIA')
ext('X13','S04','JPM storage段','摩根大通所说约三周约束是出口受阻后储油空间耗尽并迫使减产，不是消费库存耗尽。','AJPM')
ext('X14','S04','BoA infrastructure段','若伊朗打击邻国能源设施，布伦特可能超过100美元。','ABOA','forecast')
# 分拆EIA流量与比率两个测量命题。
CM['X12']['statement']='EIA估算2024年海峡日均油流为2000万桶。'
ext('X15','S11','正文2024消费分母段','EIA估算2024年海峡油流约相当于全球石油液体消费量20%。','AEIA')
# 重建桥接为显式model claim，不能回填视频。
bridges=[('M01','供应预期影响具体期货曲线还取决于库存、替代供应、需求弹性和风险偏好。'),('M02','运输成本传到特定现货基准需要可交付货源、替代路线及合约条款约束。'),('M03','控制航道要转化为持续定价权，仍需控制边际供应且其他生产者和需求无法有效抵消。'),('M04','取得石油租金不等于财政取得可供国内补贴的同额收入。'),('M05','海湾储油压力转化为美国停战，需要政治联盟、撤资能力与美国政策响应同时成立。'),('M06','中东避险流入美国资产不等于流入AI股权或AI融资。'),('M07','单一战区的武器效能跨地区复制需要地理、后勤、情报和政治条件相容。')]
for cid,t in bridges:
    claims.append(dict(claim_id=cid,statement=t,claimant_id='AMODEL',asserted_by_id='AMODEL',attribution_chain=['AMODEL'],attribution_status='reported_only',claim_type='model_reconstruction',derivation_type='model_reconstruction',temporal_mode='analytical',asserted_at=NOW,reference_time=None,knowledge_cutoff=CUT,population=None,quantifier=None,raw_quantifier=None,certainty_expressed=None,scope='待验证的必要桥接，不是事实现象或主播原话',source_segment_refs=[],atomicity_group_id=cid,corpus_origin='model_analysis',verified_knowledge_eligible=False))
CM={c['claim_id']:c for c in claims}
# 只填原文确有的时间/群体；未知字段仍保留null。
for n in [8,9,11,12,13,17,18,41,57,58,59]:
    CM[f'C{n:03}']['population']='霍尔木兹相关航运或海湾产油国（具体范围见statement）'
for n in [6,7,20,21,22,23,24,27,33,38,51,52,56,74,77,81,82,96,97,98]:
    CM[f'C{n:03}']['population']='美国或其政府/军方（命题对象见statement）'
for n in [53,87,96,104]:CM[f'C{n:03}']['temporal_mode']='past'
CM['C087']['reference_time']=['2023','2000年以前']
CM['C096']['reference_time']='特朗普刚上台时；未给日期'
CM['X04']['reference_time']='2025'
CM['X12']['reference_time']='2024';CM['X15']['reference_time']='2024'
corrections=[]
for a,b,before,after,conf in [(2,3,'反常试 / 霍尔木斯','反常识 / 霍尔木兹','high'),(16,16,'网爷','王爷','high'),(19,20,'容易算呗 / 容易算票','如意算盘','high'),(40,63,'霍尔木彩霞 / 霍尔蒙采家 / 霍乌尔木兹','霍尔木兹海峡','high'),(68,84,'游轮 / 游船','油轮 / 油船','high'),(97,97,'海和会','海合会','high'),(120,120,'哈哈内衣','哈梅内伊','high'),(384,384,'路比奥','鲁比奥','high'),(393,393,'慢剑启发','万箭齐发','medium'),(475,480,'邮储 / 石油储备','储油空间或库存；不作替换','low'),(483,483,'料底以宽','料敌以宽','high'),(613,613,'战略上的首势','战略上的守势','high'),(651,651,'100到126','100到120？保留126','low'),(657,657,'国际金价','国际油价？','medium'),(757,757,'使用医','使用AI','high'),(868,868,'实界派 / 训级派','什叶派 / 逊尼派','high')]:
    corrections.append(dict(correction_id=f'COR{len(corrections)+1:02}',**bounds(a,b),raw_text=raw(a,b),raw_form=before,proposed_normalized_form=after,status='needs_audio_review',semantic_confidence=conf,acoustic_confidence='unknown',applied=False))
annotations=[]
for typ,a,b,note in [('self_correction',319,323,'90至100改为90至110；可从文字观察，不认定听音确认'),('self_correction',234,235,'一个月改为一个星期'),('ambiguous_reference',297,314,'首周+一个月、四周、40天非同一窗口'),('ambiguous_reference',416,425,'国庆节与春节前同时出现，不能静默选择'),('mixed_fact_and_opinion',36,40,'宣布军事目标与主播解读目标分开'),('mixed_fact_and_opinion',475,486,'机构测算经主播放宽与翻倍成为政治上限'),('rhetorical_exaggeration',820,848,'神选、魔法和本土圣战的反讽铺垫，紧接否定其大概率发生'),('rhetorical_exaggeration',537,547,'祭品及杀戮比喻不抽成已发布的对以军事行动'),('ambiguous_reference',706,707,'特朗普连任指本人/党派/别的选举未知'),('ambiguous_reference',517,524,'历史封锁60天缺具体事件'),('rhetorical_exaggeration',676,683,'保护费是比喻，不是有来源的现行收费政策')]:
    annotations.append(dict(annotation_id=f'AN{len(annotations)+1:02}',annotation_type=typ,**bounds(a,b),note=note,speaker_slip_confirmed=False))
# 有限Actor注册；组织与国家、报道者与发言人分开。
actor_names={'A9527':'有何高见9527','AMODEL':'抽取模型','ATRUMP':'唐纳德·特朗普','AIRAN':'伊朗','AUS':'美国','AISRAEL':'以色列','AIRGC':'伊朗伊斯兰革命卫队','AIRAN_ADVISER':'革命卫队指挥官顾问（姓名未解析）','AJPM':'摩根大通','ADB':'德意志银行','ABOA':'美国银行','AKPLER':'Kpler','APLATTS':'S&P Global Platts','AEIA':'美国能源信息署','ARUBIO':'马尔科·鲁比奥','AANALYST_UNKNOWN':'开场“大摩”所指分析师待核','ACHINA':'中国','AGULF':'海湾国家（集合）','ASAUDI':'沙特阿拉伯','AJAPAN':'日本','AKOREA':'韩国','ARUSSIA':'俄罗斯','AVENEZUELA':'委内瑞拉','AKHAMENEI':'阿里·哈梅内伊','ASPAIN':'西班牙','AUK':'英国'}
actors=[dict(actor_id=k,name=v,entity_status='candidate' if k in ['AIRAN_ADVISER','AANALYST_UNKNOWN'] else 'resolved_name_only',identity_not_claim_veracity=True) for k,v in actor_names.items()]
events=[]
def ev(i,t,claims_,ann=None,eff=None,occur=None,status='reported_not_independently_verified',sub=None):
    events.append(dict(event_id=i,description=t,claim_refs=claims_,decision_at=None,announced_at=ann,scheduled_at=None,effective_at=eff,occurred_at=occur,status=status,event_type=sub or 'reported_event',structural_process_ref=None))
ev('EV01','美以对伊军事行动开始',['X08'],occur='2026-02-28')
ev('EV02','顾问发布海峡关闭声称',['X05'],ann='2026-03-03T04:19:00+08:00',sub='statement_event')
ev('EV03','向航母发射4枚导弹的战果声称',['X07'],ann='2026-03-01T21:54:00+08:00',sub='combatant_statement_event')
ev('EV04','击沉舰艇声称',['X06'],ann='2026-03-03T00:58:00+08:00',sub='combatant_statement_event')
ev('EV05','Platts审查原油可交付性',['X08'],ann='2026-03-02',sub='x_candidate_market_infrastructure_event')
ev('EV06','成品油MOC报价准入变更',['X09'],ann='2026-03-02',eff='2026-03-02',status='primary_notice_verified_action_scope',sub='x_candidate_market_infrastructure_event')
ev('EV07','运费评估发布审查',['X10'],ann='2026-03-02',sub='x_candidate_market_infrastructure_event')
ev('EV08','确认继续发布运费评估',['X11'],ann='2026-03-02',sub='x_candidate_market_infrastructure_event')
ev('EV09','以色列计划重新开放空域',['C030'],ann='2026-03-02',status='announcement_only_actual_opening_unknown')
# 测量口径不全仍可存reported/projection，不能作为verified观察。
indicators=[]; observations=[]
def obs(cid,name,value,unit,measure,status='reported',den=None,num=None,period=None,currency=None):
    iid=f'IN{len(indicators)+1:02}';oid=f'OB{len(observations)+1:02}'
    indicators.append(dict(indicator_id=iid,name=name,measurement_type=measure,definition_status='partial' if den is None and measure in ['share','ratio'] else 'specified_as_reported'))
    c=CM[cid]
    observations.append(dict(observation_id=oid,indicator_id=iid,claim_ref=cid,measurement_type=measure,value_status=status,value=value,unit=unit,currency=currency,numerator=num,denominator=den,gross_net='unknown',period_basis='unknown',reference_period=period,released_at=c['asserted_at'],vintage_at=None,classification_version=None,source_segment_refs=c['source_segment_refs'],eligible_for_verified_series=False))
obs('C008','海峡最窄宽度',30,'km','level')
obs('C011','最忙时每日油轮数','上几百','艘/日','count')
obs('C012','油轮规模','几十万吨','吨（载重/货物量未明）','amount')
obs('C013','最忙时过船间隔',6,'分钟/艘','rate')
obs('C017','假设流量减少幅度',20,'%','growth_rate','projected',den='未指明基期流量')
obs('C027','林肯号撤离距离',900,'km','level')
obs('C041','主播所称海峡世界油供份额',[30,40],'%','share',den='全世界油供（未定义）',num='海峡通行油量')
obs('C045','转述美伊同时间弹药产量比','6或7 : 100','枚:枚','ratio',den='伊朗攻击导弹100枚',num='美国拦截弹6或7枚')
obs('C046','设想中美同时间弹药产量比','10000 : 6或7','枚:枚','ratio','projected',den='美国拦截弹6或7枚',num='中国导弹10000枚')
obs('C057','主播转述储油可支撑天数','20多','天','level')
obs('C058','主播放宽后的储油天数',30,'天','level','estimated')
obs('C059','翻倍后的时间缓冲',60,'天','level','calculated')
obs('X04','2025海峡占全球海运石油出口份额','约1/3','比例','share',den='全球海运石油出口',num='经海峡出口油量',period='2025')
obs('X12','2024海峡日均石油流量',20,'百万桶/日','flow',period='2024')
obs('X15','2024海峡流量相对全球液体消费',20,'%','share',den='全球石油液体消费量',num='海峡油流',period='2024')
obs('C108','主播油价推算基值',70,'油价单位原话未明','level','estimated')
obs('X06','美方声称击沉伊朗舰艇数',10,'艘','count')
obs('X07','伊方声称发射导弹数',4,'枚','count')
policies=[dict(policy_id='PO01',description='特朗普所述摧毁伊朗海军目标',claim_refs=['C006'],status='reported_objective_not_implemented_result'),dict(policy_id='PO02',description='Platts成品油MOC报价准入规则临时调整',claim_refs=['X09'],status='institutional_methodology_rule',scope='受影响装港与报价；不泛化为全球期货定价规则')]
expectations=[dict(expectation_snapshot_id='EX01',observer='A9527',as_of=CUT,as_of_basis='publication_proxy',population='主播泛指油市参与者，未给抽样范围',target='near_term_oil_price_spike',expectation='市场预期尚不足以支持油价突然冲高',claim_refs=['C076'],measurement_source='creator_inference_not_survey',confidence='low')]
def assess(cid,status='uncertain',note='转写证明主播表达此观点，不能独立证明现实；尚无充分原始证据。',support=None,counter=None,families=None):
    assessments.append(dict(assessment_id='VA-'+cid,claim_id=cid,observer='AMODEL',assessed_at=NOW,knowledge_cutoff=CUT,veracity=status,assessment_scope='proposition_truth_not_utterance_existence',support_refs=support or [],counterevidence_refs=counter or [],independent_source_family_count=len(set(families or [])),count_basis='仅计相互独立且支持命题内容的外部起源；转述者不追加计数',limitations=note,verified_knowledge_eligible=False))
for c in claims:
    cid=c['claim_id'];k=c['claim_type']
    note=''
    if k=='forecast':note='截至cutoff尚未到结算时点；未使用其后结果评分。条件、指标和期限见Forecast。'
    elif k=='model_reconstruction':note='这是模型列出的待证桥接，不是已获证实的经验关系。'
    elif k in ['hypothetical_assumption','value_judgment','analogy']:note='设想、价值判断或比喻，不按现实观测评分。'
    assess(cid,'unverifiable' if k in ['value_judgment','analogy','hypothetical_assumption'] else 'uncertain',note or '语义抽取成立不等于现实成立；来源/声学核查仍不足。')
VA={a['claim_id']:a for a in assessments}
def va(cid,stat,note,support=[],counter=[],fam=[]):
    a=VA[cid];a.update(veracity=stat,limitations=note,support_refs=support,counterevidence_refs=counter,independent_source_family_count=len(set(fam)))
va('C006','likely_true','直播与油价稿均转述同一特朗普讲话，按一个讲话起源计；原始讲话未读。',['S04','LV02'],fam=['FTRUMP_SPEECH'])
va('C023','likely_true','可核对到同期报道的讲话内容；未来会持续多久并未因此证实。',['LV02'],fam=['FTRUMP_SPEECH'])
va('C030','uncertain','同期条目是拟逐步重开/最早当晚，不能证明已实际开放。',['LV05'])
va('C041','disputed','“世界油供”分母未明。EIA给的是2024消费20%，Kpler是2025海运出口约1/3，年份和分母都不同，不能直接用20%改写原话。',counter=['X04','X15'])
va('C057','disputed','机构报道讲储罐剩余容量耗尽，主播说“油储支撑”可能混淆概念；后续存储措辞又接近容量，须听音并核原研报。',counter=['X13'])
va('C064','uncertain','30天乘2不是政治停战上限模型；“绝对不可能”缺支撑。')
va('C001','disputed','参考稿120与200分属JPM和德银条件情景；开场“大摩”可能简称错误或另有所指，不能自动换机构。',counter=['X01','X02'])
for cid in ['X09','X10','X11']:
    va(cid,'verified','只核实Platts自身公布的规则/发布决定，不证明战争战果或油价必然方向。',['S08' if cid=='X09' else ('S09' if cid=='X10' else 'S10')],fam=['FPLATTS'])
    VA[cid]['verified_knowledge_eligible']=True;CM[cid]['verified_knowledge_eligible']=True
for cid in ['X12','X15']:va(cid,'likely_true','官方估算有明确口径，但页面注明重刊修正数据标签且修正日未知；历史版本未锁定，不纳入本次严格Verified集合。',['S11'],fam=['FEIA_VORTEXA'])
for cid in ['X05','X06','X07']:va(cid,'uncertain','证实报道中存在交战方声称，不能证实封锁完成、击沉或命中；无独立战场证据。',[{'X05':'LV01','X06':'LV02','X07':'LV04'}[cid]])
va('X08','likely_true','Reuters转载复述Platts通知，未取得对应原始原油通知；转载与Reuters不能计两源。',['S07'],fam=['FPLATTS_NOTICE_REPORTED'])
# Claim attribution可以核对报道，不等于claim现实核实。
for cid in ['C006','C023']:CM[cid]['attribution_status']='source_verified'
narratives=[dict(assessment_id='NA01',observer='A9527',claim_refs=['C002','C074','C100'],frame='控制权、战略成本与霸权信誉决定战争及油价路径',as_of=CUT),dict(assessment_id='NA02',observer='A9527',claim_refs=['C105'],frame='明确乐见美国陷入不利；结尾保留随事件更新判断',as_of=CUT),dict(assessment_id='NA03',observer='AMODEL',claim_refs=['C057','C064','C080','C083'],frame='时间倍乘、控制到定价、收益独占构成主要证据断点',as_of=NOW),dict(assessment_id='NA04',observer='AMODEL',claim_refs=['C101'],frame='反讽铺垫不能脱离后续否定当成主播肯定预测',as_of=NOW)]

arguments=[]
def argument(i,title,paths,conclusion,weak,limits,shortcuts=None,atype='causal',analogy=None):
    # paths元组：(from,to,expression_level,inference_mode,局限)。图中节点全部是Claim。
    steps=[]
    for j,(f,t,level,mode,lim) in enumerate(paths,1):
        steps.append(dict(step_id=f'{i}-E{j}',from_claim_refs=[f],to_claim_ref=t,relation='SUPPORTS_CONDITIONALLY',inference_mode=mode,expression_level=level,evidence_refs=CM[f]['source_segment_refs']+CM[t]['source_segment_refs'],limitations=lim))
    nodes=set();incoming=collections.defaultdict(int);adj=collections.defaultdict(list)
    for e in steps:
        f=e['from_claim_refs'][0];t=e['to_claim_ref'];nodes.update([f,t]);adj[f].append(t);incoming[t]+=1
    queue=collections.deque(n for n in nodes if not incoming[n]);d={n:0 for n in nodes};seen=0
    while queue:
        n=queue.popleft();seen+=1
        for t in adj[n]:
            d[t]=max(d[t],d[n]+1);incoming[t]-=1
            if incoming[t]==0:queue.append(t)
    assert seen==len(nodes),(i,'cycle')
    level_counts=collections.Counter(e['expression_level'] for e in steps)
    args=dict(argument_id=i,title=title,argument_type=atype,premises=sorted(nodes-{e['to_claim_ref'] for e in steps}),steps=steps,conclusion=[conclusion],inference_mode=sorted(set(e['inference_mode'] for e in steps)),expression_level=sorted(level_counts),hop_count=max(d.values()),limitations=limits,most_fragile_step=weak,creator_explicit_shortcuts=shortcuts or [],inferential_distance=dict(edge_count=len(steps),longest_path_length=max(d.values()),model_bridge_count=level_counts['model_reconstruction'],explicit_shortcut_count=len(shortcuts or []),strongly_implied_edge_count=level_counts['strongly_implied'],explicit_edge_count=level_counts['explicit']),graph_scope='representative_reconstruction_of_important_chain_not_all_possible_edges',claim_refs=sorted(nodes))
    if analogy:args.update(analogy)
    arguments.append(args)
E='explicit'; I='strongly_implied'; M='model_reconstruction'
argument('AR01','不完全封锁也能影响运输成本', [('C009','C010',E,'causal','地形不能单独证明当前武器可用'),('C010','C014',E,'causal','风险是否足以改变保险条款需报价'),('C014','C015',E,'causal','成本转嫁取决于合同和市场'),('C015','M02',M,'causal','现货交付桥缺乏实际价差'),('M02','M01',M,'causal','现货、期货基准不可混合'),('M01','C025',M,'speculation','无弹性模型不能推20%至30%幅度'),('C010','C016',E,'causal','通行密度不是唯一供给约束'),('C016','C018',E,'causal','仓储和绕行会缓冲')],'C025','AR01-E6','风险成本方向有经济合理性；不直接推出全球基准价涨幅。实际减少20%没有观测。',[dict(from_claim='C002',to_claim='C025',note='主导权→首周价格；显式捷径另存，不计入扩展路径')])
argument('AR02','从公开讲话推断美国失控', [('C021','C020',E,'elimination','未见庆祝不等于排除其他进展'),('C023','C024',E,'speculation','公开威慑语言不能证明心理状态'),('C024','C020',E,'speculation','可有多种谈判策略解释')],'C020','AR02-E2','没有情报与替代假说检验，动机不能当事实。')
argument('AR03','首周撤退分支', [('C026','C028',E,'speculation','分叉不是概率模型'),('C028','C031',I,'causal','伊朗能控制并选择性开放未证实'),('C031','C032',E,'causal','复航速度、库存与风险溢价可能延迟')],'C032','AR03-E2','撤退不必导致国际协调成功，供给恢复也不唯一决定价格。')
argument('AR04','追加行动分支到120', [('C033','C034',E,'speculation','能力不等于行动意愿或发生'),('C034','C035',E,'causal','攻击规模到涨幅缺流量/弹性测算')],'C035','AR04-E2','约一个月的起点和具体油种不明；不是已发生的袭船事实。')
argument('AR05','储油容量推到60天停战上限', [('C057','C058',E,'speculation','容量/库存概念不清；减产幅度未知'),('C058','C059',E,'statistical','乘2是安全系数而非置信区间'),('C059','C060',E,'causal','物理仓储天数不决定政治承受上限'),('C060','C061',E,'causal','海湾行动一致性未知'),('C061','M05',M,'causal','撤资可行性和政策弹性待证'),('C062','M05',M,'causal','投资总额不等于可迅速动用的政治杠杆'),('M05','C063',M,'causal','反战力量可能不足以决定战略'),('C063','C064',E,'causal','能促和不能推出绝对60天')],'C064','AR05-E3','最脆弱处是存储测算变成任何国家必然妥协；另有原研报未读、30×2人为放宽、封锁和战争终点不同。',[dict(from_claim='C057',to_claim='C064',note='油储天数→绝对停战期限')])
argument('AR06','历史封锁经验外推', [('C065','C106',E,'analogy','未给原案例，无从确认曾完全封锁60天'),('C106','C064',I,'analogy','以往妥协不保证本次上限')],'C064','AR06-E1','历史集合与样本选择均未知，不能借此增强60天确定性。',atype='historical_analogy',analogy=dict(source_case='未命名的过去霍尔木兹封锁',target_case='2026本轮冲突',shared_mechanism='持续中断产生经济成本并迫使谈判',limits_of_analogy='封锁强度、替代渠道、参与方与时间均未匹配'))
argument('AR07','中东失利外推到东亚', [('C043','C047',E,'analogy','经济不可替代不等于战场胜率'),('C045','C046',E,'speculation','100扩大100倍无生产数据'),('C046','C047',E,'causal','弹种、良率、部署与防御效能不同'),('C047','C048',I,'speculation','战区态势不能证明必然统一'),('C047','C049',I,'speculation','能力推国家意图缺证据')],'C049','AR07-E2','一战区经验不足推出东亚结果；产能、后勤、地理、目标均有差异。',atype='strategic_analogy',analogy=dict(source_case='伊朗抵抗美国',target_case='中国与美国在东亚竞争',shared_mechanism='工业与持续作战成本制约军事权力',limits_of_analogy='国家能力和海域条件不同，不推出相同胜负'))
argument('AR08','战败与霸权信誉', [('C071','C073',E,'analogy','历史叙事压缩长期多因演变'),('C072','M07',M,'causal','武器非插电即在任何地区有效'),('M07','C073',M,'causal','各国意愿、联盟与升级成本未定'),('C073','C069',E,'causal','挑战增加不等于霸权立即消失')],'C069','AR08-E3','军事信誉只是霸权组成因素，不可省略金融、技术、联盟及长期轨迹。',atype='historical_analogy',analogy=dict(source_case='西班牙无敌舰队对英失败；年份原话未给',target_case='美国在伊朗作战及全球地位',shared_mechanism='军事挫折可能削弱威慑信誉',limits_of_analogy='不能把单次海战等同帝国即时衰落；历史因果未核'))
argument('AR09','控制海峡到长期高油价和收益独占', [('C081','C082',I,'causal','控制委内瑞拉不足以证明控制全球供应，且控制的定义未核'),('C082','M03',M,'causal','需证明边际供应与替代弹性'),('M03','C086',M,'speculation','缺价格形成模型与期限'),('C082','C083',E,'causal','控制运输不等于所有生产者租金归美国'),('C083','M04',M,'causal','公司收益、税收和补贴分配不同'),('M04','C088',M,'speculation','没有实际补贴政策证据')],'C088','AR09-E4','航运控制、实物流、现货、期货、基准报价权与财政租金必须拆开；100/126/120及连任选举对象都待核。',[dict(from_claim='C080',to_claim='C086',note='海峡美国控制→长期100/120'),dict(from_claim='C082',to_claim='C088',note='供应定价控制→国内廉价油')])
argument('AR10','战事和AI资本支撑', [('C091','C092',E,'causal','军用有效不等于商业估值兜底'),('C003','C093',I,'speculation','意图不能证明实际资金流'),('C093','M06',M,'causal','缺跨境分资产流向'),('M06','C094',M,'causal','缺AI企业融资与估值传导'),('C092','C094',I,'causal','应用与融资两条路径不能相互替代')],'C094','AR10-E4','没有观察证明资金具体进入AI，不能因战事存在就核实泡沫延续。')
argument('AR11','美元短期避险与长期信用透支', [('C097','C098',E,'causal','规模不能自动提供避险需求'),('C098','C099',E,'speculation','由短期支撑推长期加速衰落没有中间时序数据')],'C099','AR11-E2','时间尺度不同可并存，不构成形式矛盾；利差、政策和替代货币遗漏。')
argument('AR12','获胜后的伊朗更愿示好', [('C079','C103',I,'speculation','共同条件为伊朗控制，油价回落本身不是外交善意的原因'),('C102','C101',E,'elimination','战败才恐袭的必要条件未经验证')],'C103','AR12-E1','共同情景不能当独立因果；宗派、国内政治、代理人和安全困境可能延续。')
argument('AR13','Platts规则响应：模型补充分析', [('X08','X09',M,'causal','涉及原油审查和成品油规则，不能直接证明二者同一决定'),('X10','X11',I,'direct','同日顺序为审查→继续发布，不等于运费未变')],'X09','AR13-E1','只构成有限市场基础设施事件；LNG评估流程的具体变化未核实；视频没有明确提到Platts。')

mechanisms=[dict(mechanism_id='ME01',status='candidate',name='通道威胁—保险及运力—交付成本',argument_refs=['AR01'],nodes=['威胁可信度','保险覆盖和价格','船东通行决策','实际运量','到岸/交付成本'],limits='替代路线、库存和合同可以缓冲；不直接给出期货涨幅'),dict(mechanism_id='ME02',status='candidate',name='出口受阻—储油空间耗尽—被迫减产',argument_refs=['AR05'],external_claim_refs=['X13'],nodes=['外运下降','库容占用增加','储油空间用尽','生产约束'],limits='须区分产地库容与消费库存；不包含60天政治上限'),dict(mechanism_id='ME03',status='candidate',name='避险资金流入与产业融资的条件传导',argument_refs=['AR10'],nodes=['原居地风险上升','目的地资产选择','资产类别配置','企业融资可得性'],limits='终点进入AI是待证条件，不能从美元资产流入直接得出')]
registry_search=dict(searched=['workspace inventory','golden_report.md','golden_sample_002/golden_sample_002.json:13_theses'],result='已检索本地摘要及GS002金融结构Thesis；无正式全库Registry。GS002为较晚样本，只作目录比对，绝不作2026-03证据。',scope='local_partial_registry',full_registry_available=False)
theses=[]
for i,t,ars,needed,decision in [('TH01','9527认为海峡最终控制者决定战争后的油价区间，而不仅是即时封锁。',['AR01','AR03','AR04','AR09'],'需区分控制、复航、净供给、期限结构及价格，进行多事件检验。','new'),('TH02','9527认为对伊战争可能暴露美国实力边界并加速其全球主导权衰退。',['AR07','AR08','AR11'],'需跨时间比较盟友行为、军力、金融与国际影响力指标；本次未证实结构过程。','new'),('TH03','9527认为地缘动荡能暂时给美国AI和美元带来资金支持，但透支长期信用。',['AR10','AR11'],'需资本流向和美元信用长期序列；与GS002中美资本竞争仅主题相关。','related')]:
    trs=[]
    for ar in arguments:
        if ar['argument_id'] in ars:
            for cid in ar['claim_refs']:
                for ss in CM[cid]['source_segment_refs']:
                    srcid=next(x['source_id'] for x in source_segments if x['source_segment_id']==ss)
                    trs.append(dict(argument_id=ar['argument_id'],claim_id=cid,source_segment_id=ss,source_id=srcid))
    theses.append(dict(thesis_id=i,statement=t,status='candidate_unverified',resolution=decision,resolution_provisional=True,registry_search=registry_search,argument_refs=ars,traceability=trs,support_and_falsification=needed,verified_knowledge_eligible=False))
# Forecast逐Claim建立；条件、窗口均保留原话语义，不从截止时间机械推断日期。
forecast_specs={
4:('AI融资','增加','unknown','中东资本避险赴美','plausible','low'),5:('地区主导权','美国取得','首周','伊朗首周屈服','likely','low'),25:('油价；基准未明','上涨到80–90，约20%–30%','战争头一周；起点待核','基线：冲突未迅速终结且未出现极端破坏','likely','medium'),26:('美国行动','撤退或升级','首周后','首周未使伊朗屈服','possible','low'),28:('海峡通行','开放','首周后未明','美国撤出；国际压力形成','likely','low'),29:('胜利叙事','声称胜利','约一周','美国撤出','possible','low'),31:('伊朗出口','继续通行','撤退后','伊朗选择性开放','likely','low'),32:('油价','适度回落或停止上涨','撤退后未明','美国撤退且伊朗开放','likely','low'),34:('美国袭击亲伊朗船运','可能实施','升级阶段','美国未控制海峡而追加行动','possible','low'),35:('油价；基准未明','约120','首周后追加行动约一个月','升级并扰乱海运、成本提高','plausible','medium'),37:('油价；基准未明','90–110并可能回落','约40天','撤退/和谈关联；与120分支的相容性待核','possible','low'),39:('美国军事行动','撤退或谈判','约40天','缺乏战略目的且持续受阻','possible','low'),40:('国内选举影响','可被包装化解','unknown','通过击杀领袖宣称胜利','possible','low'),42:('封锁持续性','最终结束','unknown','伊朗自身也需要出口','near_certain','low'),47:('美国东亚军事行动','无法有效对抗','unknown','假设中国产能极大优势','near_certain','low'),48:('台湾统一','将实现，仅剩成本','unknown','主播认定的力量优势','near_certain','unresolvable'),55:('盟友参战及分担','下降/缺席','unknown','各方判断美国打不了','likely','low'),60:('域外国家对伊妥协','全部妥协','封锁两个月','伊朗持续实控封锁','certain','low'),61:('海湾对美压力','促谈/可能翻脸','长期中断期间','美国不能恢复通行','likely','low'),63:('战争结束','迫使停战','两个月论证内','海湾资本压力与反战合力形成','near_certain','low'),64:('美国战争持续时间','不超过60天','60天上限；起点和终点定义待核','叙述通常无条件，但论证依赖持续海峡中断','certain','medium'),67:('胜负/谈判','伊朗大胜美国求和','封锁超过40天','伊朗持续控制','near_certain','low'),68:('以色列利益','被美国牺牲','和解后','美国伊朗和解','likely','low'),69:('美国全球主导权','衰退','趋势明显但过程很长','美国失去中东主导权','likely','low'),73:('全球对美挑战','增加','战败后未明','美国战败暴露实力边界','likely','low'),75:('油价波动','缓慢上涨，无巨大波动','约一个月','当前局面延续；未明示失效触发器','likely','low'),76:('油价急涨后走势','回调','急涨后未明','突发大涨且预期尚未到位','likely','low'),78:('美国战争胜负','明确','约40天','unknown','very_likely','low'),79:('油价','回落','伊朗控制后','伊朗控制海峡','likely','low'),80:('油价','100–126（ASR待核）','相当长','美国控制海峡','likely','low'),83:('油价新增租金归属','仅美国获益','美国控制之后','供应定价控制且油价提高','certain','low'),85:('油价','六七十或七八十','伊朗获胜后','伊朗掌握海峡','possible','low'),86:('油价','100甚至120','长期','美国获胜','possible','low'),88:('美国国内用油安排','相对廉价','unknown','美国主导并获高油价收益','likely','low'),89:('美国收入与物价分配','资本获利普通人仅温饱','unknown','上述高油价及补贴情景','likely','unresolvable'),90:('能源/美元结构','转向新能源','未来未明','美国无法主导当前局面','likely','unresolvable'),92:('AI估值支撑','增强','unknown','军事和信息战应用形成价值','plausible','low'),94:('AI资金来源','增加','近期未明','避险资本进入美国并配置AI','plausible','low'),99:('美国/美元信用','长期衰退加速','unknown','依靠动荡维持信用','likely','unresolvable'),100:('本轮战争结果','美国失败','本轮战争','基线综合判断','likely','low'),101:('美国本土所谓圣战','不太会发生','unknown','伊朗在正面战场不败的解释背景','likely','low'),103:('伊朗对邻国政策','更加友好','控制秩序后','伊朗主导海峡','likely','low'),106:('各方妥协时点','早于以往','本轮冲突','记取过去代价','likely','low')}
for c in claims:
    if c['claim_type']!='forecast':continue
    cid=c['claim_id']
    if cid.startswith('C'):tar,dr,w,cond,mod,res=forecast_specs[int(cid[1:])]
    else:
        spec={'X01':('Brent','120美元/桶','战争超过三周后','外运受阻使储罐满并减产','possible','medium'),'X02':('Brent','200美元/桶','unknown','海峡全面封闭的极端情景','possible','medium'),'X03':('Brent','60–70美元/桶','战争快速结束后','战争快速结束','possible','medium'),'X14':('Brent','超过100美元/桶','unknown','伊朗攻击邻国能源设施','possible','medium')}
        tar,dr,w,cond,mod,res=spec[cid]
    # 数量不是情态；保留可观察情态词，不把百分比塞进certainty。
    c['reference_time']=w
    c['certainty_expressed']=('不太有可能' if cid=='C101' else ('大概率' if cid=='C100' else ('绝对不可能超过' if cid=='C064' else None)))
    forecasts.append(dict(forecast_id='FC-'+cid,claim_id=cid,forecaster_id=c['claimant_id'],made_at=c['asserted_at'],made_at_basis=c['asserted_at_basis'],knowledge_cutoff=CUT,target=tar,direction=dr,prediction_window=w,window_start=None,window_end=None,conditions=cond,scenario_type='extreme_scenario' if cid=='X02' else ('baseline_forecast' if cid in ['C025','C075','C100'] else 'conditional_forecast'),modal_strength=mod,original_modality=raw(next(x['cue_start'] for x in source_segments if x['source_segment_id']==c['source_segment_refs'][0]),next(x['cue_end'] for x in source_segments if x['source_segment_id']==c['source_segment_refs'][0])) if cid.startswith('C') else '新闻转述可能性；原研报未读',modal_strength_assigned_by='AMODEL',modality_polarity='negative' if cid=='C101' else 'positive',resolvability=res,resolution_criteria=dict(creator_specified=c['statement'],model_proposed='先锁定目标定义、起点、条件触发证据；价格需确定油种、币种、期货/现货及收盘/盘中，政治胜负需预注册判准。',human_approved=None,accepted_for_scoring=False),evaluation_status='not_scored_no_post_cutoff_outcomes'))
heuristics=[dict(heuristic_id='HC01',status='candidate',rule='区分公开宣称与实际可执行能力，追问是否真正控制关键通道。',observed_in_arguments=['AR01','AR02','AR03'],source_segments=['SS-C019','SS-C024','SS-C107'],why_method_not_case_conclusion='同一规则被用于海军消灭、战争持续话语及空域开放三个判断。',known_limits='不能反向把所有声明视为虚假。',possible_counterexamples='可信且已落实的公告确能准确说明能力。',failure_modes='以怀疑声明为由任意揣测动机。'),dict(heuristic_id='HC02',status='candidate',rule='把冲突分成阶段，比较各方持续承担成本与外部支持的能力。',observed_in_arguments=['AR04','AR05','AR08'],source_segments=['SS-C035','SS-C056','SS-C059'],why_method_not_case_conclusion='时间分段和成本承受规则可跨冲突复用；60天是本次应用值，不是方法本身。',known_limits='安全系数不是经验证的政治上限。',possible_counterexamples='各方可接受高成本使冲突长期化。',failure_modes='随意翻倍制造精确期限；用愿望代替代价函数。')]

review('Critical','measurement_definition',['C057','C058','AR05'],'产地可用储油空间与消费库存耗尽混淆，影响整条60天链。','回听20:20–20:50并取得JPM原研报及库容/流量/减产假设。')
review('Critical','excessive_inference',['C064','AR05'],'30×2不能证明战争绝不超过60天。','分离物理约束与政治结果，登记可反证的期限定义。')
review('Critical','excessive_inference',['C082','C083','AR09'],'控制航道被升级成全球定价权和美国独享新增收益。','补边际供给、替代来源、市场份额、合同与收入分配证据。')
review('Critical','event_timing',['S05','LV06','LV07','LV08','LV09','LV10'],'滚动页面包含cutoff后内容；历史版本不可恢复。','仅准入时间明确条目；未知改动仍标版本风险，不将后续页当原页。')
review('High','source_conflict',['C001','X01','X02'],'大摩、摩根大通和德银预测来源/条件混在一起。','核音与原研报，机构不自动替换。')
review('High','numerical_conflict',['C041','X04','X15'],'30–40%全球油供可能混用海运出口分母和年份。','匹配同年同口径后判断，不自动替换20%。')
review('High','numerical_conflict',['C036','C037','C078'],'一周+一个月、四周、40天互相不等价。','保留原始相对窗口；核查锚点再转换日历日。')
review('High','asr_uncertain',['C080','C086','COR13'],'100到126与后文100/120不同。','听音确认数字；两个说法暂分开并关联，不能默改。')
review('High','source_dependency',['S02','S03','S06','S07','S08'],'同源ASR以及Reuters转载不能累加独立证据。','按原始讲话/统计/通知起源计数，文章可分多个证据家族。')
review('High','unsupported_claim',['X05','X06','X07','C027'],'封锁、击沉、航母后退不能仅靠战方/转述核实。','查独立船位、卫星/航运资料；与宣布行为分开。')
review('High','argument_bridge',['M01','M02','AR01'],'运输保险成本到期货涨幅缺可交付供给和风险定价节点。','取得同基准价格、运费保险、库存及替代供应时序。')
review('High','argument_bridge',['M03','M04','AR09'],'全球定价和美国国内补贴之间缺财政/公司收益分配节点。','不得登记成已存在政策；核制度和资金渠道。')
review('High','argument_bridge',['M06','C093','C094'],'资本赴美、中国以及流入AI没有数据支持。','寻找cutoff前跨境流量/资产配置/融资证据。')
review('High','numerical_conflict',['C045','C046'],'六七比100与1万比六七缺同弹种同时间产量来源。','原始鲁比奥讲话及实际生产能力分别核查。')
review('High','unsupported_claim',['C065','AR06'],'未能识别历史封锁60天皆妥协的案例集合。','要求事件、日期和封锁定义；没有则不入Verified。')
review('High','excessive_inference',['C070','C071','AR08'],'无敌舰队挫折被压缩成国家即时衰落。','核历史时间尺度及其他原因；保持有限类比。')
review('High','forecast_lineage',['C053','C104'],'主播追述往期预测与比喻，未取得原节目。','检索原版本、原时点和原措辞；不反填历史Forecast。')
review('High','unsupported_claim',['C048','C049','C050','C081'],'台湾结果必然、中国国家战略、韩国认知、美国控制委内瑞拉均未得原始证据。','区分主播判断和国家实际政策，补各自来源。')
review('High','source_conflict',['S11','X12','X15'],'EIA正文注明重刊改标签，但修正时间未知。','获取2026-03-03前存档；当前版本只作核查线索。')
review('High','registry_extension',['X08','X09','X10','X11','AR13'],'未读Reuters原页后续版本；LNG流程改变未取得可准入原通知。','分原油/成品油/运费/LNG，已核查范围不外推。')
review('High','source_conflict',['C030','EV09'],'计划重开空域不能写成已经安全开放。','核实际开放时刻与航班运行；原话仍保留。')
review('High','unsupported_claim',['C091','C092'],'AI在本轮战争的实际使用与估值支撑两层均缺原证。','核军用应用再单独检验商业价值传导。')
review('High','unsupported_claim',['C022','C096'],'特朗普谈判/美元承诺系二手引用，原始采访未读。','找cutoff前原采访，维持reported_only。')
review('Medium','speaker_slip_review',['C051','AN04'],'国庆节与春节前时间错位。','回听后再判ASR或口误，不能按常识静默纠正。')
review('Medium','entity_resolution',['C088','AN09'],'“为了连任”的主体及选举对象不清。','确认原音与上下文，不补写宪法例外或第三任假说。')
review('Medium','measurement_definition',['C008','C011','C012','C013'],'30公里、几百船、吨位及6分钟缺地点、统计时点和船型。','核海图与航运统计；地理宽度不等于航道宽度。')
review('Medium','measurement_definition',['C017','C108'],'20%是设想、70是举例基值，不是已核市场观测。','保留projected/estimated，勿并入观察时间序列。')
review('Medium','claim_duplication',['C025','C075','C079','C085','C080','C086'],'同方向但窗口/数值不同；不能全部合并或计作独立新证据。','维持场景与版本关系，听音后处理126。')
review('Medium','process_boundary',['TH01','TH02','TH03'],'战争数日与单次通知不足证明结构性变迁。','补跨时间观测；现阶段StructuralProcess=0。')
review('Medium','attribution_chain',['EX01','C076'],'市场预期是主播推断，非调查或隐含波动率测量。','补具体群体和当时市场量，不作总体共识。')
review('Medium','contradictory_assessment',['C020','C077','C075','C035'],'逐步失控与部分主动、慢涨与条件120未必逻辑冲突。','比较时点、条件和度量后才能CONTRADICTS。')
review('Medium','registry_extension',['TH01','TH02','TH03'],'只有本地样本目录，没有完整Thesis注册表。','全库查same/update/related/new；目前决策为provisional。')
review('Medium','event_timing',['S01','S13'],'发布时间来自追加文件，录制时间未知。','用平台元数据交叉核对；字幕时间不加到发布时间。')
review('Medium','unsupported_claim',['C087','C062'],'历史利润归属和主权基金资本作用未给统计。','核年份、利润口径及可撤出头寸，不据规模自动推政治控制。')
review('Low','asr_uncertain',[x['correction_id'] for x in corrections if x['semantic_confidence']=='high'],'专名与常用词语义纠错可信，但尚未听音。','候选规范化与raw分开，回听后才accepted。')
# 每条未评分预测都有明确待办；用组项避免重复Queue污染。
review('High','forecast_lineage',[f['forecast_id'] for f in forecasts],'多数预测缺油种/窗口锚点/条件阈值或胜负定义；所有model判准未获人工批准。','逐条锁定标准后另建后验评估；本样本不使用cutoff后结果。')
# 合并同一资金→AI命题的首述与后段展开，不把重复表达计成第二个预测。
CM['C004']['source_segment_refs'].extend(CM['C094']['source_segment_refs'])
claims[:]=[c for c in claims if c['claim_id']!='C094']
forecasts[:]=[f for f in forecasts if f['claim_id']!='C094']
for o in occurrences:
    if o['claim_id']=='C094':o.update(claim_id='C004',occurrence_type='elaboration',information_gain='medium')
seen_occ=set();dedup_occ=[]
for o in occurrences:
    key=(o['claim_id'],o.get('source_id'),o.get('cue_start'),o.get('cue_end'),o.get('source_segment_id'))
    if key not in seen_occ:dedup_occ.append(o);seen_occ.add(key)
occurrences[:]=dedup_occ
# C079与C103只共享控制权条件，不能把油价回落错画为外交善意的原因。
arguments[:]=[a for a in arguments if a['argument_id']!='AR12']
def canonical(v):
    if isinstance(v,dict):return {k:canonical(x) for k,x in v.items()}
    if isinstance(v,list):return [canonical(x) for x in v]
    return {'C094':'C004','FC-C094':'FC-C004'}.get(v,v) if isinstance(v,str) else v
arguments[:]=canonical(arguments);theses[:]=canonical(theses);reviews[:]=canonical(reviews)
for a in arguments:a['claim_refs']=sorted(set(a['claim_refs']))
assessments[:]=[a for a in assessments if a['claim_id']!='C094']
CM={c['claim_id']:c for c in claims}
issues=[
dict(issue_id='IS01',classification='schema_field_issue',problem='滚动Source当前标题、条目发布时间、条目有效时间和编辑时间无法仅靠published_at表示。',proposal='SourceVersion辅助记录entry_id、item_published_at、captured_at、valid_from/to、edited_at、content_hash、cutoff_status；未知即null。',new_core_object_needed=False),
dict(issue_id='IS02',classification='schema_field_issue',problem='一篇汇编新闻含多个讲话/机构原始起源，单一source_family_id容易误计独立性。',proposal='增加证据片段级origin_family_ids与derived_from，独立性按命题评估。',new_core_object_needed=False),
dict(issue_id='IS03',classification='schema_field_issue',problem='油储可指消费库存、产地库存或剩余库容，measurement_type=stock仍不足。',proposal='Observation增加storage_role、capacity_total/used/free、inventory_location、flow_balance_definition；未给则null。',new_core_object_needed=False),
dict(issue_id='IS04',classification='registry_issue',problem='市场基础设施变化不宜新建核心本体。',proposal='Event子类型候选market_infrastructure_event；资产、港口、合约、报价过程、实施/终止时间作为字段。',new_core_object_needed=False),
dict(issue_id='IS05',classification='schema_field_issue',problem='forecasts需共同父情景、触发条件、互斥程度和窗口锚点；possible/likely不能表示“不太可能”的极性。',proposal='增加scenario_parent、condition_expression、window_anchor、modality_polarity及original_modality；本次均为显式候选字段。',new_core_object_needed=False),
dict(issue_id='IS06',classification='schema_field_issue',problem='声学未核、语义高置信与口误三者不可混。',proposal='correction.applied与acoustic_confidence独立；未听音不写speaker_slip_confirmed。',new_core_object_needed=False),
dict(issue_id='IS07',classification='registry_issue',problem='Argument关系注册表未提供，统计/演绎方式不全。',proposal='本包SUPPORTS_CONDITIONALLY作为待注册关系，不宣称生产Schema已批准。',new_core_object_needed=False),
dict(issue_id='IS08',classification='prompt_issue',problem='附加提示称Platts影响原油、成品油和LNG，不等于证据已经验证全部品种。',proposal='用户授权提示为任务规范；其中事实仍需核，LNG未核须Review。',new_core_object_needed=False),
dict(issue_id='IS09',classification='schema_field_issue',problem='主张含“如果发生X”不是无条件现实；控制权与宣称封锁等状态容易混写。',proposal='Claim保留条件与对象状态；Event记录statement_event，现实封锁程度以观察单独证明。',new_core_object_needed=False),
dict(issue_id='IS10',classification='core_ontology_issue',problem='本期未发现必须增加核心对象的证据。',proposal='StructuralProcess、Contradiction均可为0；优先细化Event、Observation、SourceVersion和Forecast。',new_core_object_needed=False)]

closure_states=[dict(state='official_or_adviser_claim',evidence=['X05'],assessment='报道存在声明，发布者层级须保留'),dict(state='operator_suspension',evidence=['X08'],assessment='Reuters转述Platts收到停航通知，需具体船公司原公告'),dict(state='traffic_collapse',evidence=[],assessment='未取得可比AIS量化序列'),dict(state='no_vessel_can_pass',evidence=[],assessment='未证实'),dict(state='complete_legal_or_military_blockade',evidence=[],assessment='未证实；不能由上面任一状态自动推出')]
quarantine=[dict(source='S05',entries=['LV06','LV07','LV08','LV09'],reason='post_cutoff',used_in_arguments=False),dict(source='S05',entries=['LV10'],reason='review_required',used_in_arguments=False),dict(source='Platts 030326 freight clarification',reason='2026-03-03但无时刻，未准入',used_in_arguments=False),dict(source='EIA 2026-04/07/09相关文章及Reuters 2026-04-02检索结果',reason='post_cutoff搜索暴露，未读为本期证据、未评分',used_in_arguments=False),dict(source='EIA页脚2026-09数据、转载站点2026-06页眉',reason='dynamic_chrome_post_cutoff_excluded',used_in_arguments=False)]
summary=dict(source_count=len(sources),source_family_count=len(set(s['source_family_id'] for s in sources)),claim_count=len(claims),creator_claim_count=sum(c['corpus_origin']=='creator_transcript' for c in claims),external_context_claim_count=sum(c['corpus_origin']=='external_context_not_creator' for c in claims),model_claim_count=len(bridges),claim_occurrence_count=len(occurrences),event_count=len(events),structural_process_count=0,indicator_count=len(indicators),observation_count=len(observations),argument_count=len(arguments),mechanism_count=len(mechanisms),thesis_count=len(theses),forecast_count=len(forecasts),contradiction_count=0,heuristic_count=len(heuristics),review_queue_count=len(reviews),review_severity_counts=dict(collections.Counter(r['severity'] for r in reviews)))
executive=dict(status='extraction_complete_review_pending_not_verified_knowledge_base',knowledge_cutoff=CUT,publication_basis='user_authorized_addendum',recorded_at=None,max_uncertainties=['未听音，专名/数值纠错均未接受','JPM储油原研报、海峡流量和价格基准不足','滚动网页缺历史版本，既有条目也有后改风险','60天上限、航道控制到定价权和AI资金路径缺证'],core_structural_judgment='忠实保留控制权—成本—持续时间—油价情景框架；未发现足以确认长期StructuralProcess的证据。',post_cutoff_contamination=dict(encountered=True,accepted_into_creator_reconstruction=False,residual_risk='来源在cutoff后抓取，无法完全排除未披露修订；EIA修订不入严格Verified。',quarantine_refs='auxiliary.post_cutoff_quarantine'),audio_review_performed=False,verified_knowledge_scope='仅Platts自身已发布通知范围的X09/X10/X11；其余不自动升级',completion_scope='覆盖899字幕cue的语义分段与重要命题；不是每个口头填充词都建Claim。',source_family_count_caveat='Source记录层数量不等于每Claim的独立证据数。')
qa={
'A 核心3—5条Argument Chain':'① AR01：岸基威胁→保险/运力→交付成本→价格，幅度桥缺失。② AR05：储油20多天→30→60→资本及政治压力→停战，政治上限最薄弱。③ AR09：控制海峡→供应/定价→高价/收益→国内廉价油，定价与收益归属跳跃最大。④ AR08：战场受挫→信誉受损→全球挑战→霸权衰退，历史类比有限。⑤ AR10：战争应用/资金避险→AI价值和融资，流入AI未证。',
'B 四层分离':'现实层仅承认已核Platts通知行为，海峡完全封锁和战果未核；来源层X05–X07是交战方经新闻转述的声称，X01–X03是机构条件预测；9527解释层C007/C024/C057–C064把目标、言辞及储油转化为控制与期限；结构推论层TH01–TH03关于长期油价、霸权和资本，均非已验证现实。',
'C StructuralProcess证据':'本期为0。战争持续数天、Platts同日审查及继续发布，是事件及更新关系；没有本次cutoff内足够跨期证据确认市场结构永久改变。美元与霸权长期衰退保留为Thesis/Forecast。',
'D 捷径、桥接与最长路径':'详见各Argument计算值。AR01最长6边，3条模型边；AR05最长7边，3条模型边；AR09最长4边，4条模型边。显式捷径独立储存，不用它缩短扩展图；路径长度是本次代表性重建的边数，不宣称唯一真实推理长度。',
'E 分析方法':'HC01看可执行能力而非声明，HC02按阶段比较持续成本。均只算Candidate；单期无法证明稳定或有效，30天翻倍不升级为通用可靠方法。',
'F 不能进入Verified Knowledge':'60天绝对上限、美国必败、油价指定数值、伊朗完全封锁、命中/击沉/900公里后退、军工1万对六七、中国战略与台湾必然结果、全球高油价收益美国独占、赴美资本必进AI、美元必加速衰落。原声错误未排除，过去“预测过”也不等于当时存在已登记Forecast。',
'G 核心Ontology是否缺失':'没有必须新增核心对象。暴露的是SourceVersion、库容角色、情景条件和报价过程的字段及辅助对象不足；market_infrastructure_event是Event子类候选，不能悄悄扩成新核心对象。',
'H 未来30期复用':'Actor：各国、IRGC、Platts、研究机构。Indicator：实际通行桶/日、船数、停航比例、保险/运费、产地剩余库容、生产、同合约现货/期货价差。StructuralProcess：本次不建，待累计序列。Mechanism：ME01/ME02优先，ME03待数据。Thesis：TH01及TH02持续反证，TH03核资本流。Heuristic：HC01/HC02作为候选追踪成功及失败。',
'附加A 决定油价的变量':'主播明确提到控制者、战事时长、运量、保险、产油、需求、储油和预期；模型需补净供给、可用库容、替代路线、库存位置、油种/基准/合约、现货可交付性及期货风险溢价。缺数据时不能定量分配贡献。',
'附加B 主播与新闻核心变量':'不同。标题突出战火与价格能涨多高；正文机构情景更关注中断时长、全面封闭、基础设施和库容。9527进一步将最终控制权和美国战略承受力置于核心。120/200不都属于主播自己的预测，也不共享条件。',
'附加C 从军事到价格跨几步':'没有单一数字。AR01代表链7个节点/6条边：岸基条件→威胁能力→保险风险→货物成本→现货交付桥→期货定价桥→首周价格；其中地形起点的完整最长路径实际为C009→C010→C014→C015→M02→M01→C025。AR04显式只2边即能力→袭船设想→120，短不是充分而是省略多。',
'附加D explicit与model bridge':'AR01威胁、保费、转嫁、运力是explicit；现货交付和期货传导及涨幅是model_reconstruction。AR05“20多→30→翻倍→妥协”是explicit，资本撤出与美国政策响应桥是model。AR09供应/定价/收益独占是主播明确说出的跳跃，模型M03/M04把未证前提摊开，不能归给主播。',
'附加E V0.3压力测试结果':'滚动页必须entry级版本与cutoff，页面级日期不足；定价流程需要资产/港口/评估方式/规则状态维度。Platts原油审查、成品油报价准入和运费继续发布是不同事件，不能合称停止定价。LNG流程未核，追加提示本身不充当证据。'}
sections=[('01_EXECUTIVE_EXTRACTION_REPORT',executive),('02_SOURCES',sources),('03_TRANSCRIPT_CORRECTIONS',dict(accepted_ASR_corrections=[],candidate_corrections=corrections,needs_audio_review=[x['correction_id'] for x in corrections],normalization_applied=False)),('04_SOURCE_SEGMENT_ANNOTATIONS',annotations),('05_SEMANTIC_SEGMENTS',segments),('06_CLAIMS',claims),('07_CLAIM_OCCURRENCES',occurrences),('08_ACTORS',actors),('09_EVENTS',events),('10_STRUCTURAL_PROCESSES',[]),('11_INDICATORS_OBSERVATIONS',dict(indicators=indicators,observations=observations)),('12_POLICIES',policies),('13_EXPECTATION_SNAPSHOTS',expectations),('14_VERACITY_ASSESSMENTS',assessments),('15_NARRATIVE_ASSESSMENTS',narratives),('16_ARGUMENTS',arguments),('17_MECHANISMS',mechanisms),('18_THESES',theses),('19_FORECASTS',forecasts),('20_CONTRADICTIONS',[]),('21_CANDIDATE_HEURISTICS',heuristics),('22_REVIEW_QUEUE',reviews),('23_SCHEMA_ONTOLOGY_EXTRACTION_ISSUES_FOUND',issues),('24_GOLDEN_SAMPLE_SUMMARY',summary)]
data=dict(sections)
data['final_questions']=qa
data['auxiliary']=dict(source_segments=source_segments,source_versions=versions,closure_state_separation=closure_states,post_cutoff_quarantine=quarantine,registry_search=registry_search,relation_candidates=['SUPPORTS_CONDITIONALLY'],source_evolution=[dict(from_claim='X10',to_claim='X11',relation='temporal_evolution',not_contradiction=True)],scenario_crossrefs=[dict(claims=['C080','C086'],relation='numeric_variant_pending_audio'),dict(claims=['C025','C075'],relation='different_windows'),dict(claims=['C037','C035'],relation='condition_or_window_ambiguity')])
data['auxiliary']['extraction_decisions']=[dict(decision='merge_duplicate_claim',retired_id='C094',canonical_id='C004',reason='中东避险资金给美国AI续资的后段展开；保留SS-C094与Occurrence，不重复建Forecast'),dict(decision='omit_spurious_argument',retired_id='AR12',reason='油价回落与外交示好共享情景条件，不应画作因果；保留各Claim/Forecast')]
data['auxiliary']['registry_candidates']=dict(claim_types=sorted(set(c['claim_type'] for c in claims)),source_types=sorted(set(s['source_type'] for s in sources)),status='descriptive_local_values_not_production_schema_approval',note='未提供机器Schema与完整枚举注册表；正式导入前须映射。未使用未声明新核心对象。')
data['auxiliary']['snapshot_index']=dict(S04=['source_snapshots/initial_web.txt'],S05=['source_snapshots/initial_web.txt','source_snapshots/live_selected.txt'],S06=['source_snapshots/initial_web.txt'],S07=['source_snapshots/primary_selected.txt'],S08=['source_snapshots/platts_notices.txt'],S09=['source_snapshots/platts_notices.txt'],S10=['source_snapshots/platts_notices.txt'],S11=['source_snapshots/primary_selected.txt'])
save('golden_sample_003.json',data);save('claims.json',claims);save('source_segments.json',source_segments);save('claim_occurrences.json',occurrences);save('review_queue.json',reviews);save('sources.json',sources);save('source_versions.json',versions);save('raw_cues.json',cues)
save('normalization_candidates.json',dict(raw_preserved=True,accepted_corrections=[],candidates=corrections))
save('scenario_tree.json',dict(root='本轮冲突；绝不把所有分支合成单点预测',creator_branches=[f for f in forecasts if f['claim_id'].startswith('C')],external_scenarios=[f for f in forecasts if f['claim_id'].startswith('X')],exclusivity='部分条件互斥但多数窗口/触发未定义，不能强行配概率'))

# 全字段报告；每个对象独立可读，避免只给漂亮摘要而隐藏字段。
lines=['# MacroMind Golden Sample #003 · V0.3', '', '视频：《第六百二七期》霍尔木兹海峡争夺战，会如何主导油价波动？', '', f'知识截止：{CUT}。抽取完成；音频、原研报与历史网页版本仍待Review。', '', '本报告依用户授权执行V03及追加提示；转写和网页仅作为证据。null表示未知，不用模型猜测填空。全文数据另见同目录 golden_sample_003.json；逐字字幕与证据定位见 raw_cues.json / source_segments.json。', '']
def block(o):return ['```json',json.dumps(o,ensure_ascii=False,indent=2),'```','']
for title,value in sections:
    name=title.replace('_',' ');lines+=['## '+name,'']
    if isinstance(value,list):
        if not value:lines+=['none','']
        for ob in value:
            ident=next((v for k,v in ob.items() if k.endswith('_id')),None)
            if ident:lines+=['### '+str(ident),'']
            lines+=block(ob)
    else:lines+=block(value)
lines+=['## V0.3最终八问与本期追加五问','']
for q,a in qa.items():lines+=['### '+q,'',a,'']
lines+=['## 审计辅助材料（不新增核心Ontology）','']+block(data['auxiliary'])
(OUT/'golden_sample_003_report.md').write_text('\n'.join(lines),encoding='utf-8')
brief=['# Golden Sample #003 阅读导览','','完整报告按V0.3要求的24节及13问排列；JSON保留全部字段。','','**状态：抽取完成，Review待处理。没有使用3月3日17:30之后的战况或油价为主播预测评分。**','','## 主要发现','','1. 储油空间耗尽与消费库存耗尽不同；20多天→30→60不能证明政治停战上限。','2. 航道控制→定价权→美国独享收益缺关键证据。','3. 120与200必须附情景和归属；新闻中的200属于机构极端情景。','4. Platts部分报价规则变化属于有限Event；未建立StructuralProcess或Contradiction。','5. 未实际听音，所有ASR纠错保留候选。','','## 数量','']+block(summary)+['## 核心Argument距离','','|链|边数|最长路径|模型边|显式捷径|最脆弱处|','|---|---:|---:|---:|---:|---|']
for ar in arguments:
    m=ar['inferential_distance'];brief.append(f"|{ar['argument_id']} {ar['title']}|{m['edge_count']}|{m['longest_path_length']}|{m['model_bridge_count']}|{m['explicit_shortcut_count']}|{ar['most_fragile_step']}|")
brief+=['','## 价格情景（单位/基准未说清时不补）','','|归属|条件|窗口|价格方向|Claim|','|---|---|---|---|---|']
for f in forecasts:
    if any(x in f['target'] for x in ['油价','Brent']):brief.append(f"|{f['forecaster_id']}|{f['conditions']}|{f['prediction_window']}|{f['direction']}|{f['claim_id']}|")
brief+=['','## 阅读文件','','- golden_sample_003_report.md：完整报告','- golden_sample_003.json：完整机器可读对象及审计辅助表','- source_segments.json：Claim对应原文、cue与时码','- source_versions.json：直播条目cutoff名单','- review_queue.json：按严重性分类的待审问题','- validation.json：结构校验结果','- source_snapshots/：工具返回的网页片段；不是完整历史网页存档','']
brief+=['## 核查来源','','- [财联社油气情景报道](https://www.cls.cn/detail/2300559)：机构预测各有条件，储油约束是出口受阻后库容占满。','- [财联社滚动直播](https://www.cls.cn/detail/2298102)：只采纳版本表中cutoff前条目。','- [Platts成品油MOC通知]('+source_map['S08']['location']+')：只验证特定报价流程调整。','- [EIA历史统计说明](https://www.eia.gov/todayinenergy/detail.php?id=65504)：分母和年份可核查，重刊版本时间仍待确认。','']
(OUT/'README.md').write_text('\n'.join(brief),encoding='utf-8')

# 验证参照完整性/算法距离/预测先有Claim/不破坏原文；不是事实核验。
errors=[]
def check(ok,msg):
    if not ok:errors.append(msg)
check(len(set(c['claim_id'] for c in claims))==len(claims),'duplicate claims')
SS={s['source_segment_id']:s for s in source_segments};AR={a['argument_id']:a for a in arguments}
for c in claims:
    check(all(s in SS for s in c['source_segment_refs']),c['claim_id']+' source segment missing')
    check(c['claimant_id'] in actor_names,c['claim_id']+' actor missing')
    if c['corpus_origin']=='creator_transcript':check(c['asserted_at']==CUT,c['claim_id']+' invalid publication time')
for s in source_segments:check(s['source_id'] in source_map,s['source_segment_id']+' source missing')
for a in arguments:check(all(c in CM for c in a['claim_refs']),a['argument_id']+' claim missing')
for t in theses:
    check(bool(t['traceability']),t['thesis_id']+' no trace')
    for tr in t['traceability']:check(tr['claim_id'] in AR[tr['argument_id']]['claim_refs'] and tr['source_segment_id'] in CM[tr['claim_id']]['source_segment_refs'] and SS[tr['source_segment_id']]['source_id']==tr['source_id'],t['thesis_id']+' broken trace')
check({f['claim_id'] for f in forecasts}=={c['claim_id'] for c in claims if c['claim_type']=='forecast'},'forecast claim bijection')
check(len(assessments)==len(claims),'every claim assessment')
covered=[n for s in segments for n in range(s['cue_start'],s['cue_end']+1)]
check(covered==list(range(1,900)),'semantic cue coverage')
for s in sources:
    if 'sha256' in s:check(sha(Path(s['location']))==s['sha256'],'raw changed '+s['source_id'])
check(not any(f['resolution_criteria']['accepted_for_scoring'] for f in forecasts),'unapproved scoring')
check(all(not x['applied'] for x in corrections),'unreviewed correction applied')
check(all(SS[c['source_segment_refs'][0]].get('version_id') not in ['LV06','LV07','LV08','LV09','LV10'] for c in claims if c['corpus_origin']=='external_context_not_creator'),'postcutoff entry used')
validation=dict(status='pass' if not errors else 'fail',errors=errors,checked_at=NOW,claims=len(claims),forecasts=len(forecasts),raw_files_unchanged=True,all_899_cues_segmented=True,thesis_traceability=True,scope='structural_validation_not_audio_or_factual_verification',known_limitations=executive['max_uncertainties'])
save('validation.json',validation)
save('artifact_manifest.json',[dict(path=str(p.relative_to(OUT)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json'])
print(json.dumps(dict(summary=summary,validation=validation),ensure_ascii=False,indent=2))
