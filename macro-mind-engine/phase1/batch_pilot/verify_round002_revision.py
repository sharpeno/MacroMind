from apply_round002_review import *
checks=[]
def ck(name,ok):
 checks.append({'check':name,'passed':bool(ok)});wr(R/'verification.json',checks);assert ok,name
allowed={'EP001':{'C19','A03'},'EP002':{'C22'},'EP003':{'C23'},'EP004':{'C15','C22'},'EP005':{'C11','C28','C29','C30','A03'}}
diffs={};totals={};carry=[]
first10=set(rd(B/'review_round_002/selection_plan.json')['completed_first10_excluded'])
for i in range(1,6):
 ep=f'EP{i:03}';old={x['id']:x for x in rd(OLD/ep/'candidate_bundle.json')['objects']};new={x['id']:x for x in rd(R/ep/'candidate_bundle.json')['objects']};d=[{'id':k,'before':old.get(k),'after':new.get(k)} for k in sorted(old.keys()|new.keys()) if old.get(k)!=new.get(k)];diffs[ep]=d
 ck(ep+' allowed objects only',all(x['id'].split('/')[1] in allowed[ep] for x in d));ck(ep+' raw source segments unchanged',sha(OLD/ep/'segments.json')==sha(R/ep/'segments.json'))
 active={x['id'] for x in rd(R/ep/'active_bundle.json')['objects']};oldactive={x['id'] for x in rd(OLD/ep/'active_bundle.json')['objects']};ck(ep+' old isolated objects remain isolated',(set(old)-oldactive)<=(set(new)-active))
 v=rd(R/ep/'validation.json');ck(ep+' no validation errors or reference unknowns',not v['errors'] and not any(x['rule_id'].startswith('V-REF') for x in v['indeterminate']))
 s=rd(R/ep/'summary.json');ck(ep+' conservation',s['candidate_objects']==s['active_objects']+s['pre_admission_deferred']+s['activation_deferred'])
 for k in ['candidate_objects','active_objects','normalized_claims','active_claims','active_arguments','nonreference_indeterminate']:totals[k]=totals.get(k,0)+s[k]
 for aid in sorted(first10|{'EP005/A06'}):
  if not aid.startswith(ep+'/'):continue
  a=old[aid];refs=a['premises']+[a['final_conclusion']];related=[aid]+refs+[k for k in old if any(k.startswith(c+'/occurrence/') for c in refs)]
  ck(aid+' accepted subgraph unchanged',all(old[k]==new.get(k) for k in related));carry.append({'id':aid,'status':'USER_FAITHFUL_UNCHANGED','objects_compared':related})
wr(R/'canonical_diff.json',diffs);wr(R/'carried_forward_reviews.json',carry)
s5=rd(R/'EP005/annotation.json');a=next(x for x in s5['arguments'] if x[0]=='A03');ck('Debt motivation supports only term extension',a[1:3]==[['C12'],'C28']);ck('No new claim extracted from context-only cue230',not any(230 in c[1] for c in s5['claims']))
ck('C15 removed from forecast candidates',not any(x['claim_ref']=='EP004/C15' for x in rd(R/'EP004/forecast_candidates.json')))
ck('C15 remains attributed background statement',any(x['claim_id']=='EP004/C15' for x in rd(R/'EP004/claims.json')))
ck('Gap223-235 added with exact evidence',next(x for x in rd(R/'EP002/annotation.json')['claims'] if x[0]=='C22')[1]==list(range(223,236)))
for root,m in [(B/'run_001',rd(B/'run_001/acceptance_manifest.json')['generated_artifact_hashes']),(OLD,rd(OLD/'revision_manifest.json')['artifacts']),(B/'review_round_002',rd(B/'review_round_002/manifest.json')['artifacts'])]:ck(root.name+' immutable artifact hashes',all(sha(root/p)==h for p,h in m.items()))
inputs=[]
for i in range(1,6):
 for p,h in rd(B/'run_001'/f'EP{i:03}'/'input_manifest.json')['files'].items():inputs.append({'path':p,'unchanged':sha(ROOT.parent/p)==h['sha256']})
ck('25 original input files unchanged',len(inputs)==25 and all(x['unchanged'] for x in inputs));wr(R/'original_input_checks.json',inputs)
audits=rd(R/'audit_results.json');ck('Six audits complete',len(audits)==6 and all(x['execution_status']=='COMPLETED' and x['exit_code'] in [0,1] for x in audits.values()))
repeat={f:sha(Path(audits['EP001']['run_dir'])/f)==sha(Path(audits['EP001_repeat']['run_dir'])/f) for f in ['canonical_view.json','normalized_audit.json','semantic_summary.json','pattern_aggregation.json']};ck('Repeatable stable audit outputs',all(repeat.values()));wr(R/'repeatability.json',repeat);wr(R/'totals.json',totals)
res=[]
actions={'R02/EP001/A03':'忠实判定保留为历史意见；落实备注，C19及A03明确成本继续上涨条件。新文本标为按意见修订，非再次获批。','R02/EP002/gap223_235':'新增C22，区分转述市场说法与博主反对立场，保留只要加息落地的条件。候选文本由助手拟定，尚待确认。','R02/EP003/C23':'替换为用户提供的历史经验—当前反差—原因解释表述；同步修正M02方法观察，避免旧例外条件概括残留。','R02/EP004/C15':'采用用户修正文，移出预测候选。保留原话及说明性条件情景，禁止作为具体预测评分或选股规则。','R02/EP004/C22':'保留原有方法步骤，补全认识不足→机会、名不副实→风险两分支。','R02/EP005/A03':'保留三项并列方法描述，新增C28/C29/C30；A03只以C12为动机连接C28，不再以整套方法为结论。','R02/EP005/gap230':'遵从context判定，不新增主张。','R02/EP005/A06':'按faithful判定保留，链及其主张、出现位置未变。'}
for x in rd(R/'review_input.json')['records']:res.append({'id':x['id'],'raw_decision':x['decision'],'note':x['note'],'action':actions[x['id']],'status':'RETAINED_AS_REVIEWED' if x['id'] in ['R02/EP005/gap230','R02/EP005/A06'] else 'IMPLEMENTED_FROM_REVIEW_NOT_NEW_APPROVAL'})
wr(R/'review_resolution.json',res)
report=['# Round 2意见落实：run_003','', '8项原始意见已完整归档。6项涉及修订或补提取，1项按用户要求仅作上下文，1项认可原链。EP001/A03虽选faithful，但备注要求补条件，已落实而非忽略。','', '## 逐项处理','']
for x in res:report.append('- '+x['id']+'：'+x['action'])
report+=['','## 验证结果','',f'{len(checks)}项边界和保留性检查通过。原run001、run002和第二轮审核页封存产物均未改动；25个原始输入文件哈希一致。首10条已认可链以及本轮EP005/A06均逐对象保持一致。',f"本版共{totals['normalized_claims']}条归一化主张、{totals['active_claims']}条结构可用主张、{totals['active_arguments']}条结构可用推理链；{totals['candidate_objects']}个候选对象、{totals['active_objects']}个结构可用对象，隔离对象仍为{totals['candidate_objects']-totals['active_objects']}。",f"五期验证无error、无引用类未决；非引用未决共{totals['nonreference_indeterminate']}项。新增主张继续保留未知时间等字段，不伪造补全。",'五期真实CLI审计及EP001重复运行均完成；逐次状态见audit_results.json。稳定的四项输出哈希一致。工程检查不代表观点事实正确或完整人工验收。','','## 证据与进度','','review_input.json引用归档文件和SHA256；review_resolution.json为8项处理映射；canonical_diff.json为逐对象前后差异；usage_constraints.json记录使用边界；carried_forward_reviews.json为认可保留依据。每次编译及审计命令、stdout、stderr、结果均位于本目录；verification.command.json、verification.stdout.txt及verification.json保留验证执行结果。','','此前用户确认的6处转写纠正继续引用独立修订层，未改写原始SourceSegment。千倍回报不再在forecast_candidates.json中出现；原始数字及十年条件仍保存在原句和说明性情景中。分析师Skill、效果验证和扩样均未启动。','','## 未完成与下一步','','第二轮用户意见已落实，但助手新增或重组文本尚不能算用户再次认可。重点是EP002/C22新增观点、EP005三项方法拆分及局部动机连接。可先核对这些变化，不重复审原先认可的链。历史投行引用与时序、精确时长及其他非引用未决信息仍未解决。','']
(R/'REVISION_REPORT.md').write_text('\n'.join(report),encoding='utf-8')
# Readable change list, no need to inspect a raw JSON diff.
lines=['# 本轮文字与连接变更对照','']
for ep,ds in diffs.items():
 for x in ds:
  obj=x['after'] or x['before']
  if obj['object_type'] not in ['Claim','Argument']:continue
  lines+=['## '+x['id'],'']
  for label,val in [('修订前',x['before']),('修订后',x['after'])]:
   text='无（新增）' if val is None else val.get('statement') or ' + '.join(val['premises'])+' → '+val['final_conclusion']+'；'+val['steps'][0]['statement'];lines+=[label+'：'+text,'']
(R/'CHANGE_REVIEW.md').write_text('\n'.join(lines),encoding='utf-8')
progress('ROUND2_FEEDBACK_IMPLEMENTED',['Confirm assistant-derived added/split text if needed','Unresolved source attribution/timing and other fields remain','No scale-up or Skill acceptance'])
wr(ARCH/'latest_resolution.json',{'run':'run_003','resolution':str(R/'review_resolution.json'),'report':str(R/'REVISION_REPORT.md'),'status':'ROUND2_FEEDBACK_IMPLEMENTED'})
wr(B/'revision_latest.json',{'run':'run_003','report':str(R/'REVISION_REPORT.md'),'changes':str(R/'CHANGE_REVIEW.md'),'progress':str(R/'progress.json'),'status':'ROUND2_FEEDBACK_IMPLEMENTED'})
wr(B/'review_latest.json',{'round':'review_round_002','status':'FEEDBACK_RECEIVED_AND_IMPLEMENTED','receipt':str(ARCH/'receipt.json'),'revision_run':'run_003','report':str(R/'REVISION_REPORT.md')})
print(json.dumps({'checks':len(checks),'totals':totals,'audit_statuses':{k:v['findings_status'] for k,v in audits.items()}},ensure_ascii=True))
