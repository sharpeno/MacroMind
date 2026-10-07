import sys,json,hashlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_phase1_5c import request,cli_run,write
RUN=Path(__file__).parent
os.environ['PYTHONPATH']=str(ROOT/'src')
results={}
for ep in ['EP001','EP002','EP003','EP004','EP005','EP001_repeat']:
    source=RUN/ep[:5]/'active_bundle.json'
    req=request([{'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'artifact_type':'primary','phase':'BATCH_PILOT_FIRST5','component':ep[:5],'data_kind':'REAL'}],'CANONICAL')
    req['validation_context']={'validation_mode':'complete_bundle'}
    results[ep]=cli_run(RUN,ep+'_audit',req)
    write(RUN/'audit_results.json',results)
    print(ep,json.dumps(results[ep]),flush=True)
