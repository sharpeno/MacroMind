"""Evidence contract checks for this research packet, including deliberate failures."""

import copy
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def digest(p):
    with p.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def validate(p):
    assert p["mode"] == "RETROSPECTIVE_ASSISTANT_AUTHORED"
    assert p["canonical_write"] is False
    assert p["user_review"] == "NOT_YET_REVIEWED"
    assert p["source_fact_verification"] == "NOT_PERFORMED"
    ids = [c["id"] for c in p["new_claims"] + p["inherited_claims"]]
    assert len(ids) == len(set(ids))
    records = {c["id"]: c for c in p["new_claims"] + p["inherited_claims"]}
    order = [n["episode"] for n in p["chronology"]]
    assert order == sorted(order, key=lambda ep: p["episodes"][ep]["published_at"])
    assert set(order) == set(p["episodes"])
    for c in p["new_claims"]:
        source = {q["cue_id"]: q for q in read(OUT / (c["episode"] + ".segments.json"))}
        assert c["review_status"] == "ASSISTANT_EXTRACTED_NOT_HUMAN_REVIEWED"
        assert c["external_truth"] == "NOT_VERIFIED"
        assert c["quotes"] and c["constraint"]
        assert c["published_at"] == p["episodes"][c["episode"]]["published_at"]
        for q in c["quotes"]:
            assert q == source[q["cue_id"]], c["id"]
    for c in p["inherited_claims"]:
        originals = read(ROOT / "phase1/batch_pilot/run_005" / c["episode"] / "claims.json")
        orig = next(v for v in originals if v["claim_id"] == c["id"])
        assert all(c[k] == v for k, v in orig.items()), c["id"]
    for group in ["connections", "method_candidates", "issues", "chronology"]:
        for item in p[group]:
            assert item["refs"] and all(r in records for r in item["refs"])
    for m in p["method_candidates"]:
        assert m["status"] == "CANDIDATE_NOT_VALIDATED_SKILL"
        assert m["steps_attribution"] == "ASSISTANT_OPERATIONALIZATION"
    for n in p["chronology"]:
        cutoff = p["episodes"][n["episode"]]["published_at"]
        assert all(records[r]["published_at"] <= cutoff for r in n["refs"])
    for ep in ["EP007", "EP008"]:
        v = p["episodes"][ep]["intake"]
        assert v["contiguous_ids"] and v["valid_intervals"] and not v["overlaps"]
        assert v["max_gap_seconds"] <= 2 and abs(v["tail_gap_seconds"]) < 0.1
        assert v["every_srt_quote_found_in_txt"] and not v["audio_listened"]
        assert v["semantic_completeness"] == "NOT_ESTABLISHED"


p = read(OUT / "analysis.json")
validate(p)
print(
    "PASS positive packet: cue binding, chronology, references, inherited claims, provenance, intake."
)
mutations = [
    ("wrong_quote", lambda x: x["new_claims"][0]["quotes"][0].update(quote="伪造原话")),
    ("wrong_chronology", lambda x: x["chronology"].reverse()),
    (
        "changed_inherited",
        lambda x: x["inherited_claims"][0].update(normalized_statement="改写旧主张"),
    ),
    ("unreviewed_promoted", lambda x: x["new_claims"][0].update(review_status="APPROVED")),
    ("method_promoted", lambda x: x["method_candidates"][0].update(status="VALIDATED_SKILL")),
    ("future_evidence", lambda x: x["chronology"][0]["refs"].append("EP003/C01")),
    ("missing_reference", lambda x: x["connections"][0]["refs"].append("EP999/C01")),
    ("fact_verified_without_evidence", lambda x: x.update(source_fact_verification="VERIFIED")),
]
results = []
for name, mutate in mutations:
    bad = copy.deepcopy(p)
    mutate(bad)
    try:
        validate(bad)
    except (AssertionError, KeyError):
        results.append({"name": name, "expected_rejection_observed": True})
        print("PASS rejected:", name)
    else:
        raise AssertionError("Invalid packet accepted: " + name)
inputs = read(OUT / "input_manifest.json")
for name, entry in inputs.items():
    assert digest(ROOT.parent / name) == entry["sha256"], name
protected = read(OUT / "protected_before.json")
for name, expected in protected.items():
    assert digest(ROOT / name) == expected, name
for ep in ["EP007", "EP008"]:
    for src in (OUT / "sources" / ep).rglob("*"):
        if src.is_file():
            orig = (
                ROOT.parent / "batch_pilot_materials" / ep / src.relative_to(OUT / "sources" / ep)
            )
            assert digest(src) == digest(orig)
result = {
    "positive_packet": True,
    "negative_cases": results,
    "input_hashes_verified": len(inputs),
    "protected_hashes_unchanged": len(protected),
    "source_copies_match": True,
    "semantic_accuracy": "NOT_SCORED",
    "external_truth": "NOT_VERIFIED",
}
(OUT / "validation.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(
    "PASS",
    len(inputs),
    "input files unchanged;",
    len(protected),
    "protected files unchanged; copied sources identical.",
)
