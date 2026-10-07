import json,sys,os,subprocess,hashlib
from pathlib import Path
ROOT=Path('G:/youhegaojian/macro-mind-engine');B=ROOT/'phase1/batch_pilot';R=B/'run_003';O=ROOT/'phase1/extraction_quality/run_001'
def rd(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def call(name,ep,annotation=None,compile_to=None,pin=None,expected=0):
 report=O/(name+'.report.json');profile=O/'policies'/f'{ep}.json'
 args=[sys.executable,str(ROOT/'scripts/compile_reviewed_episode.py'),'--annotation',str(annotation or R/ep/'annotation.json'),'--segments',str(R/ep/'segments.json'),'--policy',str(profile),'--policy-sha256',pin or sha(profile),'--report',str(report)]
 if compile_to:args+=['--compile-to',str(compile_to)]
 with (O/(name+'.stdout.txt')).open('wb') as out,(O/(name+'.stderr.txt')).open('wb') as err:p=subprocess.run(args,cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/'src')),stdout=out,stderr=err)
 write(O/(name+'.command.json'),{'argv':args,'cwd':str(ROOT),'exit_code':p.returncode});assert p.returncode==expected,(name,p.returncode);print(name,p.returncode,flush=True)
 return rd(report)
for i in range(1,6):call(f'EP{i:03}_quality',f'EP{i:03}')
a=rd(R/'EP005/annotation.json');next(x for x in a['arguments'] if x[0]=='A03')[2]='C11';bad=O/'negative_whole_method.json';write(bad,a);denied=B/'quality_denied_should_not_exist'
call('blocked_edge','EP005',bad,denied,expected=2);assert not denied.exists()
a=rd(R/'EP003/annotation.json');next(x for x in a['claims'] if x[0]=='C07')[2]+=' 这是新增而未经复核的表述。';changed=O/'unreviewed_change.json';write(changed,a)
call('unreviewed_change','EP003',changed,denied,expected=1);assert not denied.exists()
call('tampered_pin','EP005',compile_to=denied,pin='0'*64,expected=2);assert not denied.exists()
trial=B/'quality_compile_trial_001';call('compile_success','EP005',compile_to=trial)
assert sha(trial/'EP005/active_bundle.json')==sha(R/'EP005/active_bundle.json')
write(O/'integration_results.json',{'baseline_checks':5,'blocked_wrong_edge':True,'changed_unreviewed_content_exit1':True,'tampered_policy_exit2':True,'blocked_runs_created_no_compile_output':True,'guarded_compile_byte_identical_active_bundle':True,'trial_path':str(trial),'semantic_acceptance':False,'held_out_semantic_accuracy':'NOT_MEASURED; unreviewed claim change only tests review routing'})
print('Integration checks complete.')
