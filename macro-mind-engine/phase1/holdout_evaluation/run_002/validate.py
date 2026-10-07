import json,hashlib,copy
from pathlib import Path
from datetime import datetime
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
lock=read(P/"answer_lock.json");ex=read(P/"exposure.json");comp=read(P/"comparison.json")
for n,h in lock["files"].items():assert sha(P/n)==h
assert datetime.fromisoformat(lock["locked_at"])<datetime.fromisoformat(ex["recorded_before_read_at"])
assert ex["answer_sha256"]==sha(P/"answer_before_subtitle.json")
checks.append("answer and input hashes unchanged; freeze before exposure verified")
for folder in [P.parent/"run_001",P.parent/"run_001_review_001",ROOT/"phase1/framework_review/v03_frozen_001"]:
 for n,h in read(folder/"manifest.json").items():assert sha(folder/n)==h
checks.append("prior comparison, review revision and v0.3 sealed files unchanged")
assert read(P/"prior_review_confirmation.json")["approved_revision_sha256"]==sha(P.parent/"run_001_review_001/R02_revision.json")
t=read(P/"target_transcript.json");assert len(t["cues"])==551 and [x["cue"] for x in t["cues"]]==list(range(551))
assert t["source_sha256"]==read(P/"target_metadata.json")["sha256"]
for card in comp["review_cards"]:
 for e in card["evidence"]:
  assert e["cues"]==[x for x in t["cues"] if e["from"]<=x["cue"]<=e["to"]]
checks.append("approval recorded; 551 cues complete; review quotes continuous and exact")
split=read(ROOT/"phase1/conflict_study/run_001/split_lock.json")
assert comp["remaining_unread_episodes"]==[x for x in split["reserved_evaluation"] if x not in ["472","473"]]
assert len(comp["remaining_unread_episodes"])==13
assert read(P/"review_packet.json")["comparison_sha256"]==sha(P/"comparison.json")
assert comp["human_comparison_approval"]=="PENDING"
checks.append("473 exposed; 13 reserved remain; new comparison hash bound, no human pass inferred")
for s in read(P/"retrieval_log.json"):
 if s["status"]=="retrieved":assert sha(P/s["file"])==s["sha256"]
assert read(P/"sources/cls.json")["articleDetail"]["ctime"]==1697527351
assert "2023年10月17日09:58" in (P/"sources/people.txt").read_text(encoding="utf-8")
checks.append("source snapshots and displayed dates checked; missing NYT input disclosed")
bad=copy.deepcopy(lock);bad["files"]["answer_before_subtitle.json"]="0"*64
assert any(sha(P/n)!=h for n,h in bad["files"].items())
e=comp["review_cards"][0]["evidence"][0]
assert e["cues"][:-1]!=[x for x in t["cues"] if e["from"]<=x["cue"]<=e["to"]]
checks.append("negative guards detect changed answer and truncated evidence")
qa=read(Path("G:/youhegaojian/review-ui-qa/holdout473/result.json"));assert qa["pass"]
result={"engineering_pass":True,"checks":checks,"ui":qa,"semantic_status":"partial transfer, material inference gaps; human review pending","factual_accuracy":"NOT_TESTED","forecast_accuracy":"NOT_SCORED","limits":["adaptive process after472; no pooled fixed-policy accuracy","unequal input sources","timestamps local, not independent attestation"]}
(P/"validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
progress=read(P/"progress.json");progress["status"]="WAITING_FOR_THREE_COMPARISON_REVIEWS";progress["completed"].append("integrity and browser interaction checks passed");progress["pending"]=["review R01/R02/R03 comparison","13 remaining cases not started","factual/outcome verification not performed"]
(P/"progress.json").write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))