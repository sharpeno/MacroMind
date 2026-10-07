import json,hashlib,shutil,sys,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
B=Path('G:/youhegaojian/macro-mind-engine/phase1/batch_pilot');ROOT=B.parents[1];OLD=B/'run_002';R=B/'run_003';ARCH=B/'human_reviews/review_round_002/batch_001'
def rd(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def progress(stage,pending):
 v={'time':datetime.now(timezone.utc).isoformat(),'stage':stage,'unfinished':pending,'next_step':pending[0] if pending else 'Await review of assistant-derived changes; no scale-up'};wr(R/'progress.json',v)
 with (R/'progress.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(v,ensure_ascii=False)+'\n')
def cmd(name,args):
 wr(R/(name+'.command.json'),{'argv':args,'cwd':str(ROOT.parent),'status':'RUNNING'})
 with (R/(name+'.stdout.txt')).open('wb') as out,(R/(name+'.stderr.txt')).open('wb') as err:p=subprocess.run(args,cwd=ROOT.parent,env=dict(os.environ,PYTHONPATH=str(ROOT/'src')),stdout=out,stderr=err)
 wr(R/(name+'.command.json'),{'argv':args,'cwd':str(ROOT.parent),'exit_code':p.returncode});assert p.returncode==0,name
if __name__=='__main__':
 assert not R.exists(),'Resume existing run, do not overwrite';R.mkdir();progress('RECEIVING',['Validate input','Revise annotations','Compile and audit','Verify and report'])
 source=Path('C:/Users/无语/Downloads/MacroMind_round002_2026-10-04_031040_CST_8of8_full_826e7ab4.json');p=rd(source);data=rd(B/'review_round_002/review_data.json');ids={x['id']:x for x in data['items']}
 assert p['format']=='macromind-human-review' and p['version']==2 and p['dataset']==data['dataset'];assert len(p['records'])==8 and {x['id'] for x in p['records']}==set(ids)
 for x in p['records']:
  assert all(x[k]==ids[x['id']][k] for k in ['episode','kind']);assert x['decision'] in {'faithful','extract','reject','change','context'}
  assert all(isinstance(x[k],str) for k in ['note','correction','evidence','reviewer']);datetime.fromisoformat(x['updated_at'].replace('Z','+00:00'))
 checks=[]
 for root,m in [(B/'run_001',rd(B/'run_001/acceptance_manifest.json')['generated_artifact_hashes']),(OLD,rd(OLD/'revision_manifest.json')['artifacts']),(B/'review_round_002',rd(B/'review_round_002/manifest.json')['artifacts'])]:
  bad=[f for f,h in m.items() if sha(root/f)!=h];assert not bad;checks.append({'root':str(root),'count':len(m),'mismatches':bad})
 target=ARCH/'raw'/source.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);assert sha(source)==sha(target)
 wr(ARCH/'receipt.json',{'source':str(source),'raw_path':str(target),'sha256':sha(target),'dataset':p['dataset'],'records':8,'reviewer':'User submission; name blank','immutable_checks':checks});wr(ARCH/'reviewed_records.json',p['records']);wr(R/'review_input.json',{'receipt':str(ARCH/'receipt.json'),'sha256':sha(target),'records':p['records']})
 specs={}
 for i in range(1,6):
  ep=f'EP{i:03}';(R/ep).mkdir();shutil.copyfile(OLD/ep/'segments.json',R/ep/'segments.json');specs[ep]=rd(OLD/ep/'annotation.json')
 def change(ep,cid,text,cues=None):
  cs=specs[ep]['claims'];old=next((x for x in cs if x[0]==cid),None)
  if old:old[2]=text;old[1]=cues if cues is not None else old[1]
  else:cs.append([cid,cues,text,'active'])
 change('EP001','C19','博主判断，在燃油价格及成本继续上涨的条件下，企业压缩利润延缓涨价无法长期维持，因此服务通胀缓和可能只是暂时现象。')
 a=next(x for x in specs['EP001']['arguments'] if x[0]=='A03');a[3]='在成本继续上涨的条件下，利润压缩缓冲难以长期维持；这是博主对通胀缓和暂时性的判断。'
 change('EP002','C22','博主转述并反对“加息只是暂时、不会影响交易方向”的市场说法，并判断只要9月加息落地，市场叙事就会明显改变；本段仍是决策落地前的条件性预期。',list(range(223,236)))
 rec={x['id']:x for x in p['records']}
 change('EP003','C23',rec['R02/EP003/C23']['correction'])
 next(x for x in specs['EP003']['methods'] if x[0]=='M02')[2]='对比历史经验与当前市场反应的反差，再提出原因解释；仅记录本段分析过程，不证明解释正确。'
 change('EP004','C15',rec['R02/EP004/C15']['correction']);specs['EP004']['forecast_candidates'].remove('C15')
 change('EP004','C22','博主提出，先理解行业演化、成功机制和可持续空间，再对比市场定价；若落差来自市场对企业认识不足，则可能存在市场机会；若企业名不副实，则应提前识别风险、避雷。')
 next(x for x in specs['EP004']['methods'] if x[0]=='M02')[2]='从行业演化和成功机制判断空间，再对照市场认知；区分认识不足带来的机会与名不副实的风险。'
 change('EP005','C11','博主将化债方法归纳为三个并列方向：短期债变长期债、高息债变低息债、外债变内债；这是其方法说明，不是由单个融资压力理由推导出的整套结论。')
 change('EP005','C28','博主提出以长期债替换短期债，延长偿付期限。',[220,221,228,231,232,233,234,235])
 change('EP005','C29','博主提出以低息债替换高息债，降低债务利息成本。',[220,222,226,228])
 change('EP005','C30','博主把外债转为内债列为调整债务结构的一个方向。',[227,228,229])
 a=next(x for x in specs['EP005']['arguments'] if x[0]=='A03');a[2]='C28';a[3]='较短偿付周期带来的频繁融资需求，为短债换长债提供问题背景和动机；并非必然性推导，不据此解释降低利息或外债转内债。'
 for ep,s in specs.items():wr(R/ep/'annotation.json',s)
 wr(R/'usage_constraints.json',{'EP004/C15':{'role':'BACKGROUND_CONDITIONAL_OUTLOOK','forecast_accuracy_eligible':False,'stock_selection_rule_eligible':False,'reason':'No identified firms, ex-ante selection criteria or return calculation. Original ten-year/thousandfold wording retained in unmodified quotes. Scenario S01 remains illustrative only.'},'EP005/C11':{'role':'PARALLEL_METHOD_DESCRIPTION','components':['EP005/C28','EP005/C29','EP005/C30'],'component_membership_is_not_inference':True},'EP005/A03':{'reason_supports_only':'EP005/C28','edge_semantics':'MOTIVATION_NOT_DEDUCTIVE_PROOF'},'EP005/cue/0230':{'human_decision':'context','extract_new_claim':False}})
 # User-confirmed transcript overlay remains separate from canonical source evidence.
 overlay=B/'human_reviews/run_002/batch_001/clarification_001'
 wr(R/'transcript_overlay_reference.json',{'path':str(overlay/'adopted_transcription_corrections.json'),'sha256':sha(overlay/'adopted_transcription_corrections.json'),'status':'6 corrections retained as USER_CONFIRMED_ADOPTED','canonical_source_unchanged':True})
 progress('REVISIONS_SAVED',['Compile five affected episodes','Audit','Verify and report'])
 shutil.copyfile(OLD/'build_episode.py',R/'build_episode.py');shutil.copyfile(OLD/'run_audits.py',R/'run_audits.py')
 for ep in specs:cmd(ep+'_build',[sys.executable,str(R/'build_episode.py'),ep]);print(ep+' compiled',flush=True)
 progress('COMPILED',['Audit','Verify and report']);cmd('all_audits',[sys.executable,str(R/'run_audits.py')]);progress('AUDITS_COMPLETED',['Verify diff and preserved reviews','Report and seal']);print('Audits completed',flush=True)
