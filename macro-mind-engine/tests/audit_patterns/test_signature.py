import pytest
from macromind.audit.patterns import PatternAggregator, build_signature, normalize_path_shape

from .helpers import record


def test_message_metamorphism():
    a = record(0, message="low risk", metadata={"source_record": {"description": "one"}})
    b = record(
        1,
        message="critical error",
        metadata={"source_record": {"description": "different", "review_notes": "another"}},
    )
    assert build_signature(a).pattern_id() == build_signature(b).pattern_id()
    assert PatternAggregator().aggregate([a, b]).pattern_count == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("reason_code", "other"),
        ("rule_id", "R2"),
        ("record_type", "SCHEMA_GAP"),
        ("component", "validator"),
        ("category", "different"),
    ],
)
def test_structural_field_separates(field, value):
    a = record(0, kind="VALIDATION_FINDING", rule_id="R1", reason_code="missing")
    b = record(1, kind="VALIDATION_FINDING", rule_id="R1", reason_code="missing")
    b = (
        record(
            1,
            **{
                **b.model_dump(exclude={"record_id", "record_type"}),
                "kind": b.record_type,
                field: value,
            },
        )
        if field != "record_type"
        else record(1, kind=value, rule_id="R1", reason_code="missing")
    )
    assert build_signature(a).pattern_id() != build_signature(b).pattern_id()
    assert PatternAggregator().aggregate([a, b]).pattern_count == 2


@pytest.mark.parametrize(
    "path,expected",
    [
        (None, None),
        ("", ""),
        ("/claims/0/source_refs/2", "/claims/*/source_refs/*"),
        ("/claims/12/detail", "/claims/*/detail"),
        ("/claim-12/01/１２/+2/-1", "/claim-12/01/１２/+2/-1"),
        ("/a~1b/~0/0", "/a~1b/~0/*"),
    ],
)
def test_path_shape(path, expected):
    assert normalize_path_shape(path) == expected


def test_numeric_index_metamorphism():
    a = record(0, target_path="/objects/1/value")
    b = record(12, target_path="/objects/42/value")
    assert build_signature(a) == build_signature(b)


def test_field_name_changes_pattern():
    assert build_signature(record(source_path="/claims/0/detail")) != build_signature(
        record(source_path="/claims/0/details")
    )


@pytest.mark.parametrize(
    "key",
    [
        "source_family",
        "source_object_type",
        "target_object_type",
        "object_type",
        "field",
        "field_name",
        "source_field",
        "target_field",
    ],
)
def test_each_whitelisted_dimension_is_retained(key):
    a = record(metadata={"source_record": {key: "A"}})
    b = record(metadata={"source_record": {key: "B"}})
    assert build_signature(a).structured_dimensions == {key: "A"}
    assert build_signature(a) != build_signature(b)


def test_missing_and_explicit_null_dimensions():
    missing = build_signature(record(source_path=None, target_path=None, category=None))
    explicit = build_signature(record(metadata={"source_record": {"object_type": None}}))
    assert missing.structured_dimensions == {}
    assert missing.source_path_shape is missing.target_path_shape is missing.category is None
    assert explicit.structured_dimensions == {"object_type": None}


def test_forbidden_signature_fields_not_used():
    a = record()
    b = record(
        99,
        source_artifact_id="filename:banana",
        source_artifact_hash="b" * 64,
        source_pointer="/losses/998",
        message="other",
        object_ref="new:id",
        metadata={
            "source_record": {
                "filename": "C:/banana.json",
                "run_id": "today",
                "created_at": "now",
                "thread_ref": "thread:a",
            }
        },
    )
    assert build_signature(a) == build_signature(b)


@pytest.mark.parametrize("path", ["C:/file.json", "claims.0", "/bad~2/0"])
def test_malformed_structural_path_hard_error(path):
    with pytest.raises(ValueError):
        PatternAggregator().aggregate([record(source_path=path)])


@pytest.mark.parametrize("payload", [None, [], "unstructured snapshot"])
def test_missing_structured_snapshot_conservative_pattern(payload):
    result = PatternAggregator().aggregate([record(metadata={"source_record": payload})])
    assert result.eligible_occurrence_count == result.pattern_count == 1
    assert result.patterns[0].structured_dimensions == {}


@pytest.mark.parametrize("payload", [{"field": {"message": "opaque"}}, {"field": float("nan")}])
def test_malformed_structured_source_hard_error(payload):
    with pytest.raises(ValueError):
        PatternAggregator().aggregate([record(metadata={"source_record": payload})])
