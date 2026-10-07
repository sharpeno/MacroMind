from copy import deepcopy

import pytest

from .helpers import has, issues, obj, step


def test_none_conflict_uncertain_first_allowed(engine):
    values = [
        obj("AnalystMethodSignal", "prior"),
        obj(
            "AnalystMethodSignal", "s", recurrence_match="none", matched_prior_signal_refs=["prior"]
        ),
    ]
    assert has(engine.validate(values), "V-AN001", "ERROR")
    value = obj(
        "AnalystMethodSignal", recurrence_match="uncertain", recurrence_status="first_observation"
    )
    assert not engine.validate([value]).errors


@pytest.mark.parametrize("status", ["repeated", "frequent", "candidate_pattern"])
def test_recurrence_eligibility(engine, status):
    values = [
        obj("AnalystMethodSignal", "prior"),
        obj("AnalystMethodSignal", "s", recurrence_status=status, recurrence_match="uncertain"),
    ]
    assert has(engine.validate(values), "V-AN002", "INDETERMINATE")
    values[1]["matched_prior_signal_refs"] = ["prior"]
    context = {
        "current_content_time": "2026-08-05T00:00:00Z",
        "time_overrides": {"prior": "2026-09-21T00:00:00Z"},
    }
    assert has(engine.validate(values, context), "V-AN002", "ERROR")
    context["time_overrides"]["prior"] = "2026-01-01T00:00:00Z"
    assert has(engine.validate(values, context), "V-AN002", "PASS")


@pytest.mark.parametrize(
    "attribute,value",
    [("expression_level", "model_reconstruction"), ("analysis_context", "model_diagnostic")],
)
def test_direct_model_evidence(engine, attribute, value):
    values = [
        obj("Argument", "arg", **{attribute: value}),
        obj("AnalystMethodSignal", argument_refs=["arg"]),
    ]
    before = deepcopy(values)
    report = engine.validate(values)
    assert has(report, "V-AN003", "ERROR") and values == before
    assert all(i.review_required for i in issues(report, "V-AN003") if i.outcome == "ERROR")


def test_mixed_argument_and_heuristic_guard(engine):
    values = [
        obj("Claim", "a"),
        obj("Claim", "b"),
        obj("Argument", "arg", steps=[step(expression_level="model_reconstruction")]),
        obj("AnalystMethodSignal", argument_refs=["arg"]),
    ]
    assert has(engine.validate(values), "V-AN003", "WARNING")
    values = [
        obj("Claim", "c", analysis_context="model_diagnostic"),
        obj("Heuristic", provenance=["c"]),
    ]
    assert has(engine.validate(values), "V-AN003", "ERROR")


def test_no_skill_promotion(engine):
    value = obj("Heuristic", status="candidate")
    assert has(engine.validate([value]), "V-GOV003", "INDETERMINATE")
    value["status"] = "validated_skill"
    assert has(engine.validate([value]), "V-SCH002", "ERROR")


def test_observer_is_not_inherited_or_required_to_differ(engine):
    value = obj("AnalystMethodSignal", observed_reasoner_id="same", annotation_observer="same")
    report = engine.validate([value])
    assert has(report, "V-AN004", "PASS") and not report.errors
    value["observed_reasoner_id"] = None
    before = deepcopy(value)
    assert has(engine.validate([value]), "V-AN004", "INDETERMINATE")
    assert value == before
