import copy
import json
from pathlib import Path

import pytest

from macromind.methods.prototype import analyze, render

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "phase1/method_prototype/run_001"


def load(name="public_case"):
    return json.loads((INPUT / f"{name}.packet.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "name,status",
    [
        ("public_case", "INCOMPLETE_METHOD_EVIDENCE"),
        ("complete", "TRACE_COMPLETE_NOT_VALIDATED"),
        ("missing", "INSUFFICIENT_SCOPE_EVIDENCE"),
        ("outside", "NOT_APPLICABLE"),
        ("counter", "COUNTEREVIDENCE"),
    ],
)
def test_statuses_are_not_semantic_approval(name, status):
    result = analyze(load(name), ROOT)
    assert result["status"] == status
    assert not result["semantic_acceptance"]
    assert not result["skill_ready"]
    assert not result["effectiveness_verified"]


@pytest.mark.parametrize(
    "mutation,match",
    [
        (lambda p: p["sources"]["ep002"].update(sha256="0" * 64), "hash mismatch"),
        (lambda p: p["sources"]["ep002"].update(path="../核心主旨.md"), "outside-root"),
        (lambda p: p["method"]["steps"][0]["anchors"][0].update(quote="伪造原话"), "Quote/record"),
        (lambda p: p["method"]["steps"][0]["anchors"][0].update(record="999999"), "Quote/record"),
        (
            lambda p: p["method"]["steps"][0]["anchors"][0].update(source="fed2024"),
            "remain separate",
        ),
        (lambda p: p["case"]["judgments"]["G1"].update(anchors=[]), "require case evidence"),
        (lambda p: p["case"]["judgments"].pop("S2"), "Exactly one"),
        (
            lambda p: p["case"]["judgments"].update(
                extra=copy.deepcopy(p["case"]["judgments"]["G1"])
            ),
            "Exactly one",
        ),
        (lambda p: p["method"]["steps"][0].update(id="G1"), "Duplicate"),
        (lambda p: p["case"].update(mode="as_of_analysis"), "Method unavailable"),
        (lambda p: p["sources"]["fed2024"].update(published="2025-01-01"), "beyond cutoff"),
        (lambda p: p["sources"]["ep002"].update(published="2027-01-01"), "beyond availability"),
        (lambda p: p["case"]["judgments"]["G1"].update(author="synthetic_fixture"), "Synthetic"),
        (lambda p: p["method"].update(skill_ready=True), "False"),
        (lambda p: p["sources"]["fed2024"].update(url="javascript:alert(1)"), "http"),
        (lambda p: p["method"]["steps"][0].update(question=" "), "at least 1"),
    ],
)
def test_invalid_evidence_and_time_boundaries_fail(mutation, match):
    packet = load()
    mutation(packet)
    with pytest.raises(ValueError, match=match):
        analyze(packet, ROOT)


def test_missing_is_not_false_and_trace_keeps_all_questions():
    result = analyze(load(), ROOT)
    assert len(result["open_questions"]) == 4
    assert result["counterevidence"] == []
    assert all(row["method_evidence"] for row in result["rows"])
    assert result["case"]["mode"] == "retrospective_transfer"


def test_free_text_cannot_inject_markup():
    packet = load()
    packet["case"]["judgments"]["S1"]["reason"] = '<script>alert("x")</script>'
    html = render(analyze(packet, ROOT))
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_false_semantics_with_valid_anchors_is_not_silently_certified():
    packet = load()
    for j in packet["case"]["judgments"].values():
        j.update(
            status="supported", anchors=copy.deepcopy(packet["case"]["judgments"]["G1"]["anchors"])
        )
    result = analyze(packet, ROOT)
    assert result["status"] == "TRACE_COMPLETE_NOT_VALIDATED"
    assert not result["semantic_acceptance"]
    assert result["case"]["mapping_review"] == "not_human_reviewed"
