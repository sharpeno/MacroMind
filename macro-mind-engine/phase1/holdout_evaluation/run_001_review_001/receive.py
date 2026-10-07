import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;OLD=P.parent/"run_001"
src=Path("C:/Users/无语/Downloads/MacroMind_holdout472001_2026-10-06T12-16-56-716Z_3of3.json")
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
for n,h in read(OLD/"manifest.json").items():assert sha(OLD/n)==h,(n,"changed")
r=read(src);seed=read(OLD/"review_packet.json")
for k in ["schema","review_id","comparison_sha256"]:assert r[k]==seed[k],k
assert r["comparison_sha256"]==sha(OLD/"comparison.json")
assert len(r["records"])==3 and {x["id"] for x in r["records"]}==set(seed["ids"])
for x in r["records"]:
 assert x["decision"] in ["accept","revise","uncertain"]
 assert isinstance(x["notes"],str)
 if x["decision"]=="revise":assert x["notes"].strip()
assert {x["id"]:x["decision"] for x in r["records"]}=={"R01":"accept","R02":"revise","R03":"accept"}
(P/src.name).write_bytes(src.read_bytes())
assert sha(P/src.name)==sha(src)
revision={
"id":"R02","status":"REVISED_FROM_USER_FEEDBACK_NOT_YET_REAPPROVED",
"original_comparison_sha256":sha(OLD/"comparison.json"),
"submission_sha256":sha(src),"user_note":r["records"][1]["notes"],
"title":"把讲话者身份、所代表的立场、事件态度和讲话动机分开",
"layers":[
{"layer":"可观察的公开表态","text":"据本轮新闻报道，美国财政部长耶伦公开表示美国有能力同时支持以色列和乌克兰。被记录的是谁在什么职位上作了什么表态；不是美国实际双线能力已经得到证明。","evidence":"../run_001/sources/1486755.json"},
{"layer":"讲话者及其代表身份","text":"讲话者是耶伦，角色是美国财政部长。应将这番话作为美国政府财政部门负责人在职责范围内传达的公开立场，而非普通个人随口判断；不能自动等同于美国所有机构、派别一致，或正式参战决定。"},
{"layer":"面向的事件与表达的态度","text":"针对同时支持以色列和乌克兰这一双线压力问题，公开态度是宣示有能力维持支持。这一姿态本身就是分析输入，不因尚未落实成行动就忽略；“军事支持”与“美军直接双线作战”仍要区分。"},
{"layer":"博主对讲话动机的推断","text":"博主先从财长的角色约束判断她在这种场合不能公开示弱，否则可能鼓励对手挑战；再从此时专门强调能力，进一步解读为壮胆或心虚。保留这两步及其确信程度，但后一步不是讲话事实本身。","evidence":"../run_001/CONTEXT.html#cue-237","cue_range":[237,289]}
],
"corrected_comparison":"原答案记录了耶伦的职位、支持声明与立法约束，也区分能力、意愿、行动，但没有把讲话者代表身份→针对的事件与公开态度→角色约束→讲话动机作为一条明确推理链。因此应记为结构化处理和动机推导不充分，而非完全没有识别身份或公开表态。",
"application_proposal":"后续分析先登记：讲话者、职位/代表范围、所针对事件、表态内容及公开态度，再单独列角色约束、可能动机、根据与替代解释。公开表态可直接成为基础判断输入；动机和实际能力分别保留验证边界。",
"scope":"本例对照修订与后续运用建议；未改变v0.3，也未回写阅读字幕前答案；不将单例建议自动升级为获批通用规则。"}
write("R02_revision.json",revision)
write("receipt.json",{"recorded_at":datetime.now(timezone.utc).isoformat(),"source_file":src.name,"sha256":sha(src),"accepted":["R01","R03"],"revision_requested":["R02"],"revised":["R02"],"all_approved":False})
write("progress.json",{"status":"R02_REVISED_PENDING_CONFIRMATION","completed":["submission identity and sealed files verified","original bytes archived","R01/R03 approval recorded","R02 expanded into role, event, attitude and motive layers"],"pending":["confirm revised R02 comparison","decide whether application checklist needs a separate tested revision","14 remaining holdouts not started"],"framework_change":"NONE","pre_exposure_answer_change":"NONE"})
report="""# 第472期审阅接收与R02修订

审阅文件与当前对照哈希匹配，原文件逐字节归档。R01、R03认可；R02要求补充讲话者所代表的身份、事件态度和讲话动机。3/3表示填写完成，不表示全部认可。

## R02修订表述
这段材料应按以下顺序分析：
1. **谁说了什么**：据所收集新闻，美国财长耶伦作出可以同时支持以色列、乌克兰的公开表态。
2. **代表什么身份**：她以美国财政部长身份，在职责范围内传达政府财政部门负责人的公开立场；不同于私人评论。
3. **针对什么事件、表达什么态度**：面对两地冲突带来的支持压力，宣示有能力继续支持。该姿态本身就是分析材料；不能因为还没成为实际措施就略去。
4. **角色如何约束表达**：博主认为该身份在这种场合不能示弱，否则可能鼓励对手挑战。
5. **为何此时这样说**：博主进一步将强调能力解读为壮胆、心虚。保留这项动机判断，并与公开表态事实分开。

原封存答案已经写到耶伦的职位和声明，因此不应说它完全没有识别身份；准确的差距是，没有把身份、事件态度、角色约束与讲话动机串成明确推理链。新闻中的“军事支持”也不自动等于美国军队直接进行两场战争。

## 后续运用建议
对每次关键公开讲话，先登记讲话者、职务/代表范围、事件、表态内容和态度；再列角色约束、动机解释、依据及其他可能解释。公开态度可用于形成基础判断，不要求证明真实动机后才开始推演。

这是按你的意见完成的对照修订，尚未将它标为再次认可或获批通用规则。原v0.3与阅读字幕前答案均保留。原连续证据为第472期cue237—289，可从[完整上下文](../run_001/CONTEXT.html#cue-237)查看。

## 验证与进度
原run_001封存文件逐项哈希不变；审阅schema、编号、版本哈希和意见值匹配；归档字节一致。原始输出见validation.stdout.log和validation.stderr.log，结构结果见validation.json。
R01/R03完成，R02修订待确认；其余14份字幕未读。此轮未运行新的事实/预测验证，也未改页面代码，不重复浏览器测试。
"""
(P/"REPORT.md").write_text(report,encoding="utf-8")
for n,h in read(OLD/"manifest.json").items():assert sha(OLD/n)==h
result={"pass":True,"checks":["30 sealed run_001 files unchanged","review identity and all three records verified","archive byte equality","two approvals and one revision accurately distinguished","original answer and framework untouched"],"semantic_approval":"R01/R03 only; revised R02 pending"}
write("validation.json",result)
print(json.dumps(result,ensure_ascii=False,indent=2))