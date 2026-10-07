import json,hashlib,copy
from pathlib import Path
from datetime import datetime
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[];lock=read(P/"answer_lock.json");ex=read(P/"exposure.json");comp=read(P/"comparison.json")
for n,h in lock["files"].items():assert sha(P/n)==h
assert datetime.fromisoformat(lock["locked_at"])<datetime.fromisoformat(ex["recorded_before_read_at"])
assert ex["answer_sha256"]==sha(P/"answer_before_subtitle.json")
checks.append("frozen answer and input unchanged; exposure after lock")
for folder in [P.parent/"run_003",P.parent/"run_003_review_001",ROOT/"phase1/framework_review/v03_frozen_001"]:
 for n,h in read(folder/"manifest.json").items():assert sha(folder/n)==h
checks.append("prior case, user revisions and frozen v0.3 unchanged")
t=read(P/"target_transcript.json");assert len(t["cues"])==655 and [x["cue"] for x in t["cues"]]==list(range(655))
assert t["source_sha256"]==read(P/"target_metadata.json")["sha256"]
for card in comp["review_cards"]:
 for e in card["evidence"]:
  assert e["cues"]==[x for x in t["cues"] if e["from"]<=x["cue"]<=e["to"]]
  assert (P/e["context_url"].split("#")[0]).exists()
checks.append("complete 655 cues, contiguous exact excerpts and context links")
split=read(ROOT/"phase1/conflict_study/run_001/split_lock.json")
assert comp["remaining_unread_episodes"]==[x for x in split["reserved_evaluation"] if x not in ["472","473","474","475"]]
assert len(comp["remaining_unread_episodes"])==11
assert read(P/"review_packet.json")["comparison_sha256"]==sha(P/"comparison.json")
assert comp["human_comparison_approval"]=="PENDING"
checks.append("475 exposed, 11 remain; review identity bound; approval not inferred")
src=read(P/"retrieval_log.json");assert sha(P/src["snapshot"])==src["sha256"]
assert datetime.fromtimestamp(read(P/"sources/cls.json")["articleDetail"]["ctime"]).strftime("%Y-%m-%d") <= "2023-10-18"
checks.append("news snapshot and date checked; missing travel source disclosed")
bad=copy.deepcopy(lock);bad["files"]["answer_before_subtitle.json"]="0"*64
assert any(sha(P/n)!=h for n,h in bad["files"].items())
e=comp["review_cards"][0]["evidence"][0];assert e["cues"][:-1]!=[x for x in t["cues"] if e["from"]<=x["cue"]<=e["to"]]
checks.append("negative guards detect changed answer and truncated quote")
answer=read(P/"answer_before_subtitle.json")
assert len(answer["hypotheses"])==3 and all(all(h[k] for k in ["basis","assumptions","discriminating_observations","update"]) for h in answer["hypotheses"])
checks.append("three hypotheses with evidence, observations and update criteria frozen before exposure")
qa=read(Path("G:/youhegaojian/review-ui-qa/holdout475/result.json"));assert qa["pass"]
result={"engineering_pass":True,"checks":checks,"ui":qa,"human_review":"PENDING","facts":"not independently tested; disputed attribution and technical claims not endorsed","forecasts":"NOT_SCORED","limits":["adaptive qualitative evaluation","prior historical knowledge; not strict blind test","local process timestamp, not third-party attestation"]}
(P/"validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
progress=read(P/"progress.json");progress["status"]="WAITING_FOR_THREE_COMPARISON_REVIEWS";progress["completed"].append("integrity and UI checks passed");progress["pending"]=["human review of three comparison items","11 remaining holdouts not started","independent factual/forecast evaluation not done"]
(P/"progress.json").write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))