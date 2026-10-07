from pathlib import Path
import json,hashlib,urllib.request,re
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;ROOT=P.parents[2];read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
for folder in [P.parent/"run_002_review_001",ROOT/"phase1/framework_review/v03_frozen_001"]:
 for n,h in read(folder/"manifest.json").items():assert sha(folder/n)==h
m=next(x for x in read(ROOT/"phase1/conflict_study/run_001/accepted_registry.json")["records"] if x["episode"]=="474")
write("target_metadata.json",m)
write("protocol.json",{"selected_at":datetime.now(timezone.utc).isoformat(),"episode":"474","selection":"next chronological reserved episode; content not read","framework_sha256":sha(ROOT/"phase1/framework_review/v03_frozen_001/framework.json"),"application_notes_source":"../run_002_review_001/revisions.json","application_notes_sha256":sha(P.parent/"run_002_review_001/revisions.json"),"application_checklist":["speaker/role/event/public attitude before motive","context, external situation and participation jointly interpreted","observation, expectation mechanism and long-term inference separated","allow provisional hypotheses without converting them into established facts"],"cutoff":"2023-10-18 day-level, exact video/news ordering unknown","design":"adaptive qualitative evaluation after472/473 feedback, not fixed-policy accuracy","leakage":"title known, historical knowledge and prior search snippets on hospital event and summit cancellation already exposed","target_status":"UNREAD"})
url="https://world.people.com.cn/n1/2023/1018/c1002-40097726.html"
raw=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=25).read()
(P/"sources/people.html").write_bytes(raw)
charset="gb18030" if re.search(br'charset\s*=\s*["\']?(?:gb2312|gbk)',raw,re.I) else "utf-8"
text=raw.decode(charset);text=re.sub(r"<script\b.*?</script>","",text,flags=re.S|re.I)
plain=re.sub("<[^>]+>"," ",text)
(P/"sources/people.txt").write_text(plain,encoding="utf-8")
write("retrieval_log.json",{"url":url,"retrieved_at":datetime.now(timezone.utc).isoformat(),"snapshot":"sources/people.html","sha256":sha(P/"sources/people.html"),"encoding":charset,"initial_web_tool_result":"Unicode decoding error; fetched original public page and decoded declared character set"})
start=plain.find("2023年10月18日")
print(plain[start:start+18000])