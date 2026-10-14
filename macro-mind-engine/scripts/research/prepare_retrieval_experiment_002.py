from pathlib import Path
import json,sys
from datetime import datetime,timezone
root=Path('macro-mind-engine');sys.path.insert(0,str(root/'src'))
from macromind.methods.conditional_retrieval import retrieve_mechanisms
base=root/'phase1/topic_mining';out=base/'retrieval_experiment_002';out.mkdir(exist_ok=True)
if (out/'protocol.json').exists():
 existing=json.loads((out/'protocol.json').read_text(encoding='utf-8-sig'))
 if existing.get('generation_started_at') or any((out/f'answer_{arm}.txt').exists() for arm in ['A','B']):
  raise SystemExit('Run is frozen after generation starts; use a new experiment directory.')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(out/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cutoff='2025-08-10T00:00:00+08:00'
news=[
{'id':'N1','url':'https://www.investing.com/news/economy-news/trump-says-us-will-charge-tariff-of-about-100-on-semiconductor-imports-4174803','publisher':'Reuters via Investing.com','published_date':'2025-08-06','last_displayed_update':'2025-08-07','available_before_cutoff':'2025-08-08T12:00:00+00:00','summary':'特朗普8月6日称拟对进口半导体征收约100%关税，但在美国制造或承诺在美制造的公司可获豁免；他称不兑现建厂承诺者会被追收。路透明确说明这些讲话尚不是正式关税公告，具体适用范围仍不清楚。讲话与苹果宣布新增1000亿美元美国投入同时进行。','source_locator':'article header and body lines 35–65','classification':'reported_statement_not_enacted_rule'},
{'id':'N2','url':'https://www.investing.com/news/stock-market-news/trump-calls-on-intel-ceo-to-resign-4176539','publisher':'Reuters via Investing.com','published_date':'2025-08-07','last_displayed_update':'2025-08-08','available_before_cutoff':'2025-08-09T12:00:00+00:00','summary':'特朗普8月7日要求英特尔新任CEO陈立武立即辞职，指称其因与中国企业的联系存在利益冲突。报道将这一要求置于英特尔艰难扭转经营局面的背景下。利益冲突是特朗普的指控，本材料没有提供独立裁定，也没有CEO已辞职的事实。','source_locator':'article header lines 35–37; opening paragraph line 61','classification':'reported_demand_and_allegation'},
{'id':'N3','url':'https://www.apple.com/newsroom/2025/08/apple-increases-us-commitment-to-600-billion-usd-announces-ambitious-program/','publisher':'Apple','published_date':'2025-08-06','available_before_cutoff':'2025-08-07T12:00:00+00:00','summary':'苹果8月6日宣布新增1000亿美元美国投入承诺，使未来四年总承诺达到6000亿美元，并推出American Manufacturing Program。合作涉及Corning、Samsung、GlobalFoundries、Amkor、Broadcom等；库克公开感谢总统支持。苹果称台积电亚利桑那工厂正为其生产芯片。四年投入承诺不等于资金已经全部落地，不能把美国境内生产自动等同于美国企业拥有全部技术与控制权。','source_locator':'press release dated August 6, 2025; text lines 119–142','classification':'company_commitments_and_reported_operations'},
{'id':'N4','url':'https://www.intc.com/filings-reports/annual-reports/content/0000050863-25-000109/0000050863-25-000109.pdf','publisher':'Intel 2025 Q2 Form 10-Q','published_date':'2025-07-24','available_before_cutoff':'2025-07-25T12:00:00+00:00','summary':'英特尔7月24日文件披露：若14A无法取得重要外部客户并达到相关里程碑，可能暂停或停止14A及后续先进制程的开发；未来超出18A/18A-P的产品仍保留采用外部代工的选项。公司尚未为代工业务取得重要外部客户，继续减缓俄亥俄先进工厂建设。停止后续先进制程可能导致更依赖台积电等第三方，也可能失去政府补助资格或需要偿还已收款项。这些是公司披露的风险与条件，不是已经完全退出先进制造。','source_locator':'PDF pages 28 and 43 (zero-based 27 and 42), risk factors','classification':'company_disclosed_conditions_and_risks'}]
obs={}
def supported(f,refs,note):
 obs[f]={'state':'supported','source_refs':refs,'available_at':max((n['available_before_cutoff'] for n in news if n['id'] in refs),key=datetime.fromisoformat),'note':note}
supported('public_policy_action',['N1','N2'],'公开的拟征税、豁免及人事施压，不等于政策已生效。')
supported('visible_credit_channel',['N1','N3'],'联合宣布投入，库克公开感谢总统，存在公开归功渠道；不保证选民买账。')
supported('coercive_threat',['N1'],'拟征收高关税。')
supported('conditional_concession',['N1'],'以在美制造承诺为条件宣布可豁免；非已经完成交易。')
for f in ['beneficiaries_identified','credit_attributable','exchange_value_assessable','actor_can_execute_threat','support_based_power','cost_or_delivery_pressure','channel_disruption_or_distrust','alternative_channel_visible','system_stress','financing_tool_available','public_relief_promise','political_pressure']:
 obs[f]={'state':'unknown','source_refs':[],'note':'不由行动者名称或一般背景自动补成支持。'}
cat=read(base/'mechanism_transfer_002/catalog.json');retrieval=retrieve_mechanisms(cat,as_of=cutoff,observations=obs)
assert {m['id'] for m in retrieval['candidates']}=={'M7','M11'}
evidence={e['id']:e for e in read(base/'mechanism_transfer_002/historical_evidence.json')}
package={'retrieval':retrieval,'author_excerpt_windows':[],'use_policy':'这些是历史作者论证的抽象候选，不能直接当成本期作者结论；可拒用，可提出新机制，保留未知条件与竞争解释。'}
# Compact excerpts retain actual original cue text; full windows remain in historical_evidence.json.
windows={'EP798:E3':(416,432),'EP1048:credit':(395,407),'EP1048:bargain':(749,775),'EP1056:E2':(251,264),'EP1056:E3':(288,320)}
for eid,(lo,hi) in windows.items():
 e=evidence[eid];package['author_excerpt_windows'].append({k:v for k,v in e.items() if k!='cues'}|{'excerpt_cue_range':[lo,hi],'cues':[c for c in e['cues'] if lo<=c['cue']<=hi]})
questions=[{'id':'Q1','question':'特朗普宣布半导体100%关税、矛头瞄准英特尔CEO，真实目的是什么？'},{'id':'Q2','question':'中美围绕半导体行业的斗争方向发生改变了吗？'}]
common={'target_episode':1187,'cutoff':cutoff,'title':'特朗普宣布半导体100%关税，矛头瞄准英特尔CEO，真实目的是什么？中美围绕半导体行业的斗争方向发生改变了吗？20250810','questions':questions,'instruction':'尝试复现有何高见的分析过程。仅使用给定新闻和可选作者机制包，不联网、不读取目标字幕或其他材料，不引用截止后的事实。逐题给出主判断、选择的线索、前提、机制链、解释优先级与改变判断的条件。允许大胆推断动机，但标为模型假说；缺直接证据不自动禁止推理，也不把推理冒充新闻或作者已说过的结论。若有机制包，可局部采用或拒用，不能用检索顺序代替解释排序。关税讲话、投资承诺和风险披露均须保留当时状态。中文900—1200字，引用N编号及可用机制编号；末尾列关键缺口。','news':news,'retrieved_mechanisms':None}
save('A_input.json',common);common['retrieved_mechanisms']=package;save('B_input.json',common)
save('mechanism_package.json',package);save('news.json',news);save('query.json',{'cutoff':cutoff,'observations':obs,'feature_assignment':'manual'});save('retrieval.json',retrieval)
save('protocol.json',{'status':'prepared_awaiting_current_round_agent_authorization','created_at':datetime.now(timezone.utc).isoformat(),'target_subtitle_read':False,'target_episode':1187,'cutoff':cutoff,'only_input_difference':'retrieved_mechanisms','execution':'本轮授权后两个无历史独立子代理同模型各一次；生成后读字幕，先提取作者判断再读答案。','news_time_policy':'标题日期优先，零点截止。未明确网页时区的日日期按全球最晚UTC-12日末计算保守上界；上界不是实际发布时间。','source_capture_limit':'当前读取历史页面及报告，非历史网页快照；剔除当前行情、评论和晚于截止的搜索结果。','source_selection':'围绕标题人物、关税条件及同期公司约束选择，未读取目标字幕。','evaluation':['主判断方向','解释链及排序','条件与确信程度','事实和假说归属','材料缺口与机制缺口分别归因'],'labels':['aligned','partial','conflict','model_omitted','author_uncovered','not_comparable'],'limitations':['single_case_single_generation_per_arm','whole_package_effect_not_isolated_rule_effect','parent_not_blind_to_arm','manual_feature_mapping','nearby_date_but_distinct_policy_event'],'not_claimed':'组合检索通过不等于生成效果改善。','candidate_selection':[{'episode':1199,'selected':False,'reason':'简介含同日峰会后续报道，日内边界复杂；未读字幕。'},{'episode':1189,'selected':False,'reason':'已选1187，以公司与产业约束检验机制迁移；未读字幕。'},{'episode':1187,'selected':True,'reason':'半导体产业政策区别于统计机构人事事件，具有日期明确的会前公司披露及政策新闻。'}]})
a=read(out/'A_input.json');b=read(out/'B_input.json');assert [k for k in a if a[k]!=b[k]]==['retrieved_mechanisms'];assert all(datetime.fromisoformat(n['available_before_cutoff'])<datetime.fromisoformat(cutoff) for n in news)
save('checks.json',{'passed':True,'input_difference':['retrieved_mechanisms'],'sources_before_cutoff':4,'retrieved':['M7','M11'],'generated_answers':0,'target_subtitle_read':False})
print('Prepared EP1187; 4 dated sources; M7/M11 retrieved; target subtitle unread.')
