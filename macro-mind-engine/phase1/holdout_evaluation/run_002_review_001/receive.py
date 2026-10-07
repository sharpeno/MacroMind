import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;OLD=P.parent/"run_002"
src=Path("C:/Users/无语/Downloads/MacroMind_holdout473001_2026-10-06T12-45-53-211Z_3of3.json")
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
manifest=read(OLD/"manifest.json")
for n,h in manifest.items():assert sha(OLD/n)==h,n
r=read(src);seed=read(OLD/"review_packet.json")
for k in ["schema","review_id","comparison_sha256"]:assert r[k]==seed[k]
assert r["comparison_sha256"]==sha(OLD/"comparison.json")
assert len(r["records"])==3 and {x["id"] for x in r["records"]}==set(seed["ids"])
for x in r["records"]:
 assert x["decision"] in ["accept","revise","uncertain"] and isinstance(x["notes"],str)
 if x["decision"]=="revise":assert x["notes"].strip()
assert {x["id"]:x["decision"] for x in r["records"]}=={"R01":"revise","R02":"revise","R03":"accept"}
(P/src.name).write_bytes(src.read_bytes());assert sha(P/src.name)==sha(src)
cues=read(OLD/"target_transcript.json")["cues"]
revisions=[]
for x in r["records"][:2]:
 text=x["notes"]
 marker="证据边界建议写成：" if x["id"]=="R01" else "证据边界可以写成："
 main,boundary=text.split(marker,1)
 main=main.removeprefix("建议将 R01 改为：\n").strip()
 title,body=main.split("\n",1)
 ranges=[(11,82)] if x["id"]=="R01" else [(83,113),(391,470)]
 revisions.append({"id":x["id"],"status":"USER_SUPPLIED_REPLACEMENT_APPLIED","title":title,"finding":body.strip(),"boundary":boundary.strip(),"authorship":"user-provided replacement, verbatim except heading separation","review_outcome_for_original":"revise","subsequent_review":"NOT_CLAIMED","evidence":[{"from":lo,"to":hi,"cues":[c for c in cues if lo<=c["cue"]<=hi],"context_url":"../run_002/CONTEXT.html#cue-"+str(lo)} for lo,hi in ranges]})
write("revisions.json",{"source_sha256":sha(src),"comparison_sha256":sha(OLD/"comparison.json"),"revisions":revisions,"unchanged_approved":["R03"],"scope":"revises comparison only; no framework or pre-exposure answer rewrite","evidence_note":"R02 second range expanded 391—442 to 391—470 to include the ensuing long-term US-order discussion; this expansion is assistant selection, not an extra human approval"})
write("receipt.json",{"recorded_at":datetime.now(timezone.utc).isoformat(),"submission":src.name,"sha256":sha(src),"accepted":["R03"],"revision_requested":["R01","R02"],"user_replacement_applied":["R01","R02"],"all_original_items_approved":False})
report="# 第473期审阅接收与两项修订\n\nR03认可；R01、R02要求修订。原文件版本、对照哈希和三个编号均已核验，原文件逐字节归档。3/3是填写完成，不是原对照全部通过。\n\n以下直接采用用户提供的替换文本，未另行改写核心表述。原对照保留，修订独立记录；未声称又经过一轮人工复审。\n\n"
for x in revisions:
 report+="## "+x["title"]+"\n\n"+x["finding"]+"\n\n**证据边界**\n\n"+x["boundary"]+"\n\n"
report+="""## 连续证据
R01保留第473期cue11—82。R02保留cue83—113，第二段由391—442扩展为391—470，以覆盖随后对长期秩序与利益格局的解释；逐条原文在revisions.json。扩展区间是助手的证据整理，不额外推定用户已审阅。
[查看第473期完整字幕](../run_002/CONTEXT.html#cue-391)。

## 对下一步运用的影响
- 行动信号应放在活动性质、外部局势、身份关系与参与方式中理解；不从单个姿态或接待级别跳到全面政治认可。
- 把事件前后的价格表现、作者的机制解释、远期战略推演分层记录；既可形成基础判断，又保留其他驱动因素与更新条件。
以上是从用户修订整理的运用建议，未自动写入冻结v0.3，也不把它们作为另一次通用规则验收。

## 验证和续接
原run_002封存文件未改，原答案、规则和此前审阅保持不变；用户替换正文与边界逐字匹配；连续引文与已读字幕逐条一致。validation.json及原始stdout/stderr记录结果。本轮未改页面代码，不重跑浏览器测试。
已完成：归档、R03认可记录、R01/R02按用户原文替换、证据扩展及完整性检查。
待完成：将经修订的运用要点明确纳入后续案例协议；第474期及其余共13份未读材料尚未启动；独立事实和预测检验未执行。原版TRACE.html是历史版本，最新修订以本文件及revisions.json为准。
"""
(P/"REPORT.md").write_text(report,encoding="utf-8")
for x,source in zip(revisions,r["records"]):
 assert x["finding"] in source["notes"] and x["boundary"] in source["notes"]
 for e in x["evidence"]:
  assert len(e["cues"])==e["to"]-e["from"]+1
  assert e["cues"]==[c for c in cues if e["from"]<=c["cue"]<=e["to"]]
for n,h in manifest.items():assert sha(OLD/n)==h
write("progress.json",{"status":"USER_REPLACEMENTS_APPLIED","completed":["review archived and version verified","R03 accepted","R01/R02 exact user replacement applied","R02 long-term explanation context expanded","integrity checks passed"],"pending":["carry application notes into next case protocol","13 remaining holdouts not started","independent fact and forecast testing not performed"],"extra_human_approval":"NOT_INFERRED","framework_change":"NONE"})
result={"pass":True,"checks":["source version and IDs verified","archive byte equality","all prior sealed files unchanged","replacement body and boundaries match user text","continuous quote ranges match already-read transcript"],"semantic_status":"R03 accepted; R01/R02 original requires revision, user replacements applied; no separate reapproval claimed"}
write("validation.json",result);print(json.dumps(result,ensure_ascii=False,indent=2))