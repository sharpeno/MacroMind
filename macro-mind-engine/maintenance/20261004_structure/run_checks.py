import subprocess,json,sys,os
from pathlib import Path
r=Path.cwd();p=r/'maintenance/20261004_structure'
commands={
 'after':[sys.executable,'-X','utf8','-m','pytest','-q','--basetemp='+str(p/'after_tmp')],
 'navigation':[sys.executable,'-X','utf8','scripts/operations/project_status.py'],
 'changed_lint':[sys.executable,'-m','ruff','check','scripts/operations','tests/operations'],
 'changed_format':[sys.executable,'-m','ruff','format','--check','scripts/operations','tests/operations'],
 'global_lint':[sys.executable,'-m','ruff','check','src','tests'],
 'cli_help':[sys.executable,'-X','utf8','-m','macromind.cli.main','--help'],
}
for name,args in commands.items():
 (p/(name+'.command.json')).write_text(json.dumps({'argv':args,'cwd':str(r)},indent=2))
 with (p/(name+'.stdout.txt')).open('w',encoding='utf-8') as o,(p/(name+'.stderr.txt')).open('w',encoding='utf-8') as e:
  result=subprocess.run(args,stdout=o,stderr=e,env={**os.environ,'PYTHONUTF8':'1','PYTHONPATH':str(r/'src')})
 (p/(name+'.result.json')).write_text(json.dumps({'exit_code':result.returncode}))
 print(name,result.returncode,flush=True)
