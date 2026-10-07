import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
B=Path('G:/youhegaojian/macro-mind-engine/phase1/batch_pilot');R=B/'run_002';OUT=B/'review_round_002';OUT.mkdir(exist_ok=True)
def rd(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checks=[]
for root,m in [(B/'run_001',rd(B/'run_001/acceptance_manifest.json')['generated_artifact_hashes']),(R,rd(R/'revision_manifest.json')['artifacts'])]:
 bad=[p for p,h in m.items() if sha(root/p)!=h];assert not bad;checks.append({'root':str(root),'files':len(m),'mismatches':bad})
completed={x['id'] for x in rd(R/'review_lineage.json')['carry_forward']}|set(rd(B/'human_reviews/run_002/batch_001/clarification_001/review_resolution.json')['semantic_revisions']['ids'])
items=[]
def add(ep,kind,ref,title,question,reason,cues=None):
 spec=rd(R/ep/'annotation.json');cm={c[0]:c for c in spec['claims']};am={a[0]:a for a in spec['arguments']};statements=[];related=[]
 if ref in am:
  a=am[ref];cs=a[1]+[a[2]];statements=['理由：'+ '；'.join(cm[c][2] for c in a[1]),'结论：'+cm[a[2]][2],'当前连接：'+a[3]];related=[ep+'/'+ref]+[ep+'/'+c for c in cs];cues=sorted({n for c in cs for n in cm[c][1]})
 elif ref in cm:
  c=cm[ref];statements=[c[2]];related=[ep+'/'+ref];cues=c[1]
 else:
  statements=['当前处置：重点片段尚未单独提取为主张。本卡仅征求是否补提取，不预设它一定被遗漏。'];related=[ep+'/cue/'+str(n).zfill(4) for n in cues]
 assert not completed.intersection(related)
 segs=rd(R/ep/'segments.json');evidence=[s for s in segs if s['cue_id'] in cues];assert len(evidence)==len(set(cues))
 item={'id':'R02/'+ep+'/'+ref,'episode':ep,'kind':kind,'title':title,'prompt':question,'review_summary':statements,'selection_reason':reason,'evidence':evidence,'priority':True,'related':related,'detail':{'当前材料':'run_002 原始字幕与归一化记录','本项尚未获得人工认可':True,'选择原因':reason,'判定范围':'只核对转述、条件、连接及是否遗漏；不要求你验证观点在现实中正确。'}}
 items.append(item)
add('EP001','推理链','A03','01 · 利润压缩为何只能暂时缓冲成本？','请检查：从“政策限制涨价、企业压缩利润”到“通胀缓和只是暂时”，是否忠实于原话？“成本继续上涨”这个条件是否需要在结论里写得更明确？','未审链；检查因果方向和持续成本上升的条件。')
add('EP002','字幕覆盖','gap223_235','02 · 如果加息落地，需要回答哪两个问题？','重点看205–219：是否准确保留“如果加息落地→先问一次性还是后续多次→如果后续多次，再问周期持续多久”的条件结构？223–235保留为后续上下文；是否补提取独立主张仍待核对。','原处置为上下文；检查条件性提问是否被误写为预测。',list(range(205,236)))
add('EP003','条件与范围','C23','03 · 地缘风险与美债：例外条件是否说清？','当前表述是否把原话中“美国权威受到挑战、市场抛售美债”的具体解释概括得过宽？请指出需要保留的具体原因；无需判断该解释在现实中是否正确。','未审主张；原话语气强，归一化为可能性时可能丢失立场和原因。')
add('EP004','条件与范围','C15','04 · 千倍回报是条件设想，还是明确预测？','请核对“如果现在能选中未来赢家”的前提，以及原话“十年以后回头看”。当前表述是否应补上时间范围？不要把条件设想理解为对任意药企的收益保证。','未审条件性表述；检查前提、时间范围与确定性。')
add('EP004','条件与范围','C22','05 · 行业机制与市场认知差，是否提取完整？','是否完整保留这几个步骤：理解行业如何成功→判断还能走多远→比较市场定价→区分认识不足与名不副实？有缺失时请写遗漏的步骤。','未审方法主张；检查是否过度压缩过程，尚不认定为稳定Skill。')
add('EP005','推理链','A03','06 · 短债压力与化债结构，连接是否有依据？','请核对理由和结论是否匹配，尤其是长短债、利息成本、内外债三种调整有没有混成同一件事。这里只审博主的解释，不认证政策原文。','未审链；检查理由覆盖范围。')
add('EP005','字幕覆盖','gap230','07 · “通胀逐步覆盖债务”是否需要独立保留？','重点看cue230；前后字幕只是上下文。它目前没有单独对应主张：是否应补提取为“博主认为调整债务结构后，可由通胀逐步覆盖债务”的观点？这只是一种候选转述，选择不补提取也可以。','原cue230标作上下文；检查化债机制是否漏提取。',list(range(225,236)))
add('EP005','推理链','A06','08 · 新房质量竞争与旧房价格冲击','请检查“未来一两年”“新房与已有房源”“稳住不等于升值”等限制是否保留；是否漏了“有刚需”和“可等待”的区别？原话有转写疑点时可选无法确认并标出时间。','未审链；检查时间、对象、例外条件，避免把差异概括成所有房价同向变化。')
# Keep additional existing comparison text near gap cards, avoiding a forced omission judgment.
items[1]['review_summary'] += ['如果加息落地，接下来需要回答两个问题：', '1. 这次加息是一次性的，还是意味着接下来会有多次加息？', '2. 如果接下来会有多次加息，这一加息周期会持续多久？', '表述性质：条件成立后需要回答的问题，不是对讨论焦点变化的预测。']
items[6]['review_summary'] += [next(c[2] for c in rd(R/'EP005/annotation.json')['claims'] if c[0]=='C11')]
selection={'round':'review_round_002','strategy':'Purposive risk-based sample, not random; no population accuracy inference','items':8,'episodes':5,'categories':{'推理链':3,'条件与范围':3,'字幕覆盖':2},'completed_first10_excluded':sorted(completed),'canonical_mutations':False,'prior_reviews_reopened':False}
wr(OUT/'selection_plan.json',selection)
data={'version':1,'dataset':hashlib.sha256(json.dumps(items,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'items':items,'original_run':str(R),'videos':rd(R/'review_data.json')['videos']};wr(OUT/'review_data.json',data)
t=(B/'review_ui_v2/template.html').read_text(encoding='utf-8')
t=t.replace('人工审阅工作台','第二轮质量抽查').replace('首批五期 / 可填写版 v2','首批五期 / 第二轮 / 8项').replace('先审每期两条重点链，再处理转写疑点；其余类别均可逐项填写。','这轮共8项，重点检查遗漏、条件和证据连接。每项先看“本次待审表述”和具体问题，再按需展开原字幕。此前完成的10条链无需重审。').replace('重点推理链（先审这 10 条）','本轮8项（全部）').replace('重点链 ${pr} / 10','本轮 ${pr} / ${items.length}').replace('MacroMind_run001_','MacroMind_round002_').replace('human_reviews/run_001/exports','human_reviews/review_round_002/exports').replace('证据来自封存的 run_001','证据来自封存的 run_002；本轮仅建立抽查记录，不改变已有主张').replace('MacroMind 首五期人工审阅意见','MacroMind 第二轮质量抽查意见')
t=t.replace("const optionSets={","const optionSets={\n'条件与范围':[['faithful','当前转述完整且忠实'],['change','需要补充或修改条件、范围'],['reject','原话不支持当前表述'],['unsure','无法确认']],\n'转写修订复审':[['adopt','采用展示的修正文本'],['retain_original','撤回建议，保留原转写'],['change','还需修改修正文本'],['unsure','暂不能确认']],")
needle="el('h3',item.title),el('p',item.prompt));"
assert needle in t
t=t.replace(needle,"el('h3',item.title));const focus=el('div',undefined,'notice');focus.append(el('strong','本次待审表述'));for(const text of item.review_summary||[])focus.append(el('p',text));focus.append(el('strong','你需要核对什么'),el('p',item.prompt));card.append(focus);")
t=t.replace('哪里忠实、哪里不确定、哪里有错误？','无问题可留空；有偏差时写明哪句话或哪个条件。')
(OUT/'template.html').write_text(t,encoding='utf-8');(OUT/'HUMAN_REVIEW.html').write_text(t.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c')),encoding='utf-8')
(B/'human_reviews/review_round_002/exports').mkdir(parents=True,exist_ok=True)
wr(OUT/'verification.json',{'immutable_checks':checks,'unique_ids':len({x['id'] for x in items}),'first10_overlap':False,'evidence_cue_integrity':True,'pending_decisions':8,'data_generation_only_no_audit_rerun_needed':True})
wr(OUT/'progress.json',{'stage':'SECOND_SAMPLE_GENERATED','completed':['Risk-based 8-item selection','Completed first10 excluded','Source-linked review cards generated'],'unfinished':['Browser validation','Delivery report','User reviews 8 items'],'time':datetime.now(timezone.utc).isoformat()})
print(json.dumps({'items':len(items),'categories':selection['categories'],'dataset':data['dataset']},ensure_ascii=True))
