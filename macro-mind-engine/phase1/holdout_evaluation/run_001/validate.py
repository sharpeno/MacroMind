import json,hashlib,copy
from pathlib import Path
from datetime import datetime
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
lock=read(P/"answer_lock.json")
for n,h in lock["files"].items():assert sha(P/n)==h
checks.append("locked protocol, news and pre-exposure answer unchanged")
ex=read(P/"exposure.json")
assert datetime.fromisoformat(lock["locked_at"])<datetime.fromisoformat(ex["recorded_before_read_at"])
assert ex["answer_sha256"]==sha(P/"answer_before_subtitle.json")
assert ex["answer_lock_sha256"]==sha(P/"answer_lock.json")
checks.append("answer freeze precedes recorded transcript exposure; hashes bound")
for folder in [ROOT/"phase1/framework_review/v03_frozen_001",ROOT/"phase1/framework_review/v03_draft_002",ROOT/"phase1/conflict_study/run_001",ROOT/"phase1/conflict_study/run_002"]:
 for n,h in read(folder/"manifest.json").items():assert sha(folder/n)==h
checks.append("framework and earlier sealed studies unmodified")
comp=read(P/"comparison.json");t=read(P/"target_transcript.json");meta=read(P/"target_metadata.json")
assert t["source_sha256"]==meta["sha256"] and len(t["cues"])==643
assert [x["cue"] for x in t["cues"]]==list(range(643))
assert {x["id"] for x in comp["rows"]}=={"C01","C02","C03","C04","C05","C06"}
for c in comp["review_cards"]:
 for e in c["evidence"]:
  assert e["cues"]==[x for x in t["cues"] if e["from"]<=x["cue"]<=e["to"]]
  assert (P/e["context_url"].split("#")[0]).exists()
checks.append("643 indexed cues; six-rule coverage; continuous review excerpts match source transcript")
split=read(ROOT/"phase1/conflict_study/run_001/split_lock.json")
assert comp["remaining_unread_episodes"]==[x for x in split["reserved_evaluation"] if x!="472"]
assert comp["human_comparison_approval"]=="PENDING" and comp["forecast_accuracy"]=="NOT_SCORED"
checks.append("472 marked exposed, 14 remain unread; no invented human pass or accuracy")
assert read(P/"review_packet.json")["comparison_sha256"]==sha(P/"comparison.json")
news=read(P/"news_input.json")
for source in news["sources"]:
 if "ctime_utc" in source:
  assert source["ctime_utc"][:10]<="2023-10-17"
  assert sha(P/source["retrieved_snapshot"])==source["sha256"]
assert news["unavailable"] and news["leakage"]
checks.append("source snapshot hashes/date bounds valid; missing source and contamination disclosed")
# Negative guards operate on in-memory copies; do not corrupt frozen files.
bad=copy.deepcopy(lock);bad["files"]["answer_before_subtitle.json"]="0"*64
assert any(sha(P/n)!=h for n,h in bad["files"].items())
bad_e=copy.deepcopy(comp["review_cards"][0]["evidence"][0]);bad_e["cues"]=bad_e["cues"][:-1]
assert bad_e["cues"]!=[x for x in t["cues"] if bad_e["from"]<=x["cue"]<=bad_e["to"]]
checks.append("negative checks: tampered answer digest and truncated quote rejected")
qa=read(Path("G:/youhegaojian/review-ui-qa/holdout472/result.json"))
assert qa["pass"]
result={"engineering_pass":True,"checks":checks,"ui":qa,"semantic_result":comp["conclusion"],"human_review":"PENDING","limitations":["process timestamps are local records, not independent attestation","historical source contamination prevents clean temporal backtest","one case with unequal source access; no general accuracy conclusion"]}
(P/"validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
progress=read(P/"progress.json");progress["status"]="WAITING_FOR_THREE_COMPARISON_REVIEWS";progress["completed"]+=["integrity checks and two negative checks passed","desktop/mobile interaction QA passed and visually inspected"];progress["pending"]=["human comparison review R01/R02/R03","separate factual/outcome evaluation not performed","14 subsequent holdouts not started"]
(P/"progress.json").write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))