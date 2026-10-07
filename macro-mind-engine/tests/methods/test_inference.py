import json
from pathlib import Path

import pytest

from macromind.methods.inference import render, validate

ROOT = Path(__file__).resolve().parents[2]


def load():
    return json.loads(
        (ROOT / "phase1/method_prototype/run_002/inference.json").read_text(encoding="utf-8")
    )


def test_indirect_evidence_allows_hypothesis_not_confirmation():
    data, _ = validate(load(), ROOT)
    assert len(data["cases"]) == 2
    hypotheses = [h for c in data["cases"] for h in c["hypotheses"]]
    assert len(hypotheses) == 3
    assert all(h["epistemic_status"] == "HYPOTHESIS_FROM_INDIRECT_EVIDENCE" for h in hypotheses)
    assert all(h["confirmation"] == "NOT_CONFIRMED" for h in hypotheses)
    assert not data["semantic_acceptance"]
    assert not data["skill_ready"]
    assert data["cases"][1]["hypotheses"][0]["attribution"] == "assistant_transfer"


@pytest.mark.parametrize(
    "mutate,match",
    [
        (
            lambda d: d["cases"][0]["hypotheses"][0].update(confirmation="CONFIRMED"),
            "NOT_CONFIRMED",
        ),
        (
            lambda d: d["cases"][0]["hypotheses"][0].update(observation_refs=["missing"]),
            "Unresolved",
        ),
        (
            lambda d: d["cases"][0]["hypotheses"][0].update(attribution_anchors=[]),
            "attribution requires",
        ),
        (lambda d: d["cases"][0]["hypotheses"][0].update(alternatives=[]), "at least 1"),
        (lambda d: d["cases"][0]["hypotheses"][0].update(assumptions=[]), "at least 1"),
        (lambda d: d["cases"][0]["hypotheses"][0].update(weaken_with=[]), "at least 1"),
        (lambda d: d["sources"]["ep002"].update(sha256="0" * 64), "hash mismatch"),
        (
            lambda d: d["cases"][0]["observations"][0]["anchors"][0].update(quote="invented"),
            "Quote/record",
        ),
        (lambda d: d["cases"][0]["observations"][0].update(world_fact_verified=True), "False"),
        (lambda d: d.update(skill_ready=True), "False"),
        (
            lambda d: d["cases"][0]["observations"][0].update(layer="official_statement"),
            "layer mismatch",
        ),
        (lambda d: d["cases"][0]["hypotheses"][1].update(id="H1"), "Duplicate"),
    ],
)
def test_guardrails(mutate, match):
    data = load()
    mutate(data)
    with pytest.raises(ValueError, match=match):
        validate(data, ROOT)


def test_renderer_retains_original_strength_and_escapes_input():
    data = load()
    data["cases"][1]["hypotheses"][0]["statement"] = "<script>alert(1)</script>"
    html = render(data, ROOT)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "肯定" in html
    assert "不再因缺少事前记录而停止分析" in html
    assert "尚未确证" in html
