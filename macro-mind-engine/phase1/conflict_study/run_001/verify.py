import copy
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
def read(name):
    return json.loads((P / name).read_text(encoding="utf-8-sig"))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def check(registry, split, analysis):
    rows = registry["records"]
    assert len(rows) == 30 and len({r["id"] for r in rows}) == 30
    dev, hold = set(split["development"]), set(split["reserved_evaluation"])
    assert len(dev) == len(hold) == 15 and not dev & hold
    assert dev | hold == {r["episode"] for r in rows}
    for r in rows:
        assert sha(Path(r["file"])) == r["sha256"]
        assert r["analysis_date"] == r["filename_date"]
        assert (r["episode"] in dev) == (r["analysis_date"] <= "2023-10-16")
    assert sha(Path(split["framework_path"])) == split["framework_sha256"]
    assert sha(P/"news_baseline.json") == read("news_baseline_lock.json")["sha256"]
    assert set(analysis["read_episodes"]) <= dev
    assert analysis["reserved_transcripts_read"] == []
    assert analysis["acceptance"]["prediction_accuracy"] == "NOT_TESTED"
    cues = {r["episode"]: {c["cue"]: c for c in r["cues"]}
            for r in read("development_transcripts.json")}
    for unit in analysis["units"]:
        assert unit["episode"] in dev and unit["human_approval"] == "NOT_REVIEWED"
        for evidence in unit["evidence"]:
            assert evidence == cues[unit["episode"]][evidence["cue"]]
    assert all(not p["applied"] for p in analysis["proposals"])

registry, split, analysis = read("accepted_registry.json"), read("split_lock.json"), read("analysis.json")
check(registry, split, analysis)
negative = []
for kind in ["overlap", "wrong_date", "evidence_mutation", "false_acceptance", "holdout_read"]:
    r, s, a = copy.deepcopy(registry), copy.deepcopy(split), copy.deepcopy(analysis)
    if kind == "overlap": s["reserved_evaluation"][0] = s["development"][0]
    if kind == "wrong_date": r["records"][0]["analysis_date"] = "2099-01-01"
    if kind == "evidence_mutation": a["units"][0]["evidence"][0]["text"] = "tampered"
    if kind == "false_acceptance": a["acceptance"]["prediction_accuracy"] = "PASS"
    if kind == "holdout_read": a["read_episodes"].append(s["reserved_evaluation"][0])
    try: check(r,s,a)
    except AssertionError: negative.append(kind)
    else: raise AssertionError("negative not rejected: "+kind)
result = {"status":"PASS_STRUCTURAL_ONLY","records":30,
          "source_hashes_unchanged":30,"framework_unchanged":True,
          "development":15,"reserved":15,"read_development":2,
          "parsed_cues":sum(len(r["cues"]) for r in read("development_transcripts.json")),
          "units":len(analysis["units"]),"negative_tests_rejected":negative,
          "semantic_acceptance":False,"prediction_accuracy_verified":False}
(P/"validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))
