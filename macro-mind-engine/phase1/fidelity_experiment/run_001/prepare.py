import json,hashlib,re,html,datetime
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];H=ROOT/'phase1/holdout_evaluation';F=ROOT/'phase1/fidelity_alignment/run_001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def clean(s):return html.unescape(re.sub(r'\s+',' ',re.sub('<[^>]+>',' ',s))).strip()
assert not (P/'input_lock.json').exists()
source_hashes={}
def source(p):source_hashes[p.relative_to(ROOT).as_posix()]=sha(p);return read(p)
old=source(ROOT/'phase1/framework_review/v03_frozen_001/framework.json');new=source(F/'framework_candidate.json')
mk=['id','title','steps','alternative','trigger','applicability','required_inputs','procedure','default_judgment','not_applicable_or_limited','update_rule','output_fields_v02'];ck=['id','target','title','rule','inputs','steps','default','update','boundary']
base={'methods':[{k:v for k,v in m.items() if k in mk} for m in old['methods']],'review_cards':[{k:v for k,v in c.items() if k in ck} for c in old['review_cards']],'boundaries':old['boundaries'],'case_guards':old['case_guards'],'required_case_fields':old['required_case_fields']}
projection={'included_method_fields':mk,'included_card_fields':ck,'omitted':'corpus excerpts, teaching examples, lineage and review metadata; operative rule text retained verbatim','source_sha256':sha(ROOT/'phase1/framework_review/v03_frozen_001/framework.json')}
write(P/'framework_projection.json',projection)
ops=[{k:v for k,v in o.items() if k in ['id','title','when_and_question','procedure','boundary','counterexample_probe']} for o in new['operations']]
for arm,d in {'A':{'instruction':'使用你通常的分析方法，依据提供材料形成对问题的分析。'},'B':base,'C':{'v03':base,'candidate_operations':ops}}.items():write(P/f'arms/{arm}/method.json',d)
news={};dates={472:'2023-10-17',473:'2023-10-17',474:'2023-10-18',475:'2023-10-18'}
for ep in range(472,476):
 p=H/f'run_{ep-471:03}';records=[];meta=source(p/'news_input.json')
 if ep==472:
  for n in ['1486755','1486209']:
   a=source(p/f'sources/{n}.json')['props']['pageProps']['articleDetail'];records.append(dict(id=n,title=a['title'],text=clean(a['content']),source_type='media_report'))
  records.append(dict(id='NWH',text=meta['sources'][2]['observed_summary'],source_type='existing_archived_official_summary'))
 if ep in [473,474]:
  path=p/'sources/people.txt';source_hashes[path.relative_to(ROOT).as_posix()]=sha(path);text=clean(path.read_text(encoding='utf-8-sig'));a=text.index('新华社');b=text.index('(责编',a);records.append(dict(id=f'people{ep}',text=text[a:b],source_type='media_report'))
 if ep in [473,475]:
  a=source(p/'sources/cls.json')['articleDetail'];records.append(dict(id=f'cls{ep}',title=a['title'],text=clean(a['content']),source_type='media_report'))
 news[ep]=records
states=source(F/'analyst_state.json')['entries']
questions={472:'分析美国双线支持表态、拜登访问安排与地区局势变化：美国怎样介入，哪些因素决定走向？',473:'分析普京参加论坛、中国与塞尔维亚动车组合同及地区局势：合作怎样影响各方选择与能源风险预期？',474:'分析医院爆炸争议、会晤取消及各方反应：事件怎样影响外交、组织控制和后续升级？',475:'分析美国零售超预期、利率环境与地区投入：怎样理解政策路径以及美以选择与时机？'}
for ep in range(472,476):
 prior=[{k:v for k,v in s.items() if k in ['id','observed_episode','belief','author_force','verification_status']} for s in states if dates[s['observed_episode']]<dates[ep]]
 background=news[472] if ep>472 else []
 if ep==475:background=background+news[474]
 packet={'case':ep,'design':'DEVELOPMENT_REPLAY','cutoff':dates[ep]+' day-level; exact video ordering unknown','question':questions[ep],'news':news[ep],'background_news':background,'analyst_prior_state':prior,'missing_inputs':['缺少完整早期状态','新闻与博主实际掌握材料不等量','不得查阅目标字幕或检索补充'],'state_exclusions':'同日作者状态全部排除，回顾不回填首提时间','output_contract':{'language':'Chinese','units':3,'per_case_budget':'分析正文及字段值共900—1300中文字符，不超过1600；JSON键不计','fields':['case','overall','units','missing_inputs'],'unit_fields':['id','attention','question','reasoning','ranking','conclusion','predicted_force','conditions','update','evidence_ids'],'rules':['推演为候选，不冒称博主实际说过','依据限此包和方法，历史信念与事实分开','给主倾向及条件，无法排序需说明原因','不虚构渠道、原话或数值概率','只输出3个核心单元']}}
 write(P/f'common/case_{ep}.json',packet)
write(P/'source_hashes.json',source_hashes)
diag=read(F/'diagnosis.json')['items'];dims=['attention','question','reasoning','ranking','stance']
mask={'D472C':dims,'D473A':dims,'D473B':['stance'],'D473C':['ranking','stance'],'D474B':dims,'D475B':['stance']}
reasons={'D472C':'共同材料不支持3—5天和平与会议关联。','D473A':'缺姿态、接待级别及完整活动背景。','D473B':'无价格序列，不评分具体油价方向强度。','D473C':'缺产业历史与长期秩序背景，不评分长期排序和确信。','D474B':'缺完整美方支持与伊朗介入威胁话语。','D475B':'此前注水论原始记录缺失，不要求称证实的强度。'}
write(P/'rubric_locked.json',{'dimensions':dims,'scores':{'0':'核心缺失或反转','1':'部分对应，关键联系或条件缺失','2':'核心要素与联系对应'},'units':[{'id':d['id'],'episode':d['episode'],'target':d['title'],'expected':d['observed_gap'],'force_scope':d['author_force_and_scope'],'NE_dimensions':mask.get(d['id'],[]),'NE_reason':reasons.get(d['id'],''),'evidence_ref':d['evidence_ref']} for d in diag],'scorer':'root assistant knows targets and arms; NOT independently blinded','interpretation':'descriptive development comparison, no statistical significance or unseen performance claim'})
write(P/'protocol.json',{'design':'3 fresh-context agents, one per arm; each runs sequential472-475','model':'inherited parent; no override','reasoning':'inherited; no override','temperature_seed':'not exposed; uncontrolled','repeats':1,'case_isolation_limit':'same ordered trajectory, each agent retains own earlier answers; not fresh per case','treatment':'method only; common files identical','projection':projection,'contamination':'candidate developed using all target cases','rules':['no web','no target subtitles','no sibling arms','save each output before reading next case','no rewrite after submission'],'authorization':'user explicitly approved 3 independent subagents','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat()} )
write(P/'input_lock.json',{str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file() and f.name!='input_lock.json'})
print(json.dumps({'files_locked':len(read(P/'input_lock.json')),'sources':len(source_hashes),'case_chars':{ep:len(json.dumps(read(P/f'common/case_{ep}.json'),ensure_ascii=False)) for ep in range(472,476)}},ensure_ascii=False))
