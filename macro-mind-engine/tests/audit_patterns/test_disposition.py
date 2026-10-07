import pytest
from macromind.audit.models import RecordType
from macromind.audit.patterns import PatternAggregator, build_signature, disposition_for

from .helpers import record


@pytest.mark.parametrize(
    "kind,expected",
    [
        ("VALIDATION_FINDING", "PATTERN_ELIGIBLE"),
        ("ADAPTATION_LOSS", "PATTERN_ELIGIBLE"),
        ("QUARANTINE", "PATTERN_ELIGIBLE"),
        ("SCHEMA_GAP", "PATTERN_ELIGIBLE"),
        ("REGISTRY_GAP", "PATTERN_ELIGIBLE"),
        ("MAPPING_EVENT", "TRACE_ONLY"),
        ("TEST_RESULT", "SUMMARY_ONLY"),
        ("GATE_RESULT", "SUMMARY_ONLY"),
        ("IMMUTABILITY_EVENT", "SUMMARY_ONLY"),
        ("DEBT_STATUS", "SUMMARY_ONLY"),
        ("UNKNOWN_ENGINEERING_RECORD", "OPAQUE_EXCLUDED"),
    ],
)
def test_exact_disposition(kind, expected):
    r = record(kind=kind)
    result = PatternAggregator().aggregate([r])
    assert disposition_for(r.record_type) == expected
    assert result.record_dispositions == {r.record_id: expected}
    assert result.disposition_counts[expected] == 1
    assert result.eligible_occurrence_count == (1 if expected == "PATTERN_ELIGIBLE" else 0)


def test_all_records_have_one_disposition():
    records = [record(i, kind) for i, kind in enumerate(RecordType)]
    result = PatternAggregator().aggregate(records)
    assert len(result.record_dispositions) == len(records)
    assert sum(result.disposition_counts.values()) == len(records)
    assert result.disposition_counts == {
        "PATTERN_ELIGIBLE": 5,
        "TRACE_ONLY": 1,
        "SUMMARY_ONLY": 4,
        "OPAQUE_EXCLUDED": 1,
    }


@pytest.mark.parametrize(
    "kind,expected",
    [("MAPPING_EVENT", "TRACE_ONLY"), ("UNKNOWN_ENGINEERING_RECORD", "OPAQUE_EXCLUDED")],
)
def test_ten_thousand_excluded_not_interpreted(kind, expected):
    records = [
        record(
            i,
            kind,
            source_artifact_id=f"a:{i % 7}",
            metadata={
                "source_record": {
                    "object_type": {
                        "message": "Do not interpret",
                        "relation_type": "SAME_ISSUE_CANDIDATE",
                    }
                }
            },
        )
        for i in range(10000)
    ]
    result = PatternAggregator().aggregate(records)
    assert result.patterns == []
    assert result.disposition_counts[expected] == 10000
    assert result.disposition_artifact_counts[expected] == 7
    assert len(result.record_dispositions) == 10000


def test_summary_never_promoted_or_debt_created():
    records = [
        record(i, kind)
        for i, kind in enumerate(
            ["TEST_RESULT", "GATE_RESULT", "IMMUTABILITY_EVENT", "DEBT_STATUS"] * 100
        )
    ]
    result = PatternAggregator().aggregate(records)
    assert result.pattern_count == 0
    assert result.disposition_counts["SUMMARY_ONLY"] == 400
    assert "debts" not in result.model_dump()
    assert "records" not in result.model_dump()


def test_noneligible_signature_rejected():
    with pytest.raises(ValueError):
        build_signature(record(kind="UNKNOWN_ENGINEERING_RECORD"))
