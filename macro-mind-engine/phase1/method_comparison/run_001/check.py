import copy
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def read(name):
    return json.loads((OUT / name).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


p = read("comparison.json")
base = json.loads((ROOT / p["baseline_path"]).read_text(encoding="utf-8"))
segments = {v["cue_id"]: v for v in read("segments.json")}


def validate(data):
    assert data["mode"] == "POST_UNBLINDING_QUALITATIVE_COMPARISON"
    assert data["score_eligible"] is False and data["semantic_acceptance"] is False
    assert data["input_parity"] is False
    assert data["baseline_modified"] is False and data["framework_modified"] is False
    assert data["external_truth"] == "NOT_VERIFIED"
    assert data["baseline_sha256"] == sha(ROOT / data["baseline_path"])
    assert data["framework_sha256"] == sha(
        ROOT / "phase1/method_application/run_001/framework.json"
    )
    assert data["overall"] == "PARTIAL_METHOD_ALIGNMENT_NOT_FULL_FIDELITY_ACCEPTANCE"
    units = {u["id"]: u for u in data["blogger_units"]}
    assert len(units) == len(data["blogger_units"])
    for u in units.values():
        assert u["quotes"] and u["boundary"]
        assert u["external_truth"] == "NOT_VERIFIED"
        assert u["attribution"] == "BLOGGER_VIA_UNCORRECTED_ASR"
        for q in u["quotes"]:
            assert q == segments[q["cue_id"]]
    apps = {a["method_id"]: a for a in base["applications"]}
    comparisons = data["method_comparisons"]
    assert len(comparisons) == len(apps) and {m["method_id"] for m in comparisons} == set(apps)
    for m in comparisons:
        steps = {s["id"] for s in apps[m["method_id"]]["steps"]}
        assert m["baseline_refs"] and set(m["baseline_refs"]) <= steps
        assert m["blogger_refs"] and set(m["blogger_refs"]) <= set(units)
        assert m["verdict"] in ["PARTIAL", "NOT_COMPARABLE"]
        assert all(m[k] for k in ["same", "gap", "causes", "assessment"])
    judgments = {j["id"]: j for j in base["judgments"]}
    assert len(data["judgment_comparisons"]) == len(judgments)
    for j in data["judgment_comparisons"]:
        assert j["baseline_statement"] == judgments[j["id"]]["statement"]
        assert set(j["blogger_refs"]) <= set(units)
        assert j["verdict"] in ["DIFFERENT_QUESTION_NO_DIRECT_TEST", "NO_MATCHING_ASSERTION_FOUND"]
    for suggestion in data["improvement_proposals"]:
        assert suggestion["status"] == "PROPOSED_NOT_APPLIED"
        assert suggestion["source_refs"] and set(suggestion["source_refs"]) <= set(units)
        assert set(suggestion["target_methods"]) <= set(apps)
        assert suggestion["countercheck"]


validate(p)
print(
    "PASS: comparison references, exact quotes, unchanged baseline statements and bounded conclusions."
)
mutations = [
    ("altered_quote", lambda x: x["blogger_units"][0]["quotes"][0].update(quote="错误原话")),
    ("missing_method", lambda x: x["method_comparisons"].pop()),
    ("missing_evidence", lambda x: x["method_comparisons"][0]["blogger_refs"].append("B99")),
    ("wrong_baseline_ref", lambda x: x["method_comparisons"][0]["baseline_refs"].append("A99")),
    ("false_equal_inputs", lambda x: x.update(input_parity=True)),
    ("false_score", lambda x: x.update(score_eligible=True)),
    (
        "altered_judgment",
        lambda x: x["judgment_comparisons"][0].update(baseline_statement="修改基线"),
    ),
    ("promoted_truth", lambda x: x["blogger_units"][0].update(external_truth="VERIFIED")),
    ("unapproved_rule_change", lambda x: x["improvement_proposals"][0].update(status="APPLIED")),
    ("unjustified_full_pass", lambda x: x.update(overall="PASS")),
]
results = []
for name, mutate in mutations:
    bad = copy.deepcopy(p)
    mutate(bad)
    try:
        validate(bad)
    except (AssertionError, KeyError):
        results.append({"name": name, "rejected": True})
        print("PASS rejected:", name)
    else:
        raise AssertionError("Invalid packet accepted: " + name)
for path, h in read("input_hashes.json").items():
    assert sha(Path(path)) == h, path
for path, h in read("protected_before.json").items():
    assert sha(ROOT / path) == h, path
result = {
    "positive_contract": True,
    "negative_cases": results,
    "protected_files_unchanged": len(read("protected_before.json")),
    "source_files_unchanged": len(read("input_hashes.json")),
    "cue_count": len(segments),
    "qualitative_verdict": p["overall"],
    "fidelity_score": "NOT_COMPUTED",
    "world_facts": "NOT_VERIFIED",
}
(OUT / "validation.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(
    "PASS:", result["protected_files_unchanged"], "protected files unchanged; source hashes match."
)
