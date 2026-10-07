from pathlib import Path
import urllib.request,hashlib,json,re
from datetime import datetime,timezone
p=Path("G:/youhegaojian/macro-mind-engine/phase1/holdout_evaluation/run_001")
root=p.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=root/"phase1/framework_review/v03_frozen_001"
for n,h in json.loads((f/"manifest.json").read_text(encoding="utf-8")).items():assert sha(f/n)==h
registry=json.loads((root/"phase1/conflict_study/run_001/accepted_registry.json").read_text(encoding="utf-8"))
r=next(x for x in registry["records"] if x["episode"]=="472")
(p/"target_metadata.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
(p/"protocol.json").write_text(json.dumps({"created_at":datetime.now(timezone.utc).isoformat(),"target_episode":"472","selection":"first reserved episode in frozen chronological split; selected before content read","framework_sha256":sha(f/"framework.json"),"target_subtitle_status":"UNREAD","date_precision":"day; cannot independently order video versus same-day articles","sources":["https://www.cls.cn/detail/1486755","https://www.cls.cn/detail/1487000","https://www.cls.cn/detail/1486209"],"cutoff_policy":"freeze retrieved news only; reject any source after 2023-10-17 and disclose same-day order unknown","evaluation":["six approved rules applied or explicitly limited","freeze answer before subtitle exposure","whole episode read after exposure recorded","compare overlapping themes with continuous context and opposing evidence","fidelity not truth; no percentage accuracy from one case"],"historical_knowledge":"not blinded; titles and metadata already exposed"},ensure_ascii=False,indent=2),encoding="utf-8")
for n in ["1486755","1487000","1486209"]:
 try:
  url="https://www.cls.cn/detail/"+n
  raw=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read()
  (p/"sources"/(n+".html")).write_bytes(raw)
  text=raw.decode("utf-8")
  match=re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',text,re.S)
  if match:
   data=json.loads(match.group(1))
   (p/"sources"/(n+".json")).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
   print(n,json.dumps(data,ensure_ascii=False)[:18000])
  else:print(n,"HTML",len(raw),re.sub("<[^>]+>"," ",text)[:10000])
 except Exception as e:print(n,"FAILED",str(e))