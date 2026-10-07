import json,hashlib,copy
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;ROOT=P.parents[2];D=P.parent/"v03_draft_002"
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):
 (P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
checks=[]
for folder in [D,D.parent/"v03_draft_001",ROOT/"phase1/conflict_study/run_001",ROOT/"phase1/conflict_study/run_002"]:
 for name,digest in read(folder/"manifest.json").items():
  assert sha(folder/name)==digest,(str(folder),name)
 checks.append(str(folder.relative_to(ROOT))+": sealed hashes match")
draft=read(D/"framework_draft.json");packet=read(D/"review_packet.json")
assert packet["draft_sha256"]==sha(D/"framework_draft.json")
assert read(D/"validation.json")["pass"] is True
assert len(draft["review_cards"])==6
assert {c["id"] for c in draft["review_cards"]}=={"C01","C02","C03","C04","C05","C06"}
checks.append("reviewed draft identity, six unique cards, prior engineering validation verified")
baseline=ROOT/"phase1/method_application/run_002/framework.json"
assert sha(baseline)==draft["parent"]["sha256"]
now=datetime.now(timezone.utc).isoformat()
receipt={"schema":"macromind.conversation-review-receipt.v1","recorded_at":now,
 "source":"direct_user_message_in_current_conversation","verbatim":"复审通过，没有需要修改的部分，引用的原话上下文也很合适",
 "reviewed_draft":"../v03_draft_002/framework_draft.json","reviewed_draft_sha256":sha(D/"framework_draft.json"),
 "interpretation":{"delta_rule_and_boundary_approved":["C03","C04"],"prior_approvals_preserved":["C01","C02","C05","C06"],"displayed_quote_contexts":"APPROVED","no_changes_requested":True},
 "limits":["Human approval of representation and displayed context, not independent factual accuracy or forecast performance","Conversation receipt, not a fabricated browser JSON export"]}
write("approval_receipt.json",receipt)
f=copy.deepcopy(draft)
f.update(id="9527-methods-v0.3",state="FROZEN_HUMAN_REVIEWED_RESEARCH_CANDIDATE",created_at=now,
 parent_id=read(baseline)["id"],parent_sha256=sha(baseline),
 selection_plan="Next: staged evaluation using the existing conflict_001 15-episode holdout split; freeze each case answer before reading its target analyst transcript.",
 revision_basis="phase1/framework_review/v03_draft_002/framework_draft.json",revision_basis_sha256=sha(D/"framework_draft.json"),
 evaluation_boundary="Development episodes have been read; 15 reserved transcripts remain unread. Historical knowledge is not blinded. Fidelity, factual accuracy and forecast performance must be evaluated separately.",
 activation_policy="Frozen research candidate for subsequent evaluation. Existing application runs and v0.2 baseline remain unchanged; no global runner activation performed.")
f["lineage_note"]="The reviewed draft retained some v0.2 historical metadata (v0.1 parent and ECB selection plan); freeze corrects provenance/planning only, not approved rule text. Old draft remains unchanged."
f["review_revision"]={"reviewed_draft_sha256":sha(D/"framework_draft.json"),"approved_rule_ids":[c["id"] for c in f["review_cards"]],"pending_rule_ids":[],"approval_receipt_sha256":sha(P/"approval_receipt.json")}
for c in f["review_cards"]:
 c["prior_review_receipt"]=c.pop("review_receipt")
 c["attribution"]["approval"]="HUMAN_APPROVED_RULE_AND_BOUNDARY"
 c["context_approval"]="HUMAN_APPROVED_DISPLAYED_CONTEXT"
 c["approval_receipt"]="approval_receipt.json"
 for e in c["evidence"]:e["context_url"]="../v03_draft_002/"+e["context_url"]
for m in f["methods"]:
 m["status"]="FROZEN_RESEARCH_BASELINE_WITH_REVIEWED_EXTENSIONS"
 m["baseline_semantic_approval"]=m.pop("semantic_approval",None)
 m["semantic_approval"]="BASELINE_APPROVAL_NOT_EXPANDED_BY_THIS_REVIEW"
 m["v03_approved_extensions"]=m.pop("v03_proposed_extensions")
f["operational_use"]="Use retained baseline methods together with the full approved review_cards referenced by v03_approved_extensions. Review approval does not retroactively approve every baseline method."
write("framework.json",f)
for c in f["review_cards"]:
 original=next(x for x in draft["review_cards"] if x["id"]==c["id"])
 for key in ["title","rule","inputs","steps","default","update","example","boundary","target"]:
  assert c[key]==original[key],(c["id"],key)
 for e,o in zip(c["evidence"],original["evidence"]):
  assert e["cues"]==o["cues"]
  assert (P/e["context_url"].split("#")[0]).is_file()
checks.append("all six approved rule texts and quote cues unchanged; context links resolve")
for m in f["methods"]:
 assert m["v03_approved_extensions"]==[c["id"] for c in f["review_cards"] if c["target"]==m["id"]]
checks.append("approved extensions resolve to correct methods; inherited method approval not overstated")
assert sha(baseline)==draft["parent"]["sha256"]
checks.append("v0.2 baseline unchanged; holdout transcript content not accessed")
write("framework_lock.json",{"framework_id":f["id"],"sha256":sha(P/"framework.json"),"reviewed_draft_sha256":sha(D/"framework_draft.json"),"approval_receipt_sha256":sha(P/"approval_receipt.json"),"scope":"research candidate frozen; no global application activation"})
write("validation.json",{"pass":True,"checks":checks,"limits":["No browser code changes; prior UI tests verified by sealed manifest, not rerun","No factual or predictive evaluation","No holdout evaluation started"]})
write("progress.json",{"status":"V03_FROZEN_READY_FOR_HOLDOUT_PREPARATION","completed":["conversation approval archived","all six rule cards approved","displayed contexts approved","v0.3 candidate frozen","hash, text, context link and method reference checks passed"],"pending":["prepare staged holdout case protocol and inputs","freeze each answer before target transcript exposure","evaluate fidelity separately from factual and forecast accuracy"],"global_runner_activation":"NOT_PERFORMED","holdout_transcripts":"UNREAD"})
report="""# v0.3 审阅完成并封存

用户在当前对话明确确认：“复审通过，没有需要修改的部分，引用的原话上下文也很合适”。

C03、C04 的方法与边界复审通过；C01、C02、C05、C06 继承第一轮认可；本轮展示的原话上下文获认可。直接对话确认是本次审阅依据，不要求重复填写浏览器，也未伪造浏览器导出文件。

## 封存内容
framework.json 为 9527-methods-v0.3 研究候选，framework_lock.json 绑定内容哈希，approval_receipt.json 保存原话和对应草案哈希。六项规则正文与证据文字保持不变，完整上下文继续链接到封存的第二版审阅页。

基线方法与六项扩展共同构成候选；本次认可没有扩展为对所有继承方法的重新人工验收。修正了原草案沿用的历史父版本、欧洲央行案例计划等元数据，准确指向 v0.2 与巴以留出检验。旧草案、旧审阅和旧应用均未重写。

## 验证
validation.json 与 validation.stdout.log 保存本次真实结果；核对四个封存目录的哈希、草案身份、六项正文及引文不变、上下文链接、方法引用、v0.2未变。无页面代码改动，未重复浏览器测试；此前测试文件的完整性已核对。
封存表示可作为后续检验的固定规则，不等于事实或预测准确性已经验收。没有切换全局运行器，也未读取留出字幕。

## 下一步
按既有15份留出材料划分，先确定首个案例的信息截止时间、新闻输入和评价口径；先保存新规则的分析答案，再打开对应博主字幕比较。分别记录方法运用、观点忠实度、事实核验、预测结果，不因历史知识声称严格盲测。修改规则时另建版本，不回填本版。

## 复现
本目录 finalize.py 用工程 .venv/Scripts/python.exe -X utf8 运行；stdout/stderr 已保存在本目录。该脚本会重建带时间的封存产物，封存后勿重跑；只读核验应按 manifest.json 重算哈希。
"""
(P/"REPORT.md").write_text(report,encoding="utf-8")
print(json.dumps({"pass":True,"framework_id":f["id"],"sha256":sha(P/"framework.json"),"checks":checks},ensure_ascii=False,indent=2))