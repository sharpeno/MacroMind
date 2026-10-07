import json,hashlib,shutil,sys,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path('G:/youhegaojian/macro-mind-engine');sys.path.insert(0,str(ROOT/'src'))
from macromind.quality.annotations import records,digest
B=ROOT/'phase1/batch_pilot';OLD=B/'run_003';R=B/'run_004';Q=ROOT/'phase1/extraction_quality';H=Q/'holdout_001';O=Q/'calibrated_001';A=B/'human_reviews/holdout_001/batch_001'
def rd(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def cmd(name,args,expected=0):
 wr(O/(name+'.command.json'),{'argv':args,'cwd':str(ROOT),'exit_code':None})
 with (O/(name+'.stdout.txt')).open('wb') as out,(O/(name+'.stderr.txt')).open('wb') as err:r=subprocess.run(args,cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/'src')),stdout=out,stderr=err)
 wr(O/(name+'.command.json'),{'argv':args,'cwd':str(ROOT),'exit_code':r.returncode});assert r.returncode==expected,(name,r.returncode)
 print(name,r.returncode,flush=True)
def progress(stage,pending):
 v={'time':datetime.now(timezone.utc).isoformat(),'stage':stage,'unfinished':pending,'next_step':pending[0] if pending else 'Calibration feedback closed; no blanket acceptance'};wr(O/'progress.json',v)
 with (O/'progress.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(v,ensure_ascii=False)+'\n')
if __name__=='__main__':
 assert not R.exists() and not O.exists(),'Resume existing outputs';R.mkdir();O.mkdir();progress('RECEIVING',['Validate review','Apply two corrections using guarded compiler','Verify audit and calibration results'])
 source=Path('C:/Users/无语/Downloads/MacroMind_holdout001_2026-10-04_042318_CST_5of5_full_d6ed493a.json');p=rd(source);d=rd(H/'review_data.json');by={x['id']:x for x in d['items']};assert p['dataset']==d['dataset'] and p['format']=='macromind-human-review' and p['version']==2
 assert len(p['records'])==5 and {x['id'] for x in p['records']}==set(by)
 for x in p['records']:
  assert x['decision'] in {'keep_original','change','adopt_proposal'} and all(x[k]==by[x['id']][k] for k in ['episode','kind']);assert all(isinstance(x[k],str) for k in ['note','correction','evidence']);datetime.fromisoformat(x['updated_at'].replace('Z','+00:00'))
 m=rd(H/'manifest.json')['artifacts'];assert all(sha(H/f)==h for f,h in m.items())
 target=A/'raw'/source.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);assert sha(target)==sha(source)
 wr(A/'receipt.json',{'received_at':datetime.now(timezone.utc).isoformat(),'source_path':str(source),'raw_path':str(target),'sha256':sha(target),'dataset':p['dataset'],'record_count':5,'decisions':{'keep_original':3,'change':1,'adopt_proposal':1},'reviewer':'User submission; name blank'});wr(A/'reviewed_records.json',p['records'])
 recs={x['id']:x for x in p['records']};assessment={x['id']:x for x in rd(H/'assistant_assessment.json')}
 edits={'EP002':('C05',recs['H01/EP002/C05']['correction']),'EP003':('C18',assessment['EP003/C18']['proposed_text'])};assert all(text for cid,text in edits.values())
 (O/'policies').mkdir();(O/'inputs').mkdir()
 source_hashes={}
 for i in range(1,6):
  ep=f'EP{i:03}';spec=rd(OLD/ep/'annotation.json');policy=rd(Q/'run_001/policies'/f'{ep}.json')
  if ep in edits:
   cid,text=edits[ep];next(c for c in spec['claims'] if c[0]==cid)[2]=text
   policy['baseline']={k:digest(v) for k,v in records(spec).items()}
   policy['facets'].append({'claim':cid,'name':'User-calibrated attribution and reasoning scope','required_text':['接近见底','假设中国官方','假设前提'] if ep=='EP002' else ['不能凭个人意愿','市场交易压力','冲浪者而非浪潮制造者']})
  cid={'EP001':'C02','EP002':'C05','EP003':'C18','EP004':'C08','EP005':'C21'}[ep]
  policy['reviewed_ids']=sorted(set(policy['reviewed_ids']+[cid]));policy['review_evidence'].append(str(A/'receipt.json'));wr(O/'policies'/f'{ep}.json',policy);wr(O/'inputs'/f'{ep}.annotation.json',spec)
  source_hashes[ep]=sha(O/'policies'/f'{ep}.json')
  args=[sys.executable,str(ROOT/'scripts/compile_reviewed_episode.py'),'--annotation',str(O/'inputs'/f'{ep}.annotation.json'),'--segments',str(OLD/ep/'segments.json'),'--policy',str(O/'policies'/f'{ep}.json'),'--policy-sha256',source_hashes[ep],'--report',str(O/(ep+'.quality.json'))]
  if ep in edits:
   trial=B/('calibrated_compile_'+ep+'_001');args+=['--compile-to',str(trial)];cmd(ep+'_guarded_compile',args);shutil.copytree(trial/ep,R/ep)
  else:
   cmd(ep+'_unchanged_guard',args);shutil.copytree(OLD/ep,R/ep)
 wr(O/'policy_manifest.json',source_hashes)
 wr(R/'lineage.json',{'previous':'run_003','human_review_receipt':str(A/'receipt.json'),'changed_episodes':['EP002','EP003'],'unchanged_episodes_reused':['EP001','EP004','EP005'],'transcription_overlay':str(OLD/'transcript_overlay_reference.json'),'ep004_c08':'Original explicitly retained; assistant proposal not applied','semantics':'User-approved paraphrase changes only; no external truth verification'})
 # Copy unchanged boundaries; no new candidate forecast or method created.
 for filename in ['usage_constraints.json','transcript_overlay_reference.json']:shutil.copyfile(OLD/filename,R/filename)
 progress('TWO_USER_APPROVED_CORRECTIONS_COMPILED',['Audit two changed episodes','Regression comparison and immutability','Report and seal'])
 sys.path.insert(0,str(ROOT/'scripts'));from verify_phase1_5c import request,cli_run
 os.environ['PYTHONPATH']=str(ROOT/'src');audits={}
 for ep in ['EP002','EP003']:
  f=R/ep/'active_bundle.json';req=request([{'path':str(f),'sha256':sha(f),'artifact_type':'primary','phase':'BATCH_PILOT_FIRST5','component':ep,'data_kind':'REAL'}],'CANONICAL');req['validation_context']={'validation_mode':'complete_bundle'};audits[ep]=cli_run(R,ep+'_audit',req);wr(R/'audit_results.json',audits);print(ep+' audited',flush=True)
 wr(R/'unchanged_audit_references.json',{ep:rd(OLD/'audit_results.json')[ep] for ep in ['EP001','EP004','EP005']})
 progress('AUDITS_COMPLETED',['Regression comparison and immutability','Report and seal'])
