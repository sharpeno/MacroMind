"""Build review artifacts and check persisted pilot evidence, without changing runtime."""
import json,re,html,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from macromind.audit.runner import read_package
ROOT=Path(__file__).resolve().parents[3];WS=ROOT.parent;RUN=Path(__file__).parent
EPS=[f'EP{i:03}' for i in range(1,6)]
def read(p):return json.loads(p.read_bytes())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def esc(x):return html.escape(str(x))
checks=[]
def check(name,ok,details=None):checks.append({'id':name,'status':'PASS' if ok else 'FAIL','details':details})
# Treat snapshots as data only; strip scripts without executing any page content.
refs=read(ROOT/'phase1/batch_pilot_intake/run_001/reference_candidates.json')
manual={
'EP001-N01':('美国8月PPI同比加速至5.4%超预期，核心PPI同比4.6%，美联储加息预期骤升','卜淑情','09/10 20:30'),
'EP001-N02':('加息还是按兵不动？美联储9月决策面临两难抉择','卜淑情','09/10 21:03'),
'EP003-N01':('沃什：加息展现FOMC内部坚定一致，通胀太高太久，降通胀不会牺牲就业（附全文）','杨宸','09/17 05:44')}
links={
'EP001-N01':[98,99,135,136,137,141,142,203,204,205], 'EP001-N02':[209,210,211,212,213,214,215],
'EP001-N04':[98,99,141,142], 'EP002-N02':list(range(297,312)), 'EP002-N03':[195,196,197,198,199,200],
'EP002-N04':[195,196,197,198,199], 'EP002-N05':[263,264,265,266,267,268,269,414,415,416],
'EP003-N01':[1,2,384,385,386,387,388,389,390,391,392,393,394], 'EP003-N03':[343,344,345,346,347,348],
'EP003-N04':list(range(31,64)), 'EP005-N01':[1,2,3,18,25,26], 'EP005-N02':[454,455,456,469,478,485]}
for ref in refs:
 ep=ref['episode'];id=ref['id'];url=ref['url'];tail=url.rstrip('/').split('/')[-1]
 p=RUN/('web_cls_'+tail+'.json')
 if not p.exists():p=RUN/('web_batch01_retry.json' if ep=='EP001' else 'web_batch02.json' if ep=='EP002' else 'web_batch03.json')
 raw=read(p);raw=raw['raw_response'] if isinstance(raw,dict) else raw
 sections=raw.split('-'*80);section=next((s for s in sections if url in s),raw)
 unavailable='cannot be opened' in section
 text=html.unescape(re.sub('<[^>]*>','',re.sub(r'<script[\s\S]*?</script>','',section)))
 title=re.search(r'<title[^>]*>(.*?)</title>',section)
 date=re.search(r'20\d{2}[-年]\d{2}[-月]\d{2}[日 ]+\d{2}:\d{2}(?::\d{2})?',text)
 author=re.search(r'(财联社(?:记者)?[ ]+[\u4e00-\u9fff ]+|央视财经)(?=责编)',text)
 if id in manual: title_value,author_value,date_value=manual[id]
 else:title_value=html.unescape(title.group(1)) if title else None;author_value=author.group(1).strip() if author else None;date_value=date.group(0) if date else None
 if id=='EP003-N02':author_value='财联社（电讯署名，无个人署名）'
 ref.update(status='UNAVAILABLE_BROWSER_ERROR' if unavailable else 'CURRENT_PAGE_CONTENT_OBSERVED',title_observed=None if unavailable else title_value,author_observed=None if unavailable else author_value,publication_time=None if unavailable else date_value,publication_timezone='UNKNOWN',updated_at='NOT_OBSERVED',retrieval_session_date='2026-10-03',retrieval_exact_timestamp='NOT_RECORDED',snapshot_archived_at=datetime.now(timezone.utc).isoformat(),content_snapshot=str(p),snapshot_sha256=sha(p),available_version='CURRENT_BROWSER_RESPONSE_ONLY; no historical snapshot',historical_availability='NOT_VERIFIED',external_truth='NOT_VERIFIED',eligible_as_verified_evidence=False,matched_cue_ids=links.get(id,[]),relationship_to_video='SUSPECTED_MATCH_NOT_PROVEN_CREATOR_CITATION' if id in links else 'USER_SUPPLIED_BACKGROUND_NO_CONFIRMED_LINK',source_locator='Browser response article heading, byline, timestamp and numbered lines',excerpt_policy='Source location retained; no copied article in review report')
 if id=='EP004-N02':ref['association_review']='All342 cues read: no identified gloves/英科医疗 discussion; preserve link as unconfirmed supplemental background, not innovative-drug premise.'
 if id=='EP005-N01':ref['correction']='Initial annotation reference_matches paired financing cues with N01. Ledger corrects these to N02; original annotation retained as provenance. No canonical web-source edge was created.'
write(RUN/'reference_verification.json',refs)
check('20_links_attempted',len(refs)==20 and all(Path(x['content_snapshot']).is_file() for x in refs))
# Conservative comparison, no canonical temporal or author-method continuity assertion.
write(RUN/'cross_episode_comparison.json',{'status':'TOPIC_COMPARISON_ONLY','canonical_cross_episode_edges':0,'temporal_guard':'NOT_VERIFIED: input publication timezone and historical news versions unknown','blind_evaluation':False,'observations':[{'topic':'加息是否发生与路径','EP001':['EP001/C01','EP001/C02','EP001/C21'],'EP002':['EP002/C01','EP002/C11','EP002/C13'],'EP003':['EP003/C01','EP003/C03','EP003/C08'],'interpretation':'用户时间标签下可见主题从决策前判断转到作者报告决策后路径讨论；不回填早期信息集，不认定预测兑现。'},{'topic':'概率归属','interpretation':'EP001的95%/99%是作者主观判断；新闻中的市场概率和不同日期报道不得混为同一概率序列。'},{'topic':'方法','interpretation':'可记录相对基准、激励和约束的主题连续性；未建立同一方法的跨期身份或有效性。'}]})
allstats=[];review=[]
for ep in EPS:
 d=RUN/ep;spec=read(d/'annotation.json');segments=read(d/'segments.json');cov=read(d/'coverage.json');claims=read(d/'claims.json');cand=read(d/'candidate_bundle.json')['objects'];act=read(d/'activation.json');active=act['active_bundle']['objects'];ids={o['id'] for o in active};pre=read(d/'pre_admission_pool.json');pool=act['repair_pool'];val=read(d/'validation.json');summary=read(d/'summary.json');mapping=read(d/'field_mapping.json');bycue={s['cue_id']:s for s in segments}
 input_files={k:v for k,v in read(RUN/'input_manifest.json')['files'].items() if '/'+ep+'/' in k}
 write(d/'input_manifest.json',{'files':input_files,'extraction_primary':'原始字幕.srt','audio_checked':False,'source_version':next(o for o in active if o['object_type']=='SourceVersion')})
 check(ep+'_coverage',len(cov)==len(segments) and [x['cue_id'] for x in cov]==list(range(1,len(segments)+1)))
 check(ep+'_quotes',all(q==bycue[q['cue_id']] for c in claims for q in c['quotes']))
 check(ep+'_complete_validation',val['mode']=='complete_bundle' and not val['errors'] and not any(x['rule_id'].startswith('V-REF') for x in val['indeterminate']))
 check(ep+'_conservation',len(cand)==len(active)+len(pre)+len(pool))
 check(ep+'_unique_ids',len({o['id'] for o in cand})==len(cand))
 check(ep+'_full_mapping',{m['object_ref'] for m in mapping}=={o['id'] for o in cand})
 check(ep+'_attribution',all(o['expression_level']=='model_reconstruction' and o['reasoner_id'].startswith('observer:') for o in active if o['object_type']=='Argument'))
 check(ep+'_no_forecast_skill',not any(o['object_type'] in ['Forecast','Heuristic','StructuralProcess','AnalystSkill'] for o in cand))
 check(ep+'_no_cross_episode_refs',all(not any(other+'/' in json.dumps(o,ensure_ascii=False) for other in EPS if other!=ep) for o in cand))
 check(ep+'_unknown_assertion_time',all(o['asserted_at']=={'state':'unknown'} for o in cand if o['object_type']=='Claim'))
 positive=[a for a in spec['arguments'] if ep+'/'+a[0] in ids]
 negative=[a for a in spec['arguments'] if ep+'/'+a[0] not in ids]
 check(ep+'_positive_and_negative',len(positive)>=2 and len(negative)>0)
 check(ep+'_isolation_propagates',all(ep+'/'+a[2] not in ids for a in negative))
 components=[]
 patterns={'numbers':r'\d+(?:\.\d+)?','units':r'%|BP|基点|百分点|美元|万人|亿元|亿|万|个月|月|年|倍|元|加仑','time':r'今晚|当晚|明年|今年|未来|过去|此前|\d+(?:年|月|日)|一年|两年|十年','conditions':r'如果|只要|假如|若|但是|否则|除非|一旦','modality':r'可能|预计|认为|相信|肯定|一定|必须|毫无疑问|大概','negation':r'不是|没有|不会|不能|不代表|不得|不|没','baseline':r'预期|前值|去年|同比|环比|相对|相比|同样|原来|之前|过去'}
 for c in claims:
  components.append({'claim_ref':c['claim_id'],'author':'analyst:9527:user_attributed','normalized_statement':c['normalized_statement'],'semantic_roles':'NOT_FULLY_RESOLVED; tokens are a navigation aid, not parsed financial/medical facts','components':{k:[{'cue_id':q['cue_id'],'tokens':[{'text':m.group(0),'start_character':m.start(),'end_character':m.end()} for m in re.finditer(p,q['quote'])]} for q in c['quotes'] if re.search(p,q['quote'])] for k,p in patterns.items()},'complete_context_quotes':c['quotes'],'human_review':'PENDING'})
 write(d/'evidence_components.json',components)
 issues=[{'id':ep+f'/ASR{i:02}','reason':f[2],'quotes':[bycue[n] for n in range(f[0],f[1]+1)],'proposed_correction':None,'evidence_for_correction':'NONE; no silent correction','audio_review':'NOT_PERFORMED','status':'PENDING_HUMAN_OR_AUDIO_REVIEW','affected_claims':[c['claim_id'] for c in claims if any(f[0]<=q['cue_id']<=f[1] for q in c['quotes'])]} for i,f in enumerate(spec['audio_flags'],1)]
 write(d/'review_issues.json',issues)
 write(d/'all_isolated_objects.json',{'pre_admission':pre,'activation_repair_pool':pool,'semantics':'NOT_USABLE_NOW is not FALSE or nonexistent'})
 unknown=Counter()
 def count_unknown(v,path=''):
  if v is None or v=={'state':'unknown'} or v=='unknown':unknown[path]+=1;return
  if isinstance(v,dict):
   for k,x in v.items():count_unknown(x,path+'.'+k if path else k)
  elif isinstance(v,list):
   for x in v:count_unknown(x,path+'[]')
 for o in cand:count_unknown(o,o['object_type'])
 summary.update(candidate_unknown_field_count=sum(unknown.values()),unknown_fields=dict(unknown),isolated_objects=len(pre)+len(pool),audit=read(RUN/'audit_results.json')[ep],manual_work={'assistant_cues_read':len(segments),'human_reviewed_claims':0,'human_reviewed_chains':0,'audio_cues_verified':0,'pending_issue_groups':len(issues),'pending_minimum_chain_reviews':2,'estimated_hours':'NOT_ESTIMATED'},semantic_extraction_scope='Selected claims only; all other cues preserved with topic disposition. Recall and correctness not measured.')
 write(d/'evaluation.json',summary);allstats.append(summary)
 review.extend({'episode':ep,'argument':a,'status':'PENDING','reviewer':None,'decision':None} for a in positive[:2])
write(RUN/'human_review_records.json',review)
write(RUN/'statistics.json',allstats)

# Verify both old evidence identities and the raw materials again at the end.
old=read(ROOT/'phase1/phase1_6r_manifest.json');bad=[k for k,v in old['generated_artifact_hashes'].items() if not (ROOT/k).is_file() or sha(ROOT/k)!=v]
input_bad=[k for k,v in read(RUN/'input_manifest.json')['files'].items() if not (WS/k).is_file() or sha(WS/k)!=v['sha256']]
baseline=read(ROOT/'phase1/phase1_6r_input_hashes.json')['protected']
protected={k:v for k,v in baseline.items() if k.startswith(('macro-mind-engine/src/','macro-mind-engine/tests/','macro-mind-engine/registries/','golden_sample_test/core_ontology/')) and '__pycache__' not in k}
protected.update({'macro-mind-engine/'+k:v for k,v in old['generated_artifact_hashes'].items() if k.startswith(('src/','tests/','registries/'))})
runtime_bad=[k for k,v in protected.items() if not (WS/k).is_file() or sha(WS/k)!=v]
known=set(protected);runtime_new=[]
for root in [ROOT/'src',ROOT/'tests',ROOT/'registries',WS/'golden_sample_test/core_ontology']:
 for p in root.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.relative_to(WS).as_posix() not in known:runtime_new.append(p.relative_to(WS).as_posix())
write(RUN/'immutability.json',{'previous_artifacts_verified':len(old['generated_artifact_hashes']),'previous_mismatches':bad,'raw_files_verified':26,'raw_mismatches':input_bad,'protected_runtime_and_contract_files':len(protected),'runtime_mismatches':runtime_bad,'runtime_untracked_since_prior_baseline':runtime_new,'prior_tests':old['tests'],'full_suite_rerun':False,'reason':'No runtime/schema/registry/activation-rule changes; artifact compiler checked against all five real bundles.'})
check('old_artifacts_unchanged',not bad);check('raw_materials_unchanged',not input_bad);check('runtime_and_contract_unchanged',not runtime_bad and not runtime_new)
audits=read(RUN/'audit_results.json')
for name,value in audits.items():
 read_package(value['run_dir'],value['manifest_sha256'])
 check(name+'_audit_integrity',True)
 check(name+'_audit_completed',value['execution_status']=='COMPLETED')
 v=read(Path(value['run_dir'])/'validation.json')
 check(name+'_audit_matches_validation',v['deterministic_hash']==read(RUN/name[:5]/'validation.json')['deterministic_hash'])
repeat={}
for filename in ['semantic_summary.json','validation.json','normalized_audit.json','pattern_aggregation.json']:
 x=read(Path(audits['EP001']['run_dir'])/filename)['deterministic_hash'];y=read(Path(audits['EP001_repeat']['run_dir'])/filename)['deterministic_hash']
 repeat[filename]={'first':x,'repeat':y,'equal':x==y};check('repeat_'+filename,x==y)
write(RUN/'repeatability.json',{'scope':'Persisted annotation replay; does not claim a fresh independent semantic extraction produces identical annotations','artifacts':repeat})
write(RUN/'execution_incidents.json',[{'action':'web_batch01 initial persistence','result':'FAILED_UNICODE_ENCODING','retained':'web_batch01.json is an empty failed-attempt artifact; web_batch01_retry.json contains recovered original tool response'},{'action':'web_batch03 single shell transfer','result':'FAILED_WINDOWS_COMMAND_LENGTH_206','resolution':'Saved original stored tool response in chunks to web_batch03.json'},{'action':'apply_patch web snapshot','result':'FAILED_TO_WRITE','resolution':'Saved with Python from writable workspace parent using base64; raw responses retained'},{'action':'diagnostic console print','result':'GBK_UNICODE_PRINT_FAILURE','resolution':'Set diagnostic stdout UTF-8; source files unaffected'}])
write(RUN/'source_discrepancies.json',[{'id':'D01','episode':'EP001','cues':[114,115,116],'issue':'原话前值4.7与当前新闻有修订前值4.8的不同版本；不能用网页改字幕或证明当时信息集。','status':'PENDING','references':['EP001-N01','EP001-N04']},{'id':'D02','episode':'EP001','cues':[211,212],'issue':'就业数值与新闻叙述存在疑点；原字幕保留，不从新闻反向自动纠正。','status':'PENDING','references':['EP001-N02']},{'id':'D03','episode':'EP003','cues':[343,344,345,346],'issue':'房贷与国债期限口径需核对，新闻与字幕表述不可直接等同。','status':'PENDING','references':['EP003-N03']},{'id':'D04','episode':'EP005','cues':[1,2,3,11,12,13],'issue':'作者对封顶、交付和资金释放的概括与新闻所列条件不完全相同；不是法规认证。','status':'PENDING','references':['EP005-N01']},{'id':'D05','episode':'EP004','cues':[],'issue':'手套行业链接未找到明确字幕关联，原样保留。','status':'NO_CONFIRMED_ASSOCIATION','references':['EP004-N02']}])
# Self-contained human packet: originals, candidates, active chains and isolated chains.
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MacroMind 首五期审阅包</title><style>body{font:17px/1.7 system-ui,sans-serif;max-width:1100px;margin:36px auto;padding:0 22px;color:#172d38;background:#f7f8f5}h1,h2,h3{line-height:1.35}nav a{margin-right:20px}article,details{background:white;padding:14px 20px;margin:14px 0;border:1px solid #d7dfdc;border-radius:8px}summary{cursor:pointer;font-weight:600}blockquote{border-left:3px solid #789e99;margin:10px 0;padding:8px 15px;background:#f2f6f5}small{color:#56636c}.tag{color:#975b0d}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ccd5d1;padding:8px;text-align:left}a{color:#076a73}pre{white-space:pre-wrap;overflow-wrap:anywhere}input{margin-right:8px}</style><h1>首批五期 · 人工审阅包</h1><p>所有人工判定尚未填写。请先检查每期两条重点链（共10条），再核听列出的高风险片段。可用表示引用结构完整，不表示事实已证实。粗体转述由助手整理，展开部分保留字幕原字句；箭头均为模型重建。</p><p>判断重点：转述是否忠实？有没有丢失否定、条件、数字口径？箭头是否得到原话支持？回复时用 EP编号/链编号 + 通过或问题即可。这里没有自动保存人工结论的按钮；结果应另存新版本。</p><nav>'+''.join('<a href="#'+ep+'">'+ep+'</a>' for ep in EPS)+'</nav>']
md=['# 首五期人工抽查包','', '人工抽查：尚未进行。共10条重点链，展开HTML查看全部原话和高风险队列。','']
for ep in EPS:
 d=RUN/ep;spec=read(d/'annotation.json');cs={c['claim_id']:c for c in read(d/'claims.json')};active={o['id'] for o in read(d/'active_bundle.json')['objects']};stats=read(d/'evaluation.json');issues=read(d/'review_issues.json')
 parts+=['<h2 id="'+ep+'">'+ep+'</h2><p>字幕 '+str(stats['cues'])+' 条；候选主张 '+str(stats['normalized_claims'])+'；可用主张 '+str(stats['active_claims'])+'；可用链 '+str(stats['active_arguments'])+'；隔离对象 '+str(stats['isolated_objects'])+'。</p>']
 def claim_html(cid):
  c=cs[cid];s='<details id="'+cid.replace('/','-')+'"><summary>'+esc(cid)+' · '+esc(c['normalized_statement'])+'</summary><p class="tag">'+('结构可用，人工待审' if cid in active else '暂不可用，已隔离')+'</p>'
  for q in c['quotes']:s+='<blockquote><small>cue '+str(q['cue_id'])+' · '+esc(q['time_range'])+'</small><br>'+esc(q['quote'])+'</blockquote>'
  return s+'</details>'
 selected=[a for a in spec['arguments'] if ep+'/'+a[0] in active][:2]
 md+=['## '+ep,'']
 for a in selected:
  aid=ep+'/'+a[0];parts+=['<article><h3>重点抽查 '+aid+'</h3><p>'+esc(' + '.join(a[1])+' → '+a[2])+'</p><p>'+esc(a[3])+'</p><p class="tag">关系由助手重建；不是博主列出的正式证明，也未认证因果成立。</p>']
  parts.extend(claim_html(ep+'/'+c) for c in dict.fromkeys(a[1]+[a[2]]));parts+=['</article>']
  md+=['### '+aid,'',a[3],'']
  for c in dict.fromkeys(a[1]+[a[2]]):
   claim=cs[ep+'/'+c];md+=['**'+claim['claim_id']+'** '+claim['normalized_statement'],'']
   md.extend('> cue '+str(q['cue_id'])+' / '+q['time_range']+'：'+q['quote'] for q in claim['quotes']);md+=['']
 parts+=['<details><summary>所有候选主张及原话（包括未启用）</summary>']
 # Avoid duplicate anchor IDs by removing id attributes in the repeated ledger.
 parts.extend(re.sub(r' id="[^"]+"','',claim_html(cid)) for cid in cs);parts+=['</details>']
 parts+=['<details><summary>重要隔离推理及下游结论</summary>']
 for a in spec['arguments']:
  if ep+'/'+a[0] not in active:
   parts+=['<h3>'+ep+'/'+a[0]+'</h3><p>'+esc(a[3])+'</p>'];parts.extend(re.sub(r' id="[^"]+"','',claim_html(ep+'/'+c)) for c in dict.fromkeys(a[1]+[a[2]]))
 parts+=['</details><details><summary>全部已发现疑点 · '+str(len(issues))+' 组 · 尚未核听</summary>']
 for issue in issues:
  parts+=['<details><summary>'+issue['id']+' '+esc(issue['reason'])+'</summary><p>原字句保留；没有已确认修正。请按时间范围打开原视频核听。</p>']
  for q in issue['quotes']:parts+=['<blockquote><small>cue '+str(q['cue_id'])+' · '+esc(q['time_range'])+'</small><br>'+esc(q['quote'])+'</blockquote>']
  parts+=['</details>']
 parts+=['</details><details><summary>文件、预测候选与结构不确定性</summary><ul>']
 for file in ['coverage.json','field_mapping.json','evidence_components.json','all_isolated_objects.json','forecast_candidates.json','method_observations.json','validation.json','evaluation.json']:
  parts+=['<li><a href="'+ep+'/'+file+'">'+file+'</a></li>']
 videos=list((WS/'batch_pilot_materials'/ep).glob('*.mp4'))
 if videos:parts+=['<li>原视频：'+esc(str(videos[0]))+'</li>']
 parts+=['<li><a href="'+esc(Path(stats['audit']['run_dir']).relative_to(RUN).as_posix()+'/report.md')+'">真实 Audit Runner 报告</a></li></ul></details>']
parts+=['<h2>新闻链接核验</h2><p>18个当前页面有内容，2个浏览失败。均没有历史版本证明或确认博主实际阅读的证据。当前网页内容没有反向写入字幕主张。</p><table><tr><th>编号</th><th>当前页面</th><th>关联</th></tr>']
for ref in refs:parts+=['<tr><td>'+ref['id']+'</td><td><a href="'+esc(ref['url'])+'">'+esc(ref['title_observed'] or '无法访问')+'</a><br><small>'+esc(ref['publication_time'])+' / '+esc(ref['author_observed'])+'</small></td><td>'+esc(ref['relationship_to_video'])+'</td></tr>']
parts+=['</table><p><a href="reference_verification.json">完整链接元数据与快照定位</a> · <a href="statistics.json">全部统计</a> · <a href="cross_episode_comparison.json">有限跨期对照</a></p></html>']
(RUN/'HUMAN_REVIEW.html').write_text(''.join(parts),encoding='utf-8');(RUN/'HUMAN_REVIEW.md').write_text('\n'.join(md),encoding='utf-8')
check('review_ten_chains',len(review)==10 and all(sum(x['episode']==ep for x in review)==2 for ep in EPS))
check('review_not_fabricated',all(x['reviewer'] is None and x['decision'] is None for x in review))
from html.parser import HTMLParser
class LinkCheck(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.links.extend(v for k,v in attrs if k=='href')
parser=LinkCheck();parser.feed(''.join(parts));broken=[s for s in parser.links if not s.startswith(('http','#')) and not (RUN/s).is_file()]
check('review_local_links',not broken,broken)
write(RUN/'checks.json',{'checks':checks,'passed':sum(c['status']=='PASS' for c in checks),'failed':sum(c['status']=='FAIL' for c in checks),'scope':'Artifact invariants and real-run replay; not semantic correctness score or a new584-test run'})
failed=[c['id'] for c in checks if c['status']=='FAIL']
print(json.dumps({'checks':len(checks),'failed':failed,'stats':[{k:s[k] for k in ['episode','candidate_objects','active_objects','isolated_objects','active_arguments','candidate_unknown_field_count']} for s in allstats]},ensure_ascii=True))
if failed:raise SystemExit(1)
