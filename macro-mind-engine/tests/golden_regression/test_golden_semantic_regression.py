"""Semantic invariants, not warning-count snapshots; failures remain visible."""

import json
from copy import deepcopy

import pytest
from macromind.audit.ids import canonical_bytes, digest_bytes
from tests.validation.helpers import forecast, has, obj, time

from .conftest import PATHS, objects


def test_gs001_partial_summary_never_reconstructs_objects(goldens):
    result = goldens["GS001"]
    assert result.source_family == "SUMMARY_ONLY_LEGACY"
    assert result.canonical_reconstruction_forbidden
    assert not result.canonical_bundle["objects"]
    text = PATHS["GS001"].read_text(encoding="utf-8")
    assert result.raw_document == text
    assert "来源冲突" in text and "Forecast" in text and "时间窗口模糊" in text
    assert "Candidate Heuristic" in text


@pytest.mark.parametrize("name", list(PATHS))
def test_original_bytes_and_unknown_not_repaired(goldens, name):
    result = goldens[name]
    assert result.source_sha256 == digest_bytes(PATHS[name].read_bytes())
    if name != "GS001":
        assert result.raw_document == json.loads(PATHS[name].read_bytes())
    assert result.status in {"PARTIAL", "LOSSY_BUT_SAFE", "LOSSLESS"}


@pytest.mark.parametrize("name", ["GS002", "GS003"])
def test_legacy_missing_objects_not_promoted_to_process_or_skill(goldens, name):
    result = goldens[name]
    assert not objects(result, "StructuralProcess")
    heuristics = objects(result, "Heuristic")
    assert heuristics and all(x["status"] in {"candidate", "unknown"} for x in heuristics)
    if name == "GS002":
        assert all(
            x["status"] == "candidate_only" for x in result.raw_document["16_candidate_heuristics"]
        )
        assert all(x["status"] == "unknown" for x in heuristics)
    assert result.unknowns and result.quarantined_items


def test_gs002_argument_chain_preserves_explicit_edges(goldens):
    result = goldens["GS002"]
    raw = next(x for x in result.raw_document["11_arguments"] if x["argument_id"] == "AR01")
    canonical = next(x for x in objects(result, "Argument") if x["id"] == "AR01")
    assert canonical["premises"] == raw["premises"]
    assert canonical["final_conclusion"] == raw["conclusion"]
    assert {step["id"] for step in canonical["steps"]} == {step["step_id"] for step in raw["steps"]}
    assert canonical["reasoner_id"] is None  # Never guess author from a prose label.


def test_gs003_market_infrastructure_subtype_and_no_process_promotion(goldens):
    result = goldens["GS003"]
    source = {x["event_id"]: x for x in result.raw_document["09_EVENTS"]}
    events = {x["id"]: x for x in objects(result, "Event")}
    for identity in ["EV05", "EV06", "EV07", "EV08"]:
        assert source[identity]["event_type"] == "x_candidate_market_infrastructure_event"
        assert identity in events
        assert events[identity]["description"] == source[identity]["description"]
    assert not objects(result, "StructuralProcess")


def test_gs003_rolling_source_and_separate_closure_states(goldens):
    result = goldens["GS003"]
    raw = result.raw_document
    evolution = raw["auxiliary"]["source_evolution"]
    assert any(x["relation"] == "temporal_evolution" and x["not_contradiction"] for x in evolution)
    states = {x["state"]: x for x in raw["auxiliary"]["closure_state_separation"]}
    assert {
        "official_or_adviser_claim",
        "operator_suspension",
        "traffic_collapse",
        "no_vessel_can_pass",
        "complete_legal_or_military_blockade",
    } <= states.keys()
    assert not states["complete_legal_or_military_blockade"]["evidence"]
    versions = objects(result, "SourceVersion")
    assert versions
    assert any(
        v["content_time"] == {"state": "unknown"} and v["captured_at"] != {"state": "unknown"}
        for v in versions
    )
    assert raw["auxiliary"]["scenario_crossrefs"]


def test_gs004_recurrence_decisions_and_future_prior_quarantine(goldens):
    result = goldens["GS004"]
    signals = {x["id"]: x for x in objects(result, "AnalystMethodSignal")}
    assert signals["MS01"]["recurrence_status"] == "first_observation"
    assert signals["MS01"]["recurrence_match"] == "uncertain"
    assert signals["MS02"]["matched_prior_signal_refs"] == []
    assert signals["MS02"]["recurrence_match"] == "none"
    assert (
        result.raw_document["finalization"]["human_decisions"]["MA1-FUTURE-LEAK-MS02"]
        == "accept_quarantined_future_prior"
    )
    assert (
        result.raw_document["finalization"]["future_sample_leakage_accepted_as_evidence"] is False
    )


def test_gs004_unknown_attribution_not_assigned_from_usage(goldens):
    result = goldens["GS004"]
    decisions = result.raw_document["finalization"]["human_decisions"]
    for identity in ["ME01", "ME02", "ME03"]:
        assert (
            decisions["MA1-ATTRIBUTION-" + identity]
            == "accept_unknown_shared_mechanism_attribution"
        )
    assert objects(result, "MechanismUsage")
    # Quarantined mechanisms are not fabricated to make their references pass.
    assert not objects(result, "Mechanism")
    assert any(
        q.raw_payload.get("mechanism_id") == "ME01"
        for q in result.quarantined_items
        if isinstance(q.raw_payload, dict)
    )


def test_gs004_ob20_no_percent_to_percentage_points(goldens):
    value = next(x for x in objects(goldens["GS004"], "IndicatorObservation") if x["id"] == "OB20")
    assert value["comparison_basis"]["comparison_type"] == "unknown"
    assert value["comparison_basis"]["delta_value"] is None
    assert "%" in value["unit"] and "pp" not in value["unit"]


def test_gs005_c005_scenario_only_and_explicit_nonadmission(goldens):
    result = goldens["GS005"]
    raw = result.raw_document
    assert raw["finalization"]["human_decisions"]["MA1-C005"] == "keep_scenario_only"
    scenarios = [x for x in raw["21_SCENARIOS"] if "C005" in x["claim_refs"]]
    assert scenarios and all(x["forecast_admitted"] is False for x in scenarios)
    assert all(
        x["admission_reason"] == "condition_not_endorsed_no_branch_selection" for x in scenarios
    )
    assert any("C005" in x["claim_refs"] for x in objects(result, "Scenario"))
    assert not any(x["claim_ref"] == "C005" for x in objects(result, "Forecast"))


def test_gs005_economic_diagnostic_claims_are_not_creator_method(goldens):
    result = goldens["GS005"]
    claims = {x["id"]: x for x in objects(result, "Claim")}
    source = {x["claim_id"]: x for x in result.raw_document["08_CLAIMS"]}
    for identity in ["M01", "M02", "M03", "M04"]:
        assert claims[identity]["analysis_context"] == "model_diagnostic"
        assert claims[identity]["reasoner_id"] == "model_gpt6"
        assert claims[identity]["statement"] == source[identity]["statement"]
        assert not any(
            identity in signal["claim_refs"] for signal in objects(result, "AnalystMethodSignal")
        )
    assert not objects(result, "Heuristic")


def test_gs005_first_failure_history_retained_after_hotfix(goldens):
    raw = goldens["GS005"].raw_document
    first, hotfix = raw["finalization"], raw["finalization_hotfix_1_1"]
    assert first["completed"] is False and first["validation_passed"] is False
    assert first["validation"]["status"] == "FAIL" and first["validation"]["ERROR"] > 0
    assert hotfix["completed"] is True and hotfix["validation_passed"] is True
    assert hotfix["decisions_readjudicated"] is False


@pytest.mark.parametrize("name", ["GS004", "GS005"])
def test_accepted_golden_passes_current_validator(goldens, golden_engine, name):
    report = golden_engine.validator.validate(
        goldens[name].canonical_bundle, {"validation_mode": "partial_bundle"}
    )
    # Historical diagnostics remain visible. User-approved policy 1.0 admits only
    # the dependency-closed projection, not every historical accepted record.
    from macromind.compatibility.activation import ActivationEngine

    from .conftest import CONTRACT, REGISTRY

    if name == "GS004":
        assert any(e.rule_id == "V-REF003" for e in report.errors)
    else:
        assert not report.errors
    result = ActivationEngine(CONTRACT, REGISTRY).activate(goldens[name].raw_document)
    assert result["status"] == "ACTIVE_CHAIN_CLOSED"
    assert not result["validation"]["errors"]
    assert result["repair_pool"]
    assert not any(e["rule_id"].startswith("V-REF") for e in result["validation"]["indeterminate"])


@pytest.mark.parametrize("name", ["GS002", "GS003", "GS004", "GS005"])
def test_adaptation_mapping_and_quarantine_are_reversible(goldens, name):
    from macromind.compatibility.detector import digest
    from macromind.compatibility.engine import pointer

    result = goldens[name]
    envelope = result.model_dump(mode="json")
    for entry in result.mapping_ledger:
        target = pointer(envelope, entry.target_path)
        assert digest(target) == entry.target_value_hash
    for item in result.quarantined_items:
        assert pointer(result.raw_document, item.source_path) == item.raw_payload


@pytest.mark.parametrize("left,right", [("GS002", "GS004"), ("small-id", "large-id")])
def test_synthetic_chronology_never_uses_sample_number(golden_engine, left, right):
    values = [
        obj("AnalystMethodSignal", left),
        obj(
            "AnalystMethodSignal",
            right,
            matched_prior_signal_refs=[left],
            recurrence_match="uncertain",
        ),
    ]
    report = golden_engine.validator.validate(
        values,
        {
            "current_content_time": "2026-08-01T00:00:00Z",
            "time_overrides": {left: "2026-09-01T00:00:00Z"},
        },
    )
    assert has(report, "V-TEMP003", "ERROR")


def test_synthetic_review_does_not_make_schema_valid(golden_engine):
    claim = obj("Claim", "bad")
    del claim["statement"]
    values = [claim, obj("ReviewQueueItem", target_ref="bad", status="open")]
    first = golden_engine.validator.validate(values)
    values[1]["status"] = "resolved"
    second = golden_engine.validator.validate(values)
    assert first.errors == second.errors and has(first, "V-SCH002", "ERROR")


def test_synthetic_modal_and_time_no_inferred_endorsement(golden_engine):
    values = [
        obj("Claim", "claim", population="selected group"),
        forecast(conditions="if capacity grows", branch_selection=None),
    ]
    before = deepcopy(values)
    report = golden_engine.validator.validate(values)
    assert has(report, "V-FC002", "INDETERMINATE") and values == before
    values[1]["knowledge_cutoff"] = time("2027-01-01")
    assert has(golden_engine.validator.validate(values), "V-TEMP002", "ERROR")


def test_synthetic_model_edge_and_truth_not_promoted(golden_engine):
    values = [
        obj("Argument", "a", analysis_context="model_diagnostic"),
        obj("AnalystMethodSignal", argument_refs=["a"]),
    ]
    before = deepcopy(values)
    assert has(golden_engine.validator.validate(values), "V-AN003", "ERROR") and values == before
    claim = obj("Claim", "c")
    claim["truth"] = "verified"
    assert has(golden_engine.validator.validate([claim]), "V-BND003", "ERROR")


@pytest.mark.parametrize(
    "role,stage",
    [
        ("order", "ordered"),
        ("revenue", "revenue_recognized"),
        ("cash_receipt", "cash_collected"),
        ("operating_cost", "unknown"),
    ],
)
def test_synthetic_stock_flow_and_recognition_not_converted(golden_engine, role, stage):
    values = [
        obj("Indicator", "i"),
        obj(
            "IndicatorObservation",
            indicator_ref="i",
            semantic_role=role,
            recognition_stage=stage,
            value=3,
            unit="%",
        ),
    ]
    before = deepcopy(values)
    golden_engine.validator.validate(values)
    assert values == before
    assert values[1]["comparison_basis"] == before[1]["comparison_basis"]


def test_validator_determinism_on_accepted_golden(goldens, golden_engine):
    bundle = goldens["GS005"].canonical_bundle
    values = [
        canonical_bytes(
            golden_engine.validator.validate(
                bundle, {"validation_mode": "partial_bundle"}
            ).model_dump(mode="json")
        )
        for _ in range(3)
    ]
    assert values[0] == values[1] == values[2]


def test_gs002_increment_and_stock_retained_in_quarantine(goldens):
    result = goldens["GS002"]
    claims = {x["claim_id"]: x for x in result.raw_document["06_claims"]}
    assert claims["C037"]["population"] == "China_TSF_increment"
    assert claims["C074"]["population"] == "China_TSF_stock"
    for identity in ["C037", "C074"]:
        assert any(q.raw_payload == claims[identity] for q in result.quarantined_items)
    # Missing required semantics remain quarantined; no fabricated stock/flow conversion.
    assert not objects(result, "IndicatorObservation")


def test_gs003_physical_constraint_does_not_establish_political_deadline(goldens):
    result = goldens["GS003"]
    raw = next(x for x in result.raw_document["16_ARGUMENTS"] if x["argument_id"] == "AR05")
    edge = next(x for x in raw["steps"] if x["step_id"] == "AR05-E3")
    assert edge["limitations"] == "物理仓储天数不决定政治承受上限"
    canonical = next(x for x in objects(result, "Argument") if x["id"] == "AR05")
    assert canonical["final_conclusion"] is None
    assert canonical["most_fragile_step"] == {"state": "unknown"}
    assert canonical["creator_shortcuts"] == []
    assert any(x["id"] == "AR05-E3" for x in canonical["steps"])
    # The limitation survives in raw provenance, not as an executable equivalence rule.
