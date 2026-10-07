import json,subprocess,sys,os
from pathlib import Path
R=Path('G:/youhegaojian/macro-mind-engine');O=R/'phase1/extraction_quality/run_001'
def cmd(name,args,expected=0):
 meta={'argv':args,'cwd':str(R),'exit_code':None};(O/(name+'.command.json')).write_text(json.dumps(meta,indent=2),encoding='utf-8')
 with (O/(name+'.stdout.txt')).open('wb') as out,(O/(name+'.stderr.txt')).open('wb') as err:p=subprocess.run(args,cwd=R,env=dict(os.environ,PYTHONPATH=str(R/'src')),stdout=out,stderr=err)
 meta['exit_code']=p.returncode;(O/(name+'.command.json')).write_text(json.dumps(meta,indent=2),encoding='utf-8');print(name,p.returncode,flush=True);assert p.returncode==expected,name

cmd('final_targeted_tests',[sys.executable,'-m','pytest','tests/quality','-q'])
cmd('final_full_tests',[sys.executable,'-m','pytest','-q'])
cmd('final_changed_lint',[sys.executable,'-m','ruff','check','src/macromind/quality','tests/quality','scripts/compile_reviewed_episode.py'])
cmd('final_changed_format',[sys.executable,'-m','ruff','format','--check','src/macromind/quality','tests/quality','scripts/compile_reviewed_episode.py'])
