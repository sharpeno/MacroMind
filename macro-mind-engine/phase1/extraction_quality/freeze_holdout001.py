import json,hashlib,sys,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path('G:/youhegaojian/macro-mind-engine');B=ROOT/'phase1/batch_pilot';R=B/'run_003';Q=ROOT/'phase1/extraction_quality/run_001';O=ROOT/'phase1/extraction_quality/holdout_001'
assert not O.exists(),'Resume existing evaluation rather than replace';O.mkdir()
def rd(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selection={'EP001':'C02','EP002':'C05','EP003':'C18','EP004':'C08','EP005':'C21'}
reviewed=[]
for file in [B/'review_ui_v2/review_data.json', B/'review_round_002/review_data.json',B/'review_round_002_delta/review_data.json']:
 d=rd(file)
 reviewed += [x for x in d['items'] if (file.parent.name!='review_ui_v2' or x.get('priority'))]
items=[]
for ep,cid in selection.items():
 a=rd(R/ep/'annotation.json');c=next(x for x in a['claims'] if x[0]==cid);segs=rd(R/ep/'segments.json');prior_cues={q['cue_id'] for it in reviewed if it['episode']==ep for q in it['evidence']}
 assert not set(c[1]) & prior_cues,(ep,cid)
 policy=rd(Q/'policies'/f'{ep}.json');assert cid not in policy['reviewed_ids'] and cid not in {x['claim'] for x in policy['facets']}
 items.append({'id':ep+'/'+cid,'claim':c,'source_file':str(R/ep/'annotation.json'),'annotation_sha256':sha(R/ep/'annotation.json'),'quotes':[s for s in segs if s['cue_id'] in c[1]],'context':[s for s in segs if min(c[1])-2<=s['cue_id']<=max(c[1])+2],'no_overlap_with_prior_review_cues':True,'no_specific_policy_facet':True,'baseline_fingerprint_already_known':True})
wr(O/'frozen_sample.json',{'frozen_at':datetime.now(timezone.utc).isoformat(),'selection':selection,'method':'One active unreviewed claim per episode; selected before reading detailed quotes this turn. Purposive small sample, not random. Same assistant second-pass, not blinded independent human evaluation. Baseline fingerprints known to guard.','items':items})
wr(O/'precheck_manifest.json',{'sample_sha256':sha(O/'frozen_sample.json'),'policy_hashes':{str(p):sha(p) for p in (Q/'policies').glob('*.json')}})
wr(O/'progress.json',{'stage':'SAMPLE_FROZEN','completed':['Five non-overlapping unreviewed claims frozen before semantic inspection'],'unfinished':['Run frozen guard','Compare statements with raw cues','Record capabilities and limitations','Prepare only necessary human calibration']})
for ep in selection:
 p=Q/'policies'/f'{ep}.json';args=[sys.executable,str(ROOT/'scripts/compile_reviewed_episode.py'),'--annotation',str(R/ep/'annotation.json'),'--segments',str(R/ep/'segments.json'),'--policy',str(p),'--policy-sha256',sha(p),'--report',str(O/(ep+'.guard.json'))]
 with (O/(ep+'.stdout.txt')).open('wb') as out,(O/(ep+'.stderr.txt')).open('wb') as err:r=subprocess.run(args,cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/'src')),stdout=out,stderr=err)
 wr(O/(ep+'.command.json'),{'argv':args,'cwd':str(ROOT),'exit_code':r.returncode});assert r.returncode==0
for x in items:
 print(x['id'],x['claim'][2])
 for s in x['context']:print(s['cue_id'],s['quote'])
