"""Regression cases derived from human review; passing is not semantic acceptance."""

import copy
import json
from pathlib import Path

import pytest

from macromind.quality.annotations import assess, review_disposition

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "phase1/batch_pilot/run_003"
POLICIES = ROOT / "phase1/extraction_quality/run_001/policies"


def case(ep):
    return [
        json.loads(p.read_bytes())
        for p in (
            RUN / ep / "annotation.json",
            RUN / ep / "segments.json",
            POLICIES / (ep + ".json"),
        )
    ]


def claim(a, cid):
    return next(c for c in a["claims"] if c[0] == cid)


@pytest.mark.parametrize("ep", [f"EP{i:03}" for i in range(1, 6)])
def test_baseline_guards_do_not_promote_semantic_acceptance(ep):
    result = assess(*case(ep))
    assert result["status"] == "GUARDS_PASSED"
    assert result["unreviewed_ids"]
    assert result["semantic_acceptance"] is False


@pytest.mark.parametrize(
    "ep,cid,token",
    [
        ("EP001", "C19", "成本继续上涨"),
        ("EP002", "C22", "转述并反对"),
        ("EP002", "C22", "只要9月加息落地"),
        ("EP003", "C23", "与这一历史经验相反"),
        ("EP003", "C23", "他据此判断"),
        ("EP004", "C15", "若能提前选中"),
        ("EP004", "C15", "十年后"),
        ("EP004", "C22", "名不副实"),
    ],
)
def test_lost_reviewed_facet_blocks_compilation(ep, cid, token):
    a, s, p = case(ep)
    claim(a, cid)[2] = claim(a, cid)[2].replace(token, "")
    result = assess(a, s, p)
    assert not result["compile_allowed"]
    assert any(e["rule"] == "Q-FACET" for e in result["errors"])


def test_restored_whole_method_conclusion_is_blocked():
    a, s, p = case("EP005")
    next(x for x in a["arguments"] if x[0] == "A03")[2] = "C11"
    assert any(e["rule"] == "Q-EDGE-SCOPE" for e in assess(a, s, p)["errors"])


def test_outlook_cannot_return_to_forecast_candidates():
    a, s, p = case("EP004")
    a["forecast_candidates"].append("C15")
    assert any(e["rule"] == "Q-FORECAST" for e in assess(a, s, p)["errors"])


def test_context_cannot_silently_become_claim():
    a, s, p = case("EP005")
    a["claims"].append(["C99", [230], "新增观点", "active"])
    assert any(e["rule"] == "Q-CONTEXT" for e in assess(a, s, p)["errors"])


def test_rewording_keeps_keywords_but_still_requires_review():
    a, s, p = case("EP003")
    claim(a, "C23")[2] += " 因此这已经是被证实的事实。"
    result = assess(a, s, p)
    assert result["status"] == "REVIEW_REQUIRED"
    assert result["semantic_acceptance"] is False


def test_unreviewed_material_not_automatically_approved():
    a, s, p = case("EP003")
    assert "C07" not in p["reviewed_ids"]
    claim(a, "C07")[2] += " 这是新表述。"
    assert assess(a, s, p)["status"] == "REVIEW_REQUIRED"


@pytest.mark.parametrize(
    "mutation",
    ["quote", "duplicate_cue", "duplicate_claim", "missing_reference", "missing_cue", "bad_shape"],
)
def test_invalid_evidence_and_structure_block(mutation):
    a, s, p = case("EP002")
    if mutation == "quote":
        s[0]["quote"] += "变更"
    elif mutation == "duplicate_cue":
        s.append(copy.deepcopy(s[0]))
    elif mutation == "duplicate_claim":
        a["claims"].append(copy.deepcopy(a["claims"][0]))
    elif mutation == "missing_reference":
        a["arguments"][0][2] = "absent"
    elif mutation == "missing_cue":
        a["claims"][0][1] = [999999]
    else:
        a["claims"][0] = ["broken"]
    assert not assess(a, s, p)["compile_allowed"]


def test_positive_dropdown_does_not_discard_instruction_in_note():
    assert (
        review_disposition({"decision": "faithful", "note": "成本继续上涨需明确"})
        == "INSPECT_TEXT_BEFORE_CLOSING"
    )
    assert review_disposition({"decision": "context", "note": ""}) == "KEEP_CONTEXT"
    assert review_disposition({"decision": "accept_revision"}) == "ACCEPT_WITHIN_REVIEW_SCOPE"
    assert review_disposition({"decision": "extract"}) == "ACTION_REQUIRED"
    assert review_disposition({"decision": "unknown-new-option"}) == "MANUAL_REVIEW"


def test_new_forecast_classification_requires_review_even_if_claim_unchanged():
    a, s, p = case("EP002")
    cid = next(c[0] for c in a["claims"] if c[0] not in a["forecast_candidates"])
    a["forecast_candidates"].append(cid)
    result = assess(a, s, p)
    assert result["status"] == "REVIEW_REQUIRED"
    assert result["compile_allowed"] is False
