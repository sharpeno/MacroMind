from pathlib import Path
import json,hashlib,urllib.request,re
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
for folder in [P.parent/"run_001_review_001",ROOT/"phase1/framework_review/v03_frozen_001"]:
 for n,h in read(folder/"manifest.json").items():assert sha(folder/n)==h
write("prior_review_confirmation.json",{"recorded_at":datetime.now(timezone.utc).isoformat(),"source":"direct user message","verbatim":"确认完毕，无需修改，可以开始下一步了","approved_revision":"../run_001_review_001/R02_revision.json","approved_revision_sha256":sha(P.parent/"run_001_review_001/R02_revision.json"),"approved":"R02 revised comparison and proposed application checklist","limits":"Does not approve factual accuracy or amend frozen v0.3"})
m=next(x for x in read(ROOT/"phase1/conflict_study/run_001/accepted_registry.json")["records"] if x["episode"]=="473")
write("target_metadata.json",m)
write("protocol.json",{"episode":"473","selected_at":datetime.now(timezone.utc).isoformat(),"selection":"next reserved episode in frozen order","subtitle_status":"UNREAD","framework_sha256":sha(ROOT/"phase1/framework_review/v03_frozen_001/framework.json"),"application_revision":"Explicit speaker/role/event/public stance/motive checklist approved after case472","adaptive_evaluation":"472 has informed application process; not an untouched fixed-policy aggregate evaluation","cutoff":"2023-10-17 day-level upper bound; video exact time unknown","no_target_inference":"title known, subtitle not read before answer lock"})
results=[]
for name,url in [("people","https://world.people.com.cn/n1/2023/1017/c1002-40097009.html"),("cls","https://www.cls.cn/detail/1487337")]:
 try:
  raw=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=25).read()
  (P/"sources"/(name+".html")).write_bytes(raw)
  charset="utf-8"
  if name=="people":
   charset="gb18030" if re.search(br'charset\s*=\s*["\']?(?:gb2312|gbk)',raw,re.I) else "utf-8"
  text=raw.decode(charset,errors="replace")
  text=re.sub(r"<script\b.*?</script>","",text,flags=re.S|re.I) if name=="people" else text
  if name=="cls":
   match=re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',text,re.S)
   data=json.loads(match.group(1))["props"]["pageProps"]
   write("sources/cls.json",data)
   print(name,json.dumps(data.get("articleDetail"),ensure_ascii=False))
  else:
   plain=re.sub("<[^>]+>"," ",text)
   (P/"sources/people.txt").write_text(plain,encoding="utf-8")
   print(name,plain[:18000])
  results.append({"url":url,"file":"sources/"+name+".html","sha256":sha(P/"sources"/(name+".html")),"status":"retrieved","encoding":charset})
 except Exception as e:results.append({"url":url,"status":"failed","error":str(e)})
results.append({"url":"https://cn.nytimes.com/world/20231010/hamas-israel-war/","status":"web.open non-retryable failure; excluded, not read"})
write("retrieval_log.json",results)