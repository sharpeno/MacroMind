from pathlib import Path
import json,hashlib,urllib.request,re
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
for folder in [P.parent/"run_003_review_001",ROOT/"phase1/framework_review/v03_frozen_001"]:
 for n,h in read(folder/"manifest.json").items():assert sha(folder/n)==h
write("target_metadata.json",next(x for x in read(ROOT/"phase1/conflict_study/run_001/accepted_registry.json")["records"] if x["episode"]=="475"))
write("protocol.json",{"episode":"475","selected_at":datetime.now(timezone.utc).isoformat(),"framework_sha256":sha(ROOT/"phase1/framework_review/v03_frozen_001/framework.json"),"target_status":"UNREAD","application_checklist":["role/event/attitude distinct from inferred motive","interpret actions in context","separate price observation, mechanism and long-term extrapolation","state competing hypotheses, evidence, discriminating observations and update direction","consider execution chain and control constraints"],"design":"adaptive qualitative case after human feedback on472-474; not fixed-policy accuracy","cutoff":"2023-10-18 day-level per accepted title-date policy; exact video time unknown","leakage":"titles known; previous cases and historical knowledge exposed"})
url="https://www.cls.cn/detail/1487920"
raw=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=25).read()
(P/"sources/cls.html").write_bytes(raw)
data=json.loads(re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',raw.decode("utf-8"),re.S).group(1))["props"]["pageProps"]
write("sources/cls.json",data)
write("retrieval_log.json",{"url":url,"snapshot":"sources/cls.html","sha256":sha(P/"sources/cls.html"),"retrieved_at":datetime.now(timezone.utc).isoformat(),"unavailable":[{"url":"https://cn.nytimes.com/world/20231018/biden-israel-trip/","result":"web.open non-retryable failure; not read, excluded"}]})
print(json.dumps(data.get("articleDetail"),ensure_ascii=False,indent=2))