from copy import deepcopy

import pytest

from .helpers import has, issues, obj


@pytest.mark.parametrize("status", ["verified", "false", "uncertain"])
def test_assessment_status_never_changes_claim(engine, status):
    values = [
        obj("Claim"),
        obj("InformationSet", "info"),
        obj(
            "Assessment", target_ref="claim", information_set_ref="info", verification_status=status
        ),
    ]
    before = deepcopy(values)
    report = engine.validate(values)
    assert values == before and not report.errors
    assert has(report, "V-BND003", "PASS")
    values[0]["truth"] = status
    assert has(engine.validate(values), "V-BND003", "ERROR")


def test_review_metamorphic_schema_reference_temporal_independence(engine):
    bad = obj("Claim", "bad")
    del bad["statement"]
    values = [
        bad,
        obj("Claim", "dangling", source_refs=["missing"]),
        obj("Claim", "wrong", source_refs=["dangling"]),
        obj("AnalystMethodSignal", "prior"),
        obj(
            "AnalystMethodSignal",
            "signal",
            recurrence_match="uncertain",
            matched_prior_signal_refs=["prior"],
        ),
        obj("ReviewQueueItem", target_ref="bad", status="open"),
    ]
    context = {
        "current_content_time": "2026-01-01T00:00:00Z",
        "time_overrides": {"prior": "2026-12-01T00:00:00Z"},
    }
    first = engine.validate(values, context)
    values[-1]["status"] = "resolved"
    second = engine.validate(values, context)
    assert first.errors == second.errors
    for rule in ("V-SCH002", "V-REF003", "V-REF004", "V-TEMP003"):
        assert has(first, rule, "ERROR")


@pytest.mark.parametrize("refs", [[], ["event"]])
def test_no_process_promotion(engine, refs):
    values = [obj("Event", "event"), obj("StructuralProcess", event_refs=refs)]
    before = deepcopy(values)
    report = engine.validate(values)
    assert has(report, "V-BND002", "WARNING") and values == before and not report.errors


@pytest.mark.parametrize("unit", [None, {"state": "unknown"}, "%"])
def test_no_percent_to_pp_conversion_and_unknown_baseline(engine, unit):
    basis = dict(
        comparison_type="percentage_point_change",
        baseline_value={"state": "unknown"},
        baseline_period=None,
        baseline_source_ref=None,
        delta_value=3,
        delta_unit=unit,
    )
    values = [
        obj("Indicator", "i"),
        obj(
            "IndicatorObservation",
            indicator_ref="i",
            value=3,
            unit="%",
            comparison_basis=basis,
            semantic_role="unknown",
            recognition_stage="unknown",
        ),
    ]
    before = deepcopy(values)
    report = engine.validate(values)
    assert has(report, "V-BND006", "WARNING") and values == before and not report.errors


def test_roles_stages_are_not_automatically_equivalent(engine):
    values = [obj("Indicator", "i")]
    for n, (role, stage) in enumerate(
        [
            ("order", "ordered"),
            ("revenue", "revenue_recognized"),
            ("cash_receipt", "cash_collected"),
            ("profit", "planned"),
        ]
    ):
        values.append(
            obj(
                "IndicatorObservation",
                str(n),
                indicator_ref="i",
                semantic_role=role,
                recognition_stage=stage,
            )
        )
    before = deepcopy(values)
    assert not engine.validate(values).errors
    assert values == before


@pytest.mark.parametrize("analyst", ["usage_analyst", "mechanism_author"])
def test_mechanism_usage_does_not_copy_authorship(engine, analyst):
    values = [
        obj("Mechanism", "m", reasoner_id="mechanism_author"),
        obj("MechanismUsage", mechanism_ref="m", analyst_id=analyst),
    ]
    before = deepcopy(values)
    report = engine.validate(values)
    assert values == before and not report.errors
    assert issues(report, "V-BND004")[0].details["mechanism_reasoner"] == "mechanism_author"


def test_actor_location_roles_do_not_merge_identity(engine):
    values = [obj("Actor", "a", location="same"), obj("Actor", "b", location="same")]
    before = deepcopy(values)
    report = engine.validate(values)
    assert values == before and report.object_count == 2 and not report.errors
