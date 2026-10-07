import hashlib,json,re
from pathlib import Path
r=Path.cwd();o=r/'phase1/method_prototype/run_001'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
b=rd(o/'baseline.json');changes=[n for n,h in b.items() if not (r/n).is_file() or sha(r/n)!=h]
allowed={'docs/current/README.md','docs/current/STATUS.md'}
seals=[]
for base in [r/'phase1/batch_pilot',r/'phase1/extraction_quality']:
 for p in base.rglob('*manifest.json'):
  for section in ['artifacts','generated_artifact_hashes','implementation']:
   for name,h in rd(p).get(section,{}).items():
    target=p.parent/name;seals.append({'manifest':str(p),'path':str(target),'passed':target.is_file() and sha(target)==h})
raw=[]
for p in (r/'phase1/batch_pilot/run_001').glob('EP*/input_manifest.json'):
 for name,info in rd(p)['files'].items():
  target=r.parent/name;raw.append({'path':name,'passed':target.is_file() and sha(target)==info['sha256']})
links=[]
for p in [r/'docs/current/README.md',r/'docs/current/STATUS.md',r/'docs/current/METHOD_PROTOTYPE.md']:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
  if not link.startswith(('http','#')):links.append({'file':str(p),'target':link,'passed':(p.parent/link).exists()})
result={'baseline_count':len(b),'changed_existing':changes,'unexpected_changes':[x for x in changes if x not in allowed],'historical_seal_entries':len(seals),'seal_failures':[x for x in seals if not x['passed']],'original_inputs':len(raw),'input_failures':[x for x in raw if not x['passed']],'local_links':len(links),'broken_links':[x for x in links if not x['passed']]}
(o/'integrity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True,indent=2))
raise SystemExit(1 if any(result[k] for k in ['unexpected_changes','seal_failures','input_failures','broken_links']) else 0)
