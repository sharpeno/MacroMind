import sys,json,hashlib,shutil,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path('G:/youhegaojian/macro-mind-engine');sys.path.insert(0,str(ROOT/'src'))
from macromind.quality.annotations import digest,records,assess
B=ROOT/'phase1/batch_pilot';Q=ROOT/'phase1/extraction_quality';OLD=B/'run_004';R=B/'run_005';H=Q/'semantic_pilot_001';O=Q/'semantic_calibrated_001';A=B/'human_reviews/semantic_pilot_001/batch_001'
def rd(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def progress(stage,pending):
 v={'time':datetime.now(timezone.utc).isoformat(),'stage':stage,'unfinished':pending,'next_step':pending[0] if pending else 'This feedback closed; evaluate method representation next'};wr(O/'progress.json',v)
 with (O/'progress.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(v,ensure_ascii=False)+'\n')
def cmd(name,args,expected=0):
 with (O/(name+'.stdout.txt')).open('wb') as out,(O/(name+'.stderr.txt')).open('wb') as err:p=subprocess.run(args,cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/'src')),stdout=out,stderr=err)
 wr(O/(name+'.command.json'),{'argv':args,'cwd':str(ROOT),'exit_code':p.returncode});assert p.returncode==expected,(name,p.returncode);print(name,p.returncode,flush=True)
if __name__=='__main__':
 assert not R.exists() and not O.exists(),'Resume existing revision';R.mkdir();O.mkdir();progress('RECEIVING',['Verify input','Extract missing method and separate application','Guarded compilation and audits','Verification and closure'])
 src=Path('C:/Users/无语/Downloads/MacroMind_semantic001_2026-10-04_044803_CST_3of3_full_3c6fdbb3.json');p=rd(src);d=rd(H/'review_data.json');by={x['id']:x for x in d['items']};assert p['dataset']==d['dataset'] and p['format']=='macromind-human-review' and p['version']==2
 assert len(p['records'])==3 and {x['id'] for x in p['records']}==set(by)
 for x in p['records']:
  assert x['decision'] in ['change','adopt_proposal','keep_original'] and all(x[k]==by[x['id']][k] for k in ['kind','episode']);assert all(isinstance(x[k],str) for k in ['note','correction','evidence']);datetime.fromisoformat(x['updated_at'].replace('Z','+00:00'))
 target=A/'raw'/src.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target);assert sha(src)==sha(target)
 wr(A/'receipt.json',{'source_path':str(src),'raw_path':str(target),'sha256':sha(target),'dataset':p['dataset'],'records':3,'reviewer':'User submission; name blank','received_at':datetime.now(timezone.utc).isoformat()});wr(A/'reviewed_records.json',p['records'])
 method='博主认为，当群众犯错时，领导者应提前识别问题、准备纠错方案，同时先与群众站在一起、共同经历这一错误，在过程中引导大家认识问题，再于适当时机提出预先准备的方案，带领大家纠错。'
 application='博主用假想央行讲话作为提前准备并择机提出纠错方案的应用例证，设想结合货币与财政政策应对通胀、低增长和信用压力；这是可能政策路径的推演，不是央行已经发表的讲话。'
 proposal=rd(H/'EP003.packet.json')['items'][0]['proposed_statement']
 policies={}
 for i in range(1,6):
  ep=f'EP{i:03}';a=rd(OLD/ep/'annotation.json');pol=rd(Q/'calibrated_001/policies'/f'{ep}.json')
  if ep=='EP002':
   c=next(c for c in a['claims'] if c[0]=='C16');c[1]=list(range(396,401));c[2]=application;a['claims'].append(['C23',list(range(387,393)),method,'active']);a['methods'].append(['M03',list(range(387,393)),'区分可复用的引导纠错方法与其假想政策应用：提前识别并准备，与群众同行和引导，择机提出方案，带领纠错；不证明方法有效或为博主原创。'])
   pol['facets'] += [{'claim':'C23','name':'领导纠错方法而非只有政策细节','required_text':['提前识别问题','准备纠错方案','与群众站在一起','适当时机','带领大家纠错']},{'claim':'C16','name':'假想政策作为应用例证','required_text':['应用例证','假想央行讲话','不是央行已经发表']}]
   pol['reviewed_ids']=sorted(set(pol['reviewed_ids']+['C23']))
  elif ep=='EP003':
   next(c for c in a['claims'] if c[0]=='C16')[2]=proposal;pol['facets'].append({'claim':'C16','name':'AI猜想的前提和范围','required_text':['猜想','相关期待仍未消失','新市场可能承接','未明确承接市场及时间']});pol['reviewed_ids']=sorted(set(pol['reviewed_ids']+['C16']))
  elif ep=='EP005':pol['reviewed_ids']=sorted(set(pol['reviewed_ids']+['C20']))
  pol['baseline']={k:digest(v) for k,v in records(a).items()};pol['review_evidence'].append(str(A/'receipt.json'));wr(O/'policies'/f'{ep}.json',pol);wr(O/'inputs'/f'{ep}.annotation.json',a);policies[ep]=sha(O/'policies'/f'{ep}.json')
  args=[sys.executable,str(ROOT/'scripts/compile_reviewed_episode.py'),'--annotation',str(O/'inputs'/f'{ep}.annotation.json'),'--segments',str(OLD/ep/'segments.json'),'--policy',str(O/'policies'/f'{ep}.json'),'--policy-sha256',policies[ep],'--report',str(O/(ep+'.guard.json'))]
  if ep in ['EP002','EP003']:
   trial=B/('semantic_compile_'+ep+'_001');args+=['--compile-to',str(trial)];cmd(ep+'_guarded_compile',args);shutil.copytree(trial/ep,R/ep)
  else:cmd(ep+'_retained_check',args);shutil.copytree(OLD/ep,R/ep)
 wr(O/'policy_manifest.json',policies)
 segs={s['cue_id']:s for s in rd(R/'EP002/segments.json')}
 steps=[('提前识别问题',[389]),('提前准备纠错方案并控制错误程度',[390,392]),('与群众同行、共同经历错误并引导认识',[387,388,389]),('在适当时机提出方案并带领纠错',[390])]
 wr(R/'method_evidence.json',{'method_claim':'EP002/C23','attribution':'博主转述并认同；原始说法作者未给出，不能认作博主原创','steps':[{'step':name,'quotes':[segs[n] for n in ns]} for name,ns in steps],'ordering':'对原话方法的分析整理，步骤可能交叠，不声称机械线性执行顺序','application_claim':'EP002/C16','application_quotes':[segs[n] for n in range(396,401)],'relation':'ILLUSTRATES_METHOD','relation_storage':'Evidence sidecar, not an added canonical deductive Argument','method_effectiveness_verified':False,'skill_ready':False})
 for f in ['usage_constraints.json','transcript_overlay_reference.json']:shutil.copyfile(OLD/f,R/f)
 wr(R/'lineage.json',{'previous':'run_004','receipt':str(A/'receipt.json'),'changed':['EP002/C16','EP002/C23 new','EP002/M03 new observation','EP003/C16'],'retained':'EP005/C20 and all other original claims','original_quotes_unchanged':True,'user_correction_method_applied_verbatim':True,'application_wording':'Assistant implementation of explicit request to separate hypothetical application; not separately reapproved'})
 progress('REVISIONS_COMPILED',['Audit two affected episodes','Verify scope, evidence and regressions','Close feedback with precise limits'])
 sys.path.insert(0,str(ROOT/'scripts'));from verify_phase1_5c import request,cli_run
 os.environ['PYTHONPATH']=str(ROOT/'src');audits={}
 for ep in ['EP002','EP003']:
  f=R/ep/'active_bundle.json';req=request([{'path':str(f),'sha256':sha(f),'artifact_type':'primary','phase':'BATCH_PILOT_FIRST5','component':ep,'data_kind':'REAL'}],'CANONICAL');req['validation_context']={'validation_mode':'complete_bundle'};audits[ep]=cli_run(R,ep+'_audit',req);wr(R/'audit_results.json',audits);print(ep+' audited',flush=True)
 wr(R/'unchanged_audit_references.json',rd(OLD/'unchanged_audit_references.json'));progress('AUDITS_COMPLETED',['Verify scope and evidence','Report and seal'])
