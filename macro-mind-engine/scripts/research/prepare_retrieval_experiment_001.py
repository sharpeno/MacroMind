import json, sys
from pathlib import Path
from datetime import datetime, timezone
root=Path('macro-mind-engine')
sys.path.insert(0,str(root/'src'))
from macromind.methods.conditional_retrieval import retrieve_mechanisms
out=root/'phase1/topic_mining/retrieval_experiment_001'
def save(name,data):
    (out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cutoff='2025-08-04T00:00:00+08:00'
news=[
 {'id':'N1','url':'https://www.bls.gov/news.release/archives/empsit_08012025.htm','title':'The Employment Situation — July 2025','published_at':'2025-08-01T08:30:00-04:00','available_before_cutoff':'2025-08-01T12:30:00+00:00','date_basis':'BLS archived release embargo timestamp','kind':'official_release','summary':'美国劳工统计局8月1日公布：7月非农就业增加7.3万人，失业率4.2%；5月增幅由14.4万人修订至1.9万人，6月由14.7万人修订至1.4万人，两月合计下修25.8万人。7月医疗增加5.5万人、社会援助增加1.8万人，联邦政府减少1.2万人；平均时薪同比增加3.9%。BLS解释修订来自补收到的报告及季节调整重算。这是当时发布版本，不采用后续修订。'},
 {'id':'N2','url':'https://www.cls.cn/detail/2104246','title':'数据不称心特朗普就炒人！舆论炸了：未来美国统计机构公信力何在？','published_at':'2025-08-02','available_before_cutoff':'2025-08-02T23:59:59+08:00','date_basis':'正文财联社8月2日讯；抓取页头时区不明确，仅使用正文日精度','kind':'reported_event_and_attributed_claims','summary':'报道特朗普在8月1日就业报告后解雇劳工统计局局长Erika McEntarfer，劳工部确认人事变动。特朗普指控数据受政治操纵；报道未提供支持蓄意造假的证据。民主党人士及曾由特朗普任命的前局长William Beach批评这一决定。受访人士提出调查回收率下降、较迟收到企业报告、人员预算压力和趋势变化等修订原因。这些解释与政治操纵指控应分别标记，不能仅凭大幅修订就认定造假，也不能仅凭批评就认定解雇必然产生某种经济结果。'},
 {'id':'N3','url':'https://www.cls.cn/detail/2085335','title':'特朗普关税引爆企业囤货潮，美最大港口6月吞吐量创历史新高','published_at':'2025-07-15','available_before_cutoff':'2025-07-15T23:59:59+08:00','date_basis':'正文财联社7月15日讯；不采用抓取元数据不明时区的前一日时间','kind':'observations_and_forecasts','summary':'洛杉矶港6月吞吐量892340个标准箱，同比约增8%、环比约增32%。港口负责人将其解释为企业赶在关税变化前囤货，而非终端需求突然繁荣。报道预测7月进口仍可能增加、8月可能回落；零售方面预计库存与运输时滞会延迟涨价，未来数周可能出现价格压力。后两项属于当时预测，尚不是已发生的进口回落或通胀结果。'}
]
questions=[{'id':'Q1','question':'特朗普开除劳工统计局局长，到底是果断止损还是昏招迭出？如何理解围绕数据真实性的两党争论？'},{'id':'Q2','question':'美国经济实际情况是好是坏？'},{'id':'Q3','question':'美国经济还能支撑多久？哪些条件或事件会改变判断？'}]
obs={'political_pressure':{'state':'supported','source_refs':['N2'],'available_at':news[1]['available_before_cutoff'],'note':'就业数据发布及解雇引发公开政治争议；不据此认定作者责任转移机制成立。'}}
for feature in ['policy_ineffective','industry_protection','staple_price_rise','external_financial_loss','direct_retail_release','public_relief_promise','credit_attributable','concentrated_beneficiaries','actor_has_control']:
    obs[feature]={'state':'unknown','source_refs':[],'note':'共同材料不足以确认该特征，未知不等于反证。'}
catalog=json.loads((root/'phase1/topic_mining/conditional_retrieval_001/catalog.json').read_text(encoding='utf-8-sig'))
retrieval=retrieve_mechanisms(catalog,as_of=cutoff,observations=obs)
assert [c['id'] for c in retrieval['candidates']]==['M6']
cues=json.loads((root/'phase1/topic_mining/rice_bridge_001/ep909_cues.json').read_text(encoding='utf-8-sig'))
quotes=[c for c in cues if 345<=c['cue']<=357 or 390<=c['cue']<=425]
package={'retrieval':retrieval,'author_source':{'episode':909,'date':'2024-09-03','evidence_id':'E909c','cues':quotes},'application_warning':'历史例子是日本自民党党首竞争背景下，关于放粮承诺、支持动员及未来责任归属的条件推演。本轮仅命中政治压力，尚未确认救济承诺、可归属政绩或集中受益者。不能将日本主体、米价及假想后续事件移植为美国事实。可以拒用这条机制。'}
instruction='你正在尝试复现有何高见的分析过程。只使用给定标题、新闻及可选作者机制包，不检索、不读取目标字幕、不引用截止时间后的事实。逐题形成明确倾向，说明选择哪些线索、经哪些前提连接到机制、为何优先某解释，并给出竞争解释及改变判断的条件。允许提出大胆的动机与利益推断，但标为模型假说；无需每条推断都有直接新闻证明，也不得把推断写成新闻事实或作者原话。作者机制包如存在，只提供候选路径，可判断不适用。标题中的两党争论不是证实任何一方指控。经济持续时间可给条件和阶段，不必虚构日期。中文900—1200字，逐题作答；标注新闻编号及机制编号；最后简列尚缺的关键材料。'
common={'cutoff':cutoff,'target_episode':1183,'title':'特朗普开除劳工统计局局长到底是果断止损还是昏招迭出？围绕数据真实性，美国两党再掀党争，美国经济实际情况是好是坏？还能支撑多久？20250804','questions':questions,'instruction':instruction,'news':news,'retrieved_mechanisms':None}
save('A_input.json',common)
common['retrieved_mechanisms']=package
save('B_input.json',common)
save('news.json',news)
save('query.json',{'cutoff':cutoff,'observations':obs,'assignment':'人工依照共同新闻标注，尚未实现自动特征抽取'})
save('retrieval.json',retrieval)
save('mechanism_package.json',package)
save('protocol.json',{'status':'inputs_frozen_awaiting_current_round_agent_authorization','created_at':datetime.now(timezone.utc).isoformat(),'target_episode':1183,'target_subtitle_read':False,'cutoff':cutoff,'date_policy':'标题日期优先；录制时刻未知，统一使用标题日期北京时间零点前的信息。','arms':{'A':'固定新闻，无作者机制包','B':'同一新闻与指令，增加冻结机制包'},'only_input_difference':'retrieved_mechanisms','execution':'得到本轮授权后，两个无聊天历史独立子代理，继承同一模型，每组一次；完成生成后才读取目标字幕。','judgment_extraction':'读取目标字幕后，先提取问题相关作者判断、因果链、倾向强度、条件与字幕位置，再阅读生成答案。','evaluation_labels':['aligned','partial','conflict','model_omitted','author_uncovered','not_comparable'],'conflict_rule':'同对象、同时间、同条件的直接冲突才记冲突；未覆盖的模型延伸不自动算错；作者假说无直接新闻支持不自动算错。','decision_axes':['结论方向','作者特有因果链及优先排序','确信程度和条件','事实与推断归属','新增假说的逻辑可检验性','机制误用或无作用'],'limitations':['单案例、每组一次，无法估计稳定收益','整体检索包对照，包含上下文和示例效应，不能归因于某条规则','作者历史机制来自有限米荒材料；本轮仅弱命中M6','输入为当前网页的历史报道摘要，未证明页面自发布日起从未修改','准备者知道组别；不是双盲评审','选择标题本身提供问题框架，结果仅适用于标题辅助复现'],'selection':[{'episode':1175,'selected':False,'reason':'所列报道与视频同日，录制时间未知；未读字幕即放弃该候选。'},{'episode':1183,'selected':True,'reason':'问题明确，简介包含较早报道，可固定前一日截止材料。'}],'excluded_sources':[{'url':'https://www.cls.cn/detail/2104736','reason':'页面与正文日期不一致，正文8月4日，不能确保截止前可用。'},{'url':'https://wallstreetcn.com/articles/3750726','reason':'抓取仅导航，网页解析能读正文但完整发布日期尚未确认，本轮不使用。'},{'url':'https://www.cls.cn/detail/2104378','reason':'抓取失败；已有BLS原始就业发布，避免引入重复新闻与额外市场材料。'}]})
a=json.loads((out/'A_input.json').read_text(encoding='utf-8'));b=json.loads((out/'B_input.json').read_text(encoding='utf-8'))
diff=[k for k in a if a[k]!=b[k]]
assert diff==['retrieved_mechanisms']
assert all(datetime.fromisoformat(n['available_before_cutoff'])<datetime.fromisoformat(cutoff) for n in news)
assert all(datetime.fromisoformat(c['observed_on']+'T23:59:59+08:00')<datetime.fromisoformat(cutoff) for c in retrieval['candidates'])
save('checks.json',{'passed':True,'input_difference':diff,'news_before_cutoff':3,'candidate_ids':['M6'],'target_subtitle_read':False,'generated_answers':0})
print(json.dumps({'output':str(out),'news':len(news),'candidate_ids':['M6'],'checks':'passed','generation':'pending authorization'},ensure_ascii=False))
