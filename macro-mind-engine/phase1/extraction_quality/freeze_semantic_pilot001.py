import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path('G:/youhegaojian/macro-mind-engine');B=ROOT/'phase1/batch_pilot';Q=ROOT/'phase1/extraction_quality';O=Q/'semantic_pilot_001';assert not O.exists();O.mkdir()
def rd(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prior=[]
for file in [B/'review_ui_v2/review_data.json',B/'review_round_002/review_data.json',B/'review_round_002_delta/review_data.json',Q/'holdout_001/review_data.json']:
 d=rd(file);prior.extend(x for x in d['items'] if file.parent.name!='review_ui_v2' or x['priority'])
items=[]
for ep,cid in [('EP002','C16'),('EP003','C16'),('EP005','C20')]:
 root=B/'run_004'/ep;a=rd(root/'annotation.json');c=next(c for c in a['claims'] if c[0]==cid);s=rd(root/'segments.json');used={v['cue_id'] for x in prior if x['episode']==ep for v in x['evidence']};assert not set(c[1])&used
 items.append({'id':ep+'/'+cid,'claim':c,'quotes':[x for x in s if x['cue_id'] in c[1]],'context':[x for x in s if min(c[1])-2<=x['cue_id']<=max(c[1])+2],'annotation_path':str(root/'annotation.json'),'annotation_sha256':sha(root/'annotation.json'),'segments_path':str(root/'segments.json'),'segments_sha256':sha(root/'segments.json')})
f=O/'frozen_sample.json';f.write_text(json.dumps({'time':datetime.now(timezone.utc).isoformat(),'selection':'Three claims absent from previous human review evidence; baseline seen by same assistant, not blind or random. Freeze before source-level self-check.','items':items},ensure_ascii=False,indent=2),encoding='utf-8');(O/'freeze_manifest.json').write_text(json.dumps({'frozen_sample_sha256':sha(f)},indent=2))
(O/'progress.json').write_text(json.dumps({'stage':'SAMPLE_FROZEN','unfinished':['Implement structured semantic self-check dossier','Apply nine-axis self-check to three samples','Validate and report; human acceptance remains separate']},indent=2))
for x in items:
 print(x['id'],x['claim'][2])
 for s in x['context']:print(s['cue_id'],s['quote'])
