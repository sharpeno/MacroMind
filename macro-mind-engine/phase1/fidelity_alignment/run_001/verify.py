"""Read-only integrity checks; no semantic grading or model execution."""
import copy
import hashlib
import json
import re
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check_evidence(ref):
 source=ROOT/ref['source']
 assert sha(source)==ref['source_sha256']
 t=read(source)['cues']
 for e in ref['excerpts']:
  expected=[c for c in t if e['from']<=c['cue']<=e['to']]
  assert len(expected)==e['to']-e['from']+1
  assert e['cues']==expected
 assert sha(ROOT/ref['latest_review'])==ref['latest_review_sha256']

def main():
 protected=read(P/'protected_inputs.json')
 for path,h in protected.items():assert sha(ROOT/path)==h,path
 ev=read(P/'evidence.json')
 for ref in ev.values():check_evidence(ref)
 d=read(P/'diagnosis.json')['items'];f=read(P/'framework_candidate.json');s=read(P/'analyst_state.json')['entries']
 assert len(d)==12 and len(ev)==12 and len(f['operations'])==7 and len(s)==8
 assert len({x['id'] for x in d})==12
 ids={x['id'] for x in f['operations']}
 for x in d:assert x['evidence_ref'] in ev and x['candidate_operation'] in ids
 for x in f['operations']:assert set(x['evidence_refs'])<=set(ev) and x['stable_trait_verified'] is False
 assert sha(ROOT/f['parent_framework'])==f['parent_sha256']
 for x in s:
  assert x['evidence_ref'] in ev
  assert x['observed_episode']==ev[x['evidence_ref']]['episode']
  assert x['available_for_own_episode_transfer'] is False
  assert x['earliest_original_statement']=='UNKNOWN'
 examples=read(P/'reconstruction_examples.json')
 for x in examples:
  rows={c['cue']:c for e in ev[x['evidence_ref']]['excerpts'] for c in e['cues']}
  assert all(rows[c['cue']]==c for c in x['force_evidence'])
 links=0
 for file in list(P.glob('*.md'))+[ROOT/'docs/current/FIDELITY_ALIGNMENT.md']:
  for target in re.findall(r'\]\(([^)]+)\)',file.read_text(encoding='utf-8-sig')):
   if '://' not in target:
    assert (file.parent/target.split('#')[0]).is_file(),(file,target)
    links+=1
 bad=copy.deepcopy(next(iter(ev.values())))
 bad['excerpts'][0]['cues'][0]['text']='intentionally corrupted'
 rejected=False
 try:check_evidence(bad)
 except AssertionError:rejected=True
 assert rejected
 sealed=0
 if (P/'manifest.json').exists():
  for n,h in read(P/'manifest.json').items():assert sha(P/n)==h,n;sealed+=1
 return {'structural_integrity':'PASS','protected_files_checked':len(protected),'diagnoses':len(d),'operations':len(ids),'state_entries':len(s),'reconstruction_examples':len(examples),'local_links_checked':links,'tampered_quote_rejected':rejected,'sealed_files_checked':sealed,'semantic_approval':False,'model_comparison_executed':False,'remaining_unread_episodes':[476,478,479,480,482,484,493,495,496,509,601],'scope':'Only hashes, exact quotes, references, counts and recorded cutoff fields; no semantic or temporal-enforcement certification'}
if __name__=='__main__':print(json.dumps(main(),ensure_ascii=False,indent=2))
