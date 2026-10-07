import json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lock=read(P/"answer_lock.json")
for n,h in lock["files"].items():assert sha(P/n)==h
meta=read(P/"target_metadata.json")
exposure={"episode":"472","recorded_before_read_at":datetime.now(timezone.utc).isoformat(),"answer_lock_sha256":sha(P/"answer_lock.json"),"answer_sha256":sha(P/"answer_before_subtitle.json"),"status":"EXPOSED_FOR_EVALUATION_NOT_UNREAD_HOLDOUT","other_reserved_episodes_accessed":[]}
(P/"exposure.json").write_text(json.dumps(exposure,ensure_ascii=False,indent=2),encoding="utf-8")
raw=Path(meta["file"]).read_bytes()
assert hashlib.sha256(raw).hexdigest()==meta["sha256"]
text=raw.decode("utf-8-sig").replace("\r\n","\n")
cues=[]
for block in re.split(r"\n\s*\n",text.strip()):
 lines=block.splitlines()
 if len(lines)>=3 and "-->" in lines[1]:
  cues.append({"cue":int(lines[0]),"time":lines[1],"text":"\n".join(lines[2:])})
assert cues
(P/"target_transcript.json").write_text(json.dumps({"episode":"472","source_sha256":meta["sha256"],"cues":cues},ensure_ascii=False,indent=2),encoding="utf-8")
(P/"reading.txt").write_text("\n".join(f'{c["cue"]} | {c["time"]} | {c["text"]}' for c in cues),encoding="utf-8")
print("parsed",len(cues),"cues",cues[0]["cue"],cues[-1]["cue"])
print("\n".join(f'{c["cue"]} | {c["text"]}' for c in cues[:230]))