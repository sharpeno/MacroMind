from copy import deepcopy

import pytest

from .helpers import has, issues, obj, time


def bundle():
    return [
        obj("AnalystMethodSignal", "GS002_x"),
        obj(
            "AnalystMethodSignal",
            "GS004_x",
            matched_prior_signal_refs=["GS002_x"],
            recurrence_match="uncertain",
        ),
    ]


def test_golden_number_and_label_metamorphism(engine):
    values = bundle()
    context = {
        "sample_label": "GS004",
        "current_content_time": "2026-08-05T00:00:00Z",
        "time_overrides": {"GS002_x": "2026-09-21T00:00:00Z"},
    }
    first = engine.validate(values, context)
    assert has(first, "V-TEMP003", "ERROR")
    context["sample_label"] = "GS001 arbitrary"
    assert first == engine.validate(values, context)
    renamed = deepcopy(values)
    renamed[0]["id"], renamed[1]["id"] = "GS004_x", "GS002_x"
    renamed[1]["matched_prior_signal_refs"] = ["GS004_x"]
    context["time_overrides"] = {"GS004_x": "2026-09-21T00:00:00Z"}
    second = engine.validate(renamed, context)
    a, b = issues(first, "V-TEMP003"), issues(second, "V-TEMP003")
    assert [(i.outcome, i.details) for i in a] == [(i.outcome, i.details) for i in b]


@pytest.mark.parametrize("limit", ["knowledge_cutoff", "current_content_time"])
def test_future_after_either_limit(engine, limit):
    report = engine.validate(
        bundle(),
        {limit: "2026-08-05T00:00:00Z", "time_overrides": {"GS002_x": "2026-09-21T00:00:00Z"}},
    )
    assert has(report, "V-TEMP003", "ERROR")


def test_unknown_prior_and_naive_datetime(engine):
    assert has(engine.validate(bundle()), "V-TEMP003", "INDETERMINATE")
    assert has(
        engine.validate(
            bundle(),
            {"current_content_time": "2026-08-05", "time_overrides": {"GS002_x": "2026-09-21"}},
        ),
        "V-TEMP003",
        "INDETERMINATE",
    )


def test_real_source_content_not_capture_date(engine):
    values = [
        obj("Source", "source"),
        obj(
            "SourceVersion",
            "v",
            source_ref="source",
            content_time=time("2026-01-01"),
            captured_at=time("2026-12-31"),
        ),
        obj("SourceSegment", "seg", source_ref="source", source_version_ref="v"),
        obj("AnalystMethodSignal", "prior", source_segment_refs=["seg"]),
        obj(
            "AnalystMethodSignal",
            "current",
            matched_prior_signal_refs=["prior"],
            recurrence_match="uncertain",
        ),
    ]
    report = engine.validate(values, {"current_content_time": "2026-08-05T00:00:00Z"})
    assert has(report, "V-TEMP003", "PASS") and not report.errors
    values[1]["content_time"] = {"text": "2026-01-01 written in prose"}
    assert has(
        engine.validate(values, {"current_content_time": "2026-08-05T00:00:00Z"}),
        "V-TEMP003",
        "INDETERMINATE",
    )


def test_interval_reversal_and_no_text_parsing(engine):
    value = obj("Source", published_at={"text": "去年秋天"})
    assert has(engine.validate([value]), "V-TEMP001", "INDETERMINATE")
    value["published_at"] = dict(time("2026-09-01"), end="2026-01-01T00:00:00Z")
    assert has(engine.validate([value]), "V-TEMP001", "ERROR")
