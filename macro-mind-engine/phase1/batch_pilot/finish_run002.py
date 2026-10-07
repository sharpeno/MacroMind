from prepare_run002 import *
checks=[]
def check(name,condition):
 checks.append({'check':name,'passed':bool(condition)});write(RUN/'verification.json',checks);assert condition,name
manifest=read(OLD/'acceptance_manifest.json')['generated_artifact_hashes']
check('347 sealed artifacts unchanged',len(manifest)==347 and all(sha(Path(p))==h for p,h in manifest.items()))
inputs=read(RUN/'original_source_hashes.json');check('Original input files unchanged',all(sha(Path(p))==h for p,h in inputs.items()))
records=read(RUN/'review_input.json')['records'];diffs={};carry=[];totals={}
allowed={'EP001':{'C03','C04','C22','A01'},'EP002':{'C04','C21','A01'},'EP003':set(),'EP004':{'C20','C23','A03'},'EP005':{'C06','C27','A01','A07'}}
for i in range(1,6):
 ep=f'EP{i:03}';before={x['id']:x for x in read(OLD/ep/'candidate_bundle.json')['objects']};after={x['id']:x for x in read(RUN/ep/'candidate_bundle.json')['objects']}
 diff=[{'id':k,'before':before.get(k),'after':after.get(k)} for k in sorted(before.keys()|after.keys()) if before.get(k)!=after.get(k)];diffs[ep]=diff
 check(ep+' raw segments unchanged',sha(OLD/ep/'segments.json')==sha(RUN/ep/'segments.json'))
 check(ep+' only allowed objects changed',all(x['id'].split('/')[1] in allowed[ep] for x in diff))
 oldactive={x['id'] for x in read(OLD/ep/'active_bundle.json')['objects']};newactive={x['id'] for x in read(RUN/ep/'active_bundle.json')['objects']}
 oldisolated=set(before)-oldactive;check(ep+' existing isolation retained',oldisolated<=set(after)-newactive)
 v=read(RUN/ep/'validation.json');check(ep+' no errors/reference uncertainty',not v['errors'] and not any(x['rule_id'].startswith('V-REF') for x in v['indeterminate']))
 summary=read(RUN/ep/'summary.json');check(ep+' object conservation',summary['candidate_objects']==summary['active_objects']+summary['activation_deferred']+summary['pre_admission_deferred'])
 for k in ['cues','candidate_objects','active_objects','normalized_claims','active_claims','active_arguments','nonreference_indeterminate'] :totals[k]=totals.get(k,0)+summary[k]
 for r in records:
  if r['episode']!=ep or r['decision']!='faithful':continue
  a=before[r['id']];refs=a['premises']+[a['final_conclusion']];ids=[r['id']]+refs+[k for k in before if any(k.startswith(c+'/occurrence/') for c in refs)]
  unchanged=all(before[k]==after.get(k) for k in ids);check(r['id']+' faithful chain preserved',unchanged)
  carry.append({'id':r['id'],'status':'PRIOR_USER_FAITHFUL_CARRIED_FORWARD','compared_objects':ids,'unchanged':unchanged,'correction_overlay_pending':any(x['review_id']==r['id'] for x in read(RUN/'transcription_corrections.json'))})
write(RUN/'canonical_diff.json',diffs);write(RUN/'review_lineage.json',{'input':read(RUN/'review_input.json')['path'],'carry_forward':carry,'changed_review_status':'PENDING_REVIEW','new_objects_status':'PENDING_REVIEW','truth_verified':False})
check('All six faithful chains carried forward',len(carry)==6)
overlays=read(RUN/'transcription_corrections.json');check('10 corrections trace to unchanged source',len(overlays)==10 and all(x['original'] in read(RUN/x['episode']/'segments.json') and not x['assistant_audio_verified'] for x in overlays))
a=read(RUN/'audit_results.json');check('Six CLI audits completed with retained uncertainty',len(a)==6 and all(x['execution_status']=='COMPLETED' and x['findings_status']=='INDETERMINATE' and x['exit_code']==1 for x in a.values()))
repeat={f:sha(Path(a['EP001']['run_dir'])/f)==sha(Path(a['EP001_repeat']['run_dir'])/f) for f in ['canonical_view.json','normalized_audit.json','semantic_summary.json','pattern_aggregation.json']};write(RUN/'repeatability.json',repeat);check('Repeated audit four stable outputs equal',all(repeat.values()))
raw=read(RUN/'web_tool_raw.json');check('Raw web tool output saved',isinstance(raw,str) and all(s in raw for s in ['latest-03092026','latest-09092026','goldmansachs.com']))
urls=['https://www.goldmansachs.com/insights/the-markets/what-a-fed-rate-hike-could-mean-for-us-stocks','https://www.ubs.com/global/en/wealthmanagement/insights/chief-investment-office/house-view/daily/2026/latest-03092026.html','https://www.ubs.com/global/en/wealthmanagement/insights/chief-investment-office/house-view/daily/2026/latest-09092026.html']
notes=[('2026-09-11','What a Fed Rate Hike Could Mean for US Stocks','高盛访谈讨论AI及消费机会。文内CPI已公布，视频则讨论今晚CPI；存在内容时序疑问。无法据此确认这是博主所指的前几天研报。'),('2026-09-03','Look beyond tech as AI strength persists','瑞银CIO主张在保持AI配置基础上扩大投资范围，不等于退出AI，也不证明轮动失败。'),('2026-09-09','Brent tops 100: A milestone, not a turning point','瑞银CIO讨论能源成本与拓宽配置；医疗表述带有能源影响加重的条件，不能去掉条件转述。')]
sources=[{'id':'EP001/bank/'+str(i+1),'url':url,'date_observed':n[0],'title_observed':n[1],'assessment':n[2],'web_access':'CURRENT_PAGE_READ','historical_version_verified':False,'creator_citation_verified':False,'admission':'SUPPLEMENTAL_BACKGROUND_ONLY','raw_evidence':'web_tool_raw.json'} for i,(url,n) in enumerate(zip(urls,notes))];write(RUN/'supplemental_source_verification.json',sources)
items=[]
for rid in ['EP001/A01','EP002/A01','EP004/A03','EP005/A01','EP002/A02','EP003/A01']:
 ep,aid=rid.split('/');r=next(x for x in records if x['id']==rid);ds=diffs[ep] if r['decision']=='change' else [];spec=read(RUN/ep/'annotation.json');oldspec=read(OLD/ep/'annotation.json')
 changedclaims=[x for x in ds if x['after'] and x['after']['object_type']=='Claim'];claims=read(RUN/ep/'claims.json');ev=[]
 for x in changedclaims:ev.extend(next(c['quotes'] for c in claims if c['claim_id']==x['id']))
 corr=[x for x in overlays if x['review_id']==rid];ev.extend(x['original'] for x in corr);ev=list({x['cue_id']:x for x in ev}.values())
 detail={'上次意见':r,'本次主张变更':[{'编号':x['id'],'原表述':x['before']['statement'] if x['before'] else '新增','修订表述':x['after']['statement']} for x in changedclaims],'本次链变更':[{'编号':x['id'],'修订前':next((a for a in oldspec['arguments'] if ep+'/'+a[0]==x['id']),None),'修订后':next(a for a in spec['arguments'] if ep+'/'+a[0]==x['id'])} for x in ds if x['after'] and x['after']['object_type']=='Argument'],'用户转写修正':corr}
 if rid=='EP001/A01':detail['补充网页核对']=sources
 if rid=='EP005/A01':detail['保留限制']='原话未明确支持涨租金等于房价低估的一一对应规则；保留两种方向及观察用途。'
 items.append({'id':rid+'/revision','episode':ep,'kind':'推理链' if r['decision']=='change' else '转写疑点','title':rid+(' · 修订后复审' if r['decision']=='change' else ' · 仅核对转写修正，原链认可保留'),'prompt':'请检查下方修订对照。若无问题可直接选择判定，无需填写注释。用户转写意见单独保留，助手未独立核听；原字幕不改写。','evidence':ev,'detail':detail,'priority':True,'related':[rid]})
issue=read(RUN/'open_issues.json')[0]
items.append({'id':'EP001/duration/revision','episode':'EP001','kind':'转写疑点','title':'题材转换持续时长 · 可暂留待确认','prompt':'两种时长表述尚有差异，当前主张仅保留“未能持续”，未采用精确时长。可选择无法确认并继续，不影响其他修订反馈。','evidence':[s for s in read(RUN/'EP001/segments.json') if s['cue_id'] in issue['evidence_cues']],'detail':issue,'priority':True,'related':['EP001/A01']})
olddata=read(BASE/'review_ui_v2/review_data.json');dataset=hashlib.sha256(json.dumps({'diff':diffs,'corrections':overlays,'sources':sources},sort_keys=True,ensure_ascii=False).encode()).hexdigest();data={'version':1,'dataset':dataset,'items':items,'original_run':str(RUN),'videos':olddata['videos']};write(RUN/'review_data.json',data)
t=(BASE/'review_ui_v2/template.html').read_text(encoding='utf-8').replace('run_001','run_002').replace('run001','run002').replace('首批五期 / 可填写版 v2','首批五期 / 修订复审 run_002').replace('先审每期两条重点链，再处理转写疑点；其余类别均可逐项填写。','本次只有7组复审：4组语义修订、2组转写修正、1组可暂留的时长疑问。原先认可且未改变的六条链已保留。').replace('这 10 条','这 7 组').replace('重点链 ${pr} / 10','本次复审 ${pr} / 7').replace('重点推理链','本次修订').replace('证据来自封存的 run_002','证据引用 run_001 原始字幕，修订内容保存在 run_002').replace('人工审阅工作台','修订复审工作台')
(RUN/'HUMAN_REVIEW.html').write_text(t.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c')),encoding='utf-8')
(BASE/'human_reviews/run_002/exports').mkdir(parents=True,exist_ok=True)
write(RUN/'totals.json',totals);progress('DATA_VERIFIED_UI_BUILT',['Browser QA','Final report and manifest'])
print(json.dumps({'checks':len(checks),'totals':totals,'review_groups':len(items),'inputs':len(inputs)}))
