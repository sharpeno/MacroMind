from copy import deepcopy

import pytest

from .helpers import criteria, forecast, has, issues, obj, time


def test_structurally_supported_and_unknown_window(engine):
    values = [obj("Claim"), forecast()]
    report = engine.validate(values)
    assert has(report, "V-FC001", "PASS") and not report.errors
    assert issues(report, "V-FC001")[0].details["admission"] == "ADMISSION_STRUCTURALLY_SUPPORTED"
    values[1]["prediction_window"] = {"state": "unknown"}
    before = deepcopy(values)
    report = engine.validate(values)
    assert has(report, "V-FC001", "INDETERMINATE") and not report.errors
    assert values == before


@pytest.mark.parametrize("branch", [None, {"state": "unknown"}, "selected branch text"])
def test_conditional_endorsement_is_not_inferred(engine, branch):
    values = [obj("Claim"), forecast(conditions="if demand grows", branch_selection=branch)]
    report = engine.validate(values)
    assert has(report, "V-FC002", "INDETERMINATE")
    assert not has(report, "V-FC001", "PASS") and not report.errors
    assert all(i.review_required for i in issues(report, "V-FC002"))


def test_scenario_stays_scenario_and_shared_claim_warns(engine):
    scenario = obj(
        "Scenario",
        claim_refs=["claim"],
        branches=[
            {"id": "branch", "condition": "if", "outcome": "possible", "child_branch_refs": []}
        ],
    )
    values = [obj("Claim"), scenario, forecast()]
    before = deepcopy(values)
    report = engine.validate(values)
    assert has(report, "V-BND001", "WARNING") and values == before
    attempt = deepcopy(scenario)
    attempt["object_type"] = "Forecast"
    assert has(engine.validate([attempt]), "V-SCH002", "ERROR")


@pytest.mark.parametrize(
    "change",
    [
        {"prediction_window": time("2025-01-01")},
        {"resolution_criteria": criteria(set_at=time("2027-01-01"))},
    ],
)
def test_forecast_explicit_temporal_conflicts(engine, change):
    report = engine.validate([obj("Claim"), forecast(**change)])
    assert has(report, "V-FC001", "ERROR")
    assert issues(report, "V-FC001")[0].details["admission"] == "ADMISSION_INVALID"


def test_forecast_wrong_claim_type(engine):
    report = engine.validate([obj("Scenario", "claim"), forecast()])
    assert has(report, "V-FC001", "ERROR") and has(report, "V-REF003", "ERROR")


def test_resolvability_alone_does_not_prove_admission(engine):
    report = engine.validate([obj("Claim"), forecast(claimant=None, modal_strength="unknown")])
    assert has(report, "V-FC001", "INDETERMINATE") and not report.errors


def test_unresolved_criterion_and_window_start(engine):
    report = engine.validate(
        [obj("Claim"), forecast(resolution_criteria=criteria(description=None))]
    )
    assert has(report, "V-FC001", "INDETERMINATE")
    value = forecast(prediction_window={"text": "end only", "end": "2026-12-01T00:00:00Z"})
    report = engine.validate([obj("Claim"), value])
    assert has(report, "V-TEMP002", "INDETERMINATE")
    assert has(report, "V-FC001", "INDETERMINATE") and not report.errors


def test_interval_overlap_is_not_proof_of_order(engine):
    cutoff = dict(time("2026-01-01"), end="2026-12-31T00:00:00Z")
    report = engine.validate([obj("Claim"), forecast(knowledge_cutoff=cutoff)])
    assert has(report, "V-FC001", "INDETERMINATE") and not report.errors


def test_reversed_resolution_interval_is_invalid(engine):
    criterion = criteria(set_at=dict(time("2026-02-01"), end="2026-01-01T00:00:00Z"))
    report = engine.validate([obj("Claim"), forecast(resolution_criteria=criterion)])
    assert has(report, "V-FC001", "ERROR") and has(report, "V-FC003", "ERROR")
