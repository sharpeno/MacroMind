import subprocess,json,sys,os
from pathlib import Path
r=Path.cwd();o=r/'phase1/method_prototype/run_001'
commands={
 'full_tests':[sys.executable,'-X','utf8','-m','pytest','-q','-p','no:cacheprovider','--basetemp='+str(o/'test_tmp')],
 'lint':[sys.executable,'-m','ruff','check','src/macromind/methods','scripts/run_method_prototype.py','tests/methods'],
 'format':[sys.executable,'-m','ruff','format','--check','src/macromind/methods','scripts/run_method_prototype.py','tests/methods'],
 'canonical_navigation':[sys.executable,'-X','utf8','scripts/operations/project_status.py'],
 'overwrite_rejection':[sys.executable,'-X','utf8','scripts/run_method_prototype.py','--packet',str(o/'public_case.packet.json'),'--output',str(o/'public_case_trace')],
}
for name,args in commands.items():
 (o/(name+'.command.json')).write_text(json.dumps({'argv':args,'cwd':str(r)},indent=2))
 with (o/(name+'.stdout.txt')).open('w',encoding='utf-8') as stdout,(o/(name+'.stderr.txt')).open('w',encoding='utf-8') as stderr:
  result=subprocess.run(args,stdout=stdout,stderr=stderr,env={**os.environ,'PYTHONUTF8':'1','PYTHONPATH':str(r/'src')})
 (o/(name+'.result.json')).write_text(json.dumps({'exit_code':result.returncode}))
 print(name,result.returncode,flush=True)
