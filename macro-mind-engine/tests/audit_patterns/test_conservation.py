import pytest
from macromind.audit.models import RecordType
from macromind.audit.patterns import PatternAggregator, PatternInputError, validate_conservation

from .helpers import bundle, record


def test_complete_conservation_and_bidirectional_index():
    records = [
        record(i, list(RecordType)[i % len(RecordType)], reason_code=str(i % 3)) for i in range(80)
    ]
    result = PatternAggregator().aggregate(records)
    assert all(validate_conservation(result, records).values())
    eligible = {
        r.record_id
        for r in records
        if result.record_dispositions[r.record_id] == "PATTERN_ELIGIBLE"
    }
    index = result.pattern_occurrence_index
    assert sum(p.occurrence_count for p in result.patterns) == len(eligible)
    assert set(index.by_record) == eligible
    for pid, ids in index.by_pattern.items():
        assert all(index.by_record[rid] == pid for rid in ids)


@pytest.mark.parametrize("kind", ["ADAPTATION_LOSS", "UNKNOWN_ENGINEERING_RECORD", "MAPPING_EVENT"])
def test_duplicate_input_id_hard_error(kind):
    with pytest.raises(PatternInputError, match="Duplicate"):
        PatternAggregator().aggregate([record(kind=kind), record(kind=kind)])


def test_duplicate_assignment_hard_error():
    records = [record(0, rule_id="a"), record(1, rule_id="b")]
    result = PatternAggregator().aggregate(records)
    result.patterns[1].occurrence_record_ids.extend(result.patterns[0].occurrence_record_ids)
    with pytest.raises(PatternInputError, match="Duplicate occurrence"):
        validate_conservation(result, records)


def test_missing_assignment_hard_error():
    records = [record(0), record(1)]
    result = PatternAggregator().aggregate(records)
    result.patterns[0].occurrence_record_ids.pop()
    with pytest.raises(PatternInputError, match="missing"):
        validate_conservation(result, records)


def test_wrong_reverse_index_hard_error():
    records = [record()]
    result = PatternAggregator().aggregate(records)
    result.pattern_occurrence_index.by_record[records[0].record_id] = "wrong"
    with pytest.raises(PatternInputError, match="Bidirectional"):
        validate_conservation(result, records)


@pytest.mark.parametrize(
    "field,value",
    [
        ("record_id", ""),
        ("record_type", "bogus"),
        ("reason_code", 123),
        ("source_artifact_hash", "bad"),
        ("review_required", 1),
        ("metadata", []),
        ("evidence_refs", 123),
        ("message", 123),
        ("source_severity", []),
        ("source_pointer", "not-a-pointer"),
    ],
)
def test_damaged_record_hard_error(field, value):
    with pytest.raises(PatternInputError):
        PatternAggregator().aggregate([record().model_copy(update={field: value})])


def test_damaged_bundle_counts_and_hash_hard_error():
    source = bundle([record()])
    with pytest.raises(PatternInputError, match="counts"):
        PatternAggregator().aggregate(source.model_copy(update={"record_counts": {}}))
    with pytest.raises(PatternInputError, match="hash"):
        PatternAggregator().aggregate(source.model_copy(update={"deterministic_hash": "wrong"}))


def test_damaged_bundle_record_validated_before_hashing():
    source = bundle([record()])
    bad = source.model_copy(
        update={"records": [record().model_copy(update={"record_type": "bogus"})]}
    )
    with pytest.raises(PatternInputError, match="valid Phase 1.5A"):
        PatternAggregator().aggregate(bad)
