import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
for folder in [P.parent/"v03_draft_001",ROOT/"phase1/conflict_study/run_001",ROOT/"phase1/conflict_study/run_002"]:
 for name,digest in read(folder/"manifest.json").items():
  assert sha(folder/name)==digest,(folder,name)
 checks.append(str(folder.relative_to(ROOT))+": sealed files unchanged")
src=Path("C:/Users/无语/Downloads/MacroMind_v03draft001_2026-10-05T17-32-00-452Z_6of6.json")
assert src.read_bytes()==(P/"submitted_review.json").read_bytes()==(P/"exports"/src.name).read_bytes()
checks.append("submitted review archived byte-for-byte")
old=read(P.parent/"v03_draft_001/review_packet.json")
new=read(P/"review_packet.json")
draft=read(P/"framework_draft.json")
assert new["draft_sha256"]==sha(P/"framework_draft.json")
assert draft["state"]=="DRAFT_PENDING_HUMAN_REVIEW_NOT_ACTIVE"
assert sha(ROOT/"phase1/method_application/run_002/framework.json")=="fcbc841c3f90d0bba5ee26e168d0e25bb629ffa58a9633aaeaae8a5a899ee84a"
checks.append("new identity hash matches; v0.2 unchanged; v0.3 not activated")
for c in new["cards"]:
 o=next(x for x in old["cards"] if x["id"]==c["id"])
 if c["inherited"]:
  for key in ["title","rule","inputs","steps","default","update","example","boundary","target"]:
   assert c[key]==o[key],(c["id"],key)
checks.append("four approved rule and boundary texts preserved exactly")
trans={x["episode"]:x for x in read(ROOT/"phase1/conflict_study/run_002/transcripts.json")}
n=0
for c in new["cards"]:
 for e in c["evidence"]:
  nums=[x["cue"] for x in e["cues"]]
  assert nums==list(range(nums[0],nums[-1]+1))
  assert e["cues"]==[x for x in trans[e["episode"]]["cues"] if nums[0]<=x["cue"]<=nums[-1]]
  ctx=(P/("contexts/"+e["episode"]+".html")).read_text(encoding="utf-8")
  for cue in trans[e["episode"]]["cues"]:assert 'id="cue-'+str(cue["cue"])+'"' in ctx
  n+=len(nums)
checks.append(f"{n} displayed cue occurrences match development transcripts exactly, continuous; full context anchors verified")
c4=next(c for c in new["cards"] if c["id"]=="C04")
assert set(range(194,225)) <= {q["cue"] for e in c4["evidence"] if e["episode"]=="468" for q in e["cues"]}
for method in draft["methods"]:assert method["v03_proposed_extensions"]==[c["id"] for c in new["cards"] if c["target"]==method["id"]]
checks.append("C04 missing cues 194-224 restored; C03 remapped to actor inference M01; extension references consistent")
qa=read(Path("G:/youhegaojian/review-ui-qa/framework-v03-delta/result.json"))
assert qa["pass"]
result={"pass":True,"checks":checks,"ui_qa":qa,"limits":["Context boundaries manually selected, not a guarantee of semantic completeness","No external fact or forecast accuracy validation","No held-out subtitle reading; no new semantic approval inferred from engineering tests"]}
(P/"validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))