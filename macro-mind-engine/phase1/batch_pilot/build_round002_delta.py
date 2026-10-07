import json,hashlib
from pathlib import Path
B=Path('G:/youhegaojian/macro-mind-engine/phase1/batch_pilot');R=B/'run_003';O=B/'review_round_002_delta';O.mkdir(exist_ok=True)
def rd(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=rd(R/'revision_manifest.json')['artifacts'];assert all(sha(R/p)==h for p,h in m.items())
items=[]
for ep,ref,cids,title,prompt in [('EP002','C22',['C22'],'01 · 新增观点：加息落地后的市场叙事','你此前选择需要补提取。请确认下面这句话是否准确区分了市场说法与博主立场，并保留“只要加息落地”的条件。'),('EP005','A03',['C11','C12','C28','C29','C30'],'02 · 化债：三个并列方法，一个局部理由','请确认：三种方法是并列记录；短期偿付造成的频繁融资需求，只作为“短债换长债”的动机，没有用来推导另外两项。')]:
 s=rd(R/ep/'annotation.json');cm={c[0]:c for c in s['claims']};cues=sorted({n for cid in cids for n in cm[cid][1]});summ=[cid+'：'+cm[cid][2] for cid in cids]
 if ref=='A03':summ.append('局部连接：'+next(a[3] for a in s['arguments'] if a[0]=='A03'))
 items.append({'id':'R02D/'+ep+'/'+ref,'episode':ep,'kind':'修订确认','title':title,'prompt':prompt,'review_summary':summ,'evidence':[x for x in rd(R/ep/'segments.json') if x['cue_id'] in cues],'priority':True,'related':[ep+'/'+c for c in cids],'detail':{'本次只确认':'助手按你意见写出的新增或拆分内容','原始字幕':'保留不变','不是在确认':'观点现实正确性、政策有效性或预测准确率'}})
d={'version':1,'dataset':hashlib.sha256(json.dumps(items,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'items':items,'videos':rd(R.parent/'review_round_002/review_data.json')['videos'],'original_run':str(R)};wr(O/'review_data.json',d)
t=(B/'review_round_002/template.html').read_text(encoding='utf-8').replace('第二轮质量抽查','第二轮修订确认').replace('第二轮 / 8项','第二轮修订 / 2项').replace('本轮8项','本轮2项').replace('这轮共8项，重点检查遗漏、条件和证据连接。','这里只确认第二轮意见落实后的2组新增或拆分内容。').replace('review_round_002/exports','review_round_002_delta/exports').replace('MacroMind_round002_','MacroMind_round002delta_').replace('封存的 run_002','封存的 run_003').replace("const optionSets={","const optionSets={\n'修订确认':[['accept_revision','确认采用展示的修订'],['change','还需修改'],['unsure','暂不能确认']],")
(O/'template.html').write_text(t,encoding='utf-8');(O/'HUMAN_REVIEW.html').write_text(t.replace('__DATA__',json.dumps(d,ensure_ascii=False).replace('<','\\u003c')),encoding='utf-8')
(B/'human_reviews/review_round_002_delta/exports').mkdir(parents=True,exist_ok=True)
wr(O/'verification.json',{'run003_artifacts_unchanged':len(m),'items':2,'unique_ids':len({i['id'] for i in items}),'raw_cue_evidence_preserved':True,'canonical_objects_changed':False,'all_decisions_initially_pending':True})
wr(O/'progress.json',{'stage':'GENERATED','unfinished':['Browser validation','User confirms two revisions'],'next_step':'Verify save/export/import UI'})
print('Generated two source-linked delta review cards; run003 unchanged.')
