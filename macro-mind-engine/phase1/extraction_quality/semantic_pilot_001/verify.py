import json,subprocess,sys,os
from pathlib import Path
ROOT=Path('G:/youhegaojian/macro-mind-engine');O=ROOT/'phase1/extraction_quality/semantic_pilot_001';os.environ['PYTHONPATH']=str(ROOT/'src')
def cmd(name,args,expected=0):
 with (O/(name+'.stdout.txt')).open('wb') as out,(O/(name+'.stderr.txt')).open('wb') as err:p=subprocess.run(args,cwd=ROOT,stdout=out,stderr=err)
 (O/(name+'.command.json')).write_text(json.dumps({'argv':args,'cwd':str(ROOT),'exit_code':p.returncode}),encoding='utf-8');assert p.returncode==expected,(name,p.returncode);print(name,p.returncode,flush=True)
cmd('quality_tests',[sys.executable,'-m','pytest','tests/quality','-q'])
for ep in ['EP002','EP003','EP005']:
 cmd(ep+'_packet_cli',[sys.executable,str(ROOT/'scripts/validate_semantic_review.py'),'--packet',str(O/(ep+'.packet.json')),'--annotation',str(ROOT/'phase1/batch_pilot/run_004'/ep/'annotation.json'),'--segments',str(ROOT/'phase1/batch_pilot/run_004'/ep/'segments.json'),'--report',str(O/(ep+'.cli_result.json'))])
cmd('full_tests',[sys.executable,'-m','pytest','-q'])
cmd('changed_lint',[sys.executable,'-m','ruff','check','src/macromind/quality/semantic_review.py','tests/quality/test_semantic_review.py','scripts/validate_semantic_review.py'])
cmd('changed_format',[sys.executable,'-m','ruff','format','--check','src/macromind/quality/semantic_review.py','tests/quality/test_semantic_review.py','scripts/validate_semantic_review.py'])
