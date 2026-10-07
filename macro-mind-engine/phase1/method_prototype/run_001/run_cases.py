import subprocess,json,sys,os
from pathlib import Path
r=Path.cwd();o=r/'phase1/method_prototype/run_001'
commands={name:[sys.executable,'-X','utf8','scripts/run_method_prototype.py','--packet',str(o/(name+'.packet.json')),'--output',str(o/(name+'_trace'))] for name in ['public_case','complete','missing','outside','counter']}
commands['focused_tests']=[sys.executable,'-X','utf8','-m','pytest','-q','tests/methods','-p','no:cacheprovider']
for name,args in commands.items():
 (o/(name+'.command.json')).write_text(json.dumps({'argv':args,'cwd':str(r)},indent=2))
 with (o/(name+'.stdout.txt')).open('w',encoding='utf-8') as stdout,(o/(name+'.stderr.txt')).open('w',encoding='utf-8') as stderr:
  result=subprocess.run(args,stdout=stdout,stderr=stderr,env={**os.environ,'PYTHONUTF8':'1','PYTHONPATH':str(r/'src')})
 (o/(name+'.result.json')).write_text(json.dumps({'exit_code':result.returncode}))
 print(name,result.returncode,flush=True)
