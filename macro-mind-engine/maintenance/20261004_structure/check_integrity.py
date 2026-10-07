import hashlib,json,re
from pathlib import Path
r=Path.cwd();out=r/'maintenance/20261004_structure'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
baseline=rd(out/'baseline.json')
changed=[name for name,h in baseline.items() if not (r/name).is_file() or sha(r/name)!=h]
seals=[]
for base in [r/'phase1/batch_pilot',r/'phase1/extraction_quality']:
 for p in base.rglob('*manifest.json'):
  data=rd(p)
  for section in ['artifacts','generated_artifact_hashes','implementation']:
   for name,h in data.get(section,{}).items():
    target=p.parent/name
    seals.append({'manifest':str(p.relative_to(r)),'section':section,'path':str(target),'passed':target.is_file() and sha(target)==h})
raw=[]
for p in (r/'phase1/batch_pilot/run_001').glob('EP*/input_manifest.json'):
 for name,info in rd(p)['files'].items():
  target=r.parent/name
  raw.append({'path':name,'passed':target.is_file() and sha(target)==info['sha256']})
links=[]
for p in [r/'README.md',r.parent/'START_HERE.md',r.parent/'MACROMIND_MASTER_STATE.md',* (r/'docs/current').glob('*.md')]:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
  if not link.startswith(('http','https','#')):
   links.append({'file':str(p),'target':link,'exists':(p.parent/link.split('#')[0]).exists()})
result={'baseline_count':len(baseline),'changed_existing':changed,'unexpected_changes':[x for x in changed if x!='README.md'],'sealed_entries_checked':len(seals),'sealed_failures':[x for x in seals if not x['passed']],'original_inputs_checked':len(raw),'original_input_failures':[x for x in raw if not x['passed']],'links_checked':len(links),'broken_links':[x for x in links if not x['exists']]}
(out/'integrity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'seal_details.json').write_text(json.dumps(seals,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'original_input_details.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True,indent=2))
raise SystemExit(1 if any(result[k] for k in ['unexpected_changes','sealed_failures','original_input_failures','broken_links']) else 0)
