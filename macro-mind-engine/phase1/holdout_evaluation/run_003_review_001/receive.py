import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;OLD=P.parent/"run_003";ROOT=P.parents[2]
src=Path("C:/Users/无语/Downloads/MacroMind_holdout474001_2026-10-07T12-09-46-936Z_3of3.json")
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
for folder in [OLD,ROOT/"phase1/framework_review/v03_frozen_001"]:
 for n,h in read(folder/"manifest.json").items():assert sha(folder/n)==h,(str(folder),n)
r=read(src);seed=read(OLD/"review_packet.json")
for k in ["schema","review_id","comparison_sha256"]:assert r[k]==seed[k],k
assert r["comparison_sha256"]==sha(OLD/"comparison.json")
assert len(r["records"])==3 and {x["id"] for x in r["records"]}==set(seed["ids"])
for x in r["records"]:
 assert x["decision"]=="accept" and isinstance(x["notes"],str)
assert r["completed"]==3 and r["framework_change"]=="NONE"
(P/src.name).write_bytes(src.read_bytes());assert sha(P/src.name)==sha(src)
comparison=read(OLD/"comparison.json")
assert len(comparison["remaining_unread_episodes"])==12
write("receipt.json",{"recorded_at":datetime.now(timezone.utc).isoformat(),"submission":src.name,"submission_sha256":sha(src),"review_id":r["review_id"],"comparison_sha256":r["comparison_sha256"],"accepted":["R01","R02","R03"],"revision_requested":[],"scope":"human approval of three comparison descriptions; not approval of original answer completeness, factual claims or forecast accuracy","framework_change":"NONE"})
write("progress.json",{"status":"THREE_COMPARISON_ITEMS_HUMAN_APPROVED","completed":["submission schema, identity, IDs and source hash verified","original review archived byte-for-byte","R01/R02/R03 accepted","previous sealed answer, comparison and v0.3 preserved"],"pending":["prepare explicit scenario/discriminating-observation checklist for next case","475 and remaining 12 reserved episodes not started","independent factual and forecast evaluation not performed"],"remaining_unread_episodes":comparison["remaining_unread_episodes"],"original_answer_result":comparison["conclusion"],"framework_change":"NONE"})
report="""# 第474期审阅完成

已接收 MacroMind_holdout474001_2026-10-07T12-09-46-936Z_3of3.json。
版本、对照内容哈希及三个编号匹配，R01、R02、R03均为accept，没有修改意见。原文件按原名逐字节归档。

## 已确认的对照
- R01：原答案没有充分展开两种情景及用于区分它们的后续观察。
- R02：需要保留公开话语的策略用途，并区分不同命题的确信程度。
- R03：原答案遗漏了内部责任分散、难以纠偏与持续升级的机制。

通过的是这三项对照归纳的人工审阅，不意味着原分析已完整复现博主，也不证明博主的责任、武器技术、概率或预测判断正确。原分析仍保留“部分迁移、存在关键遗漏”的结果。

## 保存与验证
原run_003及v0.3冻结目录哈希核对通过；文件schema、review_id、comparison_sha256、三个唯一编号、decision、notes和完成数核验通过；归档字节与提交文件一致。
原答案、对照页及冻结规则未改。receipt.json记录认可范围，progress.json记录续接状态，validation.json及stdout/stderr保留本次检查结果。没有页面改动，不重复浏览器测试。

## 下一步
在第475期分析协议中明确写出“候选解释—各自依据—可区分的后续观察—更新方向”，并继续记录话语的策略用途、责任链和控制能力。它们是后续运用要点，尚未自动改写通用框架。
第475期及其余共12份保留未读。下一例仍须先封存新闻输入和答案，再读取对应字幕；独立事实与预测结果验收尚未进行。
"""
(P/"REPORT.md").write_text(report,encoding="utf-8")
result={"pass":True,"checks":["sealed run_003 and v0.3 hashes match","review schema, version hash and three unique IDs match","all three actual decisions accept","archive bytes identical"],"human_approval":"three comparison descriptions accepted","not_claimed":["original answer fully matches analyst","factual or forecast correctness","framework update"]}
write("validation.json",result);print(json.dumps(result,ensure_ascii=False,indent=2))