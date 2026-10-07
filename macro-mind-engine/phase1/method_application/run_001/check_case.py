"""Validate this research application's provenance and evidence contracts."""

import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path

OUT = Path(__file__).resolve().parent
R = OUT.parents[2]


def read(name):
    return json.loads((OUT / name).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(c, f, s):
    assert c["framework_id"] == f["id"]
    assert c["framework_sha256"] == sha(OUT / "framework.json")
    assert c["mode"] == "HISTORICAL_TRANSFER_APPLICATION_NOT_BLIND"
    assert c["analysis_authorship"] == "ASSISTANT_USING_CANDIDATE_FRAMEWORK_NOT_BLOGGER_OPINION"
    assert c["score_eligible"] is False and c["semantic_acceptance"] is False
    assert c["canonical_write"] is False
    assert datetime.fromisoformat(s["published_at"]) <= datetime.fromisoformat(c["evidence_cutoff"])
    assert s["event_verification"] == "SINGLE_MEDIA_REPORT_NOT_INDEPENDENTLY_CORROBORATED"
    assert c["source_files"] == [
        {"id": s["id"], "path": "news_source.json", "sha256": sha(OUT / "news_source.json")}
    ]
    mids = {m["id"] for m in f["methods"]}
    apps = c["applications"]
    assert len(apps) == len(mids) == 5
    assert {a["method_id"] for a in apps} == mids
    facts = {v["id"] for v in s["notes"]}
    assert len(facts) == len(s["notes"])
    steps = {}
    for a in apps:
        assert a["applicability"] in [
            "APPLICABLE",
            "LIMITED",
            "PARTIAL",
            "TRANSFER_LIMITED",
            "INITIAL_ONLY",
            "NOT_APPLICABLE",
        ]
        assert all(
            a[k]
            for k in [
                "reason",
                "working_judgment",
                "alternative",
                "update_trigger",
                "transfer_note",
            ]
        )
        for step in a["steps"]:
            assert step["id"] not in steps
            assert step["evidence_refs"] and set(step["evidence_refs"]) <= facts
            assert step["operation"] and step["result"]
            steps[step["id"]] = step
    assert len({j["id"] for j in c["judgments"]}) == len(c["judgments"])
    for j in c["judgments"]:
        assert j["supports"] and set(j["supports"]) <= steps.keys()
        assert j["basis"] and set(j["basis"]) <= facts
        used = {ref for step in j["supports"] for ref in steps[step]["evidence_refs"]}
        assert set(j["basis"]) <= used
        assert all(j[k] for k in ["scope", "alternatives", "strengthen", "weaken", "withdraw"])
        assert j["claim_type"] in ["FACT_STATE", "WORKING_BASELINE"]
        assert j["status"] == ("UNKNOWN" if j["claim_type"] == "FACT_STATE" else "PROVISIONAL")
    assert c["unresolved"] and c["operating_consequence"]


c, f, s = read("case.json"), read("framework.json"), read("news_source.json")
validate(c, f, s)
print(
    "PASS: positive application, all 5 methods represented, 9 steps trace to source, judgments bounded."
)
mutations = [
    (
        "unknown_fact_ref",
        lambda c, f, s: c["applications"][0]["steps"][0]["evidence_refs"].append("MISSING"),
    ),
    ("future_source", lambda c, f, s: s.update(published_at="2026-09-02T00:00:00+08:00")),
    ("method_omitted", lambda c, f, s: c["applications"].pop()),
    ("framework_substituted", lambda c, f, s: c.update(framework_sha256="0" * 64)),
    ("blogger_attribution", lambda c, f, s: c.update(analysis_authorship="BLOGGER")),
    ("false_blind_mode", lambda c, f, s: c.update(mode="BLIND")),
    ("score_eligible", lambda c, f, s: c.update(score_eligible=True)),
    ("fact_promoted", lambda c, f, s: c["judgments"][1].update(status="OBSERVED")),
    ("baseline_promoted", lambda c, f, s: c["judgments"][0].update(status="CERTAIN")),
    (
        "unverified_news_promoted",
        lambda c, f, s: s.update(event_verification="INDEPENDENTLY_VERIFIED"),
    ),
    ("missing_withdrawal", lambda c, f, s: c["judgments"][0].update(withdraw="")),
    ("broken_reasoning_ref", lambda c, f, s: c["judgments"][0]["supports"].append("MISSING")),
]
results = []
for name, mutate in mutations:
    x, y, z = copy.deepcopy(c), copy.deepcopy(f), copy.deepcopy(s)
    mutate(x, y, z)
    try:
        validate(x, y, z)
    except (AssertionError, KeyError):
        results.append({"name": name, "rejected": True})
        print("PASS rejected:", name)
    else:
        raise AssertionError("Invalid packet accepted: " + name)
for name in ["framework_lock.json", "case_lock.json"]:
    for file, h in read(name)["files"].items():
        assert sha(OUT / file) == h, file
assert read("case_lock.json")["framework_lock_sha256"] == sha(OUT / "framework_lock.json")
assert read("source_selection.json")["after_framework_lock"] == sha(OUT / "framework_lock.json")
framework_refs = {v["id"] for v in read("framework_evidence.json")}
for m in f["methods"]:
    assert set(m["refs"]) <= framework_refs
    assert m["semantic_approval"] == "NOT_GRANTED"
    assert all(
        m[k]
        for k in [
            "applicability",
            "required_inputs",
            "procedure",
            "default_judgment",
            "not_applicable_or_limited",
            "update_rule",
        ]
    )
old = read("protected_before.json")
for path, h in old.items():
    assert sha(R / path) == h, path
result = {
    "positive_contract": True,
    "negative_cases": results,
    "method_count": 5,
    "reasoning_steps": len([v for a in c["applications"] for v in a["steps"]]),
    "judgment_count": len(c["judgments"]),
    "protected_files_unchanged": len(old),
    "framework_and_case_locks_intact": True,
    "semantic_accuracy": "NOT_SCORED",
    "blogger_case_comparison": "NOT_PERFORMED",
    "forecast_result": "NOT_EVALUATED",
    "external_events": "NOT_INDEPENDENTLY_CORROBORATED",
}
(OUT / "validation.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(
    "PASS: frozen framework/case unchanged;",
    len(old),
    "old files unchanged. Checks do not validate semantic reasoning.",
)
