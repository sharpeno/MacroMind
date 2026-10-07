import json,re,hashlib,copy
from pathlib import Path

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
PREV=P.parent/"run_001"
def read(path):return json.loads(path.read_text(encoding="utf-8-sig"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def parse(path):
    result=[]
    for block in re.split(r"\r?\n\s*\r?\n",path.read_text(encoding="utf-8-sig").strip()):
        lines=block.splitlines()
        assert len(lines)>=3 and "-->" in lines[1]
        result.append({"cue":int(lines[0]),"time":lines[1],"text":" ".join(lines[2:])})
    return result
def check(a, trans):
    split=read(PREV/"split_lock.json")
    expected=set(split["development"])-{"454","455"}
    hold=set(split["reserved_evaluation"])
    assert len(a["read_episodes"])==13 and set(a["read_episodes"])==expected
    assert not set(a["read_episodes"]) & hold and not a["reserved_transcripts_read"]
    assert len(trans)==13 and {r["episode"] for r in trans}==expected
    for r in trans:
        assert sha(Path(r["file"]))==r["sha256"]
        assert r["cues"]==parse(Path(r["file"]))
        assert len({c["cue"] for c in r["cues"]})==len(r["cues"])
    cues={r["episode"]:{c["cue"]:c for c in r["cues"]} for r in trans}
    assert len(a["units"])==39 and len({u["id"] for u in a["units"]})==39
    assert {u["episode"] for u in a["units"]}==expected
    ids={u["id"] for u in a["units"]}
    for u in a["units"]:
        assert u["fact_verification"]=="NOT_PERFORMED" and u["human_review"]=="NOT_REVIEWED"
        assert u["evidence"]==[cues[u["episode"]][i] for lo,hi in u["cue_ranges"] for i in range(lo,hi+1)]
    assert len(a["timeline"])==13 and {t["episode"] for t in a["timeline"]}==expected
    for t in a["timeline"]:
        assert set(t["units"])<=ids
        assert all(next(u for u in a["units"] if u["id"]==ident)["episode"]==t["episode"] for ident in t["units"])
    for rule in a["candidate_rules"]:
        eps=sorted({u["episode"] for u in a["units"] if u["id"] in rule["units"]},key=int)
        assert set(rule["units"])<=ids and rule["distinct_episodes"]==eps
        assert rule["status"]=="REPEATED_IN_DEVELOPMENT_NOT_APPLIED_NOT_HUMAN_APPROVED"
    assert a["acceptance"]["world_fact_accuracy"]==a["acceptance"]["prediction_accuracy"]=="NOT_TESTED"
    assert not a["acceptance"]["framework_changed"]
    assert a["acceptance"]["holdout_evaluation"]=="NOT_STARTED"
    for name,digest in read(PREV/"manifest.json").items():assert sha(PREV/name)==digest,name
    assert sha(Path(split["framework_path"]))==split["framework_sha256"]

a,trans=read(P/"analysis.json"),read(P/"transcripts.json")
check(a,trans)
cases=["holdout_read","missing_episode","tamper_evidence","duplicate_unit","false_fact_pass","false_prediction_pass","false_framework_change","false_replication","wrong_timeline_ref"]
rejected=[]
for case in cases:
    b=copy.deepcopy(a)
    if case=="holdout_read":b["read_episodes"][0]="472"
    if case=="missing_episode":b["read_episodes"].pop()
    if case=="tamper_evidence":b["units"][0]["evidence"][0]["text"]="tampered"
    if case=="duplicate_unit":b["units"][1]["id"]=b["units"][0]["id"]
    if case=="false_fact_pass":b["acceptance"]["world_fact_accuracy"]="PASS"
    if case=="false_prediction_pass":b["acceptance"]["prediction_accuracy"]="PASS"
    if case=="false_framework_change":b["acceptance"]["framework_changed"]=True
    if case=="false_replication":b["candidate_rules"][0]["distinct_episodes"].append("999")
    if case=="wrong_timeline_ref":b["timeline"][0]["units"]=["U39"]
    try:check(b,trans)
    except AssertionError:rejected.append(case)
    else:raise AssertionError("negative passed "+case)
result={"status":"PASS_STRUCTURAL_ONLY","episodes":len(trans),"cues":sum(len(r["cues"]) for r in trans),"units":len(a["units"]),"timeline_nodes":len(a["timeline"]),"candidate_rules":len(a["candidate_rules"]),"negative_tests_rejected":rejected,"prior_artifact_hashes_unchanged":len(read(PREV/"manifest.json")),"source_hashes_unchanged":13,"framework_unchanged":True,"reserved_transcripts_read":[],"fact_or_prediction_acceptance":False}
(P/"validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))
