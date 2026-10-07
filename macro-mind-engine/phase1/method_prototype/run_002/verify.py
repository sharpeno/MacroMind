import json,subprocess,sys,os
from pathlib import Path
r=Path.cwd();o=r/'phase1/method_prototype/run_002'
commands={'full_tests':[sys.executable,'-X','utf8','-m','pytest','-q','-p','no:cacheprovider','--basetemp='+str(o/'test_tmp')],'lint':[sys.executable,'-m','ruff','check','src/macromind/methods/inference.py','tests/methods/test_inference.py'],'format':[sys.executable,'-m','ruff','format','--check','src/macromind/methods/inference.py','tests/methods/test_inference.py']}
for name,args in commands.items():
 (o/(name+'.command.json')).write_text(json.dumps({'argv':args,'cwd':str(r)},indent=2))
 with (o/(name+'.stdout.txt')).open('w',encoding='utf-8') as a,(o/(name+'.stderr.txt')).open('w',encoding='utf-8') as b:res=subprocess.run(args,stdout=a,stderr=b,env={**os.environ,'PYTHONUTF8':'1','PYTHONPATH':str(r/'src')})
 (o/(name+'.result.json')).write_text(json.dumps({'exit_code':res.returncode}));print(name,res.returncode,flush=True)
