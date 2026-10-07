from macromind.audit.patterns import PatternAggregator
from macromind.audit.patterns.aggregate import distribution_key

from .helpers import record


def test_severity_does_not_split_and_distribution_exact():
    rows = [
        record(i, severity=s)
        for i, s in enumerate(["WARNING", "ERROR", "INDETERMINATE", None, "WARNING"])
    ]
    result = PatternAggregator().aggregate(rows)
    assert result.pattern_count == 1
    assert result.patterns[0].severity_distribution == {
        "ERROR": 1,
        "INDETERMINATE": 1,
        "WARNING": 2,
        "null": 1,
    }


def test_outcome_does_not_split_and_distribution_exact():
    rows = [
        record(i, source_outcome=o)
        for i, o in enumerate(["PASS", "ERROR", "INDETERMINATE", None, False, "false", "null"])
    ]
    result = PatternAggregator().aggregate(rows)
    assert result.pattern_count == 1
    assert result.patterns[0].outcome_distribution == {
        "ERROR": 1,
        "INDETERMINATE": 1,
        "PASS": 1,
        "false": 1,
        "json:false": 1,
        "null": 1,
        'str:"null"': 1,
    }


def test_distribution_reserved_keys_do_not_collide():
    values = [None, "null", False, "false", "json:false", "str:null", [1], {"a": None}]
    assert len({distribution_key(value) for value in values}) == len(values)


def test_full_occurrences_examples_artifacts_review_counts():
    records = [
        record(i, source_artifact_id=f"a:{i % 3}", review_required=True if i < 4 else None)
        for i in range(13)
    ]
    result = PatternAggregator().aggregate(list(reversed(records)))
    p = result.patterns[0]
    assert p.occurrence_count == 13
    assert p.occurrence_record_ids == sorted(r.record_id for r in records)
    assert p.example_record_ids == p.occurrence_record_ids[:5]
    assert p.artifact_count == 3
    assert p.source_artifact_ids == ["a:0", "a:1", "a:2"]
    assert p.review_required_count == 4


def test_frequency_does_not_promote_review_or_create_debt():
    result = PatternAggregator().aggregate([record(i, review_required=False) for i in range(100)])
    assert result.patterns[0].review_required_count == 0
    for key in ("risk_level", "priority", "importance", "debt", "repair_recommendation"):
        assert key not in result.patterns[0].model_dump()


def test_empty_input():
    result = PatternAggregator().aggregate([])
    assert result.patterns == []
    assert result.eligible_occurrence_count == result.pattern_count == 0
    assert sum(result.disposition_counts.values()) == 0
