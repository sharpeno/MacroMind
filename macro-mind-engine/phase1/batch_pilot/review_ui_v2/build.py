import json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent
RUN=BASE.parent/'run_001'
def read(p):return json.loads(p.read_bytes())
items=[]
def add(id,ep,kind,title,prompt,evidence=None,detail=None,priority=False,related=None):
 items.append(dict(id=id,episode=ep,kind=kind,title=title,prompt=prompt,evidence=evidence or [],detail=detail,priority=priority,related=related or []))
for ep in [f'EP{i:03}' for i in range(1,6)]:
 d=RUN/ep;spec=read(d/'annotation.json');claims=read(d/'claims.json');cm={c['claim_id']:c for c in claims};segs=read(d/'segments.json');by={x['cue_id']:x for x in segs};act=read(d/'active_bundle.json')['objects'];ids={x['id'] for x in act};selected=[x['argument'][0] for x in read(RUN/'human_review_records.json') if x['episode']==ep]
 def quotes(c):return cm.get(c,{}).get('quotes',[])
 for a in spec['arguments']:
  related=[ep+'/'+c for c in a[1]+[a[2]]];ev=[]
  for cid in related:
   for q in quotes(cid):ev.append(dict(q,claim_ref=cid,claim_statement=cm[cid]['normalized_statement']))
  add(ep+'/'+a[0],ep,'推理链',('重点 · ' if a[0] in selected else '')+a[0]+' · '+' + '.join(a[1])+' → '+a[2],a[3]+' 请检查原话是否支持这条连接。全部箭头是助手重建。',ev,{'当前状态':'结构可用，非事实认证' if ep+'/'+a[0] in ids else '已隔离，暂不可用'},a[0] in selected,related)
 for c in claims:add(c['claim_id'],ep,'主张',c['claim_id'].split('/')[-1]+' · '+c['normalized_statement'],'检查转述是否忠实，是否丢失否定、条件、数字口径和作者归属；不要求证明观点正确。',c['quotes'],{'当前状态':'结构可用' if c['claim_id'] in ids else '已隔离','事实真实性':'未认证'})
 for x in read(d/'review_issues.json'):add(x['id'],ep,'转写疑点',x['id'].split('/')[-1]+' · '+x['reason'],'请按时间范围核听原视频。若提出修正，请写原字句、修正和听到的证据；拿不准可选无法确认。',x['quotes'],related=x['affected_claims'])
 for x in read(d/'coverage.json'):add(ep+'/cue-review/'+str(x['cue_id']),ep,'字幕覆盖',f"cue {x['cue_id']} · {x['topic_block'][2]}",'检查是否遗漏值得提取的分析。可标为补提取、仅作上下文、非分析内容或需核听；这不会自动修改原始记录。',[{k:x[k] for k in ['cue_id','time_range','quote']}],{'原处置':x['status'],'原主张连接':x['claim_refs']})
 for i,x in enumerate(read(d/'forecast_candidates.json')):add(ep+'/forecast-review/'+str(i+1),ep,'预测候选',x['claim_ref']+' · 尚未准入正式预测','确认是否明确作出预测，以及条件、截止时间、指标和判定标准。缺证据时继续待补证。',quotes(x['claim_ref']),x,related=[x['claim_ref']])
 for a in spec['scenarios']:add(ep+'/'+a[0],ep,'条件情景',a[0]+' · '+a[2],'检查条件与结果是否忠实；不要把假设性情景直接认作确定预测。',quotes(ep+'/'+a[1]),{'条件':a[2],'结果':a[3]},related=[ep+'/'+a[1]])
 for x in read(d/'method_observations.json'):add(x['id'],ep,'方法观察',x['observation'],'判断原话是否支持这个方法观察；即使支持，也不等于稳定、有效的方法或Skill。',[by[n] for n in x['cues']],x)
 for x in read(d/'all_isolated_objects.json')['pre_admission']:
  o=x['object'];add(ep+'/isolation/'+o['id'],ep,'隔离对象',o['id']+' · '+o['object_type'],'检查是否继续隔离；提出补证仅进入待处理队列，不会自动恢复对象。',quotes(o['id']),{'原因':x['reason'],'原对象ID':o['id']},related=[o['id']])
 for x in read(d/'all_isolated_objects.json')['activation_repair_pool']:
  cid=x['object_ref'].split('/occurrence/')[0];add(ep+'/isolation/'+x['object_ref'],ep,'隔离对象',x['object_ref']+' · '+x['object_type'],'检查依赖问题是否已具备补证；确认提议不会自动解除隔离。',quotes(cid),{'原因':x['reasons'],'恢复条件':x['activation_condition'],'原对象ID':x['object_ref']},related=[cid])
 for i,x in enumerate(read(d/'validation.json')['indeterminate']):add(ep+'/uncertainty/'+str(i+1),ep,'字段不确定',x['rule_id']+' · '+str(x.get('object_ref')),'可记录时间、归属等补充证据；不清楚请保持待补证，不需要理解规则代码。',quotes(x.get('object_ref')),x)
 add(ep+'/time-review',ep,'时间与来源','发布时间、时区及来源版本','请填写可确认的发布时间、时区及证据。不要凭地区猜测时区。',detail=next(x for x in act if x['object_type']=='Source'))
 add(ep+'/overall',ep,'总体意见',ep+' 本期整体审阅','本期是否存在系统性漏提取、错误归属或需要重新处理之处？不必审核完所有细项才反馈。')
for x in read(RUN/'reference_verification.json'):add(x['id'],x['episode'],'新闻关联',x['id']+' · '+(x['title_observed'] or '当前无法访问'),'分别判断“新闻内容能否核对”和“能否证明作者引用过”。请在意见中说明依据；有页面不等于作者读过。',detail=x)
for x in read(RUN/'source_discrepancies.json'):add('discrepancy/'+x['id'],x['episode'],'来源差异',x['id']+' · '+x['issue'],'记录如何处理来源与字幕差异。不得用当前网页静默覆盖历史字幕。',detail=x)
for i,x in enumerate(read(RUN/'cross_episode_comparison.json')['observations']):add('cross/'+str(i+1),'跨期','跨期对照',x['topic'],'检查比较是否越过当时信息边界。没有时间及同一方法证据时保持主题对照。',detail=x)
add('overall','全部','总体意见','首五期整体意见','说明是否可以进入下一轮质量评估，以及仍需修正或补证的范围。此意见不会自动改变验收Gate。')
assert len({x['id'] for x in items})==len(items)
source_hash=hashlib.sha256((RUN/'acceptance_manifest.json').read_bytes()).hexdigest()
videos={ep:next((RUN.parents[3]/'batch_pilot_materials'/ep).glob('*.mp4')).as_uri() for ep in [f'EP{i:03}' for i in range(1,6)]}
data={'videos':videos,'version':1,'dataset':source_hash,'items':items,'original_run':str(RUN)}
(BASE/'review_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
template=(BASE/'template.html').read_text(encoding='utf-8')
(BASE/'HUMAN_REVIEW.html').write_text(template.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c')),encoding='utf-8')
from collections import Counter
print(json.dumps({'items':len(items),'categories':dict(Counter(x['kind'] for x in items)),'priority':sum(x['priority'] for x in items)},ensure_ascii=True))
