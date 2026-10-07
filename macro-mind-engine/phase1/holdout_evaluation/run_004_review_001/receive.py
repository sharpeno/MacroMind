import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;OLD=P.parent/"run_004";ROOT=P.parents[2]
src=Path("C:/Users/无语/Downloads/MacroMind_holdout475001_2026-10-07T12-33-10-308Z_3of3.json")
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
for folder in [OLD,ROOT/"phase1/framework_review/v03_frozen_001"]:
 for n,h in read(folder/"manifest.json").items():assert sha(folder/n)==h,(str(folder),n)
r=read(src);seed=read(OLD/"review_packet.json")
for k in ["schema","review_id","comparison_sha256"]:assert r[k]==seed[k],k
assert r["comparison_sha256"]==sha(OLD/"comparison.json")
assert len(r["records"])==3 and {x["id"] for x in r["records"]}==set(seed["ids"])
assert {x["id"]:x["decision"] for x in r["records"]}=={"R01":"accept","R02":"accept","R03":"revise"}
assert all(isinstance(x["notes"],str) and x["notes"].strip() for x in r["records"])
assert r["completed"]==3
(P/src.name).write_bytes(src.read_bytes());assert sha(P/src.name)==sha(src)
cues=read(OLD/"target_transcript.json")["cues"]
notes={x["id"]:x["notes"] for x in r["records"]}
main,boundary=notes["R01"].split("证据边界建议写成：",1)
title,body=main.strip().split("\n",1)
items=[
{"id":"R01","submitted_decision":"accept","status":"ACCEPTED_WITH_USER_CLARIFICATION_APPLIED","title":title,"finding":body.strip(),"boundary":boundary.strip(),"authorship":"user replacement verbatim apart from separating headings","ranges":[[367,431],[496,532]]},
{"id":"R02","submitted_decision":"accept","status":"ACCEPTED_WITH_USER_BOUNDARY_APPLIED","title":"保留由消费结果反推机制，不补造具体资金渠道","finding":notes["R02"],"boundary":"原字幕中作者使用“证实”的强措辞仍原样保留；对照解释按用户意见明确：这是作者将数据视为支持其判断，不是系统确认机制已经证实。具体渠道、机制和替代解释需后续证据，不自行填补。","authorship":"finding is user text; boundary is assistant clarification of transcript versus evidence status","ranges":[[432,495]]},
{"id":"R03","submitted_decision":"revise","status":"USER_REVISION_APPLIED_NO_EXTRA_REAPPROVAL_CLAIMED","title":"按国内主要矛盾排序，再判断美以不同的行动时机","finding":notes["R03"],"boundary":"忠实记录作者的判断排序与强确信；国内通胀是首要矛盾及其决定地区介入意愿，属于作者的分析解释，未据此判为已验证结果。“不被绑上战车”也不自动等于停止所有军援。","authorship":"finding is user text; title/boundary organized by assistant","ranges":[[367,431],[496,648]]}
]
for x in items:
 x["user_note"]=notes[x["id"]]
 x["evidence"]=[{"from":lo,"to":hi,"cues":[c for c in cues if lo<=c["cue"]<=hi],"context_url":"../run_004/CONTEXT.html#cue-"+str(lo)} for lo,hi in x.pop("ranges")]
write("revisions.json",{"comparison_sha256":sha(OLD/"comparison.json"),"submission_sha256":sha(src),"items":items,"framework_change":"NONE","scope":"comparison and application notes; no rewrite of frozen original answer"})
write("receipt.json",{"recorded_at":datetime.now(timezone.utc).isoformat(),"file":src.name,"sha256":sha(src),"accepted_with_notes":["R01","R02"],"revision_requested":["R03"],"notes_applied":["R01","R02","R03"],"all_original_items_approved":False})
report="""# 第475期审阅接收与补充落实

R01、R02选择accept，但均有实质补充；R03选择revise。不能因为前两项认可就忽略意见，也不能因3/3填完而写成原对照全部通过。
原文件版本、哈希与编号核验匹配，已按原名逐字节归档。以下落实用户意见，原对照及阅读字幕前答案不覆盖。

"""
for x in items:
 report+="## "+x["id"]+" · "+x["title"]+"\n\n"+x["finding"]+"\n\n**证据边界**\n\n"+x["boundary"]+"\n\n"
report+="""## 对分析流程的具体影响
1. 先识别作者设定的政策目标，再判断现有手段是否仍在起作用，最后判断是否需要追加手段；不能只靠“数据强”机械推出再加息。原话还保留油价暴涨这一可能触发条件。
2. 可以根据结果提出潜在机制，但要写明机制尚未识别或验证，不能补造资金渠道。作者确信程度与系统验证状态分别记录。
3. 多情景推演之后仍需表达作者认为哪个矛盾优先、哪个判断更占主导；不能以证据边界为由，把作者的明确倾向稀释成等权并列可能。竞争解释用于核验，不替换忠实归纳。

这些是按本次审阅整理的后续运用要点，未自动写入冻结v0.3。R01正文及边界采用用户原文，R02/R03正文采用用户原文；辅助标题、证据边界说明及选段为助手整理，不冒称另经一轮人工认可。

## 证据和验证
连续引文在revisions.json，链接到封存的第475期CONTEXT.html。原字幕不改字，特别保留作者使用“证实”及强断言的实际措辞，同时不把它当成独立事实验收。
原run_004、v0.3封存文件逐项哈希不变；提交schema、review_id、comparison_sha256、唯一编号和选项匹配；归档字节一致；补充意见及引文逐条核对。validation.json及stdout/stderr保存结果。没有页面代码变更，不重复浏览器测试。

## 当前进度
已完成：归档、认可与修改意见分别记录、三项文字补充落实、证据整理与完整性检查。
待完成：下一例协议落实政策目标/手段、机制未知与主要矛盾排序；第476期及其余共11份仍未读；独立事实与预测检验未执行。
原TRACE.html是历史对照页，最新补充以本记录及revisions.json为准。用户给出的具体文本已落实，不要求重复填写原页面。原R03不标通过，也不伪造修订后的复审记录。
"""
(P/"REPORT.md").write_text(report,encoding="utf-8")
assert items[0]["finding"] in notes["R01"] and items[0]["boundary"] in notes["R01"]
assert items[1]["finding"]==notes["R02"] and items[2]["finding"]==notes["R03"]
for item in items:
 for e in item["evidence"]:
  assert len(e["cues"])==e["to"]-e["from"]+1
  assert e["cues"]==[c for c in cues if e["from"]<=c["cue"]<=e["to"]]
  assert (P/e["context_url"].split("#")[0]).exists()
write("progress.json",{"status":"USER_CLARIFICATIONS_AND_REVISION_APPLIED","completed":["review identity verified and raw file archived","R01/R02 accept-with-notes recorded","R03 revision applied from user text","original transcript wording preserved alongside evidence limits","integrity and continuity checks passed"],"pending":["apply goal/instrument/mechanism/priority checklist in next case","11 unread episodes starting476 not yet started","independent fact/forecast validation not done"],"extra_human_approval":"NOT_CLAIMED","framework_change":"NONE"})
result={"pass":True,"checks":["review identity and three unique decisions match","accepted notes retained, not discarded","archive bytes identical","old comparison and v0.3 sealed hashes match","user body text matches and quotes continuous"],"human_status":"R01/R02 accepted with notes, R03 original revise; all supplied text applied","fact_forecast_validation":"NOT_PERFORMED"}
write("validation.json",result);print(json.dumps(result,ensure_ascii=False,indent=2))