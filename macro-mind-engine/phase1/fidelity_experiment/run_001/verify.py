import hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def values(x):
 if isinstance(x,str):return [x]
 if isinstance(x,dict):return [s for v in x.values() for s in values(v)]
 if isinstance(x,list):return [s for v in x for s in values(v)]
 return []
def verify():
 locks=read(P/'input_lock.json')
 for n,h in locks.items():assert sha(P/n)==h,n
 for n,h in read(P/'source_hashes.json').items():assert sha(ROOT/n)==h,n
 summaries=[]
 for arm in 'ABC':
  for ep in range(472,476):
   f=P/f'arms/{arm}/answer_{ep}.json';d=read(f)
   assert str(d['case'])==str(ep)
   assert len(d['units'])==3
   ids=[u['id'] for u in d['units']];assert len(set(ids))==3
   contract=read(P/f'common/case_{ep}.json')['output_contract']
   for u in d['units']:assert set(contract['unit_fields'])<=set(u),(arm,ep,u.get('id'))
   text=''.join(values(d));count=len(re.findall(r'[\u3400-\u9fff]',text))
   summaries.append({'arm':arm,'case':ep,'sha256':sha(f),'chinese_chars':count,'within_target':900<=count<=1300,'within_maximum':count<=1600})
 seal_checked=0
 if (P/'answer_lock.json').exists():
  for n,h in read(P/'answer_lock.json')['files'].items():assert sha(P/n)==h,n;seal_checked+=1
 return {'input_hashes':'PASS','input_files':len(locks),'source_files':len(read(P/'source_hashes.json')),'answers':summaries,'sealed_output_files_checked':seal_checked,'structural_only':True}
if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False,indent=2))
