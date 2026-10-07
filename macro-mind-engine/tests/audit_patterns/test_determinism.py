from copy import deepcopy

from macromind.audit.ids import semantic_hash
from macromind.audit.patterns import PatternAggregator

from .helpers import bundle, record


def test_three_runs_byte_stable():
    source = bundle([record(i, rule_id=str(i % 3)) for i in range(11)])
    results = [PatternAggregator().aggregate(source) for _ in range(3)]
    assert results[0].semantic_bytes() == results[1].semantic_bytes() == results[2].semantic_bytes()
    assert len({r.deterministic_hash for r in results}) == 1
    assert results[0].deterministic_hash == semantic_hash(results[0].semantic_payload())
    assert [p.pattern_id for p in results[0].patterns] == sorted(
        p.pattern_id for p in results[0].patterns
    )


def test_input_order_invariance():
    records = [record(i, reason_code=str(i % 4)) for i in range(12)]
    a = PatternAggregator().aggregate(bundle(records))
    b = PatternAggregator().aggregate(bundle(list(reversed(records))))
    assert a.input_normalization_hash != b.input_normalization_hash
    assert a.semantic_bytes() == b.semantic_bytes()
    assert a.deterministic_hash == b.deterministic_hash


def test_filename_invariance_and_operational_metadata():
    source = bundle([record()])
    results = []
    for path in ["C:/a.json", "D:/nested/banana.json"]:
        variant = source.model_copy(
            update={
                "input_manifest": [
                    {
                        "path_or_label": path,
                        "source_metadata": {"machine": path, "created_at": path},
                    }
                ]
            }
        )
        variant = variant.model_copy(
            update={"deterministic_hash": semantic_hash(variant.semantic_payload())}
        )
        results.append(PatternAggregator().aggregate(variant))
    assert results[0].semantic_bytes() == results[1].semantic_bytes()


def test_input_not_mutated_and_no_records_created(monkeypatch):
    source = bundle([record(i) for i in range(5)])
    before = deepcopy(source.model_dump())
    original_ids = [id(r) for r in source.records]

    def forbidden(*args, **kwargs):
        raise AssertionError("Aggregator must not create new AuditRecord objects")

    monkeypatch.setattr(type(source.records[0]), "__init__", forbidden)
    result = PatternAggregator().aggregate(source)
    assert source.model_dump() == before
    assert [id(r) for r in source.records] == original_ids
    assert "records" not in result.model_dump()
