import copy
import hashlib
import json
from datetime import date
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def read(n):
    return json.loads((OUT / n).read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


f, c, s = read("framework.json"), read("case.json"), read("source.json")


def check(v):
    assert v["framework_sha256"] == sha(OUT / "framework.json")
    assert v["source_sha256"] == sha(OUT / "source.json")
    assert v["analysis_author"] == "ASSISTANT_NOT_BLOGGER"
    assert v["mode"] == "HISTORICAL_TRANSFER_NOT_BLIND"
    assert v["score_eligible"] is False and v["semantic_acceptance"] is False
    assert date.fromisoformat(s["published"]) <= date.fromisoformat(v["as_of"])
    assert v["benefit_implies_authorship"] is False
    assert v["missing_implies_absence"] is False
    assert v["motive_attribution"] == "UNPROVEN"
    assert v["execution_state"] == "ANNOUNCED_SCHEDULED" and v["effect_state"] == "UNKNOWN"
    refs = {n["id"] for n in s["notes"]}
    assert len(v["applications"]) == 5 and {a["id"] for a in v["applications"]} == {
        m["id"] for m in f["methods"]
    }
    for a in v["applications"]:
        assert a["refs"] and set(a["refs"]) <= refs and a["next"]
    assert len({a["id"] for a in v["actors"]}) == len(v["actors"]) >= 3
    for a in v["actors"]:
        assert a["basis"] and set(a["basis"]) <= refs and a["dependency"]
        assert a["status"] in ["PUBLIC_GOAL", "ASSISTANT_HYPOTHESIS"]
    assert len(v["goal_action_fit"]["alternatives"]) >= 2
    assert v["goal_action_fit"]["state"] == "PARTIAL_FIT"
    for link in v["causal_links"]:
        assert link["status"] == "HYPOTHESIS" and link["condition"] and link["break"]
        assert link["refs"] and set(link["refs"]) <= refs
    assert v["baseline"]["state"] == "PROVISIONAL"
    assert all(v["baseline"][k] for k in ["strengthen", "weaken", "withdraw"])


check(c)
print(
    "PASS positive v0.2 application: actor dependencies, goal/action alternatives and bounded feedback."
)
cases = [
    ("beneficiary_to_planner", lambda x: x.update(benefit_implies_authorship=True)),
    ("missing_to_absent", lambda x: x.update(missing_implies_absence=True)),
    ("hidden_motive_proven", lambda x: x.update(motive_attribution="PROVEN")),
    ("announcement_to_execution", lambda x: x.update(execution_state="OBSERVED")),
    ("action_to_effect", lambda x: x.update(effect_state="OBSERVED")),
    ("omit_method", lambda x: x["applications"].pop()),
    ("missing_dependency", lambda x: x["actors"][1].update(dependency="")),
    ("sole_motive", lambda x: x["goal_action_fit"].update(alternatives=["only one"])),
    ("unconditional_link", lambda x: x["causal_links"][0].update(condition="")),
    ("no_retraction", lambda x: x["baseline"].update(withdraw="")),
    ("fake_reference", lambda x: x["applications"][0]["refs"].append("E99")),
    ("false_blind", lambda x: x.update(mode="BLIND")),
]
results = []
for name, mutate in cases:
    v = copy.deepcopy(c)
    mutate(v)
    try:
        check(v)
    except (AssertionError, KeyError):
        results.append({"name": name, "rejected": True})
        print("PASS rejected", name)
    else:
        raise AssertionError(name)
for name in ["framework_lock.json", "case_lock.json"]:
    for p, h in read(name)["files"].items():
        assert sha(OUT / p) == h, p
assert read("case_lock.json")["framework_lock_sha256"] == sha(OUT / "framework_lock.json")
old = read("protected_before.json")
for p, h in old.items():
    assert sha(ROOT / p) == h, p
prior = json.loads(
    (ROOT / "phase1/method_application/run_001/framework.json").read_text(encoding="utf-8")
)
for mid in ["M03", "M05"]:
    a = copy.deepcopy(next(m for m in f["methods"] if m["id"] == mid))
    a.pop("revision_evidence")
    assert a == next(m for m in prior["methods"] if m["id"] == mid)
result = {
    "positive": True,
    "negative_cases": results,
    "protected_files_unchanged": len(old),
    "frozen_files_unchanged": True,
    "unchanged_methods": ["M03", "M05"],
    "semantic_accuracy": "NOT_SCORED",
    "long_term_effectiveness": "NOT_TESTED",
    "test_scope": "Structured guard checks; cannot detect all misleading natural-language statements",
}
(OUT / "validation.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(
    "PASS",
    len(old),
    "protected files unchanged; M03/M05 unchanged. Semantic effectiveness not established.",
)
