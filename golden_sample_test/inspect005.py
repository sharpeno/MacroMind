import re,json,html
from pathlib import Path
p=next(Path(r'G:\BilibiliDown.v6.41.release\download\有何高见9527').glob('*七百四五期*.srt'))
cs=[]
for b in re.split(r'\n\s*\n',p.read_text(encoding='utf-8-sig').strip()):
 l=b.splitlines()
 if l and l[0].isdigit(): cs.append({'id':int(l[0]),'time':l[1],'text':' '.join(l[2:])})
Path('golden_sample_005/cue_index.txt').write_text('\n'.join(f"{c['id']} {c['time']} {c['text']}" for c in cs),encoding='utf-8')
for p in Path('golden_sample_005/source_snapshots').glob('*.txt'):
 t=p.read_text(encoding='utf-8')
 for m in re.finditer(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',t):
  try:
   d=json.loads(m.group(1))['props']['pageProps']['articleDetail']
   Path(f"golden_sample_005/source_snapshots/article_{d['id']}.json").write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
  except Exception: pass
 print(p.name)
 for line in t.splitlines():
  if any(x in line for x in ['Aug.','August 2','2026-08-2','Published','Original Date']) and len(line)<1500: print(line)
for p in Path('golden_sample_005/source_snapshots').glob('article_*.json'):
 d=json.loads(p.read_text(encoding='utf-8'));print(d['id'],d.get('ctime'),d.get('author'),html.unescape(re.sub('<[^>]+>','',d['content']))[:16000])
