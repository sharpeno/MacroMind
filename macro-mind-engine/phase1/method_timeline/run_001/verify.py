import json,subprocess,sys,os
from pathlib import Path
r=Path.cwd();o=r/'phase1/method_timeline/run_001';cmds={
'full_tests':[sys.executable,'-X','utf8','-m','pytest','-q','-p','no:cacheprovider','--basetemp='+str(o/'test_tmp')],
'lint':[sys.executable,'-m','ruff','check','src/macromind/methods/timeline.py','scripts/run_method_timeline.py','tests/methods/test_timeline.py'],
'format':[sys.executable,'-m','ruff','format','--check','src/macromind/methods/timeline.py','scripts/run_method_timeline.py','tests/methods/test_timeline.py'],
'cli_positive':[sys.executable,'-X','utf8','scripts/run_method_timeline.py','--packet',str(o/'T1.input.json'),'--previous',str(o/'T0/snapshot.json'),'--output',str(o/'cli_replay_T1')],
'cli_overwrite':[sys.executable,'-X','utf8','scripts/run_method_timeline.py','--packet',str(o/'T1.input.json'),'--previous',str(o/'T0/snapshot.json'),'--output',str(o/'T1')],
'canonical_navigation':[sys.executable,'-X','utf8','scripts/operations/project_status.py']}
for name,args in cmds.items():
 (o/(name+'.command.json')).write_text(json.dumps({'argv':args,'cwd':str(r)},indent=2))
 with (o/(name+'.stdout.txt')).open('w',encoding='utf-8') as a,(o/(name+'.stderr.txt')).open('w',encoding='utf-8') as b:res=subprocess.run(args,stdout=a,stderr=b,env={**os.environ,'PYTHONUTF8':'1','PYTHONPATH':str(r/'src')})
 (o/(name+'.result.json')).write_text(json.dumps({'exit_code':res.returncode}));print(name,res.returncode,flush=True)
